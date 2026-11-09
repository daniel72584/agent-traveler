"""ADK lifecycle callbacks (`before_agent_callback`, `before_model_callback`) for Executioner."""

from __future__ import annotations

import os
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

from adk_agents.executioner.pipeline import (
    TravelExecutionPipeline,
    parse_trip_spec_input,
)


def _extract_latest_user_text(llm_request: LlmRequest) -> str:
    for content in reversed(llm_request.contents or []):
        if content.role == "user" and content.parts:
            texts = [p.text for p in content.parts if getattr(p, "text", None)]
            if texts:
                return "\n".join(texts)
    return ""


def require_validated_spec_gate(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """ADK `before_agent_callback` ensuring Executioner only runs when given a complete `TripSpec`."""
    state = callback_context.state
    user_text = ""
    if callback_context.user_content and callback_context.user_content.parts:
        user_text = "\n".join(
            p.text for p in callback_context.user_content.parts if getattr(p, "text", None)
        )

    spec = parse_trip_spec_input(user_text, state)
    if spec is None:
        return types.Content(
            role="model",
            parts=[
                types.Part.from_text(
                    text=(
                        "### ⚠️ Executioner Error: Missing `trip-spec` Input\n\n"
                        "The isolated **Executioner Agent** requires a valid `trip-spec` JSON or YAML contract."
                    )
                )
            ],
        )

    missing = spec.missing_sdd_fields()
    if missing:
        return types.Content(
            role="model",
            parts=[
                types.Part.from_text(
                    text=(
                        "### ⚠️ Executioner Gate Blocked: Incomplete `trip-spec`\n\n"
                        f"Cannot execute travel orchestration because the provided `trip-spec` is missing: "
                        f"`{', '.join(missing)}`."
                    )
                )
            ],
        )

    return None


def deterministic_executioner_fallback_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """ADK `before_model_callback` running `TravelExecutionPipeline` (live tools or offline).

    Runs the 4 executioner tools (`check_cancilleria_visa_policy`,
    `build_route_and_climate_plan`, `analyze_flights_from_colombia`,
    `scout_prices_and_live_currency`) directly via `TravelExecutionPipeline.execute`
    so the A2A server responds in ~1-2s instead of timing out across 5 sequential LLM turns.
    Set `EXECUTIONER_FORCE_LLM=1` to bypass the pipeline and let the LLM invoke tools manually.
    """
    force_llm = os.environ.get("EXECUTIONER_FORCE_LLM", "").lower() in ("1", "true", "yes")
    has_api_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_KEY"))

    if force_llm and has_api_key:
        return None

    user_text = _extract_latest_user_text(llm_request)
    state = callback_context.state
    spec = parse_trip_spec_input(user_text, state)
    assert spec is not None, "TripSpec should be validated by require_validated_spec_gate"

    report = TravelExecutionPipeline.execute(spec)
    state["trip_report"] = report.model_dump(mode="json")
    state["trip_report_markdown"] = report.markdown_report

    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part.from_text(text=report.markdown_report)],
        )
    )

