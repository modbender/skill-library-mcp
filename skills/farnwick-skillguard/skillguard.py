#!/usr/bin/env python3
"""
SkillGuard — Security scanner for OpenClaw skills.
Analyzes skill files with AI to detect malicious code before installation.
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile
import argparse
import re
from pathlib import Path
from typing import Optional

# ─── Constants ───────────────────────────────────────────────────────────────

VERSION = "1.0.0"

SKILL_DIRS = [
    "/usr/lib/node_modules/openclaw/skills",
    os.path.expanduser("~/.openclaw/workspace/skills"),
    os.path.expanduser("~/.openclaw/skills"),
]

OPENCLAW_CONFIG = os.path.expanduser("~/.openclaw/openclaw.json")
AUTH_PROFILES = os.path.expanduser("~/.openclaw/agents/main/agent/auth-profiles.json")

SCAN_EXTENSIONS = {".sh", ".py", ".js", ".ts", ".rb", ".pl", ".php", ".go",
                   ".bash", ".zsh", ".fish", ".lua", ".r", ".ps1", ".psm1",
                   ".cmd", ".bat", ".vbs", ".md"}

MAX_FILE_SIZE = 100 * 1024  # 100KB per file
SECURITY_PROMPT_PATH = Path(__file__).parent / "prompts" / "security-analysis.txt"


# ─── Colour helpers ──────────────────────────────────────────────────────────

NO_COLOR = os.environ.get("NO_COLOR") or not sys.stdout.isatty()

def c(text: str, code: str) -> str:
    if NO_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"

RED    = lambda t: c(t, "31")
YELLOW = lambda t: c(t, "33")
GREEN  = lambda t: c(t, "32")
CYAN   = lambda t: c(t, "36")
BOLD   = lambda t: c(t, "1")
DIM    = lambda t: c(t, "2")


# ─── Auth / LLM ──────────────────────────────────────────────────────────────

def load_api_credentials():
    """Load the best available API credentials from OpenClaw config."""
    try:
        with open(AUTH_PROFILES) as f:
            data = json.load(f)
        profiles = data.get("profiles", {})

        # Preference order: anthropic (direct API key) > openrouter > deepseek
        for name, prof in profiles.items():
            provider = prof.get("provider", "")
            if provider == "anthropic" and prof.get("type") == "api_key":
                return {"provider": "anthropic", "key": prof["key"]}

        for name, prof in profiles.items():
            provider = prof.get("provider", "")
            if provider == "anthropic" and prof.get("type") == "token":
                return {"provider": "anthropic", "key": prof["token"]}

        for name, prof in profiles.items():
            provider = prof.get("provider", "")
            if provider == "openrouter":
                return {"provider": "openrouter", "key": prof.get("token", prof.get("key"))}

        for name, prof in profiles.items():
            provider = prof.get("provider", "")
            if provider == "deepseek":
                return {"provider": "deepseek", "key": prof.get("key", prof.get("token"))}

    except Exception as e:
        pass

    return None


def call_llm_direct(prompt: str, system: str, creds: dict) -> Optional[str]:
    """Make a direct API call to an LLM provider."""
    import urllib.request

    provider = creds["provider"]
    api_key = creds["key"]

    if provider == "deepseek":
        url = "https://api.deepseek.com/v1/chat/completions"
        payload = {
            "model": "deepseek-chat",
            "max_tokens": 2048,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    elif provider == "openrouter":
        url = "https://openrouter.ai/api/v1/chat/completions"
        payload = {
            "model": "anthropic/claude-opus-4-5",
            "max_tokens": 2048,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://openclaw.io",
            "X-Title": "SkillGuard"
        }
    elif provider == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        payload = {
            "model": "claude-sonnet-4-5",
            "max_tokens": 2048,
            "system": system,
            "messages": [{"role": "user", "content": prompt}]
        }
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
    else:
        return None

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    with urllib.request.urlopen(req, timeout=90) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    if provider == "anthropic":
        return body["content"][0]["text"]
    else:
        return body["choices"][0]["message"]["content"]


def call_llm_via_openclaw(full_prompt: str) -> Optional[str]:
    """
    Fallback: use 'openclaw agent --local' as LLM backend.
    Uses a unique throwaway session to avoid polluting real sessions.
    """
    import uuid
    session_id = f"skillguard-scan-{uuid.uuid4().hex[:12]}"

    try:
        result = subprocess.run(
            ["openclaw", "agent", "--local",
             "--session-id", session_id,
             "--message", full_prompt,
             "--json"],
            capture_output=True, text=True, timeout=120
        )

        if result.returncode != 0:
            return None

        data = json.loads(result.stdout)
        payloads = data.get("payloads", [])
        if payloads:
            return payloads[0].get("text", "")
        return None

    except Exception:
        return None


def call_llm(prompt: str, system: str) -> Optional[str]:
    """
    Call LLM API and return the response text.
    Priority: DeepSeek (direct) > OpenRouter (direct) > Anthropic (direct) > openclaw agent (fallback)
    """
    creds = load_api_credentials()

    # Try direct API calls first (faster, cleaner)
    # Priority order based on what typically works in OpenClaw deployments
    provider_order = ["deepseek", "openrouter", "anthropic"]

    if creds:
        # Reorder: put the loaded provider first, then others
        all_creds = []
        try:
            with open(AUTH_PROFILES) as f:
                data = json.load(f)
            profiles = data.get("profiles", {})

            # Collect all working providers in priority order
            for pname in provider_order:
                for _, prof in profiles.items():
                    if prof.get("provider") == pname:
                        key = prof.get("key", prof.get("token"))
                        if key:
                            all_creds.append({"provider": pname, "key": key})
                            break
        except Exception:
            all_creds = [creds]

        for c in all_creds:
            try:
                result = call_llm_direct(prompt, system, c)
                if result:
                    return result
            except Exception as e:
                # 4xx errors (except 429) mean this provider won't work — skip
                err_str = str(e)
                if "401" in err_str or "403" in err_str or "402" in err_str:
                    continue
                # 429 = rate limit, 5xx = server error — also skip for now
                continue

    # Fallback: use openclaw agent --local
    # Combine system + user prompt since agent doesn't accept separate system prompt
    combined = f"{system}\n\n---\n\n{prompt}"
    result = call_llm_via_openclaw(combined)
    if result:
        return result

    print(f"{RED('✗')} All LLM backends failed. Check API credentials.", file=sys.stderr)
    return None


# ─── File collection ─────────────────────────────────────────────────────────

def collect_skill_files(skill_path: Path) -> dict:
    """
    Collect all relevant files from a skill directory.
    Returns: { "relative/path": "file contents" }
    """
    files = {}

    if not skill_path.exists():
        return files

    for filepath in sorted(skill_path.rglob("*")):
        if not filepath.is_file():
            continue

        # Skip binary-looking files, node_modules, .git, __pycache__
        rel = filepath.relative_to(skill_path)
        parts = rel.parts
        if any(p in ("node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build") for p in parts):
            continue

        # Check extension (include all text-like files)
        ext = filepath.suffix.lower()
        name = filepath.name.lower()

        # Always include SKILL.md, README, and known script extensions
        is_skill_doc = name in ("skill.md", "readme.md", "readme", "package.json",
                                 "requirements.txt", "dockerfile")
        is_script = ext in SCAN_EXTENSIONS

        if not (is_skill_doc or is_script):
            # Try to detect text files by reading first bytes
            try:
                with open(filepath, "rb") as f:
                    header = f.read(512)
                if b"\x00" in header:
                    continue  # Binary file
                # Check if it's mostly ASCII/UTF-8
                header.decode("utf-8", errors="strict")
                # It's text — include it
            except (UnicodeDecodeError, IOError):
                continue

        # Size check
        try:
            size = filepath.stat().st_size
            if size == 0:
                continue
            if size > MAX_FILE_SIZE:
                files[str(rel)] = f"[FILE TRUNCATED — {size} bytes, showing first 100KB]\n" + \
                                   filepath.read_bytes()[:MAX_FILE_SIZE].decode("utf-8", errors="replace")
                continue
            files[str(rel)] = filepath.read_text(errors="replace")
        except IOError:
            continue

    return files


# ─── Security analysis ───────────────────────────────────────────────────────

def build_analysis_prompt(skill_name: str, files: dict) -> str:
    """Build the LLM prompt with all file contents."""
    lines = [
        f"# Security Analysis Request: Skill '{skill_name}'",
        "",
        f"Total files to analyze: {len(files)}",
        "",
        "## Files",
        ""
    ]

    for rel_path, content in sorted(files.items()):
        lines.append(f"### {rel_path}")
        lines.append("```")
        lines.append(content)
        lines.append("```")
        lines.append("")

    lines.append("## Instructions")
    lines.append("Analyze all files above for security threats as per your system prompt.")
    lines.append("Return ONLY valid JSON in the format specified. No markdown wrapper.")

    return "\n".join(lines)


def load_security_system_prompt() -> str:
    """Load the security analysis system prompt."""
    try:
        return SECURITY_PROMPT_PATH.read_text()
    except IOError:
        # Fallback minimal prompt
        return """You are a security auditor. Analyze the skill files for:
credential theft, data exfiltration, reverse shells, privilege escalation,
persistence mechanisms, obfuscated code, undisclosed package installs.
Risk levels: CLEAN, LOW, MEDIUM, HIGH.
Return JSON: {"risk_level": "...", "summary": "...", "findings": [...], "recommendation": "install|review|block"}"""


def parse_llm_response(response: str) -> Optional[dict]:
    """Extract and parse JSON from LLM response."""
    if not response:
        return None

    # Try direct parse
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        pass

    # Try to extract JSON block
    match = re.search(r'\{[\s\S]*\}', response)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def scan_skill(skill_name: str, skill_path: Path, verbose: bool = False) -> Optional[dict]:
    """
    Scan a skill directory. Returns analysis result dict or None on error.
    """
    files = collect_skill_files(skill_path)

    if not files:
        return {
            "risk_level": "CLEAN",
            "summary": "No scannable files found in skill directory.",
            "findings": [],
            "recommendation": "install",
            "_warning": "empty"
        }

    if verbose:
        print(f"  {DIM(f'Scanning {len(files)} files...')}", file=sys.stderr)

    system_prompt = load_security_system_prompt()
    user_prompt = build_analysis_prompt(skill_name, files)

    if verbose:
        print(f"  {DIM('Calling LLM for analysis...')}", file=sys.stderr)

    response = call_llm(user_prompt, system_prompt)

    if response is None:
        return None

    result = parse_llm_response(response)

    if result is None:
        # LLM returned unparseable content
        return {
            "risk_level": "MEDIUM",
            "summary": "LLM returned unparseable response — manual review recommended.",
            "findings": [{
                "severity": "MEDIUM",
                "category": "Analysis Error",
                "description": "Could not parse LLM security analysis. Review manually.",
                "location": "N/A"
            }],
            "recommendation": "review",
            "_raw": response[:500]
        }

    return result


# ─── Output formatting ───────────────────────────────────────────────────────

RISK_ICONS = {
    "CLEAN":  "✅",
    "LOW":    "🟡",
    "MEDIUM": "⚠️ ",
    "HIGH":   "🚨",
}

RISK_COLORS = {
    "CLEAN":  GREEN,
    "LOW":    YELLOW,
    "MEDIUM": YELLOW,
    "HIGH":   RED,
}


def format_risk(level: str) -> str:
    icon = RISK_ICONS.get(level, "❓")
    color = RISK_COLORS.get(level, lambda x: x)
    return f"{icon} {color(BOLD(level))}"


def print_scan_result(skill_name: str, result: dict, show_install_prompt: bool = False) -> bool:
    """
    Print scan result. Returns True if user wants to proceed (for install flow).
    """
    level = result.get("risk_level", "MEDIUM")
    summary = result.get("summary", "No summary available.")
    findings = result.get("findings", [])
    recommendation = result.get("recommendation", "review")

    print()

    if level == "CLEAN":
        print(f"{GREEN('✅')} SkillGuard: {BOLD(skill_name)} — {GREEN('Clean.')}", end="")
        if show_install_prompt:
            print(" Installing...")
        else:
            print()
        return True

    # Non-clean result
    risk_display = format_risk(level)
    print(f"{RISK_ICONS.get(level, '⚠️')} SkillGuard: {BOLD(skill_name)} — Risk: {risk_display}")

    if summary:
        print(f"   {summary}")

    # Print findings
    if findings:
        print()
        for f in findings:
            sev = f.get("severity", "?")
            cat = f.get("category", "Unknown")
            desc = f.get("description", "")
            loc = f.get("location", "")
            sev_color = RED if sev in ("CRITICAL", "HIGH") else YELLOW
            loc_str = f" [{DIM(loc)}]" if loc and loc != "N/A" else ""
            print(f"   {sev_color(f'[{sev}]')} {CYAN(cat)}: {desc}{loc_str}")

    if not show_install_prompt:
        return False

    # Install prompt
    print()
    if recommendation == "block":
        print(f"   {RED('⚠ HIGH RISK: This skill is dangerous to install.')}")
        prompt_text = f"Install {skill_name} anyway? (type YES to confirm) "
    elif recommendation == "review":
        prompt_text = f"   Install {skill_name} anyway? [y/N] "
    else:
        prompt_text = f"   Install {skill_name}? [Y/n] "

    try:
        ans = input(prompt_text).strip()
    except (KeyboardInterrupt, EOFError):
        print()
        return False

    if recommendation == "block":
        return ans == "YES"
    elif recommendation == "review":
        return ans.lower() in ("y", "yes")
    else:
        return ans.lower() not in ("n", "no")


# ─── Commands ────────────────────────────────────────────────────────────────

def cmd_scan(args):
    """Scan a local skill directory."""
    path = Path(args.path).resolve()
    name = path.name

    if not path.exists():
        print(f"{RED('✗')} Path not found: {path}", file=sys.stderr)
        sys.exit(1)
    if not path.is_dir():
        print(f"{RED('✗')} Path is not a directory: {path}", file=sys.stderr)
        sys.exit(1)

    print(f"{DIM(f'Scanning {name}...')}")
    result = scan_skill(name, path, verbose=True)

    if result is None:
        print(f"{RED('✗')} Scan failed — could not reach LLM. Check your API credentials.", file=sys.stderr)
        sys.exit(2)

    print_scan_result(name, result, show_install_prompt=False)
    level = result.get("risk_level", "HIGH")
    sys.exit(0 if level in ("CLEAN", "LOW") else 1)


def cmd_install(args):
    """Download skill to temp, scan, then install or abort."""
    skill_name = args.name

    # Create temp directory for download
    tmpdir = tempfile.mkdtemp(prefix="skillguard-scan-")
    tmp_skill_path = Path(tmpdir) / "skills" / skill_name

    try:
        print(f"{DIM(f'Downloading {skill_name} to temp directory for scanning...')}")

        # Download skill to temp dir using clawhub
        result = subprocess.run(
            ["clawhub", "install", skill_name, "--workdir", tmpdir, "--no-input"],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"{RED('✗')} clawhub download failed:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(1)

        if not tmp_skill_path.exists():
            # Try to find where it actually installed
            skills_dir = Path(tmpdir) / "skills"
            candidates = list(skills_dir.iterdir()) if skills_dir.exists() else []
            if len(candidates) == 1:
                tmp_skill_path = candidates[0]
            else:
                print(f"{RED('✗')} Could not locate downloaded skill in temp dir.", file=sys.stderr)
                sys.exit(1)

        print(f"{DIM(f'Download complete. Running security scan...')}")
        scan_result = scan_skill(skill_name, tmp_skill_path, verbose=True)

        if scan_result is None:
            print(f"{YELLOW('⚠')} Could not complete LLM scan.", file=sys.stderr)
            try:
                ans = input(f"   Proceed with installation of {skill_name} without security scan? [y/N] ").strip()
            except (KeyboardInterrupt, EOFError):
                print()
                sys.exit(1)
            if ans.lower() not in ("y", "yes"):
                print("   Aborted.")
                sys.exit(1)
        else:
            proceed = print_scan_result(skill_name, scan_result, show_install_prompt=True)
            if not proceed:
                print(f"   {YELLOW('Installation aborted.')}")
                sys.exit(1)

        # Install for real
        print(f"{DIM('Installing via clawhub...')}")

        install_result = subprocess.run(
            ["clawhub", "install", skill_name, "--force", "--no-input"],
            capture_output=True, text=True
        )

        if install_result.returncode != 0:
            print(f"{RED('✗')} Installation failed:", file=sys.stderr)
            print(install_result.stderr, file=sys.stderr)
            sys.exit(1)

        print(f"{GREEN('✓')} {BOLD(skill_name)} installed successfully.")

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def cmd_audit(args):
    """Scan all installed skills and report."""
    found_skills = {}

    # Determine which dirs to scan
    audit_dirs = [args.audit_dir] if getattr(args, "audit_dir", None) else SKILL_DIRS

    for base_dir in audit_dirs:
        base = Path(base_dir)
        if not base.exists():
            continue
        for entry in sorted(base.iterdir()):
            if entry.is_dir() and entry.name not in found_skills:
                found_skills[entry.name] = entry

    # Apply limit if set
    if getattr(args, "limit", None):
        found_skills = dict(list(found_skills.items())[:args.limit])

    if not found_skills:
        print(f"{YELLOW('⚠')} No skills found in known skill directories.")
        print(f"   Checked: {', '.join(SKILL_DIRS)}")
        return

    print(f"{BOLD('SkillGuard Audit')} — scanning {len(found_skills)} skills\n")

    results = {}
    flagged = []

    for name, path in found_skills.items():
        print(f"  Scanning {name}...", end="", flush=True)
        result = scan_skill(name, path)

        if result is None:
            results[name] = {"risk_level": "ERROR", "summary": "LLM call failed"}
            print(f"  {RED('FAIL')}")
            continue

        level = result.get("risk_level", "HIGH")
        results[name] = result

        icon = RISK_ICONS.get(level, "❓")
        print(f" {icon} {level}")

        if level not in ("CLEAN",):
            flagged.append(name)

    # Summary table
    print(f"\n{'─'*60}")
    print(f"{'SKILL':<30} {'RISK':<12} {'SUMMARY'}")
    print(f"{'─'*60}")

    for name in sorted(results.keys()):
        r = results[name]
        level = r.get("risk_level", "ERROR")
        summary = r.get("summary", "")[:35]
        color = RISK_COLORS.get(level, lambda x: x)
        print(f"{name:<30} {color(level):<12} {DIM(summary)}")

    print(f"{'─'*60}")

    if flagged:
        print(f"\n{YELLOW('⚠')} {len(flagged)} skill(s) flagged for review:\n")
        for name in flagged:
            r = results[name]
            print_scan_result(name, r, show_install_prompt=False)
    else:
        print(f"\n{GREEN('✅')} All skills clean.")


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="skillguard",
        description="SkillGuard — AI-powered security scanner for OpenClaw skills"
    )
    parser.add_argument("--version", action="version", version=f"skillguard {VERSION}")

    sub = parser.add_subparsers(dest="command", required=True)

    # scan
    p_scan = sub.add_parser("scan", help="Scan a local skill directory")
    p_scan.add_argument("path", help="Path to skill directory")
    p_scan.set_defaults(func=cmd_scan)

    # install
    p_install = sub.add_parser("install", help="Scan then install a skill from clawhub")
    p_install.add_argument("name", help="Skill slug/name")
    p_install.set_defaults(func=cmd_install)

    # audit
    p_audit = sub.add_parser("audit", help="Scan all installed skills")
    p_audit.add_argument("--dir", dest="audit_dir", default=None,
                         help="Limit audit to a specific skills directory")
    p_audit.add_argument("--limit", type=int, default=None,
                         help="Max number of skills to scan (for testing)")
    p_audit.set_defaults(func=cmd_audit)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
