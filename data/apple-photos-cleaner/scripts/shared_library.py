#!/usr/bin/env python3
"""
Analyze the Shared Library in Apple Photos.

Identifies assets shared with/from the Shared Library, contributor
breakdown, overlap analysis, and storage impact of shared content.
"""

import sys
from typing import Any, Optional

from _common import (
    PhotosDB,
    _safe_col,
    coredata_to_datetime,
    format_size,
    run_script,
)


def analyze_shared_library(
    db_path: Optional[str] = None,
) -> dict[str, Any]:
    """
    Analyze the Shared Library vs Personal Library.

    Returns a breakdown of personal vs shared assets, storage comparison,
    contributor identifiers, and content-type distributions.
    """
    with PhotosDB(db_path) as conn:
        cursor = conn.cursor()

        # Check which columns are available
        cursor.execute("PRAGMA table_info(ZASSET)")
        columns = {row["name"] for row in cursor.fetchall()}
        has_scope = "ZLIBRARYSCOPE" in columns
        has_shared_id = "ZSHAREDLIBRARYSCOPEIDENTIFIER" in columns
        has_active = "ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE" in columns

        if not has_scope:
            return {
                "error": "Shared Library columns not found. "
                "Shared Library requires macOS 13+ / iOS 16+ and Photos database v16+.",
                "shared_library_enabled": False,
                "summary": {
                    "personal_count": 0,
                    "shared_count": 0,
                    "shared_storage": 0,
                    "shared_storage_formatted": "0 B",
                },
            }

        # Query all non-trashed assets
        select_cols = [
            "a.Z_PK",
            "a.ZFILENAME",
            "a.ZDATECREATED",
            "a.ZKIND",
            "a.ZFAVORITE",
            "a.ZLIBRARYSCOPE",
            "aa.ZORIGINALFILESIZE",
        ]
        if has_shared_id:
            select_cols.append("a.ZSHAREDLIBRARYSCOPEIDENTIFIER")
        if has_active:
            select_cols.append("a.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE")

        query = f"""
            SELECT {", ".join(select_cols)}
            FROM ZASSET a
            LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
            WHERE a.ZTRASHEDSTATE != 1
            ORDER BY a.ZDATECREATED DESC
        """
        cursor.execute(query)

        personal_count = 0
        personal_size = 0
        shared_count = 0
        shared_size = 0
        shared_photos = 0
        shared_videos = 0
        personal_photos = 0
        personal_videos = 0
        contributors: dict[str, dict] = {}
        shared_by_year: dict[str, dict] = {}
        shared_by_month: dict[str, int] = {}

        for row in cursor.fetchall():
            rd = dict(row)
            scope = _safe_col(rd, "ZLIBRARYSCOPE", 0) or 0
            size = rd.get("ZORIGINALFILESIZE") or 0
            kind = rd.get("ZKIND", 0) or 0
            is_shared = scope != 0

            created = coredata_to_datetime(rd["ZDATECREATED"])
            yr = str(created.year) if created else "Unknown"
            mo = created.strftime("%Y-%m") if created else "Unknown"

            if is_shared:
                shared_count += 1
                shared_size += size
                if kind == 0:
                    shared_photos += 1
                else:
                    shared_videos += 1

                shared_by_month[mo] = shared_by_month.get(mo, 0) + 1

                if yr not in shared_by_year:
                    shared_by_year[yr] = {"count": 0, "size": 0}
                shared_by_year[yr]["count"] += 1
                shared_by_year[yr]["size"] += size

                # Track contributors
                contrib_id = _safe_col(rd, "ZSHAREDLIBRARYSCOPEIDENTIFIER", "unknown") or "unknown"
                if contrib_id not in contributors:
                    contributors[contrib_id] = {"count": 0, "size": 0, "photos": 0, "videos": 0}
                contributors[contrib_id]["count"] += 1
                contributors[contrib_id]["size"] += size
                if kind == 0:
                    contributors[contrib_id]["photos"] += 1
                else:
                    contributors[contrib_id]["videos"] += 1
            else:
                personal_count += 1
                personal_size += size
                if kind == 0:
                    personal_photos += 1
                else:
                    personal_videos += 1

        total = personal_count + shared_count
        shared_enabled = shared_count > 0

        # Build contributor list
        contributor_list = [
            {
                "identifier": cid,
                "count": info["count"],
                "size": info["size"],
                "size_formatted": format_size(info["size"]),
                "photos": info["photos"],
                "videos": info["videos"],
                "pct": round(100 * info["count"] / max(1, shared_count), 1),
            }
            for cid, info in sorted(contributors.items(), key=lambda x: -x[1]["count"])
        ]

        # Monthly trend (last 12 months)
        monthly_sorted = sorted(shared_by_month.items(), reverse=True)[:12]

        return {
            "shared_library_enabled": shared_enabled,
            "contributors": contributor_list,
            "shared_by_year": [
                {
                    "year": yr,
                    "count": info["count"],
                    "size": info["size"],
                    "size_formatted": format_size(info["size"]),
                }
                for yr, info in sorted(shared_by_year.items(), reverse=True)
            ],
            "monthly_trend": [{"month": mo, "count": ct} for mo, ct in monthly_sorted],
            "summary": {
                "total_assets": total,
                "personal_count": personal_count,
                "personal_photos": personal_photos,
                "personal_videos": personal_videos,
                "personal_storage": personal_size,
                "personal_storage_formatted": format_size(personal_size),
                "shared_count": shared_count,
                "shared_photos": shared_photos,
                "shared_videos": shared_videos,
                "shared_pct": round(100 * shared_count / max(1, total), 1),
                "shared_storage": shared_size,
                "shared_storage_formatted": format_size(shared_size),
                "contributor_count": len(contributors),
            },
        }


def format_summary(data: dict[str, Any]) -> str:
    """Format human-readable summary."""
    lines = []
    s = data["summary"]

    if "error" in data:
        lines.append(f"⚠️  {data['error']}")
        return "\n".join(lines)

    lines.append("🤝 SHARED LIBRARY ANALYSIS")
    lines.append("=" * 50)

    if not data["shared_library_enabled"]:
        lines.append("Shared Library is not enabled or has no shared content.")
        lines.append(f"Total personal assets: {s['personal_count']:,}")
        return "\n".join(lines)

    lines.append(f"Total assets:         {s['total_assets']:,}")
    lines.append(
        f"Personal library:     {s['personal_count']:,} ({s['personal_photos']:,} photos, {s['personal_videos']:,} videos)"
    )
    lines.append(f"Personal storage:    {s['personal_storage_formatted']}")
    lines.append(f"Shared library:       {s['shared_count']:,} ({s['shared_pct']}%)")
    lines.append(f"  Photos:             {s['shared_photos']:,}")
    lines.append(f"  Videos:             {s['shared_videos']:,}")
    lines.append(f"Shared storage:      {s['shared_storage_formatted']}")

    if data["contributors"]:
        lines.append("")
        lines.append(f"Contributors ({s['contributor_count']}):")
        for c in data["contributors"][:10]:
            lines.append(
                f"  {c['identifier'][:16]:18s} {c['count']:>6,} items  {c['size_formatted']:>10}  ({c['pct']}%)"
            )

    if data["shared_by_year"]:
        lines.append("")
        lines.append("Shared items by year:")
        for yr in data["shared_by_year"][:10]:
            lines.append(f"  {yr['year']:<8} {yr['count']:>8,}  {yr['size_formatted']:>10}")

    return "\n".join(lines)


def main():
    return run_script(
        description="Analyze Shared Library in Apple Photos",
        analyze_fn=lambda db_path, _args: analyze_shared_library(db_path=db_path),
        format_fn=format_summary,
    )


if __name__ == "__main__":
    sys.exit(main())
