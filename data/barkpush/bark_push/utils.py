from __future__ import annotations

import re
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable
from urllib.parse import urlparse


URL_RE = re.compile(r"https?://[^\s]+", re.IGNORECASE)
IMAGE_RE = re.compile(r"https?://[^\s]+\.(jpg|jpeg|png|gif|webp|bmp|tiff|svg)(\?[^\s]+)?$", re.IGNORECASE)


def now_ts() -> int:
    return int(time.time())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_push_id() -> str:
    return str(uuid.uuid4())


def is_url(text: str) -> bool:
    return bool(URL_RE.fullmatch(text.strip()))


def is_image_url(text: str) -> bool:
    return bool(IMAGE_RE.fullmatch(text.strip()))


def extract_urls(text: str) -> list[str]:
    return URL_RE.findall(text)


def extract_image_urls(text: str) -> list[str]:
    return [u for u in extract_urls(text) if is_image_url(u)]


def strip_urls(text: str) -> str:
    stripped = URL_RE.sub(" ", text)
    return " ".join(stripped.split()).strip()


def summarize_text(text: str, n: int = 6) -> str:
    s = (text or "").strip()
    if not s:
        return ""
    if len(s) <= n:
        return s
    return s[:n]


def safe_host(url: str) -> str:
    try:
        parsed = urlparse(url)
        return parsed.netloc or ""
    except Exception:
        return ""


def to_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    s = str(value).strip().lower()
    if s in {"1", "true", "yes", "y", "on"}:
        return True
    if s in {"0", "false", "no", "n", "off"}:
        return False
    return None


def compact_kv(items: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in items:
        if v is None:
            continue
        if isinstance(v, str) and v == "":
            continue
        out[k] = v
    return out


@dataclass(frozen=True)
class Preview:
    kind: str
    text: str


def build_preview(body: str | None, markdown: str | None, url: str | None, image: str | None) -> Preview:
    if image:
        return Preview(kind="image", text="(图片省略)")
    if url and not (body or markdown):
        return Preview(kind="url", text=summarize_text(url, 6))
    text = markdown or body or ""
    return Preview(kind="text", text=summarize_text(text, 6))
