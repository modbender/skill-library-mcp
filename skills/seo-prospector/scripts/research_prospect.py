#!/usr/bin/env python3
"""
Single-prospect research pipeline for SEO Prospector.

Combines deduplication, SEO audit, web research, and report generation.

Usage:
    python3 research_prospect.py --business "Name" --domain "example.com"
    python3 research_prospect.py --business "Name" --domain "example.com" --priority HIGH --cluster "Restaurants"
    python3 research_prospect.py --business "Name" --domain "example.com" --no-browser --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import date
from pathlib import Path
from typing import Any

# Build a proper SSL context for API calls
try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX = ssl.create_default_context()  # fallback to system certs

# Paths to existing tools
WORKSPACE = Path.home() / ".openclaw" / "workspace"
SEO_AUDIT = WORKSPACE / "scripts" / "seo_quick_audit.py"
PERPLEXITY = WORKSPACE / "scripts" / "perplexity_search.py"
TRACKER = WORKSPACE / "scripts" / "prospect_tracker.py"
LEADS_DIR = WORKSPACE / "leads"
PROSPECTS_DIR = LEADS_DIR / "prospects"


def check_duplicate(business_name: str, days: int = 14) -> dict | None:
    """Check if prospect was recently researched."""
    result = subprocess.run(
        ["python3", str(TRACKER), "check", "--business", business_name, "--days", str(days)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        return None
    data = json.loads(result.stdout)
    return data.get("prospect") if data.get("found") else None


def run_seo_audit(domain: str) -> dict[str, Any]:
    """Run SEO quick audit on domain."""
    if not domain.startswith("http"):
        domain = f"https://{domain}"
    
    result = subprocess.run(
        ["python3", str(SEO_AUDIT), domain, "--timeout", "15"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    
    # Parse the markdown output into structured findings
    output = result.stdout
    
    findings = {
        "url": domain,
        "status": "unknown",
        "strengths": [],
        "weaknesses": [],
        "recommendations": [],
        "raw_output": output,
    }
    
    # Extract key findings from markdown
    lines = output.split("\n")
    in_fixes = False
    for line in lines:
        if "Status:" in line:
            findings["status"] = line.split("Status:")[1].strip()
        elif line.startswith("✅"):
            findings["strengths"].append(line.replace("✅", "").strip())
        elif line.startswith("❌"):
            findings["weaknesses"].append(line.replace("❌", "").strip())
        elif "## Top fixes" in line:
            in_fixes = True
        elif in_fixes and line.startswith("- "):
            findings["recommendations"].append(line.replace("- ", "").strip())
    
    return findings


def run_perplexity_search(business_name: str, additional_context: str = "") -> str:
    """Search for business info via Perplexity."""
    query = f"{business_name} reviews website reputation {additional_context}"
    
    result = subprocess.run(
        ["python3", str(PERPLEXITY), query, "--max-tokens", "1000"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    if result.returncode != 0:
        return f"Error: {result.stderr or result.stdout}"
    
    return result.stdout.strip()


def generate_report(
    business_name: str,
    domain: str,
    industry: str,
    priority: str,
    cluster: str,
    seo_findings: dict[str, Any],
    perplexity_info: str,
    browser_notes: str = "",
) -> str:
    """Generate structured markdown prospect report."""
    
    today = date.today().isoformat()
    
    # Build SEO section
    seo_section = "### Website Audit\n\n"
    seo_section += f"**URL:** {domain}  \n"
    seo_section += f"**Status:** {seo_findings.get('status', 'unknown')}  \n\n"
    
    if seo_findings.get("strengths"):
        seo_section += "**SEO Strengths:**  \n"
        for s in seo_findings["strengths"][:5]:
            seo_section += f"✅ {s}  \n"
        seo_section += "\n"
    
    if seo_findings.get("weaknesses"):
        seo_section += "**SEO Weaknesses:**  \n"
        for w in seo_findings["weaknesses"][:5]:
            seo_section += f"❌ {w}  \n"
        seo_section += "\n"
    
    if seo_findings.get("recommendations"):
        seo_section += "**Recommended Fixes:**  \n"
        for r in seo_findings["recommendations"][:3]:
            seo_section += f"- {r}\n"
        seo_section += "\n"
    
    # Build report
    report = f"""# {business_name} — Prospect Report

**Date:** {today}  
**Cluster:** {cluster}  
**Priority:** {priority}

---

## Executive Summary

[TODO: 2-3 sentence summary of opportunity and key insight based on research below]

---

## Business Overview

**Name:** {business_name}  
**Website:** {domain}  
**Industry:** {industry}  

**What They Do:**
[TODO: Extract from Perplexity research below]

**Unique Selling Points:**
[TODO: Extract from research]

---

## Online Presence Analysis

{seo_section}

### Search Visibility & Reputation

{perplexity_info}

---

## Market Position

**Customer Sentiment:**
[TODO: Extract from reviews/mentions in research]

**Target Audience:**
[TODO: Infer from business type and research]

**Competitive Advantages:**
[TODO: Based on research findings]

---

## Business Health Indicators

**Positive Signals:**
[TODO: List strengths from research]

**Potential Growth Areas:**
[TODO: SEO opportunities + market gaps]

---

## Why Choose Us?

**Primary Opportunity:** [SEO improvement | Website rebuild | Content strategy]  

[TODO: Specific pitch based on findings]

**Objection Handling:**
[TODO: Address likely concerns]

**Value Proposition:**
[TODO: ROI-focused benefits]

---

## Contact & Next Steps

**Research Verified Through:**
- SEO audit via seo_quick_audit.py
- Perplexity search for business intelligence
{f'- Browser verification ({browser_notes})' if browser_notes else ''}

**Confidence Level:** [HIGH | MEDIUM | LOW]  
(Multiple sources confirm business quality and opportunity)

**Recommended Action:**
[TODO: Specific next step - email, LinkedIn, phone call, etc.]

---

*Report generated as part of SEO Prospector Pipeline ({cluster} cluster)*
"""
    
    return report


def complete_report_with_llm(report: str, business_name: str, domain: str, industry: str) -> str:
    """Use an LLM to fill in all [TODO: ...] placeholders with synthesized content.

    Calls OpenRouter (Haiku) to read the raw research already embedded in the
    report and produce concrete narrative sections.  Falls back to the original
    report (TODOs intact) on any error so the pipeline never breaks.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        print("   ⚠️  OPENROUTER_API_KEY not set — skipping LLM completion")
        return report

    system_prompt = (
        "You are a sales research analyst for your agency (configured in seo-prospector-config.json). "
        "You will receive a prospect research report that contains raw data (SEO audit results, "
        "Perplexity research text with citations) AND placeholder sections marked with [TODO: ...]. "
        "Your job is to replace every [TODO: ...] placeholder with specific, actionable content "
        "synthesized from the raw data already in the report.\n\n"
        "Rules:\n"
        "- Be specific and data-driven. Reference actual findings (star ratings, SEO issues, business details).\n"
        "- Keep each section concise (2-4 sentences or 3-5 bullet points).\n"
        "- For 'Executive Summary': Write 2-3 punchy sentences about the opportunity.\n"
        "- For 'What They Do': Extract from the Perplexity research section.\n"
        "- For 'Unique Selling Points': Pull differentiators from research.\n"
        "- For 'Customer Sentiment': Summarize review data and ratings.\n"
        "- For 'Target Audience': Infer from business type and offerings.\n"
        "- For 'Competitive Advantages': Based on reputation, years in business, specialties.\n"
        "- For 'Positive Signals': List business strengths (reviews, BBB rating, longevity, etc.).\n"
        "- For 'Potential Growth Areas': Combine SEO weaknesses with market opportunities.\n"
        "- For the 'Why Choose Us' section: Choose the primary opportunity from "
        "[SEO improvement, Website rebuild, Content strategy] and write a specific pitch. "
        "Address likely objections. Focus value proposition on ROI.\n"
        "- For 'Confidence Level': Choose HIGH, MEDIUM, or LOW based on data quality.\n"
        "- For 'Recommended Action': Suggest a specific outreach method and talking point.\n"
        "- Preserve ALL existing markdown formatting, headers, and raw data sections exactly.\n"
        "- Only replace text that is inside [TODO: ...] brackets.\n"
        "- Output the complete report with TODOs replaced. No commentary before or after."
    )

    user_prompt = (
        f"Here is the prospect report for {business_name} ({domain}, {industry} industry). "
        f"Replace all [TODO: ...] sections with real content based on the data in the report.\n\n"
        f"{report}"
    )

    payload = json.dumps({
        "model": "anthropic/claude-haiku-4.5",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 2000,
        "temperature": 0.3,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://youragency.com",
            "X-Title": "SEO Prospect Research",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60, context=_SSL_CTX) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        completed = body["choices"][0]["message"]["content"].strip()
        # Sanity check: completed report should still contain the business name
        # and be at least 60% the length of the original (guards against garbage)
        if business_name.lower() in completed.lower() and len(completed) > len(report) * 0.6:
            return completed
        else:
            print("   ⚠️  LLM output failed sanity check — keeping TODOs")
            return report
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError) as e:
        print(f"   ⚠️  LLM completion failed ({type(e).__name__}: {e}) — keeping TODOs")
        return report
    except Exception as e:
        print(f"   ⚠️  Unexpected LLM error ({type(e).__name__}: {e}) — keeping TODOs")
        return report


def save_report(business_name: str, cluster: str, report: str) -> Path:
    """Save report to prospects directory."""
    today = date.today().isoformat()
    cluster_slug = cluster.lower().replace(" ", "-").replace("&", "and")
    dir_name = f"{today}-{cluster_slug}"
    
    output_dir = PROSPECTS_DIR / dir_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Slugify business name
    filename = business_name.lower()
    filename = "".join(c if c.isalnum() or c in " -" else "" for c in filename)
    filename = "-".join(filename.split()) + ".md"
    
    output_file = output_dir / filename
    output_file.write_text(report)
    
    return output_file


def add_to_tracker(
    business_name: str,
    industry: str,
    priority: str,
    cluster: str,
    domain: str,
    report_file: Path,
) -> bool:
    """Add prospect to tracking database."""
    result = subprocess.run(
        [
            "python3", str(TRACKER), "add",
            "--business", business_name,
            "--industry", industry,
            "--priority", priority,
            "--cluster", cluster,
            "--domain", domain,
            "--file", str(report_file),
            "--source", "manual-research",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="SEO Single Prospect Research Pipeline")
    parser.add_argument("--business", required=True, help="Business name")
    parser.add_argument("--domain", required=True, help="Website domain (with or without https://)")
    parser.add_argument("--industry", default="unknown", help="Industry category")
    parser.add_argument("--priority", default="MEDIUM", choices=["HIGH", "MEDIUM", "LOW"], help="Priority level")
    parser.add_argument("--cluster", default="Manual Research", help="Cluster name from rotation")
    parser.add_argument("--no-browser", action="store_true", help="Skip browser verification")
    parser.add_argument("--dry-run", action="store_true", help="Generate report but don't save to database")
    parser.add_argument("--force", action="store_true", help="Research even if recently done")
    parser.add_argument("--output-json", action="store_true", help="Output JSON only (for batch/cron use)")
    args = parser.parse_args()
    
    log = not args.output_json  # suppress output in JSON mode
    if log:
        print(f"🔍 Researching: {args.business}")
        print(f"   Domain: {args.domain}")
        print(f"   Industry: {args.industry}")
        print(f"   Priority: {args.priority}")
        print()
    
    # Step 1: Check for duplicates
    if not args.force:
        if not args.output_json:
            print("📋 Checking for duplicates...")
        existing = check_duplicate(args.business)
        if existing:
            if args.output_json:
                print(json.dumps({"status": "duplicate", "business": args.business, "existing": existing}))
                return 0
            print(f"⚠️  Already researched on {existing.get('date')}")
            print(f"   Report: {existing.get('report_file')}")
            print()
            if not args.dry_run:
                response = input("Continue anyway? (y/N): ")
                if response.lower() != "y":
                    print("Aborted.")
                    return 1
            else:
                print("   (--dry-run: continuing anyway)")
    
    # Step 2: SEO Audit
    if log:
        print("🔎 Running SEO audit...")
    try:
        seo_findings = run_seo_audit(args.domain)
        if log:
            print(f"   Status: {seo_findings.get('status')}")
            print(f"   Strengths: {len(seo_findings.get('strengths', []))}")
            print(f"   Weaknesses: {len(seo_findings.get('weaknesses', []))}")
    except Exception as e:
        if log:
            print(f"   ⚠️  SEO audit failed: {e}")
        seo_findings = {"url": args.domain, "status": "error", "strengths": [], "weaknesses": [], "recommendations": []}
    if log:
        print()
    
    # Step 3: Perplexity Search
    if log:
        print("🌐 Searching business info via Perplexity...")
    try:
        perplexity_info = run_perplexity_search(args.business, args.industry)
        if log:
            print(f"   Found {len(perplexity_info)} chars of context")
    except Exception as e:
        if log:
            print(f"   ⚠️  Perplexity search failed: {e}")
        perplexity_info = f"Error retrieving business information: {e}"
    if log:
        print()
    
    # Step 4: Browser verification (optional, not implemented in this script)
    browser_notes = ""
    if not args.no_browser and log:
        print("🖥️  Browser verification: Not implemented (use verify_browser.py separately)")
        print("   (Continuing without browser check)")
    if log:
        print()
    
    # Step 5: Generate report
    if log:
        print("📝 Generating report...")
    report = generate_report(
        business_name=args.business,
        domain=args.domain,
        industry=args.industry,
        priority=args.priority,
        cluster=args.cluster,
        seo_findings=seo_findings,
        perplexity_info=perplexity_info,
        browser_notes=browser_notes,
    )
    
    # Step 5b: LLM completion — fill in TODO sections
    if log:
        print("🤖 Completing report sections with LLM...")
    report = complete_report_with_llm(report, args.business, args.domain, args.industry)
    if "[TODO:" in report:
        if log:
            print("   ⚠️  Some TODOs remain — LLM may have partially completed")
    else:
        if log:
            print("   ✅ All sections completed")
    if log:
        print()
    
    # Step 6: Save report
    report_file = save_report(args.business, args.cluster, report)
    if log:
        print(f"   ✅ Saved: {report_file}")
        print()
    
    # Step 7: Add to tracker
    tracker_success = False
    if not args.dry_run:
        if log:
            print("💾 Adding to prospect tracker...")
        tracker_success = add_to_tracker(
            business_name=args.business,
            industry=args.industry,
            priority=args.priority,
            cluster=args.cluster,
            domain=args.domain,
            report_file=report_file,
        )
        if log:
            if tracker_success:
                print("   ✅ Added to database")
            else:
                print("   ⚠️  Failed to add to database (report still saved)")
    elif log:
        print("💾 Dry-run: Skipping database update")
    
    # Output JSON summary
    summary = {
        "status": "success",
        "business": args.business,
        "domain": args.domain,
        "industry": args.industry,
        "priority": args.priority,
        "cluster": args.cluster,
        "report_path": str(report_file),
        "seo_status": seo_findings.get("status"),
        "weaknesses_count": len(seo_findings.get("weaknesses", [])),
        "research_summary": perplexity_info[:200] if perplexity_info else "",
        "audit_completed": seo_findings.get("status") != "error",
        "tracker_updated": tracker_success,
        "dry_run": args.dry_run,
    }
    
    if args.output_json:
        print(json.dumps(summary, indent=2))
    else:
        print()
        print("✅ Research complete!")
        print(f"   Report: {report_file}")
        print(f"   Next: Review report and run create_outreach.py")
        print()
        print(json.dumps(summary, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
