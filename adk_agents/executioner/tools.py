"""Thin ADK FunctionTool definitions for the Executioner agent (`adk_agents/executioner/tools.py`).

Delegates external HTTP API calls to `sources.py`, regional profiles to `profiles.py`,
pipeline orchestration to `pipeline.py`, and ADK callbacks to `callbacks.py`.
"""

from __future__ import annotations

import json
import math
import os
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


_CURATED_DESTINATION_HIGHLIGHTS: dict[str, dict[str, str]] = {
    "budapest": {
        "history": "Buda Castle District, Matthias Church, Fisherman's Bastion, Hungarian Parliament Building, Shoes on the Danube Bank, and Széchenyi/Gellért Art Nouveau thermal baths",
        "nature": "Normafa Ridge & Buda Hills trails (accessible by Cogwheel Railway), Margaret Island thermal gardens, Pál-völgyi Cave system, plus day-trip extensions to the **Danube Bend (Visegrád Citadel, Esztergom & Szentendre)** and **Eger + Bükk National Park**",
        "food": "Traditional goulash (*gulyás*), *lángos* with sour cream and cheese at Central Market Hall, chimney cake (*kürtőskalács*), and ruin bars in the Jewish Quarter (Szimpla Kert)",
        "remote_work": "Reliable 4G/5G and café Wi-Fi in District VII/V (Espresso Embassy, Kelet Kávézó), though prioritize dedicated work blocks in Estonia if desired",
    },
    "sopron": {
        "history": "Medieval Inner Town (*Belváros*), 13th-century Firewatch Tower (*Tűztorony*), Goat Church, Storno House, Roman Scarbantia Forum ruins, and nearby Baroque **Eszterháza Palace** in Fertőd",
        "nature": "**Fertő-Hanság National Park** (UNESCO Lake Neusiedl biosphere reserve with reed marshes, birdwatching & cycling), **Lővérek Hills** pine forest lookout towers (Károly-kilátó), and **Tihany Peninsula / Lake Balaton** volcanic uplands",
        "food": "World-renowned *Kékfrankos* (Blaufränkisch) red wine in historical stone cellars of the Sopron wine region, bean dishes (*babos ételek*), and walnut/poppy-seed strudel (*rétes*)",
        "remote_work": "Quiet historic boutique hotels and guesthouses around Várkerület ring road ideal for relaxed cultural pacing",
    },
    "eger": {
        "history": "16th-century Eger Castle, Northernmost Ottoman Minaret, Lyceum Astronomical Museum (Camera Obscura), and Minorite Baroque Church on Dobó István Square",
        "nature": "**Bükk National Park** karst plateaus, Szalajka Valley & Veil Waterfall (*Fátyol-vízesés*) in Szilvásvárad, and Egerszalók travertine salt hill thermal springs",
        "food": "*Egri Bikavér* (Bull's Blood) wine tasting in the **Valley of the Beautiful Women (*Szépasszony-völgy*)** volcanic tuff cellars",
        "remote_work": "Peaceful walkable historic core with cozy courtyard cafés",
    },
    "tallinn": {
        "history": "UNESCO Medieval Old Town (*Vanalinn*), Toompea Castle, Alexander Nevsky Cathedral, Kiek in de Kök fortifications, Kadriorg Baroque Palace, and Seaplane Harbour (*Lennusadam*)",
        "nature": "Day trip (45 min east) to **Lahemaa National Park** — **Viru Bog (*Viru raba*)** wooden boardwalk trail through glacial peatlands, **Jägala Waterfall** (often frozen or roaring in March), **Käsmu Captains' Village** boulder peninsula, and Palmse Manor",
        "food": "Nordic-Baltic cuisine in **Telliskivi Creative City** and Rotermann Quarter, black rye bread (*leib*), spiced Baltic sprat (*kiluvõileib*), elk soup at III Draakon, and craft Marzipan",
        "remote_work": "World-class digital nomad hub (Estonia e-Residency capital): Gigabit fiber Wi-Fi across 3-star hotels/hostels and coworking cafés in **Telliskivi Creative City** (Lift99, Fika, Literaat)",
    },
    "tartu": {
        "history": "1632 University of Tartu historic campus, Toomemägi (Cathedral Hill) Gothic brick ruins of Tartu Cathedral, Town Hall Square (*Raekoja plats* & Kissing Students fountain), and the striking Estonian National Museum (ERM) on a former Soviet airfield",
        "nature": "Emajõgi River valley trails, **Taevaskoja** sandstone cliffs & ancient pine forests (40 min south), **Alam-Pedja Nature Reserve** floodplains, and Lake Peipus (*Peipsi*) Old Believers' villages",
        "food": "Bohemian dining and specialty coffee in **Aparaaditehas** (The Widget Factory cultural complex), Karlova wooden district bakeries, and historic Gunpowder Cellar (*Püssirohukelder*)",
        "remote_work": "Estonia's intellectual & tech hub with ultra-fast Wi-Fi in **Aparaaditehas**, University libraries, and digital-friendly hostels/hotels",
    },
    "parnu": {
        "history": "17th-century Tallinn Gate (*Tallinna värav*), Red Tower (*Punane torn* — medieval prisoners' tower), functionalist 1930s Mud Baths & Rannahotell architecture, and wooden Art Nouveau villas",
        "nature": "**Pärnu Coastal Meadow Nature Reserve** boardwalk, frozen/early-spring Baltic Sea bay beach walk, and day trip (35 min) to **Soomaa National Park** famous for its 'Fifth Season' (*viies aastaaeg*) March snowmelt floodplains, bog-shoeing, and beaver trails",
        "food": "Smoked Baltic herring, coastal Estonian spa dining along Rüütli Street, and artisanal pastries at Supelsaksad in a preserved 19th-century wooden villa",
        "remote_work": "High-speed Estonian fiber Wi-Fi in peaceful off-season 3-star spa hotels and guesthouses—ideal for focused remote work sessions",
    },
    "pärnu": {
        "history": "17th-century Tallinn Gate (*Tallinna värav*), Red Tower (*Punane torn* — medieval prisoners' tower), functionalist 1930s Mud Baths & Rannahotell architecture, and wooden Art Nouveau villas",
        "nature": "**Pärnu Coastal Meadow Nature Reserve** boardwalk, early-spring Baltic Sea bay beach walk, and day trip (35 min) to **Soomaa National Park** famous for its 'Fifth Season' (*viies aastaaeg*) March snowmelt floodplains and bog-shoeing",
        "food": "Smoked Baltic herring, coastal Estonian spa dining along Rüütli Street, and artisanal pastries at Supelsaksad in a preserved 19th-century wooden villa",
        "remote_work": "High-speed Estonian fiber Wi-Fi in peaceful off-season 3-star spa hotels and guesthouses—ideal for focused remote work sessions",
    },
    "new york": {
        "history": "Statue of Liberty & Ellis Island, Metropolitan Museum of Art, Lower Manhattan Financial District, and Brooklyn Bridge",
        "nature": "Central Park Ramble & Conservatory Garden, Hudson River Park Greenway, High Line elevated park, and Hudson Valley day trips",
        "food": "Classic NY coal-oven pizza, Katz's Delicatessen pastrami, Chinatown dim sum, and Chelsea Market",
        "remote_work": "Abundant coworking spaces and hotel lobbies across Manhattan and Williamsburg",
    },
    "miami": {
        "history": "Art Deco Historic District in South Beach, Vizcaya Museum & Gardens, and Little Havana's Calle Ocho",
        "nature": "**Everglades National Park** airboat & Shark Valley trails, **Biscayne National Park** coral reefs, and Key Biscayne Bill Baggs Cape Florida Park",
        "food": "Cuban *ropa vieja*, *cafecito*, fresh stone crab claws, and Wynwood culinary markets",
        "remote_work": "Brickell and Wynwood cafés and hotels with fast fiber connectivity",
    },
    "tokyo": {
        "history": "Senso-ji Temple in Asakusa, Meiji Jingu Shrine, Imperial Palace East Gardens, and Yanaka old town",
        "nature": "Shinjuku Gyoen National Garden, Mount Takao forest trails, and day trips to Nikko or Hakone / Mount Fuji",
        "food": "Tsukiji Outer Market sushi, Shinjuku/Shibuya ramen alleys, and izakayas in Omoide Yokocho",
        "remote_work": "High-speed fiber Wi-Fi in business hotels and Shibuya/Marunouchi coworking lounges",
    },
    "kyoto": {
        "history": "Fushimi Inari Taisha torii gates, Kinkaku-ji (Golden Pavilion), Kiyomizu-dera, and Gion geisha district",
        "nature": "Arashiyama Bamboo Grove, Philosopher's Path canal walk, and Kurama-Kibune mountain forest trail",
        "food": "Nishiki Market street food, traditional *kaiseki* multi-course dining, and Uji matcha sweets",
        "remote_work": "Quiet machiya guesthouses and modern hotels near Kyoto Station with strong Wi-Fi",
    },
    "osaka": {
        "history": "16th-century Osaka Castle & Nishinomaru Garden, Shitenno-ji (Japan's oldest Buddhist temple), and Shinsekai",
        "nature": "Minoo Park waterfall & maple valley trail, and Osaka Castle plum/cherry blossom groves",
        "food": "Dotonbori street food capital: *takoyaki* (octopus balls), *okonomiyaki*, and Kuromon Ichiba Market",
        "remote_work": "Umeda and Namba hotels with high-speed internet and direct Shinkansen links",
    },
}


def _describe_stop_sights(stop: str, days_per_stop: int, activity_style: str = "", purpose: str = "") -> str:
    key = stop.strip().lower()
    matched = _CURATED_DESTINATION_HIGHLIGHTS.get(key)
    if matched is None:
        for k, val in _CURATED_DESTINATION_HIGHLIGHTS.items():
            if k in key or key in k:
                matched = val
                break

    if matched:
        remote_note = f" | **Remote Work & Wi-Fi**: {matched['remote_work']}" if (
            "remote" in (purpose + " " + activity_style).lower()
            or "work" in (purpose + " " + activity_style).lower()
            or key in ("tallinn", "tartu", "parnu", "pärnu")
        ) else ""
        return (
            f"**{stop}** (~{days_per_stop} days) — "
            f"**Historical**: {matched['history']} | "
            f"**Nature & Nearby Zones**: {matched['nature']} | "
            f"**Local Food**: {matched['food']}"
            f"{remote_note}."
        )

    return (
        f"**{stop}** (~{days_per_stop} days) — "
        f"**Historical & Cultural**: Old town heritage core, regional history museum, and architectural landmarks | "
        f"**Natural Zones**: Nearby national park trails, scenic viewpoints, and botanical/riverfront reserves | "
        f"**Culinary**: Traditional regional market and local specialties."
    )


def _curate_regional_bonus_zones(stops: list[str]) -> list[str]:
    joined = " ".join(stops).lower()
    bonuses: list[str] = []
    if any(k in joined for k in ("budapest", "sopron", "hungary", "eger", "balaton")):
        bonuses.append(
            "🇭🇺 **Bonus Hungary Historical & Natural Zones to Explore**: "
            "(1) **Danube Bend (*Dunakanyar*)**: Szentendre baroque river town, Visegrád medieval Royal Citadel overlooking the Danube gorge, and Esztergom Basilica (45–60 min from Budapest); "
            "(2) **Eger & Bükk National Park**: 16th-century castle siege history, Ottoman minaret, Szalajka Valley waterfalls, and volcanic wine cellars; "
            "(3) **Tihany Peninsula & Lake Balaton**: 1055 Benedictine Abbey, lavender volcanic hills, and geyser cones; "
            "(4) **Pannonhalma Archabbey & Fertő-Hanság National Park** (en route between Budapest and Sopron)."
        )
    if any(k in joined for k in ("tallinn", "tartu", "parnu", "pärnu", "estonia")):
        bonuses.append(
            "🇪🇪 **Bonus Estonia Historical & Natural Zones (+ Remote-Work Highlights)**: "
            "(1) **Lahemaa National Park** (coastal manor houses, Viru Bog wooden boardwalk through glacial wetlands, and Käsmu peninsula); "
            "(2) **Soomaa National Park** (between Tartu & Pärnu — famous in **March/April** for the *'Fifth Season'* snowmelt floodwaters where you can canoe through flooded forests and bog-shoe across peatlands); "
            "(3) **Lake Peipus (*Peipsi*) & Onion Route** (Old Believers' wooden villages and Alatskivi Castle near Tartu); "
            "(4) **Remote Work Setup**: Estonia offers pervasive Gigabit fiber Wi-Fi across 3-star hostels/hotels, public digital spaces, and nomad cafés in Tallinn's *Telliskivi* and Tartu's *Aparaaditehas*."
        )
    return bonuses


def build_route_and_climate_plan(
    places_to_visit: list[str],
    preferred_weather: str,
    dates: str,
    duration_days: int = 14,
    activity_style: str = "historical and natural exploration",
    purpose: str = "Tourism",
) -> dict[str, Any]:
    """Step 3 Tool: Generates clean Google Maps URLs, creative historical/natural sights, and climate alignment."""
    stops = [p.strip() for p in places_to_visit if p.strip()] or ["Destination"]
    maps_url = _build_google_maps_route_url(stops)

    useful_searches = [
        f"{stop} central transit & safe neighborhoods: https://www.google.com/maps/search/?api=1&query={quote_plus(stop + ' central station safe neighborhood')}"
        for stop in stops
    ]
    useful_searches.extend(
        f"{stop} national parks, nature trails & historical landmarks: https://www.google.com/maps/search/?api=1&query={quote_plus(stop + ' historical sites national park nature reserve')}"
        for stop in stops[:3]
    )

    pref_lower = (preferred_weather or "").lower()
    dates_lower = (dates or "").lower()
    joined_stops = " ".join(stops).lower()

    is_cold_season = any(
        m in dates_lower for m in ("november", "noviembre", "-11-", "december", "january", "february")
    )
    is_march = any(m in dates_lower for m in ("march", "marzo", "-03-"))
    is_northern_city = any(c in joined_stops for c in ("new york", "boston", "chicago", "washington"))
    is_baltic_or_central_eu = any(
        c in joined_stops for c in ("budapest", "sopron", "tallinn", "tartu", "parnu", "pärnu")
    )

    if is_cold_season and is_northern_city and "warm" in pref_lower:
        weather_warning = (
            f"⚠️ Climate Mismatch Alert: You requested '{preferred_weather}', "
            f"but {', '.join(stops)} in {dates} experiences cool/cold late-autumn or winter temperatures (5°C–14°C in northern stops)."
        )
    elif is_march and is_baltic_or_central_eu:
        weather_warning = (
            "March Transition Contrast: Hungary (Budapest/Sopron) enjoys crisp early-spring weather (4°C–13°C), "
            "whereas Estonia (Tallinn/Tartu/Pärnu) is still in late Nordic winter/early thaw (-4°C to +4°C with icy coastal winds and potential snow/slush). "
            "Pack thermal base layers, a windproof/waterproof insulated jacket, waterproof boots with grip for bog boardwalks & cobblestone streets, gloves, beanie, and swimwear for Hungarian thermal baths & Estonian saunas."
        )
    else:
        weather_warning = (
            "Aligned with destination seasonal norms. Pack breathable layers, comfortable walking shoes, "
            "a rain/wind shell, and universal power adapter."
        )

    days_per_stop = max(1, duration_days // max(1, len(stops)))
    sights = [
        _describe_stop_sights(stop, days_per_stop, activity_style=activity_style, purpose=purpose)
        for stop in stops
    ]
    sights.extend(_curate_regional_bonus_zones(stops))

    if is_baltic_or_central_eu:
        transport_pace = (
            f"Within **Hungary**, use MÁV/GYSEV direct intercity trains between Budapest Keleti and Sopron (~2.5h, passing near Győr/Pannonhalma) "
            f"and BKK passes in Budapest. From Central Europe (Budapest or nearby Vienna Airport `VIE`, just 1h from Sopron), take a short intra-Schengen flight (Ryanair/Wizz Air/airBaltic/Lufthansa) to **Tallinn (`TLL`)**. "
            f"Within **Estonia**, use **Elron** modern trains (with free high-speed Wi-Fi and power outlets) between Tallinn and Tartu (~2h) and **Lux Express** lounge buses between Tartu, Soomaa/Pärnu, and Tallinn (~{days_per_stop} days per stop; schedule Colombia remote-work hours in the afternoon/evening Estonian time, `UTC+2`, which aligns with `7:00 AM–12:00 PM` in Colombia `UTC-5`)."
        )
    else:
        transport_pace = (
            f"Use metro/rail networks and contactless transit cards within {', '.join(stops)}; "
            f"use high-speed intercity rail or short regional flights between stops (~{days_per_stop} days per stop with 1 buffer day)."
        )

    return {
        "ordered_route": stops,
        "google_maps_link": maps_url,
        "useful_map_searches": useful_searches,
        "sights_culture_food": sights,
        "weather_and_packing": f"Preferred weather: '{preferred_weather}' during '{dates}'. {weather_warning}",
        "local_transport_and_pace": transport_pace,
    }


def analyze_flights_from_colombia(
    origin: str,
    places_to_visit: list[str],
    activity_style: str = "",
) -> dict[str, str]:
    """Step 4 Tool: Resolves flight corridors from Colombia via `RegionProfileRegistry`."""
    first_stop = places_to_visit[0] if places_to_visit else "Destination"
    last_stop = places_to_visit[-1] if places_to_visit else first_stop
    profile = RegionProfileRegistry.resolve(places_to_visit)
    corridor = profile.corridor_template(origin, first_stop, last_stop)

    joined = " ".join(places_to_visit).lower()
    if "air france" in activity_style.lower() or any(
        c in joined for c in ("budapest", "sopron", "tallinn", "tartu", "parnu", "pärnu")
    ):
        corridor = (
            f"{origin} -> Paris Charles de Gaulle (CDG via **Air France** daily direct transatlantic flight) "
            f"or Madrid (MAD via Avianca/Iberia) -> {first_stop}; intra-European connection to Estonia (`TLL` via airBaltic/Lufthansa/LOT/Ryanair, "
            f"including convenient departure from Vienna `VIE` near Sopron or Budapest `BUD`) and open-jaw return from {last_stop}."
        )

    return {
        "recommended_corridor": corridor,
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
    low_usd = float(math.floor(max(15.0, cap_usd * 0.65)))
    high_usd = float(math.floor(cap_usd)) if cap_usd >= 16.0 else round(cap_usd, 2)

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
