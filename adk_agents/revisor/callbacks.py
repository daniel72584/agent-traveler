"""ADK lifecycle callbacks (`before_model_callback`) for the Revisor agent."""

from __future__ import annotations

import os
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

from adk_agents.revisor.engine import RevisorAuditEngine, parse_revisor_inputs
from contracts.revision_verdict import RevisionVerdict


def _extract_latest_user_text(llm_request: LlmRequest) -> str:
    for content in reversed(llm_request.contents or []):
        if content.role == "user" and content.parts:
            texts = [p.text for p in content.parts if getattr(p, "text", None)]
            if texts:
                return "\n".join(texts)
    return ""


def deterministic_revisor_fallback_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """ADK `before_model_callback` running `RevisorAuditEngine` deterministically offline."""
    offline_mode = os.environ.get("REVISOR_OFFLINE_MODE", "").lower() in ("1", "true", "yes")
    has_api_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_KEY"))

    if not offline_mode and has_api_key:
        return None

    user_text = _extract_latest_user_text(llm_request)
    state = callback_context.state
    spec, report_md, report_dict = parse_revisor_inputs(user_text, state)

    verdict: RevisionVerdict = RevisorAuditEngine.evaluate(
        spec=spec,
        report_markdown=report_md,
        report_dict=report_dict,
    )
    state["revision_verdict"] = verdict.model_dump(mode="json")

    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part.from_text(text=verdict.model_dump_json(indent=2))],
        )
    )

