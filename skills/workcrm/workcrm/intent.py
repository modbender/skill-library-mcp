from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

IntentKind = Literal["log", "task", "query", "unknown"]


@dataclass(frozen=True)
class IntentResult:
    kind: IntentKind
    score: int


_LOG_KWS = [
    "met",
    "meeting",
    "call",
    "called",
    "spoke",
    "emailed",
    "email",
    "sent",
    "回复",
    "聊了",
    "通话",
    "见了",
]
_TASK_KWS = [
    "remind",
    "need to",
    "should",
    "follow up",
    "todo",
    "催",
    "提醒",
    "跟进",
    "下次",
    "需要",
]
_QUERY_KWS = [
    "show",
    "status",
    "digest",
    "what's next",
    "whats next",
    "who do i need",
    "还有什么",
    "进展",
]


def detect_intent(text: str) -> IntentResult:
    t = (text or "").strip().lower()
    if not t:
        return IntentResult(kind="unknown", score=0)

    # Explicit commands win.
    if re.match(r"^(log|task|show|followup|digest|export)\b", t):
        cmd = t.split(None, 1)[0]
        if cmd == "log":
            return IntentResult("log", 100)
        if cmd == "task":
            return IntentResult("task", 100)
        return IntentResult("query", 100)

    def score_for(kws: list[str]) -> int:
        s = 0
        for kw in kws:
            if kw in t:
                s += 10
        return s

    log_s = score_for(_LOG_KWS)
    task_s = score_for(_TASK_KWS)
    query_s = score_for(_QUERY_KWS)

    best = max([(log_s, "log"), (task_s, "task"), (query_s, "query")], key=lambda x: x[0])
    if best[0] == 0:
        return IntentResult("unknown", 0)
    return IntentResult(best[1], best[0])
