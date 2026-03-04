#!/usr/bin/env python3
"""
Scene / Content Search: query photos by ML-detected scene classifications.
Search by content type (beach, sunset, dog, food), generate content inventory.
"""

import sys
from collections import defaultdict
from typing import Any, Optional

from _common import PhotosDB, coredata_to_datetime, format_size, run_script, validate_year


def search_scenes(
    db_path: Optional[str] = None,
    search_term: Optional[str] = None,
    min_confidence: float = 0.0,
    top_n: int = 50,
    year: Optional[str] = None,
) -> dict[str, Any]:
    """
    Search photos by scene classification or generate content inventory.

    Args:
        db_path: Path to database
        search_term: Scene name to search for (None = show inventory)
        min_confidence: Minimum confidence score for scene matches
        top_n: Number of results to return for search
        year: Filter to specific year

    Returns:
        Scene search/inventory dictionary
    """
    with PhotosDB(db_path) as conn:
        cursor = conn.cursor()

        year_filter = ""
        year_params: list = []
        if year:
            year = validate_year(year)
            year_filter = "AND strftime('%Y', datetime(a.ZDATECREATED + 978307200, 'unixepoch')) = ?"
            year_params = [year]

        if search_term:
            return _search_by_scene(cursor, search_term, min_confidence, top_n, year_filter, year_params)
        else:
            return _generate_inventory(cursor, min_confidence, year_filter, year_params)


def _search_by_scene(
    cursor, search_term: str, min_confidence: float, top_n: int, year_filter: str, year_params: list
) -> dict[str, Any]:
    """Search photos matching a specific scene classification."""
    query = f"""
        SELECT
            a.Z_PK,
            a.ZFILENAME,
            a.ZDATECREATED,
            a.ZKIND,
            a.ZFAVORITE,
            a.ZLATITUDE,
            a.ZLONGITUDE,
            aa.ZORIGINALFILESIZE,
            sc.ZSCENENAME,
            sc.ZCONFIDENCE
        FROM ZASSET a
        JOIN ZSCENECLASSIFICATION sc ON a.Z_PK = sc.ZASSET
        LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
        WHERE a.ZTRASHEDSTATE != 1
        AND LOWER(sc.ZSCENENAME) LIKE ?
        AND (sc.ZCONFIDENCE >= ? OR sc.ZCONFIDENCE IS NULL)
        {year_filter}
        ORDER BY sc.ZCONFIDENCE DESC NULLS LAST, a.ZDATECREATED DESC
        LIMIT ?
    """

    search_pattern = f"%{search_term.lower()}%"
    cursor.execute(query, (search_pattern, min_confidence, *year_params, top_n))

    results = []
    total_size = 0
    for row in cursor.fetchall():
        created = coredata_to_datetime(row["ZDATECREATED"])
        size = row["ZORIGINALFILESIZE"] or 0
        total_size += size

        results.append(
            {
                "id": row["Z_PK"],
                "filename": row["ZFILENAME"],
                "created": created.isoformat() if created else None,
                "kind": "photo" if row["ZKIND"] == 0 else "video",
                "is_favorite": bool(row["ZFAVORITE"]),
                "size": size,
                "size_formatted": format_size(size),
                "scene": row["ZSCENENAME"],
                "confidence": round(row["ZCONFIDENCE"], 3) if row["ZCONFIDENCE"] else None,
                "latitude": row["ZLATITUDE"],
                "longitude": row["ZLONGITUDE"],
            }
        )

    # Get total count (not limited)
    count_query = f"""
        SELECT COUNT(*) as total
        FROM ZASSET a
        JOIN ZSCENECLASSIFICATION sc ON a.Z_PK = sc.ZASSET
        WHERE a.ZTRASHEDSTATE != 1
        AND LOWER(sc.ZSCENENAME) LIKE ?
        AND (sc.ZCONFIDENCE >= ? OR sc.ZCONFIDENCE IS NULL)
        {year_filter}
    """
    cursor.execute(count_query, (search_pattern, min_confidence, *year_params))
    total_matches = cursor.fetchone()["total"]

    # Related scenes (other scenes that appear on the same photos)
    if results:
        photo_ids = [r["id"] for r in results[:100]]
        placeholders = ",".join("?" * len(photo_ids))
        cursor.execute(
            f"""
            SELECT sc.ZSCENENAME, COUNT(DISTINCT sc.ZASSET) as count
            FROM ZSCENECLASSIFICATION sc
            WHERE sc.ZASSET IN ({placeholders})
            AND LOWER(sc.ZSCENENAME) NOT LIKE ?
            GROUP BY sc.ZSCENENAME
            ORDER BY count DESC
            LIMIT 10
        """,
            [*photo_ids, search_pattern],
        )
        related_scenes = [
            {"scene": row["ZSCENENAME"], "count": row["count"]} for row in cursor.fetchall() if row["ZSCENENAME"]
        ]
    else:
        related_scenes = []

    return {
        "mode": "search",
        "search_term": search_term,
        "results": results,
        "related_scenes": related_scenes,
        "summary": {
            "total_matches": total_matches,
            "shown": len(results),
            "total_size": total_size,
            "total_size_formatted": format_size(total_size),
            "min_confidence": min_confidence,
        },
    }


def _generate_inventory(cursor, min_confidence: float, year_filter: str, year_params: list) -> dict[str, Any]:
    """Generate a complete content inventory by scene type."""
    query = f"""
        SELECT
            sc.ZSCENENAME,
            COUNT(DISTINCT sc.ZASSET) as photo_count,
            AVG(sc.ZCONFIDENCE) as avg_confidence
        FROM ZSCENECLASSIFICATION sc
        JOIN ZASSET a ON sc.ZASSET = a.Z_PK
        WHERE a.ZTRASHEDSTATE != 1
        AND sc.ZSCENENAME IS NOT NULL
        AND (sc.ZCONFIDENCE >= ? OR sc.ZCONFIDENCE IS NULL)
        {year_filter}
        GROUP BY sc.ZSCENENAME
        ORDER BY photo_count DESC
    """
    cursor.execute(query, (min_confidence, *year_params))

    categories = defaultdict(list)
    all_scenes = []

    for row in cursor.fetchall():
        scene = row["ZSCENENAME"]
        count = row["photo_count"]
        avg_conf = row["avg_confidence"]

        scene_data = {
            "scene": scene,
            "photo_count": count,
            "avg_confidence": round(avg_conf, 3) if avg_conf else None,
        }
        all_scenes.append(scene_data)

        # Categorize scenes
        scene_lower = scene.lower() if scene else ""
        if any(w in scene_lower for w in ["dog", "cat", "bird", "fish", "animal", "pet", "horse"]):
            categories["animals"].append(scene_data)
        elif any(
            w in scene_lower
            for w in ["food", "meal", "dinner", "lunch", "breakfast", "dessert", "cake", "pizza", "coffee"]
        ):
            categories["food_drink"].append(scene_data)
        elif any(
            w in scene_lower
            for w in [
                "beach",
                "ocean",
                "mountain",
                "lake",
                "forest",
                "park",
                "garden",
                "sunset",
                "sunrise",
                "sky",
                "snow",
                "field",
                "river",
                "waterfall",
            ]
        ):
            categories["nature_outdoor"].append(scene_data)
        elif any(
            w in scene_lower
            for w in ["sport", "swim", "run", "ball", "game", "gym", "fitness", "soccer", "basketball", "baseball"]
        ):
            categories["sports"].append(scene_data)
        elif any(
            w in scene_lower
            for w in ["car", "road", "street", "building", "house", "city", "bridge", "train", "airplane", "boat"]
        ):
            categories["urban_travel"].append(scene_data)
        elif any(
            w in scene_lower
            for w in ["face", "selfie", "portrait", "people", "group", "family", "baby", "child", "wedding"]
        ):
            categories["people"].append(scene_data)
        else:
            categories["other"].append(scene_data)

    # Summary stats
    total_tagged = sum(s["photo_count"] for s in all_scenes)

    cursor.execute("""
        SELECT COUNT(*) as total FROM ZASSET WHERE ZTRASHEDSTATE != 1
    """)
    total_all = cursor.fetchone()["total"]

    return {
        "mode": "inventory",
        "scenes": all_scenes,
        "categories": {k: v for k, v in sorted(categories.items())},
        "summary": {
            "total_scenes": len(all_scenes),
            "total_tagged_photos": total_tagged,
            "total_photos": total_all,
            "coverage": round(total_tagged / total_all * 100, 1) if total_all else 0,
            "min_confidence": min_confidence,
        },
    }


def format_summary(data: dict[str, Any]) -> str:
    """Format scene search/inventory as human-readable summary."""
    lines = []
    lines.append("🏷️  SCENE / CONTENT SEARCH")
    lines.append("=" * 50)
    lines.append("")

    if data["mode"] == "search":
        summary = data["summary"]
        lines.append(f'Search: "{data["search_term"]}"')
        lines.append(f"Matches: {summary['total_matches']:,} (showing {summary['shown']})")
        lines.append(f"Total size: {summary['total_size_formatted']}")
        lines.append("")

        lines.append("Results:")
        for r in data["results"][:20]:
            fav = " ★" if r["is_favorite"] else ""
            conf = f" ({r['confidence']:.2f})" if r["confidence"] else ""
            lines.append(f"  {r['filename']} | {r['scene']}{conf}{fav}")

        if data["related_scenes"]:
            lines.append("")
            lines.append("Related scenes:")
            for rs in data["related_scenes"]:
                lines.append(f"  {rs['scene']}: {rs['count']} photos")

    else:  # inventory
        summary = data["summary"]
        lines.append(f"Unique scene labels: {summary['total_scenes']:,}")
        lines.append(f"Scene-tagged entries: {summary['total_tagged_photos']:,}")
        lines.append(f"Library total: {summary['total_photos']:,}")
        lines.append("")

        if data["categories"]:
            lines.append("By Category:")
            for cat_name, scenes in sorted(data["categories"].items()):
                cat_total = sum(s["photo_count"] for s in scenes)
                lines.append(f"\n  📂 {cat_name.replace('_', ' ').title()} ({cat_total:,} photos)")
                for scene in scenes[:8]:
                    lines.append(f"    {scene['scene']}: {scene['photo_count']:,}")
                if len(scenes) > 8:
                    lines.append(f"    ... and {len(scenes) - 8} more")

        lines.append("")
        lines.append("Top 20 Scene Labels:")
        for scene in data["scenes"][:20]:
            lines.append(f"  {scene['scene']}: {scene['photo_count']:,}")

    lines.append("")
    return "\n".join(lines)


def main():
    def add_args(parser):
        parser.add_argument("--search", help="Scene name to search for")
        parser.add_argument("--min-confidence", type=float, default=0.0, help="Minimum confidence score (default: 0.0)")
        parser.add_argument("--top", type=int, default=50, help="Number of search results (default: 50)")
        parser.add_argument("--year", help="Filter to specific year (YYYY)")

    def invoke(db_path, args):
        return search_scenes(
            db_path=db_path,
            search_term=args.search,
            min_confidence=args.min_confidence,
            top_n=args.top,
            year=args.year,
        )

    return run_script(
        description="Search photos by scene/content or generate content inventory",
        analyze_fn=invoke,
        format_fn=format_summary,
        extra_args_fn=add_args,
        epilog="""
Examples:
  # Content inventory
  %(prog)s --human

  # Search for beach photos
  %(prog)s --search beach --human

  # Search for dogs with high confidence
  %(prog)s --search dog --min-confidence 0.5 --human

  # Content inventory for 2025
  %(prog)s --year 2025 --human
        """,
    )


if __name__ == "__main__":
    sys.exit(main())
