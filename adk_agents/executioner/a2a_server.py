"""A2A HTTP Server entrypoint for the isolated Executioner Agent (`adk_agents/executioner/a2a_server.py`).

Exposes `travel_executioner_agent` via the Agent-to-Agent (A2A) protocol using Google ADK's `to_a2a`.
Default port: `8002`.
"""

from __future__ import annotations

import os
from starlette.applications import Starlette

from google.adk.a2a.utils.agent_to_a2a import to_a2a

from adk_agents.executioner.agent import create_executioner_agent

EXECUTIONER_A2A_HOST = os.environ.get("EXECUTIONER_A2A_HOST", "localhost")
EXECUTIONER_A2A_PORT = int(os.environ.get("EXECUTIONER_A2A_PORT", "8002"))


def create_executioner_a2a_app(
    host: str = EXECUTIONER_A2A_HOST,
    port: int = EXECUTIONER_A2A_PORT,
) -> Starlette:
    """Builds a Starlette A2A server application wrapping the isolated Executioner Agent."""
    agent = create_executioner_agent()
    return to_a2a(agent, host=host, port=port, protocol="http")


app = create_executioner_a2a_app()

