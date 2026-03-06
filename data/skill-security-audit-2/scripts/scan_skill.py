#!/usr/bin/env python3
"""
ClawHub Skill Security Scanner

Performs automated static analysis on a ClawHub skill directory to detect
potential security risks before installation. Outputs a structured JSON report.

Usage:
    # Scan a local skill directory
    python3 scan_skill.py <skill-directory-path>

    # Download from ClawHub first, then scan (auto-cleanup)
    python3 scan_skill.py --slug <skill-slug>

    # Download a specific version
    python3 scan_skill.py --slug <skill-slug> --version 1.3.0

Exit codes:
    0 - Scan completed (check report for findings)
    1 - Invalid arguments or skill directory not found
    2 - Failed to download skill from ClawHub
"""

import sys
import os
import re
import json
import hashlib
import shutil
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# ---------------------------------------------------------------------------
# Risk patterns
# ---------------------------------------------------------------------------

# High-severity patterns: strong indicators of malicious intent
HIGH_RISK_PATTERNS = [
    # Remote code execution
    (r'curl\s+.*\|\s*(ba)?sh', "Remote code execution via curl pipe to shell"),
    (r'wget\s+.*\|\s*(ba)?sh', "Remote code execution via wget pipe to shell"),
    (r'curl\s+.*-[oO]\s+.*&&\s*(ba)?sh', "Download-and-execute pattern"),
    (r'wget\s+.*-O\s+.*&&\s*(ba)?sh', "Download-and-execute pattern"),
    (r'curl\s+-fsSL\s+http', "Silent download from HTTP (insecure) source"),

    # Base64 / encoding obfuscation
    (r'base64\s+-[dD]', "Base64 decoding (common obfuscation technique)"),
    (r'base64\s+--decode', "Base64 decoding (common obfuscation technique)"),
    (r"echo\s+['\"]?[A-Za-z0-9+/=]{40,}['\"]?\s*\|\s*base64", "Base64 encoded payload execution"),
    (r'\\x[0-9a-fA-F]{2}(\\x[0-9a-fA-F]{2}){5,}', "Hex-encoded string (potential obfuscation)"),
    (r'eval\s*\(', "Dynamic code evaluation via eval()"),
    (r'exec\s*\(', "Dynamic code execution via exec()"),
    (r'subprocess\.call\s*\(.*shell\s*=\s*True', "Shell command execution with shell=True"),
    (r'os\.system\s*\(', "OS-level command execution"),
    (r'os\.popen\s*\(', "OS-level command execution via popen"),

    # Credential / data exfiltration
    (r'(SSH|RSA|PRIVATE)\s*KEY', "References to private keys"),
    (r'~/.ssh/', "Accesses SSH directory"),
    (r'keychain', "Accesses macOS Keychain"),
    (r'/etc/passwd', "Accesses system password file"),
    (r'/etc/shadow', "Accesses system shadow password file"),
    (r'GITHUB_TOKEN|GH_TOKEN|OPENAI_API_KEY|AWS_SECRET|CLAWHUB_TOKEN', "References sensitive tokens/API keys"),
    (r'\.env\b', "Accesses .env file (may contain secrets)"),

    # Network exfiltration
    (r'nc\s+-[elpvw]', "Netcat usage (potential reverse shell)"),
    (r'/dev/tcp/', "Bash TCP device (potential reverse shell)"),
    (r'mkfifo', "Named pipe creation (potential reverse shell component)"),
    (r'ngrok', "Ngrok tunnel (potential data exfiltration channel)"),

    # Persistence mechanisms
    (r'crontab', "Crontab modification (persistence mechanism)"),
    (r'launchctl', "macOS launchctl (persistence mechanism)"),
    (r'LaunchAgents|LaunchDaemons', "macOS launch agent/daemon (persistence mechanism)"),
    (r'/etc/rc\.local', "System startup script modification"),
    (r'systemctl\s+enable', "Systemd service enabling (persistence)"),
    (r'chmod\s+[0-7]*[1357][0-7]*\s', "Setting executable permissions (SUID/SGID risk)"),
    (r'chmod\s+\+s\s', "Setting SUID/SGID bit"),
]

# Medium-severity patterns: suspicious but may have legitimate uses
MEDIUM_RISK_PATTERNS = [
    # Prompt injection / agent manipulation
    (r'(?i)(you\s+must|you\s+should|you\s+need\s+to)\s+(run|execute|install|download|open|visit|click)', "Directive language targeting AI agent"),
    (r'(?i)prerequisite.*\b(run|execute|install|download)\b', "Prerequisites section with execution directives"),
    (r'(?i)(open|visit|go\s+to|navigate\s+to)\s+https?://', "Directs user/agent to visit external URL"),
    (r'(?i)copy\s+(and|&)\s+(paste|run)', "Instructs copy-and-paste execution"),
    (r'(?i)paste\s+(this|the\s+following)\s+(in|into)\s+(your\s+)?terminal', "Instructs pasting commands into terminal"),
    (r'(?i)ignore\s+(previous|above|all)\s+(instructions?|prompts?|rules?)', "Prompt injection: ignore previous instructions"),
    (r'(?i)disregard\s+(everything|all|any)\s+(above|before|previous)', "Prompt injection: disregard previous context"),
    (r'(?i)new\s+instructions?\s*:', "Prompt injection: new instructions override"),
    (r'(?i)system\s*:\s', "Prompt injection: system message impersonation"),

    # Suspicious external resources
    (r'rentry\.co|pastebin\.com|paste\.ee|hastebin\.com|0bin\.net', "References anonymous paste service (common malware hosting)"),
    (r'bit\.ly|tinyurl|t\.co|is\.gd|buff\.ly|ow\.ly|shorturl', "Shortened URL (hides true destination)"),
    (r'raw\.githubusercontent\.com', "Direct raw GitHub content download"),
    (r'gist\.github\.com', "References GitHub Gist (may contain unreviewed code)"),

    # File system operations
    (r'rm\s+-rf\s+[~/]', "Recursive force deletion on home/root directory"),
    (r'rm\s+-rf\s+/(?!tmp)', "Recursive force deletion on system directory"),
    (r'>\s*/dev/null\s+2>&1', "Output suppression (hiding command results)"),
    (r'chmod\s+777', "World-writable permissions"),
    (r'sudo\s', "Requests elevated privileges"),
    (r'pip\s+install\s+(?!--)', "Installs Python packages (dependency risk)"),
    (r'npm\s+install\s+(?!--)', "Installs Node packages (dependency risk)"),
    (r'brew\s+install', "Installs Homebrew packages"),
    (r'apt(-get)?\s+install', "Installs system packages"),

    # Crypto / wallet targeting
    (r'(?i)(wallet|seed\s*phrase|mnemonic|private\s*key|recovery\s*phrase)', "References cryptocurrency wallet/keys"),
    (r'(?i)(bitcoin|ethereum|solana|metamask|phantom|ledger)', "References cryptocurrency platforms"),
]

# Low-severity patterns: informational, warrant attention
LOW_RISK_PATTERNS = [
    (r'https?://(?!github\.com|docs\.|stackoverflow\.com|clawhub\.com|npmjs\.com|pypi\.org)\S+', "External URL to non-standard domain"),
    (r'(?i)(password|token|secret|credential|api[_-]?key)\s*[:=]', "Hardcoded credential assignment"),
    (r'(?i)TODO|FIXME|HACK|XXX', "Code quality marker (may indicate incomplete implementation)"),
    (r'(?i)deprecated|experimental|unstable|alpha|beta', "Stability warning markers"),
    (r'\\u[0-9a-fA-F]{4}', "Unicode escape sequences (potential text obfuscation)"),
]

# ---------------------------------------------------------------------------
# Structural checks
# ---------------------------------------------------------------------------

def check_skill_structure(skill_dir: Path) -> list:
    """Validate the structural integrity and hygiene of the skill directory."""
    findings = []
    skill_md = skill_dir / "SKILL.md"

    # Check SKILL.md exists
    if not skill_md.exists():
        findings.append({
            "severity": "CRITICAL",
            "category": "structure",
            "message": "Missing SKILL.md - this is not a valid skill",
            "file": "SKILL.md",
        })
        return findings

    # Check SKILL.md frontmatter
    content = skill_md.read_text(encoding="utf-8", errors="replace")
    if not content.startswith("---"):
        findings.append({
            "severity": "HIGH",
            "category": "structure",
            "message": "SKILL.md missing YAML frontmatter",
            "file": "SKILL.md",
        })
    else:
        fm_end = content.find("---", 3)
        if fm_end == -1:
            findings.append({
                "severity": "HIGH",
                "category": "structure",
                "message": "SKILL.md has malformed YAML frontmatter (no closing ---)",
                "file": "SKILL.md",
            })
        else:
            frontmatter = content[3:fm_end]
            if "name:" not in frontmatter:
                findings.append({
                    "severity": "MEDIUM",
                    "category": "structure",
                    "message": "SKILL.md frontmatter missing 'name' field",
                    "file": "SKILL.md",
                })
            if "description:" not in frontmatter:
                findings.append({
                    "severity": "MEDIUM",
                    "category": "structure",
                    "message": "SKILL.md frontmatter missing 'description' field",
                    "file": "SKILL.md",
                })

    # Check for suspicious file types
    suspicious_extensions = {
        ".exe", ".dll", ".so", ".dylib", ".bin", ".dat",
        ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".apk",
        ".jar", ".war", ".class",
        ".scr", ".bat", ".cmd", ".com", ".vbs", ".vbe",
        ".ps1", ".psm1", ".psd1",
        ".app", ".ipa",
    }
    for path in skill_dir.rglob("*"):
        if path.is_file():
            ext = path.suffix.lower()
            if ext in suspicious_extensions:
                findings.append({
                    "severity": "HIGH",
                    "category": "structure",
                    "message": f"Suspicious binary/executable file type: {ext}",
                    "file": str(path.relative_to(skill_dir)),
                })
            # Large files (> 1MB) are unusual for a skill
            size = path.stat().st_size
            if size > 1_048_576:
                findings.append({
                    "severity": "MEDIUM",
                    "category": "structure",
                    "message": f"Unusually large file ({size / 1_048_576:.1f} MB)",
                    "file": str(path.relative_to(skill_dir)),
                })

    # Count total files
    all_files = list(skill_dir.rglob("*"))
    file_count = sum(1 for f in all_files if f.is_file())
    if file_count > 50:
        findings.append({
            "severity": "LOW",
            "category": "structure",
            "message": f"Skill contains {file_count} files (unusually large for a skill)",
            "file": str(skill_dir),
        })

    return findings


# ---------------------------------------------------------------------------
# Content scanning
# ---------------------------------------------------------------------------

def scan_file_content(filepath: Path, skill_dir: Path) -> list:
    """Scan a single text file for risk patterns."""
    findings = []
    rel_path = str(filepath.relative_to(skill_dir))

    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return findings

    lines = content.split("\n")

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        for pattern, description in HIGH_RISK_PATTERNS:
            if re.search(pattern, line):
                findings.append({
                    "severity": "HIGH",
                    "category": "content",
                    "message": description,
                    "file": rel_path,
                    "line": line_num,
                    "matched_text": stripped[:120],
                })

        for pattern, description in MEDIUM_RISK_PATTERNS:
            if re.search(pattern, line):
                findings.append({
                    "severity": "MEDIUM",
                    "category": "content",
                    "message": description,
                    "file": rel_path,
                    "line": line_num,
                    "matched_text": stripped[:120],
                })

        for pattern, description in LOW_RISK_PATTERNS:
            if re.search(pattern, line):
                findings.append({
                    "severity": "LOW",
                    "category": "content",
                    "message": description,
                    "file": rel_path,
                    "line": line_num,
                    "matched_text": stripped[:120],
                })

    return findings


# ---------------------------------------------------------------------------
# File hash inventory
# ---------------------------------------------------------------------------

def compute_file_hashes(skill_dir: Path) -> list:
    """Compute SHA-256 hashes for all files in the skill for integrity tracking."""
    inventory = []
    for path in sorted(skill_dir.rglob("*")):
        if path.is_file():
            sha = hashlib.sha256(path.read_bytes()).hexdigest()
            inventory.append({
                "file": str(path.relative_to(skill_dir)),
                "size_bytes": path.stat().st_size,
                "sha256": sha,
            })
    return inventory


# ---------------------------------------------------------------------------
# Safe ZIP extraction (Zip Slip / path traversal protection)
# ---------------------------------------------------------------------------

class _ZipPathTraversalError(Exception):
    """Raised when a ZIP entry attempts path traversal outside the target directory."""


def safe_extract(zf: zipfile.ZipFile, target_dir: Path) -> None:
    """Extract all members of a ZipFile with path traversal protection.

    For each entry, resolves the final destination path and verifies it falls
    within *target_dir*. Raises _ZipPathTraversalError if any entry attempts
    to escape via ``../`` or absolute paths — a technique known as "Zip Slip".
    """
    target_dir = target_dir.resolve()
    for member in zf.infolist():
        # Normalise the member filename and resolve against target_dir
        member_path = (target_dir / Path(member.filename)).resolve()
        # Ensure the resolved path is inside the target directory
        if not str(member_path).startswith(str(target_dir) + os.sep) and member_path != target_dir:
            raise _ZipPathTraversalError(
                f"Zip Slip detected — entry '{member.filename}' resolves to "
                f"'{member_path}' which is outside target directory '{target_dir}'. "
                f"This ZIP archive may be maliciously crafted."
            )
    # All entries validated — safe to extract
    zf.extractall(target_dir)


# ---------------------------------------------------------------------------
# ClawHub download helper (pure Python, no external dependencies)
# ---------------------------------------------------------------------------

CLAWHUB_API_BASE = "https://clawhub.ai/api/v1"


def download_from_clawhub(slug: str, version: str | None = None) -> tuple[Path, Path]:
    """Download a skill from ClawHub into a temporary directory using REST API.

    Uses ClawHub public API:
      1. GET /api/v1/skills/<slug>  — resolve metadata & latest version
      2. GET /api/v1/download       — download the zip package

    Returns (skill_path, tmp_root) where tmp_root is the temp dir to clean up.
    Raises SystemExit on failure.
    """
    tmp_dir = Path(tempfile.mkdtemp(prefix="skill-audit-"))

    # Step 1: Fetch skill metadata
    meta_url = f"{CLAWHUB_API_BASE}/skills/{slug}"
    print(f"Fetching metadata for '{slug}' from ClawHub...", file=sys.stderr)
    try:
        req = Request(meta_url, headers={"Accept": "application/json", "User-Agent": "skill-security-audit/1.3.0"})
        with urlopen(req, timeout=30) as resp:
            meta = json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        if e.code == 404:
            print(f"Error: Skill '{slug}' not found on ClawHub.", file=sys.stderr)
        else:
            print(f"Error: ClawHub API returned HTTP {e.code} for '{slug}'.", file=sys.stderr)
        sys.exit(2)
    except (URLError, OSError) as e:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        print(f"Error: Failed to connect to ClawHub API.\n{e}", file=sys.stderr)
        sys.exit(2)

    # Step 2: Build download URL
    download_url = f"{CLAWHUB_API_BASE}/download?slug={slug}"
    if version:
        download_url += f"&version={version}"

    print(f"Downloading skill package...", file=sys.stderr)
    zip_path = tmp_dir / f"{slug}.zip"
    try:
        req = Request(download_url, headers={"User-Agent": "skill-security-audit/1.3.0"})
        with urlopen(req, timeout=120) as resp:
            zip_path.write_bytes(resp.read())
    except HTTPError as e:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        print(f"Error: Failed to download skill '{slug}' (HTTP {e.code}).", file=sys.stderr)
        sys.exit(2)
    except (URLError, OSError) as e:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        print(f"Error: Download failed.\n{e}", file=sys.stderr)
        sys.exit(2)

    # Step 3: Extract zip (with Zip Slip / path traversal protection)
    extract_dir = tmp_dir / "extracted"
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            safe_extract(zf, extract_dir)
    except zipfile.BadZipFile:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        print(f"Error: Downloaded file for '{slug}' is not a valid zip archive.", file=sys.stderr)
        sys.exit(2)
    except _ZipPathTraversalError as e:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        print(f"SECURITY ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    # Step 4: Locate the skill directory (may be nested inside the zip)
    # Search for SKILL.md to find the actual skill root
    for md_path in extract_dir.rglob("SKILL.md"):
        skill_dir = md_path.parent
        print(f"Downloaded and extracted to: {skill_dir}", file=sys.stderr)
        return skill_dir, tmp_dir

    # Fallback: if only one subdirectory exists, use it
    subdirs = [d for d in extract_dir.iterdir() if d.is_dir()]
    if len(subdirs) == 1:
        print(f"Downloaded and extracted to: {subdirs[0]}", file=sys.stderr)
        return subdirs[0], tmp_dir

    # Last fallback: use extract_dir itself
    if any(extract_dir.iterdir()):
        print(f"Downloaded and extracted to: {extract_dir}", file=sys.stderr)
        return extract_dir, tmp_dir

    shutil.rmtree(tmp_dir, ignore_errors=True)
    print(f"Error: Could not locate skill directory after downloading '{slug}'.", file=sys.stderr)
    sys.exit(2)


# ---------------------------------------------------------------------------
# Core scan logic
# ---------------------------------------------------------------------------

def scan_skill(skill_path: Path) -> dict:
    """Run full security scan on a skill directory. Returns the report dict."""
    findings = []

    # 1. Structural checks
    findings.extend(check_skill_structure(skill_path))

    # 2. Content scanning
    text_extensions = {
        ".md", ".txt", ".py", ".sh", ".bash", ".zsh",
        ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
        ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
        ".html", ".htm", ".css", ".xml", ".svg",
        ".rb", ".go", ".rs", ".java", ".kt", ".swift",
        ".c", ".cpp", ".h", ".hpp",
        ".r", ".sql", ".lua", ".pl", ".php",
        "",  # files with no extension (e.g., Makefile, Dockerfile)
    }
    for path in skill_path.rglob("*"):
        if path.is_file() and path.suffix.lower() in text_extensions:
            findings.extend(scan_file_content(path, skill_path))

    # 3. File inventory
    file_inventory = compute_file_hashes(skill_path)

    # 4. Deduplicate findings
    seen = set()
    unique_findings = []
    for f in findings:
        key = (f["severity"], f["message"], f.get("file", ""), f.get("line", 0))
        if key not in seen:
            seen.add(key)
            unique_findings.append(f)

    # 5. Build report
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    unique_findings.sort(key=lambda x: (severity_order.get(x["severity"], 99), x.get("file", "")))

    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in unique_findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1

    report = {
        "scan_metadata": {
            "tool": "skill-security-audit/scan_skill.py",
            "version": "1.3.0",
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            "skill_directory": str(skill_path),
            "skill_name": skill_path.name,
        },
        "summary": {
            "total_findings": len(unique_findings),
            "by_severity": counts,
            "total_files_scanned": len(file_inventory),
        },
        "findings": unique_findings,
        "file_inventory": file_inventory,
    }
    return report


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args(argv: list[str]):
    """Minimal argument parser to avoid external dependencies.

    Supports:
        scan_skill.py <local-directory>
        scan_skill.py --slug <slug> [--version <ver>]
    """
    slug = None
    version = None
    local_path = None

    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg == "--slug":
            if i + 1 >= len(argv):
                print("Error: --slug requires a value", file=sys.stderr)
                sys.exit(1)
            slug = argv[i + 1]
            i += 2
        elif arg == "--version":
            if i + 1 >= len(argv):
                print("Error: --version requires a value", file=sys.stderr)
                sys.exit(1)
            version = argv[i + 1]
            i += 2
        elif arg.startswith("-"):
            print(f"Error: Unknown option '{arg}'", file=sys.stderr)
            sys.exit(1)
        else:
            local_path = arg
            i += 1

    if slug and local_path:
        print("Error: Provide either --slug or a local path, not both", file=sys.stderr)
        sys.exit(1)

    if not slug and not local_path:
        print(
            "Usage:\n"
            "  python3 scan_skill.py <skill-directory-path>\n"
            "  python3 scan_skill.py --slug <clawhub-slug> [--version <ver>]",
            file=sys.stderr,
        )
        sys.exit(1)

    return slug, version, local_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    slug, version, local_path = parse_args(sys.argv)

    tmp_root = None  # track temp dir for cleanup

    if slug:
        # Download from ClawHub via REST API (pure Python, no Node.js needed)
        skill_path, tmp_root = download_from_clawhub(slug, version)
    else:
        skill_path = Path(local_path).resolve()
        if not skill_path.is_dir():
            print(f"Error: '{skill_path}' is not a directory", file=sys.stderr)
            sys.exit(1)

    try:
        report = scan_skill(skill_path)

        # Add source info to metadata
        if slug:
            report["scan_metadata"]["source"] = "clawhub"
            report["scan_metadata"]["slug"] = slug
            if version:
                report["scan_metadata"]["requested_version"] = version
        else:
            report["scan_metadata"]["source"] = "local"

        print(json.dumps(report, indent=2, ensure_ascii=False))
    finally:
        # Clean up temp directory if we downloaded from ClawHub
        if tmp_root and tmp_root.exists():
            shutil.rmtree(tmp_root, ignore_errors=True)
            print(f"Cleaned up temporary directory: {tmp_root}", file=sys.stderr)


if __name__ == "__main__":
    main()
