#!/usr/bin/env python3
"""
PackageTracker CLI — Manage shipment tracking from the terminal.
"""

import argparse
import sys

from tracker import (
    add_package,
    check_updates,
    get_api_quota,
    get_package_details,
    get_tracking_url,
    list_packages,
    remove_package,
    STATUS_EMOJI,
)


def cmd_add(args):
    print(f"📦 Adding package: {args.tracking_number}")
    result = add_package(
        tracking_number=args.tracking_number,
        description=args.description,
        carrier=args.carrier,
    )
    if result["ok"]:
        msg = result.get("message", "Package added successfully")
        carrier = result.get("carrier", "Unknown")
        print(f"✅ {msg}")
        print(f"   Carrier: {carrier}")
        if result.get("registered_17track"):
            print("   Registered with 17track ✓")
        else:
            print("   ⚠️  Not registered with 17track yet (add API key to .env)")
        if result.get("tracking_url"):
            print(f"   Track: {result['tracking_url']}")
    else:
        print(f"❌ {result['error']}")
        sys.exit(1)


def cmd_check(args):
    print("🔍 Checking for updates on all active packages...\n")
    updates = check_updates()
    if updates:
        print(f"\n📬 Found {len(updates)} update(s)")
    else:
        print("\n✅ All packages checked")


def cmd_list(args):
    show_all = getattr(args, "all", False)
    packages = list_packages(active_only=not show_all)

    if not packages:
        print("📭 No packages being tracked")
        if not show_all:
            print("   (use --all to include inactive packages)")
        return

    title = "All packages" if show_all else "Active packages"
    print(f"📦 {title} ({len(packages)}):\n")

    for pkg in packages:
        emoji = STATUS_EMOJI.get(pkg["status"], "📦")
        active_mark = "" if pkg["active"] else " [INACTIVE]"
        desc = f' — {pkg["description"]}' if pkg["description"] else ""
        carrier = f' ({pkg["carrier"]})' if pkg["carrier"] else ""
        url = get_tracking_url(pkg["tracking_number"], pkg.get("carrier"))

        print(f"  {emoji} {pkg['tracking_number']}{carrier}{desc}{active_mark}")
        print(f"     Status: {pkg['status']}")
        if pkg["last_event"]:
            print(f"     Latest: {pkg['last_event']}")
        if pkg["last_event_date"]:
            print(f"     Date:   {pkg['last_event_date']}")
        if pkg["last_checked"]:
            print(f"     Checked: {pkg['last_checked']}")
        print(f"     Track:  {url}")
        print()


def cmd_details(args):
    details = get_package_details(args.tracking_number)
    if not details:
        print(f"❌ Package {args.tracking_number} not found")
        sys.exit(1)

    pkg = details["package"]
    events = details["events"]

    emoji = STATUS_EMOJI.get(pkg["status"], "📦")
    active_str = "Active" if pkg["active"] else "Inactive"

    print(f"\n{emoji} Package Details\n{'─' * 50}")
    print(f"  Tracking:    {pkg['tracking_number']}")
    if pkg["description"]:
        print(f"  Description: {pkg['description']}")
    if pkg["carrier"]:
        print(f"  Carrier:     {pkg['carrier']}")
    print(f"  Status:      {pkg['status']} ({active_str})")
    print(f"  Added:       {pkg['created_at']}")
    if pkg["last_checked"]:
        print(f"  Last Check:  {pkg['last_checked']}")
    if pkg["delivered_date"]:
        print(f"  Delivered:   {pkg['delivered_date']}")
    if pkg.get("tracking_url"):
        print(f"  Track URL:   {pkg['tracking_url']}")

    if events:
        print(f"\n📋 Tracking History ({len(events)} events)\n{'─' * 50}")
        for ev in events:
            date = ev["event_date"] or "?"
            loc = f" — {ev['location']}" if ev["location"] else ""
            print(f"  📍 {date}{loc}")
            print(f"     {ev['description']}")
            print()
    else:
        print("\n📋 No tracking events yet")


def cmd_remove(args):
    result = remove_package(args.tracking_number)
    if result["ok"]:
        print(f"✅ {result['message']}")
    else:
        print(f"❌ {result['error']}")
        sys.exit(1)


def cmd_quota(args):
    print("📊 API Quota Information\n")
    info = get_api_quota()

    local = info.get("local_usage")
    if local:
        used = local["registrations_used"]
        remaining = local["registrations_remaining"]
        bar_len = 20
        filled = int(bar_len * used / 100) if used <= 100 else bar_len
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"  Month: {local['month']}")
        print(f"  Registrations: {used}/100 [{bar}]")
        print(f"  Remaining:     {remaining}")
        if used >= 90:
            print("  ⚠️  Running low on registrations!")

    if info.get("api_quota"):
        print("\n  17track API response:")
        api_data = info["api_quota"].get("data", info["api_quota"])
        if isinstance(api_data, dict):
            for k, v in api_data.items():
                print(f"    {k}: {v}")
        else:
            print(f"    {api_data}")

    if info.get("api_error"):
        print(f"\n  ⚠️  {info['api_error']}")


def main():
    parser = argparse.ArgumentParser(
        prog="packagetracker",
        description="📦 PackageTracker — Track shipments via 17track API",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # add
    p_add = subparsers.add_parser("add", help="Add a package to track")
    p_add.add_argument("tracking_number", help="Tracking number")
    p_add.add_argument("-d", "--description", help="Description (e.g., 'USB-C cables from Amazon')")
    p_add.add_argument("-c", "--carrier", help="Carrier name override")
    p_add.set_defaults(func=cmd_add)

    # check
    p_check = subparsers.add_parser("check", help="Check all active packages for updates")
    p_check.set_defaults(func=cmd_check)

    # list
    p_list = subparsers.add_parser("list", help="List tracked packages")
    p_list.add_argument("-a", "--all", action="store_true", help="Include inactive packages")
    p_list.set_defaults(func=cmd_list)

    # details
    p_details = subparsers.add_parser("details", help="Show full tracking history")
    p_details.add_argument("tracking_number", help="Tracking number")
    p_details.set_defaults(func=cmd_details)

    # remove
    p_remove = subparsers.add_parser("remove", help="Stop tracking a package")
    p_remove.add_argument("tracking_number", help="Tracking number")
    p_remove.set_defaults(func=cmd_remove)

    # quota
    p_quota = subparsers.add_parser("quota", help="Show 17track API quota")
    p_quota.set_defaults(func=cmd_quota)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
