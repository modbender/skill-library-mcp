#!/usr/bin/env python3
"""
半饱 - 食物营养数据库（USDA简化版）
常用食物的每100g营养数据，中英文支持
"""

import json
import os
import argparse

# 常用食物数据库（每100g）
# 来源：USDA FoodData Central 简化
FOODS = {
    # 肉类
    "鸡胸肉": {"en": "chicken breast", "calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
    "牛肉": {"en": "beef", "calories": 250, "protein": 26, "carbs": 0, "fat": 15},
    "猪肉": {"en": "pork", "calories": 242, "protein": 27, "carbs": 0, "fat": 14},
    "三文鱼": {"en": "salmon", "calories": 208, "protein": 20, "carbs": 0, "fat": 13},
    "虾仁": {"en": "shrimp", "calories": 99, "protein": 24, "carbs": 0.2, "fat": 0.3},
    "鸡蛋": {"en": "egg", "calories": 155, "protein": 13, "carbs": 1.1, "fat": 11},
    "鸡腿肉": {"en": "chicken thigh", "calories": 209, "protein": 26, "carbs": 0, "fat": 11},
    "牛腱子": {"en": "beef shank", "calories": 150, "protein": 28, "carbs": 0, "fat": 4},
    "鳕鱼": {"en": "cod", "calories": 82, "protein": 18, "carbs": 0, "fat": 0.7},
    
    # 蔬菜
    "西兰花": {"en": "broccoli", "calories": 34, "protein": 2.8, "carbs": 7, "fat": 0.4},
    "菠菜": {"en": "spinach", "calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4},
    "番茄": {"en": "tomato", "calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2},
    "黄瓜": {"en": "cucumber", "calories": 15, "protein": 0.7, "carbs": 3.6, "fat": 0.1},
    "胡萝卜": {"en": "carrot", "calories": 41, "protein": 0.9, "carbs": 10, "fat": 0.2},
    "南瓜": {"en": "pumpkin", "calories": 26, "protein": 1, "carbs": 6.5, "fat": 0.1},
    "玉米": {"en": "corn", "calories": 86, "protein": 3.3, "carbs": 19, "fat": 1.4},
    "生菜": {"en": "lettuce", "calories": 15, "protein": 1.4, "carbs": 2.9, "fat": 0.2},
    "芹菜": {"en": "celery", "calories": 14, "protein": 0.7, "carbs": 3, "fat": 0.2},
    "白菜": {"en": "chinese cabbage", "calories": 13, "protein": 1.5, "carbs": 2.2, "fat": 0.2},
    
    # 主食
    "米饭": {"en": "cooked rice", "calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
    "糙米饭": {"en": "brown rice", "calories": 123, "protein": 2.7, "carbs": 26, "fat": 1},
    "面条": {"en": "noodles", "calories": 138, "protein": 4.5, "carbs": 25, "fat": 2},
    "全麦面包": {"en": "whole wheat bread", "calories": 247, "protein": 13, "carbs": 41, "fat": 3.4},
    "红薯": {"en": "sweet potato", "calories": 86, "protein": 1.6, "carbs": 20, "fat": 0.1},
    "燕麦": {"en": "oatmeal", "calories": 68, "protein": 2.4, "carbs": 12, "fat": 1.4},
    "馒头": {"en": "steamed bun", "calories": 223, "protein": 7, "carbs": 45, "fat": 1.1},
    "藜麦": {"en": "quinoa", "calories": 120, "protein": 4.4, "carbs": 21, "fat": 1.9},
    
    # 豆制品
    "豆腐": {"en": "tofu", "calories": 76, "protein": 8, "carbs": 1.9, "fat": 4.8},
    "豆浆": {"en": "soy milk", "calories": 33, "protein": 2.9, "carbs": 1.8, "fat": 1.6},
    "毛豆": {"en": "edamame", "calories": 122, "protein": 12, "carbs": 9, "fat": 5},
    
    # 水果
    "苹果": {"en": "apple", "calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2},
    "香蕉": {"en": "banana", "calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3},
    "牛油果": {"en": "avocado", "calories": 160, "protein": 2, "carbs": 9, "fat": 15},
    "蓝莓": {"en": "blueberry", "calories": 57, "protein": 0.7, "carbs": 14, "fat": 0.3},
    "草莓": {"en": "strawberry", "calories": 32, "protein": 0.7, "carbs": 7.7, "fat": 0.3},
    
    # 乳制品
    "酸奶": {"en": "yogurt", "calories": 63, "protein": 5.3, "carbs": 5, "fat": 2.5},
    "牛奶": {"en": "milk", "calories": 42, "protein": 3.4, "carbs": 5, "fat": 1},
    "奶酪": {"en": "cheese", "calories": 402, "protein": 25, "carbs": 1.3, "fat": 33},
    
    # 更多蔬菜
    "花菜": {"en": "cauliflower", "calories": 25, "protein": 1.9, "carbs": 5, "fat": 0.3},
    "蒜薹": {"en": "garlic sprouts", "calories": 45, "protein": 2, "carbs": 9.5, "fat": 0.4},
    "红椒": {"en": "red pepper", "calories": 31, "protein": 1, "carbs": 6, "fat": 0.3},
    "青椒": {"en": "green pepper", "calories": 20, "protein": 0.9, "carbs": 4.6, "fat": 0.2},
    "茄子": {"en": "eggplant", "calories": 25, "protein": 1, "carbs": 6, "fat": 0.2},
    "土豆": {"en": "potato", "calories": 77, "protein": 2, "carbs": 17, "fat": 0.1},
    "豆角": {"en": "green beans", "calories": 31, "protein": 1.8, "carbs": 7, "fat": 0.1},
    "莴笋": {"en": "lettuce stem", "calories": 14, "protein": 0.6, "carbs": 2.8, "fat": 0.1},
    "蘑菇": {"en": "mushroom", "calories": 22, "protein": 3.1, "carbs": 3.3, "fat": 0.3},
    "木耳": {"en": "wood ear", "calories": 21, "protein": 0.5, "carbs": 5, "fat": 0.2},
    
    # 更多肉类/加工肉
    "腊肉": {"en": "cured pork", "calories": 498, "protein": 12, "carbs": 3, "fat": 50},
    "五花肉": {"en": "pork belly", "calories": 518, "protein": 9, "carbs": 0, "fat": 53},
    "排骨": {"en": "pork ribs", "calories": 264, "protein": 18, "carbs": 0, "fat": 21},
    "鸭肉": {"en": "duck", "calories": 240, "protein": 16, "carbs": 0, "fat": 20},
    "羊肉": {"en": "lamb", "calories": 294, "protein": 25, "carbs": 0, "fat": 21},
    "香肠": {"en": "sausage", "calories": 301, "protein": 12, "carbs": 2, "fat": 27},
    
    # 淡水鱼
    "鲈鱼": {"en": "sea bass", "calories": 97, "protein": 18, "carbs": 0, "fat": 2},
    "草鱼": {"en": "grass carp", "calories": 113, "protein": 16, "carbs": 0, "fat": 5.2},
    "鲫鱼": {"en": "crucian carp", "calories": 108, "protein": 17, "carbs": 0, "fat": 4.2},
    "带鱼": {"en": "hairtail", "calories": 127, "protein": 18, "carbs": 0, "fat": 5.6},
    "鳜鱼": {"en": "mandarin fish", "calories": 117, "protein": 20, "carbs": 0, "fat": 4},
    "藜蒿": {"en": "artemisia", "calories": 31, "protein": 3.6, "carbs": 4, "fat": 0.5},
    
    # 零食/其他
    "坚果混合": {"en": "mixed nuts", "calories": 607, "protein": 20, "carbs": 21, "fat": 54},
    "黑巧克力": {"en": "dark chocolate", "calories": 546, "protein": 5, "carbs": 60, "fat": 31},
    "咖啡黑": {"en": "black coffee", "calories": 2, "protein": 0.3, "carbs": 0, "fat": 0},
}

def search(query):
    """搜索食物，支持中文和英文"""
    query = query.lower().strip()
    results = []
    for name_cn, data in FOODS.items():
        if query in name_cn.lower() or query in data.get('en', '').lower():
            results.append({
                'name': name_cn,
                'name_en': data.get('en', ''),
                'per_100g': {
                    'calories': data['calories'],
                    'protein_g': data['protein'],
                    'carbs_g': data['carbs'],
                    'fat_g': data['fat'],
                }
            })
    return results

def calc_nutrition(name, amount_g):
    """计算指定克数的营养"""
    query = name.lower().strip()
    for name_cn, data in FOODS.items():
        if query in name_cn.lower() or query in data.get('en', '').lower():
            ratio = amount_g / 100
            return {
                'name': name_cn,
                'amount_g': amount_g,
                'calories': round(data['calories'] * ratio),
                'protein_g': round(data['protein'] * ratio, 1),
                'carbs_g': round(data['carbs'] * ratio, 1),
                'fat_g': round(data['fat'] * ratio, 1),
            }
    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='半饱 - 食物营养查询')
    sub = parser.add_subparsers(dest='cmd')
    
    p_search = sub.add_parser('search')
    p_search.add_argument('query', type=str, help='食物名称（中/英文）')
    
    p_calc = sub.add_parser('calc')
    p_calc.add_argument('name', type=str, help='食物名称')
    p_calc.add_argument('--amount', type=float, required=True, help='克数')
    
    p_list = sub.add_parser('list')
    
    args = parser.parse_args()
    
    if args.cmd == 'search':
        results = search(args.query)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.cmd == 'calc':
        result = calc_nutrition(args.name, args.amount)
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({'status': 'not_found', 'message': f'没找到"{args.name}"，Agent可以估算'}, ensure_ascii=False))
    elif args.cmd == 'list':
        all_foods = [{'name': k, 'name_en': v.get('en', ''), 'cal_per_100g': v['calories']} for k, v in FOODS.items()]
        print(json.dumps(all_foods, ensure_ascii=False, indent=2))
    else:
        parser.print_help()
