#!/usr/bin/env python3
"""
Weather Checker - 命令行天气查询工具
查询目标城市目标时间的天气信息
"""

import argparse
import json
import sys
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# 城市坐标数据库（可扩展）
CITY_COORDINATES = {
    "beijing": {"name": "北京", "latitude": 39.9042, "longitude": 116.4074},
    "shanghai": {"name": "上海", "latitude": 31.2304, "longitude": 121.4737},
    "guangzhou": {"name": "广州", "latitude": 23.1291, "longitude": 113.2644},
    "shenzhen": {"name": "深圳", "latitude": 22.5431, "longitude": 114.0579},
    "hangzhou": {"name": "杭州", "latitude": 30.2741, "longitude": 120.1551},
    "chengdu": {"name": "成都", "latitude": 30.5728, "longitude": 104.0668},
    "xian": {"name": "西安", "latitude": 34.3416, "longitude": 108.9398},
    "wuhan": {"name": "武汉", "latitude": 30.5928, "longitude": 114.3055},
    "nanjing": {"name": "南京", "latitude": 32.0603, "longitude": 118.7969},
    "chongqing": {"name": "重庆", "latitude": 29.5630, "longitude": 106.5516},
}

# 天气代码映射（带emoji）
WEATHER_CODE_MAP = {
    0: {"desc": "晴", "emoji": "☀️"},
    1: {"desc": "基本晴", "emoji": "🌤️"},
    2: {"desc": "部分多云", "emoji": "⛅"},
    3: {"desc": "多云", "emoji": "☁️"},
    45: {"desc": "雾", "emoji": "🌫️"},
    48: {"desc": "雾凇", "emoji": "🌫️"},
    51: {"desc": "小雨", "emoji": "🌦️"},
    53: {"desc": "中雨", "emoji": "🌧️"},
    55: {"desc": "大雨", "emoji": "🌧️"},
    56: {"desc": "冻毛毛雨", "emoji": "🌨️"},
    57: {"desc": "冻毛毛雨", "emoji": "🌨️"},
    61: {"desc": "小雨", "emoji": "🌦️"},
    63: {"desc": "中雨", "emoji": "🌧️"},
    65: {"desc": "大雨", "emoji": "🌧️"},
    66: {"desc": "冻雨", "emoji": "🌨️"},
    67: {"desc": "冻雨", "emoji": "🌨️"},
    71: {"desc": "小雪", "emoji": "🌨️"},
    73: {"desc": "中雪", "emoji": "❄️"},
    75: {"desc": "大雪", "emoji": "❄️"},
    77: {"desc": "雪粒", "emoji": "🌨️"},
    80: {"desc": "阵雨", "emoji": "🌦️"},
    81: {"desc": "强阵雨", "emoji": "⛈️"},
    82: {"desc": "猛烈阵雨", "emoji": "⛈️"},
    85: {"desc": "阵雪", "emoji": "🌨️"},
    86: {"desc": "强阵雪", "emoji": "❄️"},
    95: {"desc": "雷暴", "emoji": "⛈️"},
    96: {"desc": "雷暴伴冰雹", "emoji": "⛈️"},
    99: {"desc": "强雷暴伴冰雹", "emoji": "⛈️"},
}


def get_city_coordinates(city_name: str) -> Optional[Dict[str, float]]:
    """获取城市坐标"""
    city_key = city_name.lower().replace(" ", "")
    
    # 检查预定义城市
    if city_key in CITY_COORDINATES:
        city = CITY_COORDINATES[city_key]
        return {
            "name": city["name"],
            "latitude": city["latitude"],
            "longitude": city["longitude"]
        }
    
    # 尝试通过Open-Meteo地理编码API查找
    try:
        response = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city_name, "count": 1, "language": "zh", "format": "json"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                result = data["results"][0]
                return {
                    "name": result.get("name", city_name),
                    "latitude": result["latitude"],
                    "longitude": result["longitude"]
                }
    except Exception:
        pass
    
    return None


def get_weather_forecast(latitude: float, longitude: float, days_ahead: int = 1) -> Dict[str, Any]:
    """获取天气预报"""
    try:
        # 计算目标日期
        target_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        
        # 调用Open-Meteo API - 获取更多天气参数
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weathercode",
                "timezone": "Asia/Shanghai",
                "forecast_days": days_ahead + 1
            },
            timeout=10
        )
        
        if response.status_code != 200:
            return {"error": f"API请求失败: {response.status_code}"}
        
        data = response.json()
        
        # 提取目标日期的数据
        daily_data = data.get("daily", {})
        if not daily_data.get("time"):
            return {"error": "未找到天气数据"}
        
        # 查找目标日期
        for i, date_str in enumerate(daily_data["time"]):
            if date_str == target_date:
                weather_code = daily_data["weathercode"][i]
                weather_info = WEATHER_CODE_MAP.get(weather_code, {"desc": "未知", "emoji": "❓"})
                
                # 获取降水概率（如果API提供）
                precipitation_probability = daily_data.get("precipitation_probability_max", [0] * len(daily_data["time"]))[i]
                
                return {
                    "date": target_date,
                    "temperature_max": daily_data["temperature_2m_max"][i],
                    "temperature_min": daily_data["temperature_2m_min"][i],
                    "precipitation": daily_data["precipitation_sum"][i],
                    "precipitation_probability": precipitation_probability,
                    "weather_code": weather_code,
                    "weather_description": weather_info["desc"],
                    "weather_emoji": weather_info["emoji"],
                    "units": data.get("daily_units", {}),
                    "location": {
                        "latitude": data["latitude"],
                        "longitude": data["longitude"],
                        "timezone": data["timezone"]
                    }
                }
        
        return {"error": f"未找到日期 {target_date} 的预报数据"}
        
    except requests.exceptions.Timeout:
        return {"error": "请求超时，请检查网络连接"}
    except Exception as e:
        return {"error": f"获取天气数据时出错: {str(e)}"}


def format_output(result: Dict[str, Any], output_format: str = "pretty") -> str:
    """格式化输出"""
    if "error" in result:
        return json.dumps({"error": result["error"]}, ensure_ascii=False, indent=2)
    
    if output_format == "json":
        return json.dumps(result, ensure_ascii=False, indent=2)
    elif output_format == "pretty":
        # 漂亮的格式化输出，带emoji
        location = result.get('location_name', '未知')
        date = result['date']
        weather_desc = result['weather_description']
        weather_emoji = result.get('weather_emoji', '❓')
        weather_code = result['weather_code']
        temp_min = result['temperature_min']
        temp_max = result['temperature_max']
        precipitation = result['precipitation']
        
        # 温度颜色标记
        def temp_color(temp, use_color=True):
            if not use_color:
                return f"{temp}°C"
            
            if temp >= 30:
                return f"\033[91m{temp}°C\033[0m"  # 红色 - 很热
            elif temp >= 25:
                return f"\033[93m{temp}°C\033[0m"  # 黄色 - 热
            elif temp >= 15:
                return f"\033[92m{temp}°C\033[0m"  # 绿色 - 舒适
            elif temp >= 5:
                return f"\033[96m{temp}°C\033[0m"  # 青色 - 凉
            else:
                return f"\033[94m{temp}°C\033[0m"  # 蓝色 - 冷
        
        # 检查终端是否支持颜色
        import sys
        use_color = sys.stdout.isatty()
        
        temp_min_colored = temp_color(temp_min, use_color)
        temp_max_colored = temp_color(temp_max, use_color)
        
        # 降水量标记
        def precip_marker(precip):
            if precip == 0:
                return "🌵"  # 干旱
            elif precip < 1:
                return "💧"  # 少量
            elif precip < 5:
                return "💦"  # 中等
            elif precip < 10:
                return "🌊"  # 大量
            else:
                return "🌧️"  # 暴雨
        
        precip_marker_emoji = precip_marker(precipitation)
        
        # 构建输出 - 简洁无边框格式
        # 获取降水概率
        precip_prob = result.get('precipitation_probability', 0)
        
        # 降水概率emoji
        def precip_prob_emoji(prob):
            if prob == 0:
                return "🌵"
            elif prob < 30:
                return "🌤️"
            elif prob < 60:
                return "🌦️"
            elif prob < 80:
                return "🌧️"
            else:
                return "⛈️"
        
        precip_prob_emoji_str = precip_prob_emoji(precip_prob)
        
        output = f"""
🌤️ 天气查询结果 🌤️

地点: {location}
日期: {date}
天气: {weather_emoji} {weather_desc}
温度: {temp_min_colored} ~ {temp_max_colored}
降水量: {precip_marker_emoji} {precipitation:.1f}mm
降水概率: {precip_prob_emoji_str} {precip_prob}%
"""
        return output.strip()
    elif output_format == "simple":
        # 简单的单行格式
        location = result.get('location_name', '未知')
        date = result['date']
        weather_desc = result['weather_description']
        weather_emoji = result.get('weather_emoji', '❓')
        temp_min = result['temperature_min']
        temp_max = result['temperature_max']
        precipitation = result['precipitation']
        precip_prob = result.get('precipitation_probability', 0)
        
        # 降水概率简写
        def precip_prob_short(prob):
            if prob == 0:
                return "🌵0%"
            elif prob < 30:
                return f"🌤️{prob}%"
            elif prob < 60:
                return f"🌦️{prob}%"
            elif prob < 80:
                return f"🌧️{prob}%"
            else:
                return f"⛈️{prob}%"
        
        precip_prob_str = precip_prob_short(precip_prob)
        
        return f"『{location} {date} {weather_emoji}{weather_desc} {temp_min}°C~{temp_max}°C 💧{precipitation}mm {precip_prob_str}』"
    else:
        return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="天气查询工具 - 查询目标城市目标时间的天气信息",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                         # 查询北京明天的天气(漂亮格式)
  %(prog)s -c shanghai             # 查询上海明天的天气
  %(prog)s -c guangzhou -d 2       # 查询广州后天的天气
  %(prog)s -c "new york"           # 查询纽约明天的天气
  %(prog)s -c hangzhou -f simple   # 以简单格式输出
  %(prog)s -c shenzhen -f json     # 以JSON格式输出
        """
    )
    
    parser.add_argument(
        "-c", "--city",
        default="beijing",
        help="城市名称 (默认: 北京). 支持中文城市名或拼音"
    )
    
    parser.add_argument(
        "-d", "--days",
        type=int,
        default=1,
        help="查询多少天后的天气 (0=今天, 1=明天, 2=后天, 默认: 1)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["json", "pretty", "simple"],
        default="pretty",
        help="输出格式: json=JSON格式, pretty=漂亮格式(默认), simple=简单单行格式"
    )
    
    parser.add_argument(
        "-l", "--list-cities",
        action="store_true",
        help="列出所有预定义的城市"
    )
    
    args = parser.parse_args()
    
    # 列出城市
    if args.list_cities:
        print("预定义城市列表:")
        for key, city in CITY_COORDINATES.items():
            print(f"  {key:12} - {city['name']}")
        return
    
    # 获取城市坐标
    city_info = get_city_coordinates(args.city)
    if not city_info:
        print(json.dumps({"error": f"未找到城市 '{args.city}' 的坐标信息"}, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    # 验证天数
    if args.days < 0 or args.days > 7:
        print(json.dumps({"error": "天数必须在 0-7 之间"}, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    # 获取天气数据
    weather_data = get_weather_forecast(
        city_info["latitude"],
        city_info["longitude"],
        args.days
    )
    
    if "error" in weather_data:
        print(format_output(weather_data, args.format))
        sys.exit(1)
    
    # 添加城市名称到结果
    weather_data["location_name"] = city_info["name"]
    weather_data["query_city"] = args.city
    
    # 输出结果
    print(format_output(weather_data, args.format))


if __name__ == "__main__":
    main()