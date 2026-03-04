#!/usr/bin/env python3
"""
Log meal to daily file with macro calculation
Usage: log-meal.py --date 2026-03-01 --meal "lunch" --food "200g chicken, 100g rice, salad" --protein 50 --carbs 35 --fat 10 --calories 410
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

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
    parser = argparse.ArgumentParser(description='Log a meal')
    parser.add_argument('--date', required=True, help='Date YYYY-MM-DD')
    parser.add_argument('--meal', required=True, help='Meal type (breakfast, lunch, dinner, snack)')
    parser.add_argument('--food', required=True, help='Description of food')
    parser.add_argument('--protein', type=float, default=0, help='Protein in grams')
    parser.add_argument('--carbs', type=float, default=0, help='Carbs in grams')
    parser.add_argument('--fat', type=float, default=0, help='Fat in grams')
    parser.add_argument('--calories', type=int, default=0, help='Total calories')
    parser.add_argument('--skipped', action='store_true', help='Mark meal as skipped')
    
    args = parser.parse_args()
    
    log = load_log(args.date)
    
    meal_entry = {
        "meal": args.meal,
        "food": args.food,
        "protein": args.protein,
        "carbs": args.carbs,
        "fat": args.fat,
        "calories": args.calories,
        "skipped": args.skipped,
        "timestamp": datetime.now().isoformat()
    }
    
    log['meals'].append(meal_entry)
    save_log(args.date, log)
    
    if args.skipped:
        print(f"⚠ Logged skipped meal: {args.meal}")
    else:
        print(f"✓ Logged {args.meal}: {args.food}")
        print(f"  Macros: P:{args.protein}g C:{args.carbs}g F:{args.fat}g")
        print(f"  Calories: {args.calories}")

if __name__ == '__main__':
    main()
