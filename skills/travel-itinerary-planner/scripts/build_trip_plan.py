#!/usr/bin/env python3
"""Generate an image-ready travel itinerary Markdown draft."""

from __future__ import annotations

import argparse
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus, urlparse


BUDGET_PROFILES = {
    "economy": {
        "lodging": 220,
        "food": 120,
        "local_transport": 70,
        "tickets": 100,
        "misc": 60,
    },
    "standard": {
        "lodging": 420,
        "food": 220,
        "local_transport": 110,
        "tickets": 180,
        "misc": 110,
    },
    "premium": {
        "lodging": 880,
        "food": 420,
        "local_transport": 220,
        "tickets": 320,
        "misc": 250,
    },
}

DEFAULT_THEMES = [
    "city landmarks",
    "culture and history",
    "nature and scenery",
    "food discovery",
    "free exploration",
]

PACE_ACTIVITY_COUNT = {
    "relaxed": 2,
    "balanced": 3,
    "intense": 4,
}


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def sanitize_text(raw: str, field_name: str, max_length: int = 120) -> str:
    cleaned = re.sub(r"[\x00-\x1f\x7f]", " ", raw or "")
    cleaned = " ".join(cleaned.split()).strip()
    if not cleaned:
        raise ValueError(f"--{field_name} cannot be empty.")
    if len(cleaned) > max_length:
        raise ValueError(f"--{field_name} is too long (max {max_length} chars).")
    return cleaned


def escape_markdown_text(raw: str) -> str:
    escaped = raw.replace("\\", "\\\\")
    for token in ("`", "*", "_", "[", "]", "(", ")", "#", "!", "|"):
        escaped = escaped.replace(token, f"\\{token}")
    return escaped


def validate_https_url(raw: str, field_name: str) -> str:
    value = (raw or "").strip()
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"--{field_name} only accepts valid HTTPS URLs.")
    if parsed.username or parsed.password:
        raise ValueError(f"--{field_name} cannot include URL credentials.")
    if "\n" in value or "\r" in value:
        raise ValueError(f"--{field_name} contains invalid newline characters.")
    return value


def parse_date(raw: str) -> date:
    return datetime.strptime(raw, "%Y-%m-%d").date()


def parse_focus(raw: str) -> list[str]:
    if not raw:
        return []
    values = []
    for item in raw.split(","):
        if not item.strip():
            continue
        values.append(sanitize_text(item, "focus item", max_length=40))
    return values[:10]


def slugify(text: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return normalized or "trip"


def iter_dates(start: date, end: date) -> list[date]:
    days = (end - start).days + 1
    return [start + timedelta(days=idx) for idx in range(days)]


def choose_theme(day_index: int, focus_items: list[str]) -> str:
    pool = focus_items if focus_items else DEFAULT_THEMES
    return pool[(day_index - 1) % len(pool)]


def format_currency(amount: int, currency: str) -> str:
    return f"{currency} {amount:,}"


def build_daily_block(day_index: int, current_date: date, theme: str, pace: str) -> str:
    safe_theme = escape_markdown_text(theme)
    activity_count = PACE_ACTIVITY_COUNT[pace]
    pace_hint = {
        "relaxed": "slow pace with longer breaks",
        "balanced": "moderate pace with buffer time",
        "intense": "dense pace with tight sequencing",
    }[pace]

    activity_lines = []
    labels = ["Morning", "Afternoon", "Evening", "Night"]
    for idx in range(activity_count):
        label = labels[idx]
        activity_lines.append(
            f"- {label}: [Plan specific {safe_theme} activity #{idx + 1}]"
        )

    return "\n".join(
        [
            f"### Day {day_index} | {current_date.isoformat()} | Theme: {safe_theme}",
            *activity_lines,
            "- Transit: [Estimate travel time between stops and mode]",
            "- Reservation flags: [List activities requiring advance booking]",
            "- Rain backup: [Indoor alternative for the main activity]",
            f"- Pace note: {pace_hint}",
            "",
        ]
    )


def build_budget_table(
    trip_days: int, travelers: int, budget_level: str, currency: str
) -> tuple[str, int]:
    profile = BUDGET_PROFILES[budget_level]
    rows = []
    total = 0

    labels = [
        ("Lodging", "lodging"),
        ("Food", "food"),
        ("Local transport", "local_transport"),
        ("Attractions and tickets", "tickets"),
        ("Misc", "misc"),
    ]
    for label, key in labels:
        per_person_day = profile[key]
        subtotal = per_person_day * trip_days * travelers
        total += subtotal
        rows.append(
            "| {label} | {ppd} | {subtotal} |".format(
                label=label,
                ppd=format_currency(per_person_day, currency),
                subtotal=format_currency(subtotal, currency),
            )
        )

    header = "\n".join(
        [
            "| Category | Per person / day | Whole trip estimate |",
            "| --- | ---: | ---: |",
        ]
    )
    return "\n".join([header, *rows]), total


def build_gallery(destination: str, image_urls: list[str]) -> str:
    if not image_urls:
        return "\n".join(
            [
                "- Add at least 3 trusted HTTPS image URLs for this destination.",
                "- Prefer official tourism boards, museums, or your own photos.",
            ]
        )
    lines = []
    for idx, url in enumerate(image_urls, start=1):
        lines.append(f"![{destination} photo {idx}]({url})")
    return "\n".join(lines)


def render_markdown(args: argparse.Namespace) -> str:
    destination = escape_markdown_text(args.destination)
    origin = escape_markdown_text(args.origin) if args.origin else "[Fill origin city]"
    title = (
        escape_markdown_text(args.title)
        if args.title
        else f"{destination} Trip Plan ({args.start_date.isoformat()} to {args.end_date.isoformat()})"
    )

    dates = iter_dates(args.start_date, args.end_date)
    trip_days = len(dates)
    focus_items = parse_focus(args.focus)
    budget_table, budget_total = build_budget_table(
        trip_days=trip_days,
        travelers=args.travelers,
        budget_level=args.budget_level,
        currency=args.currency,
    )
    destination_query = quote_plus(args.destination)
    map_link = f"https://www.google.com/maps/search/{destination_query}"
    center_link = f"https://www.google.com/maps/search/{destination_query}+city+center"
    station_link = f"https://www.google.com/maps/search/{destination_query}+main+station"
    cover = (
        f"![{destination} cover]({args.cover_image})"
        if args.cover_image
        else "Add one trusted HTTPS cover image URL."
    )
    focus_text = (
        ", ".join(escape_markdown_text(item) for item in focus_items)
        if focus_items
        else "general highlights"
    )
    origin_text = origin

    day_blocks = [
        build_daily_block(
            day_index=idx,
            current_date=current_date,
            theme=choose_theme(idx, focus_items),
            pace=args.pace,
        )
        for idx, current_date in enumerate(dates, start=1)
    ]

    return "\n".join(
        [
            f"# {title}",
            "",
            f"Generated on: {date.today().isoformat()}",
            "",
            "## Trip Snapshot",
            f"- Destination: {destination}",
            f"- Dates: {args.start_date.isoformat()} to {args.end_date.isoformat()} ({trip_days} days)",
            f"- Origin: {origin_text}",
            f"- Travelers: {args.travelers}",
            f"- Pace: {args.pace}",
            f"- Focus: {focus_text}",
            f"- Budget level: {args.budget_level}",
            f"- Currency: {args.currency}",
            "",
            "## Cover Image",
            cover,
            "",
            "## Executive Summary",
            "- Add key route logic in 3-5 bullet points.",
            "- Explain why the order of places is practical.",
            "- Highlight major reservation windows and constraints.",
            "",
            "## Day-by-Day Itinerary",
            "",
            *day_blocks,
            "## Transportation and Routing",
            f"- Arrival route from {origin_text}: [Fill exact flight/train plan]",
            "- Local move strategy: [metro/walk/taxi mix with peak-hour notes]",
            f"- Destination map: [{destination} map]({map_link})",
            f"- Suggested base area: [city center search]({center_link})",
            f"- Transit hub reference: [main station / airport]({station_link})",
            "",
            "## Accommodation Strategy",
            "- Recommend 2-3 candidate neighborhoods with reasons.",
            "- Note average nightly rate range and safety considerations.",
            "- List tradeoffs: convenience vs budget vs quietness.",
            "",
            "## Food Plan",
            "- Add one signature food target per day.",
            "- Include opening hours and queue expectations.",
            "- Mark places that need reservations.",
            "",
            "## Budget Estimate",
            budget_table,
            "",
            f"- Rough total (excluding long-distance transport): {format_currency(budget_total, args.currency)}",
            "- Add long-distance transport quotes after live checks.",
            "",
            "## Booking Checklist",
            "- T-30 to T-14 days: lock intercity transport and hotels.",
            "- T-14 to T-7 days: reserve high-demand attractions and restaurants.",
            "- T-3 to T-1 days: confirm weather-sensitive activities.",
            "- Departure day: verify passport/ID, tickets, insurance, local payment methods.",
            "",
            "## Risks and Backup Plans",
            "- Weather risk: define indoor fallback for each outdoor-heavy day.",
            "- Transport risk: prepare one alternate route for each key transfer.",
            "- Health/safety risk: include emergency contact and nearest clinic/hospital.",
            "",
            "## Image Gallery",
            build_gallery(destination, args.image_url),
            "",
            "## Verification Log (Complete Before Final Delivery)",
            "| Item | Source | Last checked date | Status |",
            "| --- | --- | --- | --- |",
            "| Weather and alerts | [Official meteorological source] | [YYYY-MM-DD] | [Pending/Done] |",
            "| Opening hours and closures | [Official attraction site] | [YYYY-MM-DD] | [Pending/Done] |",
            "| Transport timetable | [Official operator site] | [YYYY-MM-DD] | [Pending/Done] |",
            "| Visa/entry policy | [Official gov/consulate source] | [YYYY-MM-DD] | [Pending/Done] |",
            "| Local events affecting crowds | [Official event source] | [YYYY-MM-DD] | [Pending/Done] |",
            "",
            "---",
            "Replace all bracketed placeholders with verified details before final sharing.",
        ]
    )


def build_output_path(
    output: str | None, destination: str, start_date: date, end_date: date
) -> Path:
    if output:
        resolved = Path(output).expanduser().resolve()
        cwd = Path.cwd().resolve()
        if not _is_relative_to(resolved, cwd):
            raise ValueError("--output must stay inside the current working directory.")
        if resolved.suffix.lower() != ".md":
            raise ValueError("--output must be a .md file.")
        return resolved
    filename = (
        f"trip-plan-{slugify(destination)}-{start_date.isoformat()}-{end_date.isoformat()}.md"
    )
    return Path.cwd() / filename


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an image-ready trip itinerary Markdown draft.",
    )
    parser.add_argument("--destination", required=True, help="Destination city/region.")
    parser.add_argument("--start-date", required=True, help="Trip start date: YYYY-MM-DD.")
    parser.add_argument("--end-date", required=True, help="Trip end date: YYYY-MM-DD.")
    parser.add_argument("--origin", default="", help="Origin city (optional).")
    parser.add_argument(
        "--travelers",
        type=int,
        default=2,
        help="Number of travelers (default: 2).",
    )
    parser.add_argument(
        "--budget-level",
        choices=["economy", "standard", "premium"],
        default="standard",
        help="Budget level profile.",
    )
    parser.add_argument(
        "--pace",
        choices=["relaxed", "balanced", "intense"],
        default="balanced",
        help="Daily pace profile.",
    )
    parser.add_argument(
        "--focus",
        default="",
        help="Comma-separated interests. Example: food,museum,nature.",
    )
    parser.add_argument(
        "--currency",
        default="CNY",
        help="Currency code shown in budget table (default: CNY).",
    )
    parser.add_argument("--cover-image", default="", help="Cover image URL.")
    parser.add_argument(
        "--image-url",
        action="append",
        default=[],
        help="Gallery image URL. Repeat for multiple images.",
    )
    parser.add_argument("--title", default="", help="Custom report title.")
    parser.add_argument("--output", default="", help="Output Markdown file path.")
    args = parser.parse_args()

    args.destination = sanitize_text(args.destination, "destination")
    if args.origin:
        args.origin = sanitize_text(args.origin, "origin")
    if args.title:
        args.title = sanitize_text(args.title, "title", max_length=160)
    args.focus = re.sub(r"[\x00-\x1f\x7f]", "", args.focus or "").strip()
    if args.cover_image:
        args.cover_image = validate_https_url(args.cover_image, "cover-image")
    if args.image_url:
        args.image_url = [validate_https_url(url, "image-url") for url in args.image_url]

    args.start_date = parse_date(args.start_date)
    args.end_date = parse_date(args.end_date)
    if args.end_date < args.start_date:
        raise ValueError("--end-date must be on or after --start-date.")
    if args.travelers <= 0:
        raise ValueError("--travelers must be a positive integer.")
    return args


def main() -> int:
    try:
        args = parse_args()
        output_path = build_output_path(
            output=args.output or None,
            destination=args.destination,
            start_date=args.start_date,
            end_date=args.end_date,
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(render_markdown(args), encoding="utf-8")
        print(f"Wrote trip plan: {output_path}")
        return 0
    except ValueError as exc:
        print(f"Error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
