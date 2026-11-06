"""Isolated Executioner ADK Agent package."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from adk_agents.executioner.agent import create_executioner_agent, root_agent

__all__ = ["create_executioner_agent", "root_agent"]

