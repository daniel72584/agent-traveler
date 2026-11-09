"""ADK lifecycle callbacks (`before_agent_callback`, `before_model_callback`) for Builder."""

from __future__ import annotations

import os
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

from adk_agents.builder.engine import SddLifecycleEngine, TripSpecStateRepository
from adk_agents.builder.extractor import HeuristicSpecExtractor
from adk_agents.builder.prompts import MAX_SDD_ATTEMPTS
from contracts.trip_spec import TripSpecPatch


def _extract_latest_user_text(llm_request: LlmRequest) -> str:
    """Extracts the latest user message text from `LlmRequest` contents."""
    for content in reversed(llm_request.contents or []):
        if content.role == "user" and content.parts:
            texts = [p.text for p in content.parts if getattr(p, "text", None)]
            if texts:
                return "\n".join(texts)
    return ""


def enforce_sdd_attempt_gate(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """ADK `before_agent_callback` enforcing the 10-attempt SDD limit.

    If `sdd_status` is already `validated`, allows follow-up user turns to refine or
    expand the `trip-spec` (e.g., adding more cities/zones or adjusting budget)
    without tripping the attempt limit.
    """
    state = callback_context.state

    if state.get(TripSpecStateRepository.STATUS_KEY) == "validated":
        return None

    current_attempt = TripSpecStateRepository.increment_attempt(state)
    if current_attempt > MAX_SDD_ATTEMPTS:
        result = SddLifecycleEngine.evaluate_and_persist(state, TripSpecPatch())
        return types.Content(
            role="model",
            parts=[types.Part.from_text(text=result["formatted_response"])],
        )

    return None


def deterministic_builder_fallback_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """ADK `before_model_callback` providing deterministic SDD turn processing offline."""
    offline_mode = os.environ.get("BUILDER_OFFLINE_MODE", "").lower() in ("1", "true", "yes")
    has_api_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_KEY"))

    if not offline_mode and has_api_key:
        return None

    user_text = _extract_latest_user_text(llm_request)
    extracted_patch = HeuristicSpecExtractor.extract(user_text)
    transition = SddLifecycleEngine.evaluate_and_persist(
        state=callback_context.state,
        patch=extracted_patch,
    )

    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part.from_text(text=transition["formatted_response"])],
        )
    )


def ensure_validated_yaml_in_response_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
    """ADK `after_model_callback` ensuring a validated `trip-spec` YAML block is always emitted."""
    state = callback_context.state
    if state.get(TripSpecStateRepository.STATUS_KEY) != "validated":
        return None

    # Do not modify tool-call intermediate turns; only enrich the final text response
    if llm_response.content and llm_response.content.parts:
        if any(getattr(p, "function_call", None) for p in llm_response.content.parts):
            return None
        existing_text = "\n".join(
            p.text for p in llm_response.content.parts if getattr(p, "text", None)
        )
        spec = TripSpecStateRepository.load(state)
        yaml_block = spec.to_yaml_block()
        if "```yaml" not in existing_text or "status: validated" not in existing_text:
            combined_text = (
                f"{existing_text.strip()}\n\n{yaml_block}"
                if existing_text.strip()
                else yaml_block
            )
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=combined_text)],
                )
            )
    return None


