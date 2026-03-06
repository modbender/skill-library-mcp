#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高德地图实时路况与路线规划工具
功能：查询实时路况 + 规划最优自驾路线
每次运行时从 openclaw.json 配置文件中读取最新的 AMAP_KEY
"""

import sys
import os
import json
import urllib.parse
import urllib.request

def get_amap_key_from_config():
    """从 openclaw.json 配置文件中读取最新的 AMAP_KEY"""
    config_paths = [
        "/home/admin/.openclaw/openclaw.json",
        os.path.expanduser("~/.openclaw/openclaw.json")
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 优先读取技能配置中的 apiKey 字段（OpenClaw 标准字段名）
                    if 'skills' in config and 'entries' in config['skills'] and 'amap-traffic' in config['skills']['entries']:
                        skill_config = config['skills']['entries']['amap-traffic']
                        amap_key = skill_config.get('apiKey')
                        if amap_key:
                            return amap_key
                    
                    # 其他兼容性字段（向后兼容）
                    amap_key = config.get('amapKey') or config.get('AMAP_KEY')
                    if amap_key:
                        return amap_key
            except (json.JSONDecodeError, IOError) as e:
                continue
    
    # 如果配置文件中没有找到，再尝试环境变量（向后兼容）
    return os.environ.get("AMAP_KEY")

def geocode(address, city="", amap_key=None):
    """地理编码：将地址转为经纬度"""
    if amap_key is None:
        amap_key = get_amap_key_from_config()
    
    if not amap_key:
        print("错误: 未找到 AMAP_KEY，请在 OpenClaw Web 配置页面设置", file=sys.stderr)
        return None
        
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        "address": address,
        "key": amap_key
    }
    if city:
        params["city"] = city
    
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    
    try:
        with urllib.request.urlopen(full_url) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data["status"] == "1" and data["geocodes"]:
                location = data["geocodes"][0]["location"]
                return location  # 格式: "经度,纬度"
            else:
                print(f"地理编码失败: {data.get('info', '未知错误')}", file=sys.stderr)
                return None
    except Exception as e:
        print(f"请求失败: {e}", file=sys.stderr)
        return None

def get_driving_route_with_traffic(origin, destination, amap_key=None):
    """获取含实时路况的驾车路线（最快路线）"""
    if amap_key is None:
        amap_key = get_amap_key_from_config()
    
    if not amap_key:
        print("错误: 未找到 AMAP_KEY，请在 OpenClaw Web 配置页面设置", file=sys.stderr)
        return None
        
    url = "https://restapi.amap.com/v3/direction/driving"
    params = {
        "origin": origin,
        "destination": destination,
        "strategy": "2",  # 2=优先考虑实时路况的最快路线
        "key": amap_key
    }
    
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    
    try:
        with urllib.request.urlopen(full_url) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data["status"] == "1" and data["route"]["paths"]:
                path = data["route"]["paths"][0]
                duration = int(path["duration"])
                distance = int(path["distance"])
                # 解析路况详情
                traffic_info = []
                for step in path["steps"]:
                    road = step.get("road", "未知道路")
                    traffic_status = step.get("traffic_condition", [])
                    if traffic_status:
                        status = traffic_status[0].get("status", "0")
                        speed = traffic_status[0].get("speed", "0")
                        traffic_info.append({
                            "road": road,
                            "status": status,
                            "speed": speed
                        })
                
                # 费用估算（仅过路费，打车费用需额外计算）
                cost = round(distance / 1000 * 0.6, 1)
                return {
                    "type": "自驾",
                    "duration_sec": duration,
                    "distance": distance,
                    "cost": cost,
                    "traffic_details": traffic_info
                }
            else:
                print(f"路线规划失败: {data.get('info', '无可用路线')}", file=sys.stderr)
                return None
    except Exception as e:
        print(f"请求失败: {e}", file=sys.stderr)
        return None

def format_time(seconds):
    """将秒转换为易读格式"""
    if seconds < 3600:
        return f"{seconds//60}分钟"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}小时{minutes}分钟"

def format_traffic_status(status_code):
    """将路况状态码转为中文描述"""
    status_map = {
        "0": "未知",
        "1": "畅通 🟢",
        "2": "缓行 🟡",
        "3": "拥堵 🔴",
        "4": "严重拥堵 🟣"
    }
    return status_map.get(status_code, "未知")

def main():
    if len(sys.argv) < 3:
        print("用法: python3 amap_traffic.py <起点地址> <终点地址> [城市]")
        print("注意: 需在 OpenClaw Web 配置页面设置 AMAP_KEY")
        sys.exit(1)
    
    origin_addr = sys.argv[1]
    dest_addr = sys.argv[2]
    city = sys.argv[3] if len(sys.argv) > 3 else ""
    
    # 获取最新的 AMAP_KEY
    amap_key = get_amap_key_from_config()
    if not amap_key:
        print("错误: 未找到 AMAP_KEY，请在 OpenClaw Web 配置页面设置")
        sys.exit(1)
    
    # 1. 地理编码
    origin_loc = geocode(origin_addr, city, amap_key)
    if not origin_loc:
        print("起点地址解析失败")
        sys.exit(1)
    
    dest_loc = geocode(dest_addr, city, amap_key)
    if not dest_loc:
        print("终点地址解析失败")
        sys.exit(1)
    
    # 2. 获取含实时路况的路线
    route = get_driving_route_with_traffic(origin_loc, dest_loc, amap_key)
    if not route:
        print("未找到任何路线方案")
        sys.exit(1)
    
    # 3. 输出结果
    print("🚗 实时路况最优路线:")
    print("-" * 50)
    time_str = format_time(route["duration_sec"])
    dist_str = f"{route['distance']/1000:.1f}公里"
    cost_str = f"¥{route['cost']:.1f}"
    print(f"预计时间: {time_str}")
    print(f"行驶距离: {dist_str}")
    print(f"预估费用: {cost_str}")
    print("\n🚦 详细路况:")
    for segment in route["traffic_details"]:
        status = format_traffic_status(segment["status"])
        speed = segment["speed"] if segment["speed"] != "0" else "N/A"
        print(f"  - {segment['road']}: {status} (速度: {speed}km/h)")

if __name__ == "__main__":
    main()