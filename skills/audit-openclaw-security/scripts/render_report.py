#!/usr/bin/env python3
"""Render a Markdown report from collected OpenClaw audit artefacts.

This renderer is intentionally schema-tolerant:
- It attempts to parse `openclaw security audit --json` output (and --deep).
- It groups and sorts findings by severity.
- It enriches findings with a small built-in checkId map (if present) to suggest
  likely config keys / remediation areas.

Usage:
  # If --input points to a parent folder, we'll pick the newest openclaw-audit-* subfolder.
  python3 scripts/render_report.py --input ./openclaw-audit --output ./openclaw-security-report.md

  # Or pass a specific timestamped folder.
  python3 scripts/render_report.py --input ./openclaw-audit/openclaw-audit-<ts> --output ./openclaw-security-report.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4, "unknown": 9}


def load_json_text(txt: str) -> Any:
    """Extract JSON from a CLI-captured text file that starts with '$ cmd' line."""
    idx = txt.find("{")
    if idx == -1:
        idx = txt.find("[")
    if idx == -1:
        return None
    try:
        return json.loads(txt[idx:])
    except Exception:
        return None


def load_json_file(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def newest_audit_folder(root: Path) -> Path:
    """If root contains openclaw-audit-* folders, pick the newest by name."""
    if root.is_dir():
        kids = [p for p in root.iterdir() if p.is_dir() and p.name.startswith("openclaw-audit-")]
        if kids:
            return sorted(kids, key=lambda p: p.name)[-1]
    return root


def normalise_sev(raw: str) -> str:
    s = (raw or "").strip().lower()
    if not s:
        return "unknown"

    # Some outputs may have combined severities like "warn/critical".
    if "/" in s:
        parts = [p.strip() for p in s.split("/") if p.strip()]
        if "critical" in parts:
            return "critical"
        if "high" in parts:
            return "high"
        if "warn" in parts or "warning" in parts or "medium" in parts:
            return "medium"
        if "low" in parts:
            return "low"
        if "info" in parts:
            return "info"
        return parts[0] if parts else "unknown"

    if s in ("warn", "warning"):
        return "medium"
    if s == "crit":
        return "critical"
    if s not in SEV_ORDER:
        # Preserve unknown labels but bucket them at end.
        return s
    return s


def extract_findings(obj: Any) -> List[Dict[str, Any]]:
    """Try a few likely shapes to get a list of finding dicts."""
    if obj is None:
        return []
    if isinstance(obj, dict):
        for key in ("findings", "checks", "results", "issues"):
            v = obj.get(key)
            if isinstance(v, list):
                return [x for x in v if isinstance(x, dict)]
        # Some formats may be a dict of checkId -> detail
        if obj and all(isinstance(v, dict) for v in obj.values()):
            out: List[Dict[str, Any]] = []
            for k, v in obj.items():
                vv = dict(v)
                vv.setdefault("checkId", k)
                out.append(vv)
            return out
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    return []


def pick_text(f: Dict[str, Any]) -> str:
    for k in ("title", "summary", "message", "description"):
        v = f.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return "(no summary provided)"


def sort_key(f: Dict[str, Any]) -> Tuple[int, str]:
    sev = normalise_sev(str(f.get("severity") or f.get("level") or f.get("risk") or "unknown"))
    # Unknown severities go to the end.
    order = SEV_ORDER.get(sev, 8)
    return (order, str(f.get("checkId") or f.get("id") or ""))


def severity_counts(findings: List[Dict[str, Any]]) -> Dict[str, int]:
    c: Dict[str, int] = {}
    for f in findings:
        sev = normalise_sev(str(f.get("severity") or f.get("level") or f.get("risk") or "unknown"))
        c[sev] = c.get(sev, 0) + 1
    return c


def load_checkid_map(skill_root: Path) -> Dict[str, Any]:
    """Load optional checkId enrichment map."""
    cand = skill_root / "assets" / "openclaw_checkid_map.json"
    if cand.exists():
        obj = load_json_file(cand)
        if isinstance(obj, dict):
            return obj
    return {}


def read_last_nonempty_line(path: Path) -> str:
    if not path.exists():
        return "(unknown)"
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip()]
    return lines[-1] if lines else "(unknown)"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Folder produced by collect_openclaw_audit.sh (or its parent)")
    ap.add_argument("--output", required=True, help="Markdown report path")
    args = ap.parse_args()

    in_path = Path(args.input)
    in_dir = newest_audit_folder(in_path)
    out_path = Path(args.output)

    if not in_dir.exists() or not in_dir.is_dir():
        raise SystemExit(f"Input directory not found: {in_dir}")

    # Locate OpenClaw JSON audit output files
    audit_candidates = [
        in_dir / "openclaw_security_audit_deep_json.txt",
        in_dir / "openclaw_security_audit_json.txt",
    ]

    audit_obj: Any = None
    used_file: Optional[Path] = None
    for p in audit_candidates:
        if p.exists():
            txt = p.read_text(encoding="utf-8", errors="replace")
            audit_obj = load_json_text(txt)
            used_file = p
            if audit_obj is not None:
                break

    findings = extract_findings(audit_obj)
    findings_sorted = sorted(findings, key=sort_key)

    # Load enrichment map from the skill folder
    # Expect script location: <skill>/scripts/render_report.py
    skill_root = Path(__file__).resolve().parents[1]
    check_map = load_checkid_map(skill_root)

    version = read_last_nonempty_line(in_dir / "openclaw_version.txt")

    counts = severity_counts(findings_sorted)

    report: List[str] = []
    report.append("# OpenClaw Security Audit Report\n\n")

    report.append("## Executive summary\n\n")
    report.append(f"- **OpenClaw version:** {version}\n")
    report.append(f"- **Audit artefacts folder:** `{in_dir}`\n")
    if used_file is not None:
        report.append(f"- **Parsed audit file:** `{used_file.name}`\n")
    report.append("- **Overall risk rating:** (fill in)\n")
    report.append("- **Most urgent issues:** (fill in)\n\n")

    report.append("## Finding counts\n\n")
    if counts:
        # keep stable order
        for sev in ("critical", "high", "medium", "low", "info", "unknown"):
            if sev in counts:
                report.append(f"- **{sev}:** {counts[sev]}\n")
        report.append("\n")
    else:
        report.append("No findings were parsed. Review the raw audit output manually.\n\n")

    report.append("## Findings (from `openclaw security audit --json`)\n\n")

    if not findings_sorted:
        report.append(
            "No findings were parsed from the JSON output. Attach the raw audit files and review manually:\n\n"
        )
        report.append(f"- `{in_dir / 'openclaw_security_audit_json.txt'}`\n")
        report.append(f"- `{in_dir / 'openclaw_security_audit_deep_json.txt'}`\n\n")
    else:
        report.append(
            "| Severity | Check ID | Summary | Likely fix area | Auto-fix | Recommended fix (fill in) | Verify (fill in) |\n"
        )
        report.append("|---|---|---|---|---:|---|---|\n")

        for f in findings_sorted[:400]:
            sev = normalise_sev(str(f.get("severity") or f.get("level") or f.get("risk") or "unknown"))
            check_id = str(f.get("checkId") or f.get("id") or "").strip() or "(unknown)"
            summary = pick_text(f).replace("\n", " ").replace("|", "\\|")

            # Enrichment
            enrich = check_map.get(check_id, {}) if isinstance(check_map, dict) else {}
            likely_fix = ""
            auto_fix: Optional[bool] = None

            if isinstance(enrich, dict):
                likely_fix = str(enrich.get("primary_fix") or "")
                af = enrich.get("auto_fix")
                if isinstance(af, bool):
                    auto_fix = af

            # If the finding itself includes a fix path, prefer it
            for k in ("primaryFix", "fix", "path", "configPath"):
                v = f.get(k)
                if isinstance(v, str) and v.strip():
                    likely_fix = v.strip()
                    break
                if isinstance(v, dict):
                    # common shapes: { path: "gateway.bind", ... }
                    pv = v.get("path") if isinstance(v.get("path"), str) else None
                    if pv:
                        likely_fix = pv
                        break

            auto_fix_s = ""
            if isinstance(f.get("autoFix"), bool):
                auto_fix_s = "yes" if f.get("autoFix") else "no"
            elif auto_fix is not None:
                auto_fix_s = "yes" if auto_fix else "no"

            report.append(
                f"| {sev} | {check_id} | {summary} | {likely_fix.replace('|','\\|')} | {auto_fix_s} |  |  |\n"
            )

        report.append("\n")

    report.append("## Remediation plan\n\n")
    report.append("### Phase 1 — Critical fixes (same day)\n\n1. \n\n")
    report.append("### Phase 2 — Hardening (this week)\n\n1. \n\n")
    report.append("### Phase 3 — Operational practices (ongoing)\n\n")
    report.append("- Update cadence (OS, OpenClaw, Node/runtime where relevant)\n")
    report.append("- Token/password rotation policy\n")
    report.append("- Log/transcript retention + pruning\n\n")

    report.append("## Appendix\n\n")
    report.append("- Collected artefacts live in the input folder.\n")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(report), encoding="utf-8")


if __name__ == "__main__":
    main()
