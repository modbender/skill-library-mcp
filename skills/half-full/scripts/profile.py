#!/usr/bin/env python3
"""
半饱 - 用户档案管理
"""

import json
import os
import argparse
import math
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def get_profile_path():
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, 'profile.json')

def load_profile():
    path = get_profile_path()
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_profile(profile):
    path = get_profile_path()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

def calc_bmr(height_cm, weight_kg, age, gender='female'):
    """Mifflin-St Jeor公式"""
    if gender == 'male':
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

def calc_expenditure(profile):
    """每日总消耗 = BMR × 活动系数 + 脑力加成"""
    height = profile.get('height_cm', 165)
    weight = profile.get('weight_kg', 58)
    age = profile.get('age', 30)
    gender = profile.get('gender', 'female')
    
    bmr = calc_bmr(height, weight, age, gender)
    
    # 体力活动系数
    work_style = profile.get('work_style', '久坐')
    activity_map = {
        '久坐': 1.2,
        '偶尔走动': 1.35,
        '经常跑动': 1.5,
    }
    activity_factor = activity_map.get(work_style, 1.2)
    
    # 脑力加成
    brain_load = profile.get('brain_load', '日常')
    brain_map = {
        '日常': 0,
        '中度': 100,
        '高强度': 250,
    }
    brain_bonus = brain_map.get(brain_load, 0)
    
    tdee = bmr * activity_factor + brain_bonus
    
    return {
        'bmr': round(bmr),
        'activity_factor': activity_factor,
        'brain_bonus': brain_bonus,
        'tdee': round(tdee),
        'work_style': work_style,
        'brain_load': brain_load,
    }

def cmd_init(args):
    profile = load_profile()
    profile['height_cm'] = args.height
    profile['weight_kg'] = args.weight
    profile['goal'] = args.goal
    profile['gender'] = getattr(args, 'gender', 'female')
    profile['age'] = getattr(args, 'age', 30)
    profile['created_at'] = datetime.now().isoformat()
    profile['updated_at'] = datetime.now().isoformat()
    save_profile(profile)
    
    exp = calc_expenditure(profile)
    
    result = {
        'status': 'ok',
        'goal': args.goal,
        'estimated_tdee': exp['tdee'],
        'bmr': exp['bmr'],
        'message': f'档案建好了。你每天大约消耗{exp["tdee"]}千卡，基础代谢{exp["bmr"]}千卡。',
        'next_step': '可以开始记录饮食了，拍张照就行。'
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_update(args):
    profile = load_profile()
    if not profile:
        print(json.dumps({'status': 'error', 'message': '还没有档案，先用 init 创建'}, ensure_ascii=False))
        return
    
    if args.work_style:
        profile['work_style'] = args.work_style
    if args.brain_load:
        profile['brain_load'] = args.brain_load
    if args.eat_habit:
        profile['eat_habit'] = args.eat_habit
    if args.weight:
        profile['weight_kg'] = args.weight
    if args.age:
        profile['age'] = args.age
    if args.gender:
        profile['gender'] = args.gender
    
    profile['updated_at'] = datetime.now().isoformat()
    save_profile(profile)
    
    exp = calc_expenditure(profile)
    result = {
        'status': 'ok',
        'estimated_tdee': exp['tdee'],
        'message': f'已更新。每日消耗约{exp["tdee"]}千卡（基础代谢{exp["bmr"]} + 活动 + 脑力{exp["brain_bonus"]}）。'
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_expenditure(args):
    profile = load_profile()
    if not profile:
        print(json.dumps({'status': 'error', 'message': '还没有档案'}, ensure_ascii=False))
        return
    
    exp = calc_expenditure(profile)
    
    result = {
        'bmr': exp['bmr'],
        'work_style': exp['work_style'],
        'activity_factor': exp['activity_factor'],
        'brain_load': exp['brain_load'],
        'brain_bonus': exp['brain_bonus'],
        'tdee': exp['tdee'],
        'breakdown': f'基础代谢{exp["bmr"]} × 活动{exp["activity_factor"]} + 脑力{exp["brain_bonus"]} = {exp["tdee"]}千卡/天'
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_show(args):
    profile = load_profile()
    if not profile:
        print(json.dumps({'status': 'error', 'message': '还没有档案'}, ensure_ascii=False))
        return
    print(json.dumps(profile, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='半饱 - 用户档案')
    sub = parser.add_subparsers(dest='cmd')
    
    # init
    p_init = sub.add_parser('init')
    p_init.add_argument('--height', type=float, required=True, help='身高(cm)')
    p_init.add_argument('--weight', type=float, required=True, help='体重(kg)')
    p_init.add_argument('--goal', type=str, default='想瘦一点', help='目标')
    p_init.add_argument('--gender', type=str, default='female', help='性别 male/female')
    p_init.add_argument('--age', type=int, default=30, help='年龄')
    
    # update
    p_update = sub.add_parser('update')
    p_update.add_argument('--work-style', type=str, dest='work_style')
    p_update.add_argument('--brain-load', type=str, dest='brain_load')
    p_update.add_argument('--eat-habit', type=str, dest='eat_habit')
    p_update.add_argument('--weight', type=float)
    p_update.add_argument('--age', type=int)
    p_update.add_argument('--gender', type=str)
    
    # expenditure
    sub.add_parser('expenditure')
    
    # show
    sub.add_parser('show')
    
    args = parser.parse_args()
    
    if args.cmd == 'init':
        cmd_init(args)
    elif args.cmd == 'update':
        cmd_update(args)
    elif args.cmd == 'expenditure':
        cmd_expenditure(args)
    elif args.cmd == 'show':
        cmd_show(args)
    else:
        parser.print_help()
