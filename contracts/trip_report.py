"""Structured Trip Report contract produced by the Executioner agent.

Matches the unified Final Output Structure defined in travel-supervisor.md.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


REQUIRED_REPORT_HEADERS: list[str] = [
    "## 0. Validated Trip Specification (trip-spec)",
    "## 1. Feasibility & Entry Requirements (Cancillería)",
    "## 2. Route & Interactive Map",
    "## 3. Flights & Connections from Colombia",
    "## 4. Budget & Price Estimates",
    "## 5. Sights, Culture & Local Food",
    "## 6. Logistics, Weather & Practical Tips",
    "## Assumptions & Caveats",
]


class VisaFeasibilitySection(BaseModel):
    """Section 1: Feasibility & Entry Requirements (Cancillería)."""

    is_entry_feasible: bool = Field(
        default=True,
        description="Whether entry is legally feasible for an ordinary Colombian passport within the user's dates.",
    )
    visa_status: str = Field(
        description="Visa-free, eVisa, Consular Visa Required, or Visa on Arrival."
    )
    permitted_stay: str = Field(description="Allowed duration of stay (e.g., '90 days').")
    passport_validity: str = Field(
        default="Minimum 6 months validity required from departure date."
    )
    health_and_vaccines: str = Field(
        description="Yellow fever certificate, medical insurance, or other health requirements."
    )
    layovers_and_transit: str = Field(
        description="Alerts regarding transit visas in layover countries (US, UK, Schengen, etc.)."
    )
    official_source: str = Field(
        description="Verified link from Cancillería or destination immigration authority."
    )


class RouteMapSection(BaseModel):
    """Section 2: Route & Interactive Map."""

    ordered_route: list[str] = Field(description="Ordered sequence of stops A -> B -> C.")
    google_maps_link: str = Field(
        description="Clean Google Maps route URL (/dir/?api=1&origin=...)."
    )
    useful_map_searches: list[str] = Field(
        default_factory=list,
        description="Useful map search links for transit stations, safe neighborhoods, etc.",
    )


class FlightsSection(BaseModel):
    """Section 3: Flights & Connections from Colombia."""

    recommended_corridor: str = Field(
        description="Operating airlines and realistic route options from BOG / MDE."
    )
    critical_layovers: str = Field(
        description="Connection warnings and transit visa caveats."
    )


class BudgetSection(BaseModel):
    """Section 4: Budget & Price Estimates."""

    live_exchange_rate: str = Field(
        description="Live FX rate with source and fetch timestamp (e.g., '1 USD = 4,180 COP per ExchangeRate-API, fetched 2026-11-05')."
    )
    indicative_flights: str = Field(
        description="Indicative round-trip flight price ranges in USD and COP."
    )
    accommodation_estimates: str = Field(
        description="Accommodation options/ranges on Booking / Airbnb matching kind, room_type, bathroom, stars, and max_price_per_night."
    )
    max_recommended_nightly_usd: float | None = Field(
        default=None,
        description="Numeric upper bound of recommended nightly lodging in USD for deterministic budget compliance verification.",
    )


class TripReport(BaseModel):
    """Complete structured output from the Executioner agent."""

    title: str = Field(description="Trip report title, e.g., 'Trip Report: Tokyo -> Kyoto -> Osaka'.")
    visa_feasibility: VisaFeasibilitySection
    route_map: RouteMapSection
    flights: FlightsSection
    budget: BudgetSection
    sights_culture_food: list[str] = Field(
        description="Top attractions, museums, and local culinary highlights."
    )
    weather_and_packing: str = Field(
        description="Weather comparison against preferred_weather and seasonal packing list."
    )
    local_transport_and_pace: str = Field(
        description="Local metro/train/taxi advice and suggested days per stop."
    )
    assumptions_and_caveats: list[str] = Field(
        default_factory=list,
        description="Items requiring manual verification before booking.",
    )
    markdown_report: str = Field(
        default="",
        description="Rendered unified Markdown report following the 0-6 section format.",
    )

    def render_markdown(self, spec_summary_lines: list[str] | None = None) -> str:
        """Renders the canonical Markdown report matching travel-supervisor.md."""
        spec_block = "\n".join(spec_summary_lines or ["- See validated trip-spec."])
        searches = "\n  ".join(f"- {s}" for s in self.route_map.useful_map_searches) or "- N/A"
        sights = "\n".join(f"- {item}" for item in self.sights_culture_food) or "- N/A"
        caveats = "\n".join(f"- {c}" for c in self.assumptions_and_caveats) or "- Verify live fares before booking."

        return (
            f"# {self.title}\n"
            f"*For travelers with ordinary Colombian passports*\n\n"
            f"## 0. Validated Trip Specification (trip-spec)\n"
            f"{spec_block}\n\n"
            f"## 1. Feasibility & Entry Requirements (Cancillería)\n"
            f"- **Visa Status**: {self.visa_feasibility.visa_status}\n"
            f"- **Permitted Stay**: {self.visa_feasibility.permitted_stay}\n"
            f"- **Passport Validity**: {self.visa_feasibility.passport_validity}\n"
            f"- **Health & Vaccines**: {self.visa_feasibility.health_and_vaccines}\n"
            f"- **Layovers & Transit**: {self.visa_feasibility.layovers_and_transit}\n"
            f"- **Official Source**: {self.visa_feasibility.official_source}\n\n"
            f"## 2. Route & Interactive Map\n"
            f"- **Ordered Route**: {' -> '.join(self.route_map.ordered_route)}\n"
            f"- **Google Maps Link**: {self.route_map.google_maps_link}\n"
            f"- **Useful Map Searches**:\n  {searches}\n\n"
            f"## 3. Flights & Connections from Colombia\n"
            f"- **Recommended Flight Corridor**: {self.flights.recommended_corridor}\n"
            f"- **Critical Layovers**: {self.flights.critical_layovers}\n\n"
            f"## 4. Budget & Price Estimates\n"
            f"- **Live Exchange Rate**: {self.budget.live_exchange_rate}\n"
            f"- **Indicative Flights**: {self.budget.indicative_flights}\n"
            f"- **Accommodation (Booking / Airbnb)**: {self.budget.accommodation_estimates}\n\n"
            f"## 5. Sights, Culture & Local Food\n"
            f"{sights}\n\n"
            f"## 6. Logistics, Weather & Practical Tips\n"
            f"- **Weather & Packing**: {self.weather_and_packing}\n"
            f"- **Local Transport & Pace**: {self.local_transport_and_pace}\n\n"
            f"## Assumptions & Caveats\n"
            f"{caveats}\n"
        )

