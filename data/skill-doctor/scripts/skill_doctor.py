#!/usr/bin/env python3
"""
Skill Doctor — Scan skills folder for dependency issues and test skills in/out of sandbox.

- Scans workspace/skills for Python skills
- Detects missing dependencies (imported but not in requirements.txt)
- Detects unused dependencies (in requirements.txt but not imported)
- Can fix: add missing, remove unused
- Can test a skill: run skill-tester with optional sandbox (default) or no-sandbox
"""

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# Import name (top-level) -> pip package name (many are 1:1)
IMPORT_TO_PIP = {
    "yaml": "PyYAML",
    "YAML": "PyYAML",
    "cv2": "opencv-python",
    "bs4": "beautifulsoup4",
    "dotenv": "python-dotenv",
    "dateutil": "python-dateutil",
    "sklearn": "scikit-learn",
    "PIL": "Pillow",
    "Crypto": "pycryptodome",
    "OpenSSL": "pyOpenSSL",
    "dns": "dnspython",
    "requests": "requests",
    "flask": "Flask",
    "flask_cors": "flask-cors",
    "CORS": "flask-cors",
    "sqlalchemy": "SQLAlchemy",
    "pandas": "pandas",
    "numpy": "numpy",
    "openclaw": "openclaw",  # local/openclaw
}
# Stdlib modules we never add to requirements
STDLIB = frozenset(
    [
        "argparse", "ast", "base64", "collections", "configparser", "copy", "csv",
        "dataclasses", "datetime", "email", "encodings", "enum", "fnmatch", "functools", "gc",
        "glob", "gzip", "hashlib", "html", "http", "importlib", "io", "itertools",
        "json", "logging", "math", "mimetypes", "numbers", "operator", "os", "pathlib",
        "pickle", "platform", "re", "shutil", "signal", "socket", "sqlite3",
        "string", "struct", "subprocess", "sys", "tempfile", "textwrap", "threading",
        "time", "traceback", "typing", "unittest", "urllib", "uuid", "warnings",
        "weakref", "xml", "zipfile", "_thread",
    ]
)


def _openclaw_home() -> Path:
    return Path(os.environ.get("OPENCLAW_HOME", os.path.expanduser("~/.openclaw")))


def _skills_dir() -> Path:
    return _openclaw_home() / "workspace" / "skills"


def _skill_tester_script() -> Path:
    return _openclaw_home() / "workspace" / "skills" / "skill-tester" / "scripts" / "skill_tester.py"


def _discover_skills(skills_root: Path) -> List[str]:
    """Return skill slugs that have SKILL.md or _meta.json."""
    if not skills_root.exists():
        return []
    out = []
    for p in sorted(skills_root.iterdir()):
        if not p.is_dir() or p.name.startswith("."):
            continue
        if (p / "SKILL.md").exists() or (p / "_meta.json").exists():
            out.append(p.name)
    return out


def _extract_imports_from_py(path: Path) -> Set[str]:
    """Extract top-level import names from a Python file (no stdlib)."""
    names = set()
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text)
    except (SyntaxError, OSError):
        return names
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top not in STDLIB:
                    names.add(top)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                top = node.module.split(".")[0]
                if top not in STDLIB:
                    names.add(top)
    return names


def _local_module_names(skill_dir: Path) -> Set[str]:
    """Names of .py files in the skill (without extension) as top-level module names."""
    local = set()
    for folder in [skill_dir, skill_dir / "scripts"]:
        if not folder.exists():
            continue
        for py in folder.glob("*.py"):
            if "venv" in py.parts or "site-packages" in py.parts:
                continue
            local.add(py.stem)
    return local


def _all_py_imports(skill_dir: Path) -> Set[str]:
    """Collect all third-party import names from skill's scripts (and root .py)."""
    all_imports = set()
    local = _local_module_names(skill_dir)
    scripts = skill_dir / "scripts"
    for folder in [skill_dir, scripts] if scripts.exists() else [skill_dir]:
        for py in folder.glob("*.py"):
            if "venv" in py.parts or "site-packages" in py.parts:
                continue
            all_imports |= _extract_imports_from_py(py)
    # Exclude local modules (same skill)
    return all_imports - local


def _import_to_pip(name: str) -> str:
    """Map import name to pip package name."""
    return IMPORT_TO_PIP.get(name, name.replace("_", "-"))


def _parse_requirements(req_path: Path) -> List[Tuple[str, Optional[str]]]:
    """Parse requirements.txt; return list of (package_name, spec or None)."""
    if not req_path.exists():
        return []
    out = []
    for line in req_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        # Match: package, package==x, package>=x, package[x]
        m = re.match(r"([a-zA-Z0-9_-]+)\s*([^\s#]*)", line)
        if m:
            pkg, spec = m.group(1), m.group(2).strip() or None
            if spec and not re.match(r"([=<>!~]=?|\[)", spec):
                spec = None
            out.append((pkg, spec))
    return out


def _normalize_pip_name(name: str) -> str:
    """Normalize for comparison (e.g. flask_cors -> flask-cors)."""
    n = name.lower().replace("_", "-")
    # Map known aliases
    for k, v in IMPORT_TO_PIP.items():
        if v.lower() == n or k.replace("_", "-").lower() == n:
            return v
    return n


def _scan_skill(skill_dir: Path) -> Dict[str, Any]:
    """Scan one skill: imports vs requirements. Return report dict."""
    req_path = skill_dir / "requirements.txt"
    required_packages = {_normalize_pip_name(p): (p, spec) for p, spec in _parse_requirements(req_path)}
    imported = _all_py_imports(skill_dir)
    needed_pip = {_normalize_pip_name(_import_to_pip(i)): _import_to_pip(i) for i in imported}

    missing = []
    for norm, pip_name in needed_pip.items():
        if norm not in required_packages:
            missing.append(pip_name)

    unused = []
    for norm, (orig, _) in required_packages.items():
        # Check if any import maps to this package
        if norm not in needed_pip and norm not in {_normalize_pip_name(i) for i in imported}:
            unused.append(orig)

    return {
        "skill_dir": str(skill_dir),
        "requirements_path": str(req_path),
        "has_requirements": req_path.exists(),
        "imported_top_level": sorted(imported),
        "required_packages": list(required_packages.keys()),
        "missing": missing,
        "unused": unused,
    }


def _fix_skill(skill_dir: Path, add_missing: bool, remove_unused: bool, dry_run: bool) -> List[str]:
    """Add missing deps and/or remove unused from requirements.txt. Return list of actions."""
    report = _scan_skill(skill_dir)
    actions = []
    req_path = skill_dir / "requirements.txt"

    if add_missing and report["missing"]:
        if dry_run:
            actions.append(f"[dry-run] would add: {', '.join(report['missing'])}")
        else:
            lines = req_path.read_text(encoding="utf-8").splitlines() if req_path.exists() else []
            # Remove comment-only and empty at end
            while lines and (not lines[-1].strip() or lines[-1].strip().startswith("#")):
                lines.pop()
            for pkg in sorted(report["missing"]):
                lines.append(pkg)
                actions.append(f"Added: {pkg}")
            req_path.parent.mkdir(parents=True, exist_ok=True)
            req_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if remove_unused and report["unused"]:
        if not req_path.exists():
            return actions
        if dry_run:
            actions.append(f"[dry-run] would remove: {', '.join(report['unused'])}")
        else:
            lines = req_path.read_text(encoding="utf-8").splitlines()
            kept = []
            removed = set(p.lower() for p in report["unused"])
            for line in lines:
                strip = line.strip()
                if not strip or strip.startswith("#"):
                    kept.append(line)
                    continue
                m = re.match(r"([a-zA-Z0-9_-]+)", strip)
                if m and m.group(1).lower() in removed:
                    actions.append(f"Removed: {m.group(1)}")
                    continue
                kept.append(line)
            req_path.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")

    return actions


def _run_skill_tests(skill_slug: str, no_sandbox: bool, timeout: int) -> Tuple[int, str, str]:
    """Run skill-tester for one skill. Return (exit_code, stdout, stderr)."""
    tester = _skill_tester_script()
    skills_root = _skills_dir()
    if not tester.exists():
        return -1, "", "skill_tester.py not found"
    env = os.environ.copy()
    env["OPENCLAW_HOME"] = str(_openclaw_home())
    if no_sandbox:
        env["OPENCLAW_DOCTOR_NO_SANDBOX"] = "1"
    cmd = [sys.executable, str(tester), "--skill", skill_slug, "--json"]
    try:
        r = subprocess.run(
            cmd,
            cwd=str(skills_root),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except FileNotFoundError:
        return -1, "", "command not found"


def main():
    ap = argparse.ArgumentParser(
        description="Skill Doctor: scan skills for dependencies, fix, and test in/out sandbox"
    )
    ap.add_argument("--skills-dir", type=Path, default=None, help="Skills root (default: workspace/skills)")
    ap.add_argument("--skill", type=str, help="Operate on this skill only (slug)")
    ap.add_argument("--scan", action="store_true", help="Scan and report dependency issues")
    ap.add_argument("--fix", action="store_true", help="Fix: add missing deps, remove unused (use with --fix-unused to also remove)")
    ap.add_argument("--fix-unused", action="store_true", help="When fixing, also remove unused packages")
    ap.add_argument("--dry-run", action="store_true", help="With --fix: only report what would be done")
    ap.add_argument("--test", action="store_true", help="Run skill-tester for the skill")
    ap.add_argument("--no-sandbox", action="store_true", help="Run tests with full env (no sandbox)")
    ap.add_argument("--timeout", type=int, default=60, help="Test timeout seconds (default 60)")
    ap.add_argument("--json", action="store_true", help="Output JSON")
    args = ap.parse_args()

    skills_root = args.skills_dir or _skills_dir()
    if not skills_root.exists():
        print("Skills dir not found:", skills_root, file=sys.stderr)
        sys.exit(2)

    discovered = _discover_skills(skills_root)
    slugs = [args.skill] if args.skill else discovered
    if args.skill and args.skill not in discovered:
        print("Skill not found:", args.skill, file=sys.stderr)
        sys.exit(2)

    if args.scan or (not args.fix and not args.test):
        # Default: scan if nothing else requested
        if not args.fix and not args.test:
            args.scan = True
        reports = []
        for slug in slugs:
            skill_dir = skills_root / slug
            r = _scan_skill(skill_dir)
            r["slug"] = slug
            reports.append(r)
            if args.json:
                continue
            print(f"\n[{slug}]")
            print(f"  requirements: {r['requirements_path']} (exists: {r['has_requirements']})")
            print(f"  imported (top-level): {r['imported_top_level']}")
            if r["missing"]:
                print(f"  missing (add to requirements): {r['missing']}")
            if r["unused"]:
                print(f"  unused (in requirements): {r['unused']}")
            if not r["missing"] and not r["unused"] and r["imported_top_level"]:
                print("  deps: ok")

        if args.json and args.scan:
            print(json.dumps({"skills": reports}, indent=2))
            sys.exit(0)

    if args.fix:
        all_actions = []
        for slug in slugs:
            skill_dir = skills_root / slug
            actions = _fix_skill(skill_dir, add_missing=True, remove_unused=args.fix_unused, dry_run=args.dry_run)
            all_actions.extend([(slug, a) for a in actions])
            if not args.json:
                for a in actions:
                    print(f"[{slug}] {a}")
        if args.json:
            print(json.dumps({"fix_actions": [{"skill": s, "action": a} for s, a in all_actions]}))
        sys.exit(0)

    if args.test:
        results = []
        for slug in slugs:
            code, out, err = _run_skill_tests(slug, no_sandbox=args.no_sandbox, timeout=args.timeout)
            results.append({
                "skill": slug,
                "sandbox": not args.no_sandbox,
                "exit_code": code,
                "stdout": out,
                "stderr": err,
                "passed": code == 0,
            })
            if args.json:
                continue
            mode = "no-sandbox" if args.no_sandbox else "sandbox"
            status = "PASS" if code == 0 else "FAIL"
            print(f"[{slug}] test ({mode}): {status} (exit {code})")
            if err:
                print(err[:500])
        if args.json:
            print(json.dumps({"test_results": results}))
        sys.exit(0 if all(r["passed"] for r in results) else 1)

    sys.exit(0)


if __name__ == "__main__":
    main()
