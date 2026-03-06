#!/usr/bin/env python3
"""Duffel Flights API CLI — search, book, and manage flights.

Usage:
  duffel.py search --from MIA --to LHR --date 2026-04-15 [options]
  duffel.py offer <id-or-index>
  duffel.py book <id-or-index> --pax "LAST/FIRST TITLE DOB EMAIL PHONE NATIONALITY GENDER"
  duffel.py order <order-id>
  duffel.py cancel <order-id> [--confirm]
  duffel.py seatmap <id-or-index>
  duffel.py places <query>
"""

import argparse
import json
import os
import sys
import textwrap
from datetime import datetime

import requests

BASE_URL = "https://api.duffel.com"
LAST_SEARCH_FILE = "/tmp/duffel-last-search.json"

# ── Helpers ──────────────────────────────────────────────────────────────

def get_token():
    token = os.environ.get("DUFFEL_TOKEN")
    if not token:
        print("Error: DUFFEL_TOKEN environment variable not set.")
        print("Get your token at https://app.duffel.com → Developers → Access Tokens")
        sys.exit(1)
    return token

def headers():
    return {
        "Authorization": f"Bearer {get_token()}",
        "Duffel-Version": "v2",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

def api_get(path, params=None):
    r = requests.get(f"{BASE_URL}{path}", headers=headers(), params=params, timeout=30)
    return handle_response(r)

def api_post(path, payload):
    r = requests.post(f"{BASE_URL}{path}", headers=headers(), json=payload, timeout=30)
    return handle_response(r)

def handle_response(r):
    if r.status_code >= 400:
        try:
            err = r.json()
            errors = err.get("errors", [])
            if errors:
                for e in errors:
                    print(f"Error: {e.get('title', 'Unknown')} — {e.get('message', '')}")
            else:
                print(f"Error {r.status_code}: {r.text[:500]}")
        except Exception:
            print(f"Error {r.status_code}: {r.text[:500]}")
        sys.exit(1)
    return r.json()

def save_search(offers_data):
    """Save search results for index-based reference."""
    with open(LAST_SEARCH_FILE, "w") as f:
        json.dump(offers_data, f)

def load_offer(id_or_index):
    """Load an offer by ID or 1-based index from last search."""
    try:
        idx = int(id_or_index)
        with open(LAST_SEARCH_FILE) as f:
            data = json.load(f)
        offers = data if isinstance(data, list) else data.get("offers", [])
        if idx < 1 or idx > len(offers):
            print(f"Error: Index {idx} out of range (1-{len(offers)})")
            sys.exit(1)
        return offers[idx - 1]
    except (ValueError, FileNotFoundError):
        return {"id": id_or_index}

def fmt_duration(iso_dur):
    """Parse ISO 8601 duration like PT3H45M to 3h 45m."""
    if not iso_dur:
        return "?"
    d = iso_dur.replace("PT", "")
    hours = minutes = 0
    if "H" in d:
        hours, d = d.split("H")
        hours = int(hours)
    if "M" in d:
        minutes = int(d.replace("M", ""))
    return f"{hours}h {minutes:02d}m"

def fmt_time(iso_dt):
    """Format ISO datetime to HH:MM."""
    if not iso_dt:
        return "?"
    try:
        dt = datetime.fromisoformat(iso_dt.replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except Exception:
        return iso_dt[:16]

def fmt_date(iso_dt):
    """Format ISO datetime to Mon DD."""
    if not iso_dt:
        return "?"
    try:
        dt = datetime.fromisoformat(iso_dt.replace("Z", "+00:00"))
        return dt.strftime("%b %d")
    except Exception:
        return iso_dt[:10]

# ── Commands ─────────────────────────────────────────────────────────────

def cmd_search(args):
    """Search for flights."""
    slices = [{
        "origin": args.origin,
        "destination": args.destination,
        "departure_date": args.date,
    }]
    if args.return_date:
        slices.append({
            "origin": args.destination,
            "destination": args.origin,
            "departure_date": args.return_date,
        })

    passengers = []
    for _ in range(args.adults):
        passengers.append({"type": "adult"})
    for _ in range(args.children):
        passengers.append({"age": 10})
    for _ in range(args.infants):
        passengers.append({"type": "infant_without_seat"})

    payload = {
        "data": {
            "slices": slices,
            "passengers": passengers,
            "cabin_class": args.cabin,
        }
    }

    if args.max_connections is not None:
        payload["data"]["max_connections"] = args.max_connections

    data = api_post("/air/offer_requests", payload)
    offers = data.get("data", {}).get("offers", [])

    if not offers:
        print("No flights found.")
        return

    # Sort
    if args.sort == "price":
        offers.sort(key=lambda o: float(o.get("total_amount", "999999")))
    elif args.sort == "duration":
        offers.sort(key=lambda o: o.get("total_duration", "PT99H"))

    # Limit
    offers = offers[:args.max_results]

    if args.json:
        save_search(offers)
        print(json.dumps(offers, indent=2))
        return

    save_search(offers)

    route = f"{args.origin}→{args.destination}"
    if args.return_date:
        route += f" (round-trip, return {args.return_date})"
    print(f"\n✈️  {route} — {args.date} — {len(offers)} offers\n")

    for i, offer in enumerate(offers, 1):
        price = f"{offer.get('total_currency', '?')} {offer.get('total_amount', '?')}"
        owner = offer.get("owner", {}).get("name", "?")
        
        all_segments = []
        for sl in offer.get("slices", []):
            segments = sl.get("segments", [])
            all_segments.append(segments)

        # First slice summary
        first_slice = offer.get("slices", [{}])[0]
        seg_count = len(first_slice.get("segments", []))
        stops = seg_count - 1
        stops_str = "nonstop" if stops == 0 else f"{stops} stop{'s' if stops > 1 else ''}"
        duration = fmt_duration(first_slice.get("duration"))

        first_seg = first_slice.get("segments", [{}])[0]
        last_seg = first_slice.get("segments", [{}])[-1]
        dep_time = fmt_time(first_seg.get("departing_at"))
        arr_time = fmt_time(last_seg.get("arriving_at"))
        
        carrier = first_seg.get("marketing_carrier", {}).get("iata_code", "?")
        flight_no = f"{carrier}{first_seg.get('marketing_carrier_flight_number', '?')}"
        
        # Additional flights for connections
        if seg_count > 1:
            via = []
            for seg in first_slice.get("segments", [])[:-1]:
                via.append(seg.get("destination", {}).get("iata_code", "?"))
            flight_no += f" via {','.join(via)}"

        cabin = first_seg.get("passengers", [{}])[0].get("cabin_class_marketing_name", "")
        if not cabin:
            cabin = first_seg.get("passengers", [{}])[0].get("cabin_class", "")

        line = f"  {i:>2}. {dep_time}–{arr_time}  {duration:>8}  {stops_str:<10}  {flight_no:<20}  {cabin:<15}  {price}"
        print(line)

        # Show return slice if round-trip
        if len(offer.get("slices", [])) > 1:
            ret_slice = offer["slices"][1]
            ret_first = ret_slice.get("segments", [{}])[0]
            ret_last = ret_slice.get("segments", [{}])[-1]
            ret_stops = len(ret_slice.get("segments", [])) - 1
            ret_stops_str = "nonstop" if ret_stops == 0 else f"{ret_stops} stop{'s' if ret_stops > 1 else ''}"
            ret_carrier = ret_first.get("marketing_carrier", {}).get("iata_code", "?")
            ret_fno = f"{ret_carrier}{ret_first.get('marketing_carrier_flight_number', '?')}"
            print(f"      ↩ {fmt_time(ret_first.get('departing_at'))}–{fmt_time(ret_last.get('arriving_at'))}  {fmt_duration(ret_slice.get('duration')):>8}  {ret_stops_str:<10}  {ret_fno}")

    print(f"\nUse 'duffel.py offer <number>' for details on a specific flight.")


def cmd_offer(args):
    """Show details for a specific offer."""
    offer_data = load_offer(args.id)
    offer_id = offer_data.get("id", args.id)

    data = api_get(f"/air/offers/{offer_id}", {"return_available_services": "true"})
    offer = data.get("data", {})

    if args.json:
        print(json.dumps(offer, indent=2))
        return

    price = f"{offer.get('total_currency', '?')} {offer.get('total_amount', '?')}"
    owner = offer.get("owner", {}).get("name", "?")
    print(f"\n✈️  Offer from {owner} — {price}")
    print(f"   Expires: {offer.get('expires_at', '?')}")
    print(f"   Offer ID: {offer.get('id', '?')}")

    for si, sl in enumerate(offer.get("slices", []), 1):
        direction = "Outbound" if si == 1 else "Return"
        print(f"\n   {direction} — {fmt_duration(sl.get('duration'))}")
        for seg in sl.get("segments", []):
            carrier = seg.get("marketing_carrier", {}).get("iata_code", "")
            fnum = seg.get("marketing_carrier_flight_number", "")
            orig = seg.get("origin", {}).get("iata_code", "?")
            dest = seg.get("destination", {}).get("iata_code", "?")
            dep = seg.get("departing_at", "?")
            arr = seg.get("arriving_at", "?")
            aircraft = (seg.get("aircraft") or {}).get("name", "?")
            cabin = seg.get("passengers", [{}])[0].get("cabin_class_marketing_name", "")
            
            print(f"   {carrier}{fnum}: {orig} {fmt_time(dep)} → {dest} {fmt_time(arr)} ({aircraft}) {cabin}")

            # Baggage
            for pax in seg.get("passengers", []):
                bags = pax.get("baggages", [])
                for bag in bags:
                    print(f"     🧳 {bag.get('type', '?')}: {bag.get('quantity', '?')}x")

    # Available services (extra bags, seats, etc.)
    services = offer.get("available_services", [])
    if services:
        print(f"\n   Available extras:")
        for svc in services[:10]:
            stype = svc.get("type", "?")
            amt = svc.get("total_amount", "?")
            cur = svc.get("total_currency", "?")
            print(f"   + {stype}: {cur} {amt}")

    # Conditions
    conditions = offer.get("conditions", {})
    if conditions:
        refund = conditions.get("refund_before_departure")
        change = conditions.get("change_before_departure")
        if refund:
            print(f"\n   Refund: {'Allowed' if refund.get('allowed') else 'Not allowed'}" +
                  (f" (penalty {refund.get('penalty_currency', '')} {refund.get('penalty_amount', '')})" if refund.get('penalty_amount') else ""))
        if change:
            print(f"   Change: {'Allowed' if change.get('allowed') else 'Not allowed'}" +
                  (f" (penalty {change.get('penalty_currency', '')} {change.get('penalty_amount', '')})" if change.get('penalty_amount') else ""))

    print(f"\nTo book: duffel.py book {args.id} --pax \"LAST/FIRST TITLE DOB EMAIL PHONE NATIONALITY GENDER\"")


def parse_pax(pax_str):
    """Parse passenger string: LAST/FIRST TITLE DOB EMAIL PHONE NATIONALITY GENDER"""
    parts = pax_str.strip().split()
    if len(parts) < 7:
        print(f"Error: Passenger format is LAST/FIRST TITLE DOB EMAIL PHONE NATIONALITY GENDER")
        print(f"  Example: RIBEIRO/FABIO MR 1977-01-31 fabio@ribei.ro +13059159687 BR m")
        sys.exit(1)

    names = parts[0].split("/")
    family_name = names[0]
    given_name = names[1] if len(names) > 1 else ""

    title_map = {"MR": "mr", "MRS": "mrs", "MS": "ms", "MISS": "miss", "DR": "dr"}
    title = title_map.get(parts[1].upper(), parts[1].lower())

    return {
        "family_name": family_name,
        "given_name": given_name,
        "title": title,
        "born_on": parts[2],
        "email": parts[3],
        "phone_number": parts[4],
        "nationality": parts[5].upper() if len(parts) > 5 else None,
        "gender": parts[6].lower() if len(parts) > 6 else "m",
        "type": "adult",
    }


def cmd_book(args):
    """Book a flight."""
    offer_data = load_offer(args.id)
    offer_id = offer_data.get("id", args.id)

    passengers = []
    # Get passenger IDs from the offer request
    offer_passengers = offer_data.get("passengers", [])

    for i, pax_str in enumerate(args.pax):
        pax = parse_pax(pax_str)
        if i < len(offer_passengers):
            pax["id"] = offer_passengers[i].get("id")
        passengers.append(pax)

    payload = {
        "data": {
            "selected_offers": [offer_id],
            "passengers": passengers,
            "type": "instant",
            "payments": [{
                "type": "balance",
                "amount": offer_data.get("total_amount", "0"),
                "currency": offer_data.get("total_currency", "USD"),
            }],
        }
    }

    data = api_post("/air/orders", payload)
    order = data.get("data", {})

    if args.json:
        print(json.dumps(order, indent=2))
        return

    print(f"\n✅ Booking confirmed!")
    print(f"   Order ID: {order.get('id', '?')}")
    print(f"   PNR: {order.get('booking_reference', '?')}")
    print(f"   Total: {order.get('total_currency', '?')} {order.get('total_amount', '?')}")

    for sl in order.get("slices", []):
        for seg in sl.get("segments", []):
            carrier = seg.get("marketing_carrier", {}).get("iata_code", "")
            fnum = seg.get("marketing_carrier_flight_number", "")
            orig = seg.get("origin", {}).get("iata_code", "?")
            dest = seg.get("destination", {}).get("iata_code", "?")
            dep = seg.get("departing_at", "?")
            print(f"   {carrier}{fnum}: {orig} → {dest} on {fmt_date(dep)} at {fmt_time(dep)}")

    for pax in order.get("passengers", []):
        print(f"   Passenger: {pax.get('given_name', '')} {pax.get('family_name', '')}")

    print(f"\nManage: duffel.py order {order.get('id', '')}")


def cmd_order(args):
    """Get order details."""
    data = api_get(f"/air/orders/{args.order_id}")
    order = data.get("data", {})

    if args.json:
        print(json.dumps(order, indent=2))
        return

    status = "Cancelled" if order.get("cancelled_at") else "Confirmed"
    print(f"\n📋 Order {order.get('id', '?')} — {status}")
    print(f"   PNR: {order.get('booking_reference', '?')}")
    print(f"   Total: {order.get('total_currency', '?')} {order.get('total_amount', '?')}")
    print(f"   Created: {order.get('created_at', '?')}")

    for sl in order.get("slices", []):
        for seg in sl.get("segments", []):
            carrier = seg.get("marketing_carrier", {}).get("iata_code", "")
            fnum = seg.get("marketing_carrier_flight_number", "")
            orig = seg.get("origin", {}).get("iata_code", "?")
            dest = seg.get("destination", {}).get("iata_code", "?")
            dep = seg.get("departing_at", "?")
            arr = seg.get("arriving_at", "?")
            print(f"   {carrier}{fnum}: {orig} {fmt_time(dep)} → {dest} {fmt_time(arr)} on {fmt_date(dep)}")

    for pax in order.get("passengers", []):
        print(f"   Passenger: {pax.get('given_name', '')} {pax.get('family_name', '')}")

    actions = order.get("available_actions", [])
    if actions:
        print(f"   Available actions: {', '.join(actions)}")


def cmd_cancel(args):
    """Cancel an order."""
    if not args.confirm:
        # Get cancellation quote
        payload = {"data": {"order_id": args.order_id}}
        data = api_post("/air/order_cancellations", payload)
        cancel = data.get("data", {})

        if args.json:
            print(json.dumps(cancel, indent=2))
            return

        refund = cancel.get("refund_amount", "0")
        currency = cancel.get("refund_currency", "?")
        print(f"\n⚠️  Cancellation quote for order {args.order_id}")
        print(f"   Refund: {currency} {refund}")
        print(f"   Cancellation ID: {cancel.get('id', '?')}")
        print(f"\nTo confirm: duffel.py cancel {args.order_id} --confirm")
        # Save cancel ID for confirm step
        with open("/tmp/duffel-last-cancel.json", "w") as f:
            json.dump(cancel, f)
    else:
        # Load cancel ID and confirm
        try:
            with open("/tmp/duffel-last-cancel.json") as f:
                cancel = json.load(f)
            cancel_id = cancel.get("id")
        except FileNotFoundError:
            # Create and confirm in one go
            payload = {"data": {"order_id": args.order_id}}
            data = api_post("/air/order_cancellations", payload)
            cancel_id = data.get("data", {}).get("id")

        data = api_post(f"/air/order_cancellations/{cancel_id}/actions/confirm", {})
        result = data.get("data", {})

        if args.json:
            print(json.dumps(result, indent=2))
            return

        print(f"\n✅ Order {args.order_id} cancelled.")
        print(f"   Refund: {result.get('refund_currency', '?')} {result.get('refund_amount', '0')}")


def cmd_seatmap(args):
    """Show seat map for an offer."""
    offer_data = load_offer(args.id)
    offer_id = offer_data.get("id", args.id)

    data = api_get("/air/seat_maps", {"offer_id": offer_id})
    seatmaps = data.get("data", [])

    if args.json:
        print(json.dumps(seatmaps, indent=2))
        return

    if not seatmaps:
        print("No seat maps available for this offer.")
        return

    for sm in seatmaps:
        seg_id = sm.get("segment_id", "?")
        cabins = sm.get("cabins", [])
        print(f"\n🪑 Seat map (segment {seg_id})")
        for cabin in cabins:
            cabin_class = cabin.get("cabin_class", "?")
            print(f"\n   Cabin: {cabin_class}")
            rows = cabin.get("rows", [])
            for row in rows:
                sections = row.get("sections", [])
                row_seats = []
                for section in sections:
                    for seat in section.get("elements", []):
                        if seat.get("type") == "seat":
                            designator = seat.get("designator", "?")
                            available = "✅" if seat.get("available_services") else "❌"
                            price = ""
                            services = seat.get("available_services", [])
                            if services:
                                price = f" ({services[0].get('total_currency', '')} {services[0].get('total_amount', '')})"
                            row_seats.append(f"{designator}{available}{price}")
                if row_seats:
                    print(f"   {' '.join(row_seats)}")


def cmd_places(args):
    """Search airports and cities."""
    data = api_get("/places/suggestions", {"query": args.query})
    places = data.get("data", [])

    if args.json:
        print(json.dumps(places, indent=2))
        return

    if not places:
        print(f"No results for '{args.query}'")
        return

    print(f"\n🌍 Places matching '{args.query}':\n")
    for p in places[:15]:
        ptype = p.get("type", "?")
        iata = p.get("iata_code", "?")
        name = p.get("name", "?")
        city = p.get("city_name", "")
        country = p.get("city", {}).get("country", {}).get("name", "") if p.get("city") else ""
        icon = "✈️" if ptype == "airport" else "🏙️"
        loc = f"{city}, {country}" if city and country else city or country
        print(f"  {icon} {iata:>5}  {name}" + (f" — {loc}" if loc else ""))


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Duffel Flights API CLI — search, book, and manage flights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              %(prog)s search --from MIA --to LHR --date 2026-04-15
              %(prog)s search --from MIA --to CDG --date 2026-03-15 --return-date 2026-03-22 --cabin business
              %(prog)s offer 3
              %(prog)s book 3 --pax "RIBEIRO/FABIO MR 1977-01-31 fabio@ribei.ro +13059159687 BR m"
              %(prog)s order ord_00009hthhsUZ8W4LxQgkjo
              %(prog)s cancel ord_00009hthhsUZ8W4LxQgkjo
              %(prog)s seatmap 3
              %(prog)s places "new york"
        """))

    sub = parser.add_subparsers(dest="command")

    # search
    p_search = sub.add_parser("search", help="Search for flights")
    p_search.add_argument("--from", dest="origin", required=True, help="Origin IATA code")
    p_search.add_argument("--to", dest="destination", required=True, help="Destination IATA code")
    p_search.add_argument("--date", required=True, help="Departure date (YYYY-MM-DD)")
    p_search.add_argument("--return-date", help="Return date for round-trip")
    p_search.add_argument("--adults", type=int, default=1, help="Number of adults (default: 1)")
    p_search.add_argument("--children", type=int, default=0, help="Number of children")
    p_search.add_argument("--infants", type=int, default=0, help="Number of infants")
    p_search.add_argument("--cabin", default="economy",
                          choices=["economy", "premium_economy", "business", "first"],
                          help="Cabin class (default: economy)")
    p_search.add_argument("--nonstop", action="store_const", const=0, dest="max_connections",
                          help="Non-stop flights only")
    p_search.add_argument("--max-results", type=int, default=10, help="Max results (default: 10)")
    p_search.add_argument("--sort", default="price", choices=["price", "duration"])
    p_search.add_argument("--json", action="store_true", help="Output raw JSON")

    # offer
    p_offer = sub.add_parser("offer", help="Show offer details")
    p_offer.add_argument("id", help="Offer ID or search result index")
    p_offer.add_argument("--json", action="store_true")

    # book
    p_book = sub.add_parser("book", help="Book a flight")
    p_book.add_argument("id", help="Offer ID or search result index")
    p_book.add_argument("--pax", action="append", required=True,
                        help="Passenger: LAST/FIRST TITLE DOB EMAIL PHONE NATIONALITY GENDER")
    p_book.add_argument("--json", action="store_true")

    # order
    p_order = sub.add_parser("order", help="Get order details")
    p_order.add_argument("order_id", help="Order ID")
    p_order.add_argument("--json", action="store_true")

    # cancel
    p_cancel = sub.add_parser("cancel", help="Cancel an order")
    p_cancel.add_argument("order_id", help="Order ID")
    p_cancel.add_argument("--confirm", action="store_true", help="Confirm cancellation")
    p_cancel.add_argument("--json", action="store_true")

    # seatmap
    p_seat = sub.add_parser("seatmap", help="Show seat map")
    p_seat.add_argument("id", help="Offer ID or search result index")
    p_seat.add_argument("--json", action="store_true")

    # places
    p_places = sub.add_parser("places", help="Search airports and cities")
    p_places.add_argument("query", help="Search query")
    p_places.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "search": cmd_search,
        "offer": cmd_offer,
        "book": cmd_book,
        "order": cmd_order,
        "cancel": cmd_cancel,
        "seatmap": cmd_seatmap,
        "places": cmd_places,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
