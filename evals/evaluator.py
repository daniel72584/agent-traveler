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


EXPECTED_FLIGHT_SKILLS: tuple[str, ...] = (
    "google-flights-search",
    "kayak-flight-search",
    "skyscanner-flight-search",
    "momondo-flight-search",
    "kiwi-flight-search",
    "skiplagged-flight-search",
    "airfrance-flight-search",
    "avianca-flight-search",
    "ryanair-flight-search",
)

FORBIDDEN_TRACKING_PARAMS: tuple[str, ...] = (
    "gclid=",
    "gbraid=",
    "gad_source=",
    "utm_",
    "affilid=",
    "mkwid=",
)


class FlightRunEvaluator:
    """Evaluates saved `@ticket-searcher` runs in `run_fligth_agent/` across 7 compliance gates."""

    REQUIRED_REQUEST_KEYS: tuple[str, ...] = (
        "origin",
        "destination",
        "departure_date",
        "return_date",
        "passengers",
        "cabin_class",
        "baggage_type",
    )

    REQUIRED_SECTION_PREFIXES: tuple[str, ...] = (
        "## 1. Search Criteria",
        "## 2. Top 5 Ranked Flights",
        "## 3. All 9 Provider Skill Snapshots",
        "## 4. Booking & Transit Caveats",
    )

    def evaluate_execution(
        self,
        exec_record: dict[str, Any],
        markdown_text: str,
    ) -> dict[str, Any]:
        """Audits a single flight execution JSON record and its corresponding Markdown report."""
        checks: list[dict[str, Any]] = []
        violations: list[str] = []

        # Gate 1: Input & Search Criteria Completeness
        req = exec_record.get("request", {})
        missing_req_keys = [k for k in self.REQUIRED_REQUEST_KEYS if not req.get(k)]
        has_search_header = "## 1. Search Criteria" in markdown_text
        gate1_passed = len(missing_req_keys) == 0 and has_search_header
        if not gate1_passed:
            violations.append(
                f"Gate 1 (input_criteria_gate): Missing request keys={missing_req_keys}, has_header={has_search_header}"
            )
        checks.append(
            {
                "gate": "input_criteria_gate",
                "passed": gate1_passed,
                "details": (
                    "All 7 request parameters and Section 1 header present."
                    if gate1_passed
                    else f"Missing keys: {missing_req_keys}"
                ),
            }
        )

        # Gate 2: Live COP Currency Conversion & Math Accuracy
        rate = float(exec_record.get("usd_cop_rate", 0.0))
        live_fx_str = str(exec_record.get("live_exchange_rate", ""))
        has_md_fx = bool(re.search(r"1\s*USD\s*=\s*[\d,\.]+\s*COP", markdown_text))
        top_5 = exec_record.get("top_5_flights", [])
        math_mismatches: list[str] = []
        for flight in top_5:
            usd = float(flight.get("price_usd", 0))
            cop = int(flight.get("price_cop", 0))
            expected_cop = round(usd * rate)
            if abs(expected_cop - cop) > 5:
                math_mismatches.append(
                    f"Rank #{flight.get('rank')}: {usd} * {rate} = {expected_cop} != {cop}"
                )
            usd_int = int(usd)
            usd_patterns = (
                f"${usd_int} USD",
                f"${usd_int:,} USD",
                f"**${usd_int}**",
                f"**${usd_int:,}**",
                f"~${usd_int} USD",
                f"~${usd_int:,} USD",
            )
            if not any(pat in markdown_text for pat in usd_patterns):
                math_mismatches.append(f"Rank #{flight.get('rank')}: ${usd_int:,} USD missing in MD")
            if f"{cop:,}" not in markdown_text:
                math_mismatches.append(f"Rank #{flight.get('rank')}: {cop:,} COP missing in MD")

        gate2_passed = rate > 0 and bool(live_fx_str) and has_md_fx and len(math_mismatches) == 0
        if not gate2_passed:
            violations.append(
                f"Gate 2 (live_fx_math_gate): rate={rate}, has_md_fx={has_md_fx}, math_mismatches={math_mismatches}"
            )
        checks.append(
            {
                "gate": "live_fx_math_gate",
                "passed": gate2_passed,
                "details": (
                    f"Live FX rate (1 USD = {rate:,.2f} COP) verified and all 5 USD->COP conversions exact."
                    if gate2_passed
                    else f"FX issues: {math_mismatches}"
                ),
            }
        )

        # Gate 3: Report Section & Table Integrity
        missing_sections = [s for s in self.REQUIRED_SECTION_PREFIXES if s not in markdown_text]
        broken_url_lines = bool(re.search(r"https://[^\s|]+\n/[^\s|]+", markdown_text))
        gate3_passed = len(missing_sections) == 0 and not broken_url_lines
        if not gate3_passed:
            violations.append(
                f"Gate 3 (report_structure_gate): missing_sections={missing_sections}, broken_url_lines={broken_url_lines}"
            )
        checks.append(
            {
                "gate": "report_structure_gate",
                "passed": gate3_passed,
                "details": (
                    "All 4 mandatory section headers present and Markdown table rows intact."
                    if gate3_passed
                    else f"Missing headers={missing_sections}, broken_url_lines={broken_url_lines}"
                ),
            }
        )

        # Gate 4: Top 5 Ranking & Layover Safety (`layoff time`)
        ranks = [f.get("rank") for f in top_5]
        scores = [float(f.get("ranking_score", 0.0)) for f in top_5]
        scores_sorted = scores == sorted(scores, reverse=True)
        has_all_layovers = all(bool(f.get("layover_time")) for f in top_5)
        has_layoff_term = (
            "layover time" in markdown_text.lower() or "layoff time" in markdown_text.lower()
        )
        gate4_passed = (
            ranks == [1, 2, 3, 4, 5]
            and scores_sorted
            and has_all_layovers
            and has_layoff_term
        )
        if not gate4_passed:
            violations.append(
                f"Gate 4 (top_5_ranking_and_layover_gate): ranks={ranks}, scores_sorted={scores_sorted}, "
                f"has_all_layovers={has_all_layovers}, has_layoff_term={has_layoff_term}"
            )
        checks.append(
            {
                "gate": "top_5_ranking_and_layover_gate",
                "passed": gate4_passed,
                "details": (
                    f"Top 5 ranked descending ({scores[0]} -> {scores[-1]}) with explicit layover (`layoff time`) margins."
                    if gate4_passed
                    else f"Ranking/layover error: ranks={ranks}, scores={scores}"
                ),
            }
        )

        # Gate 5: All 9 Flight Provider Skills Coverage
        missing_skills = [sk for sk in EXPECTED_FLIGHT_SKILLS if sk not in markdown_text]
        gate5_passed = len(missing_skills) == 0
        if not gate5_passed:
            violations.append(f"Gate 5 (nine_skills_coverage_gate): missing skills={missing_skills}")
        checks.append(
            {
                "gate": "nine_skills_coverage_gate",
                "passed": gate5_passed,
                "details": (
                    "All 9 flight provider skills (`*-flight-search`) documented in Section 3."
                    if gate5_passed
                    else f"Missing skills: {missing_skills}"
                ),
            }
        )

        # Gate 6: Clean URL Normalization
        urls_in_md = re.findall(r"https?://[^\s)`|>]+", markdown_text)
        urls_in_json = [str(f.get("search_url", "")) for f in top_5]
        all_urls = urls_in_md + urls_in_json
        dirty_urls = [
            u for u in all_urls if any(param in u.lower() for param in FORBIDDEN_TRACKING_PARAMS)
        ]
        gate6_passed = len(all_urls) >= 9 and len(dirty_urls) == 0
        if not gate6_passed:
            violations.append(f"Gate 6 (url_normalization_gate): dirty_urls={dirty_urls}")
        checks.append(
            {
                "gate": "url_normalization_gate",
                "passed": gate6_passed,
                "details": (
                    f"Audited {len(all_urls)} URLs; zero tracking parameters found."
                    if gate6_passed
                    else f"Dirty URLs found: {dirty_urls}"
                ),
            }
        )

        # Gate 7: Colombian Passport Transit-Visa & Ticketing Safety
        lower_md = markdown_text.lower()
        has_schengen_check = "schengen" in lower_md and "colombian" in lower_md
        has_transit_safety = any(hub in markdown_text for hub in ("CDG", "FRA", "MAD", "AMS", "IST"))
        gate7_passed = has_schengen_check and has_transit_safety
        if not gate7_passed:
            violations.append(
                f"Gate 7 (colombian_visa_safety_gate): has_schengen_check={has_schengen_check}, has_transit_safety={has_transit_safety}"
            )
        checks.append(
            {
                "gate": "colombian_visa_safety_gate",
                "passed": gate7_passed,
                "details": (
                    "Colombian ordinary passport Schengen/transit-visa safety verified across all Top 5 hubs."
                    if gate7_passed
                    else "Missing Colombian passport transit-visa verification."
                ),
            }
        )

        # Gate 8: Humanizer & Data Provenance
        hype_words = (
            "seamless",
            "seamlessly",
            "rock-solid",
            "shines",
            "crucial",
            "pivotal",
            "groundbreaking",
            "zero self-transfer risk",
        )
        found_hype = [w for w in hype_words if w in lower_md]
        prose_no_urls = re.sub(r"https?://\S+", "", markdown_text)
        exclamations = prose_no_urls.count("!")
        em_dashes = prose_no_urls.count("—")
        has_provenance = any(
            tag in markdown_text
            for tag in ("Data Status:", "[Verified Live]", "[Indicative Estimate]")
        )
        is_v2 = str(exec_record.get("schema_version", "")) == "2.0"
        humanizer_issues: list[str] = []
        if found_hype:
            humanizer_issues.append(f"hype={found_hype}")
        if exclamations > 0:
            humanizer_issues.append(f"exclamations={exclamations}")
        if em_dashes > 2:
            humanizer_issues.append(f"em_dashes={em_dashes}")
        if not has_provenance:
            humanizer_issues.append("missing_provenance_label")

        gate8_passed = (len(humanizer_issues) == 0) if is_v2 else True
        if not gate8_passed:
            violations.append(
                f"Gate 8 (humanizer_and_provenance_gate): {', '.join(humanizer_issues)}"
            )
        checks.append(
            {
                "gate": "humanizer_and_provenance_gate",
                "passed": gate8_passed,
                "details": (
                    "Humanizer style and data provenance verified."
                    if not humanizer_issues
                    else (
                        f"Advisory (legacy schema): {', '.join(humanizer_issues)}"
                        if not is_v2
                        else f"Style/provenance issues: {', '.join(humanizer_issues)}"
                    )
                ),
            }
        )

        passed_gates = sum(1 for c in checks if c["passed"])
        total_gates = len(checks)
        score = round((passed_gates / total_gates) * 100, 1)
        passed = len(violations) == 0

        return {
            "execution_id": exec_record.get("execution_id", "unknown"),
            "markdown_file": exec_record.get("markdown_report_file", ""),
            "decision": "APPROVE" if passed else "REJECT",
            "passed": passed,
            "score": score,
            "passed_gates": passed_gates,
            "total_gates": total_gates,
            "checks": checks,
            "violations": violations,
        }

