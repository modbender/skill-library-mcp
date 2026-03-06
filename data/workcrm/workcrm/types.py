from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

DraftStatus = Literal["pending", "committed", "rejected"]
ParticipantRefKind = Literal["contact", "organisation"]

ProjectStage = Literal["intake", "active", "waiting", "blocked", "paused", "done"]
TaskStatus = Literal["open", "done", "canceled"]


@dataclass(frozen=True)
class ProposedAction:
    kind: Literal["log", "task", "query"]
    preview: dict
    payload: dict
    participants: list[dict] | None = None
    draft_id: str | None = None


@dataclass(frozen=True)
class EngineResponse:
    message: str
    pending: Optional[ProposedAction] = None
    wrote: bool = False
    result: Optional[dict] = None
