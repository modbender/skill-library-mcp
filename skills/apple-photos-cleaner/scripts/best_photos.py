#!/usr/bin/env python3
"""
Find best photos and hidden gems: high-quality photos that aren't favorited.
Surface overlooked great shots using Apple's computed quality scores.
"""

import sys
from typing import Any, Optional

from _common import (
    PhotosDB,
    build_asset_query,
    coredata_to_datetime,
    format_size,
    get_quality_score,
    run_script,
    validate_year,
)


def find_best_photos(
    db_path: Optional[str] = None,
    min_quality: float = 0.7,
    top_n: int = 50,
    hidden_gems_only: bool = False,
    year: Optional[str] = None,
) -> dict[str, Any]:
    """
    Find best quality photos, optionally filtering to hidden gems (not favorited).

    Args:
        db_path: Path to database
        min_quality: Minimum combined quality score (0.0-1.0)
        top_n: Number of top photos to return
        hidden_gems_only: Only show photos that aren't favorited
        year: Filter to a specific year (YYYY)

    Returns:
        Dictionary with best photos and stats
    """
    with PhotosDB(db_path) as conn:
        cursor = conn.cursor()

        where_clauses = [
            "a.ZTRASHEDSTATE != 1",
            "a.ZKIND = 0",  # photos only
            "a.ZISDETECTEDSCREENSHOT != 1",
        ]

        if hidden_gems_only:
            where_clauses.append("a.ZFAVORITE != 1")

        params: list = []
        if year:
            year = validate_year(year)
            where_clauses.append("strftime('%Y', datetime(a.ZDATECREATED + 978307200, 'unixepoch')) = ?")
            params.append(year)

        query = build_asset_query(
            where_clauses=where_clauses,
            join_additional=True,
            join_computed=True,
        )
        cursor.execute(query, params)

        scored_photos = []
        total_with_scores = 0
        total_favorites = 0
        quality_histogram = {
            "excellent": 0,  # >= 0.85
            "good": 0,  # >= 0.7
            "average": 0,  # >= 0.5
            "below_average": 0,  # >= 0.3
            "poor": 0,  # < 0.3
        }

        for row in cursor.fetchall():
            quality = get_quality_score(row)
            if quality is None:
                continue

            total_with_scores += 1
            is_fav = bool(row["ZFAVORITE"])
            if is_fav:
                total_favorites += 1

            # Update histogram
            if quality >= 0.85:
                quality_histogram["excellent"] += 1
            elif quality >= 0.7:
                quality_histogram["good"] += 1
            elif quality >= 0.5:
                quality_histogram["average"] += 1
            elif quality >= 0.3:
                quality_histogram["below_average"] += 1
            else:
                quality_histogram["poor"] += 1

            if quality >= min_quality:
                created = coredata_to_datetime(row["ZDATECREATED"])
                size = row["ZORIGINALFILESIZE"] or 0

                # Compute detailed score breakdown
                row_dict = dict(row)
                detail_scores = {}
                for key, label in [
                    ("ZPLEASANTCOMPOSITIONSCORE", "composition"),
                    ("ZPLEASANTLIGHTINGSCORE", "lighting"),
                    ("ZPLEASANTPATTERNSCORE", "patterns"),
                    ("ZPLEASANTPERSPECTIVESCORE", "perspective"),
                    ("ZPLEASANTPOSTPROCESSINGSCORE", "post_processing"),
                    ("ZPLEASANTREFLECTIONSSCORE", "reflections"),
                    ("ZPLEASANTSYMMETRYSCORE", "symmetry"),
                    ("ZFAILURESCORE", "failure"),
                    ("ZNOISESCORE", "noise"),
                ]:
                    val = row_dict.get(key)
                    if val is not None:
                        detail_scores[label] = round(val, 3)

                scored_photos.append(
                    {
                        "id": row["Z_PK"],
                        "filename": row["ZFILENAME"],
                        "created": created.isoformat() if created else None,
                        "size": size,
                        "size_formatted": format_size(size),
                        "quality_score": round(quality, 3),
                        "is_favorite": is_fav,
                        "dimensions": f"{row_dict.get('ZORIGINALWIDTH') or row['ZWIDTH']}x{row_dict.get('ZORIGINALHEIGHT') or row['ZHEIGHT']}",
                        "detail_scores": detail_scores,
                    }
                )

        # Sort by quality score descending, take top N
        scored_photos.sort(key=lambda x: x["quality_score"], reverse=True)
        top_photos = scored_photos[:top_n]

        # Hidden gems stats
        hidden_gems_count = sum(1 for p in scored_photos if not p["is_favorite"])
        favorited_high_quality = sum(1 for p in scored_photos if p["is_favorite"])

        return {
            "top_photos": top_photos,
            "summary": {
                "total_with_scores": total_with_scores,
                "total_above_threshold": len(scored_photos),
                "hidden_gems": hidden_gems_count,
                "favorited_high_quality": favorited_high_quality,
                "total_favorites": total_favorites,
                "min_quality_threshold": min_quality,
                "top_n": top_n,
            },
            "quality_distribution": quality_histogram,
        }


def format_summary(data: dict[str, Any]) -> str:
    """Format best photos findings as human-readable summary."""
    lines = []
    lines.append("⭐ BEST PHOTOS / HIDDEN GEMS")
    lines.append("=" * 50)
    lines.append("")

    summary = data["summary"]
    lines.append(f"Photos with quality scores: {summary['total_with_scores']:,}")
    lines.append(f"Above threshold ({summary['min_quality_threshold']}): {summary['total_above_threshold']:,}")
    lines.append(f"Hidden gems (great but not favorited): {summary['hidden_gems']:,}")
    lines.append(f"Already favorited high-quality: {summary['favorited_high_quality']:,}")
    lines.append("")

    dist = data["quality_distribution"]
    lines.append("Quality Distribution:")
    lines.append(f"  🌟 Excellent (≥0.85): {dist['excellent']:,}")
    lines.append(f"  ✅ Good (≥0.70):      {dist['good']:,}")
    lines.append(f"  📊 Average (≥0.50):   {dist['average']:,}")
    lines.append(f"  📉 Below avg (≥0.30): {dist['below_average']:,}")
    lines.append(f"  ❌ Poor (<0.30):       {dist['poor']:,}")
    lines.append("")

    top = data["top_photos"]
    if top:
        lines.append(f"Top {len(top)} Photos:")
        for i, photo in enumerate(top[:20], 1):
            fav = " ★" if photo["is_favorite"] else " 💎"
            lines.append(f"  {i:>3}. {photo['filename']}")
            lines.append(
                f"       Q:{photo['quality_score']:.3f} | {photo['size_formatted']} | {photo['dimensions']}{fav}"
            )

            # Show top scores
            scores = photo["detail_scores"]
            highlights = []
            for key in ["composition", "lighting", "symmetry", "patterns"]:
                if key in scores and scores[key] >= 0.7:
                    highlights.append(f"{key}:{scores[key]:.2f}")
            if highlights:
                lines.append(f"       📐 {', '.join(highlights)}")
    lines.append("")

    return "\n".join(lines)


def main():
    def add_args(parser):
        parser.add_argument(
            "--min-quality", type=float, default=0.7, help="Minimum quality score threshold (default: 0.7)"
        )
        parser.add_argument("--top", type=int, default=50, help="Number of top photos to return (default: 50)")
        parser.add_argument("--hidden-gems", action="store_true", help="Only show photos that are NOT favorited")
        parser.add_argument("--year", help="Filter to specific year (YYYY)")

    def invoke(db_path, args):
        return find_best_photos(
            db_path=db_path,
            min_quality=args.min_quality,
            top_n=args.top,
            hidden_gems_only=args.hidden_gems,
            year=args.year,
        )

    return run_script(
        description="Find best photos and hidden gems in Apple Photos",
        analyze_fn=invoke,
        format_fn=format_summary,
        extra_args_fn=add_args,
        epilog="""
Examples:
  %(prog)s --human
  %(prog)s --hidden-gems --top 100
  %(prog)s --min-quality 0.8 --year 2025
  %(prog)s --output best.json
        """,
    )


if __name__ == "__main__":
    sys.exit(main())
