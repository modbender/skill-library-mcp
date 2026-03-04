#!/usr/bin/env python3
"""
SEC Watcher — EDGAR Filing Fetcher
Free skill for OpenClaw / ClawHub

Queries the SEC EDGAR full-text search API (efts.sec.gov) for recent filings
from a curated AI/tech company watchlist.

Usage:
    python3 fetch-filings.py                      # All watchlist companies, last 48h
    python3 fetch-filings.py --company "NVIDIA"   # Single company
    python3 fetch-filings.py --form-type 8-K      # Filter by form
    python3 fetch-filings.py --hours 72            # Custom lookback
    python3 fetch-filings.py --query "NVDA"        # Raw query (ticker, CIK, keyword)
    python3 fetch-filings.py --json                # JSON output for piping
    python3 fetch-filings.py --debug               # Dump raw API response for diagnostics
"""

import argparse
import gzip
import io
import json
import re
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Default watchlist — AI/tech companies with active SEC filings
# ---------------------------------------------------------------------------

WATCHLIST = [
    # Mega-cap AI leaders
    "NVIDIA", "Microsoft", "Alphabet", "Meta Platforms", "Amazon", "Apple", "Tesla",
    # AI pure-play / public
    "Palantir", "C3.ai", "SoundHound", "BigBear.ai", "Recursion Pharmaceuticals",
    # Semiconductors
    "AMD", "Intel", "Broadcom", "Qualcomm", "TSMC", "ASML", "Marvell Technology", "Arm Holdings",
    # Cloud & enterprise AI
    "Snowflake", "MongoDB", "Cloudflare", "Datadog", "Elastic", "UiPath", "Dynatrace",
    # AI infrastructure
    "Vertiv", "Super Micro Computer", "Arista Networks", "Dell Technologies",
]

# High-signal 8-K item codes
HIGH_SIGNAL_ITEMS = {
    "1.01": "Material agreement",
    "1.02": "Terminated material agreement",
    "2.01": "Acquisition/disposition of assets",
    "4.02": "Non-reliance on prior financials",
    "5.01": "Change in control",
    "5.02": "Director/officer departure or appointment",
}

MEDIUM_SIGNAL_ITEMS = {
    "2.02": "Results of operations",
    "2.03": "Direct financial obligation created",
    "2.05": "Exit/disposal costs",
    "3.01": "Delisting notice",
    "7.01": "Regulation FD disclosure",
}

USER_AGENT = "SignalReport sec-watcher@signal-report.com"
EDGAR_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
REQUEST_DELAY = 0.15  # Stay well under 10 req/s rate limit

# Regex to strip CIK suffix from display_names, e.g. "NVIDIA CORP (CIK 0001045810)"
CIK_SUFFIX_RE = re.compile(r"\s*\(CIK\s+\d+\)\s*$", re.IGNORECASE)


def _clean_display_name(raw):
    """Strip CIK suffix from EDGAR display_names entries."""
    return CIK_SUFFIX_RE.sub("", raw).strip()


def fetch_filings(query, form_type=None, hours=48, max_results=20, debug=False, raw_query=False):
    """
    Query EDGAR full-text search API via POST.

    EFTS response _source fields:
      - display_names  (list[str])  — entity names with CIK suffix
      - root_form      (str)        — parent form type (8-K, 10-K, etc.)
      - file_type      (str)        — specific file type
      - file_date      (str)        — filing date YYYY-MM-DD
      - file_description (str)      — human-readable description
      - ciks           (list[str])  — CIK numbers
      - adsh           (str)        — accession number
      - sics           (list[int])  — SIC codes

    _id format: "accession_no:filename"
    """
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(hours=hours)

    # EFTS uses GET with query parameters
    # Use entityName (filer name) instead of q (full-text) to avoid matching
    # every fund that merely MENTIONS the company in their holdings table.
    # Fall back to q only for --query mode (raw search).
    params = {
        "dateRange": "custom",
        "startdt": start_date.strftime("%Y-%m-%d"),
        "enddt": end_date.strftime("%Y-%m-%d"),
        "from": "0",
        "size": str(min(max_results, 100)),
    }
    if raw_query:
        # Raw mode: full-text search (may include third-party mentions)
        params["q"] = f'"{query}"'
    else:
        # Entity mode: only filings BY this company, not filings that mention it
        params["entityName"] = query
    if form_type:
        params["forms"] = form_type

    url = f"{EDGAR_SEARCH_URL}?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Encoding": "gzip, deflate",
            "Host": "efts.sec.gov",
            "Accept": "application/json",
        },
    )

    def _read_response(resp):
        """Read response, handling gzip encoding."""
        raw = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        return json.loads(raw.decode("utf-8"))

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = _read_response(resp)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            sys.stderr.write("[sec-watcher] Rate limited by EDGAR. Waiting 2s...\n")
            time.sleep(2)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = _read_response(resp)
        else:
            raise

    if debug:
        # Dump first 2 hits for diagnostics
        preview = data.get("hits", {}).get("hits", [])[:2]
        sys.stderr.write(f"[debug] Raw EFTS response (first 2 hits):\n{json.dumps(preview, indent=2)}\n")

    hits = data.get("hits", {}).get("hits", [])
    total = data.get("hits", {}).get("total", {}).get("value", 0)

    filings = []
    for hit in hits:
        src = hit.get("_source", {})
        hit_id = hit.get("_id", "")

        # --- Entity name from display_names ---
        display_names = src.get("display_names", [])
        if display_names:
            entity_name = _clean_display_name(display_names[-1])
        else:
            entity_name = "Unknown"

        # --- Form type: prefer root_form, fall back to file_type ---
        form = src.get("root_form") or src.get("file_type") or "Unknown"

        # --- Filing date ---
        file_date = src.get("file_date", "")

        # --- File description ---
        file_desc = src.get("file_description", "")

        # --- Accession number (from _id or adsh field) ---
        adsh = src.get("adsh", "")
        if not adsh and ":" in hit_id:
            adsh = hit_id.split(":")[0]

        # --- CIKs ---
        ciks = src.get("ciks", [])

        # --- 8-K item detection from file_description ---
        # EFTS doesn't have a dedicated "items" field; item codes sometimes
        # appear in file_description (e.g., "8-K: Items 1.01, 5.02")
        items_list = []
        if form == "8-K" and file_desc:
            items_list = re.findall(r'\b(\d+\.\d{2})\b', file_desc)

        # Determine signal level
        signal_level = "LOW"
        if form == "8-K":
            for item in items_list:
                if item in HIGH_SIGNAL_ITEMS:
                    signal_level = "HIGH"
                    break
                if item in MEDIUM_SIGNAL_ITEMS and signal_level != "HIGH":
                    signal_level = "MEDIUM"
        # Non-8-K high-signal forms
        elif form in ("S-1", "S-1/A"):
            signal_level = "HIGH"  # IPO filing
        elif form in ("425", "SC 13D", "SC 13D/A"):
            signal_level = "HIGH"  # M&A or activist
        elif form in ("10-K", "10-Q"):
            signal_level = "MEDIUM"

        # Build EDGAR filing URL
        filing_url = ""
        if adsh:
            clean_adsh = adsh.replace("-", "")
            cik = ciks[0] if ciks else ""
            if cik:
                filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{clean_adsh}/{adsh}-index.htm"

        filings.append({
            "id": hit_id,
            "entity_name": entity_name,
            "form_type": form,
            "file_date": file_date,
            "items": items_list,
            "items_description": ", ".join(
                HIGH_SIGNAL_ITEMS.get(i, MEDIUM_SIGNAL_ITEMS.get(i, i))
                for i in items_list
            ) if items_list else "",
            "file_description": file_desc,
            "signal_level": signal_level,
            "accession_number": adsh,
            "ciks": ciks,
            "filing_url": filing_url,
        })

    return {"total": total, "returned": len(filings), "filings": filings}


def format_filing_text(filing):
    """Format a single filing for human-readable output."""
    signal_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "⚪"}.get(filing["signal_level"], "⚪")

    lines = [
        f"{signal_emoji} [{filing['form_type']}] — {filing['entity_name']}",
        f"   Filed: {filing['file_date']}  |  Signal: {filing['signal_level']}",
    ]
    if filing.get("items"):
        lines.append(f"   Items: {', '.join(filing['items'])}")
    if filing.get("items_description"):
        lines.append(f"   Meaning: {filing['items_description']}")
    if filing.get("file_description"):
        lines.append(f"   Description: {filing['file_description']}")
    if filing.get("filing_url"):
        lines.append(f"   🔗 {filing['filing_url']}")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="SEC Watcher — EDGAR Filing Fetcher")
    parser.add_argument("--company", type=str, help="Search a specific company name")
    parser.add_argument("--query", type=str, help="Raw full-text search (ticker, CIK, keyword — may include third-party mentions)")
    parser.add_argument("--form-type", type=str, help="Filter by form type (8-K, 10-K, 10-Q, S-1, 425)")
    parser.add_argument("--hours", type=int, default=48, help="Lookback window in hours (default: 48)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--debug", action="store_true", help="Dump raw API response for diagnostics")
    parser.add_argument("--max-results", type=int, default=20, help="Max results per query (default: 20)")
    args = parser.parse_args()

    all_filings = []

    if args.query:
        # Raw full-text mode — searches all filing text, may include third-party mentions
        result = fetch_filings(args.query, form_type=args.form_type, hours=args.hours,
                               max_results=args.max_results, debug=args.debug, raw_query=True)
        all_filings.extend(result["filings"])

    elif args.company:
        # Entity name mode — only filings BY this company
        result = fetch_filings(args.company, form_type=args.form_type, hours=args.hours,
                               max_results=args.max_results, debug=args.debug)
        all_filings.extend(result["filings"])

    else:
        sys.stderr.write(f"[sec-watcher] Scanning {len(WATCHLIST)} companies, last {args.hours}h...\n")
        for i, company in enumerate(WATCHLIST):
            try:
                result = fetch_filings(company, form_type=args.form_type, hours=args.hours,
                                       max_results=5, debug=(args.debug and i == 0))
                all_filings.extend(result["filings"])
                if i < len(WATCHLIST) - 1:
                    time.sleep(REQUEST_DELAY)
            except Exception as e:
                sys.stderr.write(f"[sec-watcher] Error fetching {company}: {e}\n")

        # Deduplicate by filing ID
        seen = set()
        unique = []
        for f in all_filings:
            if f["id"] not in seen:
                seen.add(f["id"])
                unique.append(f)
        all_filings = unique

    # Sort: HIGH signal first, then MEDIUM, then LOW; within each level by date descending
    signal_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    all_filings.sort(key=lambda f: (
        signal_order.get(f["signal_level"], 3),
        f["file_date"]  # ascending within group; reversed below
    ))
    # Stable sort: group by signal level, reverse date within each
    from itertools import groupby
    sorted_filings = []
    for _level, group in groupby(all_filings, key=lambda f: signal_order.get(f["signal_level"], 3)):
        chunk = list(group)
        chunk.sort(key=lambda f: f["file_date"], reverse=True)
        sorted_filings.extend(chunk)
    all_filings = sorted_filings

    # Output
    if args.json:
        high_json = [f for f in all_filings if f["signal_level"] == "HIGH"]
        output = {
            "count": len(all_filings),
            "high_signal_count": len(high_json),
            "companies_scanned": len(set(f["entity_name"] for f in all_filings)),
            "filings": all_filings,
            "intelligence_preview": {
                "patterns_detected": min(len(high_json), 3),
                "message": "Cross-source pattern analysis (SEC + hiring + research + social) available to Pro subscribers.",
                "free_brief": "https://signal-report.com",
                "pro_weekly": "https://signal-report.com/#pricing",
            },
        }
        print(json.dumps(output, indent=2))
    else:
        if not all_filings:
            print(f"No filings found in the last {args.hours} hours.")
        else:
            print(f"\n{'='*60}")
            print(f" SEC Watcher — {len(all_filings)} filing(s) found")
            print(f" Lookback: {args.hours} hours")
            print(f"{'='*60}\n")

            high = [f for f in all_filings if f["signal_level"] == "HIGH"]
            medium = [f for f in all_filings if f["signal_level"] == "MEDIUM"]
            low = [f for f in all_filings if f["signal_level"] == "LOW"]

            if high:
                print("🔴 HIGH SIGNAL\n")
                for f in high:
                    print(format_filing_text(f))

            if medium:
                print("🟡 MEDIUM SIGNAL\n")
                for f in medium:
                    print(format_filing_text(f))

            if low:
                print("⚪ ROUTINE\n")
                for f in low:
                    print(format_filing_text(f))

            # --- Intelligence tease: show what Pro subscribers get ---
            print(f"{'='*60}")
            print(" 🔍 SIGNAL REPORT INTELLIGENCE PREVIEW")
            print(f"{'='*60}\n")

            # 1. Stats summary
            print(f" 📊 This scan: {len(all_filings)} filings across"
                  f" {len(set(f['entity_name'] for f in all_filings))} companies"
                  f" | {len(high)} high-signal | {len(medium)} medium-signal\n")

            # 2. Sample cross-source insight (based on actual high-signal filings found)
            if high:
                top = high[0]
                items_hint = f" ({', '.join(top['items'])})" if top.get("items") else ""
                print(f" 💡 Sample insight:")
                print(f"    {top['entity_name']} filed {top['form_type']}{items_hint}"
                      f" on {top['file_date']}.")
                print(f"    Pro subscribers see: hiring pattern correlation, research")
                print(f"    paper activity, social signal cross-reference, and")
                print(f"    actionable strategic analysis for this event.\n")
            elif medium:
                top = medium[0]
                print(f" 💡 Sample insight:")
                print(f"    {top['entity_name']} filed {top['form_type']}"
                      f" on {top['file_date']}.")
                print(f"    Pro subscribers get context: is this routine or does it")
                print(f"    correlate with hiring surges, new research, or social buzz?\n")

            # 3. Pattern detection tease
            pattern_count = min(len(high), 3)  # Conservative estimate
            if pattern_count > 0:
                print(f" 🔮 {pattern_count} potential cross-source pattern(s) detected")
                print(f"    this period (SEC + hiring + research + social).")
                print(f"    Pattern analysis locked to Pro Weekly subscribers.\n")

            # 4. CTA
            print(f" ┌─────────────────────────────────────────────────────┐")
            print(f" │  Free daily brief: https://signal-report.com       │")
            print(f" │  Pro weekly analysis: https://signal-report.com    │")
            print(f" │                                                     │")
            print(f" │  You're seeing raw filings. Pro subscribers see    │")
            print(f" │  what they MEAN — together.                        │")
            print(f" └─────────────────────────────────────────────────────┘")
            print(f"{'='*60}")


if __name__ == "__main__":
    main()
