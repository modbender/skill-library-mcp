#!/usr/bin/env python3
"""
Photo Similarity Detection: find visually similar photos beyond exact duplicates.

Uses computed asset attributes (scene classification, quality scores, composition,
lighting, color, etc.) as feature vectors. Compares photos using cosine similarity
to surface groups of near-identical or thematically similar images.
"""

import math
import sys
from typing import Any, Optional

from _common import (
    PhotosDB,
    _safe_float,
    coredata_to_datetime,
    format_size,
    run_script,
    validate_year,
)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _extract_features(row: dict) -> list[float]:
    """
    Extract a feature vector from computed asset attributes.

    Uses quality-related scores and scene classification data that
    Apple Photos computes for every image.
    """
    feature_keys = [
        "ZPLEASANTCOMPOSITIONSCORE",
        "ZPLEASANTLIGHTINGSCORE",
        "ZPLEASANTPATTERNSCORE",
        "ZFAILURESCORE",
        "ZNOISESCORE",
        "ZPLEASANTSYMMETRYSCORE",
        "ZPLEASANTCOLORHUESCORE",
        "ZPLEASANTWALLPAPERSCORE",
        "ZHARMONIOUSCOLORSCORE",
        "ZIMMERSIVENESSSCORE",
        "ZINTERACTIONSCORE",
        "ZPLEASANTPERSPECTIVESCORE",
        "ZPLEASANTSHARPSCORE",
        "ZPLEASANTPOSTPROCESSINGSCORE",
        "ZTASTEFULLYBLURREDSCORE",
        "ZWELLFRAMEDSUBJECTSCORE",
        "ZWELLTIMEDSHOTSCORE",
    ]
    return [_safe_float(row.get(key)) for key in feature_keys]


def find_similar_photos(
    db_path: Optional[str] = None,
    threshold: float = 0.95,
    year: Optional[str] = None,
    limit: int = 500,
) -> dict[str, Any]:
    """
    Find groups of similar photos based on computed visual attributes.

    Args:
        db_path: Path to database
        threshold: Cosine similarity threshold (0-1, higher = more similar)
        year: Filter to specific year
        limit: Max photos to compare (controls runtime)

    Returns:
        Similar photo groups and summary statistics
    """
    with PhotosDB(db_path) as conn:
        cursor = conn.cursor()

        # Check available columns
        cursor.execute("PRAGMA table_info(ZCOMPUTEDASSETATTRIBUTES)")
        ca_columns = {row["name"] for row in cursor.fetchall()}
        has_composition = "ZPLEASANTCOMPOSITIONSCORE" in ca_columns

        if not has_composition:
            return {
                "error": "Computed asset attributes not available in this database version.",
                "groups": [],
                "summary": {"total_compared": 0, "groups_found": 0},
            }

        where = ["a.ZTRASHEDSTATE != 1", "a.ZKIND = 0"]  # Photos only
        params: list = []
        if year:
            year = validate_year(year)
            where.append("strftime('%Y', datetime(a.ZDATECREATED + 978307200, 'unixepoch')) = ?")
            params.append(year)

        # Get photos with computed attributes
        query = f"""
            SELECT
                a.Z_PK, a.ZFILENAME, a.ZDATECREATED, a.ZFAVORITE,
                a.ZLATITUDE, a.ZLONGITUDE, a.ZWIDTH, a.ZHEIGHT,
                aa.ZORIGINALFILESIZE,
                ca.*
            FROM ZASSET a
            LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
            JOIN ZCOMPUTEDASSETATTRIBUTES ca ON a.Z_PK = ca.ZASSET
            WHERE {" AND ".join(where)}
            ORDER BY a.ZDATECREATED DESC
            LIMIT ?
        """
        params.append(limit)
        cursor.execute(query, params)

        photos = []
        for row in cursor.fetchall():
            rd = dict(row)
            features = _extract_features(rd)
            # Skip photos with all-zero features (no computed data)
            if all(f == 0.0 for f in features):
                continue

            created = coredata_to_datetime(rd["ZDATECREATED"])
            photos.append(
                {
                    "id": rd["Z_PK"],
                    "filename": rd["ZFILENAME"],
                    "created": created.isoformat() if created else None,
                    "is_favorite": bool(rd.get("ZFAVORITE")),
                    "size": rd.get("ZORIGINALFILESIZE") or 0,
                    "size_formatted": format_size(rd.get("ZORIGINALFILESIZE") or 0),
                    "dimensions": f"{rd.get('ZWIDTH', 0)}x{rd.get('ZHEIGHT', 0)}",
                    "features": features,
                }
            )

        # Find similar pairs using cosine similarity
        groups: dict[int, list[dict]] = {}
        assigned: set[int] = set()

        for i in range(len(photos)):
            if i in assigned:
                continue
            group = [i]
            for j in range(i + 1, len(photos)):
                if j in assigned:
                    continue
                sim = _cosine_similarity(photos[i]["features"], photos[j]["features"])
                if sim >= threshold:
                    group.append(j)
                    assigned.add(j)

            if len(group) > 1:
                assigned.add(i)
                groups[i] = group

        # Format groups
        similar_groups = []
        for _anchor_idx, member_indices in groups.items():
            members = []
            for idx in member_indices:
                p = photos[idx]
                members.append(
                    {
                        "id": p["id"],
                        "filename": p["filename"],
                        "created": p["created"],
                        "is_favorite": p["is_favorite"],
                        "size": p["size"],
                        "size_formatted": p["size_formatted"],
                        "dimensions": p["dimensions"],
                    }
                )
            # Sort members by size desc
            members.sort(key=lambda x: x["size"], reverse=True)

            # The largest file is the "keep" candidate, rest are savings
            keep = members[0]
            others_size = sum(m["size"] for m in members[1:])

            similar_groups.append(
                {
                    "member_count": len(members),
                    "members": members,
                    "keep_candidate": keep["filename"],
                    "potential_savings": others_size,
                    "potential_savings_formatted": format_size(others_size),
                }
            )

        # Sort groups by size desc
        similar_groups.sort(key=lambda g: g["potential_savings"], reverse=True)

        total_savings = sum(g["potential_savings"] for g in similar_groups)
        total_extra_photos = sum(g["member_count"] - 1 for g in similar_groups)

        return {
            "groups": similar_groups[:100],
            "summary": {
                "total_compared": len(photos),
                "groups_found": len(similar_groups),
                "total_similar_photos": total_extra_photos + len(similar_groups),
                "extra_photos": total_extra_photos,
                "potential_savings": total_savings,
                "potential_savings_formatted": format_size(total_savings),
                "threshold": threshold,
            },
        }


def format_summary(data: dict[str, Any]) -> str:
    """Format human-readable summary."""
    lines = []
    s = data["summary"]

    if "error" in data:
        lines.append(f"⚠️  {data['error']}")
        return "\n".join(lines)

    lines.append("🔍 PHOTO SIMILARITY DETECTION")
    lines.append("=" * 50)
    lines.append(f"Photos compared:     {s['total_compared']:,}")
    lines.append(f"Similarity threshold: {s['threshold']:.0%}")
    lines.append(f"Similar groups:      {s['groups_found']:,}")
    lines.append(f"Extra photos:        {s['extra_photos']:,}")
    lines.append(f"Potential savings:   {s['potential_savings_formatted']}")

    if data["groups"]:
        lines.append("")
        lines.append("Similar photo groups:")
        for i, group in enumerate(data["groups"][:20], 1):
            lines.append(f"  {i:>3}. {group['member_count']} photos  savings: {group['potential_savings_formatted']}")
            for m in group["members"][:5]:
                fav = "⭐" if m["is_favorite"] else "  "
                lines.append(f"       {fav} {m['filename']:40s} {m['size_formatted']:>10}")

    return "\n".join(lines)


def main():
    def add_args(parser):
        parser.add_argument(
            "--threshold",
            type=float,
            default=0.95,
            help="Similarity threshold 0-1 (default: 0.95 = very similar)",
        )
        parser.add_argument("--year", help="Filter to specific year (YYYY)")
        parser.add_argument(
            "--limit",
            type=int,
            default=500,
            help="Max photos to compare (default: 500, higher = slower)",
        )

    def invoke(db_path, args):
        return find_similar_photos(
            db_path=db_path,
            threshold=args.threshold,
            year=args.year,
            limit=args.limit,
        )

    return run_script(
        description="Find visually similar photos",
        analyze_fn=invoke,
        format_fn=format_summary,
        extra_args_fn=add_args,
    )


if __name__ == "__main__":
    sys.exit(main())
