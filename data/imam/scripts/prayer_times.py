#!/usr/bin/env python3
"""
Prayer Times Calculator for OpenClaw Imam Skill
Uses the Adhan algorithm (simplified) to compute prayer times for a given location and date.

Usage:
  python3 prayer_times.py
  python3 prayer_times.py --lat 24.8607 --lon 67.0011 --tz-offset 5.0 --json
  python3 prayer_times.py --method MWL --asr 2
"""

import argparse
import math
import datetime
import json

PRAYER_NAMES = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]

# Calculation method params: (Fajr angle, Isha angle)
METHODS = {
    "MWL":     (18.0, 17.0),
    "ISNA":    (15.0, 15.0),
    "Egypt":   (19.5, 17.5),
    "Karachi": (18.0, 18.0),
    "Makkah":  (18.5, 90.0),
    "Tehran":  (17.7, 14.0),
    "Jafari":  (16.0, 14.0),
}

def deg_to_rad(d): return d * math.pi / 180.0
def rad_to_deg(r): return r * 180.0 / math.pi

def julian_day(year, month, day):
    if month <= 2:
        year -= 1
        month += 12
    A = int(year / 100)
    B = 2 - A + int(A / 4)
    return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5

def sun_position(jd):
    D = jd - 2451545.0
    g = deg_to_rad(357.529 + 0.98560028 * D)
    q = 280.459 + 0.98564736 * D
    L = deg_to_rad(q + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))
    e = deg_to_rad(23.439 - 0.00000036 * D)
    RA = rad_to_deg(math.atan2(math.cos(e) * math.sin(L), math.cos(L))) / 15
    dec = rad_to_deg(math.asin(math.sin(e) * math.sin(L)))
    EqT = q / 15 - RA
    return dec, EqT

def compute_times(lat, lon, date, method="Karachi", asr_factor=1):
    jd = julian_day(date.year, date.month, date.day)
    dec, EqT = sun_position(jd)

    Dhuhr_ut = 12 - lon / 15 - EqT

    def hour_angle(angle, dec_rad):
        lat_rad = deg_to_rad(lat)
        cos_val = (-math.sin(deg_to_rad(angle)) - math.sin(lat_rad) * math.sin(dec_rad)) / \
                  (math.cos(lat_rad) * math.cos(dec_rad))
        cos_val = max(-1.0, min(1.0, cos_val))
        return rad_to_deg(math.acos(cos_val)) / 15

    dec_rad = deg_to_rad(dec)
    fajr_angle, isha_angle = METHODS.get(method, METHODS["Karachi"])

    T_Fajr    = Dhuhr_ut - hour_angle(fajr_angle, dec_rad)
    T_Sunrise = Dhuhr_ut - hour_angle(0.833, dec_rad)
    T_Dhuhr   = Dhuhr_ut
    asr_angle = rad_to_deg(math.atan(1.0 / (asr_factor + math.tan(abs(deg_to_rad(lat) - dec_rad)))))
    T_Asr     = Dhuhr_ut + hour_angle(-asr_angle, dec_rad)
    T_Maghrib = Dhuhr_ut + hour_angle(0.833, dec_rad)
    T_Isha    = Dhuhr_ut + hour_angle(-isha_angle, dec_rad) if isha_angle < 50 else T_Maghrib + isha_angle / 60

    def fmt(t):
        h = int(t) % 24
        m = int((t - int(t)) * 60)
        s = int(((t - int(t)) * 60 - m) * 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    return {
        "Fajr":    fmt(T_Fajr),
        "Sunrise": fmt(T_Sunrise),
        "Dhuhr":   fmt(T_Dhuhr),
        "Asr":     fmt(T_Asr),
        "Maghrib": fmt(T_Maghrib),
        "Isha":    fmt(T_Isha),
    }

def current_prayer(times, now_str):
    order = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
    for p in reversed(order):
        if now_str >= times[p]:
            return p
    return "Isha"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute Islamic prayer times")
    parser.add_argument("--lat",       type=float, default=26.4499, help="Latitude (default: Pukhraayan, UP)")
    parser.add_argument("--lon",       type=float, default=79.8481, help="Longitude (default: Pukhraayan, UP)")
    parser.add_argument("--method",    default="Karachi", choices=list(METHODS.keys()))
    parser.add_argument("--asr",       type=int, default=1, choices=[1, 2], help="1=Shafi, 2=Hanafi")
    parser.add_argument("--tz-offset", type=float, default=5.5, help="UTC offset in hours (default: IST +5.5)")
    parser.add_argument("--json",      action="store_true", help="Output as JSON")
    args = parser.parse_args()

    today = datetime.date.today()
    adjusted_lon = args.lon + args.tz_offset * 15
    times = compute_times(args.lat, adjusted_lon, today, args.method, args.asr)
    now = datetime.datetime.now().strftime("%H:%M:%S")
    current = current_prayer(times, now)

    if args.json:
        print(json.dumps({"date": str(today), "times": times, "current": current}, indent=2))
    else:
        print(f"Prayer times for {today} (UTC+{args.tz_offset}) — Method: {args.method}")
        for name, t in times.items():
            marker = " ◄ current" if name == current else ""
            print(f"  {name:<10} {t}{marker}")
