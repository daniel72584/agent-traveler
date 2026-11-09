"""A2A HTTP Server entrypoint for the customer-facing Orchestrator Agent (`adk_agents/orchestrator/a2a_server.py`).

Exposes `travel_customer_orchestrator_agent` via the Agent-to-Agent (A2A) protocol.
Default port: `8000`.
"""

from __future__ import annotations

import os
from starlette.applications import Starlette

from google.adk.a2a.utils.agent_to_a2a import to_a2a

from adk_agents.orchestrator.agent import create_orchestrator_agent

ORCHESTRATOR_A2A_HOST = os.environ.get("ORCHESTRATOR_A2A_HOST", "localhost")
ORCHESTRATOR_A2A_PORT = int(os.environ.get("ORCHESTRATOR_A2A_PORT", "8000"))


def create_orchestrator_a2a_app(
    host: str = ORCHESTRATOR_A2A_HOST,
    port: int = ORCHESTRATOR_A2A_PORT,
) -> Starlette:
    """Builds a Starlette A2A server application wrapping the customer-facing Orchestrator Agent."""
    agent = create_orchestrator_agent()
    return to_a2a(agent, host=host, port=port, protocol="http")


app = create_orchestrator_a2a_app()

