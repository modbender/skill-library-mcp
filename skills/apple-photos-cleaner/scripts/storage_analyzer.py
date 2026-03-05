#!/usr/bin/env python3
"""
Detailed storage analysis: by year, type, source, growth trends, storage hogs.
"""

import sys
from typing import Any, Optional

from _common import PhotosDB, coredata_to_datetime, format_size, get_asset_kind_name, run_script


def analyze_storage(db_path: Optional[str] = None) -> dict[str, Any]:
    """
    Perform detailed storage analysis.

    Returns:
        Storage analysis dictionary
    """
    with PhotosDB(db_path) as conn:
        cursor = conn.cursor()

        # Total storage
        cursor.execute("""
            SELECT SUM(aa.ZORIGINALFILESIZE) as total_bytes
            FROM ZASSET a
            LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
            WHERE a.ZTRASHEDSTATE != 1
        """)
        total_storage = cursor.fetchone()["total_bytes"] or 0

        # By type (photo vs video)
        cursor.execute("""
            SELECT
                a.ZKIND,
                COUNT(*) as count,
                SUM(aa.ZORIGINALFILESIZE) as total_bytes,
                AVG(aa.ZORIGINALFILESIZE) as avg_bytes
            FROM ZASSET a
            LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
            WHERE a.ZTRASHEDSTATE != 1
            GROUP BY a.ZKIND
        """)

        by_kind = {}
        for row in cursor.fetchall():
            kind_name = get_asset_kind_name(row["ZKIND"])
            by_kind[kind_name] = {
                "count": row["count"],
                "total_bytes": row["total_bytes"] or 0,
                "total_formatted": format_size(row["total_bytes"] or 0),
                "avg_bytes": int(row["avg_bytes"] or 0),
                "avg_formatted": format_size(int(row["avg_bytes"] or 0)),
                "percent": ((row["total_bytes"] or 0) / total_storage * 100) if total_storage > 0 else 0,
            }

        # By year
        cursor.execute("""
            SELECT
                strftime('%Y', datetime(a.ZDATECREATED + 978307200, 'unixepoch')) as year,
                COUNT(*) as count,
                SUM(aa.ZORIGINALFILESIZE) as total_bytes
            FROM ZASSET a
            LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
            WHERE a.ZTRASHEDSTATE != 1
            GROUP BY year
            ORDER BY year
        """)

        by_year = {}
        for row in cursor.fetchall():
            year = row["year"]
            total_bytes = row["total_bytes"] or 0
            by_year[year] = {
                "count": row["count"],
                "total_bytes": total_bytes,
                "total_formatted": format_size(total_bytes),
                "percent": (total_bytes / total_storage * 100) if total_storage > 0 else 0,
            }

        # By year and month (for growth analysis)
        cursor.execute("""
            SELECT
                strftime('%Y-%m', datetime(a.ZDATECREATED + 978307200, 'unixepoch')) as year_month,
                COUNT(*) as count,
                SUM(aa.ZORIGINALFILESIZE) as total_bytes
            FROM ZASSET a
            LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
            WHERE a.ZTRASHEDSTATE != 1
            GROUP BY year_month
            ORDER BY year_month
        """)

        growth = []
        cumulative = 0
        for row in cursor.fetchall():
            total_bytes = row["total_bytes"] or 0
            cumulative += total_bytes
            growth.append(
                {
                    "period": row["year_month"],
                    "count": row["count"],
                    "added_bytes": total_bytes,
                    "added_formatted": format_size(total_bytes),
                    "cumulative_bytes": cumulative,
                    "cumulative_formatted": format_size(cumulative),
                }
            )

        # Screenshots vs non-screenshots
        cursor.execute("""
            SELECT
                a.ZISDETECTEDSCREENSHOT,
                COUNT(*) as count,
                SUM(aa.ZORIGINALFILESIZE) as total_bytes
            FROM ZASSET a
            LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
            WHERE a.ZTRASHEDSTATE != 1
            GROUP BY a.ZISDETECTEDSCREENSHOT
        """)

        by_source = {}
        for row in cursor.fetchall():
            source = "screenshots" if row["ZISDETECTEDSCREENSHOT"] else "photos_videos"
            total_bytes = row["total_bytes"] or 0
            by_source[source] = {
                "count": row["count"],
                "total_bytes": total_bytes,
                "total_formatted": format_size(total_bytes),
                "percent": (total_bytes / total_storage * 100) if total_storage > 0 else 0,
            }

        # Storage hogs (top 20 largest files)
        cursor.execute("""
            SELECT
                a.Z_PK,
                a.ZFILENAME,
                a.ZDATECREATED,
                a.ZKIND,
                aa.ZORIGINALFILESIZE,
                aa.ZORIGINALWIDTH,
                aa.ZORIGINALHEIGHT
            FROM ZASSET a
            LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
            WHERE a.ZTRASHEDSTATE != 1
            AND aa.ZORIGINALFILESIZE IS NOT NULL
            ORDER BY aa.ZORIGINALFILESIZE DESC
            LIMIT 20
        """)

        storage_hogs = []
        for row in cursor.fetchall():
            created = coredata_to_datetime(row["ZDATECREATED"])
            storage_hogs.append(
                {
                    "id": row["Z_PK"],
                    "filename": row["ZFILENAME"],
                    "created": created.isoformat() if created else None,
                    "kind": get_asset_kind_name(row["ZKIND"]),
                    "size": row["ZORIGINALFILESIZE"],
                    "size_formatted": format_size(row["ZORIGINALFILESIZE"]),
                    "dimensions": f"{row['ZORIGINALWIDTH']}x{row['ZORIGINALHEIGHT']}"
                    if row["ZORIGINALWIDTH"]
                    else None,
                }
            )

        # By file type (if available in ZUNIFORMTYPEIDENTIFIER)
        cursor.execute("""
            SELECT
                a.ZUNIFORMTYPEIDENTIFIER,
                COUNT(*) as count,
                SUM(aa.ZORIGINALFILESIZE) as total_bytes
            FROM ZASSET a
            LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
            WHERE a.ZTRASHEDSTATE != 1
            AND a.ZUNIFORMTYPEIDENTIFIER IS NOT NULL
            GROUP BY a.ZUNIFORMTYPEIDENTIFIER
            ORDER BY total_bytes DESC
        """)

        by_file_type = []
        for row in cursor.fetchall():
            total_bytes = row["total_bytes"] or 0
            by_file_type.append(
                {
                    "type": row["ZUNIFORMTYPEIDENTIFIER"],
                    "count": row["count"],
                    "total_bytes": total_bytes,
                    "total_formatted": format_size(total_bytes),
                    "percent": (total_bytes / total_storage * 100) if total_storage > 0 else 0,
                }
            )

        return {
            "summary": {
                "total_storage": total_storage,
                "total_formatted": format_size(total_storage),
            },
            "by_kind": by_kind,
            "by_year": by_year,
            "by_source": by_source,
            "by_file_type": by_file_type,
            "growth": growth,
            "storage_hogs": storage_hogs,
        }


def format_summary(analysis: dict[str, Any]) -> str:
    """Format storage analysis as human-readable summary."""
    lines = []
    lines.append("💾 STORAGE ANALYSIS")
    lines.append("=" * 50)
    lines.append("")

    lines.append(f"Total Storage: {analysis['summary']['total_formatted']}")
    lines.append("")

    # By kind
    lines.append("By Type:")
    for kind, data in analysis["by_kind"].items():
        lines.append(f"  {kind.title()}: {data['total_formatted']} ({data['percent']:.1f}%)")
        lines.append(f"    {data['count']:,} items, avg {data['avg_formatted']}")
    lines.append("")

    # By source
    if analysis["by_source"]:
        lines.append("By Source:")
        for source, data in analysis["by_source"].items():
            source_name = "Screenshots" if source == "screenshots" else "Photos & Videos"
            lines.append(f"  {source_name}: {data['total_formatted']} ({data['percent']:.1f}%)")
        lines.append("")

    # By year
    if analysis["by_year"]:
        lines.append("By Year:")
        for year, data in sorted(analysis["by_year"].items(), reverse=True)[:10]:
            lines.append(f"  {year}: {data['total_formatted']} ({data['count']:,} items)")
        lines.append("")

    # Storage hogs
    if analysis["storage_hogs"]:
        lines.append("Top 10 Largest Files:")
        for i, item in enumerate(analysis["storage_hogs"][:10], 1):
            kind_emoji = "📹" if item["kind"] == "video" else "📸"
            lines.append(f"  {i}. {kind_emoji} {item['size_formatted']} - {item['filename']}")
            if item["dimensions"]:
                lines.append(f"      {item['dimensions']}, {item['kind']}")
        lines.append("")

    # Growth summary
    if analysis["growth"]:
        recent_growth = analysis["growth"][-12:]  # Last 12 months
        if recent_growth:
            total_recent = sum(m["added_bytes"] for m in recent_growth)
            avg_monthly = total_recent / len(recent_growth)
            lines.append(f"Recent Growth (last {len(recent_growth)} months):")
            lines.append(f"  Total added: {format_size(total_recent)}")
            lines.append(f"  Average per month: {format_size(int(avg_monthly))}")
            lines.append("")

    # File types
    if analysis["by_file_type"]:
        lines.append("Top File Types:")
        for ft in analysis["by_file_type"][:5]:
            # Simplify UTI for display
            type_name = ft["type"].split(".")[-1].upper()
            lines.append(f"  {type_name}: {ft['total_formatted']} ({ft['percent']:.1f}%)")
        lines.append("")

    return "\n".join(lines)


def main():
    return run_script(
        description="Analyze Apple Photos storage",
        analyze_fn=lambda db_path, _args: analyze_storage(db_path),
        format_fn=format_summary,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --output storage.json
  %(prog)s --human
        """,
    )


if __name__ == "__main__":
    sys.exit(main())
