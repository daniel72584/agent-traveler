"""ADK lifecycle callbacks for the customer-facing Orchestrator Agent."""

from __future__ import annotations

from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

from adk_agents.orchestrator.pipeline import OrchestratorA2aPipeline


def _extract_latest_user_text(llm_request: LlmRequest) -> str:
    """Extracts the latest customer message text from `LlmRequest` contents."""
    for content in reversed(llm_request.contents or []):
        if content.role == "user" and content.parts:
            texts = [p.text for p in content.parts if getattr(p, "text", None)]
            if texts:
                return "\n".join(texts)
    return ""


async def deterministic_orchestrator_a2a_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """ADK `before_model_callback` that drives the A2A handoff sequence deterministically.

    Ensures every customer message is routed over A2A to `Builder` (`:8001`), and as soon
    as `Builder` emits a validated `trip-spec`, automatically chains A2A calls to
    `Executioner` (`:8002`) and `Revisor` (`:8003`) before returning the single response
    to the customer.
    """
    user_text = _extract_latest_user_text(llm_request)
    session = getattr(callback_context._invocation_context, "session", None)
    session_id = getattr(session, "id", None) or "orchestrator-session"

    response_text = await OrchestratorA2aPipeline.run_turn(
        user_text=user_text,
        state=callback_context.state,
        session_id=session_id,
    )

    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part.from_text(text=response_text)],
        )
    )

