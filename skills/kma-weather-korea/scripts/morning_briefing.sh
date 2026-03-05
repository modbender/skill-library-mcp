#!/bin/bash
# 아침 브리핑용 날씨+미세먼지 종합 스크립트
# Usage: morning_briefing.sh [nx] [ny] [측정소명]

NX=${1:-60}
NY=${2:-127}
STATION=${3:-종로구}

python3 - "$NX" "$NY" "$STATION" << 'PYEOF'
import urllib.request, urllib.parse, json, sys
from datetime import datetime, timedelta

NX, NY, STATION = sys.argv[1], sys.argv[2], sys.argv[3]
API_KEY = open("/home/scott/.config/data-go-kr/api_key").read().strip()

now = datetime.now()
if now.minute < 10:
    base = now - timedelta(hours=1)
else:
    base = now
base_date = base.strftime("%Y%m%d")
base_time = base.strftime("%H") + "00"

# 1. 초단기실황
weather = {}
try:
    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    p = urllib.parse.urlencode({"serviceKey": API_KEY, "pageNo": "1", "numOfRows": "10",
        "dataType": "JSON", "base_date": base_date, "base_time": base_time, "nx": NX, "ny": NY})
    with urllib.request.urlopen(f"{url}?{p}", timeout=10) as r:
        data = json.loads(r.read().decode())
    for item in data["response"]["body"]["items"]["item"]:
        weather[item["category"]] = item["obsrValue"]
except Exception as e:
    weather["error"] = str(e)

# 2. 단기예보 (최고/최저, 강수확률)
fcst_hours = [2, 5, 8, 11, 14, 17, 20, 23]
fcst_base = None
for h in reversed(fcst_hours):
    if now.hour >= h:
        fcst_base = h; break
fcst_date = now.strftime("%Y%m%d")
if fcst_base is None:
    fcst_base = 23; fcst_date = (now - timedelta(days=1)).strftime("%Y%m%d")

tmn, tmx, pop_max, sky_vals, pty_vals = None, None, 0, [], []
try:
    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    p = urllib.parse.urlencode({"serviceKey": API_KEY, "pageNo": "1", "numOfRows": "300",
        "dataType": "JSON", "base_date": fcst_date, "base_time": f"{fcst_base:02d}00", "nx": NX, "ny": NY})
    with urllib.request.urlopen(f"{url}?{p}", timeout=15) as r:
        data = json.loads(r.read().decode())
    today = now.strftime("%Y%m%d")
    for item in data["response"]["body"]["items"]["item"]:
        if item["fcstDate"] != today: continue
        cat, val = item["category"], item["fcstValue"]
        if cat == "TMN": tmn = val
        elif cat == "TMX": tmx = val
        elif cat == "POP": pop_max = max(pop_max, int(val))
        elif cat == "SKY": sky_vals.append(int(val))
        elif cat == "PTY": pty_vals.append(int(val))
except Exception as e:
    pass

# 3. 에어코리아
air = {}
try:
    url = "https://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"
    p = urllib.parse.urlencode({"serviceKey": API_KEY, "returnType": "json", "numOfRows": "1",
        "pageNo": "1", "stationName": STATION, "dataTerm": "DAILY", "ver": "1.0"})
    with urllib.request.urlopen(f"{url}?{p}", timeout=10) as r:
        data = json.loads(r.read().decode())
    item = data["response"]["body"]["items"][0]
    air = {k: item.get(k, "-") for k in ["pm10Value","pm25Value","pm10Grade","pm25Grade","o3Value","khaiGrade"]}
except Exception as e:
    air["error"] = str(e)

# 종합
sky_map = {1: "맑음 ☀️", 3: "구름많음 ⛅", 4: "흐림 ☁️"}
pty_map = {0: "", 1: "비 🌧️", 2: "비/눈 🌧️❄️", 3: "눈 ❄️", 4: "소나기 🌦️"}
grade_map = {"1": "좋음😊", "2": "보통🙂", "3": "나쁨😷", "4": "매우나쁨🤢"}

main_sky = max(set(sky_vals), key=sky_vals.count) if sky_vals else None
main_pty = max(pty_vals) if pty_vals else 0

result = {
    "current_temp": weather.get("T1H", "?"),
    "humidity": weather.get("REH", "?"),
    "wind_speed": weather.get("WSD", "?"),
    "precip_type": int(weather.get("PTY", "0")),
    "tmn": tmn, "tmx": tmx,
    "pop_max": pop_max,
    "sky": sky_map.get(main_sky, "?"),
    "pty": pty_map.get(main_pty, ""),
    "pm10": air.get("pm10Value", "-"),
    "pm25": air.get("pm25Value", "-"),
    "pm10_grade": grade_map.get(air.get("pm10Grade"), "?"),
    "pm25_grade": grade_map.get(air.get("pm25Grade"), "?"),
    "umbrella": pop_max >= 40 or main_pty > 0,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
PYEOF
