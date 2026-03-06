---
name: lead-scorer
description: Score a website lead 0–100 based on audit signals from the website-auditor skill, assign a priority tier (Hot/Warm/Lukewarm/Cold), and write the result to a Google Sheet. Applies a weighted rubric across 8 audit dimensions. Use as the final step in the lead list building pipeline after website-auditor and contact-enrichment have run. Requires GOOGLE_SHEET_NAME and GOOGLE_CREDS_FILE for Google Sheets output.
metadata:
  requires:
    packages: [gspread, google-auth]
  optionalEnv: [GOOGLE_SHEET_NAME, GOOGLE_CREDS_FILE]
---

# Lead Scorer Skill

Takes a completed audit dict → applies scoring rubric → assigns tier → writes row to Google Sheet.

## Scoring Rubric (0–100 scale)

Higher score = hotter lead = more likely to need a new website.

```python
SCORING_RUBRIC = [
    # Signal                            Condition                           Points
    ("dead_site",        lambda a: a.get("status_code") in ("DEAD","TIMEOUT","SSL_ERROR"), 40),
    ("copyright_5plus",  lambda a: (a.get("years_outdated") or 0) >= 5,    35),
    ("pagespeed_low",    lambda a: 0 < (a.get("pagespeed_mobile") or 101) < 50, 30),
    ("copyright_3to4",   lambda a: 3 <= (a.get("years_outdated") or 0) < 5, 25),
    ("no_ssl",           lambda a: not a.get("has_ssl"),                    25),
    ("not_mobile",       lambda a: not a.get("is_mobile_friendly"),         20),
    ("outdated_cms",     lambda a: a.get("has_outdated_cms"),               20),
    ("no_contact_found", lambda a: not a.get("primary_email") and not a.get("primary_phone"), 20),
    ("pagespeed_mid",    lambda a: 50 <= (a.get("pagespeed_mobile") or 101) < 70, 15),
    ("table_layout",     lambda a: "table_layout" in (a.get("design_signals") or []), 15),
    ("copyright_1to2",   lambda a: 1 <= (a.get("years_outdated") or 0) < 3, 10),
    ("no_open_graph",    lambda a: "no_open_graph" in (a.get("design_signals") or []), 10),
    ("flash_detected",   lambda a: "flash_detected" in (a.get("design_signals") or []), 20),
    ("uses_frames",      lambda a: "uses_frames" in (a.get("design_signals") or []), 20),
    ("no_meta_desc",     lambda a: "no_meta_description" in (a.get("design_signals") or []), 5),
    ("no_favicon",       lambda a: "no_favicon" in (a.get("design_signals") or []), 5),
    ("font_tags",        lambda a: "font_tags" in (a.get("design_signals") or []), 10),
    ("heavy_inline",     lambda a: "heavy_inline_styles" in (a.get("design_signals") or []), 8),
]
```

## Scoring Function

```python
def score_lead(audit: dict) -> dict:
    """
    Apply rubric to audit dict.
    Returns audit dict + score + tier + issues list + tier emoji.
    """
    score = 0
    issues = []
    matched_rules = []
    
    for rule_name, condition, points in SCORING_RUBRIC:
        try:
            if condition(audit):
                score += points
                matched_rules.append(f"{rule_name} (+{points})")
                issues.append(ISSUE_LABELS.get(rule_name, rule_name))
        except Exception:
            pass
    
    # Cap at 100
    score = min(score, 100)
    
    # Assign tier
    if score >= 80:
        tier = "🔥 Hot"
        tier_code = "hot"
    elif score >= 50:
        tier = "🟡 Warm"
        tier_code = "warm"
    elif score >= 25:
        tier = "🔵 Lukewarm"
        tier_code = "lukewarm"
    else:
        tier = "⚪ Cold"
        tier_code = "cold"
    
    return {
        **audit,
        "lead_score": score,
        "tier": tier,
        "tier_code": tier_code,
        "issues": issues,
        "score_breakdown": matched_rules
    }

# Human-readable issue labels
ISSUE_LABELS = {
    "dead_site":        "Site is dead/unreachable",
    "copyright_5plus":  f"Copyright {'{years}'} years old",
    "copyright_3to4":   "Copyright 3–4 years old",
    "copyright_1to2":   "Copyright 1–2 years old",
    "pagespeed_low":    "PageSpeed score under 50 (mobile)",
    "pagespeed_mid":    "PageSpeed score 50–69 (mobile)",
    "no_ssl":           "No SSL / HTTPS",
    "not_mobile":       "Not mobile responsive",
    "outdated_cms":     "Outdated CMS or tech stack",
    "no_contact_found": "No contact info found on site",
    "table_layout":     "Table-based layout (pre-2010 design)",
    "no_open_graph":    "No social meta tags",
    "flash_detected":   "Flash / Silverlight detected",
    "uses_frames":      "Uses HTML frames",
    "no_meta_desc":     "Missing meta description",
    "no_favicon":       "No favicon",
    "font_tags":        "Font tags detected (ancient HTML)",
    "heavy_inline":     "Heavy inline CSS styles",
}
```

## Google Sheets Integration

```python
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

SHEET_COLUMNS = [
    "Date Found", "Business Name", "URL", "Lead Score", "Tier",
    "Primary Email", "All Emails", "Phone", "Copyright Year",
    "Tech Stack", "PageSpeed (Mobile)", "Has SSL", "Mobile Friendly",
    "Issues Found", "Score Breakdown", "Status", "Notes"
]

def get_sheet(sheet_name: str = None, creds_file: str = None):
    """Authenticate and return the target Google Sheet."""
    sheet_name = sheet_name or os.environ.get("GOOGLE_SHEET_NAME", "Website Leads")
    creds_file = creds_file or os.environ.get("GOOGLE_CREDS_FILE", "credentials.json")
    
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
    client = gspread.authorize(creds)
    
    try:
        sheet = client.open(sheet_name).sheet1
    except gspread.SpreadsheetNotFound:
        # Create the sheet if it doesn't exist
        spreadsheet = client.create(sheet_name)
        spreadsheet.share(None, perm_type="anyone", role="writer")
        sheet = spreadsheet.sheet1
        # Write headers
        sheet.append_row(SHEET_COLUMNS)
        print(f"Created new sheet: {sheet_name}")
    
    return sheet

def ensure_headers(sheet):
    """Make sure the header row exists."""
    first_row = sheet.row_values(1)
    if not first_row or first_row[0] != "Date Found":
        sheet.insert_row(SHEET_COLUMNS, index=1)

def lead_to_row(lead: dict) -> list:
    """Convert a scored lead dict to a sheet row."""
    return [
        datetime.now().strftime("%Y-%m-%d"),
        lead.get("business_name", ""),
        lead.get("url", ""),
        lead.get("lead_score", 0),
        lead.get("tier", ""),
        lead.get("primary_email", ""),
        ", ".join(lead.get("emails", [])),
        lead.get("primary_phone", ""),
        lead.get("copyright_year", ""),
        ", ".join(lead.get("tech_stack", [])[:3]),          # Top 3 techs
        lead.get("pagespeed_mobile", ""),
        "✅" if lead.get("has_ssl") else "❌",
        "✅" if lead.get("is_mobile_friendly") else "❌",
        " | ".join(lead.get("issues", [])[:5]),             # Top 5 issues
        " | ".join(lead.get("score_breakdown", [])[:5]),
        "New",
        ""
    ]

def write_lead_to_sheet(lead: dict, sheet=None) -> bool:
    """Score the lead and write it to the Google Sheet."""
    if sheet is None:
        sheet = get_sheet()
    ensure_headers(sheet)
    
    scored = score_lead(lead)
    row = lead_to_row(scored)
    
    try:
        sheet.append_row(row, value_input_option="USER_ENTERED")
        return True
    except Exception as e:
        print(f"Sheet write error: {e}")
        return False

def write_leads_batch(leads: list[dict], sheet=None) -> int:
    """Write multiple leads at once. Returns count written."""
    if sheet is None:
        sheet = get_sheet()
    ensure_headers(sheet)
    
    rows = []
    for lead in leads:
        scored = score_lead(lead)
        if scored.get("lead_score", 0) >= 0:  # Always write (filter upstream)
            rows.append(lead_to_row(scored))
    
    if rows:
        sheet.append_rows(rows, value_input_option="USER_ENTERED")
    
    return len(rows)
```

## Apply Conditional Formatting (Color by Tier)

```python
def apply_conditional_formatting(spreadsheet_id: str, creds_file: str = None):
    """
    Apply color-coding to the sheet based on Lead Score in column D.
    Requires google-api-python-client (pip install google-api-python-client).
    """
    from googleapiclient.discovery import build
    from google.oauth2.service_account import Credentials
    
    creds_file = creds_file or os.environ.get("GOOGLE_CREDS_FILE", "credentials.json")
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
    service = build("sheets", "v4", credentials=creds)
    
    rules = [
        # 🔥 Hot (≥80) — red background
        {"ranges": [{"sheetId": 0, "startRowIndex": 1, "endRowIndex": 1000,
                     "startColumnIndex": 0, "endColumnIndex": 17}],
         "booleanRule": {
             "condition": {"type": "NUMBER_GREATER_THAN_EQ",
                           "values": [{"userEnteredValue": "80"}]},
             "format": {"backgroundColor": {"red": 1.0, "green": 0.8, "blue": 0.8}}
         }},
        # 🟡 Warm (50–79) — yellow background
        {"ranges": [{"sheetId": 0, "startRowIndex": 1, "endRowIndex": 1000,
                     "startColumnIndex": 0, "endColumnIndex": 17}],
         "booleanRule": {
             "condition": {"type": "NUMBER_BETWEEN",
                           "values": [{"userEnteredValue": "50"}, {"userEnteredValue": "79"}]},
             "format": {"backgroundColor": {"red": 1.0, "green": 0.95, "blue": 0.7}}
         }},
        # 🔵 Lukewarm (25–49) — blue background
        {"ranges": [{"sheetId": 0, "startRowIndex": 1, "endRowIndex": 1000,
                     "startColumnIndex": 0, "endColumnIndex": 17}],
         "booleanRule": {
             "condition": {"type": "NUMBER_BETWEEN",
                           "values": [{"userEnteredValue": "25"}, {"userEnteredValue": "49"}]},
             "format": {"backgroundColor": {"red": 0.8, "green": 0.9, "blue": 1.0}}
         }},
    ]
    
    # The "D" column (index 3) is used for conditional formatting range
    body = {"requests": [{"addConditionalFormatRule": {"rule": r, "index": i}}
                         for i, r in enumerate(rules)]}
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
    print("Conditional formatting applied ✅")
```

## Full Pipeline Usage Example

```python
# Putting it all together
from lead_list_builder import run_pipeline

results = run_pipeline(
    niche="landscaping",
    city="Portland OR",
    limit=25,
    min_score=30,
    sheet_name="Portland Landscaping Leads"
)

# Output:
# ✅ Scan complete.
# URLs scanned: 38
# Leads written: 25
# 🔥 Hot: 8 | 🟡 Warm: 11 | 🔵 Lukewarm: 6 | ⚪ Cold: 13
```

## Score Interpretation Guide

| Score | Tier | Meaning | Action |
|---|---|---|---|
| 80–100 | 🔥 Hot | Site is dead, ancient, or totally broken | Call or email today |
| 50–79 | 🟡 Warm | Multiple serious issues, clear need | Follow up this week |
| 25–49 | 🔵 Lukewarm | Some issues, may be open to upgrade | Low-priority outreach |
| 0–24 | ⚪ Cold | Site is decent, not a strong prospect | Skip or archive |
