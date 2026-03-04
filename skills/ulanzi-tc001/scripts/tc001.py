#!/usr/bin/env python3
import os
import re
import sys
import json
import argparse
from urllib.parse import urlencode
from urllib.request import Request, urlopen

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            if isinstance(cfg, dict):
                return cfg
    except Exception:
        pass
    return {}

CFG = load_config()


def load_host():
    # priority: skill config.json -> env -> default
    if CFG.get("host"):
        return CFG.get("host")
    return os.environ.get("TC001_HOST", "192.168.1.32")


def load_awtrix():
    host = CFG.get("awtrix_host") or os.environ.get("AWTRIX_HOST", "192.168.1.19")
    port = str(CFG.get("awtrix_port") or os.environ.get("AWTRIX_PORT", "17000"))
    return host, port

HOST = load_host()
BASE = f"http://{HOST}"

# Gadget -> checkbox field mapping (app_switch)
GADGET_FIELDS = {
    "time": "isTime",
    "date": "isDate",
    "weather": "isWeather",
    "bilibili": "isBilibili",
    "weibo": "isWeibo",
    "youtube": "isYoutube",
    "douyin": "isDouyin",
    "scoreboard": "isScoreBoard",
    "chronograph": "isChronograph",
    "tomato": "isTomatoClock",
    "battery": "isBattery",
    "matrix": "isTheMatrix",
    "awtrix": "isAwtrixSimulator",
    "localip": "isShowIp",
}

SYS_SELECT_FIELDS = [
    "language",
    "autoBrightness",
    "brightness",
    "nightBrightness",
    "showDurationSpeed",
    "showScrollSpeed",
    "timezone",
    "timeStyle",
    "dateFormat",
    "showWeek",
    "isSundayFirstday",
    "nightBeginHour",
    "nightBeginMinute",
    "nightEndHour",
    "nightEndMinute",
]

SYS_CHECKBOX_FIELDS = [
    "isNightMode",
]

APP_TEXT_FIELDS = [
    "cityCode",
    "bilibiliUid", "bilibiliAnimation", "bilibiliColor", "bilibiliFormat",
    "weiboUid", "weiboAnimation", "weiboColor", "weiboFormat",
    "youtubeUid", "youtubeApikey", "youtubeAnimation", "youtubeColor", "youtubeFormat",
    "douyinUid", "douyinAnimation", "douyinColor", "douyinFormat",
    "awtrixServer", "awtrixPort",
]


def http_get(path: str) -> str:
    # some devices serve settings at /?
    if path == "/":
        path = "/?"
    with urlopen(BASE + path, timeout=5) as r:
        return r.read().decode("utf-8", errors="ignore")


def http_post(path: str, data: dict) -> str:
    body = urlencode(data).encode("utf-8")
    req = Request(BASE + path, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urlopen(req, timeout=5) as r:
        return r.read().decode("utf-8", errors="ignore")


def _select_value(html: str, name: str):
    # find select block
    m = re.search(rf"<select[^>]*name=['\"]{re.escape(name)}['\"][^>]*>(.*?)</select>", html, re.S)
    if not m:
        return None
    block = m.group(1)
    m2 = re.search(r"<option[^>]*value=['\"]?([^'\"> ]+)['\"]?[^>]*selected", block)
    if not m2:
        return None
    return m2.group(1)


def _checkbox_checked(html: str, name: str) -> bool:
    # match input checkbox with checked attribute
    pattern = rf"<input[^>]*type=['\"]checkbox['\"][^>]*name=['\"]{re.escape(name)}['\"][^>]*>"
    m = re.search(pattern, html)
    if not m:
        return False
    return "checked" in m.group(0)


def _input_value(html: str, name: str):
    m = re.search(rf"<input[^>]*name=['\"]{re.escape(name)}['\"][^>]*value=['\"](.*?)['\"]", html)
    if not m:
        return ""
    return m.group(1)


def load_sys_settings():
    html = http_get("/")
    data = {}
    for f in SYS_SELECT_FIELDS:
        v = _select_value(html, f)
        if v is not None:
            data[f] = v
    for f in SYS_CHECKBOX_FIELDS:
        data[f] = "on" if _checkbox_checked(html, f) else ""
    return data


def load_app_settings():
    html = http_get("/app_switch")
    data = {}
    for name, field in GADGET_FIELDS.items():
        data[field] = "on" if _checkbox_checked(html, field) else ""
    for f in APP_TEXT_FIELDS:
        data[f] = _input_value(html, f)
    return data


def save_sys_settings(data: dict):
    payload = {"page": "sys_setting"}
    payload.update(data)
    return http_post("/", payload)


def save_app_settings(data: dict):
    payload = {"page": "app_switch"}
    payload.update(data)
    return http_post("/app_switch", payload)


def cmd_status(_args):
    sysd = load_sys_settings()
    appd = load_app_settings()
    out = {
        "sys": sysd,
        "gadgets_on": [k for k, f in GADGET_FIELDS.items() if appd.get(f) == "on"],
        "gadgets_off": [k for k, f in GADGET_FIELDS.items() if appd.get(f) != "on"],
    }
    print(json.dumps(out, indent=2))


def cmd_gadgets(args):
    if args.sub == "list":
        print(" ".join(GADGET_FIELDS.keys()))
        return
    appd = load_app_settings()
    if args.sub == "on":
        print(" ".join([k for k, f in GADGET_FIELDS.items() if appd.get(f) == "on"]))
        return
    if args.sub == "off":
        print(" ".join([k for k, f in GADGET_FIELDS.items() if appd.get(f) != "on"]))
        return


def cmd_gadget_toggle(args):
    name = args.name.lower()
    if name not in GADGET_FIELDS:
        print(f"Unknown gadget: {name}")
        sys.exit(1)
    appd = load_app_settings()
    field = GADGET_FIELDS[name]
    appd[field] = "on" if args.state == "on" else ""
    save_app_settings(appd)
    print(f"{name} -> {args.state}")


def cmd_brightness(args):
    sysd = load_sys_settings()
    if args.mode == "auto":
        sysd["autoBrightness"] = "0"
    else:
        sysd["autoBrightness"] = "1"
        # map 0-100 to 0-10
        pct = max(0, min(100, int(args.value)))
        sysd["brightness"] = str(round(pct / 10))
    save_sys_settings(sysd)
    print("ok")


def cmd_nightmode(args):
    sysd = load_sys_settings()
    if args.action in ("on", "off"):
        sysd["isNightMode"] = "on" if args.action == "on" else ""
    elif args.action == "start":
        h, m = args.value.split(":")
        sysd["nightBeginHour"] = str(int(h))
        sysd["nightBeginMinute"] = str(int(m))
    elif args.action == "end":
        h, m = args.value.split(":")
        sysd["nightEndHour"] = str(int(h))
        sysd["nightEndMinute"] = str(int(m))
    save_sys_settings(sysd)
    print("ok")


def cmd_timezone(args):
    # expects e.g. GMT-3
    tz = args.value.strip()
    # map to select value based on list in page
    tz_map = {
        "AUTO": "0",
        "GMT-12": "1", "GMT-11": "2", "GMT-10": "3", "GMT-9:30": "26", "GMT-9": "4",
        "GMT-8": "5", "GMT-7": "6", "GMT-6": "7", "GMT-5": "8", "GMT-4": "9",
        "GMT-3:30": "27", "GMT-3": "10", "GMT-2": "11", "GMT-1": "12", "GMT+0": "13",
        "GMT+1": "14", "GMT+2": "15", "GMT+3": "16", "GMT+3:30": "28", "GMT+4": "17",
        "GMT+4:30": "29", "GMT+5": "18", "GMT+5:30": "30", "GMT+5:45": "31",
        "GMT+6": "19", "GMT+6:30": "32", "GMT+7": "20", "GMT+8": "21", "GMT+8:45": "33",
        "GMT+9": "22", "GMT+9:30": "34", "GMT+10": "23", "GMT+10:30": "35", "GMT+11": "24",
        "GMT+12": "25", "GMT+12:45": "36",
    }
    key = tz.upper()
    if key == "AUTO" or key == "AUTO TIMEZONE":
        key = "AUTO"
    if key not in tz_map:
        print("Unknown timezone. Use e.g. GMT-3 or AUTO.")
        sys.exit(1)
    sysd = load_sys_settings()
    sysd["timezone"] = tz_map[key]
    save_sys_settings(sysd)
    print("ok")


def cmd_switch_speed(args):
    # map seconds to select values
    sec_map = {"noswitch": "0", "10": "1", "15": "2", "20": "3", "25": "4", "30": "5",
               "35": "6", "40": "7", "45": "8", "50": "9", "55": "10", "60": "11"}
    val = args.value.lower()
    if val not in sec_map:
        print("Use 10,15,20,25,30,35,40,45,50,55,60 or noswitch")
        sys.exit(1)
    sysd = load_sys_settings()
    sysd["showDurationSpeed"] = sec_map[val]
    save_sys_settings(sysd)
    print("ok")


def cmd_scroll_speed(args):
    n = max(0, min(10, int(args.value)))
    sysd = load_sys_settings()
    sysd["showScrollSpeed"] = str(n)
    save_sys_settings(sysd)
    print("ok")


def _map_simple(value, mapping, label):
    key = value.strip().lower()
    if key not in mapping:
        print(f"Unknown {label}. Options: {', '.join(mapping.keys())}")
        sys.exit(1)
    return mapping[key]


def cmd_sys_set(args):
    sysd = load_sys_settings()
    field = args.field.lower()
    val = args.value

    if field in ("language",):
        sysd["language"] = _map_simple(val, {"chinese": "0", "english": "1"}, "language")
    elif field in ("autobrightness",):
        sysd["autoBrightness"] = _map_simple(val, {"auto": "0", "manual": "1"}, "autobrightness")
    elif field in ("brightness",):
        pct = max(0, min(100, int(val)))
        sysd["brightness"] = str(round(pct / 10))
    elif field in ("nightbrightness",):
        pct = max(0, min(100, int(val)))
        sysd["nightBrightness"] = str(round(pct / 10))
    elif field in ("switchspeed",):
        sec_map = {"noswitch": "0", "10": "1", "15": "2", "20": "3", "25": "4", "30": "5",
                   "35": "6", "40": "7", "45": "8", "50": "9", "55": "10", "60": "11"}
        sysd["showDurationSpeed"] = _map_simple(val, sec_map, "switchspeed")
    elif field in ("scrollspeed",):
        n = max(0, min(10, int(val)))
        sysd["showScrollSpeed"] = str(n)
    elif field in ("timezone",):
        tz_map = {
            "auto": "0", "auto timezone": "0",
            "gmt-12": "1", "gmt-11": "2", "gmt-10": "3", "gmt-9:30": "26", "gmt-9": "4",
            "gmt-8": "5", "gmt-7": "6", "gmt-6": "7", "gmt-5": "8", "gmt-4": "9",
            "gmt-3:30": "27", "gmt-3": "10", "gmt-2": "11", "gmt-1": "12", "gmt+0": "13",
            "gmt+1": "14", "gmt+2": "15", "gmt+3": "16", "gmt+3:30": "28", "gmt+4": "17",
            "gmt+4:30": "29", "gmt+5": "18", "gmt+5:30": "30", "gmt+5:45": "31",
            "gmt+6": "19", "gmt+6:30": "32", "gmt+7": "20", "gmt+8": "21", "gmt+8:45": "33",
            "gmt+9": "22", "gmt+9:30": "34", "gmt+10": "23", "gmt+10:30": "35", "gmt+11": "24",
            "gmt+12": "25", "gmt+12:45": "36",
        }
        sysd["timezone"] = _map_simple(val, tz_map, "timezone")
    elif field in ("timeformat",):
        sysd["timeStyle"] = _map_simple(val, {"hh:mm": "0", "hh:mm:ss": "1"}, "timeformat")
    elif field in ("dateformat",):
        sysd["dateFormat"] = _map_simple(val, {"mm/dd": "0", "dd/mm": "1"}, "dateformat")
    elif field in ("showweek",):
        sysd["showWeek"] = _map_simple(val, {"show": "0", "hide": "1", "no": "1"}, "showweek")
    elif field in ("firstday",):
        sysd["isSundayFirstday"] = _map_simple(val, {"sunday": "0", "monday": "1"}, "firstday")
    elif field in ("nightmode",):
        sysd["isNightMode"] = "on" if val.lower() in ("on", "1", "true", "yes") else ""
    elif field in ("nightstart",):
        h, m = val.split(":")
        sysd["nightBeginHour"] = str(int(h))
        sysd["nightBeginMinute"] = str(int(m))
    elif field in ("nightend",):
        h, m = val.split(":")
        sysd["nightEndHour"] = str(int(h))
        sysd["nightEndMinute"] = str(int(m))
    else:
        print("Unknown sys field")
        sys.exit(1)

    save_sys_settings(sysd)
    print("ok")


def cmd_app_set(args):
    appd = load_app_settings()
    field = args.field.lower()
    val = args.value

    anim_map = {"swipe": "0", "swipe left": "0", "scroll": "1"}
    color_map = {"default": "0", "red": "1", "orange": "2", "yellow": "3", "green": "4", "cyan": "5", "blue": "6", "purple": "7"}
    fmt_map = {"none": "0", "format": "1", "number": "1", "numberformat": "1"}

    name_map = {
        "citycode": "cityCode",
        "bilibili_uid": "bilibiliUid",
        "bilibili_animation": "bilibiliAnimation",
        "bilibili_color": "bilibiliColor",
        "bilibili_format": "bilibiliFormat",
        "weibo_uid": "weiboUid",
        "weibo_animation": "weiboAnimation",
        "weibo_color": "weiboColor",
        "weibo_format": "weiboFormat",
        "youtube_uid": "youtubeUid",
        "youtube_apikey": "youtubeApikey",
        "youtube_animation": "youtubeAnimation",
        "youtube_color": "youtubeColor",
        "youtube_format": "youtubeFormat",
        "douyin_uid": "douyinUid",
        "douyin_animation": "douyinAnimation",
        "douyin_color": "douyinColor",
        "douyin_format": "douyinFormat",
        "awtrix_server": "awtrixServer",
        "awtrix_port": "awtrixPort",
        "showlocalip": "isShowIp",
    }

    if field not in name_map:
        print("Unknown app field")
        sys.exit(1)

    target = name_map[field]
    if target in ("bilibiliAnimation", "weiboAnimation", "youtubeAnimation", "douyinAnimation"):
        appd[target] = _map_simple(val, anim_map, "animation")
    elif target in ("bilibiliColor", "weiboColor", "youtubeColor", "douyinColor"):
        appd[target] = _map_simple(val, color_map, "color")
    elif target in ("bilibiliFormat", "weiboFormat", "youtubeFormat", "douyinFormat"):
        appd[target] = _map_simple(val, fmt_map, "format")
    elif target == "isShowIp":
        appd[target] = "on" if val.lower() in ("on", "1", "true", "yes") else ""
    else:
        appd[target] = val

    save_app_settings(appd)
    print("ok")


def cmd_weather(args):
    # Geocode via Open-Meteo
    city = args.city
    city_q = urlencode({"name": city, "count": 1, "language": "pt", "format": "json"})
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?{city_q}"
    import ssl
    ctx = ssl._create_unverified_context()
    with urlopen(geo_url, timeout=8, context=ctx) as r:
        geo = json.loads(r.read().decode("utf-8"))
    if not geo.get("results"):
        print("City not found")
        sys.exit(1)
    loc = geo["results"][0]
    lat, lon = loc["latitude"], loc["longitude"]
    name = loc.get("name", city)

    wx_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&timezone=America%2FSao_Paulo"
    with urlopen(wx_url, timeout=8, context=ctx) as r:
        wx = json.loads(r.read().decode("utf-8"))
    temp = wx["current"]["temperature_2m"]

    text = f"{name} {temp}°C"

    aw_host, aw_port = load_awtrix()
    api = f"http://{aw_host}:{aw_port}/api/v3/notify"
    payload = {
        "data": text,
        "color": [0, 255, 255],
        "duration": 5,
        "stack": True,
        "force": True
    }
    body = json.dumps(payload).encode("utf-8")
    req = Request(api, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    with urlopen(req, timeout=8) as r:
        r.read()
    print(text)


def build_parser():
    p = argparse.ArgumentParser(description="Control Ulanzi TC001 via local HTTP")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("status")

    g = sub.add_parser("gadgets")
    gsub = g.add_subparsers(dest="sub")
    gsub.add_parser("list")
    gsub.add_parser("on")
    gsub.add_parser("off")

    gt = sub.add_parser("gadget")
    gt.add_argument("state", choices=["on", "off"])
    gt.add_argument("name")

    b = sub.add_parser("brightness")
    b.add_argument("mode", choices=["auto", "manual"])
    b.add_argument("value", nargs="?")

    nm = sub.add_parser("nightmode")
    nm.add_argument("action", choices=["on", "off", "start", "end"])
    nm.add_argument("value", nargs="?")

    tz = sub.add_parser("timezone")
    tz.add_argument("value")

    ss = sub.add_parser("switch")
    ss.add_argument("value")

    sc = sub.add_parser("scroll")
    sc.add_argument("value")

    sset = sub.add_parser("sys")
    sset.add_argument("field")
    sset.add_argument("value")

    aset = sub.add_parser("app")
    aset.add_argument("field")
    aset.add_argument("value")

    w = sub.add_parser("weather")
    w.add_argument("city")

    return p


def main():
    p = build_parser()
    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        sys.exit(1)
    if args.cmd == "status":
        cmd_status(args)
    elif args.cmd == "gadgets":
        cmd_gadgets(args)
    elif args.cmd == "gadget":
        cmd_gadget_toggle(args)
    elif args.cmd == "brightness":
        cmd_brightness(args)
    elif args.cmd == "nightmode":
        cmd_nightmode(args)
    elif args.cmd == "timezone":
        cmd_timezone(args)
    elif args.cmd == "switch":
        cmd_switch_speed(args)
    elif args.cmd == "scroll":
        cmd_scroll_speed(args)
    elif args.cmd == "sys":
        cmd_sys_set(args)
    elif args.cmd == "app":
        cmd_app_set(args)
    elif args.cmd == "weather":
        cmd_weather(args)
    else:
        p.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
