"""A2A HTTP Server entrypoint for the isolated Builder Agent (`adk_agents/builder/a2a_server.py`).

Exposes `sdd_builder_agent` via the Agent-to-Agent (A2A) protocol using Google ADK's `to_a2a`.
Default port: `8001`.
"""

from __future__ import annotations

import os
from starlette.applications import Starlette

from google.adk.a2a.utils.agent_to_a2a import to_a2a

from adk_agents.builder.agent import create_builder_agent

BUILDER_A2A_HOST = os.environ.get("BUILDER_A2A_HOST", "localhost")
BUILDER_A2A_PORT = int(os.environ.get("BUILDER_A2A_PORT", "8001"))


def create_builder_a2a_app(
    host: str = BUILDER_A2A_HOST,
    port: int = BUILDER_A2A_PORT,
) -> Starlette:
    """Builds a Starlette A2A server application wrapping the isolated Builder Agent."""
    agent = create_builder_agent()
    return to_a2a(agent, host=host, port=port, protocol="http")


app = create_builder_a2a_app()

