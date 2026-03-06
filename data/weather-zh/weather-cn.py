#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国天气网查询脚本 - Python版本
使用方法: python weather-cn.py 城市名
"""

import sys
import os
import re
import requests
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CITY_CODE_FILE = os.path.join(SCRIPT_DIR, "weather_codes.txt")

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

def error(message):
    print(f"{Colors.RED}错误: {message}{Colors.RED}", file=sys.stderr)
    sys.exit(1)

def find_city_code(city):
    """查找城市代码"""
    try:
        with open(CITY_CODE_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                parts = line.split(',')
                if len(parts) >= 2:
                    city_name, city_code = parts[0], parts[1]
                    if city_name.lower() == city.lower():
                        return city_code
    except FileNotFoundError:
        error(f"城市代码文件不存在：{CITY_CODE_FILE}")
    except Exception as e:
        error(f"读取城市代码文件失败：{e}")
    
    return None

def fetch_weather(city_code):
    """获取天气数据"""
    url = f"https://www.weather.com.cn/weather/{city_code}.shtml"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            error(f"无法获取天气数据，HTTP状态码：{response.status_code}")
        
        return response.text
    except requests.exceptions.RequestException as e:
        error(f"无法获取天气数据，请检查网络连接：{e}")

def parse_weather(html):
    """解析天气信息"""
    result = {
        'weather': '未知',
        'temp': '未知',
        'cold_index': '较适宜',
        'sport_index': '较适宜',
        'dress_index': '较冷',
        'wash_index': '适宜',
        'uv_index': '强'
    }
    
    # 提取温度 - 使用多种模式匹配，优先匹配实际网页结构
    temp_patterns = [
        r'<span>(\d+)</span>/<i>(\d+)℃</i>',
        r'<em>(\d+)</em>℃.*<em>(\d+)</em>℃',
        r'(\d+)℃.*?(\d+)℃',
        r'temp="(\d+)"',
        r'temp1="(\d+)"',
        r'temp2="(\d+)"',
        r'(\d+)/(\d+)℃',
        r'(\d+)°C.*?(\d+)°C',
        r'(\d+)°C',
    ]
    
    for pattern in temp_patterns:
        matches = re.findall(pattern, html)
        if matches:
            if len(matches[0]) == 2:
                temp_high, temp_low = matches[0]
                result['temp'] = f"{temp_high}/{temp_low}℃"
                break
            elif len(matches[0]) == 1:
                result['temp'] = f"{matches[0][0]}℃"
                break
    
    # 提取天气状况 - 优先匹配class="wea"的p标签
    weather_patterns = [
        r'<p[^>]*class="wea"[^>]*>([^<]+)</p>',
        r'<p[^>]*title="([^"]+)"[^>]*class="wea"',
        r'<title>([^<]+)天气预报',
        r'<h1[^>]*>([^<]+)</h1>',
        r'weather="([^"]+)"',
        r'wea="([^"]+)"',
    ]
    
    for pattern in weather_patterns:
        match = re.search(pattern, html)
        if match:
            result['weather'] = match.group(1).strip()
            if '天气预报' in result['weather']:
                result['weather'] = result['weather'].replace('天气预报', '').strip()
            if '，' in result['weather']:
                result['weather'] = result['weather'].split('，')[0].strip()
            break
    
    # 如果还是未知，尝试从常见天气词汇中提取
    if result['weather'] == '未知' or len(result['weather']) > 10:
        common_weather = ['晴', '多云', '阴', '小雨', '大雨', '雪', '雷阵雨', '暴雨', '雨夹雪']
        for w in common_weather:
            if w in html[:5000]:  # 只在前5000字符中搜索
                result['weather'] = w
                break
    
    # 提取生活指数
    if '极易发感冒' in html:
        result['cold_index'] = '极易发'
    elif '易发感冒' in html:
        result['cold_index'] = '易发'
    elif '较易发感冒' in html:
        result['cold_index'] = '较易发'
    elif '少发感冒' in html:
        result['cold_index'] = '少发'
    
    if '适宜运动' in html:
        result['sport_index'] = '适宜'
    elif '较适宜运动' in html:
        result['sport_index'] = '较适宜'
    elif '较不宜运动' in html:
        result['sport_index'] = '较不宜'
    elif '不宜运动' in html:
        result['sport_index'] = '不宜'
    
    if '强紫外线' in html:
        result['uv_index'] = '强'
    elif '中等紫外线' in html:
        result['uv_index'] = '中等'
    elif '弱紫外线' in html:
        result['uv_index'] = '弱'
    
    if '适宜洗车' in html:
        result['wash_index'] = '适宜'
    elif '较适宜洗车' in html:
        result['wash_index'] = '较适宜'
    elif '不宜洗车' in html:
        result['wash_index'] = '不宜'
    
    return result

def get_weather_icon(weather):
    """获取天气图标"""
    weather = weather.strip()
    if '晴' in weather and '阴' in weather:
        return '🌤️'
    elif '晴' in weather and '多云' in weather:
        return '🌤️'
    elif '多云' in weather and '晴' in weather:
        return '🌤️'
    elif '多云' in weather and '阴' in weather:
        return '☁️'
    elif '晴' in weather:
        return '☀️'
    elif '多云' in weather:
        return '⛅'
    elif '阴' in weather:
        return '☁️'
    elif '雨' in weather:
        return '🌧️'
    elif '雪' in weather:
        return '❄️'
    return '🌤️'

def format_output(city, data):
    """格式化输出"""
    weather_icon = get_weather_icon(data['weather'])
    weather = data['weather'].strip()
    
    print()
    print(f"{Colors.GREEN}═════════════════════════════════════════════════{Colors.NC}")
    print(f"{Colors.YELLOW}  {city}天气{Colors.NC}")
    print(f"{Colors.GREEN}═════════════════════════════════════════════════{Colors.NC}")
    print()
    print(f"{Colors.YELLOW}📍 今日天气（{datetime.now().strftime('%Y-%m-%d')}）{Colors.NC}")
    print(f"  {weather_icon} {weather}  |  {Colors.BLUE}温度：{data['temp']}{Colors.NC}")
    print()
    print(f"{Colors.YELLOW}📊 生活指数{Colors.NC}")
    print(f"  🤧 感冒：{data['cold_index']}")
    print(f"  🏃 运动：{data['sport_index']}")
    print(f"  👔 穿衣：{data['dress_index']}")
    print(f"  🚗 洗车：{data['wash_index']}")
    print(f"  ☀️ 紫外线：{data['uv_index']}")
    print()
    print(f"{Colors.GREEN}═════════════════════════════════════════════════{Colors.NC}")
    print()

def main():
    if len(sys.argv) < 2:
        error("请输入城市名称，例如：python weather-cn.py 成都")
    
    city = sys.argv[1]
    
    city_code = find_city_code(city)
    if not city_code:
        error(f"未找到城市 '{city}'，请检查城市名称或手动添加到城市代码文件")
    
    html = fetch_weather(city_code)
    weather_data = parse_weather(html)
    format_output(city, weather_data)

if __name__ == "__main__":
    main()
