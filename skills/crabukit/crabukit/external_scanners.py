"""Integration with external security scanners like Clawdex."""

import subprocess
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from crabukit.rules.patterns import Finding, Severity


@dataclass
class ExternalScanResult:
    """Result from an external scanner."""
    scanner_name: str
    is_malicious: bool
    confidence: str  # "high", "medium", "low"
    details: str
    references: List[str]
    raw_output: Optional[str] = None


def check_clawdex_installed() -> bool:
    """Check if Clawdex skill is installed."""
    try:
        result = subprocess.run(
            ["clawdbot", "skills", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return "clawdex" in result.stdout.lower()
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False


def run_clawdex_check(skill_name: str) -> Optional[ExternalScanResult]:
    """Run Clawdex API check on a skill name.
    
    Uses the Clawdex API: https://clawdex.koi.security/api/skill/<skill_name>
    Returns None if check fails.
    """
    try:
        # Call Clawdex API directly
        result = subprocess.run(
            ["curl", "-s", f"https://clawdex.koi.security/api/skill/{skill_name}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return None
        
        # Parse JSON response
        try:
            data = json.loads(result.stdout)
            verdict = data.get("verdict", "unknown").lower()
        except json.JSONDecodeError:
            return None
        
        if verdict == "malicious":
            return ExternalScanResult(
                scanner_name="Clawdex",
                is_malicious=True,
                confidence="high",
                details=f"🚫 Clawdex database reports '{skill_name}' as MALICIOUS. This skill has been flagged as harmful and may steal credentials, install backdoors, or exfiltrate data.",
                references=["https://clawdex.koi.security", "https://www.koi.ai/blog/clawhavoc-341-malicious-clawedbot-skills-found-by-the-bot-they-were-targeting"],
                raw_output=result.stdout
            )
        elif verdict == "benign":
            return ExternalScanResult(
                scanner_name="Clawdex",
                is_malicious=False,
                confidence="high",
                details=f"✅ Clawdex database reports '{skill_name}' as BENIGN (safe to install).",
                references=["https://clawdex.koi.security"],
                raw_output=result.stdout
            )
        elif verdict == "unknown":
            return ExternalScanResult(
                scanner_name="Clawdex",
                is_malicious=False,
                confidence="low",
                details=f"⚠️  Clawdex database has no record for '{skill_name}' (not yet audited). Proceeding with behavior analysis...",
                references=["https://clawdex.koi.security"],
                raw_output=result.stdout
            )
        
        return None
        
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return None


def run_external_scanners(skill_name: str) -> List[ExternalScanResult]:
    """Run all available external scanners.
    
    Returns a list of results from all scanners that are installed and working.
    """
    results = []
    
    # Check Clawdex if available
    if check_clawdex_installed():
        clawdex_result = run_clawdex_check(skill_name)
        if clawdex_result:
            results.append(clawdex_result)
    
    return results


def convert_external_to_findings(external_results: List[ExternalScanResult]) -> List[Finding]:
    """Convert external scanner results to crabukit Findings."""
    findings = []
    
    for result in external_results:
        if result.is_malicious:
            severity = Severity.CRITICAL if result.confidence == "high" else Severity.HIGH
            findings.append(Finding(
                rule_id=f"EXTERNAL_{result.scanner_name.upper()}_MALICIOUS",
                title=f"🚫 {result.scanner_name}: KNOWN MALICIOUS SKILL",
                description=result.details,
                severity=severity,
                file_path="external_scan",
                line_number=0,
                remediation=f"DO NOT INSTALL. This skill is in the Clawdex malicious database. See {', '.join(result.references)}",
                references=result.references
            ))
        elif result.confidence == "low":
            # Unknown/not audited - informational
            findings.append(Finding(
                rule_id=f"EXTERNAL_{result.scanner_name.upper()}_UNKNOWN",
                title=f"⚠️  {result.scanner_name}: Not yet audited",
                description=result.details,
                severity=Severity.INFO,
                file_path="external_scan",
                line_number=0,
                references=result.references
            ))
        else:
            # Safe - info level
            findings.append(Finding(
                rule_id=f"EXTERNAL_{result.scanner_name.upper()}_SAFE",
                title=f"✅ {result.scanner_name}: Verified safe",
                description=result.details,
                severity=Severity.INFO,
                file_path="external_scan",
                line_number=0,
                references=result.references
            ))
    
    return findings
