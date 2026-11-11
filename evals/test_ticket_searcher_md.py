"""Verification tests for the Markdown Ticket Searcher Agent, 9 Flight Skills, and Travel Supervisor `.md` files (`evals/test_ticket_searcher_md.py`)."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EXPECTED_FLIGHT_SKILLS = [
    "google-flights-search",
    "kayak-flight-search",
    "skyscanner-flight-search",
    "momondo-flight-search",
    "kiwi-flight-search",
    "skiplagged-flight-search",
    "airfrance-flight-search",
    "avianca-flight-search",
    "ryanair-flight-search",
]


def test_travel_supervisor_md_and_agents_md_are_valid() -> None:
    """Ensures `travel-supervisor.md` and `AGENTS.md` preserve the 5-step SDD workflow and wire `@ticket-searcher`."""
    supervisor_path = REPO_ROOT / ".agents" / "agents" / "travel-supervisor.md"
    agents_md_path = REPO_ROOT / "AGENTS.md"

    assert supervisor_path.exists()
    assert agents_md_path.exists()

    supervisor_text = supervisor_path.read_text(encoding="utf-8")
    agents_text = agents_md_path.read_text(encoding="utf-8")

    # Verify core travel-supervisor sections remain intact
    assert "name: travel-supervisor" in supervisor_text
    assert "### Step 1: Spec-Driven Development (SDD) Interview & Validation Gate" in supervisor_text
    assert "### Step 2: Visa & Entry Requirements (Cancillería Gate)" in supervisor_text
    assert "### Step 3: Places, Culture & Route Mapping" in supervisor_text
    assert "### Step 4: Flights & Transit Connections" in supervisor_text
    assert "### Step 5: Price Scouting & Currency Conversion" in supervisor_text
    assert "@ticket-searcher" in supervisor_text
    assert "ticket-searcher.md" in agents_text


def test_ticket_searcher_md_and_all_nine_skills_exist() -> None:
    """Ensures `.agents/agents/ticket-searcher.md` and all 9 flight-provider skills are valid."""
    ticket_agent_path = REPO_ROOT / ".agents" / "agents" / "ticket-searcher.md"
    assert ticket_agent_path.exists()
    ticket_text = ticket_agent_path.read_text(encoding="utf-8")
    assert "name: ticket-searcher" in ticket_text
    assert "Top 5" in ticket_text
    assert "run_fligth_agent/" in ticket_text

    for skill_name in EXPECTED_FLIGHT_SKILLS:
        skill_file = REPO_ROOT / ".agents" / "skills" / skill_name / "SKILL.md"
        assert skill_file.exists(), f"Missing flight skill: {skill_file}"
        skill_text = skill_file.read_text(encoding="utf-8")
        assert f"name: {skill_name}" in skill_text
        assert "description:" in skill_text


def test_saved_antigravity_execution_in_run_fligth_agent() -> None:
    """Verifies that the Antigravity execution outputs in `run_fligth_agent/` are present and complete."""
    out_dir = REPO_ROOT / "run_fligth_agent"
    latest_md = out_dir / "latest_execution.md"
    executions_json = out_dir / "executions.json"

    assert latest_md.exists()
    assert executions_json.exists()

    md_text = latest_md.read_text(encoding="utf-8")
    assert "## 2. Top 5 Ranked Flights" in md_text
    assert "## 3. All 9 Provider Skill Snapshots" in md_text

    data = json.loads(executions_json.read_text(encoding="utf-8"))
    assert data["execution_environment"] == "antigravity_native"
    assert len(data["executions"]) >= 1
    assert len(data["executions"][0]["top_5_flights"]) == 5

