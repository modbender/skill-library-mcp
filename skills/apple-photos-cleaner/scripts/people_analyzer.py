#!/usr/bin/env python3
"""
People Analyzer: deep analysis of people in your photo library.
Co-occurrence, trends over time, best photos per person, and more.
"""

import sys
from collections import defaultdict
from typing import Any, Optional

from _common import PhotosDB, coredata_to_datetime, get_quality_score, run_script


def analyze_people(
    db_path: Optional[str] = None,
    min_photos: int = 5,
    top_n: int = 20,
) -> dict[str, Any]:
    """
    Analyze people detected in photos.

    Args:
        db_path: Path to database
        min_photos: Minimum photos to include a person
        top_n: Number of top people to return in detail

    Returns:
        People analysis dictionary
    """
    with PhotosDB(db_path) as conn:
        cursor = conn.cursor()

        # Get all named people with face counts
        cursor.execute(
            """
            SELECT
                p.Z_PK as person_id,
                p.ZFULLNAME as name,
                p.ZFACECOUNT as face_count,
                COUNT(DISTINCT df.ZASSET) as photo_count
            FROM ZPERSON p
            JOIN ZDETECTEDFACE df ON p.Z_PK = df.ZPERSON
            JOIN ZASSET a ON df.ZASSET = a.Z_PK
            WHERE p.ZFULLNAME IS NOT NULL
            AND p.ZFULLNAME != ''
            AND a.ZTRASHEDSTATE != 1
            GROUP BY p.Z_PK
            HAVING photo_count >= ?
            ORDER BY photo_count DESC
        """,
            (min_photos,),
        )

        people = []
        for row in cursor.fetchall():
            people.append(
                {
                    "person_id": row["person_id"],
                    "name": row["name"],
                    "face_count": row["face_count"] or 0,
                    "photo_count": row["photo_count"],
                }
            )

        # Get unnamed face count
        cursor.execute("""
            SELECT COUNT(DISTINCT df.ZASSET) as count
            FROM ZDETECTEDFACE df
            JOIN ZASSET a ON df.ZASSET = a.Z_PK
            WHERE (df.ZPERSON IS NULL OR df.ZPERSON NOT IN (
                SELECT Z_PK FROM ZPERSON WHERE ZFULLNAME IS NOT NULL AND ZFULLNAME != ''
            ))
            AND a.ZTRASHEDSTATE != 1
        """)
        unnamed_count = cursor.fetchone()["count"]

        # Detailed analysis for top people
        detailed_people = []
        for person in people[:top_n]:
            pid = person["person_id"]

            # Photos by year
            cursor.execute(
                """
                SELECT
                    strftime('%Y', datetime(a.ZDATECREATED + 978307200, 'unixepoch')) as year,
                    COUNT(*) as count
                FROM ZASSET a
                JOIN ZDETECTEDFACE df ON a.Z_PK = df.ZASSET
                WHERE df.ZPERSON = ?
                AND a.ZTRASHEDSTATE != 1
                GROUP BY year
                ORDER BY year
            """,
                (pid,),
            )
            by_year = {row["year"]: row["count"] for row in cursor.fetchall()}

            # Best photo (highest quality score)
            cursor.execute(
                """
                SELECT
                    a.Z_PK,
                    a.ZFILENAME,
                    a.ZDATECREATED,
                    a.ZFAVORITE,
                    ca.ZFAILURESCORE,
                    ca.ZNOISESCORE,
                    ca.ZPLEASANTCOMPOSITIONSCORE,
                    ca.ZPLEASANTLIGHTINGSCORE
                FROM ZASSET a
                JOIN ZDETECTEDFACE df ON a.Z_PK = df.ZASSET
                LEFT JOIN ZCOMPUTEDASSETATTRIBUTES ca ON a.Z_PK = ca.ZASSET
                WHERE df.ZPERSON = ?
                AND a.ZTRASHEDSTATE != 1
                AND a.ZKIND = 0
                ORDER BY ca.ZPLEASANTCOMPOSITIONSCORE DESC NULLS LAST
                LIMIT 5
            """,
                (pid,),
            )

            best_photos = []
            for row in cursor.fetchall():
                quality = get_quality_score(row)
                created = coredata_to_datetime(row["ZDATECREATED"])
                best_photos.append(
                    {
                        "id": row["Z_PK"],
                        "filename": row["ZFILENAME"],
                        "created": created.isoformat() if created else None,
                        "quality_score": round(quality, 3) if quality else None,
                        "is_favorite": bool(row["ZFAVORITE"]),
                    }
                )

            # Favorites count
            cursor.execute(
                """
                SELECT COUNT(*) as count
                FROM ZASSET a
                JOIN ZDETECTEDFACE df ON a.Z_PK = df.ZASSET
                WHERE df.ZPERSON = ?
                AND a.ZTRASHEDSTATE != 1
                AND a.ZFAVORITE = 1
            """,
                (pid,),
            )
            favorites = cursor.fetchone()["count"]

            # Date range
            cursor.execute(
                """
                SELECT
                    MIN(a.ZDATECREATED) as first,
                    MAX(a.ZDATECREATED) as last
                FROM ZASSET a
                JOIN ZDETECTEDFACE df ON a.Z_PK = df.ZASSET
                WHERE df.ZPERSON = ?
                AND a.ZTRASHEDSTATE != 1
            """,
                (pid,),
            )
            dates_row = cursor.fetchone()
            first_date = coredata_to_datetime(dates_row["first"])
            last_date = coredata_to_datetime(dates_row["last"])

            detailed_people.append(
                {
                    **person,
                    "favorites": favorites,
                    "first_photo": first_date.isoformat() if first_date else None,
                    "last_photo": last_date.isoformat() if last_date else None,
                    "by_year": by_year,
                    "best_photos": best_photos,
                }
            )

        # Co-occurrence analysis: who appears together
        co_occurrences = defaultdict(int)
        if people:
            person_ids = [p["person_id"] for p in people[:top_n]]
            placeholders = ",".join("?" * len(person_ids))

            # Find photos with multiple named people
            cursor.execute(
                f"""
                SELECT df.ZASSET, df.ZPERSON
                FROM ZDETECTEDFACE df
                JOIN ZASSET a ON df.ZASSET = a.Z_PK
                WHERE df.ZPERSON IN ({placeholders})
                AND a.ZTRASHEDSTATE != 1
                ORDER BY df.ZASSET
            """,
                person_ids,
            )

            # Group by photo
            photo_people = defaultdict(set)
            for row in cursor.fetchall():
                photo_people[row["ZASSET"]].add(row["ZPERSON"])

            # Count co-occurrences
            for _asset_id, person_set in photo_people.items():
                if len(person_set) >= 2:
                    person_list = sorted(person_set)
                    for i in range(len(person_list)):
                        for j in range(i + 1, len(person_list)):
                            co_occurrences[(person_list[i], person_list[j])] += 1

        # Map person IDs to names
        id_to_name = {p["person_id"]: p["name"] for p in people}
        co_occurrence_list = []
        for (pid1, pid2), count in sorted(co_occurrences.items(), key=lambda x: -x[1]):
            name1 = id_to_name.get(pid1, f"Unknown_{pid1}")
            name2 = id_to_name.get(pid2, f"Unknown_{pid2}")
            co_occurrence_list.append(
                {
                    "person_1": name1,
                    "person_2": name2,
                    "shared_photos": count,
                }
            )

        return {
            "people": detailed_people,
            "co_occurrences": co_occurrence_list[:30],
            "summary": {
                "total_named_people": len(people),
                "total_people_above_threshold": len(people),
                "unnamed_face_photos": unnamed_count,
                "min_photos_threshold": min_photos,
            },
        }


def format_summary(data: dict[str, Any]) -> str:
    """Format people analysis as human-readable summary."""
    lines = []
    lines.append("👥 PEOPLE ANALYZER")
    lines.append("=" * 50)
    lines.append("")

    summary = data["summary"]
    lines.append(f"Named people (≥{summary['min_photos_threshold']} photos): {summary['total_named_people']:,}")
    lines.append(f"Photos with unnamed faces: {summary['unnamed_face_photos']:,}")
    lines.append("")

    lines.append("Top People:")
    for person in data["people"][:15]:
        fav_str = f" (★ {person['favorites']})" if person.get("favorites") else ""
        lines.append(f"  {person['name']}: {person['photo_count']:,} photos{fav_str}")

        if person.get("by_year"):
            years = person["by_year"]
            year_strs = [f"{y}:{c}" for y, c in sorted(years.items())[-5:]]
            lines.append(f"    📅 {', '.join(year_strs)}")

    lines.append("")

    if data["co_occurrences"]:
        lines.append("Frequently Photographed Together:")
        for pair in data["co_occurrences"][:10]:
            lines.append(f"  {pair['person_1']} + {pair['person_2']}: {pair['shared_photos']:,} photos")
        lines.append("")

    return "\n".join(lines)


def main():
    def add_args(parser):
        parser.add_argument("--min-photos", type=int, default=5, help="Minimum photos to include a person (default: 5)")
        parser.add_argument(
            "--top", type=int, default=20, help="Number of top people to analyze in detail (default: 20)"
        )

    def invoke(db_path, args):
        return analyze_people(
            db_path=db_path,
            min_photos=args.min_photos,
            top_n=args.top,
        )

    return run_script(
        description="Analyze people in Apple Photos library",
        analyze_fn=invoke,
        format_fn=format_summary,
        extra_args_fn=add_args,
        epilog="""
Examples:
  %(prog)s --human
  %(prog)s --min-photos 10 --top 30
  %(prog)s --output people.json
        """,
    )


if __name__ == "__main__":
    sys.exit(main())
