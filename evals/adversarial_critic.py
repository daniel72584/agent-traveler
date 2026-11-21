"""Isolated, domain-agnostic Adversarial Critic Agent (`evals/adversarial_critic.py`).

Evaluates any `{ "name", "agent", "case", "response", "rubric" }` payload from any
domain using a live ADK LLM Agent against four universal axes:
1. `rubric_compliant`: Satisfies every positive requirement and negative constraint in `rubric`.
2. `answers_prompt`: Directly addresses every question and request in `case`.
3. `coherence_ok`: Logically consistent and free of internal contradictions.
4. `clarity_ok`: Clear, well-structured, and written in standard English.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from contracts.critic_verdict import CriticVerdict

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")

CRITIC_SYSTEM_INSTRUCTION = """You are a domain-agnostic **Adversarial Critic Agent**.

You receive a JSON payload containing:
- `name`: Test case identifier
- `agent`: Name of the target agent being evaluated
- `case`: The user's original prompt or question
- `response`: The target agent's actual output
- `rubric`: The evaluation rubric specifying required behaviors and forbidden mistakes

Your task is to critically evaluate `response` against both `case` and `rubric`, and return ONLY a valid JSON object matching `CriticVerdict`:
{
  "passed": bool,
  "score": int,
  "rubric_compliant": bool,
  "answers_prompt": bool,
  "coherence_ok": bool,
  "clarity_ok": bool,
  "failures": [str, ...],
  "critique": str
}

### Universal Evaluation Rules
1. `rubric_compliant`:
   - `true` ONLY if `response` satisfies every requirement and respects every negative constraint ("must not", "should not") in `rubric`.
   - If `response` violates any part of `rubric`, set `rubric_compliant = false` and record the exact violation in `failures`.
2. `answers_prompt`:
   - `true` ONLY if `response` directly addresses the user's actual questions and context in `case` (or appropriately asks a prerequisite clarifying question required by `rubric` when the user's question cannot yet be answered).
   - If `case` asks a specific sub-question (e.g., how/where to obtain a document or perform an action) that `response` completely ignores by dumping an unrelated generic template, set `answers_prompt = false` and explain what was ignored in `failures`.
3. `coherence_ok`:
   - `true` if `response` is logically consistent, factually coherent with the premises in `rubric`, and free of self-contradictions.
4. `clarity_ok`:
   - `true` if `response` is clear, well-structured, and written in standard English.
5. `passed`:
   - Must be `true` ONLY when `rubric_compliant`, `answers_prompt`, `coherence_ok`, and `clarity_ok` are ALL `true`. Otherwise `false`.
   - When `passed` is `true`, `failures` MUST be an empty list `[]` and `score` should be between 80 and 100.
"""


def _require_api_key() -> None:
    api_key = (
        os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GEMINI_KEY")
    )
    if not api_key:
        raise RuntimeError(
            "Missing API key: set GOOGLE_API_KEY, GEMINI_API_KEY, or GEMINI_KEY in your environment or .env."
        )
    os.environ.setdefault("GOOGLE_API_KEY", api_key)


def create_adversarial_critic_agent(model: str = DEFAULT_MODEL) -> Agent:
    """Factory creating the isolated, domain-agnostic ADK Adversarial Critic Agent."""
    _require_api_key()
    return Agent(
        name="adversarial_critic_agent",
        model=model,
        description=(
            "Domain-agnostic adversarial critic that evaluates an agent response against "
            "a prompt and rubric for coherence, clarity, prompt answering, and rubric compliance."
        ),
        instruction=CRITIC_SYSTEM_INSTRUCTION,
    )


async def run_adversarial_critic(
    case: str,
    response: str,
    rubric: str,
    agent_name: str = "target-agent",
    name: str = "unnamed_case",
    model: str = DEFAULT_MODEL,
) -> CriticVerdict:
    """Runs the live ADK Adversarial Critic Agent on `(case, response, rubric)` and returns `CriticVerdict`."""
    payload = {
        "name": name,
        "agent": agent_name,
        "case": case,
        "response": response,
        "rubric": rubric,
    }
    critic_agent = create_adversarial_critic_agent(model=model)
    async with InMemoryRunner(agent=critic_agent, app_name="adversarial_critic_app") as runner:
        session = await runner.session_service.create_session(
            app_name="adversarial_critic_app",
            user_id="adversarial_evaluator",
        )
        msg = types.Content(
            role="user",
            parts=[types.Part.from_text(text=json.dumps(payload))],
        )
        chunks: list[str] = []
        async for event in runner.run_async(
            user_id="adversarial_evaluator",
            session_id=session.id,
            new_message=msg,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if getattr(part, "text", None):
                        chunks.append(part.text)

        raw_output = "".join(chunks).strip()
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_output)
        clean_json = fence_match.group(1).strip() if fence_match else raw_output
        return CriticVerdict.model_validate_json(clean_json)
