#!/usr/bin/env python3
"""Security Audit — Comprehensive security assessment of agent skill stacks.

Chains together scanner, trust-verifier, and binary checksums into a unified report.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add sibling skill scripts to path — use realpath to prevent symlink hijacking
SKILLS_BASE = Path(os.path.realpath(str(Path.home() / ".openclaw" / "skills")))
SCANNER_PATH = SKILLS_BASE / "skill-scanner" / "scripts"
TRUST_PATH = SKILLS_BASE / "trust-verifier" / "scripts"

# Only add to sys.path if they resolve to expected locations under SKILLS_BASE
for _p in (SCANNER_PATH, TRUST_PATH):
    _real = os.path.realpath(str(_p))
    if _real.startswith(str(SKILLS_BASE)) and os.path.isdir(_real):
        sys.path.insert(0, _real)


def _find_skill_dirs():
    """Find all installed skill directories."""
    skill_dirs = [
        Path.home() / ".openclaw" / "skills",
        Path.home() / ".openclaw" / "workspace" / "skills",
    ]
    results = []
    for base in skill_dirs:
        if not base.exists():
            continue
        for d in sorted(base.iterdir()):
            if d.is_dir() and (d / "SKILL.md").exists():
                results.append(d)
    return results


def audit_skill(skill_path, generate_attestation=False):
    """Run a full audit on a single skill."""
    skill_path = Path(os.path.realpath(str(skill_path)))
    if not skill_path.is_dir():
        print(f"Error: {skill_path} is not a directory", file=sys.stderr)
        return {"name": str(skill_path), "risk_level": "UNKNOWN", "error": "Not a directory"}
    skill_name = skill_path.name
    result = {"name": skill_name, "path": str(skill_path)}

    # 1. Security scan
    try:
        from scanner import scan_directory, classify_severity
        findings = scan_directory(skill_path)
        result["scan"] = {
            "total_findings": len(findings),
            "findings": findings,
            "by_severity": {},
        }
        for f in findings:
            sev = f["severity"]
            result["scan"]["by_severity"][sev] = result["scan"]["by_severity"].get(sev, 0) + 1
    except ImportError:
        result["scan"] = {"error": "arc-skill-scanner not installed"}
    except Exception as e:
        result["scan"] = {"error": str(e)}

    # 2. Trust assessment
    try:
        from trust_verifier import assess
        trust = assess(skill_path)
        result["trust"] = {
            "level": trust["trust_level"],
            "score": trust["score"],
            "signals": trust["signals"],
        }
    except ImportError:
        result["trust"] = {"error": "arc-trust-verifier not installed"}
    except Exception as e:
        result["trust"] = {"error": str(e)}

    # 3. Generate attestation if requested
    if generate_attestation:
        try:
            from trust_verifier import generate_attestation as gen_attest
            attest_dir = Path.home() / ".openclaw" / "attestations"
            attest_dir.mkdir(exist_ok=True)
            attest_path = attest_dir / f"{skill_name}.json"

            # Only attest if clean/trusted
            trust_level = result.get("trust", {}).get("level", "UNKNOWN")
            scan_critical = result.get("scan", {}).get("by_severity", {}).get("CRITICAL", 0)
            scan_high = result.get("scan", {}).get("by_severity", {}).get("HIGH", 0)

            if trust_level in ("VERIFIED", "TRUSTED") and scan_critical == 0 and scan_high == 0:
                gen_attest(skill_path, str(attest_path))
                result["attestation"] = {"status": "generated", "path": str(attest_path)}
            else:
                result["attestation"] = {"status": "skipped", "reason": f"Trust: {trust_level}, Critical: {scan_critical}, High: {scan_high}"}
        except Exception as e:
            result["attestation"] = {"error": str(e)}

    # 4. Determine overall risk
    scan_findings = result.get("scan", {}).get("by_severity", {})
    trust_level = result.get("trust", {}).get("level", "UNKNOWN")

    if scan_findings.get("CRITICAL", 0) > 0:
        result["risk_level"] = "CRITICAL"
    elif scan_findings.get("HIGH", 0) > 0:
        result["risk_level"] = "HIGH"
    elif trust_level in ("SUSPICIOUS", "UNTRUSTED"):
        result["risk_level"] = "HIGH"
    elif scan_findings.get("MEDIUM", 0) > 0:
        result["risk_level"] = "MEDIUM"
    elif trust_level == "UNKNOWN":
        result["risk_level"] = "LOW"
    else:
        result["risk_level"] = "CLEAN"

    return result


def full_audit(generate_attestations=False, json_output=False, output_file=None):
    """Audit all installed skills."""
    skills = _find_skill_dirs()
    results = []
    summary = {"total": len(skills), "by_risk": {}, "scanned_at": datetime.now(timezone.utc).isoformat()}

    for skill_path in skills:
        result = audit_skill(skill_path, generate_attestation=generate_attestations)
        results.append(result)
        risk = result.get("risk_level", "UNKNOWN")
        summary["by_risk"][risk] = summary["by_risk"].get(risk, 0) + 1

    # Sort by risk level (CRITICAL first)
    risk_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "CLEAN": 4, "UNKNOWN": 5}
    results.sort(key=lambda r: risk_order.get(r.get("risk_level", "UNKNOWN"), 99))

    report = {"summary": summary, "skills": results}

    if json_output:
        output = json.dumps(report, indent=2)
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output)
            print(f"Report written to {output_file}")
        else:
            print(output)
    else:
        # Human-readable output
        print(f"\nSecurity Audit Report — {summary['scanned_at'][:19]} UTC")
        print(f"Skills scanned: {summary['total']}")
        print(f"Risk distribution: {json.dumps(summary['by_risk'])}")
        print(f"\n{'Skill':<30} {'Risk':<12} {'Findings':<10} {'Trust':<12}")
        print("-" * 64)
        for r in results:
            name = r["name"][:30]
            risk = r.get("risk_level", "?")
            findings = r.get("scan", {}).get("total_findings", "?")
            trust = r.get("trust", {}).get("level", "?")
            print(f"{name:<30} {risk:<12} {findings:<10} {trust:<12}")

        # Critical actions
        critical = [r for r in results if r.get("risk_level") in ("CRITICAL", "HIGH")]
        if critical:
            print(f"\nCRITICAL ACTIONS ({len(critical)} skills need attention):")
            for r in critical:
                print(f"  {r['name']} ({r['risk_level']})")
                for f in r.get("scan", {}).get("findings", [])[:3]:
                    if f["severity"] in ("CRITICAL", "HIGH"):
                        print(f"    - {f['description']}")

    return report


def main():
    parser = argparse.ArgumentParser(description="Security Audit")
    sub = parser.add_subparsers(dest="command")

    p_full = sub.add_parser("full", help="Audit all installed skills")
    p_full.add_argument("--json", action="store_true")
    p_full.add_argument("--output", "-o", help="Output file for JSON report")
    p_full.add_argument("--attest", action="store_true", help="Generate trust attestations for passing skills")

    p_single = sub.add_parser("single", help="Audit a single skill")
    p_single.add_argument("--path", required=True, help="Skill directory")
    p_single.add_argument("--json", action="store_true")
    p_single.add_argument("--attest", action="store_true")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "full":
        full_audit(
            generate_attestations=args.attest,
            json_output=args.json,
            output_file=args.output,
        )
    elif args.command == "single":
        result = audit_skill(args.path, generate_attestation=args.attest)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\nAudit: {result['name']}")
            print(f"Risk: {result.get('risk_level', '?')}")
            print(f"Scan findings: {result.get('scan', {}).get('total_findings', '?')}")
            print(f"Trust: {result.get('trust', {}).get('level', '?')} (score: {result.get('trust', {}).get('score', '?')})")
            if result.get("attestation"):
                print(f"Attestation: {result['attestation'].get('status', '?')}")


if __name__ == "__main__":
    main()
