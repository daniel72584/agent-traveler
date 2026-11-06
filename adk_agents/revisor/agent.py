"""Isolated ADK Revisor Agent definition (`adk_agents/revisor/agent.py`).

Pure agent configuration file. All tools, callbacks, audit engines, and compliance
rules are isolated in `tools.py`, `callbacks.py`, `engine.py`, and `rules.py`.
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

from adk_agents.revisor.callbacks import deterministic_revisor_fallback_callback
from adk_agents.revisor.prompts import REVISOR_SYSTEM_INSTRUCTION
from adk_agents.revisor.tools import audit_report_against_sdd

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


def create_revisor_agent(model: str = DEFAULT_MODEL) -> Agent:
    """Factory that builds an isolated ADK Revisor Agent instance."""
    return Agent(
        name="sdd_revisor_agent",
        model=model,
        description=(
            "Audits the generated Trip Report against the SDD trip-spec to decide "
            "whether the result is viable to show to the user (APPROVE) or must go back (REJECT)."
        ),
        instruction=REVISOR_SYSTEM_INSTRUCTION,
        tools=[audit_report_against_sdd],
        before_model_callback=deterministic_revisor_fallback_callback,
    )


# Exposed for `adk run adk_agents/revisor` and `adk web`
root_agent = create_revisor_agent()
