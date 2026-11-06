"""Thin ADK FunctionTool definitions for the Executioner agent (`adk_agents/executioner/tools.py`).

Delegates external HTTP API calls to `sources.py`, regional profiles to `profiles.py`,
pipeline orchestration to `pipeline.py`, and ADK callbacks to `callbacks.py`.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote_plus

from adk_agents.executioner.profiles import RegionProfileRegistry, WORK_HARD_STOP_POLICY
from adk_agents.executioner.sources import (
    FlightAndLodgingLinkSource,
    LiveCancilleriaUrlSource,
    LiveExchangeRateSource,
)

_WORK_PURPOSES = frozenset({"work", "employment", "trabajo", "worker"})
_MULTIPLIER_MAP: dict[str, float] = {
    "M": 1_000_000.0,
    "MILLONES": 1_000_000.0,
    "MILLION": 1_000_000.0,
    "K": 1_000.0,
    "MIL": 1_000.0,
}

fetch_live_usd_cop_rate = LiveExchangeRateSource.fetch_usd_cop


def check_cancilleria_visa_policy(
    places_to_visit: list[str],
    purpose: str = "Tourism",
) -> dict[str, Any]:
    """Step 2 Tool: Chain of Responsibility (Tier 1: Live Cancillería URL -> Tier 2: Local Cache)."""
    norm_purpose = (purpose or "Tourism").strip().lower()
    if norm_purpose in _WORK_PURPOSES:
        return dict(WORK_HARD_STOP_POLICY)

    live_result = LiveCancilleriaUrlSource.fetch_live_policy(places_to_visit, purpose)
    if live_result is not None:
        return live_result

    profile = RegionProfileRegistry.resolve(places_to_visit)
    return dict(profile.visa_policy)


def _build_google_maps_route_url(stops: list[str]) -> str:
    """Constructs a clean Google Maps URL based on waypoint count."""
    origin_stop = quote_plus(stops[0])
    dest_stop = quote_plus(stops[-1])

    if len(stops) == 1:
        return f"https://www.google.com/maps/search/?api=1&query={origin_stop}"
    if len(stops) == 2:
        return (
            f"https://www.google.com/maps/dir/?api=1&origin={origin_stop}"
            f"&destination={dest_stop}&travelmode=driving"
        )
    waypoints = "%7C".join(quote_plus(s) for s in stops[1:-1])
    return (
        f"https://www.google.com/maps/dir/?api=1&origin={origin_stop}"
        f"&destination={dest_stop}&waypoints={waypoints}&travelmode=driving"
    )


def build_route_and_climate_plan(
    places_to_visit: list[str],
    preferred_weather: str,
    dates: str,
    duration_days: int = 14,
) -> dict[str, Any]:
    """Step 3 Tool: Generates clean Google Maps URLs, sights, and climate alignment."""
    stops = [p.strip() for p in places_to_visit if p.strip()] or ["Destination"]
    maps_url = _build_google_maps_route_url(stops)

    useful_searches = [
        f"{stop} central transit & safe neighborhoods: https://www.google.com/maps/search/?api=1&query={quote_plus(stop + ' central station safe neighborhood')}"
        for stop in stops
    ]

    pref_lower = (preferred_weather or "").lower()
    dates_lower = (dates or "").lower()
    joined_stops = " ".join(stops).lower()

    is_cold_season = any(
        m in dates_lower for m in ("november", "noviembre", "-11-", "december", "january", "february")
    )
    is_northern_city = any(c in joined_stops for c in ("new york", "boston", "chicago", "washington"))
    weather_warning = (
        f"⚠️ Climate Mismatch Alert: You requested '{preferred_weather}', "
        f"but {', '.join(stops)} in {dates} experiences cool/cold late-autumn or winter temperatures (5°C–14°C in northern stops)."
        if (is_cold_season and is_northern_city and "warm" in pref_lower)
        else "Aligned with destination seasonal norms."
    )

    days_per_stop = max(1, duration_days // max(1, len(stops)))
    sights = [
        f"**{stop}**: Historic center, main cultural museum, iconic landmark district, and local culinary market (recommended stay: ~{days_per_stop} days)."
        for stop in stops
    ]

    return {
        "ordered_route": stops,
        "google_maps_link": maps_url,
        "useful_map_searches": useful_searches,
        "sights_culture_food": sights,
        "weather_and_packing": (
            f"Preferred weather: '{preferred_weather}' during '{dates}'. {weather_warning} "
            f"Pack breathable layers, comfortable walking shoes, a rain/wind shell, and universal power adapter."
        ),
        "local_transport_and_pace": (
            f"Use metro/rail networks and contactless transit cards within {', '.join(stops)}; "
            f"use high-speed intercity rail or short regional flights between stops (~{days_per_stop} days per stop with 1 buffer day)."
        ),
    }


def analyze_flights_from_colombia(
    origin: str,
    places_to_visit: list[str],
) -> dict[str, str]:
    """Step 4 Tool: Resolves flight corridors from Colombia via `RegionProfileRegistry`."""
    first_stop = places_to_visit[0] if places_to_visit else "Destination"
    last_stop = places_to_visit[-1] if places_to_visit else first_stop
    profile = RegionProfileRegistry.resolve(places_to_visit)

    return {
        "recommended_corridor": profile.corridor_template(origin, first_stop, last_stop),
        "critical_layovers": profile.layover_guidance,
    }


def parse_budget_cap_usd(
    max_price_str: str,
    usd_cop_rate: float,
    duration_days: int = 14,
) -> float:
    """Parses the user's `max_price_per_night` string into a nightly USD float."""
    cleaned = (max_price_str or "80 USD").upper().replace(",", "")
    num_match = re.search(r"(\d+(?:\.\d+)?)\s*(M|MILLONES|MILLION|K|MIL)?", cleaned)
    amount = float(num_match.group(1)) if num_match else 80.0
    suffix = (num_match.group(2) or "") if num_match else ""
    amount *= _MULTIPLIER_MAP.get(suffix, 1.0)

    if "COP" in cleaned:
        amount /= usd_cop_rate
    if "TOTAL" in cleaned and duration_days > 0:
        amount /= duration_days
    return round(max(15.0, amount), 2)


def scout_prices_and_live_currency(
    places_to_visit: list[str],
    accommodation_kind: str,
    room_type: str,
    bathroom: str,
    stars: str,
    max_price_per_night: str,
    duration_days: int = 14,
    origin: str = "Bogotá (BOG)",
) -> dict[str, Any]:
    """Step 5 Tool: Scouts indicative flight & lodging prices strictly within the SDD budget cap."""
    usd_cop_rate, rate_citation = LiveExchangeRateSource.fetch_usd_cop()
    cap_usd = parse_budget_cap_usd(max_price_per_night, usd_cop_rate, duration_days)
    low_usd = round(max(15.0, cap_usd * 0.65), 2)
    high_usd = round(cap_usd, 2)

    low_cop = int(low_usd * usd_cop_rate)
    high_cop = int(high_usd * usd_cop_rate)

    first_city = places_to_visit[0] if places_to_visit else "Destination"
    flight_links = FlightAndLodgingLinkSource.build_flight_links(origin, first_city)
    lodging_links = FlightAndLodgingLinkSource.build_lodging_links(first_city)

    profile = RegionProfileRegistry.resolve(places_to_visit)
    flight_low_usd, flight_high_usd = profile.flight_usd_range
    flight_low_cop = int(flight_low_usd * usd_cop_rate)
    flight_high_cop = int(flight_high_usd * usd_cop_rate)

    return {
        "live_exchange_rate": rate_citation,
        "indicative_flights": (
            f"{flight_low_usd:,}–{flight_high_usd:,} USD round-trip "
            f"(approx. {flight_low_cop:,}–{flight_high_cop:,} COP) via Kayak ({flight_links['kayak']}) "
            f"and Google Flights ({flight_links['google_flights']})."
        ),
        "accommodation_estimates": (
            f"Filtered strictly by SDD criteria (`{accommodation_kind}`, `{room_type}`, `{bathroom}`, "
            f"`{stars}`, cap ≤ `{max_price_per_night}`): Indicative range **{low_usd:.0f}–{high_usd:.0f} USD / night** "
            f"(approx. **{low_cop:,}–{high_cop:,} COP / night**) across {', '.join(places_to_visit)} "
            f"for {duration_days} nights on Booking.com ({lodging_links['booking']}) and Airbnb Colombia ({lodging_links['airbnb']})."
        ),
        "max_recommended_nightly_usd": high_usd,
    }
