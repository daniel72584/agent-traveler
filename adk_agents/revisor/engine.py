"""Audit engine and input parser for the Revisor agent (`adk_agents/revisor/engine.py`)."""

from __future__ import annotations

import json
import re
from typing import Any, Optional
import yaml

from adk_agents.revisor.rules import (
    AccommodationBudgetRule,
    AuditContext,
    LiveFxAndWeatherRule,
    PlacesAndRouteRule,
    ReportStructureRule,
    SddComplianceRule,
    SpecCompletenessRule,
    VisaCancilleriaRule,
)
from contracts.revision_verdict import AuditCheckItem, RevisionVerdict
from contracts.trip_spec import TripSpec


class RevisorAuditEngine:
    """Executes the registered `SddComplianceRule` chain to produce a `RevisionVerdict`."""

    RULES: tuple[SddComplianceRule, ...] = (
        SpecCompletenessRule(),
        ReportStructureRule(),
        VisaCancilleriaRule(),
        PlacesAndRouteRule(),
        AccommodationBudgetRule(),
        LiveFxAndWeatherRule(),
    )

    @classmethod
    def evaluate(
        cls,
        spec: Optional[TripSpec],
        report_markdown: str,
        report_dict: Optional[dict[str, Any]] = None,
    ) -> RevisionVerdict:
        if spec is None:
            return RevisionVerdict(
                decision="REJECT",
                is_viable=False,
                retry_target="builder",
                score=0,
                checks=[
                    AuditCheckItem(
                        check_name="sdd_spec_completeness",
                        passed=False,
                        details="No valid TripSpec was provided to the Revisor.",
                    )
                ],
                violations=["Missing TripSpec contract."],
                revision_instructions="Return to Builder agent to collect and validate the SDD trip-spec.",
            )

        ctx = AuditContext(spec=spec, report_markdown=report_markdown, report_dict=report_dict)
        evaluations = [rule.evaluate(ctx) for rule in cls.RULES]

        checks = [ev.check for ev in evaluations]
        violations = [v for ev in evaluations for v in ev.violations]
        needs_builder = any(ev.requires_builder_retry for ev in evaluations)

        passed_count = sum(1 for c in checks if c.passed)
        score = round((passed_count / len(checks)) * 100)

        if not violations:
            return RevisionVerdict(
                decision="APPROVE",
                is_viable=True,
                retry_target="none",
                score=score,
                checks=checks,
                violations=[],
                revision_instructions="Report satisfies all SDD trip-spec constraints and is viable to show to the user.",
            )

        retry_target = "builder" if needs_builder else "executioner"
        return RevisionVerdict(
            decision="REJECT",
            is_viable=False,
            retry_target=retry_target,
            score=score,
            checks=checks,
            violations=violations,
            revision_instructions=(
                f"Route back to `{retry_target}` and fix the following SDD violations: "
                + " ".join(f"({i + 1}) {v}" for i, v in enumerate(violations))
            ),
        )


def parse_revisor_inputs(
    raw_text: str,
    state: Any,
) -> tuple[Optional[TripSpec], str, Optional[dict[str, Any]]]:
    """Extracts `(TripSpec, report_markdown, report_dict)` from state or JSON/YAML payload."""
    spec_data = state.get("trip_spec")
    report_md = state.get("trip_report_markdown", "")
    report_dict = state.get("trip_report") if isinstance(state.get("trip_report"), dict) else None

    text = raw_text.strip()
    if text:
        fence_match = re.search(r"```(?:json|yaml)?\s*([\s\S]*?)```", text)
        candidate = fence_match.group(1).strip() if fence_match else text
        for loader in (json.loads, yaml.safe_load):
            try:
                loaded = loader(candidate)
                if isinstance(loaded, dict):
                    spec_data = loaded.get("trip_spec") if isinstance(loaded.get("trip_spec"), dict) else spec_data
                    report_md = loaded.get("report_markdown") if isinstance(loaded.get("report_markdown"), str) else report_md
                    raw_report = loaded.get("trip_report")
                    if isinstance(raw_report, dict):
                        report_dict = raw_report
                        report_md = report_md or raw_report.get("markdown_report", "")
                    elif isinstance(raw_report, str):
                        report_md = raw_report
                    break
            except Exception:
                continue

    spec = TripSpec.model_validate(spec_data) if isinstance(spec_data, dict) else None
    return spec, report_md, report_dict

