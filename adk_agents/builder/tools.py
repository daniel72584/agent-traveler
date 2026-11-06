"""Thin ADK FunctionTool definitions for the isolated Builder agent (`adk_agents/builder/tools.py`).

Delegates extraction, state management, and lifecycle transitions to:
- `adk_agents/builder/extractor.py` (`HeuristicSpecExtractor`)
- `adk_agents/builder/engine.py` (`TripSpecStateRepository`, `SddLifecycleEngine`)
- `adk_agents/builder/callbacks.py` (`enforce_sdd_attempt_gate`)
"""

from __future__ import annotations

from typing import Any, Optional

from google.adk.tools.tool_context import ToolContext

from adk_agents.builder.callbacks import enforce_sdd_attempt_gate
from adk_agents.builder.engine import SddLifecycleEngine, TripSpecStateRepository
from adk_agents.builder.extractor import HeuristicSpecExtractor
from contracts.trip_spec import TripSpecPatch

# Re-exports for backward compatibility
get_trip_spec_from_state = TripSpecStateRepository.load
save_trip_spec_to_state = TripSpecStateRepository.save
extract_fields_from_text_heuristic = HeuristicSpecExtractor.extract


def update_and_validate_trip_spec(
    origin: Optional[str] = None,
    places_to_visit: Optional[list[str]] = None,
    route_order: Optional[list[str]] = None,
    dates: Optional[str] = None,
    duration_days: Optional[int] = None,
    purpose: Optional[str] = None,
    traveler_count: Optional[int] = None,
    preferred_weather: Optional[str] = None,
    accommodation_kind: Optional[str] = None,
    accommodation_room_type: Optional[str] = None,
    accommodation_bathroom: Optional[str] = None,
    accommodation_stars: Optional[str] = None,
    accommodation_max_price_per_night: Optional[str] = None,
    activity_style: Optional[str] = None,
    tool_context: Optional[ToolContext] = None,
) -> dict[str, Any]:
    """ADK FunctionTool: Applies a `TripSpecPatch` and evaluates SDD lifecycle state."""
    state: dict[str, Any] = tool_context.state if tool_context is not None else {}
    patch = TripSpecPatch(
        origin=origin,
        places_to_visit=places_to_visit,
        route_order=route_order,
        dates=dates,
        duration_days=duration_days,
        purpose=purpose,
        traveler_count=traveler_count,
        preferred_weather=preferred_weather,
        accommodation_kind=accommodation_kind,
        accommodation_room_type=accommodation_room_type,
        accommodation_bathroom=accommodation_bathroom,
        accommodation_stars=accommodation_stars,
        accommodation_max_price_per_night=accommodation_max_price_per_night,
        activity_style=activity_style,
    )
    return SddLifecycleEngine.evaluate_and_persist(state, patch, tool_context)


__all__ = [
    "HeuristicSpecExtractor",
    "SddLifecycleEngine",
    "TripSpecStateRepository",
    "enforce_sdd_attempt_gate",
    "extract_fields_from_text_heuristic",
    "get_trip_spec_from_state",
    "save_trip_spec_to_state",
    "update_and_validate_trip_spec",
]
