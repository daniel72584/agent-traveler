"""State repository and lifecycle transition engine for the Builder agent."""

from __future__ import annotations

from typing import Any, Optional

from google.adk.tools.tool_context import ToolContext

from adk_agents.builder.prompts import MAX_SDD_ATTEMPTS, SDD_INTERVIEW_TEMPLATE
from contracts.trip_spec import TripSpec, TripSpecPatch


class TripSpecStateRepository:
    """Repository encapsulating ADK session state persistence for `TripSpec`."""

    SPEC_KEY = "trip_spec"
    STATUS_KEY = "sdd_status"
    ATTEMPT_KEY = "sdd_attempt_count"

    @classmethod
    def load(cls, state: Any) -> TripSpec:
        raw = state.get(cls.SPEC_KEY)
        return TripSpec.model_validate(raw) if isinstance(raw, dict) else TripSpec()

    @classmethod
    def save(cls, state: Any, spec: TripSpec) -> None:
        state[cls.SPEC_KEY] = spec.model_dump(mode="json")
        state[cls.STATUS_KEY] = spec.status

    @classmethod
    def get_attempt(cls, state: Any, default: int = 1) -> int:
        return int(state.get(cls.ATTEMPT_KEY, default))

    @classmethod
    def increment_attempt(cls, state: Any) -> int:
        next_attempt = int(state.get(cls.ATTEMPT_KEY, 0)) + 1
        state[cls.ATTEMPT_KEY] = next_attempt
        return next_attempt


class SddLifecycleEngine:
    """State Transition Engine managing SDD interview completion and attempt limits."""

    @classmethod
    def evaluate_and_persist(
        cls,
        state: Any,
        patch: TripSpecPatch | dict[str, Any],
        tool_context: Optional[ToolContext] = None,
    ) -> dict[str, Any]:
        """Applies `patch` to the session's `TripSpec` and transitions its lifecycle status."""
        spec = TripSpecStateRepository.load(state).apply_patch(patch)
        missing = spec.missing_sdd_fields()
        attempt_count = TripSpecStateRepository.get_attempt(state, default=1)
        attempts_remaining = max(0, MAX_SDD_ATTEMPTS - attempt_count)

        if not missing:
            return cls._transition_to_validated(
                state, spec, attempt_count, attempts_remaining, tool_context
            )

        if attempt_count >= MAX_SDD_ATTEMPTS:
            return cls._transition_to_failed(
                state, spec, attempt_count, missing, tool_context
            )

        return cls._transition_to_interviewing(
            state, spec, attempt_count, attempts_remaining, missing
        )

    @classmethod
    def _transition_to_validated(
        cls,
        state: Any,
        spec: TripSpec,
        attempt: int,
        remaining: int,
        tool_context: Optional[ToolContext],
    ) -> dict[str, Any]:
        spec.status = "validated"
        TripSpecStateRepository.save(state, spec)
        if tool_context is not None:
            tool_context.actions.escalate = True
        yaml_contract = spec.to_yaml_block()
        return {
            "status": "validated",
            "attempt": attempt,
            "max_attempts": MAX_SDD_ATTEMPTS,
            "attempts_remaining": remaining,
            "missing_fields": [],
            "trip_spec": spec.model_dump(mode="json"),
            "yaml_contract": yaml_contract,
            "formatted_response": (
                f"### ✅ Validated Trip Specification (`trip-spec`)\n\n"
                f"Completed on **Attempt {attempt}/{MAX_SDD_ATTEMPTS}**. "
                f"All required SDD parameters are confirmed:\n\n"
                f"{yaml_contract}"
            ),
            "message": "All SDD fields are complete and validated.",
        }

    @classmethod
    def _transition_to_failed(
        cls,
        state: Any,
        spec: TripSpec,
        attempt: int,
        missing: list[str],
        tool_context: Optional[ToolContext],
    ) -> dict[str, Any]:
        spec.status = "failed_max_attempts"
        TripSpecStateRepository.save(state, spec)
        if tool_context is not None:
            tool_context.actions.escalate = True
        return {
            "status": "failed_max_attempts",
            "attempt": attempt,
            "max_attempts": MAX_SDD_ATTEMPTS,
            "attempts_remaining": 0,
            "missing_fields": missing,
            "trip_spec": spec.model_dump(mode="json"),
            "formatted_response": (
                f"### ⛔ SDD Interview Halted — Maximum Attempts Reached ({attempt}/{MAX_SDD_ATTEMPTS})\n\n"
                f"We could not complete a validated `trip-spec` within the maximum allowed "
                f"**{MAX_SDD_ATTEMPTS} attempts**.\n\n"
                f"**Still Missing Fields**: {', '.join(missing)}"
            ),
            "message": (
                f"Reached maximum SDD interview attempts ({MAX_SDD_ATTEMPTS}/{MAX_SDD_ATTEMPTS}). "
                f"Still missing: {', '.join(missing)}."
            ),
        }

    @classmethod
    def _transition_to_interviewing(
        cls,
        state: Any,
        spec: TripSpec,
        attempt: int,
        remaining: int,
        missing: list[str],
    ) -> dict[str, Any]:
        spec.status = "interviewing"
        TripSpecStateRepository.save(state, spec)
        return {
            "status": "interviewing",
            "attempt": attempt,
            "max_attempts": MAX_SDD_ATTEMPTS,
            "attempts_remaining": remaining,
            "missing_fields": missing,
            "trip_spec": spec.model_dump(mode="json"),
            "interview_prompt_template": SDD_INTERVIEW_TEMPLATE,
            "formatted_response": (
                f"{SDD_INTERVIEW_TEMPLATE}\n\n"
                f"---\n"
                f"*SDD Builder Status: `interviewing` | Attempt **{attempt}/{MAX_SDD_ATTEMPTS}** "
                f"({remaining} attempts remaining) | Missing fields: `{', '.join(missing)}`*"
            ),
        }

