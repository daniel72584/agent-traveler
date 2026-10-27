"""Test runner for agent-traveler evaluations using the Google Antigravity SDK.

Reads test specifications from evals/test_cases.json, runs them through the
configured agent supervisor, verifies rubric constraints, and saves execution
records.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from evals.evaluator import TestEvaluator
from google.antigravity import Agent, CapabilitiesConfig, LocalAgentConfig

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / ".agents" / "skills"
TEST_CASES_FILE = REPO_ROOT / "evals" / "test_cases.json"

# Load environment variables from .env if present
load_dotenv(REPO_ROOT / ".env")


def load_system_instructions() -> str:
    """Combines repository orchestration rules and the supervisor agent definition."""
    agents_rule = REPO_ROOT / "AGENTS.md"
    supervisor_path = REPO_ROOT / ".agents" / "agents" / "travel-supervisor.md"

    instructions = []
    if agents_rule.exists():
        instructions.append(agents_rule.read_text(encoding="utf-8"))
    if supervisor_path.exists():
        instructions.append(supervisor_path.read_text(encoding="utf-8"))

    return "\n\n---\n\n".join(instructions)


def mock_sdd_interview_response() -> tuple[str, list[dict[str, Any]]]:
    """Generates an authentic mock SDD interview response for dry-run validation."""
    response = (
        "### ✈️ Trip Specification Interview (SDD)\n"
        "To build your personalized, accurate trip report for your trip to the USA, "
        "please confirm your travel preferences:\n\n"
        "1. **🏨 Accommodation Preferences**:\n"
        "   - Kind of lodging: Hostels, hotels, apartments/Airbnb, or guesthouses?\n"
        "   - Room configuration: Private room or shared dorm room?\n"
        "   - Bathroom: Private bathroom or shared bathroom?\n"
        "   - Preferred standard: Preferred star rating (2★, 3★, 4★, boutique) or unrated?\n"
        "   - Max price: Maximum nightly budget cap (in COP or USD)?\n\n"
        "2. **📍 Places & Cities to Visit**:\n"
        "   - What specific cities, towns, or must-see landmarks do you want to explore?\n"
        "   - Do you have a preferred route sequence?\n\n"
        "3. **☀️ Preferred Weather & Climate**:\n"
        "   - What climate do you prefer (warm & sunny, mild spring, cool autumn, snow/winter)?\n"
        "   - Any conditions to avoid (rainy season, high heat/humidity)?\n\n"
        "4. **🗓️ Timing & Traveler Profile**:\n"
        "   - Approximate travel dates or travel month, and duration (e.g. 2 weeks)?\n"
        "   - Purpose of travel (Tourism, work, study)?\n"
        "   - Origin in Colombia (Bogotá BOG, Medellín MDE, etc.)?\n"
    )
    return response, []


async def run_antigravity_agent(
    user_query: str,
    system_instructions: str,
    api_key: str | None,
    model: str | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Spawns an Antigravity agent and chats with it using the local configuration."""
    config_kwargs: dict[str, Any] = {
        "system_instructions": system_instructions,
        "workspaces": [str(REPO_ROOT)],
        "skills_paths": [str(SKILLS_DIR)],
        "capabilities": CapabilitiesConfig(),
        "api_key": api_key,
    }
    if model:
        config_kwargs["model"] = model

    config = LocalAgentConfig(**config_kwargs)

    response_tokens: list[str] = []
    recorded_tool_calls: list[dict[str, Any]] = []

    async with Agent(config) as agent:
        response = await agent.chat(user_query)

        # Stream response tokens
        async for token in response:
            response_tokens.append(token)
            sys.stdout.write(token)
            sys.stdout.flush()

        # Capture tool calls if exposed on the response object
        if hasattr(response, "tool_calls"):
            try:
                async for tool_call in response.tool_calls:
                    recorded_tool_calls.append(
                        {
                            "name": getattr(tool_call, "name", str(tool_call)),
                            "args": getattr(tool_call, "args", {}),
                        }
                    )
            except Exception:
                pass

    return "".join(response_tokens), recorded_tool_calls


REPORTS_DIR = REPO_ROOT / "evals" / "reports"


def save_markdown_report(
    version: str,
    records: list[dict[str, Any]],
    test_cases: list[dict[str, Any]],
) -> Path:
    """Writes a human-readable markdown evaluation report keyed by version."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORTS_DIR / f"report_v{version}.md"

    passed_count = sum(1 for r in records if r["status"] == "PASSED")
    total_count = len(records)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        f"# Evaluation Report: v{version}",
        f"",
        f"- **Version**: `v{version}`",
        f"- **Timestamp**: {timestamp}",
        f"- **Summary**: {passed_count}/{total_count} tests passed",
        f"",
        f"---",
        f"",
    ]

    for record, tc in zip(records, test_cases):
        eval_res = record["eval_result"]
        lines.extend([
            f"## Test Case: `{tc['id']}`",
            f"- **Name**: {tc['name']}",
            f"- **Status**: `{record['status']}` ({record['duration_seconds']}s)",
            f"- **Execution Mode**: `{record['mode']}`",
            f"- **Input Prompt**: `{tc['input']['user_query']}`",
            f"",
            f"### Rubric Verification",
            f"- **Keywords Matched**: {', '.join(eval_res.get('matched_keywords', [])) or 'None'}",
            f"- **Keywords Missing**: {', '.join(eval_res.get('missing_keywords', [])) or 'None'}",
            f"- **Forbidden Patterns Found**: {', '.join(eval_res.get('forbidden_patterns_found', [])) or 'None'}",
            f"- **Forbidden Tool Calls**: {', '.join(eval_res.get('forbidden_tool_calls', [])) or 'None'}",
            f"- **Interview Triggered**: `{eval_res.get('interview_triggered', False)}`",
            f"- **Proceeded to Downstream Steps**: `{eval_res.get('proceeded_to_downstream', False)}`",
            f"",
            f"### Full Agent Response",
            f"",
            f"```markdown",
            record.get("full_response", "").strip(),
            f"```",
            f"",
            f"---",
            f"",
        ])

    report_file.write_text("\n".join(lines), encoding="utf-8")
    return report_file


async def run_test_case(
    test_case: dict[str, Any],
    system_instructions: str,
    use_mock: bool = False,
    api_key: str | None = None,
    model: str | None = None,
    version: str = "1.0.0",
) -> dict[str, Any]:
    """Runs an individual test case, collects response, and evaluates it."""
    test_id = test_case["id"]
    test_name = test_case["name"]
    user_query = test_case["input"]["user_query"]

    print(f"\n==================================================")
    print(f"Running Test: {test_id} (Version: v{version})")
    print(f"Title: {test_name}")
    print(f"Prompt: {user_query}")
    print(f"Mode: {'MOCK SIMULATION' if use_mock else f'ANTIGRAVITY SDK ({model or 'default'})'}")
    print(f"==================================================\n")

    start_time = time.perf_counter()

    if use_mock:
        response_text, tool_calls = mock_sdd_interview_response()
        print(response_text)
    else:
        response_text, tool_calls = await run_antigravity_agent(
            user_query=user_query,
            system_instructions=system_instructions,
            api_key=api_key,
            model=model,
        )

    duration = time.perf_counter() - start_time

    evaluator = TestEvaluator(
        rubric=test_case.get("eval_rubric", {}),
        expected_behavior=test_case.get("expected_behavior", {}),
    )
    result = evaluator.evaluate(response_text, tool_calls)

    status = "PASSED" if result["passed"] else "FAILED"
    print(f"\n--------------------------------------------------")
    print(f"Result: {status} (took {duration:.2f}s)")
    print(f"Keywords matched: {', '.join(result['matched_keywords'])}")
    if result["missing_keywords"]:
        print(f"Keywords missing: {', '.join(result['missing_keywords'])}")
    if result["forbidden_patterns_found"]:
        print(f"Forbidden patterns found: {', '.join(result['forbidden_patterns_found'])}")
    if result["forbidden_tool_calls"]:
        print(f"Forbidden tool calls: {', '.join(result['forbidden_tool_calls'])}")
    print(f"--------------------------------------------------\n")

    execution_record = {
        "execution_id": f"exec-v{version}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{test_id}",
        "version": version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "duration_seconds": round(duration, 2),
        "mode": "mock" if use_mock else f"antigravity_sdk ({model or 'default'})",
        "eval_result": result,
        "full_response": response_text,
    }

    return execution_record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run evals using Antigravity SDK")
    parser.add_argument("--test-id", help="Run a specific test case by ID")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode without calling live API")
    parser.add_argument("--api-key", help="Gemini API key (overrides GEMINI_API_KEY / GEMINI_KEY)")
    parser.add_argument("--model", help="Gemini model name (overrides GEMINI_MODEL)")
    parser.add_argument("--version", help="Spec/eval version (defaults to version in test_cases.json)")
    parser.add_argument("--no-update", action="store_true", help="Do not persist execution history to test_cases.json")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    if not TEST_CASES_FILE.exists():
        print(f"Error: Could not find {TEST_CASES_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(TEST_CASES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    version = args.version or data.get("version", "1.0.0")

    test_cases = data.get("test_cases", [])
    if args.test_id:
        test_cases = [tc for tc in test_cases if tc["id"] == args.test_id]
        if not test_cases:
            print(f"No test case found matching id: {args.test_id}", file=sys.stderr)
            sys.exit(1)

    system_instructions = load_system_instructions()

    api_key = (
        args.api_key
        or os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GEMINI_KEY")
    )
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key

    model = args.model or os.environ.get("GEMINI_MODEL")

    use_mock = args.mock
    if not use_mock and not api_key:
        print("Notice: No GEMINI_API_KEY or GEMINI_KEY found in environment or --api-key.")
        print("Falling back to --mock mode to verify test harness and evaluator rubric.")
        use_mock = True

    all_passed = True
    executed_records: list[dict[str, Any]] = []

    for tc in test_cases:
        record = await run_test_case(
            test_case=tc,
            system_instructions=system_instructions,
            use_mock=use_mock,
            api_key=api_key,
            model=model,
            version=version,
        )

        executed_records.append(record)

        if record["status"] != "PASSED":
            all_passed = False

        if not args.no_update:
            if "executions" not in tc:
                tc["executions"] = []
            tc["executions"].append(record)

    if not args.no_update:
        with open(TEST_CASES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"Updated {TEST_CASES_FILE} with latest test execution records.")

    # Write human-readable markdown report keyed by version
    report_path = save_markdown_report(version, executed_records, test_cases)
    print(f"Generated markdown report: {report_path}")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())
