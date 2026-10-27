"""Evaluation engine for agent-traveler test cases.

Checks agent output and tool activity against the rubric rules defined
in test_cases.json.
"""

from __future__ import annotations

import re
from typing import Any


class TestEvaluator:
    """Evaluates test run responses and tool calls against rubric definitions."""

    def __init__(self, rubric: dict[str, Any], expected_behavior: dict[str, Any]):
        self.rubric = rubric
        self.expected = expected_behavior

    def evaluate(self, response_text: str, tool_calls: list[dict[str, Any]]) -> dict[str, Any]:
        """Runs rubric checks on response text and recorded tool calls."""
        keywords_required = self.rubric.get("must_contain_keywords", [])
        forbidden_patterns = self.rubric.get("must_not_contain_patterns", [])
        forbidden_actions = self.expected.get("forbidden_actions_at_this_stage", [])

        # Check required keywords
        matched_keywords = []
        missing_keywords = []
        for kw in keywords_required:
            if re.search(rf"\b{re.escape(kw)}\b", response_text, re.IGNORECASE):
                matched_keywords.append(kw)
            else:
                missing_keywords.append(kw)

        # Check forbidden patterns in output text
        found_forbidden_patterns = []
        for pattern in forbidden_patterns:
            if pattern.lower() in response_text.lower():
                found_forbidden_patterns.append(pattern)

        # Check tool calls against forbidden actions
        tool_names = [call.get("name", "") for call in tool_calls]
        forbidden_tool_calls = []
        for call_name in tool_names:
            lowered = call_name.lower()
            if any(term in lowered for term in ["booking", "airbnb", "maps", "price_scout"]):
                forbidden_tool_calls.append(call_name)

        # Verify whether downstream sections were generated prematurely
        downstream_headers = ["## 1. Feasibility", "## 2. Route", "## 3. Flights", "## 4. Budget"]
        proceeded_downstream = any(h.lower() in response_text.lower() for h in downstream_headers)

        # Check if interview format was triggered
        interview_triggered = len(missing_keywords) == 0

        # Overall pass criteria
        passed = (
            len(missing_keywords) == 0
            and len(found_forbidden_patterns) == 0
            and len(forbidden_tool_calls) == 0
            and not proceeded_downstream
        )

        return {
            "passed": passed,
            "interview_triggered": interview_triggered,
            "proceeded_to_downstream": proceeded_downstream,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "forbidden_patterns_found": found_forbidden_patterns,
            "forbidden_tool_calls": forbidden_tool_calls,
        }
