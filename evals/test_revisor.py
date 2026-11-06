"""Isolated test suite for the ADK Revisor Agent (`adk_agents/revisor`).

Verifies:
1. Zero dependencies on `builder` or `executioner` agents.
2. Compliant TripReport matching all SDD constraints returns `decision == "APPROVE"` (`is_viable == True`).
3. Report violating SDD budget cap (`145 USD/night` > `80 USD/night`) and omitting a destination (`Osaka`)
   returns `decision == "REJECT"` (`is_viable == False`, `retry_target == "executioner"`) with specific violations.
4. Unvalidated/incomplete `TripSpec` returns `decision == "REJECT"` with `retry_target == "builder"`.
"""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path
from typing import Any

import pytest
from google.adk.runners import InMemoryRunner
from google.genai import types

from adk_agents.revisor import create_revisor_agent
from contracts.revision_verdict import RevisionVerdict

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_FIXTURES_FILE = REPO_ROOT / "evals" / "fixtures" / "sample_reports.json"
SPEC_FIXTURES_FILE = REPO_ROOT / "evals" / "fixtures" / "sample_trip_spec.json"


async def run_revisor_with_payload(
    payload_dict: dict[str, Any],
    offline: bool = True,
) -> tuple[RevisionVerdict, dict[str, Any]]:
    """Runs the isolated ADK Revisor agent with a JSON payload of `{trip_spec, report_markdown}`."""
    prev_offline = os.environ.get("REVISOR_OFFLINE_MODE")
    if offline:
        os.environ["REVISOR_OFFLINE_MODE"] = "1"

    try:
        agent = create_revisor_agent()
        async with InMemoryRunner(agent=agent, app_name="test_revisor_app") as runner:
            session = await runner.session_service.create_session(
                app_name="test_revisor_app",
                user_id="colombian_traveler",
            )
            user_msg = types.Content(
                role="user",
                parts=[types.Part.from_text(text=json.dumps(payload_dict))],
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
                app_name="test_revisor_app",
                user_id="colombian_traveler",
                session_id=session.id,
            )
            state = dict(updated_session.state) if updated_session else {}
            verdict = RevisionVerdict.model_validate_json("".join(chunks))
            return verdict, state
    finally:
        if prev_offline is None:
            os.environ.pop("REVISOR_OFFLINE_MODE", None)
        else:
            os.environ["REVISOR_OFFLINE_MODE"] = prev_offline


def test_revisor_has_zero_sibling_dependencies() -> None:
    """Ensures `adk_agents/revisor` imports nothing from `builder` or `executioner`."""
    rev_dir = REPO_ROOT / "adk_agents" / "revisor"
    forbidden_modules = {"adk_agents.builder", "adk_agents.executioner", "builder", "executioner"}

    for py_file in rev_dir.glob("*.py"):
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
async def test_revisor_approves_compliant_report() -> None:
    """Verifies that a report meeting all SDD criteria is APPROVED (`is_viable=True`)."""
    fixtures = json.loads(REPORTS_FIXTURES_FILE.read_text(encoding="utf-8"))
    verdict, state = await run_revisor_with_payload(fixtures["compliant_case"], offline=True)

    assert verdict.decision == "APPROVE"
    assert verdict.is_viable is True
    assert verdict.retry_target == "none"
    assert verdict.score == 100
    assert verdict.violations == []
    assert state["revision_verdict"]["decision"] == "APPROVE"


@pytest.mark.asyncio
async def test_revisor_rejects_over_budget_and_missing_city_report() -> None:
    """Verifies that Revisor REJECTS a report exceeding max_price_per_night and omitting Osaka."""
    fixtures = json.loads(REPORTS_FIXTURES_FILE.read_text(encoding="utf-8"))
    verdict, state = await run_revisor_with_payload(
        fixtures["over_budget_and_missing_city_case"],
        offline=True,
    )

    assert verdict.decision == "REJECT"
    assert verdict.is_viable is False
    assert verdict.retry_target == "executioner"
    assert verdict.score < 100
    joined_violations = " ".join(verdict.violations)
    assert "Osaka" in joined_violations
    assert "exceeds SDD max_price_per_night cap" in joined_violations
    assert state["revision_verdict"]["decision"] == "REJECT"


@pytest.mark.asyncio
async def test_revisor_routes_to_builder_when_spec_incomplete() -> None:
    """Verifies that Revisor routes back to `builder` when the TripSpec itself is incomplete."""
    spec_fixtures = json.loads(SPEC_FIXTURES_FILE.read_text(encoding="utf-8"))
    report_fixtures = json.loads(REPORTS_FIXTURES_FILE.read_text(encoding="utf-8"))

    payload = {
        "trip_spec": spec_fixtures["incomplete_spec"]["trip_spec"],
        "report_markdown": report_fixtures["compliant_case"]["report_markdown"],
    }
    verdict, _ = await run_revisor_with_payload(payload, offline=True)

    assert verdict.decision == "REJECT"
    assert verdict.is_viable is False
    assert verdict.retry_target == "builder"

