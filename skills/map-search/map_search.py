#!/usr/bin/env python3
"""
地图搜索工具
支持：高德、百度、腾讯
- 关键词搜索
- 附近搜索（需经纬度）
"""

import os
import json
import requests

# 配置文件路径
CONFIG_PATH = os.path.expanduser("~/.config/openclaw/map_config.json")

def get_config():
    """从配置文件读取所有配置"""
    default_config = {
        "api_keys": {
            "amap": "",
            "baidu": "",
            "tencent": ""
        },
        "priority": ["amap", "tencent", "baidu"]
    }
    
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                return {
                    "api_keys": {
                        "amap": config.get("amap", {}).get("api_key", ""),
                        "baidu": config.get("baidu", {}).get("api_key", ""),
                        "tencent": config.get("tencent", {}).get("api_key", "")
                    },
                    "priority": config.get("priority", ["amap", "tencent", "baidu"])
                }
        except Exception as e:
            print(f"读取配置失败: {e}")
    
    # 回退到环境变量
    return {
        "api_keys": {
            "amap": os.getenv("AMAP_API_KEY", ""),
            "baidu": os.getenv("BAIDU_MAP_API_KEY", ""),
            "tencent": os.getenv("TENCENT_MAP_API_KEY", "")
        },
        "priority": ["amap", "tencent", "baidu"]
    }

# 读取配置
CONFIG = get_config()
API_KEYS = CONFIG["api_keys"]
PRIORITY = CONFIG["priority"]

AMAP_KEY = API_KEYS["amap"]
BAIDU_KEY = API_KEYS["baidu"]
TENCENT_KEY = API_KEYS["tencent"]


def get_current_location():
    """通过 IP 获取当前经纬度"""
    try:
        # 使用高德 IP 定位 API
        if AMAP_KEY:
            url = f"https://restapi.amap.com/v3/ip?key={AMAP_KEY}"
            r = requests.get(url, timeout=5).json()
            if r.get("status") == "1" and r.get("rectangle"):
                # 高德返回的是矩形坐标，取中心点
                rect = r.get("rectangle")
                coords = rect.split(";")[0].split(",")
                return float(coords[0]), float(coords[1])  # 经度, 纬度
    except:
        pass
    
    # 备选：返回默认位置（上海）
    return 121.473701, 31.230416  # 上海


def search_maps(keyword, region="全国", priority=None):
    """地图聚合搜索 - 关键词搜索"""
    if priority is None:
        priority = PRIORITY
    
    results = {}
    
    # 高德
    if "amap" in priority and AMAP_KEY:
        url = f"https://restapi.amap.com/v3/place/text?key={AMAP_KEY}&keywords={keyword}&city={region}&output=json"
        try:
            r = requests.get(url, timeout=5).json()
            if r.get("status") == "1":
                results["高德"] = [{"name": p["name"], "address": p["address"], "location": p["location"]}
                                   for p in r.get("pois", [])[:5]]
        except:
            pass
    
    # 百度
    if "baidu" in priority and BAIDU_KEY:
        url = f"https://api.map.baidu.com/place/v2/search?query={keyword}&region={region}&ak={BAIDU_KEY}&output=json"
        try:
            r = requests.get(url, timeout=5).json()
            if r.get("status") == 0:
                results["百度"] = [{"name": p["name"], "address": p.get("address", ""), "location": p.get("location", "")}
                                   for p in r.get("results", [])[:5]]
        except:
            pass
    
    # 腾讯
    if "tencent" in priority and TENCENT_KEY:
        url = f"https://apis.map.qq.com/ws/place/v1/search?keyword={keyword}&region={region}&key={TENCENT_KEY}&output=json"
        try:
            r = requests.get(url, timeout=5).json()
            if r.get("status") == 0:
                results["腾讯"] = [{"name": p["name"], "address": p.get("address", ""), "location": p.get("location", "")}
                                   for p in r.get("data", [])[:5]]
        except:
            pass
    
    return results


def search_nearby(keyword, lat=None, lng=None, radius=2000, priority=None):
    """地图聚合搜索 - 附近搜索
    
    Args:
        keyword: 搜索关键词
        lat: 纬度
        lng: 经度
        radius: 搜索半径（米），默认2000米
        priority: 地图优先级
    """
    if priority is None:
        priority = PRIORITY
    
    # 如果没有提供经纬度，自动获取
    if lat is None or lng is None:
        print("正在获取当前位置...")
        lng, lat = get_current_location()
        print(f"当前位置: 经度 {lng}, 纬度 {lat}")
    
    results = {}
    
    # 高德（location 格式：经度,纬度）
    if "amap" in priority and AMAP_KEY:
        location = f"{lng},{lat}"
        url = f"https://restapi.amap.com/v3/place/around?key={AMAP_KEY}&keywords={keyword}&location={location}&radius={radius}&output=json"
        try:
            r = requests.get(url, timeout=5).json()
            if r.get("status") == "1":
                results["高德"] = [{"name": p["name"], "address": p["address"], 
                                   "distance": p.get("distance", "N/A"),
                                   "location": p["location"]}
                                   for p in r.get("pois", [])[:10]]
        except:
            pass
    
    # 百度（location 格式：纬度,经度）
    if "baidu" in priority and BAIDU_KEY:
        location = f"{lat},{lng}"
        url = f"https://api.map.baidu.com/place/v2/search?query={keyword}&location={location}&radius={radius}&ak={BAIDU_KEY}&output=json"
        try:
            r = requests.get(url, timeout=5).json()
            if r.get("status") == 0:
                results["百度"] = [{"name": p["name"], "address": p.get("address", ""),
                                   "distance": str(p.get("distance", "N/A")),
                                   "location": p.get("location", "")}
                                   for p in r.get("results", [])[:10]]
        except:
            pass
    
    # 腾讯（boundary 格式：nearby(经度,纬度,半径)）
    if "tencent" in priority and TENCENT_KEY:
        boundary = f"nearby({lng},{lat},{radius})"
        url = f"https://apis.map.qq.com/ws/place/v1/search?keyword={keyword}&boundary={boundary}&key={TENCENT_KEY}&output=json"
        try:
            r = requests.get(url, timeout=5).json()
            if r.get("status") == 0:
                results["腾讯"] = [{"name": p["name"], "address": p.get("address", ""),
                                   "distance": str(p.get("distance", "N/A")),
                                   "location": p.get("location", "")}
                                   for p in r.get("data", [])[:10]]
        except:
            pass
    
    return results


if __name__ == "__main__":
    import sys
    
    # 解析参数
    args = sys.argv[1:]
    
    # 检查是否是附近搜索
    if "--nearby" in args or "-n" in args:
        args.remove("--nearby")
        args.remove("-n")
        
        # 解析参数
        keyword = "咖啡馆"  # 默认
        lat = None
        lng = None
        radius = 2000
        
        i = 0
        while i < len(args):
            if args[i] == "--keyword" or args[i] == "-k":
                keyword = args[i + 1]
                i += 2
            elif args[i] == "--lat":
                lat = float(args[i + 1])
                i += 2
            elif args[i] == "--lng":
                lng = float(args[i + 1])
                i += 2
            elif args[i] == "--radius" or args[i] == "-r":
                radius = int(args[i + 1])
                i += 2
            else:
                i += 1
        
        # 执行附近搜索
        print(f"\n🔍 附近搜索: {keyword} (半径 {radius} 米)")
        results = search_nearby(keyword, lat, lng, radius)
        
        for source, items in results.items():
            print(f"\n【{source}】")
            for i, item in enumerate(items, 1):
                dist = item.get("distance", "N/A")
                print(f"  {i}. {item['name']}")
                print(f"     地址: {item['address']}")
                print(f"     距离: {dist}米")
    
    else:
        # 关键词搜索
        keyword = args[0] if args else "咖啡馆"
        region = args[1] if len(args) > 1 else "上海"
        
        print(f"\n🔍 关键词搜索: {keyword} (地区: {region})")
        results = search_maps(keyword, region)
        
        for source, items in results.items():
            print(f"\n【{source}】")
            for i, item in enumerate(items, 1):
                print(f"  {i}. {item['name']}")
                print(f"     地址: {item['address']}")
