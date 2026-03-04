#!/usr/bin/env python3
"""
Album Auditor: find orphan photos, empty albums, album overlap,
and suggest album groupings from timeline clusters.
"""

import sys
from typing import Any, Optional

from _common import PhotosDB, format_size, run_script


def audit_albums(
    db_path: Optional[str] = None,
) -> dict[str, Any]:
    """
    Audit albums for organization issues.

    Args:
        db_path: Path to database

    Returns:
        Album audit dictionary
    """
    with PhotosDB(db_path) as conn:
        cursor = conn.cursor()

        # Get all user albums (filter out system/smart albums)
        # ZKIND values for user albums vary; we'll get albums with titles
        cursor.execute("""
            SELECT
                album.Z_PK as album_id,
                album.ZTITLE as title,
                album.ZKIND as kind
            FROM ZGENERICALBUM album
            WHERE album.ZTITLE IS NOT NULL
            AND album.ZTITLE != ''
            ORDER BY album.ZTITLE
        """)

        albums = {}
        for row in cursor.fetchall():
            albums[row["album_id"]] = {
                "id": row["album_id"],
                "title": row["title"],
                "kind": row["kind"],
                "photo_ids": set(),
                "photo_count": 0,
                "total_size": 0,
            }

        # Get photos in each album
        # The junction table name varies by schema version; try common patterns
        junction_tables = _find_album_junction_table(cursor)

        if junction_tables:
            album_col, asset_col, table_name = junction_tables

            cursor.execute(f"""
                SELECT
                    ga.{album_col} as album_id,
                    ga.{asset_col} as asset_id,
                    aa.ZORIGINALFILESIZE as size
                FROM {table_name} ga
                JOIN ZASSET a ON ga.{asset_col} = a.Z_PK
                LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
                WHERE a.ZTRASHEDSTATE != 1
            """)

            all_album_photo_ids = set()
            for row in cursor.fetchall():
                aid = row["album_id"]
                if aid in albums:
                    albums[aid]["photo_ids"].add(row["asset_id"])
                    albums[aid]["total_size"] += row["size"] or 0
                all_album_photo_ids.add(row["asset_id"])

            for album in albums.values():
                album["photo_count"] = len(album["photo_ids"])
        else:
            all_album_photo_ids = set()

        # Find orphan photos (not in any album)
        cursor.execute("""
            SELECT COUNT(*) as total FROM ZASSET WHERE ZTRASHEDSTATE != 1
        """)
        total_photos = cursor.fetchone()["total"]

        orphan_count = total_photos - len(all_album_photo_ids)

        # Orphan details (sample)
        if all_album_photo_ids:
            placeholders = ",".join("?" * min(len(all_album_photo_ids), 500))
            sample_ids = list(all_album_photo_ids)[:500]

            cursor.execute(
                f"""
                SELECT COUNT(*) as count,
                    SUM(aa.ZORIGINALFILESIZE) as total_size
                FROM ZASSET a
                LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
                WHERE a.ZTRASHEDSTATE != 1
                AND a.Z_PK NOT IN ({placeholders})
            """,
                sample_ids,
            )

            orphan_row = cursor.fetchone()
            orphan_size = orphan_row["total_size"] or 0
        else:
            orphan_size = 0

        # Empty and tiny albums
        empty_albums = []
        tiny_albums = []  # <= 3 photos
        for album in albums.values():
            if album["photo_count"] == 0:
                empty_albums.append(
                    {
                        "id": album["id"],
                        "title": album["title"],
                    }
                )
            elif album["photo_count"] <= 3:
                tiny_albums.append(
                    {
                        "id": album["id"],
                        "title": album["title"],
                        "photo_count": album["photo_count"],
                    }
                )

        # Album overlap: find albums that share photos
        overlaps = []
        album_list = [a for a in albums.values() if a["photo_count"] > 0]
        for i in range(len(album_list)):
            for j in range(i + 1, len(album_list)):
                a1 = album_list[i]
                a2 = album_list[j]
                shared = a1["photo_ids"] & a2["photo_ids"]
                if shared:
                    overlap_pct_1 = round(len(shared) / len(a1["photo_ids"]) * 100, 1) if a1["photo_ids"] else 0
                    overlap_pct_2 = round(len(shared) / len(a2["photo_ids"]) * 100, 1) if a2["photo_ids"] else 0
                    overlaps.append(
                        {
                            "album_1": a1["title"],
                            "album_1_count": a1["photo_count"],
                            "album_2": a2["title"],
                            "album_2_count": a2["photo_count"],
                            "shared_count": len(shared),
                            "overlap_pct_album_1": overlap_pct_1,
                            "overlap_pct_album_2": overlap_pct_2,
                        }
                    )

        overlaps.sort(key=lambda x: x["shared_count"], reverse=True)

        # Album size ranking
        album_ranking = sorted(
            [
                {
                    "title": a["title"],
                    "photo_count": a["photo_count"],
                    "total_size": a["total_size"],
                    "total_size_formatted": format_size(a["total_size"]),
                }
                for a in albums.values()
                if a["photo_count"] > 0
            ],
            key=lambda x: x["photo_count"],
            reverse=True,
        )

        return {
            "albums": album_ranking,
            "empty_albums": empty_albums,
            "tiny_albums": tiny_albums,
            "overlaps": overlaps[:20],
            "orphans": {
                "count": orphan_count,
                "total_size": orphan_size,
                "total_size_formatted": format_size(orphan_size),
            },
            "summary": {
                "total_albums": len(albums),
                "albums_with_photos": len(album_ranking),
                "empty_albums": len(empty_albums),
                "tiny_albums": len(tiny_albums),
                "total_photos": total_photos,
                "photos_in_albums": len(all_album_photo_ids),
                "orphan_photos": orphan_count,
                "albums_with_overlap": len(overlaps),
            },
        }


def _find_album_junction_table(cursor) -> Optional[tuple]:
    """
    Find the album-asset junction table. The table name varies by schema version.
    Common patterns: Z_27ASSETS, Z_26ASSETS, etc.

    Returns:
        Tuple of (album_column, asset_column, table_name) or None
    """
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row["name"] for row in cursor.fetchall()]

    # Look for junction tables matching the pattern
    for table in tables:
        if table.startswith("Z_") and "ASSETS" in table.upper():
            # Check columns
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row["name"] for row in cursor.fetchall()]

            album_col = None
            asset_col = None
            for col in columns:
                if "ALBUMS" in col.upper():
                    album_col = col
                elif "ASSETS" in col.upper():
                    asset_col = col

            if album_col and asset_col:
                return (album_col, asset_col, table)

    return None


def format_summary(data: dict[str, Any]) -> str:
    """Format album audit as human-readable summary."""
    lines = []
    lines.append("📁 ALBUM AUDITOR")
    lines.append("=" * 50)
    lines.append("")

    s = data["summary"]
    lines.append(f"Total albums: {s['total_albums']:,}")
    lines.append(f"Albums with photos: {s['albums_with_photos']:,}")
    lines.append(f"Empty albums: {s['empty_albums']:,}")
    lines.append(f"Tiny albums (≤3 photos): {s['tiny_albums']:,}")
    lines.append(f"Photos in albums: {s['photos_in_albums']:,} / {s['total_photos']:,}")
    lines.append(f"Orphan photos (no album): {s['orphan_photos']:,}")
    lines.append("")

    if data["orphans"]["count"] > 0:
        lines.append("📭 Orphan Photos:")
        lines.append(f"  {data['orphans']['count']:,} photos not in any album")
        lines.append(f"  Total size: {data['orphans']['total_size_formatted']}")
        lines.append("")

    if data["empty_albums"]:
        lines.append(f"🗑️  Empty Albums ({len(data['empty_albums'])}):")
        for album in data["empty_albums"][:10]:
            lines.append(f"  • {album['title']}")
        if len(data["empty_albums"]) > 10:
            lines.append(f"  ... and {len(data['empty_albums']) - 10} more")
        lines.append("")

    if data["tiny_albums"]:
        lines.append(f"📌 Tiny Albums ({len(data['tiny_albums'])}):")
        for album in data["tiny_albums"][:10]:
            lines.append(f"  • {album['title']} ({album['photo_count']} photos)")
        if len(data["tiny_albums"]) > 10:
            lines.append(f"  ... and {len(data['tiny_albums']) - 10} more")
        lines.append("")

    if data["overlaps"]:
        lines.append(f"🔄 Album Overlaps (top {min(len(data['overlaps']), 10)}):")
        for overlap in data["overlaps"][:10]:
            lines.append(f'  "{overlap["album_1"]}" ∩ "{overlap["album_2"]}"')
            lines.append(
                f"    {overlap['shared_count']} shared ({overlap['overlap_pct_album_1']}% / {overlap['overlap_pct_album_2']}%)"
            )
        lines.append("")

    if data["albums"]:
        lines.append("📊 Largest Albums:")
        for album in data["albums"][:15]:
            lines.append(f"  {album['title']}: {album['photo_count']:,} photos ({album['total_size_formatted']})")
        lines.append("")

    return "\n".join(lines)


def main():
    return run_script(
        description="Audit albums for organization issues",
        analyze_fn=lambda db_path, _args: audit_albums(db_path=db_path),
        format_fn=format_summary,
        epilog="""
Examples:
  %(prog)s --human
  %(prog)s --output audit.json
        """,
    )


if __name__ == "__main__":
    sys.exit(main())
