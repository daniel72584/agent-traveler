"""Isolated ADK Builder Agent definition (`adk_agents/builder/agent.py`).

Pure agent configuration file. All tools, callbacks, and state engines are
isolated in `tools.py`, `callbacks.py`, `engine.py`, and `extractor.py`.
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

from adk_agents.builder.callbacks import (
    deterministic_builder_fallback_callback,
    enforce_sdd_attempt_gate,
    ensure_validated_yaml_in_response_callback,
)
from adk_agents.builder.prompts import BUILDER_SYSTEM_INSTRUCTION
from adk_agents.builder.tools import update_and_validate_trip_spec

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


def create_builder_agent(model: str = DEFAULT_MODEL) -> Agent:
    """Factory that builds an isolated ADK Builder Agent instance."""
    return Agent(
        name="sdd_builder_agent",
        model=model,
        description=(
            "Conducts the interactive Spec-Driven Development (SDD) interview "
            "with a maximum of 10 attempts to produce a validated trip-spec."
        ),
        instruction=BUILDER_SYSTEM_INSTRUCTION,
        tools=[update_and_validate_trip_spec],
        before_agent_callback=enforce_sdd_attempt_gate,
        before_model_callback=deterministic_builder_fallback_callback,
        after_model_callback=ensure_validated_yaml_in_response_callback,
    )


# Exposed for `adk run adk_agents/builder` and `adk web`
root_agent = create_builder_agent()
