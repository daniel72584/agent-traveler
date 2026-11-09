"""Standalone Google ADK agent packages for Agent Traveler.

Each subpackage (`builder`, `executioner`, `revisor`, `orchestrator`) is strictly
isolated and has zero imports from sibling agent packages. Inter-agent communication
takes place over the Agent-to-Agent (A2A) protocol.
"""

