#!/usr/bin/env python3
"""
Generate personalized outreach package from prospect research.

Creates:
1. HTML email (mobile-responsive, branded)
2. Plain text email fallback
3. Review checklist
4. Outreach tracking file

Usage:
    create_outreach.py --report path/to/report.md --template casual --format html
    create_outreach.py --business "Name" --template professional --format plain
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path


WORKSPACE = Path.home() / ".openclaw" / "workspace"
PROSPECTS_DIR = WORKSPACE / "leads" / "prospects"
OUTREACH_DIR = WORKSPACE / "leads" / "outreach"
SKILL_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = SKILL_DIR / "assets" / "templates"
CONFIG_PATH = WORKSPACE / "leads" / "data" / "seo-prospector-config.json"

# Fallback config if no config file exists
# Buyers: copy references/config-template.json to ~/.openclaw/workspace/leads/data/seo-prospector-config.json
# and fill in your agency details. These placeholders remind you to set up your config.
DEFAULT_CONFIG = {
    "agency": {
        "name": "YOUR AGENCY NAME",
        "owner": "YOUR NAME",
        "phone": "(555) 000-0000",
        "email": "you@youragency.com",
        "website": "youragency.com",
        "city": "Your City",
        "tagline": "Helping local businesses get found online"
    },
    "outreach": {
        "default_tone": "casual",
        "signature_style": "friendly"
    }
}


def load_config() -> dict:
    """Load agency config, falling back to defaults."""
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_CONFIG


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


def find_latest_report(business_name: str = None, domain: str = None) -> Path | None:
    if not business_name and not domain:
        return None
    for report_dir in sorted(PROSPECTS_DIR.iterdir(), reverse=True):
        if not report_dir.is_dir():
            continue
        for report_file in report_dir.glob("*.md"):
            content = report_file.read_text()
            if business_name and business_name.lower() in content.lower():
                return report_file
            if domain and domain.lower() in content.lower():
                return report_file
    return None


def parse_report(report_path: Path) -> dict:
    """Extract key info from prospect report."""
    content = report_path.read_text()
    data = {
        "business": "",
        "domain": "",
        "industry": "",
        "priority": "",
        "cluster": "",
        "issues": [],
        "strengths": [],
        "contact_info": {}
    }

    # Business name
    business_match = re.search(
        r'^#\s*(.+?)(?:\s*[—–-]+\s*Prospect\s+(?:Report|Research))?\s*$', content, re.M
    )
    if not business_match:
        business_match = re.search(r'\*\*(?:Business|Name)(?:\s*Name)?:\*\*\s*(.+)', content, re.I)
    if business_match:
        data["business"] = business_match.group(1).strip()

    # Domain
    domain_match = re.search(r'\*\*(?:Website|Domain|URL):\*\*\s*(https?://)?(\S+)', content, re.I)
    if domain_match:
        data["domain"] = (domain_match.group(1) or "") + domain_match.group(2).strip()

    # Industry
    industry_match = re.search(r'\*\*Industry:\*\*\s*(.+)', content, re.I)
    if industry_match:
        data["industry"] = industry_match.group(1).strip()

    # Priority
    priority_match = re.search(r'\*\*Priority(?:\s+Level)?:\*\*\s*(\w+)', content, re.I)
    if priority_match:
        data["priority"] = priority_match.group(1).upper()

    # Contact info
    for field, patterns in [
        ("phone", [r'\*\*Phone:\*\*\s*(.+)']),
        ("email", [r'\*\*Email:\*\*\s*(.+)']),
        ("owner", [r'\*\*Owner(?:/Contact)?:\*\*\s*(.+)', r'\*\*Contact:\*\*\s*(.+)']),
    ]:
        for pat in patterns:
            m = re.search(pat, content, re.I)
            if m:
                data["contact_info"][field] = m.group(1).strip()
                break

    # Issues (multiple fallback patterns)
    issues = re.findall(r'❌\s*\*\*(.+?)\*\*', content)
    if not issues:
        issues = re.findall(r'❌\s*(.+)', content)
    if not issues:
        for section_name in ['Top fixes', 'Key Issues', 'Pain Points', 'SEO Weaknesses', 'Recommended Fixes']:
            section = re.search(
                rf'{section_name}[^\n]*\n(.*?)(?=\n##|\n\*\*[A-Z]|$)', content, re.I | re.S
            )
            if section:
                issues = re.findall(r'[-\*•]\s+(.+)', section.group(1))
                break
    if not issues:
        growth = re.search(
            r'(?:Potential Growth Areas|Growth Areas|Areas for Improvement)[^\n]*\n(.*?)(?=\n##|\n---)',
            content, re.I | re.S
        )
        if growth:
            issues = re.findall(r'[-\*•]\s+(.+)', growth.group(1))
    if not issues:
        seo_lines = re.findall(
            r'[-\*•]\s+(Missing [^.\n]+|No (?:schema|blog|H1|meta|sitemap|canonical|FAQ|alt text)[^.\n]*)',
            content, re.I
        )
        if seo_lines:
            issues = seo_lines
    data["issues"] = [i.strip() for i in issues if i.strip() and "no obvious" not in i.lower()][:5]

    # Strengths
    strengths = re.findall(r'✅\s*\*\*(.+?)\*\*', content)
    if not strengths:
        strengths = re.findall(r'✅\s*(.+)', content)
    if not strengths:
        pos_section = re.search(
            r'(?:Positive Signals|Business Strengths)[^\n]*\n(.*?)(?=\n##|\n---)',
            content, re.I | re.S
        )
        if pos_section:
            strengths = re.findall(r'[-✅•\*]\s+(.+)', pos_section.group(1))
    data["strengths"] = [s.strip() for s in strengths[:5]]

    # Executive summary
    exec_match = re.search(r'## Executive Summary\s*\n+(.*?)(?=\n##|\n---)', content, re.I | re.S)
    data["executive_summary"] = exec_match.group(1).strip() if exec_match else ""

    return data


def generate_html_email(data: dict, template_style: str, config: dict) -> str:
    """Generate HTML email from prospect data and HTML template."""
    agency = config.get("agency", {})
    business = data.get("business", "Business")
    contact = data.get("contact_info", {}).get("owner", "there")
    if contact == "there":
        words = business.split()
        if len(words) > 1 and words[0] not in ["The", "A", "An"]:
            contact = words[0]

    city = agency.get("city", "your area")
    industry = data.get("industry", "local businesses")
    issues = data.get("issues", [])[:3]
    strengths = data.get("strengths", [])

    # Build greeting
    if template_style == "professional":
        greeting = f"Hello {contact},"
    else:
        greeting = f"Hey {contact},"

    # Build opening with compliment + hook
    compliment = ""
    if strengths:
        compliment = f" I can tell you've put real work into it &mdash; {strengths[0].lower()}."

    if template_style == "professional":
        opening = (
            f"I came across {business} while researching {industry} in {city}.{compliment} "
            f"I noticed a few things on your website that might be affecting your visibility in Google search."
        )
    else:
        opening = (
            f"I was looking at {industry} in {city} and found {business}.{compliment} "
            f"Noticed a couple things on your site that might be keeping you from showing up in Google."
        )

    # Build issues section
    issues_html = ""
    if issues:
        if template_style == "professional":
            issues_intro = "Specifically, I found these opportunities:"
        else:
            issues_intro = "Here's what I spotted:"

        issue_rows = ""
        for issue in issues:
            issue_rows += f'''<tr>
                <td style="padding: 6px 0 6px 0; vertical-align: top; width: 24px;">
                  <span style="display: inline-block; width: 6px; height: 6px; background-color: #e74c3c; border-radius: 50%; margin-top: 8px;"></span>
                </td>
                <td style="padding: 6px 0 6px 8px; font-size: 15px; line-height: 1.5; color: #555555;">
                  {issue}
                </td>
              </tr>'''

        issues_html = f'''<p style="margin: 0 0 8px; font-size: 16px; line-height: 1.6; color: #333333;">
                      {issues_intro}
                    </p>
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin: 0 0 20px;">
                      {issue_rows}
                    </table>'''

    # Build value prop
    if template_style == "professional":
        value_prop = (
            f"These are relatively quick fixes that can significantly improve how {business} "
            f"appears in local search results. I specialize in helping {city} businesses "
            f"improve their web presence and search visibility."
        )
    else:
        value_prop = (
            f"These are pretty easy fixes with a big impact on where you show up in Google. "
            f"I help {city} businesses with exactly this kind of stuff."
        )

    # Build CTA
    if template_style == "professional":
        cta = (
            "If you'd like, I can send over a more detailed breakdown with specific recommendations "
            "&mdash; no obligation, just actionable feedback. Would that be helpful?"
        )
    else:
        cta = "Want me to send over a quick breakdown? No cost for the audit — just thought you'd want to know."

    # Build preheader
    if issues:
        preheader = f"I found a few quick wins for {business}'s website..."
    else:
        preheader = f"Quick note about {business}'s search visibility..."

    # Subject line
    if template_style == "professional":
        subject = f"Quick SEO win for {business}"
    else:
        subject = f"Noticed something on {business}'s website"

    # Load and populate HTML template
    template_path = TEMPLATES_DIR / "email-html.html"
    if template_path.exists():
        html = template_path.read_text()
    else:
        # Fallback inline template
        html = _fallback_html_template()

    # Replace placeholders
    replacements = {
        "{{SUBJECT}}": subject,
        "{{PREHEADER}}": preheader,
        "{{GREETING}}": greeting,
        "{{OPENING}}": opening,
        "{{ISSUES_INTRO}}": "",
        "{{VALUE_PROP}}": value_prop,
        "{{CTA}}": cta,
        "{{SENDER_NAME}}": agency.get("owner", "Your Name"),
        "{{AGENCY_NAME}}": agency.get("name", "Your Agency"),
        "{{PHONE}}": agency.get("phone", ""),
        "{{WEBSITE}}": agency.get("website", "youragency.com"),
    }

    for key, val in replacements.items():
        html = html.replace(key, val)

    # Handle conditional issues block
    if issues_html:
        # Remove the template conditional markers and insert real content
        html = re.sub(
            r'{{#IF_ISSUES}}.*?{{/IF_ISSUES}}',
            issues_html,
            html,
            flags=re.DOTALL
        )
    else:
        html = re.sub(r'{{#IF_ISSUES}}.*?{{/IF_ISSUES}}', '', html, flags=re.DOTALL)

    return html, subject


def generate_plain_email(data: dict, template_style: str, config: dict) -> str:
    """Generate plain text email from prospect data."""
    agency = config.get("agency", {})
    business = data.get("business", "Business")
    contact = data.get("contact_info", {}).get("owner", "there")
    if contact == "there":
        words = business.split()
        if len(words) > 1 and words[0] not in ["The", "A", "An"]:
            contact = words[0]

    city = agency.get("city", "your area")
    industry = data.get("industry", "local businesses")
    issues = data.get("issues", [])[:3]
    strengths = data.get("strengths", [])

    compliment = ""
    if strengths:
        compliment = f" I can see you've done a lot right — {strengths[0].lower()}."

    if template_style == "professional":
        email = f"Subject: Quick SEO win for {business}\n\n"
        email += f"Hello {contact},\n\n"
        email += f"I came across {business} while researching {industry} in {city}.{compliment}\n\n"
        email += "I noticed a few opportunities on your website that could be impacting your search visibility:\n\n"
        if issues:
            for issue in issues:
                email += f"  • {issue}\n"
        else:
            email += "  • Some on-page SEO elements could be improved for better Google rankings\n"
        email += f"\nThese are relatively quick fixes that can significantly improve how your site appears in Google search results.\n\n"
        email += f"I specialize in helping {city} businesses improve their web presence. If you'd like, I can send over a more detailed breakdown — no obligation, just actionable feedback.\n\n"
        email += "Would that be helpful?\n\n"
        email += f"Best regards,\n{agency.get('owner', 'Your Name')}\n{agency.get('name', 'Your Agency')}\n{agency.get('phone', '')}\n{agency.get('website', '')}\n"
    else:
        hook = ""
        if issues:
            first_issue = issues[0]
            if "h1" in first_issue.lower():
                hook = "Your site is missing an H1 tag — that's one of the main things Google looks at."
            elif "meta description" in first_issue.lower():
                hook = "Your site's missing a meta description, which is what shows up in Google search results."
            elif "schema" in first_issue.lower():
                hook = "Your site doesn't have schema markup, which means Google can't show your star rating or business info in search."
            elif "missing" in first_issue.lower():
                hook = f"I noticed: {first_issue}"
            else:
                hook = f"Quick heads up: {first_issue}"
        else:
            hook = "I noticed a few things on your website that might be keeping you from showing up better in Google."

        email = f"Subject: Noticed something on {business}'s website\n\n"
        email += f"Hey {contact},\n\n"
        email += f"I was looking at {industry} in {city} and came across {business}.{compliment} "
        email += f"But {hook.lower() if hook[0].isupper() else hook}\n\n"
        if len(issues) > 1:
            email += "A couple other things I noticed:\n"
            for issue in issues[1:3]:
                email += f"  • {issue}\n"
            email += "\n"
        email += "These are pretty easy fixes with big impact. Want me to send over a quick breakdown? No cost for the audit.\n\n"
        email += f"{agency.get('owner', 'Your Name')}\n{agency.get('name', 'Your Agency')}\n{agency.get('phone', '')}\n{agency.get('website', '')}\n"

    return email


def _fallback_html_template():
    """Minimal fallback if template file is missing."""
    return """<!DOCTYPE html><html><head><meta charset="utf-8"><title>{{SUBJECT}}</title></head>
<body style="font-family: sans-serif; color: #333; max-width: 580px; margin: 0 auto; padding: 20px;">
<p>{{GREETING}}</p><p>{{OPENING}}</p>
{{#IF_ISSUES}}<p>{{ISSUES_INTRO}}</p>{{/IF_ISSUES}}
<p>{{VALUE_PROP}}</p><p>{{CTA}}</p>
<hr><p><strong>{{SENDER_NAME}}</strong><br>{{AGENCY_NAME}}<br>{{PHONE}}<br>{{WEBSITE}}</p>
</body></html>"""


def generate_review_checklist(data: dict, config: dict) -> str:
    """Generate review checklist for manual verification."""
    agency = config.get("agency", {})
    business = data.get("business", "Business")
    domain = data.get("domain", "")

    checklist = f"""# Outreach Review: {business}

**Date:** {date.today().isoformat()}
**Priority:** {data.get('priority', 'MEDIUM')}
**Agency:** {agency.get('name', 'N/A')}

---

## Pre-Send Checklist

### Research Verification
- [ ] Business name spelling is correct
- [ ] Contact name is accurate (check LinkedIn/website)
- [ ] Domain is correct and accessible: {domain}
- [ ] Phone/email are current
- [ ] No recent negative news or closures

### Website Check (Open in Browser)
- [ ] Site loads properly (not under construction/parked)
- [ ] Issues mentioned in email are still present
- [ ] No major redesign since research
- [ ] Business appears active (recent social posts, reviews)

### Email Quality
- [ ] Personalization feels natural, not template-y
- [ ] Specific examples are accurate and verifiable
- [ ] Tone matches business type
- [ ] No typos or grammar issues
- [ ] CTA is clear and low-pressure

### Compliance
- [ ] Truthful claims only — no exaggeration
- [ ] Not spammy (one email, value-first approach)
- [ ] CAN-SPAM compliant (business contact, opt-out)

---

## Prospect Details

**Business:** {business}
**Domain:** {domain}
**Industry:** {data.get('industry', 'N/A')}
**Priority:** {data.get('priority', 'MEDIUM')}

**Contact:**
"""
    contact = data.get("contact_info", {})
    if contact:
        for key, value in contact.items():
            checklist += f"- {key.title()}: {value}\n"
    else:
        checklist += "- (None extracted — verify manually)\n"

    checklist += "\n**Issues Mentioned:**\n"
    issues = data.get("issues", [])
    if issues:
        for i, issue in enumerate(issues[:5], 1):
            checklist += f"{i}. {issue}\n"
    else:
        checklist += "(No specific issues extracted)\n"

    checklist += f"""
---

## Decision

- [ ] **Send** (email looks good)
- [ ] **Edit first** (notes below)
- [ ] **Skip** (reason: ____________)
- [ ] **Call instead** (phone is better for this one)

**Notes:**


---

## Tracking

**Sent:** ___________
**Response:** ___________
**Follow-up:** ___________
**Status:** pending / responded / qualified / not interested / no response
"""
    return checklist


def save_outreach_package(business_name: str, files: dict) -> Path:
    """Save outreach package to directory."""
    today = date.today().isoformat()
    slug = slugify(business_name)
    outreach_path = OUTREACH_DIR / f"{today}-{slug}"
    outreach_path.mkdir(parents=True, exist_ok=True)

    for filename, content in files.items():
        (outreach_path / filename).write_text(content)

    # Tracking file
    tracking = {
        "business": business_name,
        "created": today,
        "status": "pending_review",
        "sent_date": None,
        "response_date": None,
        "outcome": None,
        "files": list(files.keys())
    }
    (outreach_path / "tracking.json").write_text(json.dumps(tracking, indent=2))

    return outreach_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate personalized outreach package from prospect research"
    )
    parser.add_argument("--report", type=Path, help="Path to prospect report")
    parser.add_argument("--business", help="Business name (auto-find latest report)")
    parser.add_argument("--domain", help="Domain (auto-find latest report)")
    parser.add_argument("--template", choices=["casual", "professional"], default=None,
                       help="Email template style (default: from config)")
    parser.add_argument("--format", choices=["html", "plain", "both"], default="both",
                       help="Output format (default: both)")

    args = parser.parse_args()

    # Load config
    config = load_config()
    template_style = args.template or config.get("outreach", {}).get("default_tone", "casual")

    # Find report
    if args.report:
        report_path = args.report
    elif args.business or args.domain:
        print(f"Finding latest report...", file=sys.stderr)
        report_path = find_latest_report(args.business, args.domain)
        if not report_path:
            print(f"No report found for business={args.business}, domain={args.domain}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Must provide --report or --business/--domain", file=sys.stderr)
        sys.exit(1)

    if not report_path.exists():
        print(f"Report not found: {report_path}", file=sys.stderr)
        sys.exit(1)

    # Parse
    print(f"Parsing: {report_path.name}", file=sys.stderr)
    data = parse_report(report_path)
    if not data.get("business"):
        print(f"Warning: Could not extract business name from report", file=sys.stderr)

    # Generate outputs
    files = {}
    fmt = args.format

    if fmt in ("html", "both"):
        print(f"Generating HTML email ({template_style})...", file=sys.stderr)
        html_content, subject = generate_html_email(data, template_style, config)
        files["email-draft.html"] = html_content
        files["subject.txt"] = subject

    if fmt in ("plain", "both"):
        print(f"Generating plain text email ({template_style})...", file=sys.stderr)
        plain_content = generate_plain_email(data, template_style, config)
        files["email-draft.txt"] = plain_content

    print(f"Generating review checklist...", file=sys.stderr)
    review = generate_review_checklist(data, config)
    files["review.md"] = review

    # Save
    business_name = data.get("business") or report_path.stem
    outreach_path = save_outreach_package(business_name, files)

    print(f"\nOutreach package created: {outreach_path}")
    for f in sorted(files.keys()):
        print(f"  {outreach_path / f}")
    print(f"\nNext: Review the checklist, verify details, then send")


if __name__ == "__main__":
    main()
