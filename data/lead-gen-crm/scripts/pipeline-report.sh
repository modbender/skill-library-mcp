#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="${LEAD_GEN_DIR:-$HOME/.openclaw/workspace/lead-gen}"
ACTION="${1:---summary}"

export LEAD_BASE_DIR="$BASE_DIR"
export REPORT_ACTION="$ACTION"

python3 << 'PYEOF'
import json, os, glob

base_dir = os.environ["LEAD_BASE_DIR"]
action = os.environ["REPORT_ACTION"]

stages = ["raw", "enriched", "qualified", "archived"]
counts = {}
for stage in stages:
    d = os.path.join(base_dir, "leads", stage)
    counts[stage] = len(glob.glob(os.path.join(d, "*.json"))) if os.path.isdir(d) else 0

total = sum(counts.values())

print("📊 Lead Pipeline Report")
print("=" * 40)
print()
print("   Stage         Count")
print("   ─────────────────────")
for stage in stages:
    bar = "█" * counts[stage] + "░" * max(0, 10 - counts[stage])
    print(f"   {stage:12s}  {bar} {counts[stage]}")
print(f"   {'TOTAL':12s}            {total}")

# Campaign stats
campaigns_dir = os.path.join(base_dir, "campaigns")
if os.path.isdir(campaigns_dir):
    campaign_files = glob.glob(os.path.join(campaigns_dir, "*.json"))
    if campaign_files:
        print()
        print("   Campaigns")
        print("   ─────────────────────")
        for cf in campaign_files:
            with open(cf) as f:
                c = json.load(f)
            name = c.get("name", "unknown")
            status = c.get("status", "draft")
            sent = c.get("sent", 0)
            total_r = c.get("total_recipients", 0)
            replied = c.get("replied", 0)
            print(f"   {name}: {status} — {sent}/{total_r} sent, {replied} replied")

print()
if counts["raw"] > 0:
    print(f"   💡 {counts['raw']} raw leads waiting to be enriched")
if counts["enriched"] > 0:
    print(f"   💡 {counts['enriched']} enriched leads waiting to be scored")
if counts["qualified"] > 0:
    print(f"   💡 {counts['qualified']} qualified leads ready for CRM/outreach")
PYEOF
