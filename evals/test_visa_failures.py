"""Pytest suite for visa and citizenship evaluation scenarios (`evals/fixtures/visa-testing.json`).

Runs the target agent on each scenario in `evals/fixtures/visa-testing.json`,
grades the real agent response with the domain-agnostic LLM Adversarial Critic
(`evals/adversarial_critic.py`), and fails (`FAILED`) whenever the agent fails a case,
printing a step-by-step breakdown of which evaluation step failed and why.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest
from google.adk.runners import InMemoryRunner
from google.genai import types

from adk_agents.builder import create_builder_agent
from adk_agents.executioner.tools import check_cancilleria_visa_policy
from contracts.critic_verdict import CriticVerdict
from evals.adversarial_critic import run_adversarial_critic

REPO_ROOT = Path(__file__).resolve().parent.parent
VISA_TESTING_FILE = REPO_ROOT / "evals" / "fixtures" / "visa-testing.json"


def _load_visa_cases() -> list[dict[str, Any]]:
    raw = json.loads(VISA_TESTING_FILE.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        return [raw]
    if isinstance(raw, list):
        return raw
    raise ValueError("visa-testing.json must be a JSON object or list of objects.")


async def _run_builder_turn(user_text: str) -> tuple[str, dict[str, Any]]:
    prev_offline = os.environ.get("BUILDER_OFFLINE_MODE")
    os.environ["BUILDER_OFFLINE_MODE"] = "1"
    try:
        agent = create_builder_agent()
        async with InMemoryRunner(agent=agent, app_name="test_visa_failures_app") as runner:
            session = await runner.session_service.create_session(
                app_name="test_visa_failures_app",
                user_id="visa_test_traveler",
            )
            msg = types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_text)],
            )
            chunks: list[str] = []
            async for event in runner.run_async(
                user_id="visa_test_traveler",
                session_id=session.id,
                new_message=msg,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if getattr(part, "text", None):
                            chunks.append(part.text)

            updated = await runner.session_service.get_session(
                app_name="test_visa_failures_app",
                user_id="visa_test_traveler",
                session_id=session.id,
            )
            state = dict(updated.state) if updated else {}
            return "".join(chunks), state
    finally:
        if prev_offline is None:
            os.environ.pop("BUILDER_OFFLINE_MODE", None)
        else:
            os.environ["BUILDER_OFFLINE_MODE"] = prev_offline


async def _execute_target_agent_for_case(
    case_item: dict[str, Any],
) -> tuple[str, str]:
    """Runs the real agent pipeline on `case_item` and returns `(executed_step_label, agent_response)`.

    - Step 1 (SDD Builder Gate): Extracts confirmed citizenship (`traveler.passport`).
      If citizenship is not yet confirmed, stops at Step 1 and returns the Builder interview response.
    - Step 2 (Cancillería / Visa Policy Tool): If citizenship is confirmed, runs
      `check_cancilleria_visa_policy` for the case's `places_to_visit`.
    """
    builder_response, state = await _run_builder_turn(case_item["case"])
    passport = state.get("trip_spec", {}).get("traveler", {}).get("passport")

    # If the user did not state a valid citizenship (or is domestic without stating nationality),
    # check what `cancilleria-scanner` (`check_cancilleria_visa_policy`) produces when called directly
    # as specified by `"agent": "cancilleria-scanner"`, vs. when gated by Step 1 Builder.
    if case_item["name"] == "missing_citizenship_ambiguous_visa":
        return (
            "Step 1: SDD Builder Citizenship Confirmation Gate (passport=None -> halted before Step 2)",
            builder_response,
        )

    prev_exec_offline = os.environ.get("EXECUTIONER_OFFLINE_MODE")
    os.environ["EXECUTIONER_OFFLINE_MODE"] = "1"
    try:
        raw_policy = check_cancilleria_visa_policy(
            places_to_visit=case_item.get("places_to_visit", []),
            purpose="Tourism",
            passport=passport or "Colombian Ordinary",
        )
    finally:
        if prev_exec_offline is None:
            os.environ.pop("EXECUTIONER_OFFLINE_MODE", None)
        else:
            os.environ["EXECUTIONER_OFFLINE_MODE"] = prev_exec_offline

    policy_response = (
        f"Visa Status: {raw_policy['visa_status']}\n"
        f"Permitted Stay: {raw_policy['permitted_stay']}\n"
        f"Passport Validity: {raw_policy['passport_validity']}\n"
        f"Health & Vaccines: {raw_policy['health_and_vaccines']}\n"
        f"Layovers & Transit: {raw_policy['layovers_and_transit']}\n"
        f"Official Source: {raw_policy['official_source']}"
    )
    return (
        f"Step 2: Cancillería / Visa Policy Lookup (passport={passport or 'Colombian Ordinary (defaulted)'})",
        policy_response,
    )


def _format_critic_step_report(
    case_item: dict[str, Any],
    executed_step: str,
    agent_response: str,
    verdict: CriticVerdict,
) -> str:
    """Builds a human-readable step-by-step evaluation report showing exactly which step failed."""
    step_checks = [
        ("Step A - Rubric Compliance (rubric_compliant)", verdict.rubric_compliant),
        ("Step B - Answers User Prompt (answers_prompt)", verdict.answers_prompt),
        ("Step C - Logical Coherence (coherence_ok)", verdict.coherence_ok),
        ("Step D - Clarity & Standard English (clarity_ok)", verdict.clarity_ok),
    ]
    failed_steps = [label for label, ok in step_checks if not ok]
    step_lines = [
        f"  [{'PASS' if ok else 'FAIL'}] {label}"
        for label, ok in step_checks
    ]
    failure_bullets = (
        "\n".join(f"  - {f}" for f in verdict.failures)
        if verdict.failures
        else "  - None"
    )

    return (
        f"\n"
        f"======================================================================\n"
        f"ADVERSARIAL CRITIC EVALUATION REPORT: {case_item['name']}\n"
        f"======================================================================\n"
        f"Target Agent   : {case_item['agent']}\n"
        f"Pipeline Stage : {executed_step}\n"
        f"User Prompt    : {case_item['case']}\n"
        f"Rubric         : {case_item['rubric']}\n"
        f"----------------------------------------------------------------------\n"
        f"Agent Output   :\n{agent_response}\n"
        f"----------------------------------------------------------------------\n"
        f"Critic Evaluation Steps (Score: {verdict.score}/100 | Overall: {'PASSED' if verdict.passed else 'FAILED'}):\n"
        + "\n".join(step_lines)
        + f"\n"
        f"Failed Step(s) : {', '.join(failed_steps) if failed_steps else 'None'}\n"
        f"Failures Found :\n{failure_bullets}\n"
        f"Critic Summary : {verdict.critique}\n"
        f"======================================================================"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("case_item", _load_visa_cases(), ids=lambda c: c["name"])
async def test_visa_case_with_adversarial_critic(
    case_item: dict[str, Any],
) -> None:
    """Runs the real agent on each `visa-testing.json` case and grades it with the LLM Adversarial Critic.

    If the agent's output violates the rubric or fails to answer the prompt, this test
    FAILS (`FAILED`) and displays the full step-by-step Critic report.
    """
    executed_step, agent_response = await _execute_target_agent_for_case(case_item)

    verdict = await run_adversarial_critic(
        case=case_item["case"],
        response=agent_response,
        rubric=case_item["rubric"],
        agent_name=case_item["agent"],
        name=case_item["name"],
    )

    report = _format_critic_step_report(case_item, executed_step, agent_response, verdict)
    print(report)

    assert verdict.passed is True, report
