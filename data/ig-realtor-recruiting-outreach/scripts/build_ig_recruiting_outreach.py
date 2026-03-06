#!/usr/bin/env python3
"""Build personalized IG realtor recruiting outreach from a lead CSV."""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


STAGE_ORDER = ["d1_opener", "f1_value", "f2_story", "breakup"]


def norm_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def clean_handle(handle: str) -> str:
    handle = (handle or "").strip()
    if not handle:
        return ""
    return handle if handle.startswith("@") else f"@{handle}"


def choose(row: Dict[str, str], *keys: str, default: str = "") -> str:
    for key in keys:
        value = row.get(key, "").strip()
        if value:
            return value
    return default


def brokerage_angle(target_brokerage: str) -> str:
    text = target_brokerage.lower()
    if "exp" in text:
        return "scaling through a cloud model + rev share without adding office overhead"
    if "real" in text:
        return "using a modern brokerage stack with attraction economics built for agent teams"
    return "building production with stronger systems, support, and long-term attraction upside"


def profile_hook(row: Dict[str, str]) -> str:
    theme = row.get("last_post_theme", "").strip()
    pain_point = row.get("pain_point", "").strip()
    city = row.get("city", "").strip()
    if theme:
        return f"your recent content on {theme}"
    if pain_point:
        return f"how you're navigating {pain_point}"
    if city:
        return f"how you're growing in {city}"
    return "how you're building your business"


def stage_message(stage: str, lead: Dict[str, str]) -> str:
    first = lead["first_name"] or "there"
    angle = lead["angle"]
    hook = lead["hook"]
    brokerage = lead["target_brokerage"]
    brokerage_now = lead["brokerage"] or "your current brokerage"
    production_tier = lead["production_tier"].lower()

    if stage == "d1_opener":
        return (
            f"Hey {first}, I came across {hook} and liked your approach. "
            f"I'm recruiting a few growth-minded agents into {brokerage} focused on {angle}. "
            "Open to a quick DM chat to compare models?"
        )
    if stage == "f1_value":
        tier_line = ""
        if production_tier in {"team_lead", "top_producer"}:
            tier_line = "Especially for producers already running volume, the economics are worth looking at. "
        return (
            f"Quick follow-up, {first}: one reason agents move from {brokerage_now} is more control over scaling. "
            f"{tier_line}"
            f"If helpful, I can send a 3-point breakdown of how we structure recruiting and support inside {brokerage}."
        )
    if stage == "f2_story":
        return (
            f"{first}, short context: most agents I talk with are not looking for hype, just cleaner systems and a better path to build. "
            f"That's the conversation we have around {brokerage}. "
            "Want me to send the exact framework we use?"
        )
    return (
        f"No pressure either way, {first}. If timing changes and you'd like to see how {brokerage} compares to "
        f"{brokerage_now} for growth + attraction, I can send details here."
    )


def load_leads(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Input CSV has no header row.")
        headers = [norm_key(h) for h in reader.fieldnames]
        rows: List[Dict[str, str]] = []
        for raw in reader:
            row: Dict[str, str] = {}
            for original, key in zip(reader.fieldnames, headers):
                row[key] = (raw.get(original) or "").strip()
            rows.append(row)
        return rows


def build_sequence(
    row: Dict[str, str], default_target_brokerage: str
) -> Dict[str, object]:
    handle = clean_handle(row.get("instagram_handle", ""))
    if not handle:
        raise ValueError("Missing instagram_handle")
    first_name = choose(row, "first_name")
    if not first_name:
        first_name = choose(row, "name").split(" ")[0].strip()

    target_brokerage = choose(row, "target_brokerage", default=default_target_brokerage)
    if not target_brokerage:
        target_brokerage = "eXp Realty"

    lead = {
        "handle": handle,
        "first_name": first_name,
        "brokerage": choose(row, "brokerage"),
        "target_brokerage": target_brokerage,
        "production_tier": choose(row, "production_tier"),
        "hook": profile_hook(row),
        "angle": brokerage_angle(target_brokerage),
        "notes": choose(row, "notes"),
    }

    messages = [{"stage": stage, "message": stage_message(stage, lead)} for stage in STAGE_ORDER]

    return {
        "lead": lead,
        "messages": messages,
    }


def write_messages_csv(path: Path, campaign: str, sequences: List[Dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "campaign",
                "instagram_handle",
                "target_brokerage",
                "stage",
                "message",
            ],
        )
        writer.writeheader()
        for seq in sequences:
            lead = seq["lead"]  # type: ignore[index]
            for item in seq["messages"]:  # type: ignore[index]
                writer.writerow(
                    {
                        "campaign": campaign,
                        "instagram_handle": lead["handle"],
                        "target_brokerage": lead["target_brokerage"],
                        "stage": item["stage"],
                        "message": item["message"],
                    }
                )


def write_playbook(path: Path, campaign: str, sequences: List[Dict[str, object]]) -> None:
    total = len(sequences)
    with path.open("w", encoding="utf-8") as f:
        f.write(f"# IG Recruiting Playbook: {campaign}\n\n")
        f.write(f"- Generated at: {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"- Leads: {total}\n")
        f.write("- Stages: d1_opener, f1_value (+2 days), f2_story (+5 days), breakup (+10 days)\n\n")
        f.write("## Send Rules\n\n")
        f.write("- Personalize before sending each message.\n")
        f.write("- Keep one CTA per DM.\n")
        f.write("- Do not send automated bulk spam.\n")
        f.write("- Track stage tags in CRM after each touch.\n")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate IG realtor recruiting DM sequences.")
    p.add_argument("--input", required=True, help="Lead CSV path")
    p.add_argument("--campaign-name", required=True, help="Campaign identifier")
    p.add_argument(
        "--default-target-brokerage",
        default="eXp Realty",
        help="Used when target_brokerage is missing in CSV",
    )
    p.add_argument(
        "--output-dir",
        default="output/ig-recruiting",
        help="Directory for generated outputs",
    )
    p.add_argument("--max-leads", type=int, default=0, help="Optional processing limit")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    in_path = Path(args.input)
    if not in_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {in_path}")

    rows = load_leads(in_path)
    if args.max_leads > 0:
        rows = rows[: args.max_leads]

    sequences: List[Dict[str, object]] = []
    skipped: List[Dict[str, str]] = []

    for row in rows:
        try:
            sequences.append(build_sequence(row, args.default_target_brokerage))
        except ValueError as exc:
            skipped.append(
                {
                    "reason": str(exc),
                    "row": row,
                }
            )

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    slug = re.sub(r"[^a-z0-9]+", "-", args.campaign_name.lower()).strip("-") or "campaign"
    messages_csv = out_dir / f"messages_{slug}.csv"
    audit_json = out_dir / f"audit_{slug}.json"
    playbook_md = out_dir / f"playbook_{slug}.md"

    write_messages_csv(messages_csv, args.campaign_name, sequences)
    write_playbook(playbook_md, args.campaign_name, sequences)

    audit = {
        "campaign": args.campaign_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_rows": len(rows),
        "sequences_generated": len(sequences),
        "skipped_rows": len(skipped),
        "skipped": skipped,
        "sequences": sequences,
    }
    with audit_json.open("w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2)

    print(f"Generated {len(sequences)} lead sequences.")
    print(f"Messages CSV: {messages_csv}")
    print(f"Audit JSON:   {audit_json}")
    print(f"Playbook MD:  {playbook_md}")
    if skipped:
        print(f"Skipped rows: {len(skipped)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
