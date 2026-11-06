"""Isolated ADK Executioner Agent definition (`adk_agents/executioner/agent.py`).

Pure agent configuration file. All tools, callbacks, pipelines, and external data
sources are isolated in `tools.py`, `callbacks.py`, `pipeline.py`, `sources.py`,
and `profiles.py`.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys

from dotenv import load_dotenv
from google.adk.agents import Agent

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

load_dotenv(REPO_ROOT / ".env")
if os.environ.get("GEMINI_KEY") and not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_KEY"]
if os.environ.get("GEMINI_KEY") and not os.environ.get("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.environ["GEMINI_KEY"]

from adk_agents.executioner.callbacks import (
    deterministic_executioner_fallback_callback,
    require_validated_spec_gate,
)
from adk_agents.executioner.prompts import EXECUTIONER_SYSTEM_INSTRUCTION
from adk_agents.executioner.tools import (
    analyze_flights_from_colombia,
    build_route_and_climate_plan,
    check_cancilleria_visa_policy,
    scout_prices_and_live_currency,
)

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


def create_executioner_agent(model: str = DEFAULT_MODEL) -> Agent:
    """Factory that builds an isolated ADK Executioner Agent instance."""
    return Agent(
        name="travel_executioner_agent",
        model=model,
        description=(
            "Orchestrates travel planning (Cancillería visa checks, Google Maps routes, "
            "weather/transport analysis, flights from Colombia, and live COP price scouting) "
            "from a validated trip-spec."
        ),
        instruction=EXECUTIONER_SYSTEM_INSTRUCTION,
        tools=[
            check_cancilleria_visa_policy,
            build_route_and_climate_plan,
            analyze_flights_from_colombia,
            scout_prices_and_live_currency,
        ],
        before_agent_callback=require_validated_spec_gate,
        before_model_callback=deterministic_executioner_fallback_callback,
    )


# Exposed for `adk run adk_agents/executioner` and `adk web`
root_agent = create_executioner_agent()
