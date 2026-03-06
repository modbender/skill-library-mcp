"""ElevenLabs + Twilio Voice-Agent Bridge.

Main FastAPI application that serves as the personalization webhook for
ElevenLabs' native Twilio integration.

Architecture
------------
1. ElevenLabs owns the Twilio phone number and handles all audio streaming.
2. When a call arrives, ElevenLabs sends a POST to ``/webhook/personalize``
   with caller metadata (``caller_id``, ``agent_id``, ``called_number``,
   ``call_sid``).
3. This service looks up the caller's memory / session, assembles a system
   prompt from the soul template + memory context, and returns
   ``conversation_initiation_client_data`` so ElevenLabs can personalize the
   conversation on the fly.
4. No audio proxying is needed — ElevenLabs ↔ Twilio handle media directly.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import re
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterator

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from memory import (
    Session,
    add_memory,
    add_note,
    end_session,
    ensure_data_dir,
    get_memories,
    get_notes,
    load_session,
)

# ── Environment ─────────────────────────────────────────────────────────────

load_dotenv()

ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_AGENT_ID: str = os.getenv("ELEVENLABS_AGENT_ID", "")
OPENCLAW_API_BASE_URL: str = os.getenv("OPENCLAW_API_BASE_URL", "")
PUBLIC_BASE_URL: str = os.getenv("PUBLIC_BASE_URL", "")
WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")
SOUL_TEMPLATE_PATH: str = os.getenv("SOUL_TEMPLATE_PATH", "./soul_template.md")
DATA_DIR: str = os.getenv("DATA_DIR", "./data")
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

# ── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("bridge")

# ── Soul template ───────────────────────────────────────────────────────────

_soul_template: str = ""


def _load_soul_template() -> str:
    """Read the soul/personality template from disk.

    Returns the raw Markdown text, or a sensible fallback if the file is
    missing.
    """
    path = Path(SOUL_TEMPLATE_PATH)
    if path.exists():
        text = path.read_text(encoding="utf-8").strip()
        logger.info("Loaded soul template from %s (%d chars)", path, len(text))
        return text
    logger.warning("Soul template not found at %s — using built-in fallback", path)
    return "You are a helpful AI voice assistant."


# ── Pydantic models ────────────────────────────────────────────────────────


class PersonalizeRequest(BaseModel):
    """Payload ElevenLabs sends to the personalization webhook."""

    caller_id: str = Field(default="", description="Caller phone number (E.164 or raw)")
    agent_id: str = Field(default="", description="ElevenLabs agent ID")
    called_number: str = Field(default="", description="The Twilio number that was called")
    call_sid: str = Field(default="", description="Twilio Call SID")


class PostCallRequest(BaseModel):
    """Payload ElevenLabs sends after a call completes."""

    call_sid: str = Field(default="", description="Twilio Call SID")
    caller_id: str = Field(default="", description="Caller phone number")
    agent_id: str = Field(default="", description="ElevenLabs agent ID")
    duration_seconds: float = Field(default=0.0, description="Call duration in seconds")
    status: str = Field(default="completed", description="Final call status")


class AddMemoryRequest(BaseModel):
    """Request body for adding a memory fact."""

    fact: str = Field(..., min_length=1, description="The fact to store")


class AddNoteRequest(BaseModel):
    """Request body for adding a daily/global context note."""

    note: str = Field(..., min_length=1, description="The note text")
    phone_hash: str | None = Field(
        default=None,
        description="Optional phone hash to scope note to a specific caller",
    )


# ── Helpers ─────────────────────────────────────────────────────────────────

_E164_PATTERN = re.compile(r"^\+[1-9]\d{1,14}$")


def normalize_phone(raw: str) -> str:
    """Normalize a phone string to E.164 format.

    Strips whitespace, dashes, and parentheses.  If the result looks like a
    US 10-digit number without a country code, ``+1`` is prepended.
    """
    cleaned = re.sub(r"[\s\-\(\)]", "", raw.strip())
    if not cleaned:
        return ""
    if not cleaned.startswith("+"):
        digits_only = re.sub(r"\D", "", cleaned)
        if len(digits_only) == 10:
            cleaned = f"+1{digits_only}"
        elif len(digits_only) == 11 and digits_only.startswith("1"):
            cleaned = f"+{digits_only}"
        else:
            cleaned = f"+{digits_only}"
    if _E164_PATTERN.match(cleaned):
        return cleaned
    return cleaned


def hash_phone(phone: str) -> str:
    """Return a hex SHA-256 hash of a phone number string."""
    return hashlib.sha256(phone.encode("utf-8")).hexdigest()


def verify_webhook_signature(
    body: bytes,
    signature: str | None,
) -> bool:
    """Verify the HMAC-SHA256 signature from ElevenLabs.

    Returns ``True`` if the secret is unset (development mode) or if the
    signature matches.
    """
    if not WEBHOOK_SECRET:
        logger.debug("WEBHOOK_SECRET not configured — skipping signature check")
        return True
    if not signature:
        return False
    expected = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def build_memory_context(phone_hash: str) -> str:
    """Assemble a memory context block for injection into the system prompt.

    Combines long-term facts and relevant daily notes for the caller.
    """
    sections: list[str] = []

    facts = get_memories(phone_hash)
    if facts:
        bullet_list = "\n".join(f"- {f}" for f in facts)
        sections.append(f"## Known Facts About This Caller\n{bullet_list}")

    notes = get_notes(phone_hash)
    if notes:
        note_lines = "\n".join(
            f"- [{datetime.fromtimestamp(n['timestamp'], tz=timezone.utc).strftime('%Y-%m-%d')}] {n['note']}"
            for n in notes[-10:]
        )
        sections.append(f"## Context Notes\n{note_lines}")

    return "\n\n".join(sections)


def build_system_prompt(session: Session, phone_hash: str) -> str:
    """Build the full system prompt from soul template + memory context.

    The prompt is structured as::

        <soul template>

        ---
        # Caller Context
        <memory and notes>
    """
    parts: list[str] = [_soul_template]

    memory_ctx = build_memory_context(phone_hash)

    caller_name = session.get("caller_name", "")
    call_count = session.get("call_count", 1)

    caller_info_lines: list[str] = []
    if caller_name:
        caller_info_lines.append(f"- Caller name: {caller_name}")
    caller_info_lines.append(f"- This is call #{call_count} from this caller")
    if call_count > 1:
        caller_info_lines.append("- This is a returning caller — reference prior context naturally")

    caller_section = "## Caller Info\n" + "\n".join(caller_info_lines)

    context_block = "\n\n".join(filter(None, [caller_section, memory_ctx]))
    parts.append(f"---\n# Caller Context\n{context_block}")

    return "\n\n".join(parts)


def build_personalization_response(
    session: Session,
    phone_hash: str,
) -> dict:
    """Build the ``conversation_initiation_client_data`` response payload.

    This is the JSON structure ElevenLabs expects from the personalization
    webhook.
    """
    system_prompt = build_system_prompt(session, phone_hash)

    dynamic_variables: dict[str, str] = {
        "caller_name": session.get("caller_name", ""),
        "session_id": session.get("session_id", ""),
        "call_count": str(session.get("call_count", 1)),
        "phone_hash": phone_hash,
        "is_returning": str(session.get("call_count", 1) > 1).lower(),
    }

    return {
        "conversation_initiation_client_data": {
            "dynamic_variables": dynamic_variables,
            "conversation_config_override": {
                "agent": {
                    "prompt": {
                        "prompt": system_prompt,
                    },
                },
            },
        },
    }


# ── Lifespan ────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: startup / shutdown hooks."""
    global _soul_template  # noqa: PLW0603
    ensure_data_dir()
    _soul_template = _load_soul_template()

    logger.info("Bridge starting — agent_id=%s", ELEVENLABS_AGENT_ID or "(not set)")
    logger.info("Public URL: %s", PUBLIC_BASE_URL or "(not set)")
    logger.info("Data dir:   %s", Path(DATA_DIR).resolve())
    yield
    logger.info("Bridge shutting down")


# ── App ─────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="ElevenLabs–Twilio Memory Bridge",
    version="1.0.0",
    description=(
        "Personalization webhook for ElevenLabs' native Twilio integration. "
        "Injects caller memory and personality into each conversation."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Endpoints ───────────────────────────────────────────────────────────────


@app.get("/health")
async def health() -> dict[str, str]:
    """Health-check endpoint."""
    return {
        "status": "ok",
        "agent_id": ELEVENLABS_AGENT_ID or "not_configured",
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }


@app.post("/webhook/personalize")
async def personalize(
    request: Request,
    x_webhook_secret: str | None = Header(default=None),
) -> dict:
    """ElevenLabs personalization webhook.

    Called by ElevenLabs when a Twilio call arrives.  Returns
    ``conversation_initiation_client_data`` containing dynamic variables and
    a conversation config override with the assembled system prompt.
    """
    body = await request.body()

    if not verify_webhook_signature(body, x_webhook_secret):
        logger.warning("Invalid webhook signature — rejecting request")
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        payload = PersonalizeRequest.model_validate_json(body)
    except Exception:
        logger.exception("Failed to parse personalization payload")
        return _fallback_personalization_response()

    logger.info(
        "Personalize request — agent=%s called_number=%s call_sid=%s",
        payload.agent_id,
        payload.called_number,
        payload.call_sid,
    )

    try:
        phone = normalize_phone(payload.caller_id)
        phone_h = hash_phone(phone) if phone else hash_phone(payload.caller_id or "unknown")

        session = load_session(phone_h)
        if payload.call_sid:
            session["last_call_sid"] = payload.call_sid

        response = build_personalization_response(session, phone_h)

        logger.info(
            "Personalized call — sid=%s caller=%s call_count=%d",
            payload.call_sid,
            phone_h[:8],
            session.get("call_count", 1),
        )
        return response

    except Exception:
        logger.exception("Error building personalization — returning fallback")
        return _fallback_personalization_response()


@app.post("/webhook/post-call")
async def post_call(
    request: Request,
    x_webhook_secret: str | None = Header(default=None),
) -> dict[str, str]:
    """Post-call webhook for ElevenLabs to report call completion.

    Updates the caller's session with the end time and logs the call
    completion.
    """
    body = await request.body()

    if not verify_webhook_signature(body, x_webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        payload = PostCallRequest.model_validate_json(body)
    except Exception:
        logger.exception("Failed to parse post-call payload")
        return {"status": "error", "detail": "Invalid payload"}

    phone = normalize_phone(payload.caller_id)
    phone_h = hash_phone(phone) if phone else hash_phone(payload.caller_id or "unknown")

    end_session(phone_h, payload.call_sid)

    logger.info(
        "Call completed — sid=%s caller=%s duration=%.1fs status=%s",
        payload.call_sid,
        phone_h[:8],
        payload.duration_seconds,
        payload.status,
    )
    return {"status": "ok"}


@app.post("/api/memory/{phone_hash}")
async def api_add_memory(phone_hash: str, body: AddMemoryRequest) -> dict:
    """Add a long-term memory fact for a caller identified by phone hash."""
    facts = add_memory(phone_hash, body.fact)
    return {"status": "ok", "phone_hash": phone_hash, "total_facts": len(facts)}


@app.post("/api/notes")
async def api_add_note(body: AddNoteRequest) -> dict:
    """Add a daily or global context note.

    If ``phone_hash`` is provided the note is scoped to that caller;
    otherwise it is visible to all callers.
    """
    entry = add_note(body.note, body.phone_hash)
    return {
        "status": "ok",
        "timestamp": entry["timestamp"],
        "global": body.phone_hash is None,
    }


# ── Fallback ────────────────────────────────────────────────────────────────


def _fallback_personalization_response() -> dict:
    """Return a minimal valid response so the call still connects.

    If anything goes wrong during personalization we must not break the
    call — ElevenLabs expects a well-formed JSON response.
    """
    return {
        "conversation_initiation_client_data": {
            "dynamic_variables": {
                "caller_name": "",
                "session_id": "fallback",
                "call_count": "1",
                "phone_hash": "",
                "is_returning": "false",
            },
            "conversation_config_override": {},
        },
    }


# ── Entrypoint ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=HOST,
        port=PORT,
        log_level=LOG_LEVEL.lower(),
        reload=False,
    )
