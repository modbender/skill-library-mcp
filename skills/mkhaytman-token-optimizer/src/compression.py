from __future__ import annotations

from collections import Counter


def text_blocks(content: object, max_chars: int = 500) -> str:
    if isinstance(content, str):
        return content[:max_chars]
    if not isinstance(content, list):
        return ""
    out: list[str] = []
    size = 0
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") != "text":
            continue
        text = block.get("text")
        if not isinstance(text, str) or not text:
            continue
        if size >= max_chars:
            break
        chunk = text[: max_chars - size]
        out.append(chunk)
        size += len(chunk)
    return "\n".join(out)


def summarize_transcript_events(events: list[dict], keep_recent: int = 20) -> dict:
    first_user = ""
    recent: list[dict] = []
    tool_calls = Counter()

    for event in events:
        if event.get("type") != "message":
            continue
        msg = event.get("message")
        if not isinstance(msg, dict):
            continue

        role = msg.get("role")
        if role == "user" and not first_user:
            first_user = text_blocks(msg.get("content"), max_chars=2000)

        if role == "assistant":
            for part in msg.get("content", []):
                if isinstance(part, dict) and part.get("type") == "toolCall":
                    name = part.get("name")
                    if isinstance(name, str):
                        tool_calls[name] += 1

        # Keep compact recent timeline of user/assistant text only.
        if role in ("user", "assistant"):
            text = text_blocks(msg.get("content"), max_chars=280)
            if text:
                recent.append({"role": role, "text": text})

    if len(recent) > keep_recent:
        recent = recent[-keep_recent:]

    return {
        "firstUser": first_user,
        "recent": recent,
        "toolCalls": dict(tool_calls),
    }
