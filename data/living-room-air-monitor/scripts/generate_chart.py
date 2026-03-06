#!/usr/bin/env python3
"""
Generate line charts for air quality data.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import sqlite3

# Try to import matplotlib, install if not available
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
except ImportError:
    print("matplotlib not found. Installing...")
    os.system(f"{sys.executable} -m pip install matplotlib --quiet")
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

DB_PATH = os.path.expanduser("~/.openclaw/workspace/skills/living-room-air-monitor/data/air_quality.db")

def get_db_connection():
    """Get database connection."""
    return sqlite3.connect(DB_PATH)

def get_readings(start_dt: datetime, end_dt: datetime) -> List[Dict[str, Any]]:
    """Get readings from database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT datetime, temperature, humidity, pm25, co2
        FROM air_quality
        WHERE datetime BETWEEN ? AND ?
        ORDER BY datetime ASC
    ''', (start_dt.isoformat(), end_dt.isoformat()))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            'datetime': datetime.fromisoformat(row[0]),
            'temperature': row[1],
            'humidity': row[2],
            'pm25': row[3],
            'co2': row[4]
        }
        for row in rows
    ]

def generate_chart(
    start_dt: datetime,
    end_dt: datetime,
    output_path: str,
    title: str = "Air Quality Data",
    metrics: Optional[List[str]] = None
) -> str:
    """
    Generate a line chart for the specified time period.
    
    Args:
        start_dt: Start datetime
        end_dt: End datetime
        output_path: Where to save the chart (PNG)
        title: Chart title
        metrics: List of metrics to plot ['temperature', 'humidity', 'pm25', 'co2']
                If None, plots all metrics in subplots
    
    Returns:
        Path to the generated chart
    """
    readings = get_readings(start_dt, end_dt)
    
    if not readings:
        print("No data available for the specified period")
        return None
    
    if metrics is None:
        metrics = ['temperature', 'humidity', 'pm25', 'co2']
    
    # Prepare data
    dates = [r['datetime'] for r in readings]
    
    # Create figure with subplots
    fig, axes = plt.subplots(len(metrics), 1, figsize=(12, 3 * len(metrics)), sharex=True)
    if len(metrics) == 1:
        axes = [axes]
    
    metric_labels = {
        'temperature': ('Temperature (°C)', '#FF6B6B'),
        'humidity': ('Humidity (%)', '#4ECDC4'),
        'pm25': ('PM2.5 (µg/m³)', '#45B7D1'),
        'co2': ('CO2 (ppm)', '#96CEB4')
    }
    
    for ax, metric in zip(axes, metrics):
        values = [r[metric] for r in readings]
        label, color = metric_labels.get(metric, (metric, '#333333'))
        
        ax.plot(dates, values, color=color, linewidth=1.5, marker='o', markersize=3)
        ax.set_ylabel(label, fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.legend([label], loc='upper left')
        
        # Set y-axis to start from 0 for PM2.5 and CO2
        if metric in ['pm25', 'co2']:
            ax.set_ylim(bottom=0)
    
    # Format x-axis
    axes[-1].set_xlabel('Date/Time', fontsize=10)
    
    # Determine date formatter based on time range
    time_range = end_dt - start_dt
    if time_range.days <= 1:
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        axes[-1].xaxis.set_major_locator(mdates.HourLocator(interval=4))
    elif time_range.days <= 7:
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%a %H:%M'))
        axes[-1].xaxis.set_major_locator(mdates.DayLocator())
    elif time_range.days <= 31:
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        axes[-1].xaxis.set_major_locator(mdates.DayLocator(interval=2))
    else:
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        axes[-1].xaxis.set_major_locator(mdates.MonthLocator())
    
    plt.xticks(rotation=45)
    plt.suptitle(title, fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    # Save chart
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Chart saved to: {output_path}")
    return output_path

def generate_day_chart(date: datetime, output_dir: str = "/tmp/air_charts") -> str:
    """Generate chart for a specific day."""
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    date_str = date.strftime('%Y-%m-%d')
    output_path = os.path.join(output_dir, f"day_{date_str}.png")
    return generate_chart(start, end, output_path, f"Air Quality - {date_str}")

def generate_week_chart(end_date: datetime, output_dir: str = "/tmp/air_charts") -> str:
    """Generate chart for the last 7 days ending on end_date."""
    end = end_date.replace(hour=23, minute=59, second=59)
    start = end - timedelta(days=7)
    date_str = end_date.strftime('%Y-%m-%d')
    output_path = os.path.join(output_dir, f"week_ending_{date_str}.png")
    return generate_chart(start, end, output_path, f"Air Quality - Week Ending {date_str}")

def generate_month_chart(year: int, month: int, output_dir: str = "/tmp/air_charts") -> str:
    """Generate chart for a specific month."""
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    date_str = f"{year}-{month:02d}"
    output_path = os.path.join(output_dir, f"month_{date_str}.png")
    return generate_chart(start, end, output_path, f"Air Quality - {date_str}")

def generate_3month_chart(end_date: datetime, output_dir: str = "/tmp/air_charts") -> str:
    """Generate chart for the last 3 months ending on end_date."""
    end = end_date.replace(hour=23, minute=59, second=59)
    start = end - timedelta(days=90)
    date_str = end_date.strftime('%Y-%m-%d')
    output_path = os.path.join(output_dir, f"3months_ending_{date_str}.png")
    return generate_chart(start, end, output_path, f"Air Quality - 3 Months Ending {date_str}")

def generate_6month_chart(end_date: datetime, output_dir: str = "/tmp/air_charts") -> str:
    """Generate chart for the last 6 months ending on end_date."""
    end = end_date.replace(hour=23, minute=59, second=59)
    start = end - timedelta(days=180)
    date_str = end_date.strftime('%Y-%m-%d')
    output_path = os.path.join(output_dir, f"6months_ending_{date_str}.png")
    return generate_chart(start, end, output_path, f"Air Quality - 6 Months Ending {date_str}")

def generate_year_chart(year: int, output_dir: str = "/tmp/air_charts") -> str:
    """Generate chart for a specific year."""
    start = datetime(year, 1, 1)
    end = datetime(year + 1, 1, 1)
    output_path = os.path.join(output_dir, f"year_{year}.png")
    return generate_chart(start, end, output_path, f"Air Quality - {year}")

# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate air quality charts')
    parser.add_argument('--day', type=str, help='Generate chart for a specific day (YYYY-MM-DD)')
    parser.add_argument('--week', type=str, help='Generate chart for week ending on date (YYYY-MM-DD)')
    parser.add_argument('--month', type=str, help='Generate chart for a specific month (YYYY-MM)')
    parser.add_argument('--3month', dest='three_month', type=str, help='Generate chart for 3 months ending on date (YYYY-MM-DD)')
    parser.add_argument('--6month', dest='six_month', type=str, help='Generate chart for 6 months ending on date (YYYY-MM-DD)')
    parser.add_argument('--year', type=int, help='Generate chart for a specific year (YYYY)')
    parser.add_argument('--output', type=str, default='/tmp/air_charts', help='Output directory for charts')
    
    args = parser.parse_args()
    
    if args.day:
        date = datetime.strptime(args.day, '%Y-%m-%d')
        generate_day_chart(date, args.output)
    
    elif args.week:
        date = datetime.strptime(args.week, '%Y-%m-%d')
        generate_week_chart(date, args.output)
    
    elif args.month:
        year, month = map(int, args.month.split('-'))
        generate_month_chart(year, month, args.output)
    
    elif args.three_month:
        date = datetime.strptime(args.three_month, '%Y-%m-%d')
        generate_3month_chart(date, args.output)
    
    elif args.six_month:
        date = datetime.strptime(args.six_month, '%Y-%m-%d')
        generate_6month_chart(date, args.output)
    
    elif args.year:
        generate_year_chart(args.year, args.output)
    
    else:
        # Generate chart for today
        generate_day_chart(datetime.now(), args.output)
