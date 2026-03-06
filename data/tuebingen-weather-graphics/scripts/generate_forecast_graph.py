#!/usr/bin/env python3
"""Generate a 5-day weather graphic for Tübingen using Open-Meteo data."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import List
from urllib import request

import matplotlib.pyplot as plt  # type: ignore

API_URL = (
    "https://api.open-meteo.com/v1/forecast?latitude=48.5216&longitude=9.0576"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
    "&timezone=Europe/Berlin"
)


def fetch_daily() -> dict:
    with request.urlopen(API_URL, timeout=20) as resp:  # noqa: S310
        return json.load(resp)


def build_graph(dates: List[dt.date], t_max: List[float], t_min: List[float], rain: List[int], output: Path) -> None:
    plt.style.use("seaborn-v0_8")
    fig, ax1 = plt.subplots(figsize=(8, 4.5), dpi=150)

    ax1.plot(dates, t_max, marker="o", color="#d95f02", label="max °C")
    ax1.plot(dates, t_min, marker="o", color="#1b9e77", label="min °C")
    ax1.fill_between(dates, t_min, t_max, color="#b3e5fc", alpha=0.3)
    ax1.set_ylabel("Temperatur (°C)")
    ax1.set_ylim(min(t_min) - 3, max(t_max) + 3)
    ax1.grid(axis="y", alpha=0.2)

    ax2 = ax1.twinx()
    ax2.bar(dates, rain, width=0.3, color="#7570b3", alpha=0.4, label="Regen %")
    ax2.set_ylabel("Regenwahrscheinlichkeit (%)")
    ax2.set_ylim(0, 100)

    ax1.set_xticks(dates)
    ax1.set_xticklabels([d.strftime("%a\n%d.%m") for d in dates])

    title = f"Tübingen 5-Tage-Ausblick (Stand {dt.datetime.now().strftime('%d.%m.%Y')})"
    ax1.set_title(title)

    lines, labels = ax1.get_legend_handles_labels()
    l2, lab2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + l2, labels + lab2, loc="upper left")

    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Tübingen 5-day weather graphic")
    parser.add_argument("--days", type=int, default=5, help="Number of days to include (default: 5)")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/weather/tuebingen_forecast.png"),
        help="Path to save the PNG graphic",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = fetch_daily()
    daily = data["daily"]

    dates = [dt.date.fromisoformat(d) for d in daily["time"][: args.days]]
    t_max = daily["temperature_2m_max"][: args.days]
    t_min = daily["temperature_2m_min"][: args.days]
    rain = daily["precipitation_probability_max"][: args.days]

    build_graph(dates, t_max, t_min, rain, args.output)
    summary = " | ".join(
        f"{d.strftime('%a %d.%m')}: {mn:.0f}/{mx:.0f}°C, Regen {r}%"
        for d, mn, mx, r in zip(dates, t_min, t_max, rain, strict=False)
    )
    print(f"Grafik gespeichert: {args.output}\n{summary}")


if __name__ == "__main__":
    main()
