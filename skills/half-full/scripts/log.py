#!/usr/bin/env python3
"""
半饱 - 每日饮食记录
"""

import json
import os
import argparse
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def get_log_path(date_str=None):
    os.makedirs(DATA_DIR, exist_ok=True)
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    return os.path.join(DATA_DIR, f'log-{date_str}.json')

def load_log(date_str=None):
    path = get_log_path(date_str)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'date': date_str or datetime.now().strftime('%Y-%m-%d'), 'meals': []}

def save_log(log, date_str=None):
    path = get_log_path(date_str)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def load_profile():
    path = os.path.join(DATA_DIR, 'profile.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def calc_meal_totals(items):
    """计算一餐的营养总量"""
    totals = {'calories': 0, 'protein_g': 0, 'carbs_g': 0, 'fat_g': 0}
    for item in items:
        totals['calories'] += item.get('calories', 0)
        totals['protein_g'] += item.get('protein_g', 0)
        totals['carbs_g'] += item.get('carbs_g', 0)
        totals['fat_g'] += item.get('fat_g', 0)
    return totals

def calc_day_totals(log):
    """计算全天营养总量"""
    totals = {'calories': 0, 'protein_g': 0, 'carbs_g': 0, 'fat_g': 0, 'meal_count': 0}
    for meal in log.get('meals', []):
        meal_totals = calc_meal_totals(meal.get('items', []))
        totals['calories'] += meal_totals['calories']
        totals['protein_g'] += meal_totals['protein_g']
        totals['carbs_g'] += meal_totals['carbs_g']
        totals['fat_g'] += meal_totals['fat_g']
        totals['meal_count'] += 1
    return totals

def enrich_items_from_db(items):
    """用food_db为每个食材补充营养数据"""
    try:
        from food_db import FOODS
    except ImportError:
        return items
    
    for item in items:
        if item.get('calories'):
            continue  # 已有营养数据，跳过
        name = item.get('name', '')
        amount = item.get('amount_g', 100)
        
        # 在FOODS字典里模糊匹配
        matched_name = None
        matched_data = None
        for food_name, food_data in FOODS.items():
            if food_name in name or name in food_name:
                matched_name = food_name
                matched_data = food_data
                break
            if food_data.get('en', '').lower() in name.lower() and food_data.get('en'):
                matched_name = food_name
                matched_data = food_data
                break
        
        if matched_data:
            ratio = amount / 100.0
            item['calories'] = round(matched_data['calories'] * ratio)
            item['protein_g'] = round(matched_data['protein'] * ratio, 1)
            item['carbs_g'] = round(matched_data['carbs'] * ratio, 1)
            item['fat_g'] = round(matched_data['fat'] * ratio, 1)
            item['matched_food'] = matched_name
    
    return items

def cmd_add(args):
    log = load_log()
    
    items = json.loads(args.items) if args.items else []
    items = enrich_items_from_db(items)
    
    meal = {
        'type': args.meal,
        'time': datetime.now().strftime('%H:%M'),
        'items': items,
        'note': args.note or '',
        'photo': args.photo or '',
    }
    
    meal_totals = calc_meal_totals(items)
    meal['totals'] = meal_totals
    
    log['meals'].append(meal)
    save_log(log)
    
    day_totals = calc_day_totals(log)
    
    result = {
        'status': 'ok',
        'meal': args.meal,
        'meal_calories': meal_totals['calories'],
        'meal_protein': meal_totals['protein_g'],
        'day_so_far': {
            'calories': day_totals['calories'],
            'protein_g': day_totals['protein_g'],
            'carbs_g': day_totals['carbs_g'],
            'fat_g': day_totals['fat_g'],
            'meals': day_totals['meal_count'],
        }
    }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_today(args):
    log = load_log()
    day_totals = calc_day_totals(log)
    profile = load_profile()
    
    # 简单算tdee
    tdee = None
    if profile.get('weight_kg') and profile.get('height_cm'):
        from profile import calc_expenditure
        exp = calc_expenditure(profile)
        tdee = exp['tdee']
    
    result = {
        'date': log.get('date', datetime.now().strftime('%Y-%m-%d')),
        'meals': [],
        'totals': day_totals,
        'tdee': tdee,
    }
    
    for meal in log.get('meals', []):
        result['meals'].append({
            'type': meal['type'],
            'time': meal.get('time', ''),
            'note': meal.get('note', ''),
            'calories': meal.get('totals', {}).get('calories', 0),
            'protein_g': meal.get('totals', {}).get('protein_g', 0),
        })
    
    if tdee:
        remaining = tdee - day_totals['calories']
        if remaining > 0:
            result['message'] = f'今天还可以吃约{remaining}千卡，不急。'
        elif remaining > -200:
            result['message'] = '今天吃得刚刚好。'
        else:
            result['message'] = '今天吃得丰盛了点，明天清淡点就平衡了，没事。'
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_week(args):
    days = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=6-i)).strftime('%Y-%m-%d')
        log = load_log(date)
        totals = calc_day_totals(log)
        days.append({
            'date': date,
            'calories': totals['calories'],
            'protein_g': totals['protein_g'],
            'meals': totals['meal_count'],
        })
    
    total_cal = sum(d['calories'] for d in days)
    active_days = sum(1 for d in days if d['meals'] > 0)
    avg_cal = round(total_cal / active_days) if active_days > 0 else 0
    
    result = {
        'days': days,
        'summary': {
            'total_calories': total_cal,
            'active_days': active_days,
            'avg_daily_calories': avg_cal,
        }
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_delete(args):
    log = load_log()
    idx = args.index
    if 0 <= idx < len(log.get('meals', [])):
        removed = log['meals'].pop(idx)
        save_log(log)
        print(json.dumps({'status': 'ok', 'removed': removed.get('type', ''), 'note': removed.get('note', '')}, ensure_ascii=False))
    else:
        print(json.dumps({'status': 'error', 'message': f'没有第{idx}条记录'}, ensure_ascii=False))

def get_weight_path():
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, 'weight.json')

def load_weight_log():
    path = get_weight_path()
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'records': []}

def save_weight_log(data):
    path = get_weight_path()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def cmd_weight(args):
    data = load_weight_log()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 更新或追加
    updated = False
    for r in data['records']:
        if r['date'] == today:
            r['kg'] = args.kg
            updated = True
            break
    if not updated:
        data['records'].append({'date': today, 'kg': args.kg})
    
    data['records'].sort(key=lambda x: x['date'])
    save_weight_log(data)
    
    result = {'status': 'ok', 'date': today, 'kg': args.kg}
    
    # 跟上次比
    if len(data['records']) >= 2:
        prev = data['records'][-2]
        diff = round(args.kg - prev['kg'], 1)
        result['prev_date'] = prev['date']
        result['prev_kg'] = prev['kg']
        result['change'] = diff
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_weight_trend(args):
    data = load_weight_log()
    records = data.get('records', [])
    
    if not records:
        print(json.dumps({'status': 'ok', 'message': '还没有体重记录'}, ensure_ascii=False))
        return
    
    result = {
        'total_records': len(records),
        'first': records[0],
        'latest': records[-1],
        'records': records[-10:],  # 最近10条
    }
    
    if len(records) >= 2:
        result['total_change'] = round(records[-1]['kg'] - records[0]['kg'], 1)
        
        # 最近30天的记录算月均
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        recent = [r for r in records if r['date'] >= thirty_days_ago]
        if recent:
            result['month_avg'] = round(sum(r['kg'] for r in recent) / len(recent), 1)
    
    # 上次称重距今多少天
    last_date = datetime.strptime(records[-1]['date'], '%Y-%m-%d')
    days_since = (datetime.now() - last_date).days
    result['days_since_last'] = days_since
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='半饱 - 饮食记录')
    sub = parser.add_subparsers(dest='cmd')
    
    # add
    p_add = sub.add_parser('add')
    p_add.add_argument('--meal', type=str, required=True, choices=['breakfast', 'lunch', 'dinner', 'snack'], help='餐次')
    p_add.add_argument('--items', type=str, required=True, help='食材JSON数组')
    p_add.add_argument('--photo', type=str, default='')
    p_add.add_argument('--note', type=str, default='')
    
    # today
    sub.add_parser('today')
    
    # week
    sub.add_parser('week')
    
    # delete
    p_del = sub.add_parser('delete')
    p_del.add_argument('--index', type=int, required=True, help='删除第几条(从0开始)')
    
    # weight
    p_weight = sub.add_parser('weight')
    p_weight.add_argument('--kg', type=float, required=True, help='体重(kg)')
    
    # weight-trend
    sub.add_parser('weight-trend')
    
    args = parser.parse_args()
    
    if args.cmd == 'add':
        cmd_add(args)
    elif args.cmd == 'today':
        cmd_today(args)
    elif args.cmd == 'week':
        cmd_week(args)
    elif args.cmd == 'delete':
        cmd_delete(args)
    elif args.cmd == 'weight':
        cmd_weight(args)
    elif args.cmd == 'weight-trend':
        cmd_weight_trend(args)
    else:
        parser.print_help()
