#!/usr/bin/env python3
"""
claw-skill-guard — Security scanner for OpenClaw skills

Scans skills for malware patterns, suspicious URLs, and install traps.

Usage:
    python3 scanner.py scan <path-or-url>
    python3 scanner.py scan-all <directory>
    python3 scanner.py check-url <url>
"""

import os
import sys
import re
import json
import tempfile
import zipfile
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from pathlib import Path

# Risk levels
CRITICAL = "critical"
HIGH = "high"
MEDIUM = "medium"
LOW = "low"

# Get the directory where this script lives
SCRIPT_DIR = Path(__file__).parent.parent
PATTERNS_DIR = SCRIPT_DIR / "patterns"


def load_patterns():
    """Load patterns from JSON files."""
    patterns = {}
    
    for level in [CRITICAL, HIGH, MEDIUM, LOW]:
        pattern_file = PATTERNS_DIR / f"{level}.json"
        if pattern_file.exists():
            with open(pattern_file, "r") as f:
                data = json.load(f)
                patterns[level] = data.get("patterns", [])
        else:
            patterns[level] = []
    
    return patterns


def load_allowlist():
    """Load allowlist from JSON file."""
    allowlist_file = PATTERNS_DIR / "allowlist.json"
    if allowlist_file.exists():
        with open(allowlist_file, "r") as f:
            return json.load(f)
    return {"urls": [], "npm_packages": [], "pip_packages": []}


# Load patterns and allowlist
PATTERNS = load_patterns()
ALLOWLIST = load_allowlist()


def is_allowlisted(value, allowlist_key):
    """Check if a value matches any allowlist pattern."""
    if allowlist_key not in ALLOWLIST:
        return False
    for pattern in ALLOWLIST[allowlist_key]:
        if re.search(pattern, value, re.IGNORECASE):
            return True
    return False


def scan_content(content, filename=""):
    """Scan content for suspicious patterns."""
    findings = {CRITICAL: [], HIGH: [], MEDIUM: [], LOW: []}
    lines = content.split("\n")
    
    for line_num, line in enumerate(lines, 1):
        # Skip empty lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
            
        for risk_level, patterns in PATTERNS.items():
            for pattern_info in patterns:
                try:
                    matches = re.finditer(pattern_info["pattern"], line, re.IGNORECASE)
                    for match in matches:
                        matched_text = match.group(0)
                        
                        # Check allowlist if applicable
                        if "check_allowlist" in pattern_info:
                            if is_allowlisted(matched_text, pattern_info["check_allowlist"]):
                                continue
                        
                        findings[risk_level].append({
                            "file": filename,
                            "line": line_num,
                            "pattern": pattern_info["name"],
                            "matched": matched_text[:100],  # Truncate long matches
                            "description": pattern_info["description"],
                            "context": line.strip()[:150]
                        })
                except re.error as e:
                    # Skip invalid regex patterns
                    continue
    
    return findings


def scan_directory(path):
    """Scan all markdown and script files in a directory."""
    all_findings = {CRITICAL: [], HIGH: [], MEDIUM: [], LOW: []}
    
    path = Path(path)
    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        sys.exit(1)
    
    # File extensions to scan
    extensions = {".md", ".sh", ".py", ".js", ".ts"}
    
    for file_path in path.rglob("*"):
        if file_path.suffix.lower() in extensions:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                findings = scan_content(content, str(file_path.relative_to(path)))
                for level in all_findings:
                    all_findings[level].extend(findings[level])
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
    
    return all_findings


def fetch_clawhub_skill(slug):
    """Fetch a skill from ClawHub and return its contents."""
    # ClawHub API endpoint for downloading skills
    # Format: https://clawhub.com/api/skills/{owner}/{name}/download or similar
    
    # Try to get skill info first
    api_url = f"https://clawhub.ai/api/skills/{slug}"
    
    try:
        req = Request(api_url, headers={"User-Agent": "claw-skill-guard/1.0"})
        with urlopen(req, timeout=30) as response:
            skill_info = json.loads(response.read().decode("utf-8"))
            
            # Try to get download URL
            if "downloadUrl" in skill_info:
                download_url = skill_info["downloadUrl"]
            else:
                # Fallback to standard download path
                download_url = f"https://clawhub.ai/api/skills/{slug}/download"
            
            # Download the skill zip
            req = Request(download_url, headers={"User-Agent": "claw-skill-guard/1.0"})
            with urlopen(req, timeout=60) as dl_response:
                # Save to temp file and extract
                with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                    tmp.write(dl_response.read())
                    tmp_path = tmp.name
                
                # Extract to temp directory
                extract_dir = tempfile.mkdtemp()
                with zipfile.ZipFile(tmp_path, "r") as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                os.unlink(tmp_path)
                return extract_dir
                
    except HTTPError as e:
        if e.code == 404:
            print(f"Error: Skill not found: {slug}")
        else:
            print(f"Error fetching skill: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def fetch_remote_skill(url):
    """Fetch a skill from a remote URL and scan it."""
    # Handle ClawHub URLs
    if "clawhub.com" in url or "clawhub.ai" in url:
        # Extract slug from URL (e.g., clawhub.ai/owner/skill-name)
        parts = url.rstrip("/").split("/")
        if len(parts) >= 2:
            slug = f"{parts[-2]}/{parts[-1]}"
            temp_dir = fetch_clawhub_skill(slug)
            if temp_dir:
                return ("directory", temp_dir)
        return None
    
    # Handle GitHub URLs
    if "github.com" in url:
        if "/blob/" in url:
            url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        elif "/tree/" in url:
            # Can't easily fetch a directory from GitHub, suggest cloning
            print("Note: For GitHub directories, consider cloning locally first.")
            print(f"  git clone {url.split('/tree/')[0]}")
            return None
    
    try:
        req = Request(url, headers={"User-Agent": "claw-skill-guard/1.0"})
        with urlopen(req, timeout=30) as response:
            content = response.read().decode("utf-8")
            return ("content", content)
    except URLError as e:
        print(f"Error fetching URL: {e}")
        return None


def calculate_risk_level(findings):
    """Calculate overall risk level from findings."""
    if findings[CRITICAL]:
        return CRITICAL
    if findings[HIGH]:
        return HIGH
    if findings[MEDIUM]:
        return MEDIUM
    if findings[LOW]:
        return LOW
    return "safe"


def print_report(findings, source):
    """Print a formatted security report."""
    risk_level = calculate_risk_level(findings)
    total_findings = sum(len(f) for f in findings.values())
    
    print(f"\n🔍 Scanning: {source}")
    print("━" * 50)
    
    # Risk level banner
    risk_colors = {
        CRITICAL: "🔴 CRITICAL",
        HIGH: "🟡 HIGH", 
        MEDIUM: "🟠 MEDIUM",
        LOW: "🟢 LOW",
        "safe": "✅ SAFE"
    }
    print(f"\n⚠️  RISK LEVEL: {risk_colors.get(risk_level, risk_level).upper()}")
    
    if total_findings == 0:
        print("\n✅ No suspicious patterns found.")
        print("\n" + "━" * 50)
        print("✅ RECOMMENDATION: Safe to install")
        return 0
    
    print(f"\n📋 Findings ({total_findings} total):\n")
    
    for level in [CRITICAL, HIGH, MEDIUM, LOW]:
        if findings[level]:
            level_icon = {"critical": "🔴", "high": "🟡", "medium": "🟠", "low": "🟢"}[level]
            print(f"  {level_icon} {level.upper()} ({len(findings[level])})")
            
            for i, finding in enumerate(findings[level]):
                prefix = "  ├─" if i < len(findings[level]) - 1 else "  └─"
                file_info = f"{finding['file']}:" if finding['file'] else ""
                print(f"{prefix} Line {finding['line']}: {finding['matched']}")
                print(f"  │  └─ {finding['description']}")
            print()
    
    print("━" * 50)
    
    if risk_level == CRITICAL:
        print("\n❌ RECOMMENDATION: DO NOT INSTALL")
        print("   This skill contains patterns commonly used in malware.")
        return 2
    elif risk_level == HIGH:
        print("\n⚠️  RECOMMENDATION: MANUAL REVIEW REQUIRED")
        print("   Review each flagged line. Only install if you trust the author")
        print("   and understand what each command does.")
        return 1
    elif risk_level == MEDIUM:
        print("\n⚠️  RECOMMENDATION: Review flagged items")
        print("   Likely safe, but verify the URLs and commands are expected.")
        return 0
    else:
        print("\n✅ RECOMMENDATION: Low risk, likely safe to install")
        return 0


def cleanup_temp_dir(path):
    """Clean up temporary directory."""
    import shutil
    try:
        shutil.rmtree(path)
    except:
        pass


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "scan":
        if len(sys.argv) < 3:
            print("Usage: scanner.py scan <path-or-url>")
            sys.exit(1)
        
        target = sys.argv[2]
        temp_dir = None
        
        if target.startswith("http://") or target.startswith("https://"):
            # Remote URL
            result = fetch_remote_skill(target)
            if result:
                result_type, result_data = result
                if result_type == "directory":
                    temp_dir = result_data
                    findings = scan_directory(temp_dir)
                    exit_code = print_report(findings, target)
                    cleanup_temp_dir(temp_dir)
                    sys.exit(exit_code)
                else:
                    findings = scan_content(result_data, target)
                    exit_code = print_report(findings, target)
                    sys.exit(exit_code)
            else:
                print("Failed to fetch remote skill")
                sys.exit(1)
        else:
            # Local path
            path = Path(target)
            if path.is_file():
                content = path.read_text(encoding="utf-8", errors="ignore")
                findings = scan_content(content, path.name)
            else:
                findings = scan_directory(target)
            
            exit_code = print_report(findings, target)
            sys.exit(exit_code)
    
    elif command == "scan-all":
        if len(sys.argv) < 3:
            print("Usage: scanner.py scan-all <directory>")
            sys.exit(1)
        
        directory = sys.argv[2]
        skills_dir = Path(directory)
        
        if not skills_dir.is_dir():
            print(f"Error: {directory} is not a directory")
            sys.exit(1)
        
        print(f"🔍 Scanning all skills in: {directory}\n")
        
        exit_code = 0
        for skill_path in sorted(skills_dir.iterdir()):
            if skill_path.is_dir() and not skill_path.name.startswith("."):
                findings = scan_directory(skill_path)
                result = print_report(findings, skill_path.name)
                exit_code = max(exit_code, result)
                print()
        
        sys.exit(exit_code)
    
    elif command == "check-url":
        if len(sys.argv) < 3:
            print("Usage: scanner.py check-url <url>")
            sys.exit(1)
        
        url = sys.argv[2]
        if is_allowlisted(url, "urls"):
            print(f"✅ URL is allowlisted: {url}")
        else:
            print(f"⚠️  URL is NOT in allowlist: {url}")
            print("   This doesn't mean it's malicious, just unknown.")
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
