#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度地图路线规划工具
使用百度地图 DirectionLite API
"""

import os
import sys
import json
import urllib.parse
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

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
                return f"{location['lat']},{location['lng']}"
    except Exception as e:
        print(f"地理编码错误: {e}")
    
    return None

def direction_lite(origin, destination, mode='driving', ak=None):
    """
    百度地图路线规划
    
    Args:
        origin: 起点 (地址或经纬度 "lat,lng")
        destination: 终点 (地址或经纬度 "lat,lng")
        mode: 出行方式 - driving(驾车)|riding(骑行)|walking(步行)|transit(公交)
        ak: 百度API Key
    
    Returns:
        dict: 路线规划结果
    """
    if not ak:
        ak = get_api_key()
        if not ak:
            return None
    
    # 如果传入的是地址，先进行地理编码
    if ',' not in origin or not origin.replace(',', '').replace('.', '').replace('-', '').isdigit():
        origin_coord = geocode(origin, ak)
        if not origin_coord:
            print(f"无法解析起点: {origin}")
            return None
    else:
        origin_coord = origin
    
    if ',' not in destination or not destination.replace(',', '').replace('.', '').replace('-', '').isdigit():
        dest_coord = geocode(destination, ak)
        if not dest_coord:
            print(f"无法解析终点: {destination}")
            return None
    else:
        dest_coord = destination
    
    base_url = "https://api.map.baidu.com/directionlite/v1/"
    
    if mode == 'transit':
        endpoint = 'transit'
    else:
        endpoint = mode
    
    params = {
        'origin': origin_coord,
        'destination': dest_coord,
        'ak': ak,
        'output': 'json'
    }
    
    if mode == 'driving':
        params['alternatives'] = '1'
    
    url = f"{base_url}{endpoint}?" + urllib.parse.urlencode(params)
    
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"请求错误: {e}")
        return None

def format_duration(seconds):
    """格式化时间"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours}小时{minutes}分钟"
    return f"{minutes}分钟"

def format_distance(meters):
    """格式化距离"""
    if meters >= 1000:
        return f"{meters/1000:.1f}公里"
    return f"{meters}米"

def print_route(result, mode):
    """打印路线结果"""
    if not result:
        print("未获取到路线信息")
        return
    
    status = result.get('status')
    if status != 0:
        print(f"请求失败，状态码: {status}")
        message = result.get('message', '未知错误')
        print(f"错误信息: {message}")
        return
    
    route = result.get('result', {}).get('routes', [{}])[0]
    
    if not route:
        print("未找到可用路线")
        return
    
    distance = route.get('distance', 0)
    duration = route.get('duration', 0)
    
    mode_names = {
        'driving': '🚗 驾车',
        'riding': '🚴 骑行',
        'walking': '🚶 步行',
        'transit': '🚌 公交'
    }
    
    print(f"\n{mode_names.get(mode, mode)}路线规划")
    print("=" * 40)
    print(f"总距离: {format_distance(distance)}")
    print(f"预计时间: {format_duration(duration)}")
    print()
    
    steps = route.get('steps', [])
    if steps:
        print("详细路线:")
        print("-" * 40)
        for i, step in enumerate(steps, 1):
            if isinstance(step, dict):
                instruction = step.get('instruction', step.get('step_instruction', '未知步骤'))
                step_distance = step.get('distance', 0)
                print(f"{i}. {instruction} ({format_distance(step_distance)})")
            else:
                print(f"{i}. {step}")
    
    if mode == 'driving' and 'traffic_condition' in route:
        traffic = route['traffic_condition']
        print(f"\n路况: {traffic}")

def main():
    if len(sys.argv) < 3:
        print("使用方法: python baidu_direction.py <起点> <终点> [driving|riding|walking|transit]")
        print("示例:")
        print("  python baidu_direction.py '北京市朝阳区' '北京市海淀区' driving")
        print("  python baidu_direction.py '39.9,116.3' '39.8,116.4' walking")
        sys.exit(1)
    
    origin = sys.argv[1]
    destination = sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else 'driving'
    
    if mode not in ['driving', 'riding', 'walking', 'transit']:
        print(f"不支持的出行方式: {mode}")
        print("支持的类型: driving(驾车), riding(骑行), walking(步行), transit(公交)")
        sys.exit(1)
    
    print(f"🗺️ 路线规划: {origin} → {destination}")
    
    result = direction_lite(origin, destination, mode)
    print_route(result, mode)

if __name__ == '__main__':
    main()
