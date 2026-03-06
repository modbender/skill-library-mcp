#!/usr/bin/env python3
"""
Shipment Tracker

Track packages across multiple carriers by reading a shipments markdown file.
Detects carrier from tracking number patterns and checks status via carrier
tracking pages using urllib (no browser needed for basic status).

Read-only on the shipments file — does not modify it. The agent handles
updates (marking delivered, removing entries) based on the output.

Usage:
    python3 shipment_tracker.py /path/to/shipments.md
    python3 shipment_tracker.py /path/to/shipments.md --format json
    python3 shipment_tracker.py --detect 9449050899562006763949

Carriers supported:
    USPS, UPS, FedEx, DHL, Amazon, OnTrac, LaserShip

No subprocess calls. No shell execution. No file writes.
Network: HTTPS GET to carrier tracking pages only.
"""

import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import NamedTuple


class Shipment(NamedTuple):
    order: str
    item: str
    carrier: str
    tracking: str
    link: str
    added: str


# Carrier detection patterns (order matters — more specific first)
_CARRIER_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("USPS", re.compile(r"^(94|93|92|94\d{18,22}|7\d{19}|82\d{8})$")),
    ("USPS", re.compile(r"^(9[2-5]\d{20,26})$")),
    ("UPS", re.compile(r"^1Z[A-Z0-9]{16}$", re.IGNORECASE)),
    ("FedEx", re.compile(r"^(\d{12}|\d{15}|\d{20}|96\d{20}|61\d{18})$")),
    ("FedEx", re.compile(r"^7489\d{16}$")),
    ("DHL", re.compile(r"^\d{10,11}$")),
    ("DHL", re.compile(r"^[A-Z]{3}\d{7}$", re.IGNORECASE)),
    ("Amazon", re.compile(r"^TBA\d{12,}$", re.IGNORECASE)),
    ("OnTrac", re.compile(r"^(C|D)\d{14}$")),
    ("LaserShip", re.compile(r"^L[A-Z]\d{8,}$", re.IGNORECASE)),
]

# Carrier tracking URL templates
_TRACKING_URLS: dict[str, str] = {
    "USPS": "https://tools.usps.com/go/TrackConfirmAction.action?tLabels={tracking}",
    "UPS": "https://www.ups.com/track?tracknum={tracking}",
    "FedEx": "https://www.fedex.com/fedextrack/?trknbr={tracking}",
    "DHL": "https://www.dhl.com/us-en/home/tracking/tracking-parcel.html?submit=1&tracking-id={tracking}",
    "Amazon": "https://track.amazon.com/tracking/{tracking}",
    "OnTrac": "https://www.ontrac.com/tracking/?number={tracking}",
    "LaserShip": "https://www.lasership.com/track/{tracking}",
}


def detect_carrier(tracking: str) -> str | None:
    """Detect carrier from tracking number pattern."""
    clean = tracking.strip().replace(" ", "")
    for carrier, pattern in _CARRIER_PATTERNS:
        if pattern.match(clean):
            return carrier
    return None


def get_tracking_url(carrier: str, tracking: str) -> str:
    """Generate the tracking URL for a carrier and tracking number."""
    template = _TRACKING_URLS.get(carrier)
    if template:
        return template.format(tracking=tracking)
    return ""


def parse_shipments_file(path: str) -> list[Shipment]:
    """Parse a markdown shipments file with a table format.

    Expected format:
    | Order | Item | Carrier | Tracking | Link | Added |
    |-------|------|---------|----------|------|-------|
    | ... | ... | ... | ... | ... | ... |
    """
    shipments: list[Shipment] = []
    try:
        text = Path(path).read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError) as e:
        print(f"Error reading shipments file: {e}", file=sys.stderr)
        return shipments

    lines = text.strip().split("\n")
    header_found = False
    col_indices: dict[str, int] = {}

    for line in lines:
        line = line.strip()
        if not line.startswith("|"):
            continue

        cells = [c.strip() for c in line.split("|")[1:-1]]  # skip empty first/last from split

        # Skip separator rows
        if all(re.match(r"^[-:]+$", c) for c in cells):
            continue

        # Detect header row
        if not header_found:
            lower_cells = [c.lower() for c in cells]
            for i, cell in enumerate(lower_cells):
                if "order" in cell:
                    col_indices["order"] = i
                elif "item" in cell:
                    col_indices["item"] = i
                elif "carrier" in cell:
                    col_indices["carrier"] = i
                elif "tracking" in cell:
                    col_indices["tracking"] = i
                elif "link" in cell:
                    col_indices["link"] = i
                elif "added" in cell or "date" in cell:
                    col_indices["added"] = i
            header_found = True
            continue

        # Parse data rows
        if header_found and len(cells) >= 2:
            def get_col(name: str, default: str = "") -> str:
                idx = col_indices.get(name)
                if idx is not None and idx < len(cells):
                    return cells[idx]
                return default

            tracking = get_col("tracking")
            carrier = get_col("carrier")
            link_raw = get_col("link")

            # Extract URL from markdown link syntax [text](url)
            link_match = re.search(r"\[.*?\]\((.*?)\)", link_raw)
            link = link_match.group(1) if link_match else link_raw

            # Auto-detect carrier if not specified
            if not carrier and tracking:
                carrier = detect_carrier(tracking) or "Unknown"

            # Auto-generate tracking link if not provided
            if not link and tracking and carrier:
                link = get_tracking_url(carrier, tracking)

            if tracking:
                shipments.append(Shipment(
                    order=get_col("order"),
                    item=get_col("item"),
                    carrier=carrier,
                    tracking=tracking,
                    link=link,
                    added=get_col("added"),
                ))

    return shipments


def check_usps_status(tracking: str) -> dict | None:
    """Try to get USPS status via their tracking page.

    Returns basic status info or None if unable to parse.
    This is a best-effort approach — USPS pages are JS-heavy,
    so this may only work for basic status extraction.
    For full tracking history, use browser-use.
    """
    url = f"https://tools.usps.com/go/TrackConfirmAction.action?tLabels={tracking}"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; shipment-tracker/1.0)",
            "Accept": "text/html",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")

            # Try to extract status from meta tags or structured data
            status_match = re.search(
                r'class="[^"]*delivery_status[^"]*"[^>]*>([^<]+)', html
            )
            if status_match:
                return {"status": status_match.group(1).strip(), "source": "web"}

            # Try tracking banner
            banner_match = re.search(
                r'class="[^"]*tb-status[^"]*"[^>]*>([^<]+)', html
            )
            if banner_match:
                return {"status": banner_match.group(1).strip(), "source": "web"}

            return None
    except (urllib.error.URLError, OSError):
        return None


def check_status(shipment: Shipment) -> dict:
    """Check tracking status for a shipment.

    Strategy:
    1. Try basic HTTP request first (fast, VirusTotal-compliant)
    2. If HTTP fails, provide structured guidance for browser-use fallback
    """
    result = {
        "order": shipment.order,
        "item": shipment.item,
        "carrier": shipment.carrier,
        "tracking": shipment.tracking,
        "tracking_url": shipment.link or get_tracking_url(shipment.carrier, shipment.tracking),
        "added": shipment.added,
        "status": None,
        "method": None,
        "needs_browser_use": False,
    }

    # Try basic HTTP check first (carrier-specific)
    carrier_base = shipment.carrier.split()[0].upper() if shipment.carrier else ""
    
    if carrier_base == "USPS":
        usps_status = check_usps_status(shipment.tracking)
        if usps_status:
            result["status"] = usps_status["status"]
            result["method"] = "http"
            return result
    
    # TODO: Add basic HTTP checks for other carriers (UPS, FedEx, etc.)
    
    # HTTP method failed or not implemented for this carrier
    result["status"] = "Needs browser-use check"
    result["method"] = "manual"
    result["needs_browser_use"] = True
    result["browser_use_command"] = f"""python3 -c "
import asyncio
from browser_use import Agent, Browser, ChatBrowserUse
async def main():
    browser = Browser(use_cloud=True)
    llm = ChatBrowserUse()
    agent = Agent(
        task='Go to {result["tracking_url"]} and extract the current tracking status, delivery date, and location',
        llm=llm, browser=browser
    )
    result = await agent.run(max_steps=10)
    print('TRACKING:', result)
asyncio.run(main())
\""""
    
    return result


def main() -> None:
    output_format = "text"
    detect_mode = False
    shipments_path = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--format" and i + 1 < len(args):
            output_format = args[i + 1]
            i += 2
        elif args[i] == "--detect" and i + 1 < len(args):
            detect_mode = True
            tracking_num = args[i + 1]
            i += 2
        else:
            shipments_path = args[i]
            i += 1

    # Carrier detection mode
    if detect_mode:
        carrier = detect_carrier(tracking_num)
        url = get_tracking_url(carrier, tracking_num) if carrier else ""
        result = {
            "tracking": tracking_num,
            "carrier": carrier or "Unknown",
            "tracking_url": url,
        }
        if output_format == "json":
            print(json.dumps(result, indent=2))
        else:
            print(f"Tracking: {tracking_num}")
            print(f"Carrier:  {carrier or 'Unknown'}")
            if url:
                print(f"URL:      {url}")
        return

    # Shipment tracking mode
    if not shipments_path:
        print("Usage: shipment_tracker.py <shipments.md> [--format json]", file=sys.stderr)
        print("       shipment_tracker.py --detect <tracking_number>", file=sys.stderr)
        sys.exit(1)

    shipments = parse_shipments_file(shipments_path)

    if not shipments:
        result = {"shipments": [], "count": 0}
        if output_format == "json":
            print(json.dumps(result, indent=2))
        else:
            print("No active shipments found.")
        return

    results = []
    for s in shipments:
        status = check_status(s)
        results.append(status)

    browser_use_count = sum(1 for r in results if r.get("needs_browser_use", False))
    
    output = {
        "shipments": results,
        "count": len(results),
        "needs_browser_use_count": browser_use_count,
    }

    if output_format == "json":
        print(json.dumps(output, indent=2))
    else:
        print(f"📦 {len(results)} active shipment(s)")
        if browser_use_count > 0:
            print(f"🌐 {browser_use_count} need(s) browser-use for detailed tracking")
        print()
        
        for r in results:
            print(f"  {r['item'] or r['order'] or 'Package'}")
            print(f"    Carrier:  {r['carrier']}")
            print(f"    Tracking: {r['tracking']}")
            print(f"    Status:   {r['status']}")
            print(f"    Method:   {r.get('method', 'unknown')}")
            print(f"    URL:      {r['tracking_url']}")
            
            if r.get("needs_browser_use"):
                print(f"    🌐 Browser-use command:")
                print(f"        {r.get('browser_use_command', '').strip()}")
            print()


if __name__ == "__main__":
    main()
