#!/usr/bin/env python3
"""
Calorie Visualizer CLI v1.1
Enhanced with User Profile logic and advanced reporting.
"""

import argparse
import sqlite3
import os
import sys
import re
import subprocess
import json
from urllib import parse, request
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'calorie_data.db')
WORKSPACE_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))
USER_MD_PATH = os.getenv('CALORIE_VIS_USER_MD', os.path.join(WORKSPACE_DIR, 'USER.md'))
VISUAL_RENDERER_PATH = os.path.join(BASE_DIR, 'scripts', 'visual_renderer.py')
DAILY_REPORT_PATH = os.path.join(BASE_DIR, 'daily_report.png')
FOOD_DB_PATH = os.path.join(BASE_DIR, 'data', 'food_database.json')
USDA_API_KEY = os.getenv('USDA_API_KEY', '').strip()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Entries
    c.execute('''CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        food_name TEXT,
        calories INTEGER,
        protein INTEGER,
        photo_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    # User Profile & Config
    c.execute('''CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    # Weight log
    c.execute('''CREATE TABLE IF NOT EXISTS weight_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        weight_kg REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def get_config(key, default=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM config WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default

def set_config(key, value):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

def parse_user_md():
    """Extract physical info from USER.md"""
    if not os.path.exists(USER_MD_PATH):
        return None
    
    try:
        with open(USER_MD_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        info = {}
        # Simple regex extractors
        height = re.search(r"(?:身高|Height)[:：]\s*(\d+)", content)
        weight = re.search(r"(?:体重|Weight)[:：]\s*(\d+(?:\.\d+)?)", content)
        age = re.search(r"(?:年龄|Age)[:：]\s*(\d+)", content)
        gender = re.search(r"(?:性别|Gender)[:：]\s*(男|女|Male|Female)", content)
        
        if height: info['height'] = float(height.group(1))
        if weight: info['weight'] = float(weight.group(1))
        if age: info['age'] = int(age.group(1))
        if gender: info['gender'] = 'male' if gender.group(1) in ['男', 'Male'] else 'female'
        
        return info if len(info) >= 4 else None
    except Exception:
        return None

def calculate_tdee(profile):
    """Mifflin-St Jeor Formula"""
    if not profile or not all(k in profile for k in ['height', 'weight', 'age', 'gender']):
        return None
    
    if profile['gender'] == 'male':
        bmr = 10 * profile['weight'] + 6.25 * profile['height'] - 5 * profile['age'] + 5
    else:
        bmr = 10 * profile['weight'] + 6.25 * profile['height'] - 5 * profile['age'] - 161
    
    # Default to Sedentary (1.2) if activity level not found
    return bmr * 1.2

def get_daily_target():
    # 1. Check if manually set
    manual_goal = get_config('daily_goal')
    if manual_goal: return int(manual_goal)
    
    # 2. Try USER.md
    profile = parse_user_md()
    if profile:
        return calculate_tdee(profile)
    
    # 3. Check if user refused
    if get_config('user_refused_profile') == 'True':
        return None
    
    return "ASK_USER"

def normalize_food_db(raw):
    """Support both legacy dict format and new structured format."""
    if isinstance(raw, dict) and isinstance(raw.get('foods'), list):
        return raw

    # legacy: {name: {calories, protein, fat, carbs}}
    foods = []
    if isinstance(raw, dict):
        for name, v in raw.items():
            if not isinstance(v, dict):
                continue
            foods.append({
                'name': name,
                'aliases': [],
                'unit': 'serving',
                'calories': v.get('calories', 0),
                'protein': v.get('protein', 0),
                'fat': v.get('fat', 0),
                'carbs': v.get('carbs', 0),
                'source': v.get('source', 'legacy.local'),
                'country': v.get('country', 'unknown')
            })
    return {'schema_version': '1.0', 'foods': foods}


def load_food_database():
    if not os.path.exists(FOOD_DB_PATH):
        return {'schema_version': '1.0', 'foods': []}
    try:
        with open(FOOD_DB_PATH, 'r', encoding='utf-8') as f:
            return normalize_food_db(json.load(f))
    except Exception:
        return {'schema_version': '1.0', 'foods': []}


def save_food_database(db):
    os.makedirs(os.path.dirname(FOOD_DB_PATH), exist_ok=True)
    with open(FOOD_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def _norm(s):
    return re.sub(r'\s+', '', (s or '').strip().lower())


def find_food_nutrition(food_name):
    db = load_food_database()
    foods = db.get('foods', [])
    if not foods:
        return None, None

    q = _norm(food_name)
    # exact over name/aliases
    for item in foods:
        names = [item.get('name', '')] + item.get('aliases', [])
        for n in names:
            if _norm(n) == q:
                return item.get('name', food_name), item

    # fuzzy contains
    for item in foods:
        names = [item.get('name', '')] + item.get('aliases', [])
        for n in names:
            nn = _norm(n)
            if nn and (nn in q or q in nn):
                return item.get('name', food_name), item

    return None, None


def fetch_food_online(food_name):
    """Online fallback via USDA search API. Requires USDA_API_KEY."""
    if not USDA_API_KEY:
        return None

    try:
        q = parse.quote(food_name)
        url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={q}&pageSize=1&api_key={USDA_API_KEY}"
        with request.urlopen(url, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8', errors='ignore'))

        foods = data.get('foods') or []
        if not foods:
            return None

        top = foods[0]
        nutrient_map = {}
        for n in top.get('foodNutrients', []):
            name = n.get('nutrientName', '')
            val = n.get('value', 0)
            nutrient_map[name] = val

        item = {
            'name': top.get('description', food_name),
            'aliases': [food_name],
            'unit': '100g',
            'calories': float(nutrient_map.get('Energy', 0) or 0),
            'protein': float(nutrient_map.get('Protein', 0) or 0),
            'fat': float(nutrient_map.get('Total lipid (fat)', 0) or 0),
            'carbs': float(nutrient_map.get('Carbohydrate, by difference', 0) or 0),
            'source': 'usda.api',
            'country': 'US'
        }
        return item
    except Exception:
        return None


def upsert_food_database_item(item):
    db = load_food_database()
    foods = db.setdefault('foods', [])
    target = _norm(item.get('name', ''))
    replaced = False
    for i, old in enumerate(foods):
        if _norm(old.get('name', '')) == target:
            foods[i] = item
            replaced = True
            break
    if not replaced:
        foods.append(item)
    db['schema_version'] = '1.1'
    save_food_database(db)


def add_entry(food_name, calories, protein, photo_path=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    date = datetime.now().strftime('%Y-%m-%d')
    c.execute("INSERT INTO entries (date, food_name, calories, protein, photo_path) VALUES (?, ?, ?, ?, ?)",
              (date, food_name, calories, protein, photo_path))
    conn.commit()
    conn.close()
    
    # Show feedback
    target = get_daily_target()
    print(f"✓ Logged: {food_name} ({calories} kcal, {protein}g protein)")
    
    if target == "ASK_USER":
        print("\n[!] Missing profile data (height/weight/age/gender). Unable to compute a daily calorie target.")
        print("Please add details to USER.md, or share them directly. If you prefer not to provide profile data, set user_refused_profile=True.")
    elif isinstance(target, (int, float)):
        summary_today(target)

    # Auto-generate updated report image after logging
    render_report_image()

def add_from_food_database(food_name, multiplier=1.0, photo_path=None, allow_online=True):
    matched_name, item = find_food_nutrition(food_name)

    # online fallback
    if not item and allow_online:
        online_item = fetch_food_online(food_name)
        if online_item:
            upsert_food_database_item(online_item)
            item = online_item
            matched_name = online_item.get('name', food_name)
            print(f"[i] Local DB miss. Fetched online and cached: {matched_name}")

    if not item:
        print(f"[!] Food not found in local database: {food_name}")
        if not USDA_API_KEY:
            print("[i] Tip: set USDA_API_KEY to enable online fallback")
        return

    cal = int(round(float(item.get('calories', 0)) * multiplier))
    pro = int(round(float(item.get('protein', 0)) * multiplier))
    add_entry(matched_name, cal, pro, photo_path)
    src = item.get('source', 'food_database')
    print(f"[i] Source: {src} | Base item: {matched_name} | Multiplier: {multiplier}")


def summary_today(target=None):
    if target is None:
        target = get_daily_target()
        if target == "ASK_USER": target = None
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    date = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT SUM(calories), SUM(protein) FROM entries WHERE date = ?", (date,))
    row = c.fetchone()
    conn.close()
    
    total_cal = row[0] if row[0] else 0
    total_pro = row[1] if row[1] else 0
    
    print(f"\n--- Daily Summary ({date}) ---")
    if target and isinstance(target, (int, float)):
        remaining = target - total_cal
        percent = (total_cal / target) * 100
        print(f"Calories: {total_cal:.0f} / {target:.0f} kcal ({percent:.1f}%)")
        print(f"Remaining: {remaining:.0f} kcal")
    else:
        print(f"Total intake today: {total_cal} kcal")
    
    print(f"Total protein today: {total_pro}g")

def render_report_image():
    if not os.path.exists(VISUAL_RENDERER_PATH):
        print("[!] visual_renderer.py not found, skipping report image generation")
        return None

    try:
        result = subprocess.run(
            [sys.executable, VISUAL_RENDERER_PATH],
            capture_output=True,
            text=True,
            check=False,
        )

        output = (result.stdout or "") + "\n" + (result.stderr or "")
        image_path = None

        for line in output.splitlines():
            if line.startswith("IMAGE_PATH:"):
                image_path = line.split("IMAGE_PATH:", 1)[1].strip()
                break

        if not image_path and os.path.exists(DAILY_REPORT_PATH):
            image_path = DAILY_REPORT_PATH

        if image_path and os.path.exists(image_path):
            print(f"REPORT_IMAGE:{image_path}")
            return image_path

        print("[!] Report image generation failed (output file not found)")
        return None
    except Exception as e:
        print(f"[!] Report image generation error: {e}")
        return None


def generate_report():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(1) FROM entries")
    total_count = c.fetchone()[0]
    conn.close()

    if total_count <= 0:
        print("No data available to generate a report.")
        return

    image_path = render_report_image()
    if image_path:
        print("✓ Visual report generated")


def main():
    init_db()
    parser = argparse.ArgumentParser(description='Calorie Visualizer CLI')
    subparsers = parser.add_subparsers(dest='command')

    # Add
    add_p = subparsers.add_parser('add')
    add_p.add_argument('food')
    add_p.add_argument('cal', type=int)
    add_p.add_argument('pro', type=int)
    add_p.add_argument('--photo', help='Photo path')

    # Add from local food database
    add_food_p = subparsers.add_parser('add-food')
    add_food_p.add_argument('food')
    add_food_p.add_argument('--multiplier', type=float, default=1.0)
    add_food_p.add_argument('--photo', help='Photo path')
    add_food_p.add_argument('--offline', action='store_true', help='Use local database only (disable online fallback)')

    # Summary
    subparsers.add_parser('summary')
    
    # Report
    subparsers.add_parser('report')

    # Config
    conf_p = subparsers.add_parser('config')
    conf_p.add_argument('key')
    conf_p.add_argument('value')

    args = parser.parse_args()

    if args.command == 'add':
        add_entry(args.food, args.cal, args.pro, args.photo)
    elif args.command == 'add-food':
        add_from_food_database(args.food, args.multiplier, args.photo, allow_online=not args.offline)
    elif args.command == 'summary':
        summary_today()
    elif args.command == 'report':
        generate_report()
    elif args.command == 'config':
        set_config(args.key, args.value)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
