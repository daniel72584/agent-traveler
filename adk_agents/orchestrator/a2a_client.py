"""A2A JSON-RPC client for communicating with remote ADK A2A servers (`builder`, `executioner`, `revisor`).

Maintains strict package isolation: zero imports from sibling agent packages.
Uses Google ADK's `_compat` A2A client layer over HTTP / ASGI transports.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional
import uuid

from google.adk.a2a import _compat
import httpx

from adk_agents.orchestrator.prompts import (
    AGENT_CARD_WELL_KNOWN_PATH,
    BUILDER_A2A_URL,
    EXECUTIONER_A2A_URL,
    REVISOR_A2A_URL,
)


@dataclass(frozen=True)
class A2aResponsePayload:
    """Normalized response returned from a remote A2A agent invocation."""

    agent_name: str
    context_id: str
    task_id: str
    text: str
    raw_card: dict[str, Any]


# Optional registry allowing tests or local multi-app runners to bind custom httpx.AsyncClient
# factories (e.g., ASGITransport) per base URL without changing production HTTP behavior.
_CUSTOM_HTTPX_FACTORY: Optional[Callable[[str], httpx.AsyncClient]] = None


def register_httpx_client_factory(
    factory: Optional[Callable[[str], httpx.AsyncClient]],
) -> None:
    """Registers an optional `httpx.AsyncClient` factory keyed by target base URL."""
    global _CUSTOM_HTTPX_FACTORY
    _CUSTOM_HTTPX_FACTORY = factory


def _create_http_client(base_url: str, timeout: float = 300.0) -> httpx.AsyncClient:
    if _CUSTOM_HTTPX_FACTORY is not None:
        return _CUSTOM_HTTPX_FACTORY(base_url)
    return httpx.AsyncClient(timeout=httpx.Timeout(timeout, connect=30.0))


def _extract_text_from_parts(parts: Any) -> list[str]:
    texts: list[str] = []
    for part in parts or []:
        if _compat.is_text_part(part):
            val = _compat.part_text(part)
            if val:
                texts.append(val)
    return texts


def _extract_text_from_task(task: Any) -> str:
    """Extracts agent response text from an A2A Task's artifacts, status message, or history."""
    if task is None:
        return ""

    # 1. Prefer final artifacts produced by A2aAgentExecutor
    artifact_texts: list[str] = []
    for artifact in getattr(task, "artifacts", None) or []:
        artifact_texts.extend(_extract_text_from_parts(getattr(artifact, "parts", None)))
    if artifact_texts:
        return "".join(artifact_texts)

    # 2. Check task status message
    status = getattr(task, "status", None)
    status_msg = _compat.normalize_message(getattr(status, "message", None)) if status else None
    if status_msg is not None:
        status_texts = _extract_text_from_parts(getattr(status_msg, "parts", None))
        if status_texts:
            return "".join(status_texts)

    # 3. Fallback to the latest agent message in task history
    for hist_msg in reversed(list(getattr(task, "history", None) or [])):
        if _compat.role_to_str(getattr(hist_msg, "role", None)) == "model":
            hist_texts = _extract_text_from_parts(getattr(hist_msg, "parts", None))
            if hist_texts:
                return "".join(hist_texts)

    return ""


class A2aProtocolClient:
    """Client that resolves A2A Agent Cards and exchanges A2A messages with remote agents."""

    def __init__(
        self,
        builder_url: str = BUILDER_A2A_URL,
        executioner_url: str = EXECUTIONER_A2A_URL,
        revisor_url: str = REVISOR_A2A_URL,
    ) -> None:
        self.builder_url = builder_url.rstrip("/")
        self.executioner_url = executioner_url.rstrip("/")
        self.revisor_url = revisor_url.rstrip("/")

    @staticmethod
    async def fetch_agent_card(base_url: str) -> dict[str, Any]:
        """Fetches the remote agent's `/.well-known/agent-card.json` descriptor."""
        clean_base = base_url.rstrip("/")
        async with _create_http_client(clean_base) as http_client:
            for path in (AGENT_CARD_WELL_KNOWN_PATH, "/.well-known/agent.json"):
                resp = await http_client.get(f"{clean_base}{path}")
                if resp.status_code == 200:
                    return resp.json()
            resp.raise_for_status()
            return {}

    @classmethod
    async def send_a2a_message(
        cls,
        base_url: str,
        text: str,
        context_id: Optional[str] = None,
    ) -> A2aResponsePayload:
        """Resolves the target A2A AgentCard and sends a user text message via A2A JSON-RPC."""
        clean_base = base_url.rstrip("/")
        resolved_context_id = context_id or uuid.uuid4().hex

        async with _create_http_client(clean_base) as http_client:
            # 1. Resolve /.well-known/agent-card.json
            card_dict: Optional[dict[str, Any]] = None
            for path in (AGENT_CARD_WELL_KNOWN_PATH, "/.well-known/agent.json"):
                resp = await http_client.get(f"{clean_base}{path}")
                if resp.status_code == 200:
                    card_dict = resp.json()
                    break
            if card_dict is None:
                raise RuntimeError(f"Failed to resolve A2A AgentCard from {clean_base}")

            agent_card = _compat.parse_agent_card(card_dict)

            # 2. Construct version-agnostic A2A Client bound to http_client
            client_config = _compat.make_client_config(httpx_client=http_client)
            factory = _compat. rebind_client_factory_httpx(
                _compat.A2AClientFactory(config=client_config),
                http_client,
            )
            a2a_client = factory.create(agent_card)

            # 3. Build and send A2A Message preserving context_id for stateful sessions
            request_msg = _compat.make_message(
                message_id=uuid.uuid4().hex,
                role="user",
                parts=[_compat.make_text_part(text)],
                context_id=resolved_context_id,
            )

            normalize = _compat.make_stream_normalizer()
            last_task: Any = None
            direct_texts: list[str] = []
            task_id = ""

            async for raw_item in _compat.send_message(a2a_client, request=request_msg):
                normalized = normalize(raw_item)
                if isinstance(normalized, tuple):
                    task, _update = normalized
                    if task is not None:
                        last_task = task
                        task_id = getattr(task, "id", "") or task_id
                else:
                    direct_texts.extend(
                        _extract_text_from_parts(getattr(normalized, "parts", None))
                    )

            response_text = (
                "".join(direct_texts)
                if direct_texts
                else _extract_text_from_task(last_task)
            )
            return A2aResponsePayload(
                agent_name=card_dict.get("name", "remote_a2a_agent"),
                context_id=resolved_context_id,
                task_id=task_id,
                text=response_text,
                raw_card=card_dict,
            )

