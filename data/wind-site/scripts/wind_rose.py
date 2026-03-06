#!/usr/bin/env python3
"""
Plot a wind rose (direction + speed frequency) for a location.
Fetches hourly wind from Open-Meteo historical API and draws a polar wind rose.
"""
import argparse
import sys
from datetime import datetime, timedelta

try:
    import requests
    import numpy as np
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"Error: {e}. Install requests, numpy, matplotlib.", file=sys.stderr)
    sys.exit(1)


def fetch_wind_series(lat: float, lon: float, start_date: str, end_date: str):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "wind_speed_10m,wind_direction_10m",
        "timezone": "UTC",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def plot_wind_rose(directions_deg, speeds_ms, output_path: str, n_speed_bins: int = 5):
    """Draw wind rose: direction in 16 bins, speed in n_speed_bins."""
    dir_bins = np.linspace(0, 360, 17)
    speed_bins = np.linspace(0, max(speeds_ms) * 1.01 or 1, n_speed_bins + 1)
    dir_centers = (dir_bins[:-1] + dir_bins[1:]) / 2
    width = 360 / 16 * np.pi / 180
    fig, ax = plt.subplots(subplot_kw=dict(projection="polar"))
    bottom = np.zeros(16)
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, n_speed_bins))
    for i in range(n_speed_bins):
        low, high = speed_bins[i], speed_bins[i + 1]
        counts = np.zeros(16)
        for d, s in zip(directions_deg, speeds_ms):
            if np.isnan(d) or np.isnan(s):
                continue
            if low <= s < high:
                idx = int((d % 360) / (360 / 16)) % 16
                counts[idx] += 1
        total = sum(counts)
        if total > 0:
            counts = counts / total * 100
        ax.bar(dir_centers * np.pi / 180, counts, width=width, bottom=bottom, color=colors[i], label=f"{low:.1f}-{high:.1f} m/s")
        bottom += counts
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.legend(loc="upper left", bbox_to_anchor=(1.15, 1))
    ax.set_title("Wind rose (% of hours by direction and speed)")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Plot wind rose for a location (Open-Meteo historical).")
    parser.add_argument("--lat", type=float, required=True, help="Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Longitude")
    parser.add_argument("--days", type=int, default=30, help="Days of history (default 30)")
    parser.add_argument("--output", default="wind_rose.png", help="Output image path")
    args = parser.parse_args()
    end = datetime.utcnow()
    start = end - timedelta(days=args.days)
    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")
    try:
        data = fetch_wind_series(args.lat, args.lon, start_str, end_str)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    h = data.get("hourly", {})
    dirs = h.get("wind_direction_10m", [])
    speeds = h.get("wind_speed_10m", [])
    if not dirs or not speeds:
        print("No wind data in range.", file=sys.stderr)
        sys.exit(1)
    dirs = [float(x) if x is not None else np.nan for x in dirs]
    speeds = [float(x) if x is not None else np.nan for x in speeds]
    plot_wind_rose(np.array(dirs), np.array(speeds), args.output)
    print(f"Wind rose saved: {args.output} ({args.days} days, {args.lat}, {args.lon})")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
