"""ADK FunctionTools and RemoteA2aAgent descriptors for the customer-facing Orchestrator Agent."""

from __future__ import annotations

import json
from typing import Any, Optional

from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.tool_context import ToolContext

from adk_agents.orchestrator.a2a_client import A2aProtocolClient
from adk_agents.orchestrator.prompts import (
    AGENT_CARD_WELL_KNOWN_PATH,
    BUILDER_A2A_URL,
    EXECUTIONER_A2A_URL,
    REVISOR_A2A_URL,
)


def create_remote_a2a_subagents(
    builder_url: str = BUILDER_A2A_URL,
    executioner_url: str = EXECUTIONER_A2A_URL,
    revisor_url: str = REVISOR_A2A_URL,
) -> list[RemoteA2aAgent]:
    """Builds the 3 ADK `RemoteA2aAgent` descriptors pointing to the specialist A2A servers."""
    return [
        RemoteA2aAgent(
            name="sdd_builder_a2a",
            description="Remote A2A Builder Agent that conducts the SDD interview (max 10 attempts).",
            agent_card=f"{builder_url.rstrip('/')}{AGENT_CARD_WELL_KNOWN_PATH}",
        ),
        RemoteA2aAgent(
            name="travel_executioner_a2a",
            description="Remote A2A Executioner Agent that generates the TripReport from a validated trip-spec.",
            agent_card=f"{executioner_url.rstrip('/')}{AGENT_CARD_WELL_KNOWN_PATH}",
        ),
        RemoteA2aAgent(
            name="sdd_revisor_a2a",
            description="Remote A2A Revisor Agent that audits the TripReport against the SDD trip-spec.",
            agent_card=f"{revisor_url.rstrip('/')}{AGENT_CARD_WELL_KNOWN_PATH}",
        ),
    ]


async def delegate_to_builder_a2a(
    customer_message: str,
    tool_context: Optional[ToolContext] = None,
) -> dict[str, Any]:
    """ADK FunctionTool: Sends the customer's message over A2A to the Builder Agent (`:8001`)."""
    state = tool_context.state if tool_context is not None else {}
    context_id = state.get("builder_a2a_context_id", "builder-session")
    resp = await A2aProtocolClient.send_a2a_message(
        base_url=BUILDER_A2A_URL,
        text=customer_message,
        context_id=context_id,
    )
    return {
        "agent": resp.agent_name,
        "context_id": resp.context_id,
        "task_id": resp.task_id,
        "response": resp.text,
    }


async def delegate_to_executioner_a2a(
    validated_trip_spec_yaml: str,
    tool_context: Optional[ToolContext] = None,
) -> dict[str, Any]:
    """ADK FunctionTool: Sends a validated `trip-spec` over A2A to the Executioner Agent (`:8002`)."""
    state = tool_context.state if tool_context is not None else {}
    context_id = state.get("executioner_a2a_context_id", "executioner-session")
    resp = await A2aProtocolClient.send_a2a_message(
        base_url=EXECUTIONER_A2A_URL,
        text=validated_trip_spec_yaml,
        context_id=context_id,
    )
    state["trip_report_markdown"] = resp.text
    return {
        "agent": resp.agent_name,
        "context_id": resp.context_id,
        "task_id": resp.task_id,
        "report_markdown": resp.text,
    }


async def delegate_to_revisor_a2a(
    trip_spec_json: str,
    report_markdown: str,
    tool_context: Optional[ToolContext] = None,
) -> dict[str, Any]:
    """ADK FunctionTool: Sends `{trip_spec, report_markdown}` over A2A to the Revisor Agent (`:8003`)."""
    state = tool_context.state if tool_context is not None else {}
    context_id = state.get("revisor_a2a_context_id", "revisor-session")
    spec_obj = json.loads(trip_spec_json) if isinstance(trip_spec_json, str) else trip_spec_json
    payload = json.dumps(
        {
            "trip_spec": spec_obj,
            "report_markdown": report_markdown,
        }
    )
    resp = await A2aProtocolClient.send_a2a_message(
        base_url=REVISOR_A2A_URL,
        text=payload,
        context_id=context_id,
    )
    return {
        "agent": resp.agent_name,
        "context_id": resp.context_id,
        "task_id": resp.task_id,
        "verdict_json": resp.text,
    }

