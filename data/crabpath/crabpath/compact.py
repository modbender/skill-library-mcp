"""Daily note compaction utilities."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from ._util import _extract_json
from .hasher import HashEmbedder
from .inject import inject_node
from .journal import log_event
from .store import load_state, save_state

COMPACT_DAILY_PROMPT = (
    "Summarize the following daily note into key facts, decisions, and corrections. "
    "Return JSON: {\"facts\": [\"fact one\", \"fact two\"]}. "
    "Keep each fact short and semantically focused."
)
_NOTE_PATTERN = re.compile(r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})\.md$")


@dataclass
class CompactReport:
    files_scanned: int
    files_compacted: int
    files_skipped: int
    nodes_injected: int
    lines_before: int
    lines_after: int


def _is_target_file(path: Path) -> bool:
    """Return True when path matches YYYY-MM-DD.md."""
    return bool(_NOTE_PATTERN.fullmatch(path.name))


def _parse_note_date(path: Path) -> tuple[int, int, int] | None:
    """Parse date parts from a note filename."""
    match = _NOTE_PATTERN.fullmatch(path.name)
    if match is None:
        return None
    year = int(match.group("year"))
    month = int(match.group("month"))
    day = int(match.group("day"))
    return year, month, day


def _is_old_enough(path: Path, max_age_days: int, *, today: datetime) -> bool:
    """Return True when file date is strictly older than max_age_days."""
    parts = _parse_note_date(path)
    if parts is None:
        return False
    file_date = datetime(*parts, tzinfo=timezone.utc)
    age = today - file_date
    return age.days > max_age_days


def _split_markdown_sections(content: str) -> list[tuple[str, str]]:
    """Extract ``(header, first_line)`` pairs from markdown sections."""
    lines = content.splitlines()
    sections: list[tuple[str, str]] = []
    current_header: str | None = None
    first_line: str = ""

    def flush() -> None:
        nonlocal current_header, first_line
        if current_header is None:
            return
        sections.append((current_header, first_line.strip()))
        current_header = None
        first_line = ""

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            flush()
            current_header = stripped
            continue
        if first_line == "":
            first_line = stripped

    flush()

    if not sections:
        return []
    return sections


def _fallback_facts(content: str) -> list[str]:
    """Fallback fact extraction from headers plus first line per section."""
    sections = _split_markdown_sections(content)
    if sections:
        return [f"{header}\n{fact}" if fact else header for header, fact in sections]
    return [line.strip() for line in content.splitlines() if line.strip()][:20]


def _summary_facts(summary: str) -> list[str]:
    """Parse LLM summary into per-fact lines."""
    payload = _extract_json(summary) or summary

    if isinstance(payload, dict):
        for key in ("facts", "items", "points", "bullets", "corrections"):
            raw = payload.get(key)
            if isinstance(raw, list):
                return [str(item).strip() for item in raw if str(item).strip()]
        value = payload.get("summary")
        if isinstance(value, str):
            payload = value

    if isinstance(payload, list):
        return [str(item).strip() for item in payload if str(item).strip()]
    if not isinstance(payload, str):
        return []
    lines = [line.strip(" -\t") for line in payload.splitlines() if line.strip()]
    if len(lines) == 1:
        compacted = [piece.strip() for piece in payload.split(".") if piece.strip()]
        if compacted:
            return compacted
    return lines


def _line_limit(lines: list[str], target_lines: int) -> list[str]:
    """Trim a candidate compact block to approximate target_lines."""
    if target_lines <= 0:
        return []
    if len(lines) <= target_lines:
        return lines
    return lines[:target_lines]


def _compact_content(facts: list[str], target_lines: int) -> str:
    """Build compact note content from extracted facts."""
    compact_lines: list[str] = []
    for item in facts:
        compact_lines.extend(part for part in item.splitlines() if part.strip())
    return "\n".join(_line_limit(compact_lines, target_lines)).strip()


def _node_id_for_fact(file_path: Path, idx: int, fact: str) -> str:
    """Build deterministic node id."""
    digest = hashlib.sha256(f"{file_path}:{idx}:{fact}".encode("utf-8")).hexdigest()[:12]
    return f"learning::compact::{digest}"


def _resolve_embed_fn(
    index: object,
    meta_embed_dim: int | None,
    embed_fn: Callable[[str], list[float]] | None,
) -> Callable[[str], list[float]]:
    """Resolve embedding callback and enforce index compatibility."""
    if embed_fn is not None:
        return embed_fn

    if meta_embed_dim is None:
        return HashEmbedder().embed

    if isinstance(index, dict) and index:
        first_vector = next(iter(index.values()))
        if len(first_vector) != HashEmbedder().dim:
            raise ValueError(
                "embed_fn is required because the state index dimension does not match hash-v1 embedding."
            )
        return HashEmbedder().embed

    if meta_embed_dim != HashEmbedder().dim:
        raise ValueError(
            "embed_fn is required because the state index dimension does not match hash-v1 embedding."
        )
    return HashEmbedder().embed


def compact_daily_notes(
    state_path: str,
    memory_dir: str,
    *,
    max_age_days: int = 7,
    min_lines_to_compact: int = 20,
    target_lines: int = 15,
    embed_fn: Callable[[str], list[float]] | None = None,
    llm_fn: Callable[[str, str], str] | None = None,
    journal_path: str | None = None,
    dry_run: bool = False,
) -> CompactReport:
    """Compact older daily notes, inject summaries, and rewrite compact files."""
    if max_age_days < 0:
        raise ValueError("max_age_days must be >= 0")
    if min_lines_to_compact < 0:
        raise ValueError("min_lines_to_compact must be >= 0")
    if target_lines <= 0:
        raise ValueError("target_lines must be >= 1")

    graph, index, meta = load_state(state_path)
    resolved_embed_fn = _resolve_embed_fn(
        index._vectors,
        meta.get("embedder_dim") if isinstance(meta.get("embedder_dim"), int) else None,
        embed_fn,
    )
    notes_root = Path(memory_dir).expanduser()
    if not notes_root.exists():
        raise SystemExit(f"memory directory not found: {notes_root}")
    if not notes_root.is_dir():
        raise SystemExit(f"memory path is not a directory: {notes_root}")

    report = CompactReport(
        files_scanned=0,
        files_compacted=0,
        files_skipped=0,
        nodes_injected=0,
        lines_before=0,
        lines_after=0,
    )
    today = datetime.now(timezone.utc)

    for file_path in sorted(notes_root.glob("*.md")):
        if not _is_target_file(file_path):
            continue
        report.files_scanned += 1

        if not _is_old_enough(file_path, max_age_days=max_age_days, today=today):
            report.files_skipped += 1
            continue

        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        if len(lines) <= min_lines_to_compact:
            report.files_skipped += 1
            continue

        if llm_fn is None:
            facts = _fallback_facts(content)
        else:
            try:
                summary = llm_fn(COMPACT_DAILY_PROMPT, content)
            except (Exception, SystemExit):  # noqa: BLE001
                summary = ""
            facts = _summary_facts(summary)
            if not facts:
                facts = _fallback_facts(content)

        if not facts:
            report.files_skipped += 1
            continue

        compact_text = _compact_content(facts, target_lines)
        if compact_text:
            compact_lines = compact_text.splitlines()
        else:
            compact_lines = []

        report.files_compacted += 1
        report.lines_before += len(lines)
        report.lines_after += len(compact_lines)

        if dry_run:
            continue

        file_path.write_text("\n".join(compact_lines) + ("\n" if compact_lines else ""), encoding="utf-8")

        for idx, fact in enumerate(facts):
            node_id = _node_id_for_fact(file_path, idx, fact)
            if graph.get_node(node_id) is not None:
                continue
            payload = inject_node(
                graph=graph,
                index=index,
                node_id=node_id,
                content=fact[:2000],
                summary=fact[:120],
                metadata={"source": str(file_path), "authority": "overlay", "type": "TEACHING"},
                embed_fn=resolved_embed_fn,
                connect_top_k=3,
                connect_min_sim=0.0,
            )
            if payload["node_id"] == node_id:
                report.nodes_injected += 1

        save_state(
            graph=graph,
            index=index,
            path=state_path,
            embedder_name=meta.get("embedder_name", "hash-v1"),
            embedder_dim=meta.get("embedder_dim"),
            meta=meta,
        )

    if journal_path is not None:
        log_event(
            {
                "type": "compact_daily_notes",
                "files_scanned": report.files_scanned,
                "files_compacted": report.files_compacted,
                "files_skipped": report.files_skipped,
                "nodes_injected": report.nodes_injected,
                "lines_before": report.lines_before,
                "lines_after": report.lines_after,
                "dry_run": dry_run,
            },
            journal_path=journal_path,
        )

    return report
