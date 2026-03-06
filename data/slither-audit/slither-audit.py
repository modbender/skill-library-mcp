#!/usr/bin/env python3
"""
Slither Audit - Lightweight smart contract security scanner
Usage: slither-audit <path>
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

def run_slither(contract_path):
    """Run slither static analysis."""
    try:
        result = subprocess.run(
            ["slither", contract_path, "--json", "-"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        
        # Try JSON first, fallback to text parsing
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                return {"findings": data.get("results", {}).get("detectors", [])}, None
            except:
                findings = []
                for line in result.stdout.split("\n"):
                    if "Detector:" in line:
                        parts = line.split("Detector: ")
                        if len(parts) > 1:
                            name = parts[1].split()[0] if parts[1] else "Unknown"
                            findings.append({"check": name, "impact": "High", "description": line[:200]})
                return {"findings": findings}, None
        
        # Check stderr for slither output
        if result.stderr:
            findings = []
            for line in result.stderr.split("\n"):
                if "Detector:" in line:
                    parts = line.split("Detector: ")
                    if len(parts) > 1:
                        name = parts[1].split()[0] if parts[1] else "Unknown"
                        findings.append({"check": name, "impact": "High", "description": line[:200]})
            if findings:
                return {"findings": findings}, None
            
        return {"findings": [], "error": "No output"}, None
    except FileNotFoundError:
        return {"findings": [], "error": "slither not installed. Run: pip install slither-analyzer"}, None
    except Exception as e:
        return {"findings": [], "error": str(e)}, None

def generate_report(slither_results):
    """Generate vulnerability report."""
    report = {
        "vulnerabilities": [],
        "slither_findings": slither_results.get("findings", []),
    }
    
    findings = slither_results.get("findings", [])
    if isinstance(findings, list):
        for f in findings[:10]:
            if isinstance(f, dict):
                report["vulnerabilities"].append({
                    "type": f.get("check", "Unknown"),
                    "severity": f.get("impact", "Medium"),
                    "description": f.get("description", "")[:200],
                })
    
    return report

def main():
    parser = argparse.ArgumentParser(description="Slither Audit - Run Slither static analysis on Solidity contracts")
    parser.add_argument("target", help="Path to Solidity file or directory")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Output format")
    
    args = parser.parse_args()
    
    target = args.target
    
    # Validate target is a local path
    if not os.path.exists(target):
        print(f"Error: {target} does not exist")
        sys.exit(1)
    
    # Run slither
    slither_results, err = run_slither(target)
    
    if err:
        print(f"Error: {err}")
        sys.exit(1)
    
    # Generate report
    report = generate_report(slither_results)
    
    # Output
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        name = os.path.basename(target)
        print(f"# Audit Report: {name}")
        print(f"**Chain:** local")
        print()
        print("## Vulnerabilities Found")
        
        if report["vulnerabilities"]:
            for v in report["vulnerabilities"]:
                print(f"- **{v['type']}** ({v['severity']})")
                desc = v.get("description", "")
                if desc:
                    print(f"  {desc[:100]}")
        else:
            print("No critical vulnerabilities found.")
        
        print()
        print(f"## Summary")
        print(f"Found {len(report['slither_findings'])} issues")

if __name__ == "__main__":
    main()
