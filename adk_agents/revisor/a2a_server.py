"""A2A HTTP Server entrypoint for the isolated Revisor Agent (`adk_agents/revisor/a2a_server.py`).

Exposes `sdd_revisor_agent` via the Agent-to-Agent (A2A) protocol using Google ADK's `to_a2a`.
Default port: `8003`.
"""

from __future__ import annotations

import os
from starlette.applications import Starlette

from google.adk.a2a.utils.agent_to_a2a import to_a2a

from adk_agents.revisor.agent import create_revisor_agent

REVISOR_A2A_HOST = os.environ.get("REVISOR_A2A_HOST", "localhost")
REVISOR_A2A_PORT = int(os.environ.get("REVISOR_A2A_PORT", "8003"))


def create_revisor_a2a_app(
    host: str = REVISOR_A2A_HOST,
    port: int = REVISOR_A2A_PORT,
) -> Starlette:
    """Builds a Starlette A2A server application wrapping the isolated Revisor Agent."""
    agent = create_revisor_agent()
    return to_a2a(agent, host=host, port=port, protocol="http")


app = create_revisor_a2a_app()

