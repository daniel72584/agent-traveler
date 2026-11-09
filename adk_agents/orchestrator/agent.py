"""Customer-facing ADK Orchestrator Agent definition (`adk_agents/orchestrator/agent.py`).

Streams incremental A2A stage events (`sdd_builder_agent` -> `travel_executioner_agent`
-> `sdd_revisor_agent`) directly to the customer as each remote A2A agent finishes.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import AsyncGenerator

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.genai import types
from typing_extensions import override

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

load_dotenv(REPO_ROOT / ".env")
if os.environ.get("GEMINI_KEY") and not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_KEY"]
if os.environ.get("GEMINI_KEY") and not os.environ.get("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.environ["GEMINI_KEY"]

from adk_agents.orchestrator.callbacks import deterministic_orchestrator_a2a_callback
from adk_agents.orchestrator.pipeline import OrchestratorA2aPipeline
from adk_agents.orchestrator.prompts import ORCHESTRATOR_SYSTEM_INSTRUCTION
from adk_agents.orchestrator.tools import (
    delegate_to_builder_a2a,
    delegate_to_executioner_a2a,
    delegate_to_revisor_a2a,
)

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


def _extract_user_text_from_ctx(ctx: InvocationContext) -> str:
    """Extracts the latest user text message from `InvocationContext`."""
    if ctx.user_content and ctx.user_content.parts:
        texts = [p.text for p in ctx.user_content.parts if getattr(p, "text", None)]
        if texts:
            return "\n".join(texts)
    for event in reversed(ctx.session.events):
        if event.author == "user" and event.content and event.content.parts:
            texts = [p.text for p in event.content.parts if getattr(p, "text", None)]
            if texts:
                return "\n".join(texts)
    return ""


class StreamingCustomerOrchestratorAgent(Agent):
    """ADK Agent that streams incremental A2A stage events (`Builder` -> `Executioner` -> `Revisor`)."""

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        user_text = _extract_user_text_from_ctx(ctx)
        session_id = getattr(ctx.session, "id", None) or "orchestrator-session"

        async for stage_event in OrchestratorA2aPipeline.stream_turn_stages(
            user_text=user_text,
            state=ctx.session.state,
            session_id=session_id,
        ):
            yield Event(
                author=self.name,
                invocation_id=ctx.invocation_id,
                branch=ctx.branch,
                content=types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=stage_event.text)],
                ),
                actions=EventActions(state_delta=stage_event.state_delta),
            )


def create_orchestrator_agent(model: str = DEFAULT_MODEL) -> Agent:
    """Factory that builds the customer-facing streaming ADK Orchestrator Agent instance."""
    return StreamingCustomerOrchestratorAgent(
        name="travel_customer_orchestrator_agent",
        model=model,
        description=(
            "Single customer-facing Travel Orchestrator Agent that communicates with "
            "Builder, Executioner, and Revisor agents via the A2A protocol and streams "
            "each stage live to the customer."
        ),
        instruction=ORCHESTRATOR_SYSTEM_INSTRUCTION,
        tools=[
            delegate_to_builder_a2a,
            delegate_to_executioner_a2a,
            delegate_to_revisor_a2a,
        ],
        before_model_callback=deterministic_orchestrator_a2a_callback,
    )


# Exposed for `adk run adk_agents/orchestrator` and `adk web`
root_agent = create_orchestrator_agent()
