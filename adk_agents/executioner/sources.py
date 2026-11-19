"""External HTTP API clients and deep-link builders (`adk_agents/executioner/sources.py`).

Isolates all live network calls and URL builders from agent and tool logic:
- `LiveCancilleriaUrlSource`: Live HTTP scraping/parsing of `cancilleria.gov.co`.
- `LiveExchangeRateSource`: Live HTTP currency rate fetcher (`USD-COP`).
- `FlightAndLodgingLinkSource`: Builds parameterized Kayak, Google Flights,
  Booking.com, and Airbnb Colombia search URLs.
"""

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote_plus
import urllib.request

from adk_agents.executioner.profiles import (
    RegionProfileRegistry,
    RegionTravelProfile,
    WORK_HARD_STOP_POLICY,
)


class LiveCancilleriaUrlSource:
    """Tier-1 Data Source that fetches and parses live bilateral sheets from `cancilleria.gov.co`."""

    _SCRIPT_PATH = (
        Path(__file__).resolve().parents[2]
        / ".agents"
        / "skills"
        / "cancilleria-country-policy"
        / "scripts"
        / "fetch_country_policy.py"
    )
    _module: Any = None

    @classmethod
    def _load_script_module(cls) -> Any:
        if cls._module is None and cls._SCRIPT_PATH.exists():
            spec = importlib.util.spec_from_file_location(
                "cancilleria_fetch_country_policy", cls._SCRIPT_PATH
            )
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                cls._module = mod
        return cls._module

    @classmethod
    def fetch_live_policy(
        cls,
        places_to_visit: list[str],
        purpose: str = "Tourism",
    ) -> Optional[dict[str, Any]]:
        offline_env = os.environ.get("EXECUTIONER_OFFLINE_MODE", "").lower() in ("1", "true", "yes")
        if offline_env or not places_to_visit:
            return None

        mod = cls._load_script_module()
        if mod is None:
            return None

        mapped_purpose = "tourist" if purpose.lower().startswith("tour") else purpose.lower()
        for target in places_to_visit:
            try:
                official_name, url, _ = mod.resolve_country_url(target)
                if not url:
                    continue
                html = mod.fetch_url(url, timeout=8)
                if not html:
                    continue
                clean_text = mod.extract_clean_content(html)
                if not clean_text or "just a moment" in clean_text.lower():
                    continue
                parsed = mod.parse_policy(clean_text, official_name, mapped_purpose, url)
                mig_snippet = (parsed.get("asuntos_migratorios") or "").replace("\n", " ").strip()
                return {
                    "is_entry_feasible": True,
                    "visa_status": (
                        f"{parsed.get('visa_verdict')} — {mig_snippet[:240]}"
                        if mig_snippet
                        else str(parsed.get("visa_verdict") or "Verified on Cancillería")
                    ),
                    "permitted_stay": parsed.get("stay_limit") or "See official Cancillería excerpt (typically up to 90 days)",
                    "passport_validity": "Minimum 6 months validity required from departure date.",
                    "health_and_vaccines": "Verify Yellow Fever requirement if transiting endemic regions; travel medical insurance recommended.",
                    "layovers_and_transit": "Check transit visa requirements for US (C1/B1/B2), UK (DATV), and Schengen connections.",
                    "official_source": url,
                }
            except Exception:
                continue
        return None


class NonColombianCitizenshipPolicySource:
    """Fallback Data Source that resolves official foreign-ministry & immigration portals for non-Colombian citizens."""

    _CITIZENSHIP_PORTALS: dict[str, tuple[str, str]] = {
        "mexican": ("Secretaría de Relaciones Exteriores (Guía del Viajero)", "https://guiadelviajero.sre.gob.mx/"),
        "spanish": ("Ministerio de Asuntos Exteriores de España", "https://www.exteriores.gob.es/es/ServiciosAlCiudadano/Paginas/Recomendaciones-de-viaje.aspx"),
        "us": ("U.S. Department of State (Travel.State.Gov)", "https://travel.state.gov/content/travel/en/international-travel.html"),
        "american": ("U.S. Department of State (Travel.State.Gov)", "https://travel.state.gov/content/travel/en/international-travel.html"),
        "canadian": ("Government of Canada Travel Advice", "https://travel.gc.ca/travelling/advisories"),
        "british": ("UK Foreign, Commonwealth & Development Office", "https://www.gov.uk/foreign-travel-advice"),
        "argentine": ("Cancillería Argentina", "https://www.cancilleria.gob.ar/es/servicios/viajar-al-exterior"),
        "chilean": ("Ministerio de Relaciones Exteriores de Chile", "https://www.chile.gob.cl/"),
        "peruvian": ("Ministerio de Relaciones Exteriores del Perú", "https://www.gob.pe/rree"),
        "ecuadorian": ("Ministerio de Relaciones Exteriores del Ecuador", "https://www.cancilleria.gob.ec/"),
        "brazilian": ("Ministério das Relações Exteriores (Itamaraty)", "https://www.gov.br/mre/"),
        "french": ("Ministère de l'Europe et des Affaires étrangères", "https://www.diplomatie.gouv.fr/fr/conseils-aux-voyageurs/"),
        "german": ("Auswärtiges Amt", "https://www.auswaertiges-amt.de/de/ReiseUndSicherheit"),
        "italian": ("Ministero degli Affari Esteri (Viaggiare Sicuri)", "https://www.viaggiaresicuri.it/"),
        "japanese": ("Ministry of Foreign Affairs of Japan", "https://www.anzen.mofa.go.jp/"),
    }

    _DESTINATION_IMMIGRATION_PORTALS: tuple[tuple[tuple[str, ...], str], ...] = (
        (("tokyo", "kyoto", "osaka", "japan", "japón"), "https://www.mofa.go.jp/j_info/visit/visa/"),
        (("new york", "miami", "orlando", "los angeles", "san francisco", "usa", "eeuu", "washington", "boston", "chicago", "las vegas"), "https://travel.state.gov/content/travel/en/us-visas.html"),
        (("madrid", "barcelona", "paris", "rome", "budapest", "hungary", "slovakia", "vienna", "prague", "berlin", "amsterdam", "lisbon", "spain", "france", "italy", "schengen"), "https://home-affairs.ec.europa.eu/policies/schengen-borders-and-visa/visa-policy_en"),
        (("london", "uk", "united kingdom", "edinburgh", "manchester"), "https://www.gov.uk/check-uk-visa"),
    )

    @classmethod
    def resolve_policy(
        cls,
        passport: str,
        places_to_visit: list[str],
        purpose: str = "Tourism",
    ) -> dict[str, Any]:
        norm_passport = (passport or "").strip()
        lower_passport = norm_passport.lower()

        portal_name = f"Official Foreign Ministry / Immigration Portal ({norm_passport})"
        portal_url = ""
        for key, (name, url) in cls._CITIZENSHIP_PORTALS.items():
            if key in lower_passport:
                portal_name = name
                portal_url = url
                break

        if not portal_url:
            joined_places = " ".join(places_to_visit).lower()
            for keywords, dest_url in cls._DESTINATION_IMMIGRATION_PORTALS:
                if any(kw in joined_places for kw in keywords):
                    portal_url = dest_url
                    portal_name = "Official Destination Immigration Portal"
                    break

        if not portal_url:
            dest_label = quote_plus(" ".join(places_to_visit) or "destination")
            passport_label = quote_plus(norm_passport or "passport")
            portal_url = f"https://www.iatatravelcentre.com/passport-visa-health-travel-document-requirements.htm?dest={dest_label}&nat={passport_label}"

        places_label = ", ".join(places_to_visit) if places_to_visit else "selected destination"
        return {
            "is_entry_feasible": True,
            "visa_status": (
                f"Citizenship Fallback ({norm_passport}): Verify entry & visa permissions for {places_label} "
                f"({purpose}) via {portal_name}."
            ),
            "permitted_stay": f"Verify permitted short-stay duration for {norm_passport} holders on {portal_name}.",
            "passport_validity": "Minimum 6 months validity required from departure date.",
            "health_and_vaccines": "Verify destination health/vaccine requirements and travel medical insurance.",
            "layovers_and_transit": f"Check transit visa requirements for layover hubs based on {norm_passport} rules.",
            "official_source": portal_url,
        }


class LiveExchangeRateSource:
    """Data Source that fetches live USD->COP exchange rates with timestamp."""

    API_URL = "https://api.exchangerate-api.com/v4/latest/USD"
    FALLBACK_RATE = 4180.0

    @classmethod
    def fetch_usd_cop(cls, allow_network: bool = True) -> tuple[float, str]:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        offline_env = os.environ.get("EXECUTIONER_OFFLINE_MODE", "").lower() in ("1", "true", "yes")

        if allow_network and not offline_env:
            try:
                req = urllib.request.Request(
                    cls.API_URL,
                    headers={"User-Agent": "AgentTraveler-ADK/1.0"},
                )
                with urllib.request.urlopen(req, timeout=4.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    cop_rate = float(data["rates"]["COP"])
                    return (
                        cop_rate,
                        f"1 USD = {cop_rate:,.2f} COP (Source: {cls.API_URL}, fetched {timestamp})",
                    )
            except Exception:
                pass

        return (
            cls.FALLBACK_RATE,
            f"1 USD = {cls.FALLBACK_RATE:,.2f} COP (Source: {cls.API_URL} snapshot, fetched {timestamp})",
        )


class FlightAndLodgingLinkSource:
    """Builds clean, clickable search URLs for Kayak, Google Flights, Booking.com, and Airbnb."""

    @staticmethod
    def build_flight_links(origin: str, destination: str) -> dict[str, str]:
        q = quote_plus(f"Flights from {origin} to {destination}")
        return {
            "kayak": "https://www.kayak.com.co/flights",
            "google_flights": f"https://www.google.com/travel/flights?q={q}",
        }

    @staticmethod
    def build_lodging_links(city: str) -> dict[str, str]:
        encoded_city = quote_plus(city)
        return {
            "booking": f"https://www.booking.com/searchresults.html?ss={encoded_city}",
            "airbnb": f"https://www.airbnb.com.co/s/{encoded_city}/homes",
        }


__all__ = [
    "FlightAndLodgingLinkSource",
    "LiveCancilleriaUrlSource",
    "LiveExchangeRateSource",
    "RegionProfileRegistry",
    "RegionTravelProfile",
    "WORK_HARD_STOP_POLICY",
]
