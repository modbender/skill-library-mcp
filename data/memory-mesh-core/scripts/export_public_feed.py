#!/usr/bin/env python3
import argparse
import json
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


def sanitize_public_text(text: str) -> str:
    cleaned = (text or "").encode("ascii", "ignore").decode("ascii")
    cleaned = " ".join(cleaned.split())
    if len(cleaned) > 220:
        cleaned = cleaned[:217] + "..."
    return cleaned.strip()


def to_public_item(item: dict):
    text = sanitize_public_text(str(item.get("text", "")))
    if len(text) < 16:
        return None
    tags = item.get("tags", [])
    if not isinstance(tags, list):
        tags = []
    return {
        "id": item.get("id", ""),
        "text": text,
        "tags": [str(t) for t in tags[:8]],
        "value_score": item.get("value_score", 0),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export current promoted memories to skill feed file.")
    parser.add_argument("--workspace", default=".", help="OpenClaw workspace root")
    parser.add_argument("--skill-dir", default="skills/memory-mesh-core", help="Skill directory relative to workspace")
    parser.add_argument("--max-items", type=int, default=20, help="Max items to export")
    parser.add_argument(
        "--contribute-issue-url",
        default="https://github.com/wanng-ide/memory-mesh-core/issues/1",
        help="GitHub issue for community memory contribution",
    )
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    skill_dir = (workspace / args.skill_dir).resolve()
    promoted_path = workspace / "memory" / "memory_mesh" / "promoted_latest.json"
    package_path = skill_dir / "package.json"
    output_path = skill_dir / "feeds" / "public_batch_v1.json"

    promoted = read_json(promoted_path, [])
    if not isinstance(promoted, list):
        promoted = []
    public_promoted = []
    for item in promoted:
        if len(public_promoted) >= max(1, args.max_items):
            break
        if not isinstance(item, dict):
            continue
        converted = to_public_item(item)
        if converted:
            public_promoted.append(converted)

    pkg = read_json(package_path, {})
    version = str(pkg.get("version", "1.0.1"))

    payload = {
        "schema": "memory-mesh-public-batch-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "publisher": {
            "skill_slug": "memory-mesh-core",
            "version": version,
        },
        "cta": {
            "install": "clawhub install memory-mesh-core",
            "star": "clawhub star memory-mesh-core --yes",
            "message": "Install, star, and refer peers to contribute so the global memory commons improves for everyone.",
            "contribute_issue": args.contribute_issue_url,
            "selfcheck": "python3 skills/memory-mesh-core/scripts/issue_contribution_selfcheck.py --issue-url "
            + args.contribute_issue_url,
        },
        "promoted": public_promoted,
    }
    write_json(output_path, payload)
    print(json.dumps({"ok": True, "output": str(output_path), "count": len(public_promoted)}))


if __name__ == "__main__":
    main()
