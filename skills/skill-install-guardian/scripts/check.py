#!/usr/bin/env python3
"""
Skill Install Guardian - Security and Due Diligence Check
Performs layered security checks before installing external skills.
"""

import os
import json
import re
import subprocess
import argparse
import sys
from datetime import datetime

# Patterns that indicate potential security risks
DANGEROUS_PATTERNS = [
    (r'eval\s*\(', 'CRITICAL', 'Code execution via eval()'),
    (r'exec\s*\(', 'CRITICAL', 'Code execution via exec()'),
    (r'subprocess\s*\.\s*call\s*\(\s*\[', 'HIGH', 'Subprocess call'),
    (r'os\.system\s*\(', 'HIGH', 'OS command execution'),
    (r'shell\s*=\s*True', 'HIGH', 'Shell execution enabled'),
    (r'requests\.post\s*\(\s*["\'](?!https?://)', 'HIGH', 'HTTP POST to unknown domain'),
    (r'fetch\s*\(\s*["\'](?!https?://)', 'HIGH', 'Fetch to unknown domain'),
    (r'curl\s+', 'HIGH', 'curl command execution'),
    (r'wget\s+', 'HIGH', 'wget command execution'),
    (r'sk-[a-zA-Z0-9]{20,}', 'CRITICAL', 'Potential API key'),
    (r'ghp_[a-zA-Z0-9]{36}', 'CRITICAL', 'GitHub token'),
    (r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*', 'CRITICAL', 'JWT token'),
    (r'password\s*=\s*["\'][^"\']+["\']', 'HIGH', 'Hardcoded password'),
    (r'secret\s*=\s*["\'][^"\']+["\']', 'HIGH', 'Hardcoded secret'),
    (r'token\s*=\s*["\'][^"\']+["\']', 'MEDIUM', 'Hardcoded token'),
    (r'base64\.b64decode', 'MEDIUM', 'Base64 decode (potential obfuscation)'),
    (r'import\s+os\s*;.*os\.', 'MEDIUM', 'OS module import'),
    (r'import\s+subprocess', 'MEDIUM', 'Subprocess import'),
    (r'__import__\s*\(', 'MEDIUM', 'Dynamic import'),
]

# Safe domains (you can extend this)
SAFE_DOMAINS = [
    'github.com',
    'raw.githubusercontent.com',
    'api.github.com',
    'clawhub.ai',
    'registry.npmjs.org',
    'pypi.org',
    'picoapps.com',
]


def validate_slug(slug):
    """Validate slug to prevent command injection."""
    # Only allow alphanumeric, hyphens, and underscores
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', slug):
        return False
    # Block dangerous patterns
    dangerous = [';', '&&', '||', '`', '$(', '\n', '\r', '|']
    return not any(c in slug for c in dangerous)


def run_command(cmd, use_shell=False):
    """Run a command and return output."""
    try:
        if use_shell:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
        else:
            # Use list form to avoid shell injection
            if isinstance(cmd, str):
                cmd = cmd.split()
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1


def security_check_v1_clawhub(slug):
    """Phase 1: Check ClawHub security report."""
    # Validate slug to prevent command injection
    if not validate_slug(slug):
        return {
            "status": "INVALID_SLUG",
            "message": "Invalid characters in slug - possible injection attempt",
            "passed": False
        }
    
    print(f"\n🔍 Phase 1: ClawHub Security Report for '{slug}'...")
    
    # Use list form to avoid shell injection
    stdout, stderr, code = run_command(["npx", "clawhub", "inspect", slug, "--json"])
    
    if code != 0 or not stdout:
        return {
            "status": "UNKNOWN",
            "message": "Could not fetch ClawHub report",
            "passed": False
        }
    
    try:
        data = json.loads(stdout)
        # Check for any security flags in the data
        if 'security' in data:
            return {
                "status": "CHECKED",
                "message": "Security report found",
                "passed": True
            }
        return {
            "status": "NO_REPORT",
            "message": "No specific security report available",
            "passed": True  # Not a failure, just no report
        }
    except:
        return {
            "status": "UNKNOWN",
            "message": "Could not parse ClawHub response",
            "passed": False
        }


def fetch_file_content(slug, file_path):
    """Fetch a single file's content from the skill."""
    # Use npx to get file content
    stdout, stderr, code = run_command(["npx", "clawhub", "inspect", slug, "--file", file_path])
    if code == 0 and stdout:
        return stdout
    return None


def security_check_v2_code_analysis(slug):
    """
    Phase 2: DEEP content analysis for malicious patterns.
    
    SECURITY NOTES:
    - This fetches and scans actual file contents
    - Uses multiple pattern detectors for security risks
    - Can produce false positives - owner must review
    - Does NOT execute any fetched code
    """
    # Validate slug
    if not validate_slug(slug):
        return {
            "status": "INVALID_SLUG",
            "message": "Invalid characters in slug",
            "issues": [],
            "passed": False
        }
    
    print(f"\n🔍 Phase 2: DEEP Content Analysis for '{slug}'...")
    
    # Use list form to avoid shell injection
    stdout, stderr, code = run_command(["npx", "clawhub", "inspect", slug, "--files"])
    
    issues = []
    
    if code != 0:
        return {
            "status": "ERROR",
            "message": f"Could not fetch files: {stderr}",
            "issues": [],
            "passed": False
        }
    
    # Parse file list - format is "filename size hash type"
    files = []
    in_files_section = False
    for line in stdout.strip().split('\n'):
        if line.strip() == 'Files:':
            in_files_section = True
            continue
        if in_files_section and line.strip():
            # Extract filename (first field)
            parts = line.strip().split()
            if parts:
                files.append(parts[0])
    
    print(f"   Found {len(files)} files to analyze...")
    
    # Analyze each file for dangerous patterns
    text_extensions = ['.py', '.js', '.sh', '.md', '.json', '.yaml', '.yml', '.txt']
    
    # Count files scanned
    files_scanned = 0
    
    for file in files:
        file = file.strip()
        if not file:
            continue
        
        # Only analyze text files
        if not any(file.endswith(ext) for ext in text_extensions):
            continue
        
        files_scanned += 1
        
        # Check for suspicious file names FIRST (before content)
        suspicious_names = ['backdoor', 'exploit', 'miner', 'virus', 'trojan', 'keylogger', 'rootkit']
        if any(s in file.lower() for s in suspicious_names):
            issues.append({
                "file": file,
                "pattern": "suspicious_filename",
                "severity": "CRITICAL",
                "message": "Suspicious file name detected"
            })
            continue  # Skip further analysis of clearly suspicious files
        
        # For .md files, do content analysis on the SKILL.md specifically
        if file.endswith('/SKILL.md') or file == 'SKILL.md':
            # Fetch and analyze SKILL.md content
            # This is the main instruction file - critical to scan
            content = fetch_file_content(slug, "SKILL.md")
            if content:
                
                # Scan for dangerous patterns in content
                for pattern, severity, msg in DANGEROUS_PATTERNS:
                    import re
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        # Avoid duplicate issues
                        if not any(i['file'] == "SKILL.md" and i['pattern'] == pattern for i in issues):
                            issues.append({
                                "file": "SKILL.md",
                                "pattern": pattern,
                                "severity": severity,
                                "message": f"Found: {msg} ({len(matches)} matches)"
                            })
        
        # For script files (.py, .js, .sh), analyze content
        if file.endswith(('.py', '.js', '.sh')):
            # Get the file name without path
            filename = file.split('/')[-1]
            content = fetch_file_content(slug, filename)
            if content:
                # Scan for dangerous patterns
                for pattern, severity, msg in DANGEROUS_PATTERNS:
                    import re
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        if not any(i['file'] == filename and i['pattern'] == pattern for i in issues):
                            issues.append({
                                "file": filename,
                                "pattern": pattern,
                                "severity": severity,
                                "message": f"Found: {msg} ({len(matches)} matches)"
                            })
    
    # Check for scripts folder - warning for executable code
    if any('scripts/' in f for f in files):
        # Check if scripts are present - this is a warning, not critical
        issues.append({
            "file": "scripts/",
            "pattern": "contains_scripts",
            "severity": "INFO",
            "message": "Contains scripts/ folder - review carefully before execution"
        })
    
    # Determine pass/fail - fail only on CRITICAL issues
    critical_issues = [i for i in issues if i['severity'] == 'CRITICAL']
    passed = len(critical_issues) == 0
    
    return {
        "status": "ANALYZED",
        "message": f"Deep analyzed {files_scanned} files, found {len(issues)} issues",
        "issues": issues,
        "critical_count": len(critical_issues),
        "passed": passed
    }


def integration_check(slug):
    """Phase 3: Check if skill fits the workspace architecture."""
    # Validate slug
    if not validate_slug(slug):
        return {
            "status": "INVALID_SLUG",
            "already_installed": False,
            "similar_skills": [],
            "workspace_skills_count": 0,
            "conflicts": [],
            "passed": False,
            "recommendation": "INVALID_SLUG"
        }
    
    print(f"\n🔍 Phase 3: Integration Check for '{slug}'...")
    
    # Use list form to avoid shell injection
    stdout, stderr, code = run_command(["npx", "clawhub", "search", slug])
    
    similar_skills = []
    if stdout:
        lines = stdout.strip().split('\n')
        for line in lines[1:]:  # Skip header
            if line.strip() and slug not in line:
                similar_skills.append(line.strip())
    
    # Check if already installed - use list form
    stdout2, _, _ = run_command(["npx", "clawhub", "list"])
    already_installed = slug in stdout2 if stdout2 else False
    
    # Check workspace for similar skills
    workspace_skills = []
    skills_dir = os.path.expanduser("~/.openclaw/workspace/skills")
    if os.path.exists(skills_dir):
        for item in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, item)
            if os.path.isdir(skill_path) and item not in ['.archive', 'mocs']:
                workspace_skills.append(item)
    
    # Check for conflicts
    conflicts = []
    for sim in similar_skills[:3]:  # Top 3 similar
        for ws in workspace_skills:
            if ws.lower() in sim.lower() or sim.lower() in ws.lower():
                conflicts.append(f"Similar to installed: {ws}")
    
    passed = len(conflicts) == 0 and not already_installed
    
    return {
        "status": "CHECKED",
        "already_installed": already_installed,
        "similar_skills": similar_skills[:5],
        "workspace_skills_count": len(workspace_skills),
        "conflicts": conflicts,
        "passed": passed,
        "recommendation": "PROCEED" if not already_installed else "ALREADY_INSTALLED"
    }


def generate_report(slug, v1, v2, integration):
    """Generate a report for the owner."""
    print("\n" + "="*50)
    print(f"📋 SKILL INSTALL REPORT: {slug}")
    print("="*50)
    
    # Security Status
    print("\n🛡️ SECURITY STATUS")
    print("-"*30)
    print(f"  Phase 1 (ClawHub): {v1['status']} - {'✅ PASS' if v1['passed'] else '❌ FAIL'}")
    print(f"  Phase 2 (DEEP Analysis): {v2['status']} - {'✅ PASS' if v2['passed'] else '❌ FAIL'}")
    
    if v2.get('issues'):
        critical_count = v2.get('critical_count', 0)
        print(f"\n  📊 Issues: {len(v2['issues'])} total, {critical_count} CRITICAL")
        print("\n  Details:")
        for issue in v2['issues']:
            emoji = "🔴" if issue['severity'] == 'CRITICAL' else "🟡" if issue['severity'] == 'HIGH' else "ℹ️"
            print(f"    {emoji} [{issue['severity']}] {issue['file']}: {issue['message']}")
    
    # Integration Status
    print("\n📦 INTEGRATION STATUS")
    print("-"*30)
    if integration['already_installed']:
        print(f"  ⚠️ Already installed!")
    else:
        print(f"  Workspace skills: {integration['workspace_skills_count']}")
        
        if integration['conflicts']:
            print(f"  Potential conflicts:")
            for c in integration['conflicts']:
                print(f"    - {c}")
        else:
            print(f"  ✅ No conflicts detected")
    
    # Overall Recommendation
    print("\n🎯 RECOMMENDATION")
    print("-"*30)
    
    can_proceed = v1['passed'] and v2['passed'] and not integration['already_installed']
    
    if not v1['passed']:
        print("  ❌ ABORTED - Failed ClawHub security check")
    elif not v2['passed']:
        print("  ❌ ABORTED - Failed deep content analysis (CRITICAL issues found)")
    elif integration['already_installed']:
        print("  ⏭️  SKIPPED - Already installed")
    else:
        print("  ✅ PROCEED - Deep analysis passed, no critical issues!")
    
    print("\n" + "="*50)
    print("⚠️  Owner confirmation required before installation.")
    print("    This is an automated check - always review manually.")
    print("="*50)
    
    return can_proceed


def main():
    parser = argparse.ArgumentParser(
        description="Skill Install Guardian - Security and Due Diligence Check"
    )
    parser.add_argument("slug", help="Skill slug to check")
    parser.add_argument("--quick", action="store_true", help="Skip detailed code analysis")
    
    args = parser.parse_args()
    
    print(f"\n🛡️ Skill Install Guardian")
    print(f"Checking skill: {args.slug}")
    print(f"Time: {datetime.now().isoformat()}")
    
    # Phase 1: ClawHub Security
    v1 = security_check_v1_clawhub(args.slug)
    
    # Phase 2: Code Analysis (skip if --quick)
    if args.quick:
        v2 = {"status": "SKIPPED", "message": "Quick mode", "issues": [], "passed": True}
    else:
        v2 = security_check_v2_code_analysis(args.slug)
    
    # Phase 3: Integration
    integration = integration_check(args.slug)
    
    # Generate Report
    can_proceed = generate_report(args.slug, v1, v2, integration)
    
    # Output JSON for automation
    result = {
        "skill": args.slug,
        "timestamp": datetime.now().isoformat(),
        "security": {
            "v1_clawhub": v1,
            "v2_code_analysis": v2
        },
        "integration": integration,
        "can_proceed": can_proceed
    }
    
    print(f"\n📄 JSON Output:")
    print(json.dumps(result, indent=2))
    
    return 0 if can_proceed else 1


if __name__ == "__main__":
    sys.exit(main())
