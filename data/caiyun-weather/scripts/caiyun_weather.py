#!/usr/bin/env python3
"""Caiyun Weather API client for OpenClaw skill."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timedelta


API_BASE = "https://api.caiyunapp.com/v2.6"

# Built-in city coordinates (lng, lat)
CITY_COORDS = {
    "北京": (116.4074, 39.9042), "beijing": (116.4074, 39.9042),
    "上海": (121.4737, 31.2304), "shanghai": (121.4737, 31.2304),
    "广州": (113.2644, 23.1291), "guangzhou": (113.2644, 23.1291),
    "深圳": (114.0579, 22.5431), "shenzhen": (114.0579, 22.5431),
    "杭州": (120.1551, 30.2741), "hangzhou": (120.1551, 30.2741),
    "成都": (104.0665, 30.5728), "chengdu": (104.0665, 30.5728),
    "武汉": (114.3054, 30.5931), "wuhan": (114.3054, 30.5931),
    "南京": (118.7969, 32.0603), "nanjing": (118.7969, 32.0603),
    "重庆": (106.5516, 29.5630), "chongqing": (106.5516, 29.5630),
    "西安": (108.9402, 34.2615), "xian": (108.9402, 34.2615),
    "天津": (117.1901, 39.1256), "tianjin": (117.1901, 39.1256),
    "苏州": (120.5853, 31.2989), "suzhou": (120.5853, 31.2989),
    "郑州": (113.6254, 34.7466), "zhengzhou": (113.6254, 34.7466),
    "长沙": (112.9388, 28.2282), "changsha": (112.9388, 28.2282),
    "青岛": (120.3826, 36.0671), "qingdao": (120.3826, 36.0671),
    "大连": (121.6147, 38.9140), "dalian": (121.6147, 38.9140),
    "厦门": (118.0894, 24.4798), "xiamen": (118.0894, 24.4798),
    "昆明": (102.8329, 25.0389), "kunming": (102.8329, 25.0389),
    "贵阳": (106.6302, 26.6477), "guiyang": (106.6302, 26.6477),
    "哈尔滨": (126.5350, 45.8038), "haerbin": (126.5350, 45.8038),
    "沈阳": (123.4315, 41.8057), "shenyang": (123.4315, 41.8057),
    "长春": (125.3235, 43.8171), "changchun": (125.3235, 43.8171),
    "福州": (119.2965, 26.0745), "fuzhou": (119.2965, 26.0745),
    "合肥": (117.2272, 31.8206), "hefei": (117.2272, 31.8206),
    "济南": (117.0009, 36.6758), "jinan": (117.0009, 36.6758),
    "南昌": (115.8581, 28.6820), "nanchang": (115.8581, 28.6820),
    "石家庄": (114.5149, 38.0428), "shijiazhuang": (114.5149, 38.0428),
    "太原": (112.5489, 37.8706), "taiyuan": (112.5489, 37.8706),
    "呼和浩特": (111.7490, 40.8424), "huhehaote": (111.7490, 40.8424),
    "南宁": (108.3200, 22.8240), "nanning": (108.3200, 22.8240),
    "海口": (110.3494, 20.0174), "haikou": (110.3494, 20.0174),
    "三亚": (109.5120, 18.2528), "sanya": (109.5120, 18.2528),
    "拉萨": (91.1322, 29.6600), "lasa": (91.1322, 29.6600),
    "乌鲁木齐": (87.6168, 43.8256), "wulumuqi": (87.6168, 43.8256),
    "兰州": (103.8343, 36.0611), "lanzhou": (103.8343, 36.0611),
    "西宁": (101.7782, 36.6171), "xining": (101.7782, 36.6171),
    "银川": (106.2782, 38.4664), "yinchuan": (106.2782, 38.4664),
    "香港": (114.1694, 22.3193), "hongkong": (114.1694, 22.3193),
    "澳门": (113.5439, 22.1987), "macau": (113.5439, 22.1987),
    "台北": (121.5654, 25.0330), "taipei": (121.5654, 25.0330),
    "珠海": (113.5767, 22.2710), "zhuhai": (113.5767, 22.2710),
    "东莞": (113.7518, 23.0208), "dongguan": (113.7518, 23.0208),
    "佛山": (113.1214, 23.0218), "foshan": (113.1214, 23.0218),
    "无锡": (120.3119, 31.4912), "wuxi": (120.3119, 31.4912),
    "宁波": (121.5440, 29.8683), "ningbo": (121.5440, 29.8683),
    "温州": (120.6994, 28.0015), "wenzhou": (120.6994, 28.0015),
}


def get_token():
    token = os.environ.get("CAIYUN_WEATHER_API_TOKEN")
    if not token:
        print("Error: CAIYUN_WEATHER_API_TOKEN environment variable is not set.", file=sys.stderr)
        print("Apply for a free API key at: https://docs.caiyunapp.com/weather-api/", file=sys.stderr)
        sys.exit(1)
    return token


def geocode_city(city_name):
    """Look up city coordinates using Nominatim (OpenStreetMap) as fallback."""
    encoded = urllib.parse.quote(city_name)
    url = f"https://nominatim.openstreetmap.org/search?q={encoded}&format=json&limit=1"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "caiyun-weather-skill/1.0")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            results = json.loads(resp.read().decode("utf-8"))
            if results:
                lat = float(results[0]["lat"])
                lng = float(results[0]["lon"])
                name = results[0].get("display_name", city_name).split(",")[0]
                return lng, lat, name
    except Exception:
        pass
    return None, None, None


def resolve_location(args):
    """Resolve lng/lat from --city or --lng/--lat arguments."""
    if args.city:
        city_key = args.city.strip().lower()
        if city_key in CITY_COORDS:
            lng, lat = CITY_COORDS[city_key]
            return lng, lat
        # Also try the original case
        if args.city.strip() in CITY_COORDS:
            lng, lat = CITY_COORDS[args.city.strip()]
            return lng, lat
        # Fallback: geocode via Nominatim
        lng, lat, name = geocode_city(args.city)
        if lng is not None:
            return lng, lat
        print(f"Error: Cannot find coordinates for city '{args.city}'.", file=sys.stderr)
        print("Please use --lng and --lat to specify coordinates manually.", file=sys.stderr)
        sys.exit(1)
    elif args.lng is not None and args.lat is not None:
        return args.lng, args.lat
    else:
        print("Error: Please specify --city <name> or both --lng and --lat.", file=sys.stderr)
        sys.exit(1)


def make_request(url, params=None):
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{query}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "caiyun-weather-skill/1.0")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection Error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def format_percent(value):
    return f"{value * 100:.0f}%"


def cmd_realtime(args):
    token = get_token()
    lng, lat = resolve_location(args)
    url = f"{API_BASE}/{token}/{lng},{lat}/realtime"
    data = make_request(url, {"lang": "en_US", "unit": "metric:v2"})
    r = data["result"]["realtime"]
    print(f"""=== Realtime Weather ===
Temperature: {r['temperature']}°C
Humidity: {format_percent(r['humidity'])}
Wind: {r['wind']['speed']} km/h, Direction {r['wind']['direction']}°
Precipitation: {r['precipitation']['local']['intensity']} mm/hr
Air Quality:
  PM2.5: {r['air_quality']['pm25']} μg/m³
  PM10: {r['air_quality']['pm10']} μg/m³
  O3: {r['air_quality']['o3']} μg/m³
  SO2: {r['air_quality']['so2']} μg/m³
  NO2: {r['air_quality']['no2']} μg/m³
  CO: {r['air_quality']['co']} mg/m³
  AQI (China): {r['air_quality']['aqi']['chn']}
  AQI (USA): {r['air_quality']['aqi']['usa']}
Life Index:
  UV: {r['life_index']['ultraviolet']['desc']}
  Comfort: {r['life_index']['comfort']['desc']}""")


def cmd_hourly(args):
    token = get_token()
    lng, lat = resolve_location(args)
    url = f"{API_BASE}/{token}/{lng},{lat}/hourly"
    data = make_request(url, {"hourlysteps": "72", "lang": "en_US", "unit": "metric:v2"})
    hourly = data["result"]["hourly"]
    print("=== 72-Hour Forecast ===")
    for i in range(len(hourly["temperature"])):
        t = hourly["temperature"][i]
        sky = hourly["skycon"][i]["value"]
        rain = hourly["precipitation"][i]["probability"]
        wind = hourly["wind"][i]
        print(f"""
Time: {t['datetime']}
Temperature: {t['value']}°C
Weather: {sky}
Rain Probability: {rain}%
Wind: {wind['speed']} km/h, {wind['direction']}°
------------------------""")


def cmd_weekly(args):
    token = get_token()
    lng, lat = resolve_location(args)
    url = f"{API_BASE}/{token}/{lng},{lat}/daily"
    data = make_request(url, {"dailysteps": "7", "lang": "en_US", "unit": "metric:v2"})
    daily = data["result"]["daily"]
    print("=== 7-Day Forecast ===")
    for i in range(len(daily["temperature"])):
        temp = daily["temperature"][i]
        date = temp["date"].split("T")[0]
        sky = daily["skycon"][i]["value"]
        rain = daily["precipitation"][i]["probability"]
        print(f"""
Date: {date}
Temperature: {temp['min']}°C ~ {temp['max']}°C
Weather: {sky}
Rain Probability: {rain}%
------------------------""")


def cmd_history(args):
    token = get_token()
    lng, lat = resolve_location(args)
    timestamp = int((datetime.now() - timedelta(hours=24)).timestamp())
    url = f"{API_BASE}/{token}/{lng},{lat}/hourly"
    data = make_request(url, {
        "hourlysteps": "24",
        "begin": str(timestamp),
        "lang": "en_US",
        "unit": "metric:v2",
    })
    hourly = data["result"]["hourly"]
    print("=== Past 24-Hour Weather ===")
    for i in range(len(hourly["temperature"])):
        t = hourly["temperature"][i]
        sky = hourly["skycon"][i]["value"]
        print(f"""
Time: {t['datetime']}
Temperature: {t['value']}°C
Weather: {sky}
------------------------""")


def cmd_alerts(args):
    token = get_token()
    lng, lat = resolve_location(args)
    url = f"{API_BASE}/{token}/{lng},{lat}/weather"
    data = make_request(url, {"alert": "true", "lang": "en_US", "unit": "metric:v2"})
    alerts = data["result"].get("alert", {}).get("content", [])
    if not alerts:
        print("No active weather alerts.")
        return
    print("=== Weather Alerts ===")
    for alert in alerts:
        print(f"""
Title: {alert.get('title', 'N/A')}
Code: {alert.get('code', 'N/A')}
Status: {alert.get('status', 'N/A')}
Description: {alert.get('description', 'N/A')}
------------------------""")


def main():
    parser = argparse.ArgumentParser(description="Caiyun Weather API client")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name, func in [
        ("realtime", cmd_realtime),
        ("hourly", cmd_hourly),
        ("weekly", cmd_weekly),
        ("history", cmd_history),
        ("alerts", cmd_alerts),
    ]:
        sub = subparsers.add_parser(name)
        sub.add_argument("--city", type=str, help="City name (Chinese or English, e.g. 北京 or beijing)")
        sub.add_argument("--lng", type=float, help="Longitude (use with --lat)")
        sub.add_argument("--lat", type=float, help="Latitude (use with --lng)")
        sub.set_defaults(func=func)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
