#!/usr/bin/env python3
"""
Query functions for air quality database.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple

DB_PATH = os.path.expanduser("~/.openclaw/workspace/skills/living-room-air-monitor/data/air_quality.db")

def get_db_connection():
    """Get database connection."""
    return sqlite3.connect(DB_PATH)

def get_reading_by_datetime(dt: datetime) -> Optional[Dict[str, Any]]:
    """
    Get a single reading for a specific datetime.
    Returns the closest reading within 1 hour of the specified time.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    target_str = dt.isoformat()
    one_hour_before = (dt - timedelta(hours=1)).isoformat()
    one_hour_after = (dt + timedelta(hours=1)).isoformat()
    
    cursor.execute('''
        SELECT datetime, temperature, humidity, pm25, co2
        FROM air_quality
        WHERE datetime BETWEEN ? AND ?
        ORDER BY ABS(JULIANDAY(datetime) - JULIANDAY(?))
        LIMIT 1
    ''', (one_hour_before, one_hour_after, target_str))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'datetime': row[0],
            'temperature': row[1],
            'humidity': row[2],
            'pm25': row[3],
            'co2': row[4]
        }
    return None

def get_readings_by_interval(start_dt: datetime, end_dt: datetime) -> List[Dict[str, Any]]:
    """
    Get all readings within a datetime interval (inclusive).
    """
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
            'datetime': row[0],
            'temperature': row[1],
            'humidity': row[2],
            'pm25': row[3],
            'co2': row[4]
        }
        for row in rows
    ]

def get_readings_by_day(date: datetime) -> List[Dict[str, Any]]:
    """
    Get all readings for a specific day.
    """
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return get_readings_by_interval(start, end)

def get_readings_by_month(year: int, month: int) -> List[Dict[str, Any]]:
    """
    Get all readings for a specific month.
    """
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    return get_readings_by_interval(start, end)

def get_average_by_day(date: datetime, metric: str) -> Optional[float]:
    """
    Get the average value for a specific metric on a specific day.
    Metric can be: 'temperature', 'humidity', 'pm25', 'co2'
    """
    valid_metrics = ['temperature', 'humidity', 'pm25', 'co2']
    if metric not in valid_metrics:
        raise ValueError(f"Invalid metric. Must be one of: {valid_metrics}")
    
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(f'''
        SELECT AVG({metric})
        FROM air_quality
        WHERE datetime BETWEEN ? AND ?
    ''', (start.isoformat(), end.isoformat()))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result[0] is not None else None

def get_average_by_month(year: int, month: int, metric: str) -> Optional[float]:
    """
    Get the average value for a specific metric for a specific month.
    Metric can be: 'temperature', 'humidity', 'pm25', 'co2'
    """
    valid_metrics = ['temperature', 'humidity', 'pm25', 'co2']
    if metric not in valid_metrics:
        raise ValueError(f"Invalid metric. Must be one of: {valid_metrics}")
    
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(f'''
        SELECT AVG({metric})
        FROM air_quality
        WHERE datetime BETWEEN ? AND ?
    ''', (start.isoformat(), end.isoformat()))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result[0] is not None else None

def get_all_averages_by_day(date: datetime) -> Optional[Dict[str, float]]:
    """
    Get all average values for a specific day.
    """
    metrics = ['temperature', 'humidity', 'pm25', 'co2']
    result = {}
    
    for metric in metrics:
        avg = get_average_by_day(date, metric)
        if avg is not None:
            result[metric] = round(avg, 2)
    
    return result if result else None

def get_all_averages_by_month(year: int, month: int) -> Optional[Dict[str, float]]:
    """
    Get all average values for a specific month.
    """
    metrics = ['temperature', 'humidity', 'pm25', 'co2']
    result = {}
    
    for metric in metrics:
        avg = get_average_by_month(year, month, metric)
        if avg is not None:
            result[metric] = round(avg, 2)
    
    return result if result else None

def get_date_range() -> Tuple[Optional[str], Optional[str]]:
    """
    Get the date range of available data.
    Returns (earliest, latest) or (None, None) if no data.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT MIN(datetime), MAX(datetime) FROM air_quality')
    result = cursor.fetchone()
    conn.close()
    
    return (result[0], result[1]) if result else (None, None)

# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Query air quality data')
    parser.add_argument('--day', type=str, help='Get readings for a specific day (YYYY-MM-DD)')
    parser.add_argument('--month', type=str, help='Get readings for a specific month (YYYY-MM)')
    parser.add_argument('--avg-day', type=str, help='Get averages for a specific day (YYYY-MM-DD)')
    parser.add_argument('--avg-month', type=str, help='Get averages for a specific month (YYYY-MM)')
    parser.add_argument('--metric', type=str, choices=['temperature', 'humidity', 'pm25', 'co2'],
                        help='Metric for average calculation')
    parser.add_argument('--range', action='store_true', help='Show date range of available data')
    
    args = parser.parse_args()
    
    if args.range:
        earliest, latest = get_date_range()
        print(f"Data available from {earliest} to {latest}")
    
    elif args.day:
        date = datetime.strptime(args.day, '%Y-%m-%d')
        readings = get_readings_by_day(date)
        print(f"Readings for {args.day}:")
        for r in readings:
            print(f"  {r['datetime']}: Temp={r['temperature']:.1f}°C, Hum={r['humidity']:.0f}%, "
                  f"PM2.5={r['pm25']:.0f}, CO2={r['co2']:.0f}")
    
    elif args.month:
        year, month = map(int, args.month.split('-'))
        readings = get_readings_by_month(year, month)
        print(f"Readings for {args.month}:")
        for r in readings:
            print(f"  {r['datetime']}: Temp={r['temperature']:.1f}°C, Hum={r['humidity']:.0f}%, "
                  f"PM2.5={r['pm25']:.0f}, CO2={r['co2']:.0f}")
    
    elif args.avg_day:
        date = datetime.strptime(args.avg_day, '%Y-%m-%d')
        if args.metric:
            avg = get_average_by_day(date, args.metric)
            print(f"Average {args.metric} for {args.avg_day}: {avg:.2f}" if avg else "No data")
        else:
            avgs = get_all_averages_by_day(date)
            print(f"Averages for {args.avg_day}:")
            for metric, value in avgs.items():
                print(f"  {metric}: {value}")
    
    elif args.avg_month:
        year, month = map(int, args.avg_month.split('-'))
        if args.metric:
            avg = get_average_by_month(year, month, args.metric)
            print(f"Average {args.metric} for {args.avg_month}: {avg:.2f}" if avg else "No data")
        else:
            avgs = get_all_averages_by_month(year, month)
            print(f"Averages for {args.avg_month}:")
            for metric, value in avgs.items():
                print(f"  {metric}: {value}")
    
    else:
        parser.print_help()
