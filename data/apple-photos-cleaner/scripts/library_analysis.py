#!/usr/bin/env python3
"""
Analyze Apple Photos library: counts, storage, date ranges, people, quality scores.
"""

import sys
from typing import Any, Optional

from _common import (
    PhotosDB,
    coredata_to_datetime,
    format_date_range,
    format_size,
    get_asset_kind_name,
    get_quality_score,
    run_script,
)


def analyze_library(db_path: Optional[str] = None) -> dict[str, Any]:
    """
    Perform comprehensive library analysis.

    Returns:
        Dictionary with analysis results
    """
    with PhotosDB(db_path) as conn:
        cursor = conn.cursor()

        # Basic counts
        cursor.execute("""
            SELECT COUNT(*) as total FROM ZASSET WHERE ZTRASHEDSTATE != 1
        """)
        total_assets = cursor.fetchone()["total"]

        # By kind
        cursor.execute("""
            SELECT ZKIND, COUNT(*) as count
            FROM ZASSET
            WHERE ZTRASHEDSTATE != 1
            GROUP BY ZKIND
        """)
        by_kind = {get_asset_kind_name(row["ZKIND"]): row["count"] for row in cursor.fetchall()}

        # Screenshots
        cursor.execute("""
            SELECT COUNT(*) as count FROM ZASSET
            WHERE ZTRASHEDSTATE != 1 AND ZISDETECTEDSCREENSHOT = 1
        """)
        screenshot_count = cursor.fetchone()["count"]

        # Favorites
        cursor.execute("""
            SELECT COUNT(*) as count FROM ZASSET
            WHERE ZTRASHEDSTATE != 1 AND ZFAVORITE = 1
        """)
        favorites_count = cursor.fetchone()["count"]

        # Hidden
        cursor.execute("""
            SELECT COUNT(*) as count FROM ZASSET
            WHERE ZTRASHEDSTATE != 1 AND ZHIDDEN = 1
        """)
        hidden_count = cursor.fetchone()["count"]

        # Date range
        cursor.execute("""
            SELECT MIN(ZDATECREATED) as min_date, MAX(ZDATECREATED) as max_date
            FROM ZASSET WHERE ZTRASHEDSTATE != 1
        """)
        date_row = cursor.fetchone()
        min_date = coredata_to_datetime(date_row["min_date"])
        max_date = coredata_to_datetime(date_row["max_date"])

        # By year
        cursor.execute("""
            SELECT
                strftime('%Y', datetime(ZDATECREATED + 978307200, 'unixepoch')) as year,
                COUNT(*) as count
            FROM ZASSET
            WHERE ZTRASHEDSTATE != 1
            GROUP BY year
            ORDER BY year
        """)
        by_year = {row["year"]: row["count"] for row in cursor.fetchall()}

        # Storage analysis
        cursor.execute("""
            SELECT
                SUM(aa.ZORIGINALFILESIZE) as total_bytes,
                AVG(aa.ZORIGINALFILESIZE) as avg_bytes
            FROM ZASSET a
            LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
            WHERE a.ZTRASHEDSTATE != 1
        """)
        storage_row = cursor.fetchone()
        total_storage = storage_row["total_bytes"] or 0
        avg_size = storage_row["avg_bytes"] or 0

        # Storage by kind
        cursor.execute("""
            SELECT
                a.ZKIND,
                SUM(aa.ZORIGINALFILESIZE) as total_bytes
            FROM ZASSET a
            LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
            WHERE a.ZTRASHEDSTATE != 1
            GROUP BY a.ZKIND
        """)
        storage_by_kind = {get_asset_kind_name(row["ZKIND"]): row["total_bytes"] or 0 for row in cursor.fetchall()}

        # Storage by year
        cursor.execute("""
            SELECT
                strftime('%Y', datetime(a.ZDATECREATED + 978307200, 'unixepoch')) as year,
                SUM(aa.ZORIGINALFILESIZE) as total_bytes
            FROM ZASSET a
            LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
            WHERE a.ZTRASHEDSTATE != 1
            GROUP BY year
            ORDER BY year
        """)
        storage_by_year = {row["year"]: row["total_bytes"] or 0 for row in cursor.fetchall()}

        # People stats
        cursor.execute("""
            SELECT
                p.ZFULLNAME,
                COUNT(DISTINCT df.ZASSETFORFACE) as photo_count
            FROM ZPERSON p
            JOIN ZDETECTEDFACE df ON p.Z_PK = df.ZPERSONFORFACE
            JOIN ZASSET a ON df.ZASSETFORFACE = a.Z_PK
            WHERE a.ZTRASHEDSTATE != 1
            GROUP BY p.Z_PK
            ORDER BY photo_count DESC
            LIMIT 10
        """)
        top_people = [{"name": row["ZFULLNAME"], "photo_count": row["photo_count"]} for row in cursor.fetchall()]

        # Quality score distribution (sample to avoid expensive computation)
        cursor.execute("""
            SELECT
                ca.ZFAILURESCORE,
                ca.ZNOISESCORE,
                ca.ZPLEASANTCOMPOSITIONSCORE,
                ca.ZPLEASANTLIGHTINGSCORE
            FROM ZASSET a
            LEFT JOIN ZCOMPUTEDASSETATTRIBUTES ca ON a.Z_PK = ca.ZASSET
            WHERE a.ZTRASHEDSTATE != 1 AND a.ZKIND = 0
            LIMIT 1000
        """)

        quality_scores = []
        for row in cursor.fetchall():
            score = get_quality_score(row)
            if score is not None:
                quality_scores.append(score)

        quality_stats = None
        if quality_scores:
            quality_stats = {
                "min": min(quality_scores),
                "max": max(quality_scores),
                "avg": sum(quality_scores) / len(quality_scores),
                "sample_size": len(quality_scores),
            }

        # Location stats
        cursor.execute("""
            SELECT COUNT(*) as count FROM ZASSET
            WHERE ZTRASHEDSTATE != 1
            AND ZLATITUDE IS NOT NULL
            AND ZLONGITUDE IS NOT NULL
        """)
        with_location = cursor.fetchone()["count"]

        # Burst stats
        cursor.execute("""
            SELECT COUNT(*) as count FROM ZASSET
            WHERE ZTRASHEDSTATE != 1 AND ZAVALANCHEKIND > 0
        """)
        burst_count = cursor.fetchone()["count"]

        return {
            "summary": {
                "total_assets": total_assets,
                "total_storage": total_storage,
                "total_storage_formatted": format_size(total_storage),
                "avg_size": int(avg_size),
                "avg_size_formatted": format_size(int(avg_size)),
                "date_range": format_date_range(min_date, max_date),
                "min_date": min_date.isoformat() if min_date else None,
                "max_date": max_date.isoformat() if max_date else None,
            },
            "by_type": {
                **by_kind,
                "screenshots": screenshot_count,
                "favorites": favorites_count,
                "hidden": hidden_count,
                "bursts": burst_count,
                "with_location": with_location,
            },
            "by_year": by_year,
            "storage_by_kind": {k: {"bytes": v, "formatted": format_size(v)} for k, v in storage_by_kind.items()},
            "storage_by_year": {k: {"bytes": v, "formatted": format_size(v)} for k, v in storage_by_year.items()},
            "top_people": top_people,
            "quality_distribution": quality_stats,
        }


def format_summary(analysis: dict[str, Any]) -> str:
    """Format analysis as human-readable summary."""
    lines = []
    lines.append("📊 APPLE PHOTOS LIBRARY ANALYSIS")
    lines.append("=" * 50)
    lines.append("")

    summary = analysis["summary"]
    lines.append(f"Total Assets: {summary['total_assets']:,}")
    lines.append(f"Total Storage: {summary['total_storage_formatted']}")
    lines.append(f"Average Size: {summary['avg_size_formatted']}")
    lines.append(f"Date Range: {summary['date_range']}")
    lines.append("")

    lines.append("By Type:")
    by_type = analysis["by_type"]
    for key in ["photo", "video", "screenshots", "favorites", "hidden", "bursts", "with_location"]:
        if key in by_type and by_type[key] > 0:
            lines.append(f"  {key.title()}: {by_type[key]:,}")
    lines.append("")

    if analysis["by_year"]:
        lines.append("By Year:")
        for year, count in sorted(analysis["by_year"].items()):
            storage = analysis["storage_by_year"].get(year, {})
            storage_str = storage.get("formatted", "N/A")
            lines.append(f"  {year}: {count:,} items, {storage_str}")
        lines.append("")

    if analysis["top_people"]:
        lines.append("Top People:")
        for person in analysis["top_people"][:5]:
            lines.append(f"  {person['name']}: {person['photo_count']:,} photos")
        lines.append("")

    if analysis["quality_distribution"]:
        q = analysis["quality_distribution"]
        lines.append("Quality Scores (sample):")
        lines.append(f"  Min: {q['min']:.3f}")
        lines.append(f"  Avg: {q['avg']:.3f}")
        lines.append(f"  Max: {q['max']:.3f}")
        lines.append(f"  (based on {q['sample_size']} photos)")
        lines.append("")

    return "\n".join(lines)


def main():
    return run_script(
        description="Analyze Apple Photos library",
        analyze_fn=lambda db_path, _args: analyze_library(db_path),
        format_fn=format_summary,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --output analysis.json
  %(prog)s --db-path ~/path/to/Photos.sqlite --human
        """,
    )


if __name__ == "__main__":
    sys.exit(main())
