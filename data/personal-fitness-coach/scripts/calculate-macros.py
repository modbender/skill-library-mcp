#!/usr/bin/env python3
"""
Calculate daily macro totals from log file
Usage: calculate-macros.py --date 2026-03-01
"""

import argparse
import json
from pathlib import Path

def get_log_path(date):
    base = Path.home() / '.openclaw' / 'workspace' / 'fitness' / 'logs'
    return base / f"{date}.json"

def main():
    parser = argparse.ArgumentParser(description='Calculate daily macros')
    parser.add_argument('--date', required=True, help='Date YYYY-MM-DD')
    
    args = parser.parse_args()
    
    path = get_log_path(args.date)
    if not path.exists():
        print(f"No log found for {args.date}")
        return
    
    with open(path) as f:
        log = json.load(f)
    
    totals = {"protein": 0, "carbs": 0, "fat": 0, "calories": 0}
    skipped = []
    
    for meal in log.get('meals', []):
        if meal.get('skipped'):
            skipped.append(meal['meal'])
        else:
            totals['protein'] += meal.get('protein', 0)
            totals['carbs'] += meal.get('carbs', 0)
            totals['fat'] += meal.get('fat', 0)
            totals['calories'] += meal.get('calories', 0)
    
    print(f"\n📊 Daily Summary for {args.date}")
    print(f"{'─' * 40}")
    print(f"Protein:  {totals['protein']:.1f}g")
    print(f"Carbs:    {totals['carbs']:.1f}g")
    print(f"Fat:      {totals['fat']:.1f}g")
    print(f"Calories: {totals['calories']}")
    
    if skipped:
        print(f"\n⚠️ Skipped meals: {', '.join(skipped)}")

if __name__ == '__main__':
    main()
