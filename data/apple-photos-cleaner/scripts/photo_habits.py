#!/usr/bin/env python3
"""
Photo Habits & Insights: behavioral analytics for your photo library.
Time-of-day patterns, busiest days, seasonal trends, photo vs video ratios.
"""

import sys
from collections import defaultdict
from typing import Any, Optional

from _common import PhotosDB, coredata_to_datetime, format_size, run_script, validate_year

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def analyze_habits(
    db_path: Optional[str] = None,
    year: Optional[str] = None,
) -> dict[str, Any]:
    """
    Analyze photo-taking habits and patterns.

    Args:
        db_path: Path to database
        year: Filter to specific year

    Returns:
        Habits analysis dictionary
    """
    with PhotosDB(db_path) as conn:
        cursor = conn.cursor()

        year_filter = ""
        year_params: list = []
        if year:
            year = validate_year(year)
            year_filter = "AND strftime('%Y', datetime(a.ZDATECREATED + 978307200, 'unixepoch')) = ?"
            year_params = [year]

        # Get all non-trashed assets with timestamps
        cursor.execute(
            f"""
            SELECT
                a.ZDATECREATED,
                a.ZKIND,
                a.ZFAVORITE,
                a.ZISDETECTEDSCREENSHOT,
                aa.ZORIGINALFILESIZE
            FROM ZASSET a
            LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
            WHERE a.ZTRASHEDSTATE != 1
            AND a.ZDATECREATED IS NOT NULL
            {year_filter}
            ORDER BY a.ZDATECREATED
        """,
            year_params,
        )

        # Accumulators
        by_hour = defaultdict(int)
        by_day_of_week = defaultdict(int)
        by_month = defaultdict(int)
        by_year_month = defaultdict(lambda: {"photos": 0, "videos": 0, "screenshots": 0, "size": 0, "favorites": 0})
        by_year = defaultdict(lambda: {"photos": 0, "videos": 0, "total": 0, "size": 0})
        streaks = {"current": 0, "max": 0, "max_start": None, "max_end": None}
        daily_counts = defaultdict(int)

        total_photos = 0
        total_videos = 0
        total_screenshots = 0
        total_favorites = 0
        total_size = 0
        first_date = None
        last_date = None

        for row in cursor.fetchall():
            dt = coredata_to_datetime(row["ZDATECREATED"])
            if dt is None:
                continue

            if first_date is None:
                first_date = dt
            last_date = dt

            is_video = row["ZKIND"] == 1
            is_screenshot = bool(row["ZISDETECTEDSCREENSHOT"])
            is_fav = bool(row["ZFAVORITE"])
            size = row["ZORIGINALFILESIZE"] or 0

            total_size += size
            if is_fav:
                total_favorites += 1

            if is_video:
                total_videos += 1
            elif is_screenshot:
                total_screenshots += 1
            else:
                total_photos += 1

            # Hour of day
            by_hour[dt.hour] += 1

            # Day of week (0=Monday)
            by_day_of_week[dt.weekday()] += 1

            # Month of year
            by_month[dt.month] += 1

            # Year-month
            ym = dt.strftime("%Y-%m")
            if is_video:
                by_year_month[ym]["videos"] += 1
            elif is_screenshot:
                by_year_month[ym]["screenshots"] += 1
            else:
                by_year_month[ym]["photos"] += 1
            by_year_month[ym]["size"] += size
            if is_fav:
                by_year_month[ym]["favorites"] += 1

            # Year
            y = str(dt.year)
            if is_video:
                by_year[y]["videos"] += 1
            else:
                by_year[y]["photos"] += 1
            by_year[y]["total"] += 1
            by_year[y]["size"] += size

            # Daily counts for streak tracking
            day_key = dt.strftime("%Y-%m-%d")
            daily_counts[day_key] += 1

        # Calculate streaks
        if daily_counts:
            from datetime import date

            all_days = sorted(daily_counts.keys())
            current_streak = 1
            max_streak = 1
            max_streak_start = all_days[0]
            max_streak_end = all_days[0]
            streak_start = all_days[0]

            for i in range(1, len(all_days)):
                d1 = date.fromisoformat(all_days[i - 1])
                d2 = date.fromisoformat(all_days[i])

                if (d2 - d1).days == 1:
                    current_streak += 1
                else:
                    if current_streak > max_streak:
                        max_streak = current_streak
                        max_streak_start = streak_start
                        max_streak_end = all_days[i - 1]
                    current_streak = 1
                    streak_start = all_days[i]

            # Check final streak
            if current_streak > max_streak:
                max_streak = current_streak
                max_streak_start = streak_start
                max_streak_end = all_days[-1]

            streaks = {
                "max_days": max_streak,
                "max_start": max_streak_start,
                "max_end": max_streak_end,
                "total_active_days": len(daily_counts),
            }

        # Busiest single day
        busiest_day = max(daily_counts.items(), key=lambda x: x[1]) if daily_counts else (None, 0)

        # Average photos per active day
        total_items = total_photos + total_videos + total_screenshots
        avg_per_active_day = total_items / len(daily_counts) if daily_counts else 0

        # Format hour-of-day data
        hour_data = []
        peak_hour = max(by_hour.items(), key=lambda x: x[1])[0] if by_hour else 0
        for h in range(24):
            count = by_hour.get(h, 0)
            hour_data.append(
                {
                    "hour": h,
                    "label": f"{h:02d}:00",
                    "count": count,
                    "is_peak": h == peak_hour,
                }
            )

        # Format day-of-week data
        dow_data = []
        peak_dow = max(by_day_of_week.items(), key=lambda x: x[1])[0] if by_day_of_week else 0
        for d in range(7):
            count = by_day_of_week.get(d, 0)
            dow_data.append(
                {
                    "day": d,
                    "name": DAY_NAMES[d],
                    "count": count,
                    "is_peak": d == peak_dow,
                }
            )

        # Format month data
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_data = []
        peak_month = max(by_month.items(), key=lambda x: x[1])[0] if by_month else 1
        for m in range(1, 13):
            count = by_month.get(m, 0)
            month_data.append(
                {
                    "month": m,
                    "name": month_names[m - 1],
                    "count": count,
                    "is_peak": m == peak_month,
                }
            )

        # Monthly trend
        monthly_trend = []
        for ym in sorted(by_year_month.keys()):
            data = by_year_month[ym]
            monthly_trend.append(
                {
                    "period": ym,
                    "photos": data["photos"],
                    "videos": data["videos"],
                    "screenshots": data["screenshots"],
                    "total": data["photos"] + data["videos"] + data["screenshots"],
                    "size": data["size"],
                    "size_formatted": format_size(data["size"]),
                    "favorites": data["favorites"],
                }
            )

        # Year trends
        yearly_trend = []
        for y in sorted(by_year.keys()):
            data = by_year[y]
            ratio = round(data["videos"] / data["photos"] * 100, 1) if data["photos"] else 0
            yearly_trend.append(
                {
                    "year": y,
                    "photos": data["photos"],
                    "videos": data["videos"],
                    "total": data["total"],
                    "size": data["size"],
                    "size_formatted": format_size(data["size"]),
                    "video_ratio": ratio,
                }
            )

        # Time of day categories
        morning = sum(by_hour.get(h, 0) for h in range(6, 12))
        afternoon = sum(by_hour.get(h, 0) for h in range(12, 18))
        evening = sum(by_hour.get(h, 0) for h in range(18, 24))
        night = sum(by_hour.get(h, 0) for h in range(0, 6))

        return {
            "by_hour": hour_data,
            "by_day_of_week": dow_data,
            "by_month": month_data,
            "monthly_trend": monthly_trend,
            "yearly_trend": yearly_trend,
            "time_of_day": {
                "morning": {"label": "Morning (6am-12pm)", "count": morning},
                "afternoon": {"label": "Afternoon (12pm-6pm)", "count": afternoon},
                "evening": {"label": "Evening (6pm-12am)", "count": evening},
                "night": {"label": "Night (12am-6am)", "count": night},
            },
            "streaks": streaks,
            "summary": {
                "total_photos": total_photos,
                "total_videos": total_videos,
                "total_screenshots": total_screenshots,
                "total_favorites": total_favorites,
                "total_size": total_size,
                "total_size_formatted": format_size(total_size),
                "first_date": first_date.isoformat() if first_date else None,
                "last_date": last_date.isoformat() if last_date else None,
                "busiest_day": busiest_day[0],
                "busiest_day_count": busiest_day[1],
                "avg_per_active_day": round(avg_per_active_day, 1),
                "peak_hour": f"{peak_hour:02d}:00" if by_hour else None,
                "peak_day": DAY_NAMES[peak_dow] if by_day_of_week else None,
                "peak_month": month_names[peak_month - 1] if by_month else None,
            },
        }


def format_summary(data: dict[str, Any]) -> str:
    """Format habits analysis as human-readable summary."""
    lines = []
    lines.append("📊 PHOTO HABITS & INSIGHTS")
    lines.append("=" * 50)
    lines.append("")

    s = data["summary"]
    lines.append(
        f"Total: {s['total_photos']:,} photos, {s['total_videos']:,} videos, {s['total_screenshots']:,} screenshots"
    )
    lines.append(f"Favorites: {s['total_favorites']:,}")
    lines.append(f"Storage: {s['total_size_formatted']}")
    if s["first_date"] and s["last_date"]:
        lines.append(f"Period: {s['first_date'][:10]} → {s['last_date'][:10]}")
    lines.append(f"Average per active day: {s['avg_per_active_day']}")
    lines.append("")

    lines.append("⏰ When You Shoot:")
    lines.append(f"  Peak hour: {s['peak_hour']}")
    lines.append(f"  Peak day: {s['peak_day']}")
    lines.append(f"  Peak month: {s['peak_month']}")
    lines.append("")

    tod = data["time_of_day"]
    total = sum(v["count"] for v in tod.values()) or 1
    lines.append("  Time of Day:")
    for period in ["morning", "afternoon", "evening", "night"]:
        d = tod[period]
        pct = round(d["count"] / total * 100, 1)
        bar = "█" * int(pct / 3)
        lines.append(f"    {d['label']}: {d['count']:,} ({pct}%) {bar}")
    lines.append("")

    lines.append("  Day of Week:")
    for day in data["by_day_of_week"]:
        peak = " ← peak" if day["is_peak"] else ""
        bar = "█" * int(day["count"] / max(d["count"] for d in data["by_day_of_week"]) * 20) if day["count"] else ""
        lines.append(f"    {day['name']:>9}: {day['count']:>6,} {bar}{peak}")
    lines.append("")

    if data["streaks"].get("max_days"):
        st = data["streaks"]
        lines.append("🔥 Streaks:")
        lines.append(f"  Longest streak: {st['max_days']} consecutive days")
        lines.append(f"    ({st['max_start']} → {st['max_end']})")
        lines.append(f"  Total active days: {st['total_active_days']:,}")
        lines.append("")

    if data["summary"]["busiest_day"]:
        lines.append(f"📸 Busiest day: {s['busiest_day']} ({s['busiest_day_count']:,} items)")
        lines.append("")

    lines.append("📈 Year Trends:")
    for yt in data["yearly_trend"]:
        lines.append(
            f"  {yt['year']}: {yt['total']:,} items ({yt['size_formatted']}) | video ratio: {yt['video_ratio']}%"
        )
    lines.append("")

    return "\n".join(lines)


def main():
    def add_args(parser):
        parser.add_argument("--year", help="Filter to specific year (YYYY)")

    def invoke(db_path, args):
        return analyze_habits(
            db_path=db_path,
            year=args.year,
        )

    return run_script(
        description="Analyze photo-taking habits and patterns",
        analyze_fn=invoke,
        format_fn=format_summary,
        extra_args_fn=add_args,
        epilog="""
Examples:
  %(prog)s --human
  %(prog)s --year 2025 --human
  %(prog)s --output habits.json
        """,
    )


if __name__ == "__main__":
    sys.exit(main())
