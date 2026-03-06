#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def read_json(path: Path, fallback):
    try:
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sanitize_text(text: str) -> str:
    cleaned = (text or "").encode("ascii", "ignore").decode("ascii")
    cleaned = " ".join(cleaned.split()).strip()
    if len(cleaned) > 240:
        cleaned = cleaned[:237] + "..."
    return cleaned


def canonical(text: str) -> str:
    s = re.sub(r"\s+", " ", str(text or "").strip()).lower()
    return re.sub(r"[^a-z0-9\s:_-]", "", s).strip()


def stable_contribution_id(memory_text: str, source_ref: str) -> str:
    base = f"{canonical(memory_text)}|{canonical(source_ref)}"
    return "contrib_" + hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]


def build_source_ref(workspace: Path, item: dict) -> str:
    src = str(item.get("source_file", "")).strip()
    if not src:
        return ""
    try:
        src_path = Path(src).expanduser().resolve()
        rel = src_path.relative_to(workspace)
        src_str = rel.as_posix()
    except Exception:
        src_str = Path(src).name
    line = item.get("source_line")
    if line:
        return f"{src_str}:{line}"
    return src_str


def to_comment_item(workspace: Path, item: dict, now_utc: str):
    memory_text = sanitize_text(str(item.get("text", "")))
    if len(memory_text) < 16:
        return None

    tags = item.get("tags", [])
    if not isinstance(tags, list) or not tags:
        tags = ["general"]

    metrics = item.get("metrics", {}) if isinstance(item.get("metrics"), dict) else {}
    risk_flags = item.get("risk_reasons", [])
    if not isinstance(risk_flags, list):
        risk_flags = []

    source_ref = build_source_ref(workspace, item)
    contribution_id = stable_contribution_id(memory_text, source_ref)

    return {
        "schema": "memory_contribution_v1",
        "contribution_id": contribution_id,
        "agent_id": "memory-mesh-core",
        "memory_text": memory_text,
        "tags": [str(t) for t in tags[:8]],
        "evidence": "Promoted by local value-scoring and safety gating in memory-mesh-core.",
        "confidence": round(float(metrics.get("confidence", 0.7)), 4),
        "impact": round(float(metrics.get("impact", 0.6)), 4),
        "actionability": round(float(metrics.get("actionability", 0.6)), 4),
        "novelty": round(float(metrics.get("novelty", 0.5)), 4),
        "risk_flags": [str(x) for x in risk_flags[:8]],
        "source_ref": source_ref,
        "timestamp_utc": now_utc,
    }


def build_markdown(issue_url: str, items: list[dict]) -> str:
    lines = [
        "# GitHub Issue Contribution Seed",
        "",
        f"- target_issue: {issue_url}",
        f"- item_count: {len(items)}",
        "",
        "Paste one JSON object per comment into the issue thread.",
        "",
    ]
    for idx, item in enumerate(items, start=1):
        lines += [
            f"## Comment {idx}",
            "",
            "```json",
            json.dumps(item, indent=2, ensure_ascii=False),
            "```",
            "",
        ]
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export promoted memories to GitHub issue comment payloads.")
    parser.add_argument("--workspace", default=".", help="OpenClaw workspace root")
    parser.add_argument("--skill-dir", default="skills/memory-mesh-core", help="Skill directory relative to workspace")
    parser.add_argument(
        "--issue-url",
        default="https://github.com/wanng-ide/memory-mesh-core/issues/1",
        help="GitHub issue URL for contribution intake",
    )
    parser.add_argument("--max-items", type=int, default=5, help="Max promoted items to export")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    skill_dir = (workspace / args.skill_dir).resolve()
    promoted_path = workspace / "memory" / "memory_mesh" / "promoted_latest.json"
    out_json = skill_dir / "feeds" / "github_issue_batch_v1.json"
    out_md = workspace / "memory" / "memory_mesh" / "github_issue_comment_seed.md"

    promoted = read_json(promoted_path, [])
    if not isinstance(promoted, list):
        promoted = []

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    items = []
    for raw in promoted:
        if len(items) >= max(1, args.max_items):
            break
        if not isinstance(raw, dict):
            continue
        converted = to_comment_item(workspace, raw, now_utc)
        if converted:
            items.append(converted)

    payload = {
        "schema": "memory-mesh-github-issue-batch-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "issue_url": args.issue_url,
        "count": len(items),
        "items": items,
    }
    write_json(out_json, payload)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(args.issue_url, items), encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": True,
                "count": len(items),
                "issue_url": args.issue_url,
                "json_output": str(out_json),
                "markdown_output": str(out_md),
            }
        )
    )


if __name__ == "__main__":
    main()
