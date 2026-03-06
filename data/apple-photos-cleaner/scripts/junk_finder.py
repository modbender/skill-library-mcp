#!/usr/bin/env python3
"""
Find junk photos: screenshots, low-quality images, burst leftovers, old screenshots.
"""

import sys
from datetime import datetime, timedelta
from typing import Any, Optional

from _common import (
    PhotosDB,
    build_asset_query,
    coredata_to_datetime,
    datetime_to_coredata,
    format_size,
    get_quality_score,
    run_script,
)


def find_junk(
    db_path: Optional[str] = None,
    screenshot_age_days: int = 30,
    quality_threshold: float = 0.3,
    include_duplicates: bool = True,
) -> dict[str, Any]:
    """
    Find various types of junk photos.

    Args:
        db_path: Path to database
        screenshot_age_days: Consider screenshots older than this as junk
        quality_threshold: Quality score threshold (lower = worse quality)
        include_duplicates: Include duplicate detection

    Returns:
        Dictionary with junk categories
    """
    with PhotosDB(db_path) as conn:
        cursor = conn.cursor()

        results = {
            "screenshots": [],
            "old_screenshots": [],
            "low_quality": [],
            "burst_leftovers": [],
            "possible_duplicates": [],
            "totals": {},
            "estimated_savings": {},
        }

        # 1. All screenshots
        query = build_asset_query(
            where_clauses=["a.ZTRASHEDSTATE != 1", "a.ZISDETECTEDSCREENSHOT = 1"],
            join_additional=True,
            order_by="a.ZDATECREATED DESC",
        )
        cursor.execute(query)

        screenshot_size = 0
        old_screenshot_size = 0
        screenshot_age_cutoff = datetime.now() - timedelta(days=screenshot_age_days)
        cutoff_timestamp = datetime_to_coredata(screenshot_age_cutoff)

        for row in cursor.fetchall():
            asset_id = row["Z_PK"]
            filename = row["ZFILENAME"]
            created = coredata_to_datetime(row["ZDATECREATED"])
            size = row["ZORIGINALFILESIZE"] or 0

            screenshot_size += size

            item = {
                "id": asset_id,
                "filename": filename,
                "created": created.isoformat() if created else None,
                "size": size,
                "size_formatted": format_size(size),
            }

            results["screenshots"].append(item)

            # Check if old screenshot
            if row["ZDATECREATED"] and row["ZDATECREATED"] < cutoff_timestamp:
                results["old_screenshots"].append(item)
                old_screenshot_size += size

        # 2. Low quality photos (not screenshots, not videos)
        query = build_asset_query(
            where_clauses=[
                "a.ZTRASHEDSTATE != 1",
                "a.ZKIND = 0",  # photos only
                "a.ZISDETECTEDSCREENSHOT != 1",  # exclude screenshots
            ],
            join_additional=True,
            join_computed=True,
            order_by="ca.ZFAILURESCORE DESC",
        )
        cursor.execute(query)

        low_quality_size = 0
        for row in cursor.fetchall():
            quality = get_quality_score(row)
            if quality is not None and quality < quality_threshold:
                asset_id = row["Z_PK"]
                filename = row["ZFILENAME"]
                created = coredata_to_datetime(row["ZDATECREATED"])
                size = row["ZORIGINALFILESIZE"] or 0

                low_quality_size += size

                results["low_quality"].append(
                    {
                        "id": asset_id,
                        "filename": filename,
                        "created": created.isoformat() if created else None,
                        "size": size,
                        "size_formatted": format_size(size),
                        "quality_score": round(quality, 3),
                        "failure_score": dict(row).get("ZFAILURESCORE"),
                        "noise_score": dict(row).get("ZNOISESCORE"),
                    }
                )

        # 3. Burst leftovers (non-picked burst photos)
        cursor.execute("""
            SELECT
                a.Z_PK,
                a.ZFILENAME,
                a.ZDATECREATED,
                a.ZAVALANCHEKIND,
                a.ZAVALANCHEPICKTYPE,
                aa.ZORIGINALFILESIZE
            FROM ZASSET a
            LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
            WHERE a.ZTRASHEDSTATE != 1
            AND a.ZAVALANCHEKIND > 0
            AND (a.ZAVALANCHEPICKTYPE IS NULL OR a.ZAVALANCHEPICKTYPE = 0)
            ORDER BY a.ZDATECREATED DESC
        """)

        burst_size = 0
        for row in cursor.fetchall():
            asset_id = row["Z_PK"]
            filename = row["ZFILENAME"]
            created = coredata_to_datetime(row["ZDATECREATED"])
            size = row["ZORIGINALFILESIZE"] or 0

            burst_size += size

            results["burst_leftovers"].append(
                {
                    "id": asset_id,
                    "filename": filename,
                    "created": created.isoformat() if created else None,
                    "size": size,
                    "size_formatted": format_size(size),
                    "avalanche_kind": row["ZAVALANCHEKIND"],
                }
            )

        # 4. Possible duplicates (if enabled)
        duplicate_size = 0
        if include_duplicates:
            # Method 1: Use Apple's duplicate detection
            cursor.execute("""
                SELECT
                    a.Z_PK,
                    a.ZFILENAME,
                    a.ZDATECREATED,
                    a.ZDUPLICATEASSETVISIBILITYSTATE,
                    aa.ZORIGINALFILESIZE
                FROM ZASSET a
                LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
                WHERE a.ZTRASHEDSTATE != 1
                AND a.ZDUPLICATEASSETVISIBILITYSTATE > 0
                ORDER BY a.ZDATECREATED DESC
            """)

            for row in cursor.fetchall():
                asset_id = row["Z_PK"]
                filename = row["ZFILENAME"]
                created = coredata_to_datetime(row["ZDATECREATED"])
                size = row["ZORIGINALFILESIZE"] or 0

                duplicate_size += size

                results["possible_duplicates"].append(
                    {
                        "id": asset_id,
                        "filename": filename,
                        "created": created.isoformat() if created else None,
                        "size": size,
                        "size_formatted": format_size(size),
                        "duplicate_state": row["ZDUPLICATEASSETVISIBILITYSTATE"],
                        "detection_method": "apple_builtin",
                    }
                )

        # Calculate totals
        results["totals"] = {
            "screenshots": len(results["screenshots"]),
            "old_screenshots": len(results["old_screenshots"]),
            "low_quality": len(results["low_quality"]),
            "burst_leftovers": len(results["burst_leftovers"]),
            "possible_duplicates": len(results["possible_duplicates"]),
        }

        # Estimated savings (conservative - assume we'd delete old screenshots + burst leftovers)
        conservative_savings = old_screenshot_size + burst_size
        aggressive_savings = screenshot_size + low_quality_size + burst_size + (duplicate_size // 2)

        results["estimated_savings"] = {
            "conservative": {
                "bytes": conservative_savings,
                "formatted": format_size(conservative_savings),
                "description": "Old screenshots + burst leftovers",
            },
            "aggressive": {
                "bytes": aggressive_savings,
                "formatted": format_size(aggressive_savings),
                "description": "All screenshots + low quality + bursts + ~50% of duplicates",
            },
        }

        return results


def format_summary(junk: dict[str, Any]) -> str:
    """Format junk findings as human-readable summary."""
    lines = []
    lines.append("🗑️  JUNK FINDER RESULTS")
    lines.append("=" * 50)
    lines.append("")

    totals = junk["totals"]

    lines.append("Found:")
    if totals["screenshots"] > 0:
        lines.append(f"  📸 Screenshots: {totals['screenshots']:,}")
        if totals["old_screenshots"] > 0:
            lines.append(f"     └─ Old (>30 days): {totals['old_screenshots']:,}")

    if totals["low_quality"] > 0:
        lines.append(f"  📉 Low Quality: {totals['low_quality']:,}")

    if totals["burst_leftovers"] > 0:
        lines.append(f"  📸 Burst Leftovers: {totals['burst_leftovers']:,}")

    if totals["possible_duplicates"] > 0:
        lines.append(f"  👥 Possible Duplicates: {totals['possible_duplicates']:,}")

    lines.append("")
    lines.append("Estimated Savings:")
    savings = junk["estimated_savings"]
    lines.append(f"  Conservative: {savings['conservative']['formatted']}")
    lines.append(f"    ({savings['conservative']['description']})")
    lines.append(f"  Aggressive: {savings['aggressive']['formatted']}")
    lines.append(f"    ({savings['aggressive']['description']})")
    lines.append("")

    return "\n".join(lines)


def main():
    def add_args(parser):
        parser.add_argument(
            "--screenshot-age",
            type=int,
            default=30,
            help="Consider screenshots older than N days as junk (default: 30)",
        )
        parser.add_argument(
            "--quality-threshold",
            type=float,
            default=0.3,
            help="Quality score threshold for low quality photos (default: 0.3)",
        )
        parser.add_argument("--no-duplicates", action="store_true", help="Skip duplicate detection")

    def invoke(db_path, args):
        return find_junk(
            db_path=db_path,
            screenshot_age_days=args.screenshot_age,
            quality_threshold=args.quality_threshold,
            include_duplicates=not args.no_duplicates,
        )

    return run_script(
        description="Find junk photos in Apple Photos library",
        analyze_fn=invoke,
        format_fn=format_summary,
        extra_args_fn=add_args,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --screenshot-age 60 --quality-threshold 0.25
  %(prog)s --output junk.json
  %(prog)s --human
        """,
    )


if __name__ == "__main__":
    sys.exit(main())
