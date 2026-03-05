#!/usr/bin/env python3
"""
GHIN Golf Statistics Analyzer

This script reads a GHIN (Golf Handicap and Information Network) data JSON file 
and computes comprehensive golf statistics including handicap trends, scoring averages,
course performance, and historical breakdowns.

WHAT IT DOES:
- Reads a single JSON file containing GHIN data (path provided as CLI argument)
- Computes handicap trends, scoring statistics, and course performance metrics
- Outputs results in text or JSON format
- Analyzes historical data for trends and patterns

WHAT IT DOES NOT DO:
- No network calls or web scraping (GHIN data collection is handled separately by the agent)
- No subprocess execution or system commands
- No file writes or data persistence
- No credential handling or authentication
- No external API calls or database connections

The GHIN data collection itself is performed by the OpenClaw agent using browser automation.
This script only processes the already-collected data file.
"""

import json
import sys
import argparse
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze GHIN golf statistics from JSON data file"
    )
    parser.add_argument(
        "json_file", 
        help="Path to GHIN data JSON file"
    )
    parser.add_argument(
        "--format", 
        choices=["text", "json"], 
        default="text",
        help="Output format (default: text)"
    )
    return parser.parse_args()


def load_ghin_data(file_path: str) -> Dict[str, Any]:
    """Load and parse GHIN data from JSON file.
    
    Args:
        file_path: Path to the JSON file containing GHIN data.
                   Must be a .json file containing expected GHIN keys.
        
    Returns:
        Dictionary containing parsed GHIN data
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist
        ValueError: If the file is not a .json file or lacks GHIN data keys
    """
    resolved = Path(file_path).resolve()

    # Restrict to .json files only to prevent arbitrary file reads
    if resolved.suffix.lower() != ".json":
        raise ValueError("Input file must have a .json extension")

    if not resolved.is_file():
        raise FileNotFoundError(f"GHIN data file not found: {file_path}")

    try:
        with open(resolved, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise ValueError("File does not contain valid JSON")

    # Validate expected GHIN data structure (must have at least one key field)
    required_keys = {"scores", "handicap_index"}
    if not isinstance(data, dict) or not required_keys.intersection(data.keys()):
        raise ValueError("File does not appear to contain GHIN data (missing expected keys)")

    return data


def get_handicap_trend(handicap_history: List[Dict[str, Any]]) -> str:
    """Determine handicap trend based on recent history.
    
    Args:
        handicap_history: List of handicap history entries with date and index
        
    Returns:
        String indicating trend: "improving", "declining", "stable", or "insufficient_data"
    """
    if len(handicap_history) < 5:
        return "insufficient_data"
    
    # Sort by date and get last 5 entries
    sorted_history = sorted(handicap_history, key=lambda x: x["date"])
    recent_5 = sorted_history[-5:]
    
    indices = [entry["index"] for entry in recent_5]
    
    # Calculate trend using linear regression slope approximation
    n = len(indices)
    x_values = list(range(n))
    x_mean = statistics.mean(x_values)
    y_mean = statistics.mean(indices)
    
    numerator = sum((x_values[i] - x_mean) * (indices[i] - y_mean) for i in range(n))
    denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return "stable"
    
    slope = numerator / denominator
    
    # Threshold for significant change (0.5 handicap points over 5 revisions)
    if slope > 0.1:
        return "declining"  # Handicap going up (getting worse)
    elif slope < -0.1:
        return "improving"  # Handicap going down (getting better)
    else:
        return "stable"


def extract_numeric_score(score_str: str) -> Optional[float]:
    """Extract numeric score from score string (e.g., '82A' -> 82).
    
    Args:
        score_str: Score string from GHIN data
        
    Returns:
        Numeric score value or None if cannot parse
    """
    if not score_str:
        return None
    
    # Remove non-numeric characters except decimal point
    import re
    numeric_part = re.match(r'(\d+(?:\.\d+)?)', str(score_str))
    if numeric_part:
        try:
            return float(numeric_part.group(1))
        except ValueError:
            return None
    return None


def get_best_differentials(scores: List[Dict[str, Any]], count: int = 5) -> List[Dict[str, Any]]:
    """Get the best (lowest) differentials with course and date info.
    
    Args:
        scores: List of score entries
        count: Number of best differentials to return
        
    Returns:
        List of best differential entries
    """
    valid_scores = [score for score in scores if score.get("differential") is not None]
    sorted_scores = sorted(valid_scores, key=lambda x: x["differential"])
    return sorted_scores[:count]


def analyze_courses(scores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze performance by course.
    
    Args:
        scores: List of score entries
        
    Returns:
        List of course statistics sorted by play frequency
    """
    course_stats = defaultdict(lambda: {"rounds": 0, "scores": []})
    
    for score_entry in scores:
        course = score_entry.get("course", "Unknown Course")
        numeric_score = extract_numeric_score(score_entry.get("score", ""))
        
        course_stats[course]["rounds"] += 1
        if numeric_score is not None:
            course_stats[course]["scores"].append(numeric_score)
    
    # Convert to list with averages
    result = []
    for course, stats in course_stats.items():
        avg_score = statistics.mean(stats["scores"]) if stats["scores"] else None
        result.append({
            "course": course,
            "rounds": stats["rounds"],
            "avg_score": round(avg_score, 1) if avg_score else None
        })
    
    return sorted(result, key=lambda x: x["rounds"], reverse=True)


def analyze_by_year(scores: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Analyze performance by year.
    
    Args:
        scores: List of score entries
        
    Returns:
        Dictionary with year as key and stats as values
    """
    yearly_stats = defaultdict(lambda: {"rounds": 0, "scores": []})
    
    for score_entry in scores:
        date_str = score_entry.get("date", "")
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = str(date_obj.year)
        except ValueError:
            continue
        
        numeric_score = extract_numeric_score(score_entry.get("score", ""))
        yearly_stats[year]["rounds"] += 1
        if numeric_score is not None:
            yearly_stats[year]["scores"].append(numeric_score)
    
    # Calculate averages
    result = {}
    for year, stats in yearly_stats.items():
        avg_score = statistics.mean(stats["scores"]) if stats["scores"] else None
        result[year] = {
            "rounds": stats["rounds"],
            "avg_score": round(avg_score, 1) if avg_score else None
        }
    
    return result


def get_handicap_extremes(handicap_history: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Get handicap high and low with dates.
    
    Args:
        handicap_history: List of handicap history entries
        
    Returns:
        Tuple of (lowest_handicap_entry, highest_handicap_entry)
    """
    if not handicap_history:
        return None, None
    
    sorted_by_index = sorted(handicap_history, key=lambda x: x["index"])
    lowest = sorted_by_index[0] if sorted_by_index else None
    highest = sorted_by_index[-1] if sorted_by_index else None
    
    return lowest, highest


def compute_statistics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Compute all golf statistics from GHIN data.
    
    Args:
        data: Parsed GHIN data dictionary
        
    Returns:
        Dictionary containing computed statistics
    """
    stats = {}
    
    # Current handicap and trend
    stats["current_handicap"] = data.get("handicap_index")
    handicap_history = data.get("handicap_history", [])
    stats["handicap_trend"] = get_handicap_trend(handicap_history)
    
    # Lifetime totals
    stats["lifetime_rounds"] = data.get("lifetime_rounds", 0)
    
    scores = data.get("scores", [])
    numeric_scores = [extract_numeric_score(score.get("score", "")) for score in scores]
    valid_scores = [s for s in numeric_scores if s is not None]
    
    stats["low_score"] = min(valid_scores) if valid_scores else None
    stats["high_score"] = max(valid_scores) if valid_scores else None
    
    # Best differentials
    stats["best_differentials"] = get_best_differentials(scores)
    
    # Course analysis
    stats["courses"] = analyze_courses(scores)
    
    # Yearly breakdown
    stats["yearly_breakdown"] = analyze_by_year(scores)
    
    # Performance stats from data
    ghin_stats = data.get("stats", {})
    if ghin_stats:
        stats["performance"] = {
            "par3_avg": ghin_stats.get("par3_avg"),
            "par4_avg": ghin_stats.get("par4_avg"),
            "par5_avg": ghin_stats.get("par5_avg"),
            "gir_pct": ghin_stats.get("gir_pct"),
            "fairways_pct": ghin_stats.get("fairways_pct"),
            "putts_avg": ghin_stats.get("putts_avg")
        }
    
    # Handicap extremes
    lowest_hcp, highest_hcp = get_handicap_extremes(handicap_history)
    stats["handicap_low"] = lowest_hcp
    stats["handicap_high"] = highest_hcp
    
    return stats


def format_text_output(stats: Dict[str, Any]) -> str:
    """Format statistics as human-readable text.
    
    Args:
        stats: Computed statistics dictionary
        
    Returns:
        Formatted text string
    """
    lines = []
    lines.append("GHIN Golf Statistics Report")
    lines.append("=" * 30)
    lines.append("")
    
    # Current handicap and trend
    current_hcp = stats.get("current_handicap")
    if current_hcp is not None:
        trend = stats.get("handicap_trend", "unknown")
        trend_display = {
            "improving": "↗️  Improving",
            "declining": "↘️  Declining", 
            "stable": "→ Stable",
            "insufficient_data": "Insufficient data"
        }.get(trend, trend)
        
        lines.append(f"Current Handicap: {current_hcp}")
        lines.append(f"Trend (last 5): {trend_display}")
        lines.append("")
    
    # Lifetime totals
    lines.append("LIFETIME TOTALS")
    lines.append("-" * 15)
    lines.append(f"Total Rounds: {stats.get('lifetime_rounds', 0)}")
    if stats.get("low_score"):
        lines.append(f"Best Score: {stats['low_score']}")
    if stats.get("high_score"):
        lines.append(f"Worst Score: {stats['high_score']}")
    lines.append("")
    
    # Handicap extremes
    if stats.get("handicap_low") or stats.get("handicap_high"):
        lines.append("HANDICAP RANGE")
        lines.append("-" * 14)
        if stats.get("handicap_low"):
            hcp_low = stats["handicap_low"]
            lines.append(f"Lowest: {hcp_low['index']} ({hcp_low['date']})")
        if stats.get("handicap_high"):
            hcp_high = stats["handicap_high"]
            lines.append(f"Highest: {hcp_high['index']} ({hcp_high['date']})")
        lines.append("")
    
    # Best differentials
    best_diffs = stats.get("best_differentials", [])
    if best_diffs:
        lines.append("BEST DIFFERENTIALS")
        lines.append("-" * 17)
        for i, diff in enumerate(best_diffs, 1):
            course = diff.get("course", "Unknown")
            date = diff.get("date", "Unknown")
            differential = diff.get("differential", 0)
            lines.append(f"{i}. {differential:.1f} - {course} ({date})")
        lines.append("")
    
    # Course analysis
    courses = stats.get("courses", [])
    if courses:
        lines.append("MOST PLAYED COURSES")
        lines.append("-" * 19)
        for course in courses[:5]:  # Top 5
            name = course["course"]
            rounds = course["rounds"]
            avg = course["avg_score"]
            avg_str = f"avg {avg:.1f}" if avg else "no avg"
            lines.append(f"{name}: {rounds} rounds ({avg_str})")
        lines.append("")
    
    # Performance stats
    performance = stats.get("performance", {})
    if any(v is not None for v in performance.values()):
        lines.append("PERFORMANCE AVERAGES")
        lines.append("-" * 20)
        if performance.get("par3_avg"):
            lines.append(f"Par 3 Average: {performance['par3_avg']:.2f}")
        if performance.get("par4_avg"):
            lines.append(f"Par 4 Average: {performance['par4_avg']:.2f}")
        if performance.get("par5_avg"):
            lines.append(f"Par 5 Average: {performance['par5_avg']:.2f}")
        if performance.get("gir_pct"):
            lines.append(f"Greens in Regulation: {performance['gir_pct']:.1f}%")
        if performance.get("fairways_pct"):
            lines.append(f"Fairways Hit: {performance['fairways_pct']:.1f}%")
        if performance.get("putts_avg"):
            lines.append(f"Average Putts: {performance['putts_avg']:.1f}")
        lines.append("")
    
    # Yearly breakdown
    yearly = stats.get("yearly_breakdown", {})
    if yearly:
        lines.append("YEARLY BREAKDOWN")
        lines.append("-" * 16)
        for year in sorted(yearly.keys(), reverse=True):
            year_stats = yearly[year]
            rounds = year_stats["rounds"]
            avg = year_stats["avg_score"]
            avg_str = f"avg {avg:.1f}" if avg else "no avg"
            lines.append(f"{year}: {rounds} rounds ({avg_str})")
    
    return "\n".join(lines)


def format_json_output(stats: Dict[str, Any]) -> str:
    """Format statistics as JSON.
    
    Args:
        stats: Computed statistics dictionary
        
    Returns:
        JSON formatted string
    """
    return json.dumps(stats, indent=2, default=str)


def main() -> None:
    """Main function to run the GHIN statistics analyzer."""
    try:
        args = parse_arguments()
        
        # Load and parse data
        data = load_ghin_data(args.json_file)
        
        # Compute statistics
        stats = compute_statistics(data)
        
        # Output results
        if args.format == "json":
            print(format_json_output(stats))
        else:
            print(format_text_output(stats))
            
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()