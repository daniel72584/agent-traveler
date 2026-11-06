"""Isolated test suite for the ADK Builder Agent (`adk_agents/builder`).

Verifies:
1. Zero dependencies on `executioner` or `revisor` agents.
2. Incomplete prompt triggers SDD Interview (tc-001 rubric compatibility).
3. Multi-turn SDD interview converges to `status == "validated"` and emits a valid YAML contract.
4. Reaching 10 attempts without completing the spec halts with `status == "failed_max_attempts"`.
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

from adk_agents.builder import create_builder_agent
from adk_agents.builder.prompts import MAX_SDD_ATTEMPTS
from evals.evaluator import TestEvaluator

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_FILE = REPO_ROOT / "evals" / "fixtures" / "sample_user_turns.json"
TEST_CASES_FILE = REPO_ROOT / "evals" / "test_cases.json"


async def run_builder_conversation(
    turns: list[str],
    offline: bool = True,
) -> tuple[list[str], dict[str, Any]]:
    """Runs a multi-turn conversation against an isolated ADK Builder agent."""
    prev_offline = os.environ.get("BUILDER_OFFLINE_MODE")
    if offline:
        os.environ["BUILDER_OFFLINE_MODE"] = "1"

    try:
        agent = create_builder_agent()
        async with InMemoryRunner(agent=agent, app_name="test_builder_app") as runner:
            session = await runner.session_service.create_session(
                app_name="test_builder_app",
                user_id="colombian_traveler",
            )

            responses: list[str] = []
            for turn_text in turns:
                user_msg = types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=turn_text)],
                )
                turn_chunks: list[str] = []
                async for event in runner.run_async(
                    user_id="colombian_traveler",
                    session_id=session.id,
                    new_message=user_msg,
                ):
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if getattr(part, "text", None):
                                turn_chunks.append(part.text)
                responses.append("".join(turn_chunks))

            updated_session = await runner.session_service.get_session(
                app_name="test_builder_app",
                user_id="colombian_traveler",
                session_id=session.id,
            )
            final_state = dict(updated_session.state) if updated_session else {}
            return responses, final_state
    finally:
        if prev_offline is None:
            os.environ.pop("BUILDER_OFFLINE_MODE", None)
        else:
            os.environ["BUILDER_OFFLINE_MODE"] = prev_offline


def test_builder_has_zero_sibling_dependencies() -> None:
    """Ensures `adk_agents/builder` imports nothing from `executioner` or `revisor`."""
    builder_dir = REPO_ROOT / "adk_agents" / "builder"
    forbidden_modules = {"adk_agents.executioner", "adk_agents.revisor", "executioner", "revisor"}

    for py_file in builder_dir.glob("*.py"):
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
async def test_builder_incomplete_prompt_triggers_sdd_interview() -> None:
    """Verifies that 'i wanna visit EEUU for 2 weeks' triggers the SDD interview and passes tc-001 rubric."""
    responses, state = await run_builder_conversation(
        ["i wanna visit EEUU for 2 weeks"],
        offline=True,
    )
    assert len(responses) == 1
    assert state.get("sdd_status") == "interviewing"
    assert state.get("sdd_attempt_count") == 1
    assert state["trip_spec"]["timing"]["duration_days"] == 14

    # Verify against existing tc-001 evaluator rubric
    tc_data = json.loads(TEST_CASES_FILE.read_text(encoding="utf-8"))
    tc_001 = tc_data["test_cases"][0]
    evaluator = TestEvaluator(
        rubric=tc_001["eval_rubric"],
        expected_behavior=tc_001["expected_behavior"],
    )
    eval_result = evaluator.evaluate(responses[0], tool_calls=[])
    assert eval_result["passed"] is True, f"Rubric failed: {eval_result}"


@pytest.mark.asyncio
async def test_builder_multi_turn_reaches_validated_spec() -> None:
    """Verifies that a 3-turn conversation produces a validated trip-spec YAML contract."""
    fixtures = json.loads(FIXTURES_FILE.read_text(encoding="utf-8"))
    scenario = fixtures["scenarios"][1]

    responses, state = await run_builder_conversation(scenario["turns"], offline=True)
    assert state.get("sdd_status") == "validated"
    assert state.get("sdd_attempt_count") == 3
    assert "```yaml" in responses[-1]
    assert 'status: validated' in responses[-1] or 'status: "validated"' in responses[-1]

    spec = state["trip_spec"]
    assert spec["origin"] == "Bogotá (BOG)"
    assert spec["destinations"]["places_to_visit"] == ["New York", "Miami"]
    assert spec["accommodation"]["kind"] == "hotel"
    assert spec["accommodation"]["room_type"] == "private_room"
    assert spec["accommodation"]["bathroom"] == "private_bathroom"
    assert spec["accommodation"]["stars"] == "3 stars"
    assert spec["accommodation"]["max_price_per_night"] == "80 USD"


@pytest.mark.asyncio
async def test_builder_enforces_10_max_attempts_limit() -> None:
    """Verifies that the Builder halts at MAX_SDD_ATTEMPTS (10) when fields remain missing."""
    fixtures = json.loads(FIXTURES_FILE.read_text(encoding="utf-8"))
    scenario = fixtures["scenarios"][2]
    assert len(scenario["turns"]) == MAX_SDD_ATTEMPTS

    responses, state = await run_builder_conversation(scenario["turns"], offline=True)
    assert state.get("sdd_attempt_count") == MAX_SDD_ATTEMPTS
    assert state.get("sdd_status") == "failed_max_attempts"
    assert "Maximum Attempts Reached" in responses[-1]
    assert "accommodation.bathroom" in responses[-1]
    assert "accommodation.max_price_per_night" in responses[-1]

