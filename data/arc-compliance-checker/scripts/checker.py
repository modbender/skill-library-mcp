#!/usr/bin/env python3
"""Compliance Checker — Policy-based compliance assessment for OpenClaw skills.

Defines security policies, assesses skills against them, tracks violations,
and generates compliance reports with framework mappings.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

# Paths
COMPLIANCE_DIR = os.path.expanduser("~/.openclaw/compliance")
POLICIES_DIR = os.path.join(COMPLIANCE_DIR, "policies")
ASSESSMENTS_DIR = os.path.join(COMPLIANCE_DIR, "assessments")
EXEMPTIONS_DIR = os.path.join(COMPLIANCE_DIR, "exemptions")
REMEDIATIONS_DIR = os.path.join(COMPLIANCE_DIR, "remediations")
SKILLS_DIR = os.path.expanduser("~/.openclaw/skills")

# Built-in rules with framework mappings
BUILTIN_RULES = {
    "no-critical-findings": {
        "description": "No CRITICAL findings from skill scanner",
        "severity": "critical",
        "frameworks": ["CIS Control 16", "OWASP A06"],
        "check": "scanner_severity",
        "params": {"max_severity": "CRITICAL", "max_count": 0},
    },
    "no-high-findings": {
        "description": "No HIGH findings from skill scanner",
        "severity": "high",
        "frameworks": ["CIS Control 16", "OWASP A06"],
        "check": "scanner_severity",
        "params": {"max_severity": "HIGH", "max_count": 0},
    },
    "trust-verified": {
        "description": "Must have VERIFIED or TRUSTED trust level",
        "severity": "high",
        "frameworks": ["CIS Control 2"],
        "check": "trust_level",
        "params": {"min_level": "TRUSTED"},
    },
    "no-network-calls": {
        "description": "No unauthorized network requests in scripts",
        "severity": "high",
        "frameworks": ["CIS Control 9", "OWASP A10"],
        "check": "pattern_absent",
        "params": {"patterns": ["urllib", "requests", "http.client", "socket.connect", "urlopen"]},
    },
    "no-shell-exec": {
        "description": "No shell execution patterns",
        "severity": "medium",
        "frameworks": ["CIS Control 2", "OWASP A03"],
        "check": "pattern_absent",
        "params": {"patterns": ["shell=True", "os.system(", "subprocess.call("]},
    },
    "no-eval-exec": {
        "description": "No eval/exec patterns",
        "severity": "medium",
        "frameworks": ["OWASP A03"],
        "check": "pattern_absent",
        "params": {"patterns": ["eval(", "exec(", "compile("]},
    },
    "has-checksum": {
        "description": "SHA-256 checksums for all script files",
        "severity": "medium",
        "frameworks": ["CIS Control 2"],
        "check": "checksums_present",
        "params": {},
    },
    "no-env-access": {
        "description": "No environment variable access",
        "severity": "medium",
        "frameworks": ["CIS Control 3"],
        "check": "pattern_absent",
        "params": {"patterns": ["os.environ", "os.getenv(", "ENV["]},
    },
    "no-data-exfil": {
        "description": "No data exfiltration patterns",
        "severity": "high",
        "frameworks": ["CIS Control 3", "CIS Control 13"],
        "check": "pattern_absent",
        "params": {"patterns": ["base64.b64encode", ".encode('base64')", "webhook", "exfil"]},
    },
    "version-pinned": {
        "description": "All dependencies version-pinned",
        "severity": "low",
        "frameworks": ["CIS Control 2"],
        "check": "version_pinned",
        "params": {},
    },
}


import re as _re


def _sanitize_name(name, label="name"):
    """Validate that a name contains only safe characters (no path traversal)."""
    if not _re.match(r'^[a-zA-Z0-9_-]+$', name):
        print(f"ERROR: Invalid {label}: {name!r} — only alphanumeric, dash, underscore allowed", file=sys.stderr)
        sys.exit(1)
    return name


def ensure_dirs():
    for d in [POLICIES_DIR, ASSESSMENTS_DIR, EXEMPTIONS_DIR, REMEDIATIONS_DIR]:
        os.makedirs(d, exist_ok=True)


def load_json(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def get_policy_path(name):
    return os.path.join(POLICIES_DIR, f"{name}.json")


def get_assessment_path(skill, policy):
    return os.path.join(ASSESSMENTS_DIR, f"{skill}__{policy}.json")


def get_exemption_path(skill):
    return os.path.join(EXEMPTIONS_DIR, f"{skill}.json")


def get_remediation_path(skill):
    return os.path.join(REMEDIATIONS_DIR, f"{skill}.json")


# --- Rule Checks ---

def _get_skill_scripts(skill_name):
    """Get all script files for a skill."""
    skill_dir = os.path.join(SKILLS_DIR, skill_name, "scripts")
    if not os.path.isdir(skill_dir):
        return []
    scripts = []
    for root, _, files in os.walk(skill_dir):
        for f in files:
            if f.endswith((".py", ".sh", ".js", ".ts", ".rb")):
                scripts.append(os.path.join(root, f))
    return scripts


def _read_skill_content(skill_name):
    """Read all script content for a skill."""
    content = ""
    for path in _get_skill_scripts(skill_name):
        with open(path, errors="replace") as f:
            content += f.read() + "\n"
    # Also read SKILL.md
    skill_md = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
    if os.path.exists(skill_md):
        with open(skill_md, errors="replace") as f:
            content += f.read()
    return content


def check_scanner_severity(skill_name, params):
    """Check if skill scanner reports findings at or above a severity."""
    max_sev = params.get("max_severity", "CRITICAL")
    max_count = params.get("max_count", 0)

    # Run skill scanner if available
    scanner_script = os.path.join(SKILLS_DIR, "skill-scanner", "scripts", "scanner.py")
    if not os.path.exists(scanner_script):
        return {"pass": True, "note": "Scanner not installed, skipping"}

    skill_path = os.path.join(SKILLS_DIR, skill_name)
    try:
        result = subprocess.run(
            ["python3", scanner_script, "--json", skill_path],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return {"pass": False, "note": f"Scanner error: {result.stderr[:200]}"}

        scan = json.loads(result.stdout)
        findings = scan.get("findings", [])

        severity_order = ["CLEAN", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
        threshold_idx = severity_order.index(max_sev) if max_sev in severity_order else 4

        violations = [f for f in findings if severity_order.index(f.get("severity", "LOW")) >= threshold_idx]

        if len(violations) > max_count:
            return {
                "pass": False,
                "violations": len(violations),
                "details": [{"severity": v["severity"], "message": v.get("message", "")[:100]} for v in violations[:5]],
            }
        return {"pass": True, "findings_checked": len(findings)}
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
        return {"pass": False, "note": f"Scanner check failed: {str(e)[:100]}"}


def check_trust_level(skill_name, params):
    """Check if skill has required trust level."""
    min_level = params.get("min_level", "TRUSTED")
    level_order = ["UNTRUSTED", "SUSPICIOUS", "UNKNOWN", "TRUSTED", "VERIFIED"]

    # Run trust verifier if available
    verifier_script = os.path.join(SKILLS_DIR, "trust-verifier", "scripts", "verifier.py")
    if not os.path.exists(verifier_script):
        return {"pass": True, "note": "Trust verifier not installed, skipping"}

    skill_path = os.path.join(SKILLS_DIR, skill_name)
    try:
        result = subprocess.run(
            ["python3", verifier_script, "verify", skill_path],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout + result.stderr
        # Parse trust level from output
        for level in reversed(level_order):
            if level in output.upper():
                actual_idx = level_order.index(level)
                required_idx = level_order.index(min_level)
                if actual_idx >= required_idx:
                    return {"pass": True, "trust_level": level}
                return {"pass": False, "trust_level": level, "required": min_level}
        return {"pass": False, "note": "Could not determine trust level"}
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {"pass": False, "note": f"Trust check failed: {str(e)[:100]}"}


def check_pattern_absent(skill_name, params):
    """Check that patterns are absent from skill code."""
    patterns = params.get("patterns", [])
    content = _read_skill_content(skill_name)

    found = []
    for pattern in patterns:
        if pattern.lower() in content.lower():
            # Find line numbers
            for i, line in enumerate(content.split("\n"), 1):
                if pattern.lower() in line.lower():
                    found.append({"pattern": pattern, "line": i, "snippet": line.strip()[:80]})
                    break

    if found:
        return {"pass": False, "patterns_found": found}
    return {"pass": True, "patterns_checked": len(patterns)}


def check_checksums_present(skill_name, _params):
    """Check that SHA-256 checksums exist for all scripts."""
    scripts = _get_skill_scripts(skill_name)
    if not scripts:
        return {"pass": True, "note": "No scripts to checksum"}

    checksum_file = os.path.join(SKILLS_DIR, skill_name, "checksums.sha256")
    if not os.path.exists(checksum_file):
        return {"pass": False, "note": "No checksums.sha256 file found", "scripts_count": len(scripts)}

    with open(checksum_file) as f:
        checksums = f.read()

    missing = []
    for script in scripts:
        basename = os.path.basename(script)
        if basename not in checksums:
            missing.append(basename)

    if missing:
        return {"pass": False, "missing_checksums": missing}
    return {"pass": True, "verified_count": len(scripts)}


def check_version_pinned(skill_name, _params):
    """Check that dependencies (if any) are version-pinned."""
    skill_dir = os.path.join(SKILLS_DIR, skill_name)
    req_file = os.path.join(skill_dir, "requirements.txt")

    if not os.path.exists(req_file):
        return {"pass": True, "note": "No requirements.txt (no dependencies)"}

    with open(req_file) as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    unpinned = [l for l in lines if "==" not in l and ">=" not in l]
    if unpinned:
        return {"pass": False, "unpinned": unpinned}
    return {"pass": True, "deps_checked": len(lines)}


# Rule check dispatcher
RULE_CHECKS = {
    "scanner_severity": check_scanner_severity,
    "trust_level": check_trust_level,
    "pattern_absent": check_pattern_absent,
    "checksums_present": check_checksums_present,
    "version_pinned": check_version_pinned,
}


# --- Commands ---

def cmd_policy_create(args):
    ensure_dirs()
    _sanitize_name(args.name, "policy name")
    path = get_policy_path(args.name)
    if os.path.exists(path):
        print(f"Policy '{args.name}' already exists. Use 'policy add-rule' to modify.")
        return

    policy = {
        "name": args.name,
        "description": args.description or "",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "rules": [],
    }
    save_json(path, policy)
    print(f"Policy '{args.name}' created.")


def cmd_policy_add_rule(args):
    ensure_dirs()
    path = get_policy_path(args.policy)
    policy = load_json(path)
    if not policy:
        print(f"Policy '{args.policy}' not found. Create it first.")
        return

    rule_name = args.rule
    if rule_name in BUILTIN_RULES:
        rule = {
            "name": rule_name,
            **BUILTIN_RULES[rule_name],
        }
        if args.severity:
            rule["severity"] = args.severity
        if args.description:
            rule["description"] = args.description
    else:
        rule = {
            "name": rule_name,
            "description": args.description or rule_name,
            "severity": args.severity or "medium",
            "frameworks": [],
            "check": "pattern_absent",
            "params": {"patterns": [rule_name]},
        }

    # Don't duplicate
    existing_names = [r["name"] for r in policy["rules"]]
    if rule_name in existing_names:
        print(f"Rule '{rule_name}' already in policy. Skipping.")
        return

    policy["rules"].append(rule)
    save_json(path, policy)
    print(f"Rule '{rule_name}' added to policy '{args.policy}'.")


def cmd_policy_list(args):
    ensure_dirs()
    policies = [f[:-5] for f in os.listdir(POLICIES_DIR) if f.endswith(".json")]
    if not policies:
        print("No policies defined. Use 'policy create' to create one.")
        return
    for name in sorted(policies):
        p = load_json(get_policy_path(name))
        rules_count = len(p.get("rules", []))
        print(f"  {name}: {p.get('description', '')} ({rules_count} rules)")


def cmd_assess(args):
    ensure_dirs()
    skill_name = _sanitize_name(args.skill, "skill name")
    policy_name = _sanitize_name(args.policy, "policy name")

    # Verify skill exists
    skill_dir = os.path.join(SKILLS_DIR, skill_name)
    if not os.path.isdir(skill_dir):
        print(f"Skill '{skill_name}' not found at {skill_dir}")
        return

    # Load policy
    policy = load_json(get_policy_path(policy_name))
    if not policy:
        print(f"Policy '{policy_name}' not found.")
        return

    # Load exemptions
    exemptions = load_json(get_exemption_path(skill_name)) or {"exemptions": []}
    exempted_rules = {e["rule"] for e in exemptions.get("exemptions", [])}

    # Assess each rule
    results = []
    all_pass = True
    all_exempted = True

    for rule in policy["rules"]:
        check_type = rule.get("check", "pattern_absent")
        check_fn = RULE_CHECKS.get(check_type)

        if not check_fn:
            result = {"pass": False, "note": f"Unknown check type: {check_type}"}
        else:
            result = check_fn(skill_name, rule.get("params", {}))

        is_exempted = rule["name"] in exempted_rules
        passed = result.get("pass", False)

        entry = {
            "rule": rule["name"],
            "severity": rule.get("severity", "medium"),
            "frameworks": rule.get("frameworks", []),
            "passed": passed,
            "exempted": is_exempted,
            "details": result,
        }
        results.append(entry)

        if not passed and not is_exempted:
            all_pass = False
            all_exempted = False
        elif not passed and is_exempted:
            all_pass = False

    # Determine overall status
    if all_pass:
        status = "COMPLIANT"
    elif not all_pass and all([r["passed"] or r["exempted"] for r in results]):
        status = "EXEMPTED"
    else:
        status = "NON-COMPLIANT"

    assessment = {
        "skill": skill_name,
        "policy": policy_name,
        "status": status,
        "assessed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "rules_total": len(results),
        "rules_passed": sum(1 for r in results if r["passed"]),
        "rules_failed": sum(1 for r in results if not r["passed"] and not r["exempted"]),
        "rules_exempted": sum(1 for r in results if r["exempted"]),
        "results": results,
    }

    save_json(get_assessment_path(skill_name, policy_name), assessment)

    # Print summary
    status_color = {"COMPLIANT": "PASS", "EXEMPTED": "EXEMPT", "NON-COMPLIANT": "FAIL"}
    print(f"[{status_color.get(status, status)}] {skill_name} against '{policy_name}': {status}")
    exempted_count = assessment['rules_exempted']
    failed_count = assessment['rules_failed']
    summary = f"  Rules: {assessment['rules_passed']}/{assessment['rules_total']} passed"
    if exempted_count:
        summary += f", {exempted_count} exempted"
    if failed_count:
        summary += f", {failed_count} FAILED"
    print(summary)

    if args.verbose:
        for r in results:
            mark = "PASS" if r["passed"] else ("EXEMPT" if r["exempted"] else "FAIL")
            print(f"  [{mark}] {r['rule']} ({r['severity']})")
            if not r["passed"] and not r["exempted"]:
                details = r.get("details", {})
                for k, v in details.items():
                    if k != "pass":
                        print(f"         {k}: {json.dumps(v)[:100]}")

    if args.json_output:
        print(json.dumps(assessment, indent=2))

    return assessment


def cmd_assess_all(args):
    ensure_dirs()
    policy_name = args.policy

    policy = load_json(get_policy_path(policy_name))
    if not policy:
        print(f"Policy '{policy_name}' not found.")
        return

    skills = sorted([d for d in os.listdir(SKILLS_DIR)
                     if os.path.isdir(os.path.join(SKILLS_DIR, d))
                     and os.path.exists(os.path.join(SKILLS_DIR, d, "SKILL.md"))])

    print(f"Assessing {len(skills)} skills against policy '{policy_name}'")
    print("=" * 60)

    stats = {"COMPLIANT": 0, "NON-COMPLIANT": 0, "EXEMPTED": 0}
    for skill in skills:
        args_copy = argparse.Namespace(
            skill=skill, policy=policy_name, verbose=False, json_output=False
        )
        assessment = cmd_assess(args_copy)
        if assessment:
            stats[assessment["status"]] = stats.get(assessment["status"], 0) + 1

    print("=" * 60)
    total = len(skills)
    print(f"Summary: {stats['COMPLIANT']}/{total} compliant, "
          f"{stats['NON-COMPLIANT']} non-compliant, "
          f"{stats['EXEMPTED']} exempted")
    compliance_pct = (stats["COMPLIANT"] + stats["EXEMPTED"]) / total * 100 if total else 0
    print(f"Compliance rate: {compliance_pct:.0f}%")


def cmd_status(args):
    ensure_dirs()
    policy_name = args.policy

    # Find all assessments for this policy
    assessments = []
    for f in os.listdir(ASSESSMENTS_DIR):
        if f.endswith(f"__{policy_name}.json"):
            a = load_json(os.path.join(ASSESSMENTS_DIR, f))
            if a:
                assessments.append(a)

    if not assessments:
        print(f"No assessments found for policy '{policy_name}'. Run 'assess-all' first.")
        return

    assessments.sort(key=lambda a: a["skill"])

    print(f"Compliance status for policy '{policy_name}'")
    print(f"{'Skill':<35} {'Status':<15} {'Passed':<10} {'Failed':<10} {'Assessed'}")
    print("-" * 90)

    for a in assessments:
        print(f"{a['skill']:<35} {a['status']:<15} {a['rules_passed']:<10} {a['rules_failed']:<10} {a['assessed_at'][:16]}")


def cmd_report(args):
    ensure_dirs()
    policy_name = args.policy

    policy = load_json(get_policy_path(policy_name))
    if not policy:
        print(f"Policy '{policy_name}' not found.")
        return

    # Collect all assessments
    assessments = []
    for f in sorted(os.listdir(ASSESSMENTS_DIR)):
        if f.endswith(f"__{policy_name}.json"):
            a = load_json(os.path.join(ASSESSMENTS_DIR, f))
            if a:
                assessments.append(a)

    report = {
        "policy": policy_name,
        "policy_description": policy.get("description", ""),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_skills": len(assessments),
        "compliant": sum(1 for a in assessments if a["status"] == "COMPLIANT"),
        "non_compliant": sum(1 for a in assessments if a["status"] == "NON-COMPLIANT"),
        "exempted": sum(1 for a in assessments if a["status"] == "EXEMPTED"),
        "compliance_rate": 0,
        "framework_coverage": {},
        "skills": assessments,
    }

    if assessments:
        report["compliance_rate"] = round(
            (report["compliant"] + report["exempted"]) / report["total_skills"] * 100, 1
        )

    # Aggregate framework violations
    framework_violations = {}
    for a in assessments:
        for r in a.get("results", []):
            if not r["passed"] and not r.get("exempted"):
                for fw in r.get("frameworks", []):
                    framework_violations.setdefault(fw, []).append({
                        "skill": a["skill"],
                        "rule": r["rule"],
                        "severity": r["severity"],
                    })
    report["framework_violations"] = framework_violations

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"\nCompliance Report: {policy_name}")
        print(f"Generated: {report['generated_at']}")
        print(f"{'=' * 60}")
        print(f"Skills assessed: {report['total_skills']}")
        print(f"Compliant: {report['compliant']}")
        print(f"Non-compliant: {report['non_compliant']}")
        print(f"Exempted: {report['exempted']}")
        print(f"Compliance rate: {report['compliance_rate']}%")
        print()

        if framework_violations:
            print("Framework Violations:")
            for fw, violations in sorted(framework_violations.items()):
                print(f"  {fw}: {len(violations)} violation(s)")
                for v in violations[:3]:
                    print(f"    - {v['skill']}: {v['rule']} ({v['severity']})")
            print()

        if report["non_compliant"] > 0:
            print("Non-Compliant Skills:")
            for a in assessments:
                if a["status"] == "NON-COMPLIANT":
                    failed = [r for r in a["results"] if not r["passed"] and not r.get("exempted")]
                    print(f"  {a['skill']}:")
                    for r in failed:
                        print(f"    [{r['severity'].upper()}] {r['rule']}")


def cmd_exempt(args):
    ensure_dirs()
    _sanitize_name(args.skill, "skill name")
    _sanitize_name(args.rule, "rule name")
    path = get_exemption_path(args.skill)
    data = load_json(path) or {"skill": args.skill, "exemptions": []}

    # Check for duplicate
    for e in data["exemptions"]:
        if e["rule"] == args.rule:
            print(f"Exemption already exists for {args.skill}/{args.rule}")
            return

    data["exemptions"].append({
        "rule": args.rule,
        "reason": args.reason or "",
        "approved_by": args.approved_by or "unknown",
        "granted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })
    save_json(path, data)
    print(f"Exemption granted: {args.skill} for rule '{args.rule}'")


def cmd_remediate(args):
    ensure_dirs()
    _sanitize_name(args.skill, "skill name")
    path = get_remediation_path(args.skill)
    data = load_json(path) or {"skill": args.skill, "remediations": []}

    data["remediations"].append({
        "rule": args.rule,
        "action": args.action or "",
        "status": args.status or "in_progress",
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })
    save_json(path, data)
    print(f"Remediation recorded: {args.skill}/{args.rule} — {args.status}")


def cmd_pipeline(args):
    """Run full pipeline: scan → trust verify → compliance assess."""
    ensure_dirs()
    skill_name = _sanitize_name(args.skill, "skill name")
    policy_name = _sanitize_name(args.policy, "policy name")

    print(f"Running full compliance pipeline for '{skill_name}'...")
    print()

    # Step 1: Scan
    scanner = os.path.join(SKILLS_DIR, "skill-scanner", "scripts", "scanner.py")
    if os.path.exists(scanner):
        print("[1/3] Running skill scanner...")
        result = subprocess.run(
            ["python3", scanner, os.path.join(SKILLS_DIR, skill_name)],
            capture_output=True, text=True, timeout=30
        )
        print(result.stdout[:500] if result.stdout else "  (no output)")
    else:
        print("[1/3] Skill scanner not found, skipping.")

    # Step 2: Trust verify
    verifier = os.path.join(SKILLS_DIR, "trust-verifier", "scripts", "verifier.py")
    if os.path.exists(verifier):
        print("[2/3] Running trust verifier...")
        result = subprocess.run(
            ["python3", verifier, "verify", os.path.join(SKILLS_DIR, skill_name)],
            capture_output=True, text=True, timeout=30
        )
        print(result.stdout[:500] if result.stdout else "  (no output)")
    else:
        print("[2/3] Trust verifier not found, skipping.")

    # Step 3: Compliance assess
    print("[3/3] Assessing compliance...")
    assess_args = argparse.Namespace(
        skill=skill_name, policy=policy_name, verbose=True, json_output=False
    )
    cmd_assess(assess_args)


def main():
    parser = argparse.ArgumentParser(description="Compliance Checker for OpenClaw skills")
    sub = parser.add_subparsers(dest="command")

    # Policy commands
    p_create = sub.add_parser("policy-create", aliases=["policy create"])
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--description", default="")

    p_add = sub.add_parser("policy-add-rule")
    p_add.add_argument("--policy", required=True)
    p_add.add_argument("--rule", required=True)
    p_add.add_argument("--description", default="")
    p_add.add_argument("--severity", default="")

    p_list = sub.add_parser("policy-list")

    # Assessment commands
    p_assess = sub.add_parser("assess")
    p_assess.add_argument("--skill", required=True)
    p_assess.add_argument("--policy", required=True)
    p_assess.add_argument("--verbose", "-v", action="store_true")
    p_assess.add_argument("--json", dest="json_output", action="store_true")

    p_all = sub.add_parser("assess-all")
    p_all.add_argument("--policy", required=True)

    # Status and reporting
    p_status = sub.add_parser("status")
    p_status.add_argument("--policy", required=True)

    p_report = sub.add_parser("report")
    p_report.add_argument("--policy", required=True)
    p_report.add_argument("--format", choices=["json", "text"], default="text")

    # Exemptions
    p_exempt = sub.add_parser("exempt")
    p_exempt.add_argument("--skill", required=True)
    p_exempt.add_argument("--rule", required=True)
    p_exempt.add_argument("--reason", default="")
    p_exempt.add_argument("--approved-by", default="")

    # Remediation
    p_remed = sub.add_parser("remediate")
    p_remed.add_argument("--skill", required=True)
    p_remed.add_argument("--rule", required=True)
    p_remed.add_argument("--action", default="")
    p_remed.add_argument("--status", default="in_progress")

    # Pipeline
    p_pipe = sub.add_parser("pipeline")
    p_pipe.add_argument("--skill", required=True)
    p_pipe.add_argument("--policy", required=True)

    args = parser.parse_args()

    commands = {
        "policy-create": cmd_policy_create,
        "policy-add-rule": cmd_policy_add_rule,
        "policy-list": cmd_policy_list,
        "assess": cmd_assess,
        "assess-all": cmd_assess_all,
        "status": cmd_status,
        "report": cmd_report,
        "exempt": cmd_exempt,
        "remediate": cmd_remediate,
        "pipeline": cmd_pipeline,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
