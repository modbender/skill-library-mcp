#!/usr/bin/env python3
"""
Analyze Live Photos vs still photos: identify Live Photos, compare storage,
find Live Photos that could be converted to stills to save space.
"""

import sys
from typing import Any, Optional

from _common import (
    PhotosDB,
    _safe_col,
    coredata_to_datetime,
    format_size,
    get_quality_score,
    run_script,
    validate_year,
)

# Live Photo sub-kinds
LIVE_PHOTO_SUBTYPE = 2
PLAYBACK_LIVE = 2
PLAYBACK_LOOP = 3
PLAYBACK_BOUNCE = 4
PLAYBACK_LONG_EXPOSURE = 5

PLAYBACK_NAMES = {
    1: "still",
    PLAYBACK_LIVE: "live",
    PLAYBACK_LOOP: "loop",
    PLAYBACK_BOUNCE: "bounce",
    PLAYBACK_LONG_EXPOSURE: "long_exposure",
}


def analyze_live_photos(
    db_path: Optional[str] = None,
    year: Optional[str] = None,
) -> dict[str, Any]:
    """
    Analyze Live Photos in the library.

    Returns breakdown of live vs still, storage comparison, and
    Live Photos that are rarely played (candidates for conversion).
    """
    with PhotosDB(db_path) as conn:
        cursor = conn.cursor()

        # Check which columns exist
        cursor.execute("PRAGMA table_info(ZASSET)")
        columns = {row["name"] for row in cursor.fetchall()}
        has_subtype = "ZKINDSUBTYPE" in columns
        has_playback = "ZPLAYBACKSTYLE" in columns

        if not has_subtype and not has_playback:
            return {
                "error": "Live Photo columns not found in this database version",
                "live_photos": [],
                "summary": {
                    "total_photos": 0,
                    "live_count": 0,
                    "still_count": 0,
                    "live_storage": 0,
                    "live_storage_formatted": "0 B",
                    "still_storage": 0,
                    "still_storage_formatted": "0 B",
                    "potential_savings": 0,
                    "potential_savings_formatted": "0 B",
                },
            }

        # Build dynamic query based on available columns
        select_cols = [
            "a.Z_PK",
            "a.ZFILENAME",
            "a.ZDATECREATED",
            "a.ZKIND",
            "a.ZFAVORITE",
            "a.ZWIDTH",
            "a.ZHEIGHT",
            "aa.ZORIGINALFILESIZE",
        ]
        if has_subtype:
            select_cols.append("a.ZKINDSUBTYPE")
        if has_playback:
            select_cols.append("a.ZPLAYBACKSTYLE")

        # Include quality scores for identifying best live photos
        select_cols.extend(
            [
                "ca.ZPLEASANTCOMPOSITIONSCORE",
                "ca.ZPLEASANTLIGHTINGSCORE",
                "ca.ZFAILURESCORE",
                "ca.ZNOISESCORE",
            ]
        )

        where = ["a.ZTRASHEDSTATE != 1", "a.ZKIND = 0"]  # photos only
        params: list = []
        if year:
            year = validate_year(year)
            where.append("strftime('%Y', datetime(a.ZDATECREATED + 978307200, 'unixepoch')) = ?")
            params.append(year)

        query = f"""
            SELECT {", ".join(select_cols)}
            FROM ZASSET a
            LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
            LEFT JOIN ZCOMPUTEDASSETATTRIBUTES ca ON a.Z_PK = ca.ZASSET
            WHERE {" AND ".join(where)}
            ORDER BY a.ZDATECREATED DESC
        """
        cursor.execute(query, params)

        live_photos = []
        still_photos_count = 0
        still_photos_size = 0
        live_total_size = 0
        by_playback = {}
        by_year: dict[str, dict] = {}

        for row in cursor.fetchall():
            rd = dict(row)
            subtype = _safe_col(rd, "ZKINDSUBTYPE", 0) or 0
            playback = _safe_col(rd, "ZPLAYBACKSTYLE", 1) or 1
            size = rd.get("ZORIGINALFILESIZE") or 0
            is_live = subtype == LIVE_PHOTO_SUBTYPE or playback >= PLAYBACK_LIVE

            created = coredata_to_datetime(rd["ZDATECREATED"])
            yr = str(created.year) if created else "Unknown"

            if yr not in by_year:
                by_year[yr] = {"live": 0, "still": 0, "live_size": 0, "still_size": 0}

            if is_live:
                live_total_size += size
                by_year[yr]["live"] += 1
                by_year[yr]["live_size"] += size

                playback_name = PLAYBACK_NAMES.get(playback, f"unknown_{playback}")
                by_playback[playback_name] = by_playback.get(playback_name, 0) + 1

                quality = get_quality_score(rd)
                live_photos.append(
                    {
                        "id": rd["Z_PK"],
                        "filename": rd["ZFILENAME"],
                        "created": created.isoformat() if created else None,
                        "size": size,
                        "size_formatted": format_size(size),
                        "is_favorite": bool(rd.get("ZFAVORITE")),
                        "playback_style": playback_name,
                        "quality_score": round(quality, 3) if quality else None,
                        "dimensions": f"{rd.get('ZWIDTH', 0)}x{rd.get('ZHEIGHT', 0)}",
                    }
                )
            else:
                still_photos_count += 1
                still_photos_size += size
                by_year[yr]["still"] += 1
                by_year[yr]["still_size"] += size

        # Estimate savings: Live Photos have a ~2-3s video component that
        # is roughly 40-60% of the total file size on average.
        estimated_video_pct = 0.50
        potential_savings = int(live_total_size * estimated_video_pct)

        # Sort live photos by size desc (biggest savings first)
        live_photos.sort(key=lambda x: x["size"], reverse=True)

        # Non-favorite live photos are stronger conversion candidates
        conversion_candidates = [p for p in live_photos if not p["is_favorite"]]

        return {
            "live_photos": live_photos[:200],
            "conversion_candidates": conversion_candidates[:100],
            "by_playback_style": by_playback,
            "by_year": [
                {
                    "year": yr,
                    "live": info["live"],
                    "still": info["still"],
                    "live_size": info["live_size"],
                    "live_size_formatted": format_size(info["live_size"]),
                    "still_size": info["still_size"],
                    "still_size_formatted": format_size(info["still_size"]),
                }
                for yr, info in sorted(by_year.items(), reverse=True)
            ],
            "summary": {
                "total_photos": len(live_photos) + still_photos_count,
                "live_count": len(live_photos),
                "still_count": still_photos_count,
                "live_pct": round(100 * len(live_photos) / max(1, len(live_photos) + still_photos_count), 1),
                "live_storage": live_total_size,
                "live_storage_formatted": format_size(live_total_size),
                "still_storage": still_photos_size,
                "still_storage_formatted": format_size(still_photos_size),
                "potential_savings": potential_savings,
                "potential_savings_formatted": format_size(potential_savings),
                "unfavorited_live_count": len(conversion_candidates),
            },
        }


def format_summary(data: dict[str, Any]) -> str:
    """Format human-readable summary."""
    lines = []
    s = data["summary"]

    if "error" in data:
        lines.append(f"⚠️  {data['error']}")
        return "\n".join(lines)

    lines.append("📸 LIVE PHOTO ANALYSIS")
    lines.append("=" * 50)
    lines.append(f"Total photos:       {s['total_photos']:,}")
    lines.append(f"Live Photos:        {s['live_count']:,} ({s['live_pct']}%)")
    lines.append(f"Still photos:       {s['still_count']:,}")
    lines.append(f"Live storage:       {s['live_storage_formatted']}")
    lines.append(f"Still storage:      {s['still_storage_formatted']}")
    lines.append("")
    lines.append(f"💾 Potential savings if converted to still: {s['potential_savings_formatted']}")
    lines.append(f"   Unfavorited Live Photos (candidates):   {s['unfavorited_live_count']:,}")

    if data["by_playback_style"]:
        lines.append("")
        lines.append("Playback styles:")
        for style, count in sorted(data["by_playback_style"].items(), key=lambda x: -x[1]):
            lines.append(f"  {style:20s} {count:,}")

    if data["by_year"]:
        lines.append("")
        lines.append("By year:")
        lines.append(f"  {'Year':<8} {'Live':>8} {'Still':>8} {'Live Size':>12}")
        for yr in data["by_year"][:10]:
            lines.append(f"  {yr['year']:<8} {yr['live']:>8,} {yr['still']:>8,} {yr['live_size_formatted']:>12}")

    if data["live_photos"][:10]:
        lines.append("")
        lines.append("Largest Live Photos:")
        for p in data["live_photos"][:10]:
            fav = "⭐" if p["is_favorite"] else "  "
            lines.append(f"  {fav} {p['filename']:40s} {p['size_formatted']:>10} ({p['playback_style']})")

    return "\n".join(lines)


def main():
    def add_args(parser):
        parser.add_argument("--year", help="Filter to specific year (YYYY)")

    def invoke(db_path, args):
        return analyze_live_photos(db_path=db_path, year=args.year)

    return run_script(
        description="Analyze Live Photos in Apple Photos",
        analyze_fn=invoke,
        format_fn=format_summary,
        extra_args_fn=add_args,
    )


if __name__ == "__main__":
    sys.exit(main())
