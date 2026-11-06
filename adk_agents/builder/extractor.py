"""Declarative regex rule tables and heuristic extractor for the Builder agent."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Callable


@dataclass(frozen=True)
class RegexFieldRule:
    """Declarative extraction rule mapping a regex pattern to a `TripSpecPatch` field."""

    target_field: str
    pattern: re.Pattern[str]
    transform: Callable[[re.Match[str]], Any]


_DECLARATIVE_REGEX_RULES: tuple[RegexFieldRule, ...] = (
    RegexFieldRule(
        "duration_days",
        re.compile(r"\b(\d+)\s*(?:weeks?|semanas?)\b", re.IGNORECASE),
        lambda m: int(m.group(1)) * 7,
    ),
    RegexFieldRule(
        "duration_days",
        re.compile(r"\b(\d+)\s*(?:days?|d[ií]as?)\b", re.IGNORECASE),
        lambda m: int(m.group(1)),
    ),
    RegexFieldRule(
        "origin",
        re.compile(r"\b(bogot[aá]|bog)\b", re.IGNORECASE),
        lambda _: "Bogotá (BOG)",
    ),
    RegexFieldRule(
        "origin",
        re.compile(r"\b(medell[ií]n|mde)\b", re.IGNORECASE),
        lambda _: "Medellín (MDE)",
    ),
    RegexFieldRule(
        "origin",
        re.compile(r"\b(cali|clo)\b", re.IGNORECASE),
        lambda _: "Cali (CLO)",
    ),
    RegexFieldRule(
        "purpose",
        re.compile(r"\b(tourism|turismo|vacation|vacaciones|leisure)\b", re.IGNORECASE),
        lambda _: "Tourism",
    ),
    RegexFieldRule(
        "purpose",
        re.compile(r"\b(work|trabajo|business|negocios)\b", re.IGNORECASE),
        lambda _: "Work",
    ),
    RegexFieldRule(
        "purpose",
        re.compile(r"\b(study|estudio|estudiar|university)\b", re.IGNORECASE),
        lambda _: "Study",
    ),
    RegexFieldRule(
        "accommodation_kind",
        re.compile(r"\b(hotel|hoteles)\b", re.IGNORECASE),
        lambda _: "hotel",
    ),
    RegexFieldRule(
        "accommodation_kind",
        re.compile(r"\b(hostel|hostal|hostales)\b", re.IGNORECASE),
        lambda _: "hostel",
    ),
    RegexFieldRule(
        "accommodation_kind",
        re.compile(r"\b(apartment|apartamento|airbnb)\b", re.IGNORECASE),
        lambda _: "apartment / Airbnb",
    ),
    RegexFieldRule(
        "accommodation_kind",
        re.compile(r"\b(guesthouse|posada)\b", re.IGNORECASE),
        lambda _: "guesthouse / posada",
    ),
    RegexFieldRule(
        "accommodation_room_type",
        re.compile(r"\b(private\s+room|habitaci[oó]n\s+privada)\b", re.IGNORECASE),
        lambda _: "private_room",
    ),
    RegexFieldRule(
        "accommodation_room_type",
        re.compile(r"\b(shared\s+dorm|dormitorio\s+compartido|shared\s+room)\b", re.IGNORECASE),
        lambda _: "shared_dorm",
    ),
    RegexFieldRule(
        "accommodation_bathroom",
        re.compile(r"\b(private\s+bath(?:room)?|ba[ñn]o\s+privado)\b", re.IGNORECASE),
        lambda _: "private_bathroom",
    ),
    RegexFieldRule(
        "accommodation_bathroom",
        re.compile(r"\b(shared\s+bath(?:room)?|ba[ñn]o\s+compartido)\b", re.IGNORECASE),
        lambda _: "shared_bathroom",
    ),
    RegexFieldRule(
        "accommodation_stars",
        re.compile(r"\b([1-5])\s*(?:-\s*star|stars?|estrellas?|★)\b", re.IGNORECASE),
        lambda m: f"{m.group(1)} stars",
    ),
    RegexFieldRule(
        "accommodation_stars",
        re.compile(r"\bboutique\b", re.IGNORECASE),
        lambda _: "boutique",
    ),
    RegexFieldRule(
        "accommodation_stars",
        re.compile(r"\b(any\s+stars?|unrated|sin\s+estrellas)\b", re.IGNORECASE),
        lambda _: "any",
    ),
    RegexFieldRule(
        "accommodation_max_price_per_night",
        re.compile(
            r"\b(\d[\d,\.]*\s*(?:usd|cop|eur|\$)(?:\s*/\s*(?:night|noche))?|\$\s*\d[\d,\.]*)\b",
            re.IGNORECASE,
        ),
        lambda m: (
            f"{m.group(1).strip()[1:].strip()} USD"
            if m.group(1).strip().startswith("$")
            else m.group(1).upper().strip()
        ),
    ),
    RegexFieldRule(
        "preferred_weather",
        re.compile(
            r"\b(warm\s*&\s*sunny|warm\s+and\s+sunny|mild\s+autumn|mild\s+spring|cool\s+autumn|snow|warm|mild|cool|sunny|dry)\b",
            re.IGNORECASE,
        ),
        lambda m: m.group(1).lower(),
    ),
    RegexFieldRule(
        "dates",
        re.compile(
            r"\b(202\d-\d{2}-\d{2}(?:\s+to\s+202\d-\d{2}-\d{2})?|(?:january|february|march|april|may|june|july|august|september|october|november|december|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(?:\s+202\d)?)\b",
            re.IGNORECASE,
        ),
        lambda m: m.group(1).title(),
    ),
)

_CITY_GAZETTEER: tuple[tuple[str, str], ...] = (
    ("new york", "New York"),
    ("nyc", "New York"),
    ("miami", "Miami"),
    ("orlando", "Orlando"),
    ("los angeles", "Los Angeles"),
    ("san francisco", "San Francisco"),
    ("washington", "Washington D.C."),
    ("boston", "Boston"),
    ("chicago", "Chicago"),
    ("las vegas", "Las Vegas"),
    ("tokyo", "Tokyo"),
    ("kyoto", "Kyoto"),
    ("osaka", "Osaka"),
    ("madrid", "Madrid"),
    ("barcelona", "Barcelona"),
    ("paris", "Paris"),
    ("rome", "Rome"),
    ("budapest", "Budapest"),
    ("istanbul", "Istanbul"),
)


class HeuristicSpecExtractor:
    """Data-driven extractor mapping natural language text into a `TripSpecPatch` dict."""

    @classmethod
    def extract(cls, text: str) -> dict[str, Any]:
        extracted: dict[str, Any] = {}
        for rule in _DECLARATIVE_REGEX_RULES:
            if rule.target_field not in extracted:
                match = rule.pattern.search(text)
                if match:
                    extracted[rule.target_field] = rule.transform(match)

        found_cities = list(
            dict.fromkeys(
                canonical
                for token, canonical in _CITY_GAZETTEER
                if re.search(rf"\b{re.escape(token)}\b", text, re.IGNORECASE)
            )
        )
        if found_cities:
            extracted["places_to_visit"] = found_cities
            extracted["route_order"] = list(found_cities)

        return extracted

