#!/usr/bin/env python3
"""Scan local network for Tuya devices."""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description='Scan for Tuya devices on local network')
    parser.add_argument('--timeout', type=int, default=18, help='Scan timeout in seconds (default: 18)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    try:
        import tinytuya
    except ImportError:
        print("❌ tinytuya not installed. Run: pip3 install tinytuya", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 Scanning for Tuya devices ({args.timeout}s)...")
    devices = tinytuya.deviceScan(verbose=False, maxretry=3)

    if not devices:
        print("No devices found. Ensure devices are on the same network.")
        return

    if args.json:
        print(json.dumps(devices, indent=2, ensure_ascii=False))
    else:
        print(f"\n✅ Found {len(devices)} device(s):\n")
        for ip, info in devices.items():
            print(f"  📍 {ip}")
            print(f"     Device ID: {info.get('gwId', 'unknown')}")
            print(f"     Product ID: {info.get('productKey', 'unknown')}")
            print(f"     Version: {info.get('version', 'unknown')}")
            print()


if __name__ == '__main__':
    main()
