"""Trip Specification (trip-spec v1.0) data contracts.

Uses declarative field descriptors and a Patch DTO (`TripSpecPatch`) so updates
and completeness checks are data-driven rather than procedural `if/else` chains.
Has zero dependencies on any agent implementation.
"""

from __future__ import annotations

from operator import attrgetter
from typing import Any, Literal
import yaml
from pydantic import BaseModel, Field, field_validator


class TravelerProfile(BaseModel):
    """Traveler identity and trip purpose."""

    passport: str = Field(
        default="Colombian Ordinary",
        description="Nationality and passport type (default: ordinary Colombian passport).",
    )
    count: int = Field(
        default=1,
        ge=1,
        description="Number of travelers in the party.",
    )
    purpose: str | None = Field(
        default=None,
        description="Travel purpose: Tourism, Work, or Study.",
    )


class DestinationsSpec(BaseModel):
    """Target destinations, cities, and ordered route."""

    places_to_visit: list[str] = Field(
        default_factory=list,
        description="Target destinations, specific cities, regions, and must-see attractions.",
    )
    route_order: list[str] = Field(
        default_factory=list,
        description="Ordered sequence of stops or cities.",
    )


class TimingSpec(BaseModel):
    """Travel dates, month, or season and total duration."""

    dates: str | None = Field(
        default=None,
        description="Travel dates, month, or season (e.g., '2026-11-05 to 2026-11-20' or 'November 2026').",
    )
    duration_days: int | None = Field(
        default=None,
        ge=1,
        description="Total trip duration in days.",
    )


class AccommodationSpec(BaseModel):
    """Detailed lodging criteria required by the SDD interview."""

    kind: str | None = Field(
        default=None,
        description="hotel | hostel | apartment / Airbnb | guesthouse / posada | flexible",
    )
    room_type: str | None = Field(
        default=None,
        description="private_room | shared_dorm | entire_place | flexible",
    )
    bathroom: str | None = Field(
        default=None,
        description="private_bathroom | shared_bathroom | flexible",
    )
    stars: str | None = Field(
        default=None,
        description="1-2 stars | 3 stars | 4 stars | 5 stars | boutique | any",
    )
    max_price_per_night: str | None = Field(
        default=None,
        description="Numeric amount with currency (e.g., '80 USD' or '330,000 COP').",
    )


class TripSpecPatch(BaseModel):
    """Data Transfer Object (DTO) that normalizes partial updates to a `TripSpec`.

    Eliminates repetitive `if field: spec.x = field.strip()` chains by centralizing
    normalization in Pydantic validators and mapping patch keys declaratively to
    `TripSpec` target paths.
    """

    origin: str | None = None
    places_to_visit: list[str] | None = None
    route_order: list[str] | None = None
    dates: str | None = None
    duration_days: int | None = None
    purpose: str | None = None
    traveler_count: int | None = None
    preferred_weather: str | None = None
    accommodation_kind: str | None = None
    accommodation_room_type: str | None = None
    accommodation_bathroom: str | None = None
    accommodation_stars: str | None = None
    accommodation_max_price_per_night: str | None = None
    activity_style: str | None = None

    @field_validator(
        "origin",
        "dates",
        "purpose",
        "preferred_weather",
        "accommodation_kind",
        "accommodation_room_type",
        "accommodation_bathroom",
        "accommodation_stars",
        "accommodation_max_price_per_night",
        "activity_style",
        mode="before",
    )
    @classmethod
    def _clean_optional_str(cls, val: Any) -> str | None:
        if isinstance(val, str):
            stripped = val.strip()
            return stripped if stripped else None
        return None

    @field_validator("places_to_visit", "route_order", mode="before")
    @classmethod
    def _clean_str_list(cls, val: Any) -> list[str] | None:
        if not isinstance(val, list):
            return None
        cleaned = [str(item).strip() for item in val if item and str(item).strip()]
        return cleaned if cleaned else None

    @field_validator("duration_days", "traveler_count", mode="before")
    @classmethod
    def _clean_positive_int(cls, val: Any) -> int | None:
        if isinstance(val, int) and val > 0:
            return val
        return None


# Declarative mapping from `TripSpecPatch` attribute -> `(nested_object_attr | None, target_attr)`
_PATCH_TARGET_MAP: dict[str, tuple[str | None, str]] = {
    "origin": (None, "origin"),
    "places_to_visit": ("destinations", "places_to_visit"),
    "route_order": ("destinations", "route_order"),
    "dates": ("timing", "dates"),
    "duration_days": ("timing", "duration_days"),
    "purpose": ("traveler", "purpose"),
    "traveler_count": ("traveler", "count"),
    "preferred_weather": (None, "preferred_weather"),
    "accommodation_kind": ("accommodation", "kind"),
    "accommodation_room_type": ("accommodation", "room_type"),
    "accommodation_bathroom": ("accommodation", "bathroom"),
    "accommodation_stars": ("accommodation", "stars"),
    "accommodation_max_price_per_night": ("accommodation", "max_price_per_night"),
    "activity_style": (None, "activity_style"),
}

# Declarative table of `(public_missing_field_name, attribute_path)` for SDD completeness checks
_REQUIRED_SDD_FIELDS: tuple[tuple[str, str], ...] = (
    ("origin", "origin"),
    ("places_to_visit", "destinations.places_to_visit"),
    ("timing.dates", "timing.dates"),
    ("timing.duration_days", "timing.duration_days"),
    ("traveler.purpose", "traveler.purpose"),
    ("preferred_weather", "preferred_weather"),
    ("accommodation.kind", "accommodation.kind"),
    ("accommodation.room_type", "accommodation.room_type"),
    ("accommodation.bathroom", "accommodation.bathroom"),
    ("accommodation.stars", "accommodation.stars"),
    ("accommodation.max_price_per_night", "accommodation.max_price_per_night"),
)


def _is_populated(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) > 0
    return True


class TripSpec(BaseModel):
    """Validated or in-progress Trip Specification (trip-spec v1.0)."""

    version: str = Field(default="1.0", description="Specification schema version.")
    status: Literal["draft", "interviewing", "validated", "failed_max_attempts"] = Field(
        default="draft",
        description="Current lifecycle status of the trip-spec.",
    )
    traveler: TravelerProfile = Field(default_factory=TravelerProfile)
    origin: str | None = Field(
        default=None,
        description="Departure city/airport in Colombia (e.g., 'Bogotá (BOG)', 'Medellín (MDE)').",
    )
    destinations: DestinationsSpec = Field(default_factory=DestinationsSpec)
    timing: TimingSpec = Field(default_factory=TimingSpec)
    preferred_weather: str | None = Field(
        default=None,
        description="Desired climate (e.g., warm & sunny, mild spring, cool autumn, snow/winter, avoid rain).",
    )
    accommodation: AccommodationSpec = Field(default_factory=AccommodationSpec)
    activity_style: str | None = Field(
        default="moderate cultural exploration",
        description="Travel pace: relaxed, moderate, or packed / fast-paced.",
    )

    def apply_patch(self, patch: TripSpecPatch | dict[str, Any]) -> TripSpec:
        """Applies a normalized `TripSpecPatch` declaratively via `_PATCH_TARGET_MAP`."""
        validated_patch = (
            patch if isinstance(patch, TripSpecPatch) else TripSpecPatch.model_validate(patch)
        )
        non_null_updates = validated_patch.model_dump(exclude_none=True)

        for patch_field, value in non_null_updates.items():
            parent_attr, leaf_attr = _PATCH_TARGET_MAP[patch_field]
            target_obj = getattr(self, parent_attr) if parent_attr else self
            setattr(target_obj, leaf_attr, value)

        if (
            self.destinations.places_to_visit
            and not self.destinations.route_order
        ):
            self.destinations.route_order = list(self.destinations.places_to_visit)

        return self

    def missing_sdd_fields(self) -> list[str]:
        """Evaluates `_REQUIRED_SDD_FIELDS` declaratively to list any missing SDD fields."""
        return [
            label
            for label, attr_path in _REQUIRED_SDD_FIELDS
            if not _is_populated(attrgetter(attr_path)(self))
        ]

    def is_complete(self) -> bool:
        """Returns True when all mandatory SDD fields are populated."""
        return len(self.missing_sdd_fields()) == 0

    def to_yaml_block(self) -> str:
        """Serializes the trip-spec into the standard Markdown YAML contract block."""
        payload = {"trip_spec": self.model_dump(mode="json")}
        yaml_str = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True).strip()
        return f"```yaml\n{yaml_str}\n```"
