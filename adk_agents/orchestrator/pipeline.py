"""End-to-end A2A orchestration pipeline for the customer-facing Orchestrator Agent."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any, AsyncIterator, Optional
import yaml

from adk_agents.orchestrator.a2a_client import A2aProtocolClient
from adk_agents.orchestrator.prompts import (
    BUILDER_A2A_URL,
    EXECUTIONER_A2A_URL,
    REVISOR_A2A_URL,
)
from contracts.revision_verdict import RevisionVerdict
from contracts.trip_spec import TripSpec


@dataclass(frozen=True)
class OrchestratorStageEvent:
    """Represents an incremental stage message yielded by the Orchestrator as each A2A agent finishes."""

    stage: str
    text: str
    state_delta: dict[str, Any]


def extract_validated_trip_spec(text: str) -> Optional[TripSpec]:
    """Parses a `TripSpec` from a Builder A2A response if present and validated."""
    if not text or not text.strip():
        return None

    fence_match = re.search(r"```(?:yaml|json)?\s*([\s\S]*?)```", text)
    candidate = fence_match.group(1).strip() if fence_match else text.strip()

    for loader in (yaml.safe_load, json.loads):
        try:
            loaded = loader(candidate)
            if isinstance(loaded, dict):
                payload = loaded.get("trip_spec", loaded)
                if isinstance(payload, dict):
                    spec = TripSpec.model_validate(payload)
                    if spec.status == "validated" and not spec.missing_sdd_fields():
                        return spec
        except Exception:
            continue

    return None


def parse_revision_verdict(text: str) -> Optional[RevisionVerdict]:
    """Parses a `RevisionVerdict` from a Revisor A2A response."""
    if not text or not text.strip():
        return None

    fence_match = re.search(r"```(?:json|yaml)?\s*([\s\S]*?)```", text)
    candidate = fence_match.group(1).strip() if fence_match else text.strip()

    for loader in (json.loads, yaml.safe_load):
        try:
            loaded = loader(candidate)
            if isinstance(loaded, dict) and "decision" in loaded:
                return RevisionVerdict.model_validate(loaded)
        except Exception:
            continue

    return None


class OrchestratorA2aPipeline:
    """Coordinates Builder -> Executioner -> Revisor strictly via A2A protocol calls."""

    @classmethod
    async def stream_turn_stages(
        cls,
        user_text: str,
        state: dict[str, Any],
        session_id: str = "default",
        builder_url: str = BUILDER_A2A_URL,
        executioner_url: str = EXECUTIONER_A2A_URL,
        revisor_url: str = REVISOR_A2A_URL,
    ) -> AsyncIterator[OrchestratorStageEvent]:
        """Streams each A2A agent stage (`builder` -> `executioner` -> `revisor`) as soon as it finishes."""
        trace: list[dict[str, Any]] = list(state.get("a2a_trace", []))
        builder_context_id = state.get("builder_a2a_context_id") or f"builder-{session_id}"
        state["builder_a2a_context_id"] = builder_context_id

        # Stage 1: Forward customer turn to Builder A2A Agent (:8001)
        builder_resp = await A2aProtocolClient.send_a2a_message(
            base_url=builder_url,
            text=user_text,
            context_id=builder_context_id,
        )
        trace.append(
            {
                "step": "builder",
                "agent_name": builder_resp.agent_name,
                "context_id": builder_resp.context_id,
                "task_id": builder_resp.task_id,
            }
        )

        validated_spec = extract_validated_trip_spec(builder_resp.text)
        if validated_spec is None:
            sdd_status = (
                "failed_max_attempts"
                if "Maximum Attempts Reached" in builder_resp.text
                else "interviewing"
            )
            state["sdd_status"] = sdd_status
            state["a2a_trace"] = trace
            yield OrchestratorStageEvent(
                stage="builder_interview",
                text=builder_resp.text,
                state_delta={
                    "builder_a2a_context_id": builder_context_id,
                    "sdd_status": sdd_status,
                    "a2a_trace": list(trace),
                },
            )
            return

        # SDD Validated! Immediately stream Stage 1 completion to the customer UI
        spec_dict = validated_spec.model_dump(mode="json")
        state["sdd_status"] = "validated"
        state["trip_spec"] = spec_dict
        state["a2a_trace"] = list(trace)
        yaml_contract = validated_spec.to_yaml_block()

        yield OrchestratorStageEvent(
            stage="builder_validated",
            text=(
                f"{builder_resp.text}\n\n"
                f"---\n"
                f"⏳ **A2A Handoff → Executioner (`:8002`)**: Generating complete Trip Report..."
            ),
            state_delta={
                "builder_a2a_context_id": builder_context_id,
                "sdd_status": "validated",
                "trip_spec": spec_dict,
                "a2a_trace": list(trace),
            },
        )

        # Stage 2: Send validated trip-spec over A2A to Executioner (:8002)
        exec_context_id = f"executioner-{session_id}"
        exec_resp = await A2aProtocolClient.send_a2a_message(
            base_url=executioner_url,
            text=yaml_contract,
            context_id=exec_context_id,
        )
        report_markdown = exec_resp.text
        state["trip_report_markdown"] = report_markdown
        trace.append(
            {
                "step": "executioner",
                "agent_name": exec_resp.agent_name,
                "context_id": exec_resp.context_id,
                "task_id": exec_resp.task_id,
            }
        )
        state["a2a_trace"] = list(trace)

        # Immediately stream Stage 2 (TripReport) to the customer UI
        yield OrchestratorStageEvent(
            stage="executioner_report",
            text=(
                f"{report_markdown}\n\n"
                f"---\n"
                f"⏳ **A2A Handoff → Revisor (`:8003`)**: Auditing report against SDD `trip-spec`..."
            ),
            state_delta={
                "trip_report_markdown": report_markdown,
                "a2a_trace": list(trace),
            },
        )

        # Stage 3: Send {trip_spec, report_markdown} to Revisor A2A (:8003)
        revisor_payload = json.dumps(
            {
                "trip_spec": spec_dict,
                "report_markdown": report_markdown,
            }
        )
        rev_context_id = f"revisor-{session_id}"
        rev_resp = await A2aProtocolClient.send_a2a_message(
            base_url=revisor_url,
            text=revisor_payload,
            context_id=rev_context_id,
        )
        verdict = parse_revision_verdict(rev_resp.text)
        trace.append(
            {
                "step": "revisor",
                "agent_name": rev_resp.agent_name,
                "context_id": rev_resp.context_id,
                "task_id": rev_resp.task_id,
                "decision": verdict.decision if verdict else "UNKNOWN",
            }
        )

        # Self-healing retry if Revisor rejects with retry_target == "executioner"
        if (
            verdict is not None
            and verdict.decision == "REJECT"
            and verdict.retry_target == "executioner"
        ):
            retry_resp = await A2aProtocolClient.send_a2a_message(
                base_url=executioner_url,
                text=yaml_contract,
                context_id=f"{exec_context_id}-retry",
            )
            report_markdown = retry_resp.text
            state["trip_report_markdown"] = report_markdown
            revisor_retry_payload = json.dumps(
                {
                    "trip_spec": spec_dict,
                    "report_markdown": report_markdown,
                }
            )
            rev_retry_resp = await A2aProtocolClient.send_a2a_message(
                base_url=revisor_url,
                text=revisor_retry_payload,
                context_id=f"{rev_context_id}-retry",
            )
            verdict = parse_revision_verdict(rev_retry_resp.text) or verdict
            trace.append(
                {
                    "step": "revisor_retry",
                    "agent_name": rev_retry_resp.agent_name,
                    "context_id": rev_retry_resp.context_id,
                    "task_id": rev_retry_resp.task_id,
                    "decision": verdict.decision,
                }
            )

        verdict_dict = verdict.model_dump(mode="json") if verdict is not None else {}
        if verdict is not None:
            state["revision_verdict"] = verdict_dict
        state["a2a_trace"] = list(trace)

        verdict_badge = (
            f"### ✅ SDD Revisor A2A Audit: `{verdict.decision}` (Score: **{verdict.score}/100**)\n"
            f"{verdict.revision_instructions}"
            if verdict is not None
            else "### ✅ SDD Revisor A2A Audit Complete"
        )

        yield OrchestratorStageEvent(
            stage="revisor_verdict",
            text=verdict_badge,
            state_delta={
                "trip_report_markdown": report_markdown,
                "revision_verdict": verdict_dict,
                "a2a_trace": list(trace),
            },
        )

    @classmethod
    async def run_turn(
        cls,
        user_text: str,
        state: dict[str, Any],
        session_id: str = "default",
        builder_url: str = BUILDER_A2A_URL,
        executioner_url: str = EXECUTIONER_A2A_URL,
        revisor_url: str = REVISOR_A2A_URL,
    ) -> str:
        """Processes a customer turn and returns the combined stage outputs."""
        chunks: list[str] = []
        async for stage_event in cls.stream_turn_stages(
            user_text=user_text,
            state=state,
            session_id=session_id,
            builder_url=builder_url,
            executioner_url=executioner_url,
            revisor_url=revisor_url,
        ):
            chunks.append(stage_event.text)
        return "\n\n---\n\n".join(chunks)
