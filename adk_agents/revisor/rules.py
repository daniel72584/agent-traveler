"""Specification / Rule classes for the Revisor agent (`adk_agents/revisor/rules.py`)."""

from __future__ import annotations

import abc
from dataclasses import dataclass
import re
from typing import Any, Optional

from contracts.revision_verdict import AuditCheckItem
from contracts.trip_report import REQUIRED_REPORT_HEADERS
from contracts.trip_spec import TripSpec

_MULTIPLIER_MAP: dict[str, float] = {
    "M": 1_000_000.0,
    "MILLONES": 1_000_000.0,
    "MILLION": 1_000_000.0,
    "K": 1_000.0,
    "MIL": 1_000.0,
}


def _parse_usd_cap(price_str: str | None, duration_days: int = 14) -> float | None:
    if not price_str:
        return None
    cleaned = price_str.upper().replace(",", "")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(M|MILLONES|MILLION|K|MIL)?", cleaned)
    if not m:
        return None
    val = float(m.group(1))
    suffix = m.group(2) or ""
    val *= _MULTIPLIER_MAP.get(suffix, 1.0)
    if "COP" in cleaned:
        val /= 4180.0
    if "TOTAL" in cleaned and duration_days > 0:
        val /= duration_days
    return round(val, 2)


def _extract_max_nightly_usd_from_report(
    report_markdown: str,
    report_dict: dict[str, Any] | None = None,
) -> float | None:
    if isinstance(report_dict, dict):
        budget = report_dict.get("budget", {})
        if isinstance(budget, dict) and budget.get("max_recommended_nightly_usd") is not None:
            return float(budget["max_recommended_nightly_usd"])

    range_match = re.search(
        r"(\d+(?:\.\d+)?)\s*[–\-]\s*(\d+(?:\.\d+)?)\s*USD\s*/\s*(?:night|noche)",
        report_markdown,
        re.IGNORECASE,
    )
    if range_match:
        return float(range_match.group(2))

    single_match = re.search(
        r"(?:\$\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*USD)\s*/\s*(?:night|noche)",
        report_markdown,
        re.IGNORECASE,
    )
    if single_match:
        num = single_match.group(1) or single_match.group(2)
        return float(num)
    return None


@dataclass(frozen=True)
class AuditContext:
    """Immutable context passed into each `SddComplianceRule`."""

    spec: TripSpec
    report_markdown: str
    report_dict: Optional[dict[str, Any]] = None

    @property
    def lower_markdown(self) -> str:
        return self.report_markdown.lower()


@dataclass(frozen=True)
class RuleEvaluation:
    """Output of a single `SddComplianceRule` evaluation."""

    check: AuditCheckItem
    violations: list[str]
    requires_builder_retry: bool = False


class SddComplianceRule(abc.ABC):
    """Abstract base class for SDD compliance rules (Specification Pattern)."""

    check_name: str

    @abc.abstractmethod
    def evaluate(self, ctx: AuditContext) -> RuleEvaluation:
        """Evaluates the rule against `AuditContext`."""


class SpecCompletenessRule(SddComplianceRule):
    """Gate 1: Verifies that the `TripSpec` itself is complete and validated."""

    check_name = "sdd_spec_completeness"

    def evaluate(self, ctx: AuditContext) -> RuleEvaluation:
        missing = ctx.spec.missing_sdd_fields()
        passed = len(missing) == 0 and ctx.spec.status == "validated"
        details = (
            "TripSpec is complete and validated."
            if passed
            else f"TripSpec status='{ctx.spec.status}', missing fields: {missing}"
        )
        violations = (
            []
            if passed
            else [
                f"SDD TripSpec is incomplete or unvalidated (status={ctx.spec.status}, missing={missing})."
            ]
        )
        return RuleEvaluation(
            check=AuditCheckItem(check_name=self.check_name, passed=passed, details=details),
            violations=violations,
            requires_builder_retry=not passed,
        )


class ReportStructureRule(SddComplianceRule):
    """Gate 2: Verifies that all 8 mandatory report headers (`## 0` through `## 6`) exist."""

    check_name = "report_structure"

    def evaluate(self, ctx: AuditContext) -> RuleEvaluation:
        missing_headers = [h for h in REQUIRED_REPORT_HEADERS if h not in ctx.report_markdown]
        passed = len(missing_headers) == 0
        details = (
            "All 8 mandatory report sections are present."
            if passed
            else f"Missing report headers: {missing_headers}"
        )
        violations = (
            []
            if passed
            else [f"Report is missing mandatory sections: {', '.join(missing_headers)}."]
        )
        return RuleEvaluation(
            check=AuditCheckItem(check_name=self.check_name, passed=passed, details=details),
            violations=violations,
        )


class VisaCancilleriaRule(SddComplianceRule):
    """Gate 3: Verifies official Cancillería citation and 6-month passport validity rule."""

    check_name = "visa_cancilleria_gate"

    def evaluate(self, ctx: AuditContext) -> RuleEvaluation:
        has_cancilleria = "cancilleria.gov.co" in ctx.lower_markdown
        has_validity = "6 months" in ctx.lower_markdown or "6 meses" in ctx.lower_markdown
        passed = has_cancilleria and has_validity
        details = (
            "Official Cancillería source and 6-month passport validity rule verified."
            if passed
            else "Missing official cancilleria.gov.co citation or 6-month passport validity rule."
        )
        violations = (
            []
            if passed
            else [
                "Report lacks official cancilleria.gov.co source link or 6-month passport validity verification."
            ]
        )
        return RuleEvaluation(
            check=AuditCheckItem(check_name=self.check_name, passed=passed, details=details),
            violations=violations,
        )


class PlacesAndRouteRule(SddComplianceRule):
    """Gate 4: Verifies all `places_to_visit` are covered and mapped with a clean Google Maps URL."""

    check_name = "places_and_route_mapping"

    def evaluate(self, ctx: AuditContext) -> RuleEvaluation:
        missing_places = [
            place
            for place in ctx.spec.destinations.places_to_visit
            if place.lower() not in ctx.lower_markdown
        ]
        has_clean_maps = bool(
            re.search(
                r"https://www\.google\.com/maps/(?:dir/\?api=1|search/\?api=1)",
                ctx.report_markdown,
            )
        )
        passed = len(missing_places) == 0 and has_clean_maps
        details = (
            f"All places ({', '.join(ctx.spec.destinations.places_to_visit)}) and clean Google Maps API URL verified."
            if passed
            else f"Missing places: {missing_places}, has_clean_maps={has_clean_maps}"
        )
        violations: list[str] = []
        if missing_places:
            violations.append(
                f"Report omitted destination(s) required by SDD spec: {', '.join(missing_places)}."
            )
        if not has_clean_maps:
            violations.append(
                "Report is missing a clean Google Maps route link (https://www.google.com/maps/dir/?api=1&...)."
            )
        return RuleEvaluation(
            check=AuditCheckItem(check_name=self.check_name, passed=passed, details=details),
            violations=violations,
        )


class AccommodationBudgetRule(SddComplianceRule):
    """Gate 5: Verifies accommodation criteria and nightly budget cap compliance."""

    check_name = "accommodation_and_budget_cap"

    def evaluate(self, ctx: AuditContext) -> RuleEvaluation:
        acc = ctx.spec.accommodation
        criteria_matched = all(
            (field_val or "").lower() in ctx.lower_markdown
            for field_val in (acc.kind, acc.room_type, acc.bathroom)
        )

        spec_cap_usd = _parse_usd_cap(
            acc.max_price_per_night,
            duration_days=ctx.spec.timing.duration_days or 14,
        )
        report_max_usd = _extract_max_nightly_usd_from_report(
            ctx.report_markdown, ctx.report_dict
        )

        price_ok, price_detail = self._check_price_cap(spec_cap_usd, report_max_usd)
        passed = criteria_matched and price_ok

        violations: list[str] = []
        if not criteria_matched:
            violations.append(
                f"Report accommodation does not match SDD filters ({acc.kind}, {acc.room_type}, {acc.bathroom})."
            )
        if not price_ok:
            violations.append(price_detail)

        details = (
            f"Lodging matches SDD ({acc.kind}, {acc.room_type}, {acc.bathroom}) and respects budget ({price_detail})."
            if passed
            else f"Lodging mismatch: criteria_matched={criteria_matched}, {price_detail}"
        )
        return RuleEvaluation(
            check=AuditCheckItem(check_name=self.check_name, passed=passed, details=details),
            violations=violations,
        )

    @staticmethod
    def _check_price_cap(
        spec_cap_usd: float | None,
        report_max_usd: float | None,
    ) -> tuple[bool, str]:
        if report_max_usd is None:
            return False, "Report does not state an explicit nightly USD accommodation price range."
        if spec_cap_usd is not None and report_max_usd > spec_cap_usd:
            return (
                False,
                f"Report lodging price ({report_max_usd} USD/night) exceeds SDD max_price_per_night cap ({spec_cap_usd} USD/night).",
            )
        return True, f"Spec cap={spec_cap_usd} USD, Report max={report_max_usd} USD"


class LiveFxAndWeatherRule(SddComplianceRule):
    """Gate 6: Verifies live COP exchange rate citation and weather alignment."""

    check_name = "live_fx_and_weather_alignment"

    def evaluate(self, ctx: AuditContext) -> RuleEvaluation:
        has_live_fx = bool(
            re.search(r"1\s*(?:USD|EUR)\s*=\s*[\d,\.]+\s*COP", ctx.report_markdown, re.IGNORECASE)
        )
        has_weather = bool(
            ctx.spec.preferred_weather
            and (
                ctx.spec.preferred_weather.lower() in ctx.lower_markdown
                or "weather" in ctx.lower_markdown
            )
        )
        passed = has_live_fx and has_weather
        details = (
            "Live COP exchange rate and preferred weather verification present."
            if passed
            else f"has_live_fx={has_live_fx}, has_weather={has_weather}"
        )
        violations: list[str] = []
        if not has_live_fx:
            violations.append("Report is missing a live USD/EUR to COP exchange rate citation.")
        if not has_weather:
            violations.append("Report failed to evaluate the user's preferred_weather.")
        return RuleEvaluation(
            check=AuditCheckItem(check_name=self.check_name, passed=passed, details=details),
            violations=violations,
        )

