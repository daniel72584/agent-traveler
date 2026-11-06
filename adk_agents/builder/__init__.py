"""Isolated Builder ADK Agent package."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from adk_agents.builder.agent import create_builder_agent, root_agent

__all__ = ["create_builder_agent", "root_agent"]

