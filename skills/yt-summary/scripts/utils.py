"""Utility functions for YouTube summary skill."""

import re
from urllib.parse import urlparse, parse_qs


def extract_video_id(url_or_id: str) -> str:
    """Extract YouTube video ID from various URL formats or a bare ID."""
    url_or_id = url_or_id.strip()

    # Already a bare ID (11 chars, alphanumeric + dash/underscore)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id

    # youtu.be/ID
    m = re.search(r'youtu\.be/([\w-]{11})', url_or_id)
    if m:
        return m.group(1)

    # youtube.com/shorts/ID or youtube.com/live/ID
    m = re.search(r'youtube\.com/(?:shorts|live)/([\w-]{11})', url_or_id)
    if m:
        return m.group(1)

    # youtube.com/watch?v=ID (including m.youtube.com)
    parsed = urlparse(url_or_id)
    if parsed.hostname and 'youtube.com' in parsed.hostname:
        qs = parse_qs(parsed.query)
        if 'v' in qs:
            vid = qs['v'][0]
            if not re.match(r'^[a-zA-Z0-9_-]{11}$', vid):
                raise ValueError(f"Invalid video ID in URL: {vid}")
            return vid

    # Last resort: find 11-char ID pattern
    m = re.search(r'[\?&]v=([\w-]{11})', url_or_id)
    if m:
        return m.group(1)

    raise ValueError(f"Could not extract video ID from: {url_or_id}")


def count_tokens_approx(text: str) -> int:
    """Cheap token estimate: words * 1.3."""
    return int(len(text.split()) * 1.3)


def chunk_text(text: str, chunk_size: int = 3000, overlap: int = 100) -> list[str]:
    """Split text into chunks of approximately chunk_size tokens with overlap."""
    words = text.split()
    # Convert token counts to word counts (reverse the 1.3 factor)
    words_per_chunk = int(chunk_size / 1.3)
    words_overlap = int(overlap / 1.3)

    chunks = []
    start = 0
    while start < len(words):
        end = start + words_per_chunk
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start = end - words_overlap
        if start >= len(words):
            break
    return chunks


def truncate_for_telegram(text: str, max_chars: int = 3900) -> str:
    """Truncate text at a sentence boundary to fit Telegram limits."""
    if len(text) <= max_chars:
        return text

    truncated = text[:max_chars]
    # Find last sentence boundary
    for sep in ['\n\n', '.\n', '. ', '\n']:
        idx = truncated.rfind(sep)
        if idx > max_chars * 0.5:
            return truncated[:idx + len(sep)].rstrip() + '\n\n… _(truncated)_'

    return truncated.rstrip() + '\n\n… _(truncated)_'


def format_duration(seconds: int) -> str:
    """Format seconds into human-readable duration."""
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    if h:
        return f"{h}h {m}min"
    return f"{m}min"
