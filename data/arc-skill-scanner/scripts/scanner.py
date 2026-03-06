#!/usr/bin/env python3
"""Security Scanner for OpenClaw skills.

Scan skills for vulnerabilities before installing them.
Detects credential stealers, data exfiltration, malicious URLs, and more.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

# === Pattern Definitions ===

# Suspicious URL patterns
SUSPICIOUS_URL_PATTERNS = [
    (r'http://(?!localhost|127\.0\.0\.1)', "Non-HTTPS URL found"),
    (r'https?://\d+\.\d+\.\d+\.\d+', "Direct IP address URL"),
    (r'(bit\.ly|tinyurl|t\.co|goo\.gl|is\.gd|buff\.ly|ow\.ly|rebrand\.ly)', "URL shortener detected"),
    (r'(ngrok\.io|serveo\.net|localtunnel\.me|cloudflare-dns\.com)', "Tunneling/proxy service"),
    (r'(pastebin\.com|paste\.ee|ghostbin|hastebin)', "Paste site URL"),
]

# Credential harvesting patterns
CREDENTIAL_PATTERNS = [
    (r'(OPENAI_API_KEY|ANTHROPIC_API_KEY|OPENROUTER_API_KEY|AWS_SECRET|GITHUB_TOKEN|DISCORD_TOKEN)', "Accesses sensitive API keys"),
    (r'os\.environ\[.*(key|token|secret|password|credential)', "Reads sensitive env vars"),
    (r'(\.ssh/|id_rsa|id_ed25519|known_hosts)', "Accesses SSH keys"),
    (r'(\.aws/credentials|\.npmrc|\.netrc|\.gitconfig)', "Accesses credential files"),
    (r'keychain|keyring|credential.store', "Accesses system keychain"),
]

# Data exfiltration patterns
EXFIL_PATTERNS = [
    (r'requests\.post\(|urllib\.request\.urlopen.*POST|fetch\(.*method.*POST', "POSTs data externally"),
    (r'(curl|wget)\s+.*-[dX]\s+POST', "Shell POST request"),
    (r'smtp|sendmail|email\.mime', "Email sending capability"),
    (r'socket\.connect|socket\.create_connection', "Raw socket connection"),
    (r'ftp://|ftplib', "FTP connection"),
]

# Code execution patterns
EXEC_PATTERNS = [
    (r'eval\(|exec\(', "Dynamic code execution (eval/exec)"),
    (r'os\.system\(|subprocess\.(call|run|Popen)', "Shell command execution"),
    (r'subprocess\..*shell\s*=\s*True', "Shell=True in subprocess — RCE risk"),
    (r'__import__\(|importlib\.import_module', "Dynamic module import"),
    (r'compile\(.*exec', "Compiled code execution"),
    (r'ctypes|cffi|ffi\.dlopen', "Native code loading"),
]

# Obfuscation patterns
OBFUSCATION_PATTERNS = [
    (r'base64\.(b64decode|decodebytes)', "Base64 decoding (potential obfuscation)"),
    (r'\\x[0-9a-f]{2}\\x[0-9a-f]{2}\\x[0-9a-f]{2}', "Hex-encoded strings"),
    (r'\\u[0-9a-f]{4}\\u[0-9a-f]{4}', "Unicode-escaped strings"),
    (r'chr\(\d+\)\s*\+\s*chr\(\d+\)', "Character code construction"),
    (r'codecs\.decode\(', "Codec-based decoding"),
    (r'zlib\.decompress|gzip\.decompress', "Compressed payload"),
    (r'marshal\.loads|pickle\.loads', "Serialized code loading"),
]

# Prompt injection patterns (for SKILL.md)
INJECTION_PATTERNS = [
    (r'ignore\s+(previous|all|above)\s+(instructions|prompts)', "Prompt injection: override instructions"),
    (r'(system|admin|root)\s*:?\s*(you are|act as|pretend)', "Prompt injection: role override"),
    (r'do not (tell|reveal|share|disclose)', "Information suppression instruction"),
    (r'(secretly|covertly|silently|without.*(telling|informing|notifying))', "Covert action instruction"),
    (r'<!--|/\*.*\*/|<!--.*-->', "Hidden content in comments"),
]

# Filesystem access patterns
FS_PATTERNS = [
    (r'open\(.*[\'"]/(etc|var|tmp|proc|sys)', "Reads system files"),
    (r'(shutil\.rmtree|os\.remove|os\.unlink).*/', "Deletes files"),
    (r'os\.chmod|os\.chown', "Changes file permissions"),
    (r'(\/root\/|\/home\/[^/]+\/\.)(?!openclaw)', "Accesses home directory hidden files"),
    (r'\.\./\.\./|\.\.[\\/]\.\.[\\/]', "Path traversal pattern (directory escape)"),
    (r'os\.path\.join\(.*\.\.', "Path traversal via os.path.join"),
]

# Crypto patterns
CRYPTO_PATTERNS = [
    (r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}', "Bitcoin address pattern"),
    (r'0x[0-9a-fA-F]{40}', "Ethereum address pattern"),
    (r'(mining|miner|hashrate|cryptonight|xmr)', "Cryptocurrency mining reference"),
]

# Dynamic instruction fetching (supply chain attack vector)
DYNAMIC_FETCH_PATTERNS = [
    (r'(fetch|requests\.get|urllib\.request\.urlopen|curl|wget).*\.(md|txt|yaml|yml|json)', "Fetches remote instructions"),
    (r'(fetch|get|download).*instruction', "Downloads instructions dynamically"),
    (r'(heartbeat|interval|cron|schedule).*fetch', "Periodic remote instruction fetch"),
    (r'eval\(.*requests|eval\(.*fetch|eval\(.*urlopen', "Fetches and executes remote code"),
]

# Telemetry and log leak patterns (data exfil via stdout/logging)
TELEMETRY_PATTERNS = [
    (r'printenv|env\s*\||set\s*\|', "Dumps environment variables to stdout"),
    (r'(print|log|console\.log|sys\.stdout).*environ', "Logs environment variables"),
    (r'(print|log|console\.log).*config', "Logs configuration data"),
    (r'(print|log|console\.log).*(key|token|secret|password)', "Logs sensitive values"),
    (r'logging\.(debug|info).*environ', "Debug-logs environment data"),
    (r'traceback\.print_exc.*|traceback\.format_exc', "Full traceback exposure (may leak paths/secrets)"),
]

# Binary and asset risk patterns
BINARY_ASSET_PATTERNS = [
    (r'\.(exe|dll|so|dylib|bin|wasm)\b', "Contains prebuilt binary — cannot verify source"),
    (r'\.(pyc|pyo|class)\b', "Contains compiled code — cannot audit"),
    (r'chmod\s+\+x|chmod\s+[0-7]*[1357]', "Makes file executable"),
    (r'LD_PRELOAD|DYLD_INSERT_LIBRARIES', "Library injection via environment"),
]

# Binary file extensions that should be checksummed
BINARY_EXTENSIONS = {
    ".exe", ".dll", ".so", ".dylib", ".bin", ".wasm", ".pyc", ".pyo",
    ".class", ".jar", ".war", ".ear", ".deb", ".rpm", ".apk", ".ipa",
    ".tar", ".gz", ".zip", ".7z", ".rar", ".bz2", ".xz",
}

# Known popular skill names (for typosquatting detection)
POPULAR_SKILLS = [
    "discord-helper", "memory-setup", "memory-hygiene", "budget-tracker",
    "security-scanner", "elite-longterm-memory", "skill-scanner", "moltbook",
    "email-podcast", "nightly-build", "mission-control", "swarm", "dispatch",
    "browser-tool", "web-search", "code-review", "git-helper",
]


def classify_severity(finding_type):
    """Classify a finding into a severity level."""
    critical = {"Dynamic code execution", "Serialized code loading", "Native code loading",
                "Prompt injection: override instructions", "Prompt injection: role override",
                "Fetches and executes remote code"}
    high = {"Shell command execution", "Shell=True in subprocess — RCE risk",
            "Accesses SSH keys", "Accesses credential files",
            "Accesses system keychain", "POSTs data externally", "Raw socket connection",
            "Covert action instruction", "Information suppression instruction",
            "Fetches remote instructions", "Downloads instructions dynamically",
            "Periodic remote instruction fetch", "Dumps environment variables to stdout",
            "Logs sensitive values", "Library injection via environment",
            "Contains prebuilt binary — cannot verify source",
            "Path traversal pattern (directory escape)",
            "Path traversal via os.path.join"}
    medium = {"Accesses sensitive API keys", "Reads sensitive env vars", "Base64 decoding",
              "Shell POST request", "Email sending capability", "Dynamic module import",
              "Compiled code execution", "Reads system files", "Deletes files",
              "Changes file permissions", "Accesses home directory hidden files",
              "Logs environment variables", "Logs configuration data",
              "Debug-logs environment data", "Full traceback exposure (may leak paths/secrets)",
              "Contains compiled code — cannot audit", "Makes file executable"}

    if finding_type in critical:
        return "CRITICAL"
    elif finding_type in high:
        return "HIGH"
    elif finding_type in medium:
        return "MEDIUM"
    return "LOW"


def scan_content(content, filename, patterns):
    """Scan content against a set of patterns."""
    findings = []
    for line_num, line in enumerate(content.split("\n"), 1):
        for pattern, desc in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append({
                    "file": filename,
                    "line": line_num,
                    "severity": classify_severity(desc),
                    "description": desc,
                    "match": line.strip()[:120],
                })
    return findings


def scan_skill_md(path):
    """Scan a SKILL.md file for security issues."""
    if not os.path.exists(path):
        return []

    with open(path) as f:
        content = f.read()

    findings = []
    findings.extend(scan_content(content, "SKILL.md", SUSPICIOUS_URL_PATTERNS))
    findings.extend(scan_content(content, "SKILL.md", INJECTION_PATTERNS))
    findings.extend(scan_content(content, "SKILL.md", CREDENTIAL_PATTERNS))

    # Check for excessive metadata requirements
    if "requires" in content:
        env_matches = re.findall(r'"env"\s*:\s*\[([^\]]+)\]', content)
        for match in env_matches:
            keys = [k.strip().strip('"').strip("'") for k in match.split(",")]
            if len(keys) > 5:
                findings.append({
                    "file": "SKILL.md",
                    "line": 0,
                    "severity": "MEDIUM",
                    "description": f"Requests {len(keys)} env vars — excessive permissions",
                    "match": match[:120],
                })

    return findings


def scan_script(path):
    """Scan a script file for security issues."""
    with open(path) as f:
        content = f.read()

    filename = os.path.basename(path)
    findings = []
    findings.extend(scan_content(content, filename, SUSPICIOUS_URL_PATTERNS))
    findings.extend(scan_content(content, filename, CREDENTIAL_PATTERNS))
    findings.extend(scan_content(content, filename, EXFIL_PATTERNS))
    findings.extend(scan_content(content, filename, EXEC_PATTERNS))
    findings.extend(scan_content(content, filename, OBFUSCATION_PATTERNS))
    findings.extend(scan_content(content, filename, FS_PATTERNS))
    findings.extend(scan_content(content, filename, CRYPTO_PATTERNS))
    findings.extend(scan_content(content, filename, DYNAMIC_FETCH_PATTERNS))
    findings.extend(scan_content(content, filename, TELEMETRY_PATTERNS))
    findings.extend(scan_content(content, filename, BINARY_ASSET_PATTERNS))

    return findings


def check_typosquatting(skill_name):
    """Check if a skill name looks like a typosquat of a popular skill."""
    findings = []
    name_lower = skill_name.lower().strip()

    for popular in POPULAR_SKILLS:
        if name_lower == popular:
            continue  # Exact match is fine

        # Check edit distance (Levenshtein distance of 1-2 is suspicious)
        dist = _edit_distance(name_lower, popular)
        if 1 <= dist <= 2:
            findings.append({
                "file": "skill-name",
                "line": 0,
                "severity": "HIGH",
                "description": f"Possible typosquat of '{popular}' (edit distance: {dist})",
                "match": f"Skill name '{skill_name}' is very similar to popular skill '{popular}'",
            })

    return findings


def _edit_distance(s1, s2):
    """Compute Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return _edit_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    prev_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row

    return prev_row[-1]


def checksum_binaries(skill_path, checksum_file=None):
    """Scan for binary/asset files and compute or verify SHA-256 checksums.

    If checksum_file is provided, verify binaries against expected hashes.
    Otherwise, compute and report checksums for all binary/asset files found.
    """
    skill_path = Path(skill_path)
    findings = []
    binaries_found = []

    # Find all binary/asset files
    for root, dirs, files in os.walk(skill_path):
        for f in files:
            fpath = Path(root) / f
            if fpath.suffix.lower() in BINARY_EXTENSIONS:
                rel_path = str(fpath.relative_to(skill_path))
                sha256 = hashlib.sha256(fpath.read_bytes()).hexdigest()
                binaries_found.append({"path": rel_path, "sha256": sha256, "size": fpath.stat().st_size})

    if not binaries_found:
        return findings, binaries_found

    # If a checksum file is provided, verify against it
    if checksum_file and os.path.exists(checksum_file):
        with open(checksum_file) as cf:
            expected = json.load(cf)

        expected_map = {e["path"]: e["sha256"] for e in expected}
        for b in binaries_found:
            if b["path"] not in expected_map:
                findings.append({
                    "file": b["path"],
                    "line": 0,
                    "severity": "HIGH",
                    "description": f"Binary not in checksum manifest — unverified asset ({b['size']} bytes)",
                    "match": f"SHA-256: {b['sha256']}",
                })
            elif b["sha256"] != expected_map[b["path"]]:
                findings.append({
                    "file": b["path"],
                    "line": 0,
                    "severity": "CRITICAL",
                    "description": "Binary checksum MISMATCH — file has been tampered with",
                    "match": f"Expected: {expected_map[b['path']][:32]}... Got: {b['sha256'][:32]}...",
                })
    else:
        # No checksum file — flag all binaries as unverified
        for b in binaries_found:
            findings.append({
                "file": b["path"],
                "line": 0,
                "severity": "HIGH" if b["size"] > 100000 else "MEDIUM",
                "description": f"Unverified binary asset ({b['size']} bytes) — no checksum manifest",
                "match": f"SHA-256: {b['sha256']}",
            })

    return findings, binaries_found


def _is_safe_path(fpath, base_dir):
    """Check that a resolved path stays within the expected base directory.

    Prevents symlink-based directory escapes.
    """
    real_path = os.path.realpath(str(fpath))
    real_base = os.path.realpath(str(base_dir))
    return real_path.startswith(real_base + os.sep) or real_path == real_base


def scan_directory(skill_path, verbose=False, checksum_file=None):
    """Scan an entire skill directory."""
    skill_path = Path(skill_path)
    findings = []

    # Resolve to real path to prevent symlink attacks
    real_skill_path = Path(os.path.realpath(str(skill_path)))

    # Check for typosquatting
    skill_name = skill_path.name
    findings.extend(check_typosquatting(skill_name))

    # Scan SKILL.md
    skill_md = real_skill_path / "SKILL.md"
    if skill_md.exists() and _is_safe_path(skill_md, real_skill_path):
        findings.extend(scan_skill_md(str(skill_md)))
        # Also check for dynamic instruction fetching in SKILL.md
        with open(skill_md) as f:
            content = f.read()
        findings.extend(scan_content(content, "SKILL.md", DYNAMIC_FETCH_PATTERNS))
    else:
        findings.append({
            "file": "SKILL.md",
            "line": 0,
            "severity": "MEDIUM",
            "description": "No SKILL.md found — not a valid skill",
            "match": "",
        })

    # Scan all scripts and code files
    code_extensions = {".py", ".js", ".ts", ".sh", ".bash", ".rb", ".go", ".rs", ".pl"}
    for root, dirs, files in os.walk(real_skill_path, followlinks=False):
        for f in files:
            fpath = Path(root) / f
            # Skip symlinks — prevent reading files outside skill directory
            if fpath.is_symlink():
                findings.append({
                    "file": str(fpath.relative_to(real_skill_path)),
                    "line": 0,
                    "severity": "HIGH",
                    "description": "Symlink detected — potential directory escape",
                    "match": f"→ {os.readlink(str(fpath))}",
                })
                continue
            if fpath.suffix in code_extensions:
                try:
                    findings.extend(scan_script(str(fpath)))
                except Exception as e:
                    if verbose:
                        print(f"  Warning: Could not scan {fpath}: {e}", file=sys.stderr)

    # Checksum verification for binary/asset files
    checksum_findings, binaries = checksum_binaries(skill_path, checksum_file)
    findings.extend(checksum_findings)
    if binaries and verbose:
        print(f"  Found {len(binaries)} binary/asset file(s)", file=sys.stderr)

    return findings


def format_findings(findings, skill_name="", json_output=False):
    """Format and display findings."""
    if json_output:
        result = {
            "skill": skill_name,
            "total_findings": len(findings),
            "findings": findings,
        }
        by_severity = {}
        for f in findings:
            sev = f["severity"]
            by_severity[sev] = by_severity.get(sev, 0) + 1
        result["by_severity"] = by_severity

        critical = by_severity.get("CRITICAL", 0)
        high = by_severity.get("HIGH", 0)
        if critical > 0:
            result["verdict"] = "CRITICAL"
        elif high > 0:
            result["verdict"] = "HIGH"
        elif len(findings) > 0:
            result["verdict"] = "MEDIUM"
        else:
            result["verdict"] = "CLEAN"

        print(json.dumps(result, indent=2))
        return

    if not findings:
        print(f"✅ CLEAN — No security issues detected{f' in {skill_name}' if skill_name else ''}.")
        return

    by_severity = {}
    for f in findings:
        sev = f["severity"]
        by_severity.setdefault(sev, []).append(f)

    critical = len(by_severity.get("CRITICAL", []))
    high = len(by_severity.get("HIGH", []))

    if critical > 0:
        verdict = "🚨 CRITICAL"
    elif high > 0:
        verdict = "⚠️  HIGH RISK"
    else:
        verdict = "⚡ REVIEW NEEDED"

    print(f"{verdict} — {len(findings)} issue(s) found{f' in {skill_name}' if skill_name else ''}")
    print()

    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        items = by_severity.get(severity, [])
        if not items:
            continue
        print(f"  [{severity}] ({len(items)} findings)")
        for item in items:
            loc = f"{item['file']}:{item['line']}" if item['line'] else item['file']
            print(f"    • {item['description']}")
            print(f"      Location: {loc}")
            if item['match']:
                print(f"      Code: {item['match'][:100]}")
        print()


def cmd_scan(args):
    if args.path:
        skill_path = Path(args.path)
        skill_name = skill_path.name
        if args.verbose:
            print(f"Scanning {skill_path}...", file=sys.stderr)
        checksum_file = args.checksum if hasattr(args, 'checksum') else None
        findings = scan_directory(skill_path, verbose=args.verbose, checksum_file=checksum_file)
    elif args.file:
        skill_name = os.path.basename(args.file)
        with open(args.file) as f:
            content = f.read()
        findings = scan_content(content, skill_name, SUSPICIOUS_URL_PATTERNS)
        findings.extend(scan_content(content, skill_name, INJECTION_PATTERNS))
        findings.extend(scan_content(content, skill_name, CREDENTIAL_PATTERNS))
    else:
        print("ERROR: Specify --path or --file", file=sys.stderr)
        sys.exit(1)

    format_findings(findings, skill_name, json_output=args.json)

    # Exit with non-zero if critical/high findings
    critical = sum(1 for f in findings if f["severity"] in ("CRITICAL", "HIGH"))
    if critical > 0:
        sys.exit(1)


def cmd_checksum(args):
    """Generate or verify checksums for binary assets in a skill."""
    skill_path = Path(args.path)
    if not skill_path.exists():
        print(f"ERROR: Path {skill_path} does not exist", file=sys.stderr)
        sys.exit(1)

    if args.verify:
        # Verify mode
        if not os.path.exists(args.verify):
            print(f"ERROR: Checksum file {args.verify} not found", file=sys.stderr)
            sys.exit(1)
        findings, binaries = checksum_binaries(skill_path, args.verify)
        if findings:
            print(f"CHECKSUM VERIFICATION FAILED — {len(findings)} issue(s)")
            for f in findings:
                sev = f["severity"]
                print(f"  [{sev}] {f['file']}: {f['description']}")
            sys.exit(1)
        else:
            print(f"All {len(binaries)} binary checksum(s) verified OK")
    else:
        # Generate mode
        _, binaries = checksum_binaries(skill_path)
        if not binaries:
            print("No binary/asset files found.")
            return
        if args.json:
            print(json.dumps(binaries, indent=2))
        else:
            print(f"Found {len(binaries)} binary/asset file(s):")
            for b in binaries:
                print(f"  {b['path']} ({b['size']} bytes)")
                print(f"    SHA-256: {b['sha256']}")
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(binaries, f, indent=2)
            print(f"\nChecksum manifest written to {args.output}")


def cmd_scan_all(args):
    skill_dirs = [
        Path.home() / ".openclaw" / "skills",
        Path.home() / ".openclaw" / "workspace" / "skills",
    ]

    total_findings = 0
    results = []

    for base_dir in skill_dirs:
        if not base_dir.exists():
            continue
        for skill_path in sorted(base_dir.iterdir()):
            if not skill_path.is_dir():
                continue
            skill_name = skill_path.name
            findings = scan_directory(skill_path)
            total_findings += len(findings)
            results.append({"name": skill_name, "path": str(skill_path), "findings": findings})

    if args.json:
        print(json.dumps({"skills_scanned": len(results), "total_findings": total_findings, "results": results}, indent=2))
    else:
        print(f"Scanned {len(results)} installed skills\n")
        for r in results:
            if r["findings"]:
                format_findings(r["findings"], r["name"])
            else:
                print(f"✅ {r['name']} — CLEAN")
        print(f"\nTotal: {total_findings} issue(s) across {len(results)} skills")


def main():
    parser = argparse.ArgumentParser(description="Security Scanner for OpenClaw skills")
    sub = parser.add_subparsers(dest="command")

    p_scan = sub.add_parser("scan", help="Scan a skill")
    p_scan.add_argument("--path", help="Path to skill directory")
    p_scan.add_argument("--file", help="Path to a single file to scan")
    p_scan.add_argument("--checksum", help="Path to checksum manifest JSON for binary verification")
    p_scan.add_argument("--verbose", action="store_true")
    p_scan.add_argument("--json", action="store_true")

    p_all = sub.add_parser("scan-all", help="Scan all installed skills")
    p_all.add_argument("--json", action="store_true")

    p_chk = sub.add_parser("checksum", help="Generate or verify checksums for binary assets")
    p_chk.add_argument("--path", required=True, help="Path to skill directory")
    p_chk.add_argument("--verify", help="Path to checksum manifest to verify against")
    p_chk.add_argument("--output", "-o", help="Write checksum manifest to this file")
    p_chk.add_argument("--json", action="store_true")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    {"scan": cmd_scan, "scan-all": cmd_scan_all, "checksum": cmd_checksum}[args.command](args)


if __name__ == "__main__":
    main()
