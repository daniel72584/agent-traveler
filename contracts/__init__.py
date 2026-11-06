"""Pure data contracts shared across isolated ADK agents."""

from contracts.revision_verdict import AuditCheckItem, RevisionVerdict
from contracts.trip_report import (
    REQUIRED_REPORT_HEADERS,
    BudgetSection,
    FlightsSection,
    RouteMapSection,
    TripReport,
    VisaFeasibilitySection,
)
from contracts.trip_spec import (
    AccommodationSpec,
    DestinationsSpec,
    TimingSpec,
    TravelerProfile,
    TripSpec,
    TripSpecPatch,
)

__all__ = [
    "AccommodationSpec",
    "AuditCheckItem",
    "BudgetSection",
    "DestinationsSpec",
    "FlightsSection",
    "REQUIRED_REPORT_HEADERS",
    "RevisionVerdict",
    "RouteMapSection",
    "TimingSpec",
    "TravelerProfile",
    "TripReport",
    "TripSpec",
    "TripSpecPatch",
    "VisaFeasibilitySection",
]
