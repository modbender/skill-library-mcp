#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple


WEIGHTS = {
    "reuse_potential": 0.22,
    "impact": 0.20,
    "confidence": 0.16,
    "actionability": 0.14,
    "novelty": 0.10,
    "freshness": 0.08,
    "evidence_quality": 0.10,
    "risk_penalty": 0.12,
}

REUSE_KW = {
    "always",
    "never",
    "if",
    "when",
    "retry",
    "timeout",
    "fallback",
    "idempotent",
    "policy",
    "workflow",
    "pattern",
    "guardrail",
    "checklist",
    "validate",
    "deterministic",
}
IMPACT_KW = {
    "fix",
    "stability",
    "faster",
    "latency",
    "performance",
    "reduce",
    "error",
    "success",
    "reliable",
    "availability",
    "coverage",
    "prevent",
}
CONFIDENCE_KW = {"verified", "tested", "passed", "benchmark", "measured", "observed", "reproduced", "confirmed"}
ACTION_KW = {"do", "run", "set", "add", "remove", "check", "ensure", "avoid", "prefer", "limit", "block"}
EVIDENCE_KW = {"log", "trace", "report", "metric", "diff", "result", "assert", "test"}

SECRET_PATTERNS = [
    re.compile(r"clh_[A-Za-z0-9_-]{12,}"),
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"hf_[A-Za-z0-9]{16,}"),
    re.compile(r"AIza[0-9A-Za-z\-_]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(api[_-]?key|token|secret|password)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{10,}", re.IGNORECASE),
]
PII_PATTERNS = [
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b\+?[0-9][0-9\- ]{7,}[0-9]\b"),
]

MIN_LEN = 28
MAX_LEN = 420

TAG_KEYWORDS = {
    "skill": {"skill", "skills", "tool", "tools", "workflow", "plugin", "capability"},
    "task": {"task", "todo", "backlog", "deliverable", "milestone", "deadline"},
    "session": {"session", "conversation", "chat", "context", "turn"},
    "policy": {"policy", "rule", "must", "never", "always", "guardrail"},
    "incident": {"incident", "outage", "failure", "failed", "error", "root cause"},
    "metric": {"metric", "score", "latency", "throughput", "accuracy", "benchmark"},
    "preference": {"prefer", "style", "tone", "format", "constraint"},
    "gene": {"gene", "capsule", "evolution"},
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def read_json(path: Path, fallback):
    try:
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def canonical_text(text: str) -> str:
    s = normalize_text(text).lower()
    s = s.replace("...", " ")
    s = re.sub(r"[^a-z0-9\s:_-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def text_id(text: str) -> str:
    base = canonical_text(text)
    return "mem_" + hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]


def infer_tags(source_file: str, text: str, base_tags: List[str] = None) -> List[str]:
    tags = set(base_tags or [])
    src = str(source_file or "").lower()
    normalized = canonical_text(text)

    if "skill_memory" in src or "/skills/" in src:
        tags.add("skill")
    if "task_memory" in src or "task_board" in src:
        tags.add("task")
    if "session_bridge" in src:
        tags.add("session")
    if "gene_memory" in src:
        tags.add("gene")
    if "evolution" in src:
        tags.add("evolution")

    for tag, kws in TAG_KEYWORDS.items():
        for kw in kws:
            if kw in normalized:
                tags.add(tag)
                break

    if not tags:
        tags.add("general")
    return sorted(tags)


def iter_source_files(workspace: Path) -> List[Path]:
    files = []
    root_memory = workspace / "MEMORY.md"
    if root_memory.exists():
        files.append(root_memory)

    memory_dir = workspace / "memory"
    if memory_dir.exists():
        for path in sorted(memory_dir.rglob("*.md")):
            if "memory_mesh" in path.parts:
                continue
            if path.name in {"session_bridge.md", "task_board.md"}:
                continue
            files.append(path)
    return files


def extract_candidates(path: Path, content: str) -> List[Dict]:
    out = []
    in_code = False
    noise_re = re.compile(
        r"(cron:|subagent task|queued announce|completed successfully|current time:|session_id:|tool_count:|output exactly one final line)",
        re.IGNORECASE,
    )
    for idx, raw in enumerate(content.splitlines(), start=1):
        line = raw.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not line:
            continue
        if line.startswith("#"):
            continue

        candidate = ""
        if line.startswith(("- ", "* ")):
            candidate = line[2:].strip()
        elif re.match(r"^\d+\.\s+", line):
            candidate = re.sub(r"^\d+\.\s+", "", line).strip()
        elif ":" in line and len(line) <= MAX_LEN:
            # Keep concise key statements like "Rule: ..." or "Lesson: ..."
            head = line.split(":", 1)[0].strip().lower()
            if head in {"rule", "lesson", "insight", "policy", "decision", "note"}:
                candidate = line

        candidate = normalize_text(candidate)
        if len(candidate) < MIN_LEN or len(candidate) > MAX_LEN:
            continue
        if noise_re.search(candidate):
            continue
        if candidate.lower().startswith(("[user]", "[assistant]", "[system]")):
            continue
        if candidate.startswith("http://") or candidate.startswith("https://"):
            continue

        out.append(
            {
                "id": text_id(candidate),
                "text": candidate,
                "source_file": str(path),
                "source_line": idx,
                "tags": infer_tags(str(path), candidate),
            }
        )
    return out


def load_consolidated_candidates(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(obj, dict):
        return []
    entries = obj.get("entries", [])
    if not isinstance(entries, list):
        return []

    out = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        text = normalize_text(str(item.get("text", "")))
        if len(text) < MIN_LEN or len(text) > MAX_LEN:
            continue
        source_file = str(item.get("source_file", str(path)))
        tags = item.get("tags", [])
        if not isinstance(tags, list):
            tags = []
        out.append(
            {
                "id": text_id(text),
                "text": text,
                "source_file": source_file,
                "source_line": int(item.get("source_line", 0) or 0),
                "tags": infer_tags(source_file, text, tags),
            }
        )
    return out


def keyword_score(text: str, words: set, cap: int) -> float:
    lower = text.lower()
    hit = sum(1 for w in words if w in lower)
    return min(1.0, hit / float(cap))


def freshness_score(age_days: float) -> float:
    if age_days <= 1:
        return 1.0
    if age_days <= 3:
        return 0.9
    if age_days <= 7:
        return 0.75
    if age_days <= 14:
        return 0.6
    if age_days <= 30:
        return 0.4
    return 0.2


def detect_risks(text: str) -> Tuple[float, List[str], bool]:
    reasons: List[str] = []
    blocked = False
    penalty = 0.0

    for pat in SECRET_PATTERNS:
        if pat.search(text):
            reasons.append("secret_pattern")
            penalty = max(penalty, 1.0)
            blocked = True
            break

    for pat in PII_PATTERNS:
        if pat.search(text):
            reasons.append("pii_pattern")
            penalty = max(penalty, 0.6)
            break

    if "private" in text.lower() and "key" in text.lower():
        reasons.append("private_key_hint")
        penalty = max(penalty, 1.0)
        blocked = True

    return min(1.0, penalty), reasons, blocked


def score_candidate(candidate: Dict, seen_ids: set, file_mtime: float, now_ts: float) -> Dict:
    text = candidate["text"]
    age_days = max(0.0, (now_ts - file_mtime) / 86400.0)

    reuse = min(1.0, 0.2 + keyword_score(text, REUSE_KW, cap=5))
    impact = min(1.0, 0.15 + keyword_score(text, IMPACT_KW, cap=4))
    confidence = min(1.0, 0.35 + keyword_score(text, CONFIDENCE_KW, cap=3))
    actionability = min(1.0, 0.2 + keyword_score(text, ACTION_KW, cap=4))
    novelty = 0.7 if candidate["id"] in seen_ids else 1.0
    freshness = freshness_score(age_days)

    evidence = min(1.0, 0.3 + keyword_score(text, EVIDENCE_KW, cap=3))
    if re.search(r"\b\d+(\.\d+)?%?\b", text):
        evidence = min(1.0, evidence + 0.2)
    if "http://" in text or "https://" in text:
        evidence = min(1.0, evidence + 0.2)

    risk_penalty, risk_reasons, blocked = detect_risks(text)

    value = (
        WEIGHTS["reuse_potential"] * reuse
        + WEIGHTS["impact"] * impact
        + WEIGHTS["confidence"] * confidence
        + WEIGHTS["actionability"] * actionability
        + WEIGHTS["novelty"] * novelty
        + WEIGHTS["freshness"] * freshness
        + WEIGHTS["evidence_quality"] * evidence
        - WEIGHTS["risk_penalty"] * risk_penalty
    )
    value_score = max(0.0, min(100.0, value * 100.0))

    return {
        **candidate,
        "metrics": {
            "reuse_potential": round(reuse, 4),
            "impact": round(impact, 4),
            "confidence": round(confidence, 4),
            "actionability": round(actionability, 4),
            "novelty": round(novelty, 4),
            "freshness": round(freshness, 4),
            "evidence_quality": round(evidence, 4),
            "risk_penalty": round(risk_penalty, 4),
            "age_days": round(age_days, 2),
        },
        "value_score": round(value_score, 2),
        "risk_reasons": risk_reasons,
        "blocked": blocked,
    }


def is_promotable(scored: Dict, min_score: float) -> Tuple[bool, List[str]]:
    reasons = []
    m = scored["metrics"]
    if scored["blocked"]:
        reasons.append("blocked_by_security")
    if scored["value_score"] < min_score:
        reasons.append("low_value_score")
    if m["confidence"] < 0.45:
        reasons.append("low_confidence")
    if m["evidence_quality"] < 0.30:
        reasons.append("low_evidence")
    if m["risk_penalty"] > 0.30:
        reasons.append("risk_too_high")
    return len(reasons) == 0, reasons


def build_comment_seed(promoted: List[Dict], generated_at: str, out_path: Path) -> None:
    lines = [
        "# Memory Mesh Comment Seed",
        "",
        f"- generated_at: {generated_at}",
        "- target_version: 1.0.1",
        "- note: 1.0.0 is local-only. Use this template after ClawHub page URL exists.",
        "",
        "## Comment Template",
        "",
        "New memory batch published by memory-mesh-core:",
        "- batch: memory_mesh_v1",
        "- promoted_count: " + str(len(promoted)),
        "- digest_file: memory/memory_mesh/public_batch_v1.json",
        "- safety: secret and privacy gates passed",
        "- install: clawhub install memory-mesh-core",
        "- star: clawhub star memory-mesh-core --yes",
        "",
        "Top promoted memories:",
    ]
    for item in promoted[:8]:
        lines.append(f"- {item['id']} [{','.join(item.get('tags', []))}]: {item['text'][:120]}")
    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def build_cycle_report(candidates: List[Dict], promoted: List[Dict], generated_at: str, out_path: Path) -> None:
    lines = [
        "# Memory Mesh Cycle Report",
        "",
        f"- generated_at: {generated_at}",
        f"- candidates: {len(candidates)}",
        f"- promoted: {len(promoted)}",
        "",
        "## Top Promoted",
        "",
    ]
    if not promoted:
        lines.append("- (none)")
    else:
        for item in promoted[:12]:
            tags = ",".join(item.get("tags", []))
            lines.append(
                f"- {item['id']} | score={item['value_score']} | "
                f"confidence={item['metrics']['confidence']} | tags={tags} | text={item['text'][:140]}"
            )
    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one memory mesh cycle.")
    parser.add_argument("--workspace", default=".", help="OpenClaw workspace root path")
    parser.add_argument("--top-k", type=int, default=20, help="Max promoted memories per cycle")
    parser.add_argument("--min-score", type=float, default=45.0, help="Promotion score threshold")
    parser.add_argument(
        "--consolidated-json",
        default="",
        help="Optional consolidated memory JSON path (entries[] with text/tags/source_file).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not write files")
    parser.add_argument("--cycle-id", default="", help="Optional cycle identifier")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    output_dir = workspace / "memory" / "memory_mesh"
    state_path = output_dir / "state.json"
    now = datetime.now(timezone.utc)
    now_ts = now.timestamp()
    generated_at = now.isoformat()

    state = read_json(state_path, {"seen_ids": [], "runs": []})
    seen_ids = set(state.get("seen_ids", []))

    dedup = {}
    for source in iter_source_files(workspace):
        raw = read_text(source)
        if not raw:
            continue
        mtime = source.stat().st_mtime
        for c in extract_candidates(source, raw):
            key = c["id"]
            if key in dedup:
                continue
            scored = score_candidate(c, seen_ids, mtime, now_ts)
            dedup[key] = scored

    consolidated_arg = str(args.consolidated_json or "").strip()
    if consolidated_arg:
        consolidated_path = Path(consolidated_arg).expanduser()
        if not consolidated_path.is_absolute():
            consolidated_path = (workspace / consolidated_path).resolve()
        for c in load_consolidated_candidates(consolidated_path):
            key = c["id"]
            if key in dedup:
                continue
            scored = score_candidate(c, seen_ids, now_ts, now_ts)
            dedup[key] = scored

    candidates = sorted(dedup.values(), key=lambda x: x["value_score"], reverse=True)

    promoted: List[Dict] = []
    for item in candidates:
        ok, reasons = is_promotable(item, args.min_score)
        item["promotion_reasons"] = [] if ok else reasons
        if ok:
            promoted.append(item)
        if len(promoted) >= max(1, args.top_k):
            break

    run_record = {
        "generated_at": generated_at,
        "cycle_id": args.cycle_id or None,
        "candidate_count": len(candidates),
        "promoted_count": len(promoted),
        "top_promoted_ids": [p["id"] for p in promoted[:10]],
    }

    next_seen = list(seen_ids.union({c["id"] for c in candidates}))
    next_state = {
        "seen_ids": next_seen[-10000:],
        "runs": (state.get("runs", []) + [run_record])[-200:],
    }

    public_batch = {
        "schema": "memory-mesh-public-batch-v1",
        "generated_at": generated_at,
        "cycle_id": args.cycle_id or None,
        "promoted": promoted,
    }

    summary = {
        "ok": True,
        "generated_at": generated_at,
        "workspace": str(workspace),
        "candidate_count": len(candidates),
        "promoted_count": len(promoted),
        "top_promoted_ids": [p["id"] for p in promoted[:5]],
        "top_promoted_tags": sorted({t for p in promoted for t in p.get("tags", [])})[:10],
    }

    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        write_json(output_dir / "candidates_latest.json", candidates)
        write_json(output_dir / "promoted_latest.json", promoted)
        write_json(output_dir / "public_batch_v1.json", public_batch)
        write_json(output_dir / "last_run.json", summary)
        write_json(state_path, next_state)
        build_cycle_report(candidates, promoted, generated_at, output_dir / "cycle_report.md")
        build_comment_seed(promoted, generated_at, output_dir / "comment_seed.md")

    print(json.dumps(summary))


if __name__ == "__main__":
    main()
