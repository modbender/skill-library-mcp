#!/usr/bin/env python3
"""
generate_checklist_card.py — Generate a visual HTML checklist progress card.

Usage:
  python generate_checklist_card.py --region "Northern California" [--workspace ./birdfolio]

Output (JSON to stdout):
  {"status": "ok", "cardPath": "..."}
"""
import argparse, json, os, sys
from datetime import datetime, timezone

COMMON_COLOR   = "#16a34a"
RARE_COLOR     = "#b45309"
SUPER_RARE_COLOR = "#dc2626"

def pct(found, total):
    return int((found / total) * 100) if total else 0

def species_rows(species_list, color):
    rows = ""
    for s in species_list:
        check = "✅" if s["found"] else "⬜"
        date  = f'<span class="date">{s["dateFound"]}</span>' if s["found"] else ""
        rows += f'<div class="species-row {"found" if s["found"] else ""}">{check} {s["species"]}{date}</div>\n'
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", required=True)
    parser.add_argument("--workspace", default="./birdfolio")
    args = parser.parse_args()

    workspace  = os.path.abspath(args.workspace)
    checklist_path = os.path.join(workspace, "checklist.json")
    config_path    = os.path.join(workspace, "config.json")
    cards_dir      = os.path.join(workspace, "cards")
    os.makedirs(cards_dir, exist_ok=True)

    with open(checklist_path) as f:
        checklist = json.load(f)
    with open(config_path) as f:
        config = json.load(f)

    region = args.region
    data   = checklist.get(region, {})
    common     = data.get("common", [])
    rare       = data.get("rare", [])
    super_rare = data.get("superRare", [])

    cf, ct = sum(1 for s in common if s["found"]), len(common)
    rf, rt = sum(1 for s in rare if s["found"]), len(rare)
    sf, st = sum(1 for s in super_rare if s["found"]), len(super_rare)
    total_found = cf + rf + sf
    total       = ct + rt + st

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      width: 600px;
      background: #0a0f1e;
      font-family: 'Segoe UI', system-ui, sans-serif;
      padding: 28px;
      color: #f1f5f9;
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 20px;
    }}
    .title {{ font-size: 22px; font-weight: 900; letter-spacing: -0.5px; }}
    .subtitle {{ font-size: 12px; color: #475569; margin-top: 3px; }}
    .logo {{ font-size: 11px; font-weight: 800; color: #334155; letter-spacing: 1.5px; text-transform: uppercase; }}

    .total-bar-wrap {{ margin-bottom: 24px; }}
    .total-label {{ font-size: 11px; color: #475569; margin-bottom: 6px; }}
    .total-count {{ font-size: 28px; font-weight: 900; color: #f1f5f9; }}
    .total-count span {{ font-size: 16px; color: #475569; font-weight: 400; }}
    .bar-track {{ background: #1e293b; border-radius: 4px; height: 6px; margin-top: 8px; }}
    .bar-fill {{ height: 6px; border-radius: 4px; transition: width 0.3s; }}

    .tier {{ margin-bottom: 20px; }}
    .tier-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }}
    .tier-badge {{
      display: inline-flex; align-items: center; gap: 5px;
      font-size: 10px; font-weight: 800; letter-spacing: 2px;
      text-transform: uppercase; padding: 3px 8px;
      border-radius: 3px; color: #fff;
    }}
    .tier-progress {{ font-size: 12px; color: #475569; }}
    .species-row {{
      font-size: 12px; color: #475569;
      padding: 5px 0;
      border-bottom: 1px solid rgba(255,255,255,0.04);
      display: flex; align-items: center; gap: 6px;
    }}
    .species-row.found {{ color: #94a3b8; }}
    .date {{ font-size: 10px; color: #334155; margin-left: auto; }}

    .divider {{ border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 20px 0; }}
    .footer {{ font-size: 10px; color: #1e293b; text-align: right; margin-top: 16px; }}
  </style>
</head>
<body>
  <div class="header">
    <div>
      <div class="title">🦅 {region}</div>
      <div class="subtitle">Birdfolio Checklist · {datetime.now().strftime("%b %d, %Y")}</div>
    </div>
    <div class="logo">🦅 Birdfolio</div>
  </div>

  <div class="total-bar-wrap">
    <div class="total-label">TOTAL PROGRESS</div>
    <div class="total-count">{total_found} <span>/ {total} species</span></div>
    <div class="bar-track">
      <div class="bar-fill" style="width:{pct(total_found,total)}%; background: linear-gradient(to right, {COMMON_COLOR}, {RARE_COLOR});"></div>
    </div>
  </div>

  <hr class="divider">

  <div class="tier">
    <div class="tier-header">
      <span class="tier-badge" style="background:{COMMON_COLOR}">🟢 Common</span>
      <span class="tier-progress">{cf} / {ct}</span>
    </div>
    <div class="bar-track" style="margin-bottom:10px">
      <div class="bar-fill" style="width:{pct(cf,ct)}%; background:{COMMON_COLOR};"></div>
    </div>
    {species_rows(common, COMMON_COLOR)}
  </div>

  <div class="tier">
    <div class="tier-header">
      <span class="tier-badge" style="background:{RARE_COLOR}">🟡 Rare</span>
      <span class="tier-progress">{rf} / {rt}</span>
    </div>
    <div class="bar-track" style="margin-bottom:10px">
      <div class="bar-fill" style="width:{pct(rf,rt)}%; background:{RARE_COLOR};"></div>
    </div>
    {species_rows(rare, RARE_COLOR)}
  </div>

  <div class="tier">
    <div class="tier-header">
      <span class="tier-badge" style="background:{SUPER_RARE_COLOR}">🔴 Super Rare</span>
      <span class="tier-progress">{sf} / {st}</span>
    </div>
    <div class="bar-track" style="margin-bottom:10px">
      <div class="bar-fill" style="width:{pct(sf,st)}%; background:{SUPER_RARE_COLOR};"></div>
    </div>
    {species_rows(super_rare, SUPER_RARE_COLOR)}
  </div>

  <div class="footer">Generated by Birdfolio · {config.get("totalSpecies", 0)} lifers total</div>
</body>
</html>"""

    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    out_path = os.path.join(cards_dir, f"checklist-{ts}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(json.dumps({"status": "ok", "cardPath": out_path}))

if __name__ == "__main__":
    main()
