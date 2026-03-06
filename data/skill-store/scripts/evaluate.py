#!/usr/bin/env python3
"""
skill-store evaluate.py — Smart skill installation advisor for ClawHub.

Searches, installs candidates, runs skill-shield security scans,
evaluates code quality, and produces a comparison report.

Usage:
    python3 evaluate.py "search query" [--top 5] [--output-dir DIR]
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Scanner discovery
# ---------------------------------------------------------------------------

def find_scanner(explicit_path: str | None = None) -> Path | None:
    """Locate skill-shield's scan.py."""
    if explicit_path:
        p = Path(explicit_path)
        if p.is_file():
            return p

    # Check env var
    env_path = os.environ.get("SKILL_SHIELD_SCANNER")
    if env_path:
        p = Path(env_path)
        if p.is_file():
            return p

    # Auto-detect: sibling directory pattern
    here = Path(__file__).resolve().parent  # scripts/
    candidates = [
        here.parent.parent.parent / "skill-shield" / "skill" / "scripts" / "scan.py",
        here.parent.parent.parent.parent / "skill-shield" / "skill" / "scripts" / "scan.py",
        Path.home() / ".openclaw" / "workspace" / "skills" / "skill-shield" / "scripts" / "scan.py",
        Path.home() / ".openclaw" / "workspace" / "agents-workspace" / "skill-shield" / "skill" / "scripts" / "scan.py",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


# ---------------------------------------------------------------------------
# ClawHub CLI wrappers
# ---------------------------------------------------------------------------

def clawhub_search(query: str, limit: int = 10) -> list[dict]:
    """Search ClawHub and parse results. Returns list of {slug, version, name, score}."""
    try:
        result = subprocess.run(
            ["clawhub", "search", query, "--limit", str(limit)],
            capture_output=True, text=True, timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"Error: clawhub search failed: {e}", file=sys.stderr)
        return []

    entries = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if line.startswith("- "):
            continue  # progress indicator
        # Format: "slug vX.Y.Z  Name  (score)"
        m = re.match(r'^(\S+)\s+(v[\d.]+)\s+(.+?)\s+\(([\d.]+)\)$', line)
        if m:
            entries.append({
                "slug": m.group(1),
                "version": m.group(2),
                "name": m.group(3).strip(),
                "score": float(m.group(4)),
            })
    return entries


def clawhub_install(slug: str, workdir: str) -> bool:
    """Install a skill into workdir. Returns True on success."""
    try:
        result = subprocess.run(
            ["clawhub", "install", slug, "--force"],
            capture_output=True, text=True, timeout=60,
            cwd=workdir,
            env={**os.environ, "CLAWHUB_WORKDIR": workdir},
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"Error installing {slug}: {e}", file=sys.stderr)
        return False


def clawhub_uninstall(slug: str, workdir: str) -> bool:
    """Uninstall a skill by removing its directory."""
    skill_dir = Path(workdir) / "skills" / slug
    if skill_dir.is_dir():
        shutil.rmtree(skill_dir, ignore_errors=True)
        return True
    return False


# ---------------------------------------------------------------------------
# Security scan via skill-shield
# ---------------------------------------------------------------------------

def run_security_scan(skill_dir: Path, scanner_path: Path) -> dict | None:
    """Run skill-shield scan.py on a skill directory. Returns parsed JSON report or None."""
    try:
        result = subprocess.run(
            [sys.executable, str(scanner_path), str(skill_dir)],
            capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        return None

    # Extract JSON from output
    output = result.stdout
    json_start = output.find("--- JSON START ---")
    json_end = output.find("--- JSON END ---")
    if json_start == -1 or json_end == -1:
        return None

    json_str = output[json_start + len("--- JSON START ---"):json_end].strip()
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------------------
# Code quality evaluation
# ---------------------------------------------------------------------------

def evaluate_quality(skill_dir: Path) -> dict:
    """Evaluate code quality of a skill directory."""
    skill_md = skill_dir / "SKILL.md"
    readme = None
    for name in ("README.md", "readme.md", "README"):
        if (skill_dir / name).exists():
            readme = skill_dir / name
            break

    # Count code files and lines
    code_exts = {".py", ".js", ".ts", ".sh", ".bash", ".mjs", ".cjs"}
    code_files = []
    total_lines = 0
    total_code_lines = 0  # non-empty, non-comment

    for f in skill_dir.rglob("*"):
        if f.is_file() and f.suffix in code_exts:
            code_files.append(f)
            try:
                lines = f.read_text(errors="replace").splitlines()
                total_lines += len(lines)
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#") and not stripped.startswith("//"):
                        total_code_lines += 1
            except Exception:
                pass

    # SKILL.md completeness
    skill_md_lines = 0
    skill_md_status = "missing"
    if skill_md.exists():
        skill_md_lines = len(skill_md.read_text(errors="replace").splitlines())
        if skill_md_lines >= 50:
            skill_md_status = "complete"
        elif skill_md_lines >= 20:
            skill_md_status = "basic"
        else:
            skill_md_status = "minimal"

    # Test files
    test_patterns = ["test_", "_test.", ".test.", "spec.", "_spec."]
    test_files = [f for f in skill_dir.rglob("*") if f.is_file()
                  and any(p in f.name.lower() for p in test_patterns)]

    # All files for total size
    all_files = list(skill_dir.rglob("*"))
    file_count = sum(1 for f in all_files if f.is_file())

    # Quality score (0-100)
    score = 0

    # Code substance (0-30): having actual code is good, but too much is suspicious
    if total_code_lines == 0:
        score += 5  # empty shell
    elif total_code_lines <= 50:
        score += 15
    elif total_code_lines <= 300:
        score += 30
    elif total_code_lines <= 800:
        score += 25
    else:
        score += 20  # very large, harder to audit

    # Documentation (0-35)
    doc_score = 0
    if skill_md_status == "complete":
        doc_score += 25
    elif skill_md_status == "basic":
        doc_score += 15
    elif skill_md_status == "minimal":
        doc_score += 5
    if readme:
        doc_score += 10
    score += doc_score

    # Tests (0-20)
    if test_files:
        score += 20
    elif total_code_lines > 100:
        score += 0  # should have tests for substantial code
    else:
        score += 10  # small code, tests less critical

    # Structure (0-15): having a scripts/ dir, proper layout
    has_scripts_dir = (skill_dir / "scripts").is_dir()
    score += 10 if has_scripts_dir else 5
    score += 5 if len(code_files) >= 1 else 0

    return {
        "total_lines": total_lines,
        "code_lines": total_code_lines,
        "code_files": len(code_files),
        "file_count": file_count,
        "skill_md_lines": skill_md_lines,
        "skill_md_status": skill_md_status,
        "has_readme": readme is not None,
        "test_files": len(test_files),
        "has_tests": len(test_files) > 0,
        "quality_score": min(100, score),
    }


# ---------------------------------------------------------------------------
# Scoring and ranking
# ---------------------------------------------------------------------------

RATING_SCORES = {"A": 100, "B": 80, "C": 50, "D": 20, "F": 0}


def compute_final_score(security_report: dict | None, quality: dict, search_score: float,
                        max_search_score: float) -> dict:
    """Compute weighted final score."""
    # Security (40%)
    if security_report:
        rating = security_report.get("security_rating", security_report.get("rating", "F"))
        if rating == "N/A":
            rating = "A"  # doc-only skills are safe but low quality
        sec_base = RATING_SCORES.get(rating, 0)
        findings_count = security_report.get("summary", {}).get("total_findings", 0)
        # Penalize for many findings even within same rating
        sec_penalty = min(20, findings_count * 0.5)
        security_score = max(0, sec_base - sec_penalty)
    else:
        security_score = 0
        rating = "?"

    # Quality (30%)
    quality_score = quality.get("quality_score", 0)

    # Relevance (30%)
    if max_search_score > 0:
        relevance_score = (search_score / max_search_score) * 100
    else:
        relevance_score = 50

    # Weighted total
    total = security_score * 0.4 + quality_score * 0.3 + relevance_score * 0.3

    # Extract compliance and recommendation from report
    comp_rating = "?"
    recommendation = "?"
    rec_reason = ""
    is_doc_only = False
    if security_report:
        comp_rating = security_report.get("compliance_rating", "?")
        recommendation = security_report.get("recommendation", "?")
        rec_reason = security_report.get("recommendation_reason", "")
        is_doc_only = security_report.get("is_documentation_only", False)

    return {
        "total": round(total, 1),
        "security_score": round(security_score, 1),
        "quality_score": round(quality_score, 1),
        "relevance_score": round(relevance_score, 1),
        "security_rating": rating,
        "compliance_rating": comp_rating,
        "recommendation": recommendation,
        "recommendation_reason": rec_reason,
        "is_doc_only": is_doc_only,
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def build_md_report(query: str, evaluations: list[dict], recommended: dict | None) -> str:
    """Build markdown comparison report."""
    lines = []
    lines.append(f"# 🏪 Skill Store 推荐报告: \"{query}\"")
    lines.append("")
    lines.append(f"**搜索时间:** {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"**候选数量:** {len(evaluations)}")
    if recommended:
        lines.append(f"**🏆 推荐:** {recommended['slug']} {recommended['version']}")
    else:
        lines.append("**推荐:** 无合适候选")
    lines.append("")

    if not evaluations:
        lines.append("未找到匹配的 skill。")
        return "\n".join(lines)

    # Comparison table
    lines.append("## 对比表")
    lines.append("")

    # Header
    slugs = [e["slug"] for e in evaluations]
    header = "| 维度 | " + " | ".join(slugs) + " |"
    sep = "|------|" + "|".join(["------"] * len(slugs)) + "|"
    lines.append(header)
    lines.append(sep)

    # Rows
    emoji_map = {"A": "🟢", "B": "🔵", "C": "🟡", "D": "🟠", "F": "🔴", "?": "⚪"}

    def _row(label, getter):
        vals = [str(getter(e)) for e in evaluations]
        return f"| {label} | " + " | ".join(vals) + " |"

    emoji_map["N/A"] = "⚪"
    lines.append(_row("安全评级", lambda e: f"{emoji_map.get(e['scores']['security_rating'], '⚪')} {e['scores']['security_rating']}"))
    lines.append(_row("合规评级", lambda e: f"{emoji_map.get(e['scores'].get('compliance_rating', '?'), '⚪')} {e['scores'].get('compliance_rating', '?')}"))
    lines.append(_row("建议", lambda e: {"install": "✅ 安装", "install_with_review": "⚠️ 审查后装", "review_required": "🔍 需审查", "do_not_install": "❌ 不推荐", "documentation_only": "📄 纯文档"}.get(e["scores"].get("recommendation", "?"), "?")))
    lines.append(_row("综合评分", lambda e: f"**{e['scores']['total']}**"))
    lines.append(_row("安全分", lambda e: e["scores"]["security_score"]))
    lines.append(_row("质量分", lambda e: e["scores"]["quality_score"]))
    lines.append(_row("相关度分", lambda e: e["scores"]["relevance_score"]))
    lines.append(_row("代码行数", lambda e: e["quality"]["code_lines"]))
    lines.append(_row("文档完整度", lambda e: {"complete": "✅ 完整", "basic": "⚠️ 基本", "minimal": "📄 简陋", "missing": "❌ 缺失"}.get(e["quality"]["skill_md_status"], "?")))
    lines.append(_row("有测试", lambda e: "✅" if e["quality"]["has_tests"] else "❌"))
    lines.append(_row("有 README", lambda e: "✅" if e["quality"]["has_readme"] else "❌"))

    # Permission audit row
    def _perm_coverage(e):
        sr = e.get("security_report")
        if not sr:
            return "N/A"
        perm = sr.get("permissions", {})
        return perm.get("declaration_coverage", "N/A")

    lines.append(_row("权限声明覆盖", _perm_coverage))

    # Findings count
    def _findings(e):
        sr = e.get("security_report")
        if not sr:
            return "N/A"
        return sr.get("summary", {}).get("total_findings", 0)

    lines.append(_row("安全发现数", _findings))
    lines.append("")

    # Recommendation
    if recommended:
        lines.append("## 🏆 推荐理由")
        lines.append("")
        rec_eval = next((e for e in evaluations if e["slug"] == recommended["slug"]), None)
        if rec_eval:
            lines.append(f"**{rec_eval['slug']}** ({rec_eval['version']}) 综合评分最高 ({rec_eval['scores']['total']})：")
            lines.append("")
            rating = rec_eval["scores"]["security_rating"]
            if rating in ("A", "B"):
                lines.append(f"- 安全评级 {emoji_map.get(rating, '')} {rating}，可放心安装")
            else:
                lines.append(f"- 安全评级 {emoji_map.get(rating, '')} {rating}，建议安装前审查")
            lines.append(f"- 代码质量分 {rec_eval['scores']['quality_score']}/100")
            lines.append(f"- 搜索相关度分 {rec_eval['scores']['relevance_score']}/100")
        lines.append("")

    # Per-candidate details
    lines.append("## 各候选详情")
    lines.append("")
    for e in evaluations:
        status = "🏆 推荐" if recommended and e["slug"] == recommended["slug"] else ""
        lines.append(f"### {e['slug']} {e['version']} {status}")
        lines.append("")
        lines.append(f"- **搜索名称:** {e['name']}")
        lines.append(f"- **搜索相关度:** {e['search_score']}")
        sec_r = e['scores']['security_rating']
        comp_r = e['scores'].get('compliance_rating', '?')
        lines.append(f"- **安全评级:** {emoji_map.get(sec_r, '⚪')} {sec_r}")
        lines.append(f"- **合规评级:** {emoji_map.get(comp_r, '⚪')} {comp_r}")
        rec = e['scores'].get('recommendation', '?')
        rec_reason = e['scores'].get('recommendation_reason', '')
        if rec_reason:
            lines.append(f"- **建议:** {rec} — {rec_reason}")
        lines.append(f"- **代码行数:** {e['quality']['code_lines']} (总 {e['quality']['total_lines']})")
        lines.append(f"- **代码文件数:** {e['quality']['code_files']}")
        lines.append(f"- **SKILL.md:** {e['quality']['skill_md_status']} ({e['quality']['skill_md_lines']} 行)")
        lines.append(f"- **测试文件:** {e['quality']['test_files']} 个")

        sr = e.get("security_report")
        if sr:
            perm = sr.get("permissions", {})
            undecl = perm.get("undeclared", [])
            if undecl:
                lines.append(f"- **⚠️ 未声明权限:** {', '.join(undecl)}")
            findings = sr.get("summary", {}).get("total_findings", 0)
            if findings > 0:
                cats = sr.get("summary", {}).get("by_category", {})
                cat_str = ", ".join(f"{k}: {v}" for k, v in sorted(cats.items()))
                lines.append(f"- **安全发现:** {findings} ({cat_str})")

        if e.get("error"):
            lines.append(f"- **⚠️ 评估错误:** {e['error']}")
        lines.append("")

    return "\n".join(lines)


def build_json_report(query: str, evaluations: list[dict], recommended: dict | None) -> dict:
    """Build JSON report."""
    return {
        "skill_store_version": "1.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "candidates_evaluated": len(evaluations),
        "recommended": recommended,
        "evaluations": evaluations,
    }


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Skill Store — smart skill installation advisor")
    parser.add_argument("query", help="Search query describing what you need")
    parser.add_argument("--top", type=int, default=5, help="Number of candidates to evaluate (default: 5)")
    parser.add_argument("--output-dir", "-o", help="Directory to write report.md and report.json")
    parser.add_argument("--workdir", help="Working directory for clawhub install (default: temp dir)")
    parser.add_argument("--scanner", help="Path to skill-shield's scan.py")
    parser.add_argument("--keep-all", action="store_true", help="Don't uninstall non-recommended candidates")
    args = parser.parse_args()

    # Find scanner
    scanner = find_scanner(args.scanner)
    if not scanner:
        print("Error: Cannot find skill-shield scan.py. Use --scanner to specify path.", file=sys.stderr)
        print("Looked in: SKILL_SHIELD_SCANNER env, sibling dirs, ~/.openclaw/workspace/", file=sys.stderr)
        sys.exit(1)
    print(f"Scanner: {scanner}", file=sys.stderr)

    # Setup workdir
    if args.workdir:
        workdir = args.workdir
        os.makedirs(workdir, exist_ok=True)
    else:
        workdir = tempfile.mkdtemp(prefix="skill-store-eval-")
    print(f"Workdir: {workdir}", file=sys.stderr)

    # Ensure skills subdir exists (clawhub installs into <workdir>/skills/<slug>)
    skills_dir = Path(workdir) / "skills"
    skills_dir.mkdir(exist_ok=True)

    # Step 1: Search
    print(f"Searching ClawHub for: \"{args.query}\"...", file=sys.stderr)
    results = clawhub_search(args.query, limit=args.top * 2)  # fetch extra in case some fail
    if not results:
        print("No results found.", file=sys.stderr)
        sys.exit(1)

    candidates = results[:args.top]
    max_score = max(c["score"] for c in candidates) if candidates else 1.0
    print(f"Found {len(results)} results, evaluating top {len(candidates)}", file=sys.stderr)

    # Step 2-4: Install, scan, evaluate each candidate
    evaluations = []
    for i, cand in enumerate(candidates, 1):
        slug = cand["slug"]
        print(f"[{i}/{len(candidates)}] Evaluating {slug}...", file=sys.stderr)

        eval_entry = {
            "slug": slug,
            "version": cand["version"],
            "name": cand["name"],
            "search_score": cand["score"],
            "error": None,
            "security_report": None,
            "quality": None,
            "scores": None,
        }

        # Install
        print(f"  Installing...", file=sys.stderr)
        if not clawhub_install(slug, workdir):
            eval_entry["error"] = "Installation failed"
            eval_entry["quality"] = {"total_lines": 0, "code_lines": 0, "code_files": 0,
                                     "file_count": 0, "skill_md_lines": 0, "skill_md_status": "missing",
                                     "has_readme": False, "test_files": 0, "has_tests": False, "quality_score": 0}
            eval_entry["scores"] = {"total": 0, "security_score": 0, "quality_score": 0,
                                    "relevance_score": 0, "security_rating": "?"}
            evaluations.append(eval_entry)
            continue

        skill_dir = skills_dir / slug

        # Security scan
        print(f"  Security scan...", file=sys.stderr)
        sec_report = run_security_scan(skill_dir, scanner)
        eval_entry["security_report"] = sec_report

        # Quality evaluation
        print(f"  Quality evaluation...", file=sys.stderr)
        quality = evaluate_quality(skill_dir)
        eval_entry["quality"] = quality

        # Scoring
        scores = compute_final_score(sec_report, quality, cand["score"], max_score)
        eval_entry["scores"] = scores

        evaluations.append(eval_entry)

    # Step 5: Rank and recommend
    valid = [e for e in evaluations if e["scores"] and e["scores"]["total"] > 0]
    valid.sort(key=lambda e: e["scores"]["total"], reverse=True)

    recommended = None
    if valid:
        best = valid[0]
        recommended = {"slug": best["slug"], "version": best["version"], "score": best["scores"]["total"]}

    # Step 6: Generate reports
    # Sort evaluations by score for display
    evaluations.sort(key=lambda e: (e["scores"]["total"] if e["scores"] else 0), reverse=True)

    md_report = build_md_report(args.query, evaluations, recommended)
    json_report = build_json_report(args.query, evaluations, recommended)

    print(md_report)

    if args.output_dir:
        out = Path(args.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "report.md").write_text(md_report)
        (out / "report.json").write_text(json.dumps(json_report, indent=2, ensure_ascii=False))
        print(f"\nReports written to {out}/", file=sys.stderr)

    # Step 7: Cleanup non-recommended
    if not args.keep_all and recommended:
        for e in evaluations:
            if e["slug"] != recommended["slug"] and not e.get("error"):
                print(f"  Removing {e['slug']}...", file=sys.stderr)
                clawhub_uninstall(e["slug"], workdir)

    # Summary
    print(f"\n{'='*50}", file=sys.stderr)
    if recommended:
        print(f"Recommended: {recommended['slug']} (score: {recommended['score']})", file=sys.stderr)
        print(f"Installed at: {skills_dir / recommended['slug']}", file=sys.stderr)
    else:
        print("No recommendation — all candidates failed evaluation.", file=sys.stderr)
    print(f"{'='*50}", file=sys.stderr)

    sys.exit(0 if recommended else 1)


if __name__ == "__main__":
    main()
