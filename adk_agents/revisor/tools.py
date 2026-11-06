"""Thin ADK FunctionTool definitions for the Revisor agent (`adk_agents/revisor/tools.py`).

Delegates compliance rules to `rules.py`, audit aggregation to `engine.py`,
and ADK callbacks to `callbacks.py`.
"""

from __future__ import annotations

import json
from typing import Any

from adk_agents.revisor.engine import RevisorAuditEngine, parse_revisor_inputs
from contracts.trip_spec import TripSpec

evaluate_sdd_compliance = RevisorAuditEngine.evaluate


def audit_report_against_sdd(
    trip_spec_json: str,
    report_markdown: str,
) -> dict[str, Any]:
    """ADK FunctionTool: Audits a Trip Report Markdown string against a `TripSpec` JSON string."""
    raw = json.loads(trip_spec_json)
    payload = raw.get("trip_spec", raw) if isinstance(raw, dict) else {}
    spec = TripSpec.model_validate(payload)
    verdict = RevisorAuditEngine.evaluate(spec=spec, report_markdown=report_markdown)
    return verdict.model_dump(mode="json")


__all__ = [
    "RevisorAuditEngine",
    "audit_report_against_sdd",
    "evaluate_sdd_compliance",
    "parse_revisor_inputs",
]
