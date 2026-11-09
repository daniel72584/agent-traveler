"""End-to-end test suite for the 4-Agent A2A Architecture (`evals/test_orchestrator_a2a.py`).

Verifies:
1. Strict zero-import isolation: `adk_agents/orchestrator` imports nothing from
   `builder`, `executioner`, or `revisor`.
2. All 4 agents (`builder`, `executioner`, `revisor`, `orchestrator`) expose valid
   A2A Agent Cards at `/.well-known/agent-card.json` via `to_a2a()`.
3. Single Customer-Facing Agent Flow over A2A:
   - Customer talks ONLY to `travel_customer_orchestrator_agent`.
   - Incomplete prompt triggers `Builder` via A2A (`status == "interviewing"`) and does NOT
     call `Executioner` or `Revisor`.
   - Once SDD is completed on turn 3 (`status == "validated"`), `Orchestrator` automatically
     sends the `trip-spec` over A2A to `Executioner`, then sends the generated `TripReport`
     over A2A to `Revisor` (`decision == "APPROVE"`), and returns the complete verified
     report to the customer.
"""

from __future__ import annotations

import ast
from contextlib import AsyncExitStack
import json
import os
from pathlib import Path
from typing import Any, AsyncIterator

import httpx
import pytest
from google.adk.runners import InMemoryRunner
from google.genai import types
from starlette.applications import Starlette

from adk_agents.builder.a2a_server import create_builder_a2a_app
from adk_agents.executioner.a2a_server import create_executioner_a2a_app
from adk_agents.orchestrator import create_orchestrator_agent
from adk_agents.orchestrator.a2a_client import (
    A2aProtocolClient,
    register_httpx_client_factory,
)
from adk_agents.orchestrator.a2a_server import create_orchestrator_a2a_app
from adk_agents.revisor.a2a_server import create_revisor_a2a_app
from contracts.trip_report import REQUIRED_REPORT_HEADERS

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_FILE = REPO_ROOT / "evals" / "fixtures" / "sample_user_turns.json"


class _LifespanManager:
    """Runs a Starlette app's lifespan context so `to_a2a` routes are mounted for ASGI testing."""

    def __init__(self, app: Starlette) -> None:
        self.app = app
        self._stack = AsyncExitStack()

    async def __aenter__(self) -> Starlette:
        await self._stack.enter_async_context(self.app.router.lifespan_context(self.app))
        return self.app

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        await self._stack.aclose()


@pytest.fixture
async def a2a_cluster_apps() -> AsyncIterator[dict[str, Starlette]]:
    """Boots all 4 isolated A2A Starlette apps in-memory and binds ASGI httpx transports."""
    prev_env = {
        k: os.environ.get(k)
        for k in ("BUILDER_OFFLINE_MODE", "EXECUTIONER_OFFLINE_MODE", "REVISOR_OFFLINE_MODE")
    }
    os.environ["BUILDER_OFFLINE_MODE"] = "1"
    os.environ["EXECUTIONER_OFFLINE_MODE"] = "1"
    os.environ["REVISOR_OFFLINE_MODE"] = "1"

    builder_app = create_builder_a2a_app(host="localhost", port=8001)
    executioner_app = create_executioner_a2a_app(host="localhost", port=8002)
    revisor_app = create_revisor_a2a_app(host="localhost", port=8003)
    orchestrator_app = create_orchestrator_a2a_app(host="localhost", port=8000)

    url_map: dict[str, Starlette] = {
        "http://localhost:8001": builder_app,
        "http://localhost:8002": executioner_app,
        "http://localhost:8003": revisor_app,
        "http://localhost:8000": orchestrator_app,
    }

    def _asgi_client_factory(base_url: str) -> httpx.AsyncClient:
        clean_url = base_url.rstrip("/")
        target_app = url_map[clean_url]
        transport = httpx.ASGITransport(app=target_app)
        return httpx.AsyncClient(transport=transport, base_url=clean_url, timeout=60.0)

    async with (
        _LifespanManager(builder_app),
        _LifespanManager(executioner_app),
        _LifespanManager(revisor_app),
        _LifespanManager(orchestrator_app),
    ):
        register_httpx_client_factory(_asgi_client_factory)
        try:
            yield url_map
        finally:
            register_httpx_client_factory(None)
            for key, val in prev_env.items():
                if val is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = val


def test_orchestrator_has_zero_sibling_dependencies() -> None:
    """Ensures `adk_agents/orchestrator` imports nothing from `builder`, `executioner`, or `revisor`."""
    orch_dir = REPO_ROOT / "adk_agents" / "orchestrator"
    forbidden_modules = {
        "adk_agents.builder",
        "adk_agents.executioner",
        "adk_agents.revisor",
        "builder",
        "executioner",
        "revisor",
    }

    for py_file in orch_dir.glob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not any(
                        alias.name.startswith(f) for f in forbidden_modules
                    ), f"Forbidden import {alias.name} in {py_file}"
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert not any(
                    node.module.startswith(f) for f in forbidden_modules
                ), f"Forbidden import from {node.module} in {py_file}"


@pytest.mark.asyncio
async def test_all_four_agents_expose_valid_a2a_agent_cards(
    a2a_cluster_apps: dict[str, Starlette],
) -> None:
    """Verifies that all 4 agents serve their `/.well-known/agent-card.json` via `to_a2a`."""
    expected_names = {
        "http://localhost:8000": "travel_customer_orchestrator_agent",
        "http://localhost:8001": "sdd_builder_agent",
        "http://localhost:8002": "travel_executioner_agent",
        "http://localhost:8003": "sdd_revisor_agent",
    }

    for base_url, expected_agent_name in expected_names.items():
        card = await A2aProtocolClient.fetch_agent_card(base_url)
        assert card["name"] == expected_agent_name
        assert card.get("description"), f"Missing description in AgentCard for {expected_agent_name}"


@pytest.mark.asyncio
async def test_orchestrator_a2a_end_to_end_customer_journey(
    a2a_cluster_apps: dict[str, Starlette],
) -> None:
    """Verifies that the customer talks ONLY to Orchestrator while A2A coordinates Builder -> Executioner -> Revisor."""
    fixtures = json.loads(FIXTURES_FILE.read_text(encoding="utf-8"))
    turns: list[str] = fixtures["scenarios"][1]["turns"]

    orchestrator = create_orchestrator_agent()
    async with InMemoryRunner(
        agent=orchestrator,
        app_name="customer_facing_orchestrator_app",
    ) as runner:
        session = await runner.session_service.create_session(
            app_name="customer_facing_orchestrator_app",
            user_id="colombian_customer",
        )

        responses: list[str] = []
        for turn_idx, user_text in enumerate(turns):
            user_msg = types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_text)],
            )
            chunks: list[str] = []
            async for event in runner.run_async(
                user_id="colombian_customer",
                session_id=session.id,
                new_message=user_msg,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if getattr(part, "text", None):
                            chunks.append(part.text)
            turn_response = "".join(chunks)
            responses.append(turn_response)

            current_session = await runner.session_service.get_session(
                app_name="customer_facing_orchestrator_app",
                user_id="colombian_customer",
                session_id=session.id,
            )
            assert current_session is not None
            current_state = dict(current_session.state)

            if turn_idx < 2:
                # Turns 1 and 2: SDD is still incomplete -> only Builder A2A was called
                assert current_state.get("sdd_status") == "interviewing"
                assert "trip_report_markdown" not in current_state
                assert all(
                    step["step"] == "builder" for step in current_state.get("a2a_trace", [])
                )

        # Turn 3: SDD completes -> Orchestrator automatically triggers Executioner A2A and Revisor A2A!
        final_session = await runner.session_service.get_session(
            app_name="customer_facing_orchestrator_app",
            user_id="colombian_customer",
            session_id=session.id,
        )
        assert final_session is not None
        final_state = dict(final_session.state)

        assert final_state.get("sdd_status") == "validated"
        assert final_state["trip_spec"]["destinations"]["places_to_visit"] == [
            "New York",
            "Miami",
        ]

        # Verify A2A trace shows all 3 specialist agents were invoked in sequence
        trace_steps = [entry["step"] for entry in final_state["a2a_trace"]]
        assert trace_steps == ["builder", "builder", "builder", "executioner", "revisor"]

        # Verify Revisor A2A approved the Executioner's report
        assert final_state["revision_verdict"]["decision"] == "APPROVE"
        assert final_state["revision_verdict"]["score"] == 100

        # Verify the customer received the full TripReport + Revisor approval badge on Turn 3
        final_customer_response = responses[-1]
        for header in REQUIRED_REPORT_HEADERS:
            assert header in final_customer_response, f"Missing report header: {header}"
        assert "SDD Revisor A2A Audit: `APPROVE`" in final_customer_response

