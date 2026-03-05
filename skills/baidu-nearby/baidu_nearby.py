#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度地图附近场所推荐工具
使用百度地图 Place API 进行周边POI搜索
"""

import os
import sys
import json
import urllib.parse
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# 场所分类映射
CATEGORY_MAP = {
    '餐饮': 'catering',
    '美食': 'catering',
    '餐厅': 'catering',
    '吃饭': 'catering',
    '娱乐': 'entertainment',
    '休闲': 'entertainment',
    '景点': 'scenic',
    '旅游': 'scenic',
    '景区': 'scenic',
    '酒店': 'hotel',
    '住宿': 'hotel',
    '购物': 'shopping',
    '商场': 'shopping',
    '超市': 'shopping',
    '交通': 'transportation',
    '地铁': 'transportation',
    '公交': 'transportation',
    '生活': 'life_service',
    '服务': 'life_service',
    '医疗': 'medical',
    '医院': 'medical',
    '教育': 'education',
    '学校': 'education',
    '金融': 'finance',
    '银行': 'finance',
}

# 分类标签映射
TAG_MAP = {
    'catering': ['中餐厅', '西餐厅', '咖啡厅', '火锅', '烧烤', '小吃', '快餐', '酒吧'],
    'entertainment': ['KTV', '电影院', '网吧', '游乐场', '体育馆', '健身房', '公园'],
    'scenic': ['公园', '广场', '景区', '博物馆', '展览馆', '寺庙', '古迹'],
    'hotel': ['酒店', '宾馆', '旅馆', '招待所'],
    'shopping': ['商场', '购物中心', '超市', '便利店', '专卖店', '市场'],
    'transportation': ['地铁站', '公交站', '火车站', '机场', '汽车站'],
    'life_service': ['加油站', '停车场', '厕所', '快递', '洗衣', '理发'],
    'medical': ['医院', '诊所', '药店', '急救中心'],
    'education': ['大学', '中学', '小学', '幼儿园', '培训机构', '图书馆'],
    'finance': ['银行', 'ATM', '证券', '保险'],
}

DEFAULT_TAGS = {
    'catering': '美食',
    'entertainment': '休闲娱乐',
    'scenic': '旅游景点',
    'hotel': '酒店宾馆',
    'shopping': '购物',
    'transportation': '交通设施',
    'life_service': '生活服务',
    'medical': '医疗保健',
    'education': '教育培训',
    'finance': '金融银行',
}


def get_api_key():
    """从环境变量获取API Key"""
    api_key = os.environ.get('BAIDU_API_KEY') or os.environ.get('BAIDU_AK')
    if not api_key:
        print("错误: 未设置 BAIDU_API_KEY 环境变量")
        print("请访问 https://lbsyun.baidu.com/ 申请AK")
        return None
    return api_key


def geocode(address, ak):
    """地理编码 - 地址转经纬度"""
    url = f"https://api.map.baidu.com/geocoding/v3/?address={urllib.parse.quote(address)}&output=json&ak={ak}"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('status') == 0:
                location = data['result']['location']
                return (location['lat'], location['lng'])
    except Exception as e:
        print(f"地理编码错误: {e}")
    
    return None


def reverse_geocode(lat, lng, ak):
    """逆地理编码 - 经纬度转地址"""
    url = f"https://api.map.baidu.com/reverse_geocoding/v3/?location={lat},{lng}&output=json&ak={ak}"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('status') == 0:
                return data['result']['formatted_address']
    except Exception as e:
        print(f"逆地理编码错误: {e}")
    
    return None


def search_nearby(location, query=None, radius=1000, page_size=10, ak=None):
    """
    周边POI搜索
    
    Args:
        location: 中心点坐标 (lat,lng) 或地址
        query: 搜索关键词（可选，不传则搜索全类别）
        radius: 搜索半径（米），默认1000
        page_size: 返回结果数量，默认10
        ak: 百度API Key
    
    Returns:
        list: POI列表
    """
    if not ak:
        ak = get_api_key()
        if not ak:
            return None
    
    # 如果传入的是地址，先进行地理编码
    if isinstance(location, str) and (',' not in location or len(location.split(',')) != 2):
        coord = geocode(location, ak)
        if not coord:
            print(f"无法解析位置: {location}")
            return None
        lat, lng = coord
    elif isinstance(location, str):
        lat, lng = map(float, location.split(','))
    else:
        lat, lng = location
    
    base_url = "https://api.map.baidu.com/place/v2/search"
    
    params = {
        'query': query or '美食',
        'location': f"{lat},{lng}",
        'radius': radius,
        'output': 'json',
        'ak': ak,
        'scope': '2',  # 返回详细信息
        'page_size': page_size,
        'page_num': '0',
    }
    
    url = f"{base_url}?" + urllib.parse.urlencode(params)
    
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('status') == 0:
                return data.get('results', [])
            else:
                print(f"搜索失败: {data.get('message', '未知错误')}")
    except Exception as e:
        print(f"请求错误: {e}")
    
    return None


def get_category_tag(category):
    """获取分类对应的搜索标签"""
    category_lower = category.lower()
    if category_lower in TAG_MAP:
        return DEFAULT_TAGS.get(category_lower, category)
    
    # 尝试中文匹配
    for cn, en in CATEGORY_MAP.items():
        if cn in category or category in cn:
            return DEFAULT_TAGS.get(en, category)
    
    return category


def format_distance(meters):
    """格式化距离"""
    if meters >= 1000:
        return f"{meters/1000:.1f}km"
    return f"{meters}m"


def print_poi_results(results, location_name, category=None):
    """格式化打印POI结果"""
    if not results:
        print(f"未找到{category or ''}相关场所")
        return
    
    category_display = category or "周边场所"
    print(f"\n📍 {location_name} 附近的{category_display}推荐")
    print("=" * 50)
    print(f"找到 {len(results)} 个推荐地点\n")
    
    for i, poi in enumerate(results, 1):
        name = poi.get('name', '未知')
        address = poi.get('address', '地址未知')
        distance = poi.get('distance', 0)
        rating = poi.get('detail_info', {}).get('overall_rating', '')
        price = poi.get('detail_info', {}).get('price', '')
        tag = poi.get('detail_info', {}).get('tag', '')
        phone = poi.get('telephone', '')
        
        # 构建评分和价格显示
        meta = []
        if rating:
            meta.append(f"⭐{rating}")
        if price:
            meta.append(f"💰{price}元")
        if tag:
            meta.append(f"🏷️{tag}")
        
        print(f"{i}. 🏪 {name}")
        print(f"   📍 {address}")
        if meta:
            print(f"   {' | '.join(meta)}")
        print(f"   📏 距离: {format_distance(int(distance))}")
        if phone:
            print(f"   📞 {phone}")
        print()


def recommend_nearby(location, category=None, radius=1000, limit=10):
    """
    推荐附近场所的主函数
    
    Args:
        location: 位置（地址或坐标）
        category: 类别（餐饮、娱乐、景点等）
        radius: 搜索半径（米）
        limit: 返回数量
    
    Returns:
        list: POI列表
    """
    ak = get_api_key()
    if not ak:
        return None
    
    # 获取坐标和位置名称
    if isinstance(location, str) and (',' not in location or len(location.split(',')) != 2):
        coord = geocode(location, ak)
        if not coord:
            print(f"无法解析位置: {location}")
            return None
        lat, lng = coord
        location_name = location
    elif isinstance(location, str):
        lat, lng = map(float, location.split(','))
        location_name = reverse_geocode(lat, lng, ak) or f"{lat},{lng}"
    else:
        lat, lng = location
        location_name = reverse_geocode(lat, lng, ak) or f"{lat},{lng}"
    
    # 确定搜索关键词
    query = None
    if category:
        query = get_category_tag(category)
    
    # 搜索
    results = search_nearby((lat, lng), query=query, radius=radius, page_size=limit, ak=ak)
    
    if results:
        print_poi_results(results, location_name, category)
    
    return results


def main():
    if len(sys.argv) < 2:
        print("使用方法: python baidu_nearby.py <位置> [类别] [半径(米)] [数量]")
        print("")
        print("位置: 具体地址或经纬度坐标（如：39.9,116.4）")
        print("类别: 餐饮/美食、娱乐/休闲、景点/旅游、酒店、购物等")
        print("")
        print("示例:")
        print("  python baidu_nearby.py '北京市朝阳区三里屯' 餐饮 2000 5")
        print("  python baidu_nearby.py '39.9,116.4' 景点 5000 10")
        print("  python baidu_nearby.py '上海市人民广场' 娱乐")
        sys.exit(1)
    
    location = sys.argv[1]
    category = sys.argv[2] if len(sys.argv) > 2 else None
    radius = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 10
    
    print(f"🔍 正在搜索: {location}")
    if category:
        print(f"   类别: {category}")
    print(f"   半径: {radius}米")
    print(f"   数量: {limit}个")
    print("-" * 40)
    
    recommend_nearby(location, category, radius, limit)


if __name__ == '__main__':
    main()
