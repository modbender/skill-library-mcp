"""Message splitting helpers (parser layer).

Goal: avoid corrupting Markdown code fences when a platform enforces a hard
per-message character limit (Discord webhooks: ~2000).

This module intentionally does not depend on platform adapters so it can be
unit-tested in isolation.
"""

from __future__ import annotations

from typing import List


_FENCE = "```"


def _is_fence_line(line: str) -> bool:
    return line.lstrip().startswith(_FENCE)


def _split_plain_text(text: str, limit: int) -> List[str]:
    if limit <= 0:
        return [text]
    if len(text) <= limit:
        return [text]

    chunks: List[str] = []
    start = 0
    threshold = max(1, limit // 2)
    text_len = len(text)

    while start < text_len:
        end = min(start + limit, text_len)
        if end < text_len:
            split_at = text.rfind("\n", start, end)
            if split_at != -1 and (split_at - start) >= threshold:
                end = split_at + 1
        if end <= start:
            end = min(start + limit, text_len)
        chunks.append(text[start:end])
        start = end

    return chunks


def split_markdown_code_fence_safe(text: str, limit: int) -> List[str]:
    """Split text into <=limit chunks while keeping code fences self-contained.

    If the input contains no triple-backtick fences, falls back to plain split
    with no data loss: "".join(chunks) == text.

    When splitting *inside* a fenced code block, this function closes the fence
    at the end of the chunk and re-opens it at the start of the next chunk,
    preserving the original language tag (```py) when present.
    """
    text = text or ""
    if limit <= 0:
        return [text]
    if len(text) <= limit:
        return [text]

    if _FENCE not in text:
        return _split_plain_text(text, limit)

    lines = text.splitlines(keepends=True)

    chunks: List[str] = []
    buf = ""

    in_code = False
    open_fence = _FENCE  # e.g., ``` or ```python (without trailing newline)

    def flush(*, final: bool = False) -> None:
        nonlocal buf
        if not buf:
            return

        if in_code:
            closing = _FENCE if buf.endswith("\n") else "\n" + _FENCE
            # If limit is extremely small, fall back to hard cut (best-effort).
            if len(buf) + len(closing) > limit:
                buf = buf[: max(0, limit - len(closing))]
            buf += closing

        chunks.append(buf)
        buf = ""

        if in_code and not final:
            reopen = open_fence.rstrip("\n") + "\n"
            if len(reopen) >= limit:
                reopen = _FENCE + "\n"
            buf = reopen

    def soft_limit() -> int:
        if not in_code:
            return limit
        # Reserve room for a worst-case inserted "\n```" closing fence.
        return max(1, limit - 4)

    for line in lines:
        if not line:
            continue

        max_len = soft_limit()
        if len(line) <= max_len:
            if len(buf) + len(line) > max_len and buf:
                flush()
            # Recompute after flush (may have reopened a fence line).
            max_len = soft_limit()
            if len(buf) + len(line) <= max_len:
                buf += line
            else:
                # Reopen fence overhead can make a previously-fit line not fit.
                remaining = line
                while remaining:
                    max_len = soft_limit()
                    room = max_len - len(buf)
                    if room <= 0:
                        flush()
                        continue
                    buf += remaining[:room]
                    remaining = remaining[room:]
                    if remaining:
                        flush()
        else:
            if buf:
                flush()
            remaining = line
            while remaining:
                max_len = soft_limit()
                room = max_len - len(buf)
                if room <= 0:
                    flush()
                    continue
                buf += remaining[:room]
                remaining = remaining[room:]
                if remaining:
                    flush()

        if _is_fence_line(line):
            if not in_code:
                in_code = True
                open_fence = line.rstrip("\n")
            else:
                in_code = False
                open_fence = _FENCE

    if buf:
        flush(final=True)

    return chunks
