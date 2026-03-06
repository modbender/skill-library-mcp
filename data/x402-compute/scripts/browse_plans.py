#!/usr/bin/env python3
"""
x402Compute — Browse available compute plans.

Lists GPU, VPS, and dedicated plans with pricing.
Usage:
  python browse_plans.py                  # all plans
  python browse_plans.py --type vcg       # GPU plans only
  python browse_plans.py --type vps       # VPS plans only
"""

import argparse
import json
import sys

import requests

BASE_URL = "https://compute.x402layer.cc"


def browse_plans(plan_type: str = None) -> dict:
    """Fetch available compute plans."""
    url = f"{BASE_URL}/compute/plans"
    params = {}
    if plan_type:
        params["type"] = plan_type

    response = requests.get(url, params=params, timeout=30)

    if response.status_code != 200:
        return {"error": f"HTTP {response.status_code}", "response": response.text[:500]}

    data = response.json()
    plans = data.get("plans", [])

    print(f"Found {len(plans)} plan(s)")
    for p in plans:
        monthly = p.get("our_monthly")
        if monthly is None:
            monthly = p.get("monthly_cost", p.get("vultr_monthly", 0))
        gpu_info = f" | GPU: {p.get('gpu_type', 'N/A')} {p.get('gpu_vram_gb', '')}GB" if p.get("gpu_vram_gb") else ""
        print(
            f"  {p['id']:30s}  ${float(monthly):>8.2f}/mo  "
            f"{p['vcpu_count']} vCPU  {p['ram'] // 1024}GB RAM  {p['disk']}GB disk"
            f"{gpu_info}"
        )

    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Browse x402Compute plans")
    parser.add_argument("--type", choices=["vps", "vhp", "vdc", "vcg"], help="Filter by plan type")
    args = parser.parse_args()

    result = browse_plans(plan_type=args.type)
    if "error" in result:
        print(json.dumps(result, indent=2))
        sys.exit(1)
