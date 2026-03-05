#!/usr/bin/env python3
"""
Log workout to daily file
Usage: log-workout.py --date 2026-03-01 --exercise "bench" --weight 20 --sets "12,12,10" --notes "felt good"
"""

import argparse
import os
import json
from datetime import datetime
from pathlib import Path

def parse_sets(sets_str):
    """Parse '12,12,10' into list [12,12,10]"""
    return [int(x.strip()) for x in sets_str.split(',')]

def calculate_volume(weight, reps_list):
    """Calculate total volume (weight × total reps)"""
    return weight * sum(reps_list)

def get_log_path(date):
    """Get path to daily log file"""
    base = Path.home() / '.openclaw' / 'workspace' / 'fitness' / 'logs'
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{date}.json"

def load_log(date):
    """Load existing log or create new"""
    path = get_log_path(date)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"date": date, "workouts": [], "meals": []}

def save_log(date, data):
    """Save log to file"""
    path = get_log_path(date)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Log a workout')
    parser.add_argument('--date', required=True, help='Date YYYY-MM-DD')
    parser.add_argument('--exercise', required=True, help='Exercise name')
    parser.add_argument('--weight', type=float, required=True, help='Weight in kg')
    parser.add_argument('--sets', required=True, help='Reps per set, comma separated (e.g., 12,12,10)')
    parser.add_argument('--notes', default='', help='Optional notes')
    
    args = parser.parse_args()
    
    reps_list = parse_sets(args.sets)
    volume = calculate_volume(args.weight, reps_list)
    
    log = load_log(args.date)
    
    workout_entry = {
        "exercise": args.exercise,
        "weight": args.weight,
        "sets": len(reps_list),
        "reps": reps_list,
        "total_reps": sum(reps_list),
        "volume": volume,
        "notes": args.notes,
        "timestamp": datetime.now().isoformat()
    }
    
    log['workouts'].append(workout_entry)
    save_log(args.date, log)
    
    print(f"✓ Logged: {args.exercise} {args.weight}kg × {args.sets}")
    print(f"  Volume: {volume} kg")
    print(f"  Total reps: {sum(reps_list)}")

if __name__ == '__main__':
    main()
