"""Regional travel strategy profiles and registry (`adk_agents/executioner/profiles.py`)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class RegionTravelProfile:
    """Declarative strategy encapsulating regional visa, flight corridor, and fare rules."""

    name: str
    keywords: tuple[str, ...]
    visa_policy: dict[str, Any]
    corridor_template: Callable[[str, str, str], str]
    layover_guidance: str
    flight_usd_range: tuple[int, int]

    def matches(self, joined_places: str) -> bool:
        return any(kw in joined_places for kw in self.keywords)


_REGIONAL_PROFILES: tuple[RegionTravelProfile, ...] = (
    RegionTravelProfile(
        name="japan",
        keywords=("tokyo", "kyoto", "osaka", "japan", "japón"),
        visa_policy={
            "is_entry_feasible": True,
            "visa_status": "Consular Visa Required for ordinary Colombian passports (apply at Embassy of Japan in Bogotá) / eVisa eligibility check required",
            "permitted_stay": "Up to 90 days for short-term tourism",
            "passport_validity": "Minimum 6 months validity required from departure date.",
            "health_and_vaccines": "No mandatory vaccines from Colombia; travel medical insurance strongly recommended.",
            "layovers_and_transit": "Warning: Connections via US hubs (MIA, IAH, LAX, JFK) require a valid US B1/B2 or C1 Transit Visa. Connections via Schengen (MAD, CDG, FRA) stay airside visa-free for Colombian citizens.",
            "official_source": "https://www.cancilleria.gov.co/politica-exterior/asuntos-bilaterales/asia/japon",
        },
        corridor_template=lambda origin, first, _: (
            f"1-stop or 2-stop routing from {origin} to {first} via Madrid (Iberia)/Paris (Air France)/Istanbul (Turkish Airlines) "
            f"to avoid US transit, or via Houston/Los Angeles/Dallas if holding a valid US visa."
        ),
        layover_guidance=(
            "Colombian citizens WITHOUT a US B1/B2 or C1 transit visa must route via Europe (MAD/CDG/AMS) or Istanbul (IST) "
            "rather than US hubs."
        ),
        flight_usd_range=(1350, 1950),
    ),
    RegionTravelProfile(
        name="usa",
        keywords=(
            "new york",
            "miami",
            "orlando",
            "los angeles",
            "san francisco",
            "usa",
            "eeuu",
            "washington",
            "boston",
            "chicago",
            "las vegas",
        ),
        visa_policy={
            "is_entry_feasible": True,
            "visa_status": "Consular Tourist Visa Required (US B1/B2 Non-Immigrant Visa mandatory for ordinary Colombian passports)",
            "permitted_stay": "Up to 180 days per entry (determined by CBP Form I-94 at port of entry)",
            "passport_validity": "Minimum 6 months validity required beyond intended period of stay.",
            "health_and_vaccines": "No mandatory vaccines for direct entry from Colombia; travel health insurance highly recommended due to US healthcare costs.",
            "layovers_and_transit": "Direct flights available from BOG/MDE; any US domestic connection clears CBP immigration at the first US port of entry.",
            "official_source": "https://www.cancilleria.gov.co/politica-exterior/asuntos-bilaterales/america/estados-unidos",
        },
        corridor_template=lambda origin, first, last: (
            f"Direct or 1-stop flights from {origin} to {first} (returning from {last}) "
            f"via Avianca, LATAM, American Airlines, Delta, or United."
        ),
        layover_guidance=(
            "All passengers clear US Customs and Border Protection (CBP) at the first US arrival airport; "
            "valid US B1/B2 visa required."
        ),
        flight_usd_range=(420, 780),
    ),
    RegionTravelProfile(
        name="schengen",
        keywords=(
            "madrid",
            "barcelona",
            "paris",
            "rome",
            "budapest",
            "hungary",
            "hungría",
            "slovakia",
            "eslovaquia",
            "bratislava",
            "vienna",
            "prague",
            "berlin",
            "amsterdam",
            "lisbon",
            "spain",
            "france",
            "italy",
            "schengen",
        ),
        visa_policy={
            "is_entry_feasible": True,
            "visa_status": "Visa-Free Short Stay (Schengen Area exemption for ordinary Colombian passports; verify EES/ETIAS pre-registration status)",
            "permitted_stay": "Up to 90 days within any 180-day period",
            "passport_validity": "Minimum 6 months validity (must be valid at least 3 months beyond planned Schengen departure).",
            "health_and_vaccines": "Schengen travel medical insurance (€30,000 minimum coverage) recommended/required at border control.",
            "layovers_and_transit": "Direct flights from BOG to Madrid (MAD) or Paris (CDG via Air France) connect intra-Schengen without US/UK transit visas.",
            "official_source": "https://www.cancilleria.gov.co/politica-exterior/asuntos-bilaterales/europa/union-europea",
        },
        corridor_template=lambda origin, first, last: (
            f"Primary international corridor from {origin} to {first} (open-jaw return from {last}) "
            f"operated by Avianca, Iberia, Air France, KLM, or LATAM."
        ),
        layover_guidance=(
            "Verify whether layover hubs (US, UK, or Schengen) require an airport transit visa for ordinary Colombian passports."
        ),
        flight_usd_range=(750, 1250),
    ),
    RegionTravelProfile(
        name="central_asia",
        keywords=(
            "kyrgyzstan",
            "kirguistán",
            "kirguistan",
            "bishkek",
            "kazakhstan",
            "kazajistán",
            "kazajistan",
            "almaty",
            "astana",
            "uzbekistan",
            "uzbekistán",
            "tashkent",
            "samarkand",
        ),
        visa_policy={
            "is_entry_feasible": True,
            "visa_status": (
                "Electronic Visa (e-Visa) or Consular Verification Required for ordinary Colombian passports "
                "traveling to the Kyrgyz Republic (verify via e-Visa portal evisa.e-gov.kg and concurrent embassy)"
            ),
            "permitted_stay": "Up to 30–60 days per e-Visa / bilateral tourist rules",
            "passport_validity": "Minimum 6 months validity required beyond intended departure date.",
            "health_and_vaccines": "Yellow Fever vaccination certificate recommended if transiting endemic hubs; comprehensive high-altitude/medical insurance advised.",
            "layovers_and_transit": (
                "Best routed from Colombia via Istanbul (IST - Turkish Airlines) or Schengen hubs (MAD/FRA) "
                "to avoid US/UK transit visa requirements."
            ),
            "official_source": "https://www.cancilleria.gov.co/politica-exterior/asuntos-bilaterales/europa/republica-kirguisa",
        },
        corridor_template=lambda origin, first, last: (
            f"1-stop or 2-stop routing from {origin} to {first} (returning from {last}) "
            f"via Istanbul (Turkish Airlines BOG-IST-FRU/ALA) or via Madrid/Frankfurt + Istanbul."
        ),
        layover_guidance=(
            "Route via Istanbul (IST) or Schengen (MAD/CDG/FRA) airside transit to avoid US B1/B2/C1 or UK DATV transit visas."
        ),
        flight_usd_range=(1250, 1850),
    ),
)

_DEFAULT_PROFILE = RegionTravelProfile(
    name="default_international",
    keywords=(),
    visa_policy={
        "is_entry_feasible": True,
        "visa_status": "Verify bilateral Cancillería sheet for ordinary Colombian passport (Tourist Short Stay)",
        "permitted_stay": "Up to 90 days (standard tourist stay; confirm on official bilateral sheet)",
        "passport_validity": "Minimum 6 months validity required from departure date.",
        "health_and_vaccines": "Yellow Fever vaccination certificate required if transiting endemic regions (carry international ICVP card).",
        "layovers_and_transit": "Check transit visa rules for US (C1/B1/B2 required), UK (DATV), and Schengen hubs.",
        "official_source": "https://www.cancilleria.gov.co/politica-exterior/asuntos-bilaterales",
    },
    corridor_template=lambda origin, first, last: (
        f"Primary international corridor from {origin} to {first} (open-jaw return from {last}) "
        f"operated by Avianca, Iberia, Air France, KLM, Turkish Airlines, or LATAM."
    ),
    layover_guidance=(
        "Verify whether layover hubs (US, UK, or Schengen) require an airport transit visa for ordinary Colombian passports."
    ),
    flight_usd_range=(750, 1250),
)

WORK_HARD_STOP_POLICY: dict[str, Any] = {
    "is_entry_feasible": False,
    "visa_status": "Work Visa / Labor Permit Mandatory (Hard Stop: Tourist entry does NOT allow employment)",
    "permitted_stay": "Subject to consular work permit approval prior to travel",
    "passport_validity": "Minimum 6 months validity required from departure date.",
    "health_and_vaccines": "Verify destination occupational health & Yellow Fever rules.",
    "layovers_and_transit": "Do not book flights until the consular work visa is stamped.",
    "official_source": "https://www.cancilleria.gov.co/politica-exterior/asuntos-bilaterales",
}


class RegionProfileRegistry:
    """Tier-2 Strategy Registry resolving destinations into a `RegionTravelProfile`."""

    @classmethod
    def resolve(cls, places_to_visit: list[str]) -> RegionTravelProfile:
        joined = " ".join(places_to_visit).lower()
        return next(
            (profile for profile in _REGIONAL_PROFILES if profile.matches(joined)),
            _DEFAULT_PROFILE,
        )

