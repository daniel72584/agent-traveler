"""Isolated test suite for the ADK Executioner Agent (`adk_agents/executioner`).

Verifies:
1. Zero dependencies on `builder` or `revisor` agents.
2. Incomplete `TripSpec` is rejected at the Executioner entry gate.
3. Validated `TripSpec` orchestrates Steps 2-5 (Visa/Cancillería, Route Mapping & Weather,
   Flights from Colombia, and Price Scouting + Live FX) and outputs all required report sections.
4. Work-purpose spec triggers the Cancillería Golden Rule hard-stop alert.
"""

from __future__ import annotations

import ast
import copy
import json
import os
from pathlib import Path
from typing import Any

import pytest
from google.adk.runners import InMemoryRunner
from google.genai import types

from adk_agents.executioner import create_executioner_agent
from contracts.trip_report import REQUIRED_REPORT_HEADERS

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_FIXTURES_FILE = REPO_ROOT / "evals" / "fixtures" / "sample_trip_spec.json"


async def run_executioner_with_payload(
    payload_str: str,
    offline: bool = True,
) -> tuple[str, dict[str, Any]]:
    """Runs the isolated ADK Executioner agent with a single JSON/YAML payload."""
    prev_offline = os.environ.get("EXECUTIONER_OFFLINE_MODE")
    if offline:
        os.environ["EXECUTIONER_OFFLINE_MODE"] = "1"

    try:
        agent = create_executioner_agent()
        async with InMemoryRunner(agent=agent, app_name="test_executioner_app") as runner:
            session = await runner.session_service.create_session(
                app_name="test_executioner_app",
                user_id="colombian_traveler",
            )
            user_msg = types.Content(
                role="user",
                parts=[types.Part.from_text(text=payload_str)],
            )
            chunks: list[str] = []
            async for event in runner.run_async(
                user_id="colombian_traveler",
                session_id=session.id,
                new_message=user_msg,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if getattr(part, "text", None):
                            chunks.append(part.text)

            updated_session = await runner.session_service.get_session(
                app_name="test_executioner_app",
                user_id="colombian_traveler",
                session_id=session.id,
            )
            state = dict(updated_session.state) if updated_session else {}
            return "".join(chunks), state
    finally:
        if prev_offline is None:
            os.environ.pop("EXECUTIONER_OFFLINE_MODE", None)
        else:
            os.environ["EXECUTIONER_OFFLINE_MODE"] = prev_offline


def test_executioner_has_zero_sibling_dependencies() -> None:
    """Ensures `adk_agents/executioner` imports nothing from `builder` or `revisor`."""
    exec_dir = REPO_ROOT / "adk_agents" / "executioner"
    forbidden_modules = {"adk_agents.builder", "adk_agents.revisor", "builder", "revisor"}

    for py_file in exec_dir.glob("*.py"):
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
async def test_executioner_blocks_incomplete_trip_spec() -> None:
    """Verifies that Executioner refuses to run when given an incomplete `TripSpec`."""
    fixtures = json.loads(SPEC_FIXTURES_FILE.read_text(encoding="utf-8"))
    incomplete_json = json.dumps(fixtures["incomplete_spec"])

    response_text, state = await run_executioner_with_payload(incomplete_json, offline=True)
    assert "Executioner Gate Blocked: Incomplete `trip-spec`" in response_text
    assert "places_to_visit" in response_text
    assert "trip_report" not in state


@pytest.mark.asyncio
async def test_executioner_generates_complete_report_from_valid_spec() -> None:
    """Verifies that Executioner produces a full TripReport with all 0-6 sections from a valid spec."""
    fixtures = json.loads(SPEC_FIXTURES_FILE.read_text(encoding="utf-8"))
    valid_json = json.dumps(fixtures["valid_japan_spec"])

    response_text, state = await run_executioner_with_payload(valid_json, offline=True)

    for header in REQUIRED_REPORT_HEADERS:
        assert header in response_text, f"Missing required report section: {header}"

    assert "https://www.cancilleria.gov.co" in response_text
    assert "https://www.google.com/maps/dir/?api=1&origin=Tokyo&destination=Osaka&waypoints=Kyoto" in response_text
    assert "1 USD =" in response_text and "COP" in response_text

    report_dict = state["trip_report"]
    assert report_dict["visa_feasibility"]["is_entry_feasible"] is True
    assert report_dict["budget"]["max_recommended_nightly_usd"] <= 80.0


@pytest.mark.asyncio
async def test_executioner_flags_work_purpose_hard_stop() -> None:
    """Verifies that Executioner flags `is_entry_feasible=False` when purpose is Work."""
    fixtures = json.loads(SPEC_FIXTURES_FILE.read_text(encoding="utf-8"))
    work_spec = copy.deepcopy(fixtures["valid_japan_spec"])
    work_spec["trip_spec"]["traveler"]["purpose"] = "Work"

    response_text, state = await run_executioner_with_payload(json.dumps(work_spec), offline=True)
    assert "HARD STOP ALERT" in response_text
    assert state["trip_report"]["visa_feasibility"]["is_entry_feasible"] is False

