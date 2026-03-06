#!/usr/bin/env python3
"""
小饭卡 - 新用户引导
交互式建立初始口味画像。

用法（Agent调用，非用户直接运行）:
  python3 onboard.py init --city 北京 --areas "三里屯,工体"
  python3 onboard.py add-fav "鲤承" --reason "精致，有调性，菜品有创意"
  python3 onboard.py add-dislike "小吊梨汤" --reason "味道一般，太连锁"
  python3 onboard.py finish

设计说明:
  onboarding不是用户自己跑的CLI，而是Agent按步骤调用的。
  Agent负责对话引导，这个脚本负责数据写入。
  
  流程:
  1. Agent问用户在哪吃饭 → 调 init
  2. Agent问喜欢的店 → 每家调 add-fav（Agent先搜索确认再调）
  3. Agent问不喜欢的 → 调 add-dislike（可选）
  4. Agent调 finish → 生成画像分析 + 输出推荐搜索词
"""

import sys
import json
import argparse
import os
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / 'data'
PROFILE_PATH = DATA_DIR / 'taste-profile.json'


def load_profile() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if PROFILE_PATH.exists():
        with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'user': {}, 'restaurants': [], 'preferences': {}, 'updated_at': None}


def save_profile(profile: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    profile['updated_at'] = datetime.now().isoformat()
    with open(PROFILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


def cmd_init(args):
    """初始化用户基本信息"""
    profile = load_profile()
    areas = [a.strip() for a in args.areas.split(',') if a.strip()] if args.areas else []
    
    profile['user'] = {
        'city': args.city,
        'areas': areas,
        'onboarded': False,
        'created_at': datetime.now().isoformat(),
    }
    save_profile(profile)
    
    result = {
        'status': 'ok',
        'city': args.city,
        'areas': areas,
        'next_step': 'ask_favorites',
        'prompt': f'用户在{args.city}，常去{",".join(areas)}。接下来问用户喜欢的3-5家餐厅。',
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_add_fav(args):
    """添加一家喜欢的餐厅（含原因分析）"""
    profile = load_profile()
    
    # 从reason中提取标签
    tags = extract_tags(args.reason) if args.reason else []
    
    # 检查是否已存在
    existing = next((r for r in profile['restaurants'] if r['name'] == args.name), None)
    if existing:
        existing['tags'] = list(set(existing.get('tags', []) + tags))
        existing['feeling'] = '喜欢'
        if args.reason:
            existing['notes'] = args.reason
        if args.price:
            existing['avg_price'] = args.price
        if args.area:
            existing['area'] = args.area
        existing['updated_at'] = datetime.now().isoformat()
    else:
        entry = {
            'name': args.name,
            'tags': tags,
            'feeling': '喜欢',
            'avg_price': args.price,
            'area': args.area,
            'city': profile.get('user', {}).get('city'),
            'notes': args.reason,
            'source': 'onboarding',
            'visits': 1,
            'added_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }
        profile['restaurants'].append(entry)
    
    save_profile(profile)
    
    fav_count = sum(1 for r in profile['restaurants'] if r.get('feeling') == '喜欢')
    
    result = {
        'status': 'ok',
        'name': args.name,
        'tags_extracted': tags,
        'total_favorites': fav_count,
        'enough': fav_count >= 3,
        'next_step': 'ask_more_or_dislikes' if fav_count >= 3 else 'ask_more_favorites',
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_add_dislike(args):
    """添加不喜欢的餐厅/类型"""
    profile = load_profile()
    
    tags = extract_tags(args.reason) if args.reason else []
    
    existing = next((r for r in profile['restaurants'] if r['name'] == args.name), None)
    if existing:
        existing['feeling'] = '不喜欢'
        existing['tags'] = list(set(existing.get('tags', []) + tags))
        if args.reason:
            existing['notes'] = args.reason
        existing['updated_at'] = datetime.now().isoformat()
    else:
        entry = {
            'name': args.name,
            'tags': tags,
            'feeling': '不喜欢',
            'avg_price': None,
            'area': None,
            'city': profile.get('user', {}).get('city'),
            'notes': args.reason,
            'source': 'onboarding',
            'visits': 0,
            'added_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }
        profile['restaurants'].append(entry)
    
    save_profile(profile)
    print(json.dumps({'status': 'ok', 'name': args.name, 'feeling': '不喜欢'}, ensure_ascii=False))


def cmd_finish(args):
    """完成引导，生成画像分析和推荐搜索词"""
    profile = load_profile()
    profile['user']['onboarded'] = True
    profile['user']['onboarded_at'] = datetime.now().isoformat()
    
    # 分析画像
    liked = [r for r in profile['restaurants'] if r.get('feeling') in ('喜欢', '常去')]
    disliked = [r for r in profile['restaurants'] if r.get('feeling') == '不喜欢']
    
    # 收集标签
    liked_tags = {}
    for r in liked:
        for tag in r.get('tags', []):
            liked_tags[tag] = liked_tags.get(tag, 0) + 1
    
    disliked_tags = {}
    for r in disliked:
        for tag in r.get('tags', []):
            disliked_tags[tag] = disliked_tags.get(tag, 0) + 1
    
    # 价位
    prices = [r['avg_price'] for r in liked if r.get('avg_price')]
    
    # 区域
    areas = {}
    for r in liked:
        area = r.get('area')
        if area:
            areas[area] = areas.get(area, 0) + 1
    
    top_tags = sorted(liked_tags.items(), key=lambda x: x[1], reverse=True)[:8]
    top_tag_names = [t for t, _ in top_tags]
    top_areas = sorted(areas.items(), key=lambda x: x[1], reverse=True)[:3]
    top_area_names = [a for a, _ in top_areas]
    
    # 保存偏好
    profile['preferences'] = {
        'liked_tags': top_tag_names,
        'disliked_tags': list(disliked_tags.keys()),
        'avg_price': round(sum(prices) / len(prices)) if prices else None,
        'price_range': [min(prices), max(prices)] if prices else None,
        'top_areas': top_area_names,
        'total_restaurants': len(profile['restaurants']),
        'analyzed_at': datetime.now().isoformat(),
    }
    save_profile(profile)
    
    # 生成推荐搜索词
    city = profile.get('user', {}).get('city', '')
    search_suggestions = []
    if top_area_names and top_tag_names:
        for area in top_area_names[:2]:
            for tag in top_tag_names[:3]:
                search_suggestions.append(f"{area} {tag}")
    
    result = {
        'status': 'onboarding_complete',
        'summary': {
            'liked_count': len(liked),
            'disliked_count': len(disliked),
            'top_tags': top_tag_names,
            'disliked_tags': list(disliked_tags.keys()),
            'avg_price': profile['preferences']['avg_price'],
            'top_areas': top_area_names,
        },
        'search_suggestions': search_suggestions[:6],
        'next_step': 'recommend_3_restaurants',
        'prompt': f'画像建好了。用search_all.py搜索以下关键词，挑3家最匹配的推荐给用户：{search_suggestions[:3]}',
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def extract_tags(text: str) -> list:
    """从自然语言描述中提取标签"""
    tag_map = {
        # 菜系
        '中餐': ['中餐', '中式', '国菜'],
        '日料': ['日料', '日本', '寿司', '刺身', '居酒屋', '日式'],
        '西餐': ['西餐', '法餐', '意大利', '牛排', '西式'],
        '火锅': ['火锅', '涮'],
        '烧烤': ['烧烤', '烤肉', '串', '炙子'],
        '川菜': ['川菜', '四川', '麻辣'],
        '湘菜': ['湘菜', '湖南'],
        '粤菜': ['粤菜', '广东', '广式', '港式', '茶餐厅'],
        '云南菜': ['云南', '滇'],
        '贵州菜': ['贵州', '黔'],
        '潮汕': ['潮汕', '潮州', '汕头'],
        '素食': ['素食', '素菜', '蔬食'],
        '东南亚': ['泰国', '越南', '东南亚', '泰餐'],
        '韩餐': ['韩国', '韩餐', '韩式'],
        '创意菜': ['创意', '融合', '新派'],
        '私房菜': ['私房', '私厨'],
        # 风格
        '精致小馆': ['精致', '小馆', '小店'],
        '有调性': ['调性', '格调', '氛围', '环境好', '装修好'],
        '性价比': ['性价比', '便宜', '实惠', '划算'],
        '老字号': ['老字号', '老店', '传统', '经典'],
        '网红': ['网红', '打卡', '拍照'],
        '接地气': ['接地气', '苍蝇馆子', '市井', '烟火气'],
        '有特色': ['特色', '独特', '有意思', '创意', '与众不同'],
        'Bistro': ['bistro', 'Bistro', '小酒馆'],
        # 场景
        '请客': ['请客', '商务', '宴请', '正式'],
        '约会': ['约会', '情侣', '浪漫'],
        '家庭': ['家庭', '带孩子', '亲子', '适合小孩'],
        '朋友聚餐': ['聚餐', '朋友', '几个人'],
        '一人食': ['一人', '一个人', '独食'],
        # 特点
        '排队': ['排队', '等位'],
        '有酒': ['酒', '微醺', '鸡尾酒', '清酒'],
        '适合减脂': ['减脂', '低卡', '健康', '轻食'],
        '香料': ['香料', '香草', '薄荷', '罗勒'],
        '自然烹饪': ['自然', '原生态', '天然', '土菜'],
    }
    
    tags = []
    text_lower = text.lower()
    for tag, keywords in tag_map.items():
        if any(kw.lower() in text_lower for kw in keywords):
            tags.append(tag)
    
    return tags


def main():
    parser = argparse.ArgumentParser(description='小饭卡 - 新用户引导')
    sub = parser.add_subparsers(dest='command')
    
    # init
    init_p = sub.add_parser('init', help='初始化')
    init_p.add_argument('--city', required=True, help='城市')
    init_p.add_argument('--areas', default='', help='常去区域，逗号分隔')
    
    # add-fav
    fav_p = sub.add_parser('add-fav', help='添加喜欢的店')
    fav_p.add_argument('name', help='餐厅名')
    fav_p.add_argument('--reason', help='为什么喜欢')
    fav_p.add_argument('--price', type=int, help='人均')
    fav_p.add_argument('--area', help='区域')
    
    # add-dislike
    dis_p = sub.add_parser('add-dislike', help='添加不喜欢的')
    dis_p.add_argument('name', help='餐厅/类型名')
    dis_p.add_argument('--reason', help='为什么不喜欢')
    
    # finish
    sub.add_parser('finish', help='完成引导')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        cmd_init(args)
    elif args.command == 'add-fav':
        cmd_add_fav(args)
    elif args.command == 'add-dislike':
        cmd_add_dislike(args)
    elif args.command == 'finish':
        cmd_finish(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
