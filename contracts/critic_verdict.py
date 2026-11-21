"""Adversarial Critic Verdict contract (`contracts/critic_verdict.py`).

Structured evaluation verdict emitted by the Adversarial Critic Agent when
grading an agent's response against a test case prompt and rubric.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CriticVerdict(BaseModel):
    """Structured verdict produced by the Adversarial Critic Agent."""

    passed: bool = Field(
        description="True only if rubric_compliant, answers_prompt, coherence_ok, and clarity_ok are all True."
    )
    score: int = Field(
        ge=0,
        le=100,
        description="Overall quality and rubric alignment score from 0 to 100.",
    )
    rubric_compliant: bool = Field(
        description="True if the response satisfies every constraint in the rubric."
    )
    answers_prompt: bool = Field(
        description="True if the response directly addresses the user's prompt/question."
    )
    coherence_ok: bool = Field(
        description="True if the response is logically consistent and free of contradictions."
    )
    clarity_ok: bool = Field(
        description="True if the response is clear, well-structured, and written in standard English."
    )
    failures: list[str] = Field(
        default_factory=list,
        description="Specific reasons or rubric violations discovered by the adversarial critic.",
    )
    critique: str = Field(
        default="",
        description="Concise adversarial review explaining the score and any failures.",
    )
