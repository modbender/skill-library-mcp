#!/usr/bin/env python3
"""
Generate timeline recaps: narrative summaries of photo activity over time.
Groups photos by day/event clusters and includes context like people, locations, scenes.
"""

import argparse
import sys
from datetime import datetime, timedelta
from typing import Any, Optional

from _common import PhotosDB, coredata_to_datetime, datetime_to_coredata, format_date_range, output_json


def generate_timeline(
    db_path: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    cluster_hours: int = 4,
) -> dict[str, Any]:
    """
    Generate a timeline recap for a date range.

    Args:
        db_path: Path to database
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        cluster_hours: Hours gap to consider photos part of same event

    Returns:
        Timeline dictionary
    """
    with PhotosDB(db_path) as conn:
        cursor = conn.cursor()

        # Build date filters
        where_clauses = ["a.ZTRASHEDSTATE != 1"]
        params: list = []

        if start_date:
            dt = datetime.fromisoformat(start_date)
            timestamp = datetime_to_coredata(dt)
            where_clauses.append("a.ZDATECREATED >= ?")
            params.append(timestamp)

        if end_date:
            dt = datetime.fromisoformat(end_date + " 23:59:59")
            timestamp = datetime_to_coredata(dt)
            where_clauses.append("a.ZDATECREATED <= ?")
            params.append(timestamp)

        # Get photos with metadata
        query = f"""
            SELECT
                a.Z_PK,
                a.ZFILENAME,
                a.ZDATECREATED,
                a.ZKIND,
                a.ZLATITUDE,
                a.ZLONGITUDE,
                a.ZFAVORITE
            FROM ZASSET a
            WHERE {" AND ".join(where_clauses)}
            ORDER BY a.ZDATECREATED
        """

        cursor.execute(query, params)
        photos = []

        for row in cursor.fetchall():
            created = coredata_to_datetime(row["ZDATECREATED"])
            if created:
                photos.append(
                    {
                        "id": row["Z_PK"],
                        "filename": row["ZFILENAME"],
                        "created": created,
                        "kind": "photo" if row["ZKIND"] == 0 else "video",
                        "latitude": row["ZLATITUDE"],
                        "longitude": row["ZLONGITUDE"],
                        "is_favorite": bool(row["ZFAVORITE"]),
                    }
                )

        if not photos:
            return {
                "timeline": [],
                "summary": {
                    "total_photos": 0,
                    "total_days": 0,
                    "total_events": 0,
                    "date_range": "Unknown",
                },
            }

        # Cluster photos into events
        events = []
        current_event = None
        cluster_delta = timedelta(hours=cluster_hours)

        for photo in photos:
            if current_event is None:
                # Start new event
                current_event = {
                    "start_time": photo["created"],
                    "end_time": photo["created"],
                    "photos": [photo],
                }
            else:
                # Check if photo belongs to current event
                time_gap = photo["created"] - current_event["end_time"]

                if time_gap <= cluster_delta:
                    # Add to current event
                    current_event["end_time"] = photo["created"]
                    current_event["photos"].append(photo)
                else:
                    # Close current event and start new one
                    events.append(current_event)
                    current_event = {
                        "start_time": photo["created"],
                        "end_time": photo["created"],
                        "photos": [photo],
                    }

        # Add last event
        if current_event:
            events.append(current_event)

        # Enrich events with additional data
        for event in events:
            photo_ids = [p["id"] for p in event["photos"]]
            event["photo_count"] = len(photo_ids)
            event["video_count"] = sum(1 for p in event["photos"] if p["kind"] == "video")
            event["favorites"] = sum(1 for p in event["photos"] if p["is_favorite"])

            # Get people in this event
            if photo_ids:
                placeholders = ",".join("?" * len(photo_ids))
                cursor.execute(
                    f"""
                    SELECT DISTINCT p.ZFULLNAME, COUNT(df.ZASSET) as count
                    FROM ZPERSON p
                    JOIN ZDETECTEDFACE df ON p.Z_PK = df.ZPERSON
                    WHERE df.ZASSET IN ({placeholders})
                    GROUP BY p.Z_PK
                    ORDER BY count DESC
                """,
                    photo_ids,
                )

                event["people"] = [{"name": row["ZFULLNAME"], "count": row["count"]} for row in cursor.fetchall()]
            else:
                event["people"] = []

            # Get scene classifications
            if photo_ids:
                cursor.execute(
                    f"""
                    SELECT DISTINCT sc.ZSCENENAME, COUNT(*) as count
                    FROM ZSCENECLASSIFICATION sc
                    WHERE sc.ZASSET IN ({placeholders})
                    GROUP BY sc.ZSCENENAME
                    ORDER BY count DESC
                    LIMIT 5
                """,
                    photo_ids,
                )

                event["scenes"] = [
                    {"scene": row["ZSCENENAME"], "count": row["count"]}
                    for row in cursor.fetchall()
                    if row["ZSCENENAME"]
                ]
            else:
                event["scenes"] = []

            # Location summary
            locations = [(p["latitude"], p["longitude"]) for p in event["photos"] if p["latitude"] and p["longitude"]]

            if locations:
                avg_lat = sum(loc[0] for loc in locations) / len(locations)
                avg_lon = sum(loc[1] for loc in locations) / len(locations)
                event["location"] = {
                    "latitude": round(avg_lat, 4),
                    "longitude": round(avg_lon, 4),
                    "has_location": True,
                }
            else:
                event["location"] = {"has_location": False}

        # Group events by day
        timeline = []
        current_day = None
        day_events = []

        for event in events:
            event_date = event["start_time"].date()

            if current_day is None or event_date != current_day:
                # Save previous day
                if day_events:
                    timeline.append(
                        {
                            "date": current_day.isoformat(),
                            "day_name": current_day.strftime("%A"),
                            "events": day_events,
                            "total_photos": sum(e["photo_count"] for e in day_events),
                        }
                    )

                # Start new day
                current_day = event_date
                day_events = [format_event(event)]
            else:
                # Add to current day
                day_events.append(format_event(event))

        # Add last day
        if day_events:
            timeline.append(
                {
                    "date": current_day.isoformat(),
                    "day_name": current_day.strftime("%A"),
                    "events": day_events,
                    "total_photos": sum(e["photo_count"] for e in day_events),
                }
            )

        # Summary
        total_photos = sum(day["total_photos"] for day in timeline)

        return {
            "timeline": timeline,
            "summary": {
                "total_photos": total_photos,
                "total_days": len(timeline),
                "total_events": len(events),
                "date_range": format_date_range(
                    photos[0]["created"] if photos else None, photos[-1]["created"] if photos else None
                ),
            },
        }


def format_event(event: dict[str, Any]) -> dict[str, Any]:
    """Format event for output."""
    return {
        "time": event["start_time"].strftime("%H:%M"),
        "duration_minutes": int((event["end_time"] - event["start_time"]).total_seconds() / 60),
        "photo_count": event["photo_count"],
        "video_count": event["video_count"],
        "favorites": event["favorites"],
        "people": event["people"],
        "scenes": event["scenes"],
        "location": event["location"],
    }


def format_narrative(timeline_data: dict[str, Any]) -> str:
    """Format timeline as narrative text suitable for AI narration."""
    lines = []
    lines.append("📅 PHOTO TIMELINE RECAP")
    lines.append("=" * 50)
    lines.append("")

    summary = timeline_data["summary"]
    lines.append(f"Period: {summary['date_range']}")
    lines.append(f"Total: {summary['total_photos']} photos across {summary['total_days']} days")
    lines.append(f"Events: {summary['total_events']}")
    lines.append("")

    for day in timeline_data["timeline"]:
        lines.append(f"📆 {day['date']} ({day['day_name']}) - {day['total_photos']} photos")

        for event in day["events"]:
            duration = f"{event['duration_minutes']}m" if event["duration_minutes"] > 0 else "instant"
            lines.append(f"  🕐 {event['time']} ({duration})")
            lines.append(f"     {event['photo_count']} photos")

            if event["video_count"] > 0:
                lines[-1] += f", {event['video_count']} videos"
            if event["favorites"] > 0:
                lines[-1] += f" ⭐ {event['favorites']} favorites"
            lines.append("")

            if event["people"]:
                people_str = ", ".join(p["name"] for p in event["people"][:3])
                lines.append(f"     👥 {people_str}")

            if event["scenes"]:
                scenes_str = ", ".join(s["scene"] for s in event["scenes"][:3])
                lines.append(f"     🏷️  {scenes_str}")

            if event["location"]["has_location"]:
                loc = event["location"]
                lines.append(f"     📍 {loc['latitude']}, {loc['longitude']}")

            lines.append("")

        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate photo timeline recap",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Last week
  %(prog)s --start-date 2025-03-01 --end-date 2025-03-07

  # Last month
  %(prog)s --start-date 2025-02-01 --end-date 2025-02-28

  # Custom clustering (8-hour gaps = same event)
  %(prog)s --start-date 2025-03-01 --cluster-hours 8 --narrative
        """,
    )
    parser.add_argument("--db-path", help="Path to Photos.sqlite database")
    parser.add_argument("--library", help="Path to Photos library")
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date (YYYY-MM-DD)")
    parser.add_argument(
        "--cluster-hours", type=int, default=4, help="Hours between photos to consider separate events (default: 4)"
    )
    parser.add_argument("--narrative", action="store_true", help="Output narrative text instead of JSON")
    parser.add_argument("-o", "--output", help="Output file")

    args = parser.parse_args()

    try:
        db_path = args.db_path or args.library

        timeline = generate_timeline(
            db_path=db_path,
            start_date=args.start_date,
            end_date=args.end_date,
            cluster_hours=args.cluster_hours,
        )

        if args.narrative:
            output_text = format_narrative(timeline)
            if args.output:
                with open(args.output, "w") as f:
                    f.write(output_text)
                print(f"Written to: {args.output}", file=sys.stderr)
            else:
                print(output_text)
        else:
            output_json(timeline, args.output)

            if not args.output:
                print("\n" + format_narrative(timeline), file=sys.stderr)

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error generating timeline: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
