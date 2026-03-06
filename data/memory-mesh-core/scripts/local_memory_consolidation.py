#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


MAX_TEXT_LEN = 320
MIN_TEXT_LEN = 24


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip())


def canonical(text: str) -> str:
    s = normalize(text).lower()
    s = re.sub(r"[^a-z0-9\s:_-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def stable_id(text: str) -> str:
    return "cons_" + hashlib.sha256(canonical(text).encode("utf-8")).hexdigest()[:16]


def infer_tags(source_file: str, text: str):
    tags = set()
    src = source_file.lower()
    txt = canonical(text)

    if "session_bridge" in src:
        tags.add("session")
    if "skill_memory" in src or "/skills/" in src:
        tags.add("skill")
    if "task_memory" in src or "task_board" in src:
        tags.add("task")
    if "gene_memory" in src:
        tags.add("gene")
    if "policy" in txt or "must " in txt or txt.startswith("rule:"):
        tags.add("policy")
    if any(k in txt for k in ["error", "failed", "incident", "outage", "bug"]):
        tags.add("incident")
    if any(k in txt for k in ["score", "latency", "benchmark", "accuracy", "metric"]):
        tags.add("metric")
    if any(k in txt for k in ["prefer", "tone", "style", "format"]):
        tags.add("preference")

    if not tags:
        tags.add("general")
    return sorted(tags)


def collect_source_files(workspace: Path):
    candidates = [
        workspace / "MEMORY.md",
        workspace / "memory" / "shared" / "session_bridge.md",
        workspace / "memory" / "shared" / "skill_memory.md",
        workspace / "memory" / "shared" / "task_memory.md",
        workspace / "memory" / "shared" / "task_board.md",
        workspace / "memory" / "shared" / "gene_memory.md",
    ]
    memory_dir = workspace / "memory"
    if memory_dir.exists():
        for p in sorted(memory_dir.glob("20*.md")):
            candidates.append(p)
    return [p for p in candidates if p.exists() and p.is_file()]


def extract_entries(path: Path):
    out = []
    in_code = False
    for idx, raw in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
        line = raw.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not line or line.startswith("#"):
            continue

        text = ""
        if line.startswith(("- ", "* ")):
            text = line[2:].strip()
        elif re.match(r"^\d+\.\s+", line):
            text = re.sub(r"^\d+\.\s+", "", line).strip()
        elif ":" in line and len(line) <= MAX_TEXT_LEN:
            head = line.split(":", 1)[0].strip().lower()
            if head in {"rule", "lesson", "insight", "policy", "decision", "note", "action"}:
                text = line

        text = normalize(text)
        if len(text) < MIN_TEXT_LEN:
            continue
        if len(text) > MAX_TEXT_LEN:
            text = text[: MAX_TEXT_LEN - 3] + "..."
        if text.lower().startswith(("[user]", "[assistant]", "[system]")):
            continue
        if "output exactly one final line" in text.lower():
            continue

        out.append(
            {
                "id": stable_id(text),
                "text": text,
                "source_file": str(path),
                "source_line": idx,
                "tags": infer_tags(str(path), text),
            }
        )
    return out


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Consolidate local memory into tagged entries before contribution.")
    parser.add_argument("--workspace", default=".", help="OpenClaw workspace root")
    parser.add_argument("--max-entries", type=int, default=400, help="Max consolidated entries")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    out_dir = workspace / "memory" / "memory_mesh"
    out_dir.mkdir(parents=True, exist_ok=True)

    entries = []
    seen = set()
    for src in collect_source_files(workspace):
        for item in extract_entries(src):
            key = canonical(item["text"])
            if not key or key in seen:
                continue
            seen.add(key)
            entries.append(item)
            if len(entries) >= max(1, args.max_entries):
                break
        if len(entries) >= max(1, args.max_entries):
            break

    tag_counts = {}
    for e in entries:
        for t in e.get("tags", []):
            tag_counts[t] = tag_counts.get(t, 0) + 1

    payload = {
        "schema": "memory-mesh-consolidated-v1",
        "generated_at": now_iso(),
        "entry_count": len(entries),
        "tag_counts": tag_counts,
        "entries": entries,
    }

    write_json(out_dir / "consolidated_memory.json", payload)

    md_lines = [
        "# Memory Mesh Local Consolidation",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- entry_count: {len(entries)}",
        "",
        "## Tag Summary",
        "",
    ]
    if not tag_counts:
        md_lines.append("- (none)")
    else:
        for tag, count in sorted(tag_counts.items(), key=lambda x: (-x[1], x[0])):
            md_lines.append(f"- {tag}: {count}")
    md_lines += ["", "## Sample Entries", ""]
    for item in entries[:30]:
        md_lines.append(f"- [{','.join(item.get('tags', []))}] {item['text']}")
    md_lines.append("")
    (workspace / "memory" / "shared" / "memory_mesh_consolidated.md").write_text("\n".join(md_lines), encoding="utf-8")

    print(json.dumps({"ok": True, "entry_count": len(entries), "tag_counts": tag_counts}))


if __name__ == "__main__":
    main()
