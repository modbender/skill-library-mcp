#!/usr/bin/env python3
"""OpenClaw Arbiter— Permission auditor + enforcement for agent skills.

Analyzes installed skills to report what system resources each one
accesses: binaries, environment variables, file I/O, network calls,
subprocess execution, and more. Full features adds automated policy
enforcement, quarantine, revocation, and protection sweeps.

Philosophy: alert -> subvert -> quarantine -> defend
Free = alert. Pro = subvert + quarantine + defend.

Usage:
    arbiter.py audit   [skill] [--workspace PATH]
    arbiter.py report  [skill] [--workspace PATH]
    arbiter.py status         [--workspace PATH]
    arbiter.py policy  [--init] [--workspace PATH]
    arbiter.py enforce [skill] [--workspace PATH]
    arbiter.py quarantine <skill> [--workspace PATH]
    arbiter.py unquarantine <skill> [--workspace PATH]
    arbiter.py revoke <skill> [--workspace PATH]
    arbiter.py protect        [--workspace PATH]
"""

import argparse
import io
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Windows Unicode stdout fix
# ---------------------------------------------------------------------------

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace"
    )

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

QUARANTINE_PREFIX = ".quarantined-"
QUARANTINE_VAULT = ".quarantine"
POLICY_FILE = ".arbiter-policy.json"

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".integrity", ".quarantine", ".snapshots",
}

SELF_SKILL_DIRS = {
    "openclaw-arbiter", "openclaw-arbiter",
}

# ---------------------------------------------------------------------------
# Permission categories and detection patterns
# ---------------------------------------------------------------------------

PYTHON_PATTERNS = {
    "network": [
        (re.compile(r"\burllib\b"), "urllib import"),
        (re.compile(r"\brequests\b"), "requests library"),
        (re.compile(r"\bhttpx\b"), "httpx library"),
        (re.compile(r"\baiohttp\b"), "aiohttp library"),
        (re.compile(r"\bsocket\b"), "socket module"),
        (re.compile(r"\bhttp\.client\b"), "http.client module"),
        (re.compile(r"\bftplib\b"), "FTP library"),
        (re.compile(r"\bsmtplib\b"), "SMTP library"),
        (re.compile(r"https?://"), "hardcoded URL"),
    ],
    "subprocess": [
        (re.compile(r"\bsubprocess\b"), "subprocess module"),
        (re.compile(r"\bos\.system\b"), "os.system call"),
        (re.compile(r"\bos\.popen\b"), "os.popen call"),
        (re.compile(r"\bos\.exec"), "os.exec* call"),
        (re.compile(r"\bshutil\.which\b"), "binary lookup"),
        (re.compile(r"\bPopen\b"), "Popen constructor"),
    ],
    "file_write": [
        (re.compile(r"""open\s*\([^)]*['"][wa]"""), "file write/append"),
        (re.compile(r"\bshutil\.copy"), "file copy"),
        (re.compile(r"\bshutil\.move\b"), "file move"),
        (re.compile(r"\bos\.rename\b"), "file rename"),
        (re.compile(r"\bos\.remove\b"), "file delete"),
        (re.compile(r"\bos\.unlink\b"), "file unlink"),
        (re.compile(r"\bos\.rmdir\b"), "directory remove"),
        (re.compile(r"\bshutil\.rmtree\b"), "recursive delete"),
        (re.compile(r"\bos\.makedirs\b"), "directory creation"),
        (re.compile(r"\bPath\b[^;]*\.write_"), "pathlib write"),
        (re.compile(r"\bPath\b[^;]*\.mkdir\b"), "pathlib mkdir"),
        (re.compile(r"\bPath\b[^;]*\.unlink\b"), "pathlib unlink"),
    ],
    "file_read": [
        (re.compile(r"""open\s*\([^)]*['"]r"""), "file read"),
        (re.compile(r"\bPath\b[^;]*\.read_"), "pathlib read"),
        (re.compile(r"\bos\.walk\b"), "directory walk"),
        (re.compile(r"\bos\.listdir\b"), "directory listing"),
        (re.compile(r"\bglob\b"), "glob pattern"),
    ],
    "environment": [
        (re.compile(r"\bos\.environ\b"), "env var access"),
        (re.compile(r"\bos\.getenv\b"), "env var read"),
        (re.compile(r"\bos\.putenv\b"), "env var write"),
    ],
    "crypto": [
        (re.compile(r"\bhashlib\b"), "hash computation"),
        (re.compile(r"\bhmac\b"), "HMAC operations"),
        (re.compile(r"\bssl\b"), "SSL/TLS"),
        (re.compile(r"\bcryptography\b"), "cryptography library"),
    ],
    "serialization": [
        (re.compile(r"\bpickle\b"), "pickle (unsafe deserialization)"),
        (re.compile(r"\byaml\.load\b"), "YAML load (potentially unsafe)"),
        (re.compile(r"\beval\b\s*\("), "eval() call"),
        (re.compile(r"\bexec\b\s*\("), "exec() call"),
        (re.compile(r"\b__import__\b"), "dynamic import"),
        (re.compile(r"\bcompile\b\s*\("), "compile() call"),
    ],
}

SHELL_PATTERNS = {
    "network": [
        (re.compile(r"\bcurl\b"), "curl command"),
        (re.compile(r"\bwget\b"), "wget command"),
        (re.compile(r"\bnc\b"), "netcat"),
        (re.compile(r"\bssh\b"), "SSH connection"),
        (re.compile(r"\bscp\b"), "SCP transfer"),
    ],
    "subprocess": [
        (re.compile(r"\beval\b"), "eval command"),
        (re.compile(r"\bsource\b"), "source command"),
        (re.compile(r"\$\("), "command substitution"),
    ],
    "file_write": [
        (re.compile(r">\s*[^&]"), "file redirect"),
        (re.compile(r"\brm\s"), "file delete"),
        (re.compile(r"\bmkdir\b"), "directory creation"),
        (re.compile(r"\bchmod\b"), "permission change"),
        (re.compile(r"\bchown\b"), "ownership change"),
    ],
}

RISK_LEVELS = {
    "serialization": "CRITICAL",
    "subprocess": "HIGH",
    "network": "HIGH",
    "file_write": "MEDIUM",
    "environment": "MEDIUM",
    "crypto": "LOW",
    "file_read": "LOW",
}

RISK_ORDER = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}

ALL_CATEGORIES = [
    "network", "subprocess", "file_write", "file_read",
    "environment", "crypto", "serialization",
]

# Default policy: what is allowed without flagging
DEFAULT_POLICY = {
    "max_risk": "MEDIUM",
    "rules": {
        "serialization": "deny",
        "subprocess": "review",
        "network": "review",
        "file_write": "allow",
        "file_read": "allow",
        "environment": "allow",
        "crypto": "allow",
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_iso():
    return datetime.now(timezone.utc).isoformat()


def resolve_workspace(ws_arg):
    """Determine workspace path from arg, env, or defaults."""
    if ws_arg:
        return Path(ws_arg).resolve()
    env = os.environ.get("OPENCLAW_WORKSPACE")
    if env:
        return Path(env).resolve()
    cwd = Path.cwd()
    if (cwd / "AGENTS.md").exists():
        return cwd
    default = Path.home() / ".openclaw" / "workspace"
    if default.exists():
        return default
    return cwd


def parse_skill_metadata(skill_md_path):
    """Parse SKILL.md YAML frontmatter for metadata."""
    info = {
        "name": "", "description": "",
        "requires_bins": [], "requires_env": [], "os": [],
    }
    try:
        content = skill_md_path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, PermissionError):
        return info

    if not content.startswith("---"):
        return info
    end = content.find("---", 3)
    if end == -1:
        return info
    frontmatter = content[3:end].strip()

    for line in frontmatter.split("\n"):
        line = line.strip()
        if line.startswith("name:"):
            info["name"] = line[5:].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            info["description"] = line[12:].strip().strip('"').strip("'")
        elif line.startswith("metadata:"):
            meta_str = line[9:].strip()
            try:
                meta = json.loads(meta_str)
                oc = meta.get("openclaw", {})
                req = oc.get("requires", {})
                info["requires_bins"] = req.get("bins", [])
                info["requires_env"] = req.get("env", [])
                info["os"] = oc.get("os", [])
            except (json.JSONDecodeError, AttributeError):
                pass
    return info


def find_skills(workspace):
    """Find all installed skills (excluding self and quarantined)."""
    skills_dir = workspace / "skills"
    if not skills_dir.exists():
        return []

    skills = []
    for entry in sorted(skills_dir.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name in SELF_SKILL_DIRS:
            continue
        if entry.name.startswith(QUARANTINE_PREFIX):
            continue
        if entry.name.startswith(".quarantine"):
            continue
        skill_md = entry / "SKILL.md"
        if skill_md.exists():
            skills.append(entry)
    return skills


def find_quarantined_skills(workspace):
    """Find all quarantined skills."""
    skills_dir = workspace / "skills"
    if not skills_dir.exists():
        return []

    quarantined = []
    for entry in sorted(skills_dir.iterdir()):
        if entry.is_dir() and entry.name.startswith(QUARANTINE_PREFIX):
            quarantined.append(entry)
    return quarantined


def scan_script(filepath, workspace):
    """Scan a script file for permission usage patterns."""
    permissions = {}
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except (OSError, PermissionError):
        return permissions

    lines = content.split("\n")
    is_python = filepath.suffix == ".py"
    is_shell = filepath.suffix in (".sh", ".bash", ".zsh") or (
        lines and lines[0].startswith("#!") and ("sh" in lines[0] or "bash" in lines[0])
    )

    patterns = {}
    if is_python:
        patterns = PYTHON_PATTERNS
    elif is_shell:
        patterns = SHELL_PATTERNS

    for category, pats in patterns.items():
        for pattern, desc in pats:
            for line_idx, line in enumerate(lines, 1):
                stripped = line.strip()
                if is_python and stripped.startswith("#"):
                    continue
                if is_shell and stripped.startswith("#") and not stripped.startswith("#!"):
                    continue

                if pattern.search(line):
                    if category not in permissions:
                        permissions[category] = []
                    permissions[category].append({
                        "file": str(filepath.relative_to(workspace)),
                        "line": line_idx,
                        "detail": desc,
                        "snippet": stripped[:80],
                    })

    return permissions


def audit_skill(skill_dir, workspace):
    """Full audit of a single skill."""
    skill_md = skill_dir / "SKILL.md"
    meta = parse_skill_metadata(skill_md)

    all_permissions = {}

    for root, dirs, filenames in os.walk(skill_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in filenames:
            fpath = Path(root) / fname
            if fpath.suffix in (".py", ".sh", ".bash", ".zsh", ".js", ".ts"):
                perms = scan_script(fpath, workspace)
                for cat, findings in perms.items():
                    if cat not in all_permissions:
                        all_permissions[cat] = []
                    all_permissions[cat].extend(findings)

    return {
        "name": meta["name"] or skill_dir.name,
        "description": meta["description"],
        "requires_bins": meta["requires_bins"],
        "requires_env": meta["requires_env"],
        "os": meta["os"],
        "permissions": all_permissions,
    }


def highest_risk(permissions):
    """Return the highest risk level found in a permissions dict."""
    best = "LOW"
    for cat in permissions:
        risk = RISK_LEVELS.get(cat, "LOW")
        if RISK_ORDER.get(risk, 0) > RISK_ORDER.get(best, 0):
            best = risk
    return best if permissions else "CLEAN"


def load_policy(workspace):
    """Load the policy file from the workspace, or return None."""
    policy_path = workspace / POLICY_FILE
    if not policy_path.exists():
        return None
    try:
        with open(policy_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def save_policy(workspace, policy):
    """Save a policy file to the workspace."""
    policy_path = workspace / POLICY_FILE
    with open(policy_path, "w", encoding="utf-8") as f:
        json.dump(policy, f, indent=2)
    return policy_path


# ---------------------------------------------------------------------------
# Free Commands: audit, report, status
# ---------------------------------------------------------------------------

def cmd_audit(workspace, skill_name=None):
    """Audit permissions for all or a specific skill."""
    print("=" * 60)
    print("OPENCLAW ARBITER FULL -- PERMISSION AUDIT")
    print("=" * 60)
    print(f"Workspace: {workspace}")
    print(f"Timestamp: {now_iso()}")
    print()

    skills = find_skills(workspace)
    if not skills:
        print("No skills found.")
        return 0

    if skill_name:
        skills = [s for s in skills if s.name == skill_name]
        if not skills:
            print(f"Skill not found: {skill_name}")
            return 1

    total_high = 0
    total_critical = 0

    for skill_dir in skills:
        result = audit_skill(skill_dir, workspace)
        print("-" * 40)
        print(f"SKILL: {result['name']}")
        print("-" * 40)

        if result["description"]:
            print(f"  Description: {result['description'][:80]}")
        if result["requires_bins"]:
            print(f"  Requires: {', '.join(result['requires_bins'])}")
        if result["requires_env"]:
            print(f"  Env vars: {', '.join(result['requires_env'])}")
        print()

        if not result["permissions"]:
            print("  [CLEAN] No elevated permissions detected.")
            print()
            continue

        for category, findings in sorted(result["permissions"].items()):
            risk = RISK_LEVELS.get(category, "UNKNOWN")
            if risk == "CRITICAL":
                total_critical += len(findings)
            elif risk == "HIGH":
                total_high += len(findings)

            print(f"  [{risk}] {category.upper()} ({len(findings)} occurrence(s))")
            for f in findings[:5]:
                print(f"    Line {f['line']}: {f['detail']}")
                print(f"      {f['snippet']}")
            if len(findings) > 5:
                print(f"    ... and {len(findings) - 5} more")
            print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Skills audited: {len(skills)}")
    print(f"  Critical findings: {total_critical}")
    print(f"  High-risk findings: {total_high}")
    print()

    if total_critical > 0:
        print("ACTION REQUIRED: Skills with critical permissions detected.")
        print()
        print("Use 'enforce' or 'protect' to auto-quarantine dangerous skills.")
        return 2
    elif total_high > 0:
        print("REVIEW NEEDED: Skills with elevated permissions detected.")
        print()
        print("Use 'enforce' to check skills against your policy.")
        return 1
    else:
        print("[CLEAN] All skills within normal permission bounds.")
        return 0


def cmd_report(workspace, skill_name=None):
    """Generate a compact permission matrix."""
    print("=" * 60)
    print("OPENCLAW ARBITER FULL -- PERMISSION MATRIX")
    print("=" * 60)
    print()

    skills = find_skills(workspace)
    if skill_name:
        skills = [s for s in skills if s.name == skill_name]

    if not skills:
        print("No skills found.")
        return 0

    categories = ALL_CATEGORIES

    # Header
    header = f"{'Skill':<30}"
    for cat in categories:
        header += f" {cat[:6]:>6}"
    print(header)
    print("-" * len(header))

    for skill_dir in skills:
        result = audit_skill(skill_dir, workspace)
        row = f"{result['name']:<30}"
        for cat in categories:
            count = len(result["permissions"].get(cat, []))
            if count > 0:
                row += f" {count:>6}"
            else:
                row += f" {'--':>6}"
        print(row)

    print()
    print("Legend: Numbers = occurrences found. -- = none detected.")
    print()
    return 0


def cmd_status(workspace):
    """Quick summary of all skills and quarantine state."""
    skills = find_skills(workspace)
    quarantined = find_quarantined_skills(workspace)
    risky = 0
    for skill_dir in skills:
        result = audit_skill(skill_dir, workspace)
        for cat in result["permissions"]:
            if RISK_LEVELS.get(cat) in ("CRITICAL", "HIGH"):
                risky += 1
                break

    parts = []
    if risky > 0:
        parts.append(f"{risky} risky")
    if quarantined:
        parts.append(f"{len(quarantined)} quarantined")

    if risky > 0:
        detail = f" ({', '.join(parts)})" if parts else ""
        print(f"[WARNING] {len(skills)} skill(s) audited{detail}")
        return 1
    else:
        detail = f" ({', '.join(parts)})" if parts else ""
        print(f"[CLEAN] {len(skills)} skill(s) audited, all within normal bounds{detail}")
        return 0


# ---------------------------------------------------------------------------
# Pro Commands: policy, enforce, quarantine, unquarantine, revoke, protect
# ---------------------------------------------------------------------------

def cmd_policy(workspace, init=False):
    """Generate or display the permission policy."""
    policy_path = workspace / POLICY_FILE
    existing = load_policy(workspace)

    if init:
        if existing:
            print(f"Policy already exists: {policy_path}")
            print("Delete it first to re-initialize.")
            print()
            print(json.dumps(existing, indent=2))
            return 0

        save_policy(workspace, DEFAULT_POLICY)
        print(f"Policy initialized: {policy_path}")
        print()
        print(json.dumps(DEFAULT_POLICY, indent=2))
        print()
        print("Edit this file to customize permission rules.")
        print()
        print("Rule values:")
        print("  allow  -- permit this category without flagging")
        print("  review -- flag for manual review")
        print("  deny   -- auto-quarantine skills using this category")
        print()
        print("max_risk: maximum overall risk level before auto-quarantine")
        print("  CRITICAL, HIGH, MEDIUM, LOW")
        return 0

    if existing:
        print(f"Policy: {policy_path}")
        print()
        print(json.dumps(existing, indent=2))
        print()
        print("Rule values: allow | review | deny")
        print(f"Max risk: {existing.get('max_risk', 'MEDIUM')}")
        return 0

    print("No policy found.")
    print(f"Run 'policy --init' to create a default policy at:")
    print(f"  {policy_path}")
    return 1


def cmd_enforce(workspace, skill_name=None):
    """Check skills against the permission policy."""
    policy = load_policy(workspace)
    if policy is None:
        print("No policy found. Run 'policy --init' first.")
        return 1

    print("=" * 60)
    print("OPENCLAW ARBITER FULL -- POLICY ENFORCEMENT")
    print("=" * 60)
    print(f"Workspace: {workspace}")
    print(f"Timestamp: {now_iso()}")
    print(f"Max risk:  {policy.get('max_risk', 'MEDIUM')}")
    print()

    rules = policy.get("rules", {})
    max_risk = policy.get("max_risk", "MEDIUM")
    max_risk_order = RISK_ORDER.get(max_risk, 2)

    skills = find_skills(workspace)
    if skill_name:
        skills = [s for s in skills if s.name == skill_name]
        if not skills:
            print(f"Skill not found: {skill_name}")
            return 1

    denied = []
    review = []
    allowed = []

    for skill_dir in skills:
        result = audit_skill(skill_dir, workspace)
        skill_risk = highest_risk(result["permissions"])
        skill_risk_order = RISK_ORDER.get(skill_risk, 0)

        violations = []
        reviews = []

        # Check each permission category against rules
        for cat, findings in result["permissions"].items():
            rule = rules.get(cat, "allow")
            if rule == "deny":
                violations.append((cat, len(findings)))
            elif rule == "review":
                reviews.append((cat, len(findings)))

        # Check overall risk against max_risk
        exceeds_max = skill_risk_order > max_risk_order

        if violations or exceeds_max:
            denied.append({
                "name": result["name"],
                "dir": skill_dir,
                "risk": skill_risk,
                "violations": violations,
                "exceeds_max": exceeds_max,
            })
        elif reviews:
            review.append({
                "name": result["name"],
                "dir": skill_dir,
                "risk": skill_risk,
                "reviews": reviews,
            })
        else:
            allowed.append({
                "name": result["name"],
                "risk": skill_risk,
            })

    # Report denied
    if denied:
        print("-" * 40)
        print("DENIED (exceeds policy)")
        print("-" * 40)
        for d in denied:
            print(f"  [{d['risk']}] {d['name']}")
            if d["exceeds_max"]:
                print(f"    Exceeds max_risk ({d['risk']} > {max_risk})")
            for cat, count in d.get("violations", []):
                print(f"    Policy: {cat} = deny ({count} occurrence(s))")
            print(f"    -> Run: quarantine {d['name']}")
        print()

    # Report review
    if review:
        print("-" * 40)
        print("REVIEW (flagged for manual review)")
        print("-" * 40)
        for r in review:
            print(f"  [{r['risk']}] {r['name']}")
            for cat, count in r.get("reviews", []):
                print(f"    Policy: {cat} = review ({count} occurrence(s))")
        print()

    # Report allowed
    if allowed:
        print("-" * 40)
        print("ALLOWED")
        print("-" * 40)
        for a in allowed:
            risk_label = a["risk"] if a["risk"] != "CLEAN" else "CLEAN"
            print(f"  [{risk_label}] {a['name']}")
        print()

    # Summary
    print("=" * 60)
    print("ENFORCEMENT SUMMARY")
    print("=" * 60)
    print(f"  Denied:  {len(denied)}")
    print(f"  Review:  {len(review)}")
    print(f"  Allowed: {len(allowed)}")
    print()

    if denied:
        print("Run 'quarantine <skill>' or 'revoke <skill>' for denied skills.")
        print("Run 'protect' to auto-quarantine all denied skills.")
        return 2
    elif review:
        print("Skills flagged for review. Audit them individually for details.")
        return 1
    else:
        print("[CLEAN] All skills comply with policy.")
        return 0


def cmd_quarantine(workspace, skill_name):
    """Quarantine an over-privileged skill by renaming its directory."""
    skills_dir = workspace / "skills"
    skill_dir = skills_dir / skill_name

    if not skill_dir.is_dir():
        quarantined = skills_dir / (QUARANTINE_PREFIX + skill_name)
        if quarantined.is_dir():
            print(f"Skill '{skill_name}' is already quarantined.")
            return 0
        print(f"Skill not found: {skill_name}")
        print("Available skills:")
        if skills_dir.is_dir():
            for d in sorted(skills_dir.iterdir()):
                if d.is_dir() and d.name not in SELF_SKILL_DIRS:
                    prefix = "[Q] " if d.name.startswith(QUARANTINE_PREFIX) else "    "
                    name = d.name.removeprefix(QUARANTINE_PREFIX) if d.name.startswith(QUARANTINE_PREFIX) else d.name
                    print(f"  {prefix}{name}")
        return 1

    quarantined = skills_dir / (QUARANTINE_PREFIX + skill_name)
    skill_dir.rename(quarantined)
    print(f"Quarantined: {skill_name}")
    print(f"  Moved: skills/{skill_name}/ -> skills/{QUARANTINE_PREFIX}{skill_name}/")
    print(f"  The agent will not load this skill on next session.")
    print(f"  To restore: run 'unquarantine {skill_name}'")
    return 0


def cmd_unquarantine(workspace, skill_name):
    """Restore a quarantined skill."""
    skills_dir = workspace / "skills"
    quarantined = skills_dir / (QUARANTINE_PREFIX + skill_name)

    if not quarantined.is_dir():
        print(f"No quarantined skill found: {skill_name}")
        return 1

    restored = skills_dir / skill_name
    if restored.is_dir():
        print(f"Cannot unquarantine: skills/{skill_name}/ already exists")
        return 1

    quarantined.rename(restored)
    print(f"Unquarantined: {skill_name}")
    print(f"  Moved: skills/{QUARANTINE_PREFIX}{skill_name}/ -> skills/{skill_name}/")
    print(f"  WARNING: Re-audit this skill before use.")
    return 0


def cmd_revoke(workspace, skill_name):
    """Delete a skill entirely, moving it to the quarantine vault first."""
    skills_dir = workspace / "skills"
    skill_dir = skills_dir / skill_name

    # Also handle quarantined skills
    if not skill_dir.is_dir():
        quarantined = skills_dir / (QUARANTINE_PREFIX + skill_name)
        if quarantined.is_dir():
            skill_dir = quarantined
        else:
            print(f"Skill not found: {skill_name}")
            return 1

    # Create vault directory with metadata
    vault_dir = workspace / QUARANTINE_VAULT / "arbiter" / skill_name
    vault_dir.mkdir(parents=True, exist_ok=True)

    # Save revocation metadata
    meta = {
        "skill": skill_name,
        "revoked_at": now_iso(),
        "original_path": str(skill_dir),
    }

    # Audit the skill before revoking to preserve the record
    try:
        result = audit_skill(skill_dir, workspace)
        meta["permissions"] = {}
        for cat, findings in result["permissions"].items():
            meta["permissions"][cat] = len(findings)
        meta["risk"] = highest_risk(result["permissions"])
    except Exception:
        meta["permissions"] = {}
        meta["risk"] = "UNKNOWN"

    meta_path = vault_dir / "revocation.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # Move skill to vault
    vault_skill_dir = vault_dir / "skill"
    if vault_skill_dir.exists():
        shutil.rmtree(vault_skill_dir)
    shutil.copytree(skill_dir, vault_skill_dir)
    shutil.rmtree(skill_dir)

    print(f"Revoked: {skill_name}")
    print(f"  Backed up to: {vault_dir}")
    print(f"  Revocation metadata: {meta_path}")
    print(f"  Risk at revocation: {meta['risk']}")
    print()
    print("  This skill has been permanently removed from the workspace.")
    print("  The backup in .quarantine/arbiter/ can be deleted manually.")
    return 0


def cmdtect(workspace):
    """Full automated sweep: audit all, enforce policy, quarantine critical.

    Actions:
    1. Audit all installed skills
    2. Auto-quarantine any with CRITICAL permissions (serialization: eval/exec/pickle)
    3. If a policy exists, enforce it (quarantine denied skills)
    4. Flag HIGH-risk skills for review
    5. Report all actions taken
    """
    print("=" * 60)
    print("OPENCLAW ARBITER FULL -- FULLTECTION SWEEP")
    print("=" * 60)
    print(f"Workspace: {workspace}")
    print(f"Timestamp: {now_iso()}")
    print()

    skills = find_skills(workspace)
    if not skills:
        print("No skills found. Workspace is clean.")
        print("=" * 60)
        return 0

    policy = load_policy(workspace)
    rules = policy.get("rules", {}) if policy else {}
    max_risk = policy.get("max_risk", "MEDIUM") if policy else "MEDIUM"
    max_risk_order = RISK_ORDER.get(max_risk, 2)

    actions_taken = []
    quarantined_skills = set()
    flagged_skills = []
    clean_skills = []

    print(f"Auditing {len(skills)} skill(s)...")
    if policy:
        print(f"Policy: {workspace / POLICY_FILE}")
        print(f"Max risk: {max_risk}")
    else:
        print("No policy found. Using defaults (quarantine CRITICAL, flag HIGH).")
    print()

    for skill_dir in skills:
        result = audit_skill(skill_dir, workspace)
        skill_risk = highest_risk(result["permissions"])
        skill_risk_order = RISK_ORDER.get(skill_risk, 0)
        name = result["name"]

        should_quarantine = False
        reasons = []

        # Rule 1: Always quarantine CRITICAL (serialization: eval/exec/pickle)
        if "serialization" in result["permissions"]:
            should_quarantine = True
            reasons.append(f"CRITICAL: serialization ({len(result['permissions']['serialization'])} occurrence(s))")

        # Rule 2: Check policy rules for deny
        if policy:
            for cat, findings in result["permissions"].items():
                rule = rules.get(cat, "allow")
                if rule == "deny":
                    should_quarantine = True
                    reasons.append(f"POLICY DENY: {cat} ({len(findings)} occurrence(s))")

            # Rule 3: Check overall risk against max_risk
            if skill_risk_order > max_risk_order:
                should_quarantine = True
                reasons.append(f"EXCEEDS max_risk: {skill_risk} > {max_risk}")

        if should_quarantine:
            # Quarantine this skill
            skills_dir = workspace / "skills"
            quarantined_path = skills_dir / (QUARANTINE_PREFIX + name)
            if not quarantined_path.exists():
                skill_dir.rename(quarantined_path)
                quarantined_skills.add(name)
                action = f"QUARANTINED: {name}"
                for r in reasons:
                    action += f"\n    {r}"
                actions_taken.append(action)
                print(f"  [QUARANTINE] {name}")
                for r in reasons:
                    print(f"    {r}")
        elif skill_risk_order >= RISK_ORDER.get("HIGH", 3):
            # Flag HIGH-risk for review
            flagged_skills.append(name)
            flag_cats = [
                cat for cat in result["permissions"]
                if RISK_LEVELS.get(cat) in ("HIGH", "CRITICAL")
            ]
            actions_taken.append(f"FLAGGED: {name} ({', '.join(flag_cats)})")
            print(f"  [FLAG] {name} -- {skill_risk} risk, review recommended")
        else:
            clean_skills.append(name)
            print(f"  [OK] {name} -- {skill_risk}")

    # Summary
    print()
    print("=" * 60)
    print("FULLTECTION SUMMARY")
    print("=" * 60)
    print(f"  Skills audited:     {len(skills)}")
    print(f"  Quarantined:        {len(quarantined_skills)}")
    print(f"  Flagged for review: {len(flagged_skills)}")
    print(f"  Clean:              {len(clean_skills)}")
    print()

    if actions_taken:
        print("ACTIONS TAKEN:")
        for a in actions_taken:
            for line in a.split("\n"):
                print(f"  - {line}")
        print()

    if quarantined_skills:
        print("QUARANTINED SKILLS:")
        for name in sorted(quarantined_skills):
            print(f"  - {name}")
        print()
        print("  Quarantined skills will not be loaded by the agent.")
        print("  Use 'unquarantine <skill>' to restore after review.")
        print("  Use 'revoke <skill>' to permanently delete.")
        print()

    if flagged_skills:
        print("FLAGGED FOR REVIEW:")
        for name in flagged_skills:
            print(f"  - {name}")
        print()
        print("  Run 'audit <skill>' for detailed findings.")
        print()

    if not quarantined_skills and not flagged_skills:
        print("[CLEAN] All skills within acceptable permission bounds.")
        print()

    print("=" * 60)

    if quarantined_skills:
        return 2
    elif flagged_skills:
        return 1
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw Arbiter — Permission auditor + enforcement"
    )
    sub = parser.add_subparsers(dest="command", help="Command to run")

    # audit
    p_audit = sub.add_parser("audit", help="Deep audit of skill permissions")
    p_audit.add_argument("skill", nargs="?", help="Specific skill to audit")
    p_audit.add_argument("--workspace", "-w", help="Workspace path")

    # report
    p_report = sub.add_parser("report", help="Compact permission matrix")
    p_report.add_argument("skill", nargs="?", help="Specific skill to report")
    p_report.add_argument("--workspace", "-w", help="Workspace path")

    # status
    p_status = sub.add_parser("status", help="Quick permission summary")
    p_status.add_argument("--workspace", "-w", help="Workspace path")

    # policy
    p_policy = sub.add_parser("policy", help="Manage permission policy")
    p_policy.add_argument("--init", action="store_true", help="Create default policy")
    p_policy.add_argument("--workspace", "-w", help="Workspace path")

    # enforce
    p_enforce = sub.add_parser("enforce", help="Enforce permission policy")
    p_enforce.add_argument("skill", nargs="?", help="Specific skill to check")
    p_enforce.add_argument("--workspace", "-w", help="Workspace path")

    # quarantine
    p_quarantine = sub.add_parser("quarantine", help="Quarantine an over-privileged skill")
    p_quarantine.add_argument("skill", help="Skill to quarantine")
    p_quarantine.add_argument("--workspace", "-w", help="Workspace path")

    # unquarantine
    p_unquarantine = sub.add_parser("unquarantine", help="Restore a quarantined skill")
    p_unquarantine.add_argument("skill", help="Skill to unquarantine")
    p_unquarantine.add_argument("--workspace", "-w", help="Workspace path")

    # revoke
    p_revoke = sub.add_parser("revoke", help="Permanently revoke a skill")
    p_revoke.add_argument("skill", help="Skill to revoke")
    p_revoke.add_argument("--workspace", "-w", help="Workspace path")

    # protect
    ptect = sub.add_parser("protect", help="Full automated protection sweep")
    ptect.add_argument("--workspace", "-w", help="Workspace path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    workspace = resolve_workspace(getattr(args, "workspace", None))
    if not workspace.exists():
        print(f"Workspace not found: {workspace}", file=sys.stderr)
        sys.exit(1)

    if args.command == "audit":
        sys.exit(cmd_audit(workspace, getattr(args, "skill", None)))
    elif args.command == "report":
        sys.exit(cmd_report(workspace, getattr(args, "skill", None)))
    elif args.command == "status":
        sys.exit(cmd_status(workspace))
    elif args.command == "policy":
        sys.exit(cmd_policy(workspace, init=args.init))
    elif args.command == "enforce":
        sys.exit(cmd_enforce(workspace, getattr(args, "skill", None)))
    elif args.command == "quarantine":
        sys.exit(cmd_quarantine(workspace, args.skill))
    elif args.command == "unquarantine":
        sys.exit(cmd_unquarantine(workspace, args.skill))
    elif args.command == "revoke":
        sys.exit(cmd_revoke(workspace, args.skill))
    elif args.command == "protect":
        sys.exit(cmdtect(workspace))


if __name__ == "__main__":
    main()
