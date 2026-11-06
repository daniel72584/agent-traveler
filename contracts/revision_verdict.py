"""Revision Verdict contract produced by the Revisor agent.

Determines whether the Executioner's Trip Report satisfies the Builder's
validated TripSpec or must be sent back for revision.
"""

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class AuditCheckItem(BaseModel):
    """Individual SDD vs. Report compliance check result."""

    check_name: str = Field(
        description="Name of the check (e.g., 'accommodation_budget_cap', 'places_coverage', 'visa_cancilleria_gate', 'weather_alignment', 'live_fx_citation', 'report_structure')."
    )
    passed: bool = Field(description="True if the report satisfies this SDD requirement.")
    details: str = Field(description="Explanation or evidence found in the report.")


class RevisionVerdict(BaseModel):
    """Structured gatekeeper verdict emitted by the Revisor agent."""

    decision: Literal["APPROVE", "REJECT"] = Field(
        description="'APPROVE' if the report is viable to show to the user; 'REJECT' if it violates the SDD trip-spec or misses mandatory sections."
    )
    is_viable: bool = Field(
        description="True when decision == 'APPROVE', False when decision == 'REJECT'."
    )
    retry_target: Literal["executioner", "builder", "none"] = Field(
        default="none",
        description="Which stage should re-run if rejected ('executioner' for report/constraint violations, 'builder' if the spec itself is unfeasible/contradictory, 'none' if approved)."
    )
    score: int = Field(
        ge=0,
        le=100,
        description="Compliance score from 0 to 100 across all SDD checks.",
    )
    checks: list[AuditCheckItem] = Field(
        default_factory=list,
        description="Itemized audit results for each SDD constraint.",
    )
    violations: list[str] = Field(
        default_factory=list,
        description="Specific SDD or guardrail violations that caused rejection.",
    )
    revision_instructions: str = Field(
        default="",
        description="Actionable instructions for fixing the violations before showing the final result.",
    )

