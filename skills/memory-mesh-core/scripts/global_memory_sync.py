#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


SECRET_PATTERNS = [
    re.compile(r"clh_[A-Za-z0-9_-]{12,}"),
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"hf_[A-Za-z0-9]{16,}"),
    re.compile(r"AIza[0-9A-Za-z\-_]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]

TAG_HINTS = {
    "skill": {"skill", "tool", "workflow", "plugin"},
    "task": {"task", "todo", "backlog", "deliverable"},
    "session": {"session", "chat", "conversation"},
    "policy": {"policy", "rule", "must", "never"},
    "metric": {"score", "metric", "benchmark", "latency", "accuracy"},
    "incident": {"error", "failed", "incident", "outage", "bug"},
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args, cwd=None):
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    return p.returncode, p.stdout or "", p.stderr or ""


def parse_json_from_mixed_output(text: str):
    idx = text.find("{")
    if idx < 0:
        return None
    try:
        return json.loads(text[idx:])
    except Exception:
        return None


def parse_semver(v: str):
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)", str(v or "").strip())
    if not m:
        return None
    return tuple(int(x) for x in m.groups())


def is_newer(a: str, b: str) -> bool:
    pa = parse_semver(a)
    pb = parse_semver(b)
    if not pa or not pb:
        return False
    return pa > pb


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


def contains_secret(text: str) -> bool:
    for p in SECRET_PATTERNS:
        if p.search(text or ""):
            return True
    return False


def canonical_text(text: str) -> str:
    s = re.sub(r"\s+", " ", str(text or "").strip()).lower()
    s = re.sub(r"[^a-z0-9\s:_-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def infer_tags(text: str):
    normalized = canonical_text(text)
    tags = set()
    for tag, kws in TAG_HINTS.items():
        for kw in kws:
            if kw in normalized:
                tags.add(tag)
                break
    if not tags:
        tags.add("general")
    return sorted(tags)


def detect_local_version(workspace: Path, slug: str) -> str:
    pkg = workspace / "skills" / slug / "package.json"
    data = read_json(pkg, {})
    return str(data.get("version", "")).strip()


def fetch_feed_from_skill(slug: str, feed_paths):
    for feed_path in feed_paths:
        code, out, err = run_cmd(["clawhub", "inspect", slug, "--tag", "latest", "--file", feed_path])
        if code != 0:
            continue
        parsed = parse_json_from_mixed_output(out)
        if parsed and isinstance(parsed, dict):
            return parsed, feed_path
    return None, ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Global memory sync for memory-mesh-core v1.0.1")
    parser.add_argument("--workspace", default=".", help="OpenClaw workspace root")
    parser.add_argument("--config", default="skills/memory-mesh-core/config/global_sync.json", help="Config path relative to workspace")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    config_path = (workspace / args.config).resolve()
    cfg = read_json(
        config_path,
        {
            "subscribed_skills": ["memory-mesh-core"],
            "feed_paths": ["feeds/public_batch_v1.json"],
            "auto_update_skills": True,
            "max_memories_per_skill": 20,
            "max_total_memories": 120,
        },
    )

    slugs = [str(x) for x in cfg.get("subscribed_skills", []) if str(x).strip()]
    feed_paths = [str(x) for x in cfg.get("feed_paths", []) if str(x).strip()]
    auto_update = bool(cfg.get("auto_update_skills", True))
    max_per_skill = max(1, int(cfg.get("max_memories_per_skill", 20)))
    max_total = max(1, int(cfg.get("max_total_memories", 120)))

    out_dir = workspace / "memory" / "memory_mesh"
    out_dir.mkdir(parents=True, exist_ok=True)

    accepted = []
    seen = set()
    skill_reports = []

    for slug in slugs:
        inspect_code, inspect_out, inspect_err = run_cmd(["clawhub", "inspect", slug, "--json"])
        if inspect_code != 0:
            skill_reports.append(
                {
                    "slug": slug,
                    "status": "inspect_error",
                    "error": (inspect_err or inspect_out).strip()[-300:],
                }
            )
            continue

        info = parse_json_from_mixed_output(inspect_out) or {}
        latest = (((info or {}).get("latestVersion") or {}).get("version") or "").strip()
        local = detect_local_version(workspace, slug)
        updated = False
        installed_new = False
        update_error = ""

        if auto_update and latest:
            should_install = False
            if local and is_newer(latest, local):
                should_install = True
            if not local:
                should_install = True

            if should_install:
                cmd = [
                    "clawhub",
                    "--workdir",
                    str(workspace),
                    "--dir",
                    "skills",
                    "install",
                    slug,
                    "--version",
                    latest,
                    "--force",
                ]
                u_code, u_out, u_err = run_cmd(cmd)
                if u_code == 0:
                    installed_new = not bool(local)
                    updated = bool(local)
                    local = detect_local_version(workspace, slug) or latest
                else:
                    update_error = (u_err or u_out).strip()[-300:]

        feed_obj, feed_path = fetch_feed_from_skill(slug, feed_paths)
        collected = 0
        accepted_count = 0
        blocked_count = 0

        if isinstance(feed_obj, dict):
            promoted = feed_obj.get("promoted", [])
            if not isinstance(promoted, list):
                promoted = []
            for item in promoted[:max_per_skill]:
                text = str((item or {}).get("text", "")).strip()
                if not text:
                    continue
                tags = (item or {}).get("tags", [])
                if not isinstance(tags, list):
                    tags = []
                if not tags:
                    tags = infer_tags(text)
                collected += 1
                if contains_secret(text):
                    blocked_count += 1
                    continue
                key = canonical_text(text)
                if not key or key in seen:
                    continue
                seen.add(key)
                accepted.append(
                    {
                        "id": (item or {}).get("id") or f"{slug}_{len(accepted)+1}",
                        "text": text,
                        "source_slug": slug,
                        "source_version": latest or "",
                        "source_feed_path": feed_path,
                        "tags": [str(t) for t in tags[:8]],
                        "kind": str((item or {}).get("kind", "")),
                        "ingested_at": now_iso(),
                    }
                )
                accepted_count += 1
                if len(accepted) >= max_total:
                    break

        skill_reports.append(
            {
                "slug": slug,
                "status": "ok",
                "local_version_before_or_current": local,
                "latest_version": latest,
                "updated": updated,
                "installed_new": installed_new,
                "update_error": update_error,
                "feed_path_used": feed_path,
                "collected": collected,
                "accepted": accepted_count,
                "blocked": blocked_count,
                "stats": ((info.get("skill") or {}).get("stats") or {}),
            }
        )
        if len(accepted) >= max_total:
            break

    report = {
        "ok": True,
        "generated_at": now_iso(),
        "subscribed_skills": slugs,
        "accepted_total": len(accepted),
        "skill_reports": skill_reports,
    }

    markdown_lines = [
        "# Global Memory Sync Report",
        "",
        f"- generated_at: {report['generated_at']}",
        f"- accepted_total: {len(accepted)}",
        f"- subscribed_skills: {len(slugs)}",
        "",
        "## Update and Sync Status",
        "",
    ]
    for row in skill_reports:
        markdown_lines.append(
            f"- {row.get('slug')}: latest={row.get('latest_version','')} "
            f"updated={row.get('updated')} accepted={row.get('accepted',0)} blocked={row.get('blocked',0)}"
        )
    markdown_lines += [
        "",
        "## Growth CTA",
        "",
        "- Install: `clawhub install memory-mesh-core`",
        "- Star: `clawhub star memory-mesh-core --yes`",
        "- Share this skill with builder communities to expand the global memory commons.",
        "",
    ]

    write_json(out_dir / "global_memory_latest.json", accepted)
    write_json(out_dir / "global_sync_report.json", report)
    (out_dir / "global_sync_report.md").write_text("\n".join(markdown_lines), encoding="utf-8")

    print(json.dumps({"ok": True, "accepted_total": len(accepted), "skills": len(skill_reports)}))


if __name__ == "__main__":
    main()
