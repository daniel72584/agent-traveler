"""Pipeline Facade and input parser for the Executioner agent (`adk_agents/executioner/pipeline.py`)."""

from __future__ import annotations

import json
import re
from typing import Any, Optional
import yaml

from adk_agents.executioner.tools import (
    analyze_flights_from_colombia,
    build_route_and_climate_plan,
    check_cancilleria_visa_policy,
    scout_prices_and_live_currency,
)
from contracts.trip_report import (
    BudgetSection,
    FlightsSection,
    RouteMapSection,
    TripReport,
    VisaFeasibilitySection,
)
from contracts.trip_spec import TripSpec


def parse_trip_spec_input(raw_text: str, state: Any) -> Optional[TripSpec]:
    """Extracts a `TripSpec` from session state or from a JSON/YAML user message."""
    if isinstance(state.get("trip_spec"), dict):
        return TripSpec.model_validate(state["trip_spec"])

    text = raw_text.strip()
    if not text:
        return None

    fence_match = re.search(r"```(?:yaml|json)?\s*([\s\S]*?)```", text)
    candidate = fence_match.group(1).strip() if fence_match else text

    for loader in (json.loads, yaml.safe_load):
        try:
            loaded = loader(candidate)
            if isinstance(loaded, dict):
                payload = loaded.get("trip_spec", loaded)
                if isinstance(payload, dict):
                    spec = TripSpec.model_validate(payload)
                    state["trip_spec"] = spec.model_dump(mode="json")
                    return spec
        except Exception:
            continue

    return None


class TravelExecutionPipeline:
    """Pipeline Facade coordinating Steps 2-5 from a validated `TripSpec`."""

    @classmethod
    def execute(cls, spec: TripSpec) -> TripReport:
        visa_data = check_cancilleria_visa_policy(
            places_to_visit=spec.destinations.places_to_visit,
            purpose=spec.traveler.purpose or "Tourism",
        )
        route_data = build_route_and_climate_plan(
            places_to_visit=spec.destinations.route_order or spec.destinations.places_to_visit,
            preferred_weather=spec.preferred_weather or "mild",
            dates=spec.timing.dates or "TBD",
            duration_days=spec.timing.duration_days or 14,
        )
        flights_data = analyze_flights_from_colombia(
            origin=spec.origin or "Bogotá (BOG)",
            places_to_visit=spec.destinations.places_to_visit,
        )
        budget_data = scout_prices_and_live_currency(
            places_to_visit=spec.destinations.places_to_visit,
            accommodation_kind=spec.accommodation.kind or "hotel",
            room_type=spec.accommodation.room_type or "private_room",
            bathroom=spec.accommodation.bathroom or "private_bathroom",
            stars=spec.accommodation.stars or "3 stars",
            max_price_per_night=spec.accommodation.max_price_per_night or "80 USD",
            duration_days=spec.timing.duration_days or 14,
            origin=spec.origin or "Bogotá (BOG)",
        )

        spec_summary_lines = [
            f"- **Traveler Profile**: {spec.traveler.passport} | {spec.traveler.count} Traveler(s) | {spec.traveler.purpose}",
            f"- **Origin**: {spec.origin}",
            f"- **Places & Cities**: {', '.join(spec.destinations.places_to_visit)}",
            f"- **Dates & Duration**: {spec.timing.dates} ({spec.timing.duration_days} days)",
            f"- **Preferred Weather**: {spec.preferred_weather}",
            (
                f"- **Lodging Criteria**: Type: {spec.accommodation.kind} | "
                f"Room: {spec.accommodation.room_type} | Bath: {spec.accommodation.bathroom} | "
                f"Stars: {spec.accommodation.stars} | Max: {spec.accommodation.max_price_per_night}"
            ),
        ]

        caveats = [
            "All flight and accommodation figures are read-only indicative estimates; verify final taxes and fees at checkout.",
            "Confirm visa, ETIAS/EES, or consular appointment wait times on official Cancillería and embassy portals before purchasing non-refundable tickets.",
        ]
        if not visa_data["is_entry_feasible"]:
            caveats.insert(
                0,
                "⛔ HARD STOP ALERT: Entry is NOT legally feasible on a tourist exemption for the stated purpose. Obtain the required consular work/study visa before booking.",
            )

        report = TripReport(
            title=f"Trip Report: {' -> '.join(spec.destinations.places_to_visit)}",
            visa_feasibility=VisaFeasibilitySection(**visa_data),
            route_map=RouteMapSection(
                ordered_route=route_data["ordered_route"],
                google_maps_link=route_data["google_maps_link"],
                useful_map_searches=route_data["useful_map_searches"],
            ),
            flights=FlightsSection(**flights_data),
            budget=BudgetSection(**budget_data),
            sights_culture_food=route_data["sights_culture_food"],
            weather_and_packing=route_data["weather_and_packing"],
            local_transport_and_pace=route_data["local_transport_and_pace"],
            assumptions_and_caveats=caveats,
        )
        report.markdown_report = report.render_markdown(spec_summary_lines)
        return report


build_complete_trip_report = TravelExecutionPipeline.execute

