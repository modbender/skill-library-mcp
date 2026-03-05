#!/usr/bin/env python3
"""
Cleanup Executor: perform batch cleanup operations via AppleScript.
Supports moving junk photos to trash with interactive confirmation.
All actions go through Photos.app for safety — nothing touches the database directly.
"""

import argparse
import subprocess
import sys
from typing import Any, Optional

from _common import PhotosDB, coredata_to_datetime, escape_applescript, format_size, output_json

# Maximum items per AppleScript batch (Photos.app can be slow with large batches)
MAX_BATCH_SIZE = 50


def get_cleanup_candidates(
    db_path: Optional[str] = None,
    category: str = "old_screenshots",
    screenshot_age_days: int = 30,
    quality_threshold: float = 0.3,
    limit: int = 500,
) -> dict[str, Any]:
    """
    Get cleanup candidates for a specific category.

    Args:
        db_path: Path to database
        category: Type of cleanup ('old_screenshots', 'burst_leftovers',
                  'low_quality', 'duplicates', 'all_screenshots')
        screenshot_age_days: Age threshold for old screenshots
        quality_threshold: Quality score threshold for low quality
        limit: Maximum candidates to return

    Returns:
        Cleanup candidates dictionary
    """
    with PhotosDB(db_path) as conn:
        cursor = conn.cursor()

        candidates = []

        if category in ("old_screenshots", "all_screenshots"):
            from datetime import datetime, timedelta

            from _common import datetime_to_coredata

            where = "a.ZTRASHEDSTATE != 1 AND a.ZISDETECTEDSCREENSHOT = 1"
            params: list[Any] = []

            if category == "old_screenshots":
                cutoff = datetime.now() - timedelta(days=screenshot_age_days)
                cutoff_ts = datetime_to_coredata(cutoff)
                where += " AND a.ZDATECREATED < ?"
                params.append(cutoff_ts)

            params.append(limit)
            cursor.execute(
                f"""
                SELECT
                    a.Z_PK, a.ZFILENAME, a.ZDATECREATED,
                    aa.ZORIGINALFILESIZE
                FROM ZASSET a
                LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
                WHERE {where}
                ORDER BY a.ZDATECREATED
                LIMIT ?
            """,
                params,
            )

            for row in cursor.fetchall():
                created = coredata_to_datetime(row["ZDATECREATED"])
                candidates.append(
                    {
                        "id": row["Z_PK"],
                        "filename": row["ZFILENAME"],
                        "created": created.isoformat() if created else None,
                        "size": row["ZORIGINALFILESIZE"] or 0,
                        "size_formatted": format_size(row["ZORIGINALFILESIZE"] or 0),
                        "category": category,
                    }
                )

        elif category == "burst_leftovers":
            cursor.execute(
                """
                SELECT
                    a.Z_PK, a.ZFILENAME, a.ZDATECREATED,
                    aa.ZORIGINALFILESIZE
                FROM ZASSET a
                LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
                WHERE a.ZTRASHEDSTATE != 1
                AND a.ZAVALANCHEKIND > 0
                AND (a.ZAVALANCHEPICKTYPE IS NULL OR a.ZAVALANCHEPICKTYPE = 0)
                ORDER BY a.ZDATECREATED
                LIMIT ?
            """,
                (limit,),
            )

            for row in cursor.fetchall():
                created = coredata_to_datetime(row["ZDATECREATED"])
                candidates.append(
                    {
                        "id": row["Z_PK"],
                        "filename": row["ZFILENAME"],
                        "created": created.isoformat() if created else None,
                        "size": row["ZORIGINALFILESIZE"] or 0,
                        "size_formatted": format_size(row["ZORIGINALFILESIZE"] or 0),
                        "category": "burst_leftovers",
                    }
                )

        elif category == "low_quality":
            from _common import build_asset_query, get_quality_score

            query = build_asset_query(
                where_clauses=[
                    "a.ZTRASHEDSTATE != 1",
                    "a.ZKIND = 0",
                    "a.ZISDETECTEDSCREENSHOT != 1",
                ],
                join_additional=True,
                join_computed=True,
                order_by="ca.ZFAILURESCORE DESC",
                limit=limit * 3,  # fetch more since we filter by quality
            )
            cursor.execute(query)

            for row in cursor.fetchall():
                quality = get_quality_score(row)
                if quality is not None and quality < quality_threshold:
                    created = coredata_to_datetime(row["ZDATECREATED"])
                    candidates.append(
                        {
                            "id": row["Z_PK"],
                            "filename": row["ZFILENAME"],
                            "created": created.isoformat() if created else None,
                            "size": row["ZORIGINALFILESIZE"] or 0,
                            "size_formatted": format_size(row["ZORIGINALFILESIZE"] or 0),
                            "quality_score": round(quality, 3),
                            "category": "low_quality",
                        }
                    )
                    if len(candidates) >= limit:
                        break

        elif category == "duplicates":
            cursor.execute(
                """
                SELECT
                    a.Z_PK, a.ZFILENAME, a.ZDATECREATED,
                    a.ZFAVORITE,
                    aa.ZORIGINALFILESIZE,
                    a.ZDUPLICATEASSETVISIBILITYSTATE
                FROM ZASSET a
                LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
                WHERE a.ZTRASHEDSTATE != 1
                AND a.ZDUPLICATEASSETVISIBILITYSTATE > 0
                AND a.ZFAVORITE != 1
                ORDER BY a.ZDATECREATED
                LIMIT ?
            """,
                (limit,),
            )

            for row in cursor.fetchall():
                created = coredata_to_datetime(row["ZDATECREATED"])
                candidates.append(
                    {
                        "id": row["Z_PK"],
                        "filename": row["ZFILENAME"],
                        "created": created.isoformat() if created else None,
                        "size": row["ZORIGINALFILESIZE"] or 0,
                        "size_formatted": format_size(row["ZORIGINALFILESIZE"] or 0),
                        "category": "duplicates",
                    }
                )

        total_size = sum(c["size"] for c in candidates)

        return {
            "candidates": candidates,
            "summary": {
                "category": category,
                "count": len(candidates),
                "total_size": total_size,
                "total_size_formatted": format_size(total_size),
            },
        }


def generate_trash_applescript(filenames: list[str]) -> str:
    """
    Generate AppleScript to move items to trash by filename matching.

    Photos.app doesn't expose database IDs, so we match by filename.
    This is the safest approach.

    Args:
        filenames: List of filenames to trash

    Returns:
        AppleScript string
    """
    # Build the filename matching list with proper escaping
    filename_list = ", ".join(f'"{escape_applescript(fn)}"' for fn in filenames)

    script = f"""
set targetNames to {{{filename_list}}}
set matchCount to 0

tell application "Photos"
    repeat with targetName in targetNames
        try
            set matchingItems to (search for targetName)
            repeat with anItem in matchingItems
                if (filename of anItem) is equal to (contents of targetName) then
                    delete anItem
                    set matchCount to matchCount + 1
                end if
            end repeat
        end try
    end repeat
end tell

return matchCount & " items moved to Recently Deleted"
"""
    return script


def execute_cleanup(
    candidates: list[dict[str, Any]],
    dry_run: bool = True,
    batch_size: int = MAX_BATCH_SIZE,
) -> dict[str, Any]:
    """
    Execute cleanup by moving candidates to trash via AppleScript.

    Args:
        candidates: List of cleanup candidates
        dry_run: If True, show what would happen without doing it
        batch_size: Number of items per AppleScript batch

    Returns:
        Execution results
    """
    total = len(candidates)
    total_size = sum(c["size"] for c in candidates)
    results = {
        "dry_run": dry_run,
        "total_candidates": total,
        "total_size": total_size,
        "total_size_formatted": format_size(total_size),
        "batches": [],
        "errors": [],
        "success_count": 0,
    }

    if dry_run:
        results["message"] = (
            f"DRY RUN: Would move {total} items ({format_size(total_size)}) to Recently Deleted. "
            f"Run with --execute to proceed."
        )
        return results

    # Process in batches
    for i in range(0, total, batch_size):
        batch = candidates[i : i + batch_size]
        filenames = [c["filename"] for c in batch]

        script = generate_trash_applescript(filenames)

        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                results["batches"].append(
                    {
                        "batch": i // batch_size + 1,
                        "count": len(batch),
                        "status": "success",
                        "output": result.stdout.strip(),
                    }
                )
                results["success_count"] += len(batch)
            else:
                results["batches"].append(
                    {
                        "batch": i // batch_size + 1,
                        "count": len(batch),
                        "status": "error",
                        "error": result.stderr.strip(),
                    }
                )
                results["errors"].append(result.stderr.strip())

        except subprocess.TimeoutExpired:
            results["errors"].append(f"Batch {i // batch_size + 1} timed out")
        except Exception as e:
            results["errors"].append(f"Batch {i // batch_size + 1}: {e!s}")

    results["message"] = (
        f"Processed {results['success_count']}/{total} items. "
        f"Check Recently Deleted in Photos.app to confirm or recover."
    )
    return results


def format_summary(data: dict[str, Any]) -> str:
    """Format cleanup candidates/results as human-readable summary."""
    lines = []
    lines.append("🧹 CLEANUP EXECUTOR")
    lines.append("=" * 50)
    lines.append("")

    if "candidates" in data:
        s = data["summary"]
        lines.append(f"Category: {s['category']}")
        lines.append(f"Candidates: {s['count']:,}")
        lines.append(f"Total size: {s['total_size_formatted']}")
        lines.append("")

        lines.append("Items to clean up:")
        for c in data["candidates"][:20]:
            lines.append(f"  {c['filename']} ({c['size_formatted']})")
            if c.get("quality_score") is not None:
                lines.append(f"    Quality: {c['quality_score']:.3f}")

        if len(data["candidates"]) > 20:
            lines.append(f"  ... and {len(data['candidates']) - 20} more")
        lines.append("")
        lines.append("⚠️  To execute, run with --execute flag")
        lines.append("    Items will be moved to Recently Deleted (recoverable for 30 days)")

    elif "message" in data:
        lines.append(data["message"])
        if data.get("errors"):
            lines.append("")
            lines.append("Errors:")
            for err in data["errors"]:
                lines.append(f"  ⚠️  {err}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Execute cleanup operations via AppleScript",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview old screenshots to clean up
  %(prog)s --category old_screenshots --human

  # Preview burst leftovers
  %(prog)s --category burst_leftovers --human

  # Actually move old screenshots to trash
  %(prog)s --category old_screenshots --execute

  # Clean up with custom settings
  %(prog)s --category old_screenshots --screenshot-age 14 --execute

Categories:
  old_screenshots   - Screenshots older than --screenshot-age days
  all_screenshots   - All screenshots
  burst_leftovers   - Unpicked burst photos
  low_quality       - Photos below --quality-threshold
  duplicates        - Apple-detected duplicates (non-favorites only)

⚠️  SAFETY: Items are moved to Recently Deleted, not permanently deleted.
    You have 30 days to recover them in Photos.app.
        """,
    )
    parser.add_argument("--db-path", help="Path to Photos.sqlite database")
    parser.add_argument("--library", help="Path to Photos library")
    parser.add_argument(
        "--category",
        required=True,
        choices=["old_screenshots", "all_screenshots", "burst_leftovers", "low_quality", "duplicates"],
        help="Category of items to clean up",
    )
    parser.add_argument("--screenshot-age", type=int, default=30, help="Screenshot age in days (default: 30)")
    parser.add_argument(
        "--quality-threshold", type=float, default=0.3, help="Quality threshold for low_quality category (default: 0.3)"
    )
    parser.add_argument("--limit", type=int, default=500, help="Maximum items to process (default: 500)")
    parser.add_argument(
        "--execute", action="store_true", help="Actually perform the cleanup (moves to Recently Deleted)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=MAX_BATCH_SIZE,
        help=f"Items per AppleScript batch (default: {MAX_BATCH_SIZE})",
    )
    parser.add_argument("-o", "--output", help="Output JSON file")
    parser.add_argument("--human", action="store_true", help="Output human-readable summary")

    args = parser.parse_args()

    try:
        db_path = args.db_path or args.library

        # Get candidates
        data = get_cleanup_candidates(
            db_path=db_path,
            category=args.category,
            screenshot_age_days=args.screenshot_age,
            quality_threshold=args.quality_threshold,
            limit=args.limit,
        )

        if not data["candidates"]:
            print(f"No cleanup candidates found for category: {args.category}")
            return 0

        if args.execute:
            # Confirm before executing
            count = len(data["candidates"])
            total_size = format_size(sum(c["size"] for c in data["candidates"]))

            print(f"⚠️  About to move {count} items ({total_size}) to Recently Deleted.")
            print(f"    Category: {args.category}")
            print("    You can recover them within 30 days in Photos.app.")
            print()

            confirm = input("Type 'yes' to proceed: ").strip().lower()
            if confirm != "yes":
                print("Cancelled.")
                return 0

            result = execute_cleanup(
                candidates=data["candidates"],
                dry_run=False,
                batch_size=args.batch_size,
            )

            if args.human:
                print(format_summary(result))
            else:
                output_json(result, args.output)
        else:
            # Preview mode
            if args.human:
                print(format_summary(data))
            else:
                output_json(data, args.output)
                if not args.output:
                    print("\n" + format_summary(data), file=sys.stderr)

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
