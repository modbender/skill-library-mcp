#!/usr/bin/env python3
"""Fetch and normalize latest AFAD earthquake records."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DEFAULT_SOURCE_URL = "https://deprem.afad.gov.tr/apiv2/event/filter"
SOURCE_TZ = timezone(timedelta(hours=3))


class AppError(Exception):
    def __init__(self, code: str, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.exit_code = exit_code


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch and normalize AFAD recent earthquakes as JSON."
    )
    parser.add_argument("--hours", type=int, default=None)
    parser.add_argument("--days", type=int, default=None)
    parser.add_argument("--minMag", dest="min_mag", type=float, default=None)
    parser.add_argument("--query", type=str, default=None)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--source-url", default=DEFAULT_SOURCE_URL)
    parser.add_argument("--fixture", default=None)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def to_utc_iso(dt: datetime) -> str:
    return (
        dt.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def parse_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        dt = None

    if dt is None:
        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y.%m.%d %H:%M:%S",
        ):
            try:
                dt = datetime.strptime(text, fmt)
                break
            except ValueError:
                continue

    if dt is None:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=SOURCE_TZ)

    return dt.astimezone(timezone.utc)


def pick_first(raw: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in raw and raw[key] not in (None, ""):
            return raw[key]
    return None


def split_location(location: str) -> tuple[str | None, str | None]:
    text = location.strip()
    if not text:
        return None, None

    # Common AFAD style can be "DISTRICT (PROVINCE)"
    if "(" in text and text.endswith(")"):
        head, tail = text.rsplit("(", 1)
        district = head.strip(" -") or None
        province = tail[:-1].strip() or None
        return province, district

    return None, None


def normalize_event(raw: dict[str, Any]) -> dict[str, Any]:
    location = str(pick_first(raw, "location", "place", "title") or "Unknown").strip()
    province, district = split_location(location)

    raw_time = pick_first(raw, "date", "time", "eventDate", "datetime")
    dt = parse_datetime(raw_time)

    normalized = {
        "id": str(pick_first(raw, "eventID", "eventId", "id") or ""),
        "time_utc": to_utc_iso(dt) if dt else None,
        "magnitude": parse_float(pick_first(raw, "m", "mag", "magnitude")),
        "depth_km": parse_float(pick_first(raw, "depth", "depth_km")),
        "latitude": parse_float(pick_first(raw, "lat", "latitude")),
        "longitude": parse_float(pick_first(raw, "lon", "longitude")),
        "location": location or "Unknown",
        "province": (
            str(pick_first(raw, "province", "il") or province)
            if (pick_first(raw, "province", "il") or province)
            else None
        ),
        "district": (
            str(pick_first(raw, "district", "ilce") or district)
            if (pick_first(raw, "district", "ilce") or district)
            else None
        ),
        "source": "AFAD",
    }
    return normalized


def extract_events(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        events = payload
    elif isinstance(payload, dict):
        events = pick_first(payload, "data", "result", "items", "events")
    else:
        events = None

    if not isinstance(events, list):
        raise AppError(
            "PARSE_ERROR",
            "AFAD yaniti icinde deprem listesi bulunamadi",
            exit_code=5,
        )

    output: list[dict[str, Any]] = []
    for event in events:
        if isinstance(event, dict):
            output.append(event)

    return output


def resolve_time_window(hours: int | None, days: int | None) -> timedelta | None:
    if hours is None and days is None:
        return None

    total_hours = 0
    if hours is not None:
        if hours < 0:
            raise AppError(
                "INPUT_ERROR",
                "--hours degeri sifirdan kucuk olamaz",
                exit_code=2,
            )
        total_hours += hours
    if days is not None:
        if days < 0:
            raise AppError(
                "INPUT_ERROR",
                "--days degeri sifirdan kucuk olamaz",
                exit_code=2,
            )
        total_hours += days * 24

    if total_hours <= 0:
        raise AppError(
            "INPUT_ERROR",
            "--hours/--days toplam zaman araligi sifirdan buyuk olmali",
            exit_code=2,
        )

    return timedelta(hours=total_hours)


def build_url(source_url: str, window: timedelta | None) -> str:
    params: dict[str, str] = {"orderby": "timedesc"}

    if window is not None:
        now_local = datetime.now(timezone.utc).astimezone(SOURCE_TZ)
        start_local = now_local - window
        params["start"] = start_local.replace(tzinfo=None, microsecond=0).isoformat(
            sep="T"
        )
        params["end"] = now_local.replace(tzinfo=None, microsecond=0).isoformat(sep="T")

    return f"{source_url}?{urlencode(params)}"


def fetch_events(
    source_url: str,
    timeout: int,
    window: timedelta | None,
) -> list[dict[str, Any]]:
    url = build_url(source_url=source_url, window=window)
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "turkiye-afad-deprem-skill/0.1",
        },
        method="GET",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", 200)
            if int(status) >= 400:
                raise AppError(
                    "HTTP_ERROR",
                    f"AFAD servisi HTTP {status} dondu",
                    exit_code=4,
                )
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        raise AppError(
            "HTTP_ERROR",
            f"AFAD servisi HTTP {exc.code} dondu",
            exit_code=4,
        ) from exc
    except URLError as exc:
        raise AppError(
            "NETWORK_ERROR",
            f"AFAD servisine erisilemedi: {exc.reason}",
            exit_code=3,
        ) from exc

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise AppError(
            "PARSE_ERROR",
            "AFAD JSON yaniti cozumlenemedi",
            exit_code=5,
        ) from exc

    return extract_events(payload)


def load_fixture(path: str) -> list[dict[str, Any]]:
    fixture_path = Path(path)
    if not fixture_path.exists():
        raise AppError(
            "INPUT_ERROR",
            f"Fixture dosyasi bulunamadi: {fixture_path}",
            exit_code=2,
        )

    try:
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AppError(
            "PARSE_ERROR",
            "Fixture JSON gecersiz",
            exit_code=5,
        ) from exc

    return extract_events(payload)


def normalize_events(
    raw_events: list[dict[str, Any]],
    window: timedelta | None,
    min_magnitude: float | None,
    query: str | None,
    now_utc: datetime | None = None,
) -> list[dict[str, Any]]:
    now = now_utc or datetime.now(timezone.utc)
    earliest = now - window if window else None
    query_norm = query.strip().casefold() if query else None

    items: list[dict[str, Any]] = []
    for raw in raw_events:
        normalized = normalize_event(raw)

        if normalized["time_utc"] is None:
            continue
        event_time = datetime.fromisoformat(normalized["time_utc"].replace("Z", "+00:00"))

        if earliest is not None and event_time < earliest:
            continue

        magnitude = normalized["magnitude"]
        if min_magnitude is not None:
            if magnitude is None or magnitude < min_magnitude:
                continue

        if query_norm is not None:
            if query_norm not in normalized["location"].casefold():
                continue

        items.append(normalized)

    # Sort newest first by UTC time string
    items.sort(key=lambda item: item["time_utc"], reverse=True)
    return items


def validate_args(args: argparse.Namespace) -> None:
    if args.timeout <= 0:
        raise AppError(
            "INPUT_ERROR",
            "--timeout degeri sifirdan buyuk olmali",
            exit_code=2,
        )
    if args.min_mag is not None and args.min_mag < 0:
        raise AppError(
            "INPUT_ERROR",
            "--minMag degeri sifirdan kucuk olamaz",
            exit_code=2,
        )


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    validate_args(args)
    window = resolve_time_window(args.hours, args.days)

    if args.fixture:
        raw_events = load_fixture(args.fixture)
    else:
        raw_events = fetch_events(
            source_url=args.source_url,
            timeout=args.timeout,
            window=window,
        )

    items = normalize_events(
        raw_events,
        window=window,
        min_magnitude=args.min_mag,
        query=args.query,
    )

    output = {
        "source": "AFAD",
        "fetched_at_utc": to_utc_iso(datetime.now(timezone.utc)),
        "count": len(items),
        "items": items,
    }

    if args.pretty:
        json.dump(output, sys.stdout, indent=2, ensure_ascii=False)
    else:
        json.dump(output, sys.stdout, separators=(",", ":"), ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    try:
        return run(sys.argv[1:])
    except AppError as exc:
        print(
            json.dumps({"error": exc.code, "message": exc.message}, ensure_ascii=False),
            file=sys.stderr,
        )
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
