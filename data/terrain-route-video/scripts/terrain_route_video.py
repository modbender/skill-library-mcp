#!/usr/bin/env python3
"""Generate a terrain-style driving route video (no Remotion).

Pipeline:
- OSRM public API: build driving route geometry between stops
- OpenTopoMap tiles: stitch a terrain basemap
- Matplotlib: render frames (route draw, fly-follow camera, labels)
- FFmpeg: encode MP4

This script is designed to be run from a *project folder* (not from inside the skill).

Example:
  python terrain_route_video.py \
    --stops stops.json \
    --out out.mp4 \
    --size 1600x900 \
    --fps 30 --duration 12 \
    --title "江汉平原到洞庭湖 · 足迹" \
    --subtitle "襄阳 → 老河口 → 荆州 → 监利 → 洪湖·峰口镇 → 岳阳"

stops.json format:
  {
    "stops": [
      {"id":"01","name":"襄阳","lon":112.1163785,"lat":32.0109980},
      ...
    ]
  }
"""

from __future__ import annotations

import argparse
import io
import json
import math
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

# matplotlib must be imported after setting backend
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

from PIL import Image, ImageEnhance
import requests


@dataclass
class Stop:
    id: str
    name: str
    lon: float
    lat: float


def mercator(lon: float, lat: float) -> Tuple[float, float]:
    x = math.radians(lon)
    lat = max(min(lat, 85.0), -85.0)
    y = math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return x, y


def inv_mercator(x: float, y: float) -> Tuple[float, float]:
    lon = math.degrees(x)
    lat = math.degrees(2 * math.atan(math.exp(y)) - math.pi / 2)
    return lon, lat


def lonlat_to_tile(lon: float, lat: float, z: int) -> Tuple[int, int]:
    lat_rad = math.radians(lat)
    n = 2**z
    xt = int((lon + 180.0) / 360.0 * n)
    yt = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xt, yt


def tile_to_lonlat(x: int, y: int, z: int) -> Tuple[float, float]:
    n = 2**z
    lon = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat = math.degrees(lat_rad)
    return lon, lat


def fetch_osrm_route(stops: List[Stop], session: requests.Session) -> np.ndarray:
    """Return route coords as Nx2 [lon,lat] from OSRM, leg-by-leg."""
    coords: List[List[float]] = []
    for i in range(len(stops) - 1):
        a = stops[i]
        b = stops[i + 1]
        url = (
            "https://router.project-osrm.org/route/v1/driving/"
            f"{a.lon},{a.lat};{b.lon},{b.lat}"
            "?overview=full&geometries=geojson"
        )
        r = session.get(url, timeout=30)
        r.raise_for_status()
        j = r.json()
        c = j["routes"][0]["geometry"]["coordinates"]
        if i == 0:
            coords.extend(c)
        else:
            coords.extend(c[1:])
    return np.asarray(coords, dtype=np.float64)


def _kml_findall(elem: ET.Element, local_name: str) -> List[ET.Element]:
    """Find all elements by local tag name (namespace-agnostic)."""
    out: List[ET.Element] = []
    for e in elem.iter():
        if e.tag.split("}")[-1] == local_name:
            out.append(e)
    return out


def load_route_from_gpx(path: str) -> np.ndarray:
    """Load route as Nx2 [lon,lat] from a GPX file.

    Supports:
    - <trk><trkseg><trkpt lon=".." lat=".."/></trkseg></trk>
    - <rte><rtept lon=".." lat=".."/></rte>
    """
    root = ET.parse(path).getroot()

    pts: List[Tuple[float, float]] = []
    # prefer trackpoints
    for trkpt in _kml_findall(root, "trkpt"):
        lon = trkpt.attrib.get("lon")
        lat = trkpt.attrib.get("lat")
        if lon is None or lat is None:
            continue
        pts.append((float(lon), float(lat)))

    # fallback to routepoints
    if not pts:
        for rtept in _kml_findall(root, "rtept"):
            lon = rtept.attrib.get("lon")
            lat = rtept.attrib.get("lat")
            if lon is None or lat is None:
                continue
            pts.append((float(lon), float(lat)))

    if len(pts) < 2:
        raise ValueError(f"GPX has insufficient points: {path}")

    return np.asarray(pts, dtype=np.float64)


def load_route_from_kml(path: str) -> np.ndarray:
    """Load route as Nx2 [lon,lat] from a KML file.

    Supported encodings:
    1) Standard KML: <LineString><coordinates>lon,lat[,alt] ...</coordinates></LineString>
    2) Google extension: <gx:Track><gx:coord>lon lat alt</gx:coord>...</gx:Track>

    For (1), coordinates are comma-separated tuples separated by whitespace.
    For (2), gx:coord text is space-separated "lon lat alt".
    """
    root = ET.parse(path).getroot()

    # (1) LineString coordinates
    coords_text: Optional[str] = None
    for ls in _kml_findall(root, "LineString"):
        coords = None
        for c in _kml_findall(ls, "coordinates"):
            coords = c
            break
        if coords is not None and coords.text and coords.text.strip():
            coords_text = coords.text
            break

    pts: List[Tuple[float, float]] = []
    if coords_text:
        for token in coords_text.replace("\n", " ").replace("\t", " ").split():
            parts = token.split(",")
            if len(parts) < 2:
                continue
            lon = float(parts[0])
            lat = float(parts[1])
            pts.append((lon, lat))

    # (2) gx:Track gx:coord
    if not pts:
        for gxcoord in _kml_findall(root, "coord"):
            if not gxcoord.text:
                continue
            parts = gxcoord.text.strip().split()
            if len(parts) < 2:
                continue
            lon = float(parts[0])
            lat = float(parts[1])
            pts.append((lon, lat))

    if len(pts) < 2:
        raise ValueError(f"KML has insufficient route geometry (LineString/Track): {path}")

    return np.asarray(pts, dtype=np.float64)


def load_route_from_file(path: str) -> np.ndarray:
    p = str(path)
    ext = Path(p).suffix.lower()
    if ext == ".gpx":
        return load_route_from_gpx(p)
    if ext in (".kml", ".kmz"):
        if ext == ".kmz":
            raise ValueError("KMZ is not supported yet; please provide a .kml file")
        return load_route_from_kml(p)
    raise ValueError(f"Unsupported route file type: {ext} (expected .gpx or .kml)")


def route_cumulative(route_xy: np.ndarray) -> Tuple[np.ndarray, float]:
    seg = route_xy[1:] - route_xy[:-1]
    seg_len = np.sqrt((seg**2).sum(axis=1))
    cum = np.concatenate([[0.0], np.cumsum(seg_len)])
    return cum, float(cum[-1])


def point_at_s(route_xy: np.ndarray, cum: np.ndarray, total: float, s: float) -> np.ndarray:
    s = float(np.clip(s, 0, total))
    idx = int(np.searchsorted(cum, s, side="left"))
    if idx <= 0:
        return route_xy[0]
    if idx >= len(cum):
        return route_xy[-1]
    s0, s1 = cum[idx - 1], cum[idx]
    t = 0.0 if s1 == s0 else (s - s0) / (s1 - s0)
    return route_xy[idx - 1] * (1 - t) + route_xy[idx] * t


def polyline_up_to_s(route_xy: np.ndarray, cum: np.ndarray, total: float, s: float) -> np.ndarray:
    s = float(np.clip(s, 0, total))
    idx = int(np.searchsorted(cum, s, side="left"))
    if idx <= 1:
        return route_xy[:2]
    pts = route_xy[:idx].copy()
    pts[-1] = point_at_s(route_xy, cum, total, s)
    return pts


def nearest_route_s(route_xy: np.ndarray, cum: np.ndarray, lon: float, lat: float) -> float:
    x, y = mercator(lon, lat)
    d = np.sqrt(((route_xy - np.array([x, y])) ** 2).sum(axis=1))
    i = int(d.argmin())
    return float(cum[i])


def ensure_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found in PATH")


def build_basemap(
    minx_all: float,
    maxx_all: float,
    miny_all: float,
    maxy_all: float,
    session: requests.Session,
    zoom: int,
    tile_cache_dir: Path,
    *,
    color_mult: Optional[float] = None,
    contrast_mult: Optional[float] = None,
    sharpness_mult: Optional[float] = None,
) -> Tuple[np.ndarray, Tuple[float, float, float, float]]:
    """Fetch terrain tiles (OpenTopoMap), stitch, then return np image + mercator extent."""

    tile_cache_dir.mkdir(parents=True, exist_ok=True)

    pad = 0.20
    mx0 = minx_all - (maxx_all - minx_all) * pad
    mx1 = maxx_all + (maxx_all - minx_all) * pad
    my0 = miny_all - (maxy_all - miny_all) * pad
    my1 = maxy_all + (maxy_all - miny_all) * pad

    lon0, lat0 = inv_mercator(mx0, my0)
    lon1, lat1 = inv_mercator(mx1, my1)

    minlon, maxlon = min(lon0, lon1), max(lon0, lon1)
    minlat, maxlat = min(lat0, lat1), max(lat0, lat1)

    x0, y1 = lonlat_to_tile(minlon, minlat, zoom)
    x1, y0 = lonlat_to_tile(maxlon, maxlat, zoom)

    tx0, tx1 = min(x0, x1), max(x0, x1)
    ty0, ty1 = min(y0, y1), max(y0, y1)

    tile_size = 256
    cols = tx1 - tx0 + 1
    rows = ty1 - ty0 + 1

    basemap = Image.new("RGB", (cols * tile_size, rows * tile_size))

    for iy, ty in enumerate(range(ty0, ty1 + 1)):
        for ix, tx in enumerate(range(tx0, tx1 + 1)):
            tile_path = tile_cache_dir / f"z{zoom}_{tx}_{ty}.png"
            if tile_path.exists():
                tile = Image.open(tile_path).convert("RGB")
            else:
                url = f"https://a.tile.opentopomap.org/{zoom}/{tx}/{ty}.png"
                r = session.get(url, timeout=30)
                r.raise_for_status()
                tile = Image.open(io.BytesIO(r.content)).convert("RGB")
                try:
                    tile.save(tile_path)
                except Exception:
                    pass
            basemap.paste(tile, (ix * tile_size, iy * tile_size))

    # Mercator extent of stitched tiles
    lon_left, lat_top = tile_to_lonlat(tx0, ty0, zoom)
    lon_right, lat_bottom = tile_to_lonlat(tx1 + 1, ty1 + 1, zoom)
    mx0e, my0e = mercator(lon_left, lat_bottom)
    mx1e, my1e = mercator(lon_right, lat_top)
    basemap_extent = (mx0e, mx1e, my0e, my1e)

    # Reduce map noise a bit, but keep labels readable.
    # At low zoom, aggressive desaturation/contrast reduction makes text illegible.
    if zoom >= 13:
        color_default = 0.70
        contrast_default = 0.95
        sharp_default = 1.15
    else:
        # keep close to original tiles so place names/contours stay visible
        color_default = 0.95
        contrast_default = 1.05
        sharp_default = 1.15

    cm = float(color_mult) if color_mult is not None else color_default
    ct = float(contrast_mult) if contrast_mult is not None else contrast_default
    sh = float(sharpness_mult) if sharpness_mult is not None else sharp_default

    basemap = ImageEnhance.Color(basemap).enhance(cm)
    basemap = ImageEnhance.Contrast(basemap).enhance(ct)
    basemap = ImageEnhance.Sharpness(basemap).enhance(sh)

    return np.asarray(basemap), basemap_extent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="Output mp4 path")
    ap.add_argument("--stops", help="Path to stops.json (OSRM road-follow mode)")
    ap.add_argument("--route", help="Path to .gpx or .kml (use route geometry directly; no OSRM)")
    ap.add_argument("--size", default="1600x900")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--duration", type=int, default=12)
    ap.add_argument("--title", default="")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--zoom", type=int, default=18, help="Terrain tile zoom")
    ap.add_argument("--dwell", type=int, default=0, help="Pause at each stop, frames")
    ap.add_argument("--lookahead", type=float, default=0.020, help="Camera look-ahead as fraction of route length")
    ap.add_argument("--no-follow", action="store_true", help="Disable fly-follow camera (show full route)")
    ap.add_argument("--font", default="/System/Library/Fonts/Hiragino Sans GB.ttc")
    ap.add_argument(
        "--basemap-alpha",
        type=float,
        default=None,
        help="Basemap alpha override (0..1). If omitted, chosen based on zoom.",
    )
    ap.add_argument(
        "--overlay-alpha",
        type=float,
        default=None,
        help="Dark overlay alpha override (0..1). If omitted, chosen based on zoom.",
    )
    ap.add_argument(
        "--basemap-color",
        type=float,
        default=None,
        help="Basemap color (saturation) multiplier override. 1.0 = original tiles.",
    )
    ap.add_argument(
        "--basemap-contrast",
        type=float,
        default=None,
        help="Basemap contrast multiplier override. 1.0 = original tiles.",
    )
    ap.add_argument(
        "--basemap-sharpness",
        type=float,
        default=None,
        help="Basemap sharpness multiplier override. 1.0 = original tiles.",
    )
    args = ap.parse_args()

    ensure_ffmpeg()

    if not args.stops and not args.route:
        raise SystemExit("Must provide --stops (OSRM mode) or --route (GPX/KML mode)")
    if args.stops and args.route:
        raise SystemExit("Provide only one of --stops or --route")

    w, h = map(int, args.size.lower().split("x"))
    fps = args.fps
    duration_s = args.duration
    frames = fps * duration_s

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": "openclaw-terrain-route-video/1.1"})

    if args.route:
        coords_lonlat = load_route_from_file(args.route)
        # synthesize stops (start/end) so we can keep the UI overlays consistent
        s0 = coords_lonlat[0]
        s1 = coords_lonlat[-1]
        stops = [
            Stop(id="S", name="Start", lon=float(s0[0]), lat=float(s0[1])),
            Stop(id="E", name="End", lon=float(s1[0]), lat=float(s1[1])),
        ]
    else:
        stops_json = json.load(open(args.stops, "r", encoding="utf-8"))
        stops = [Stop(**s) for s in stops_json["stops"]]
        coords_lonlat = fetch_osrm_route(stops, session)

    route_xy = np.array([mercator(lon, lat) for lon, lat in coords_lonlat], dtype=np.float64)
    cum, total = route_cumulative(route_xy)

    # stop distances on route
    stop_s = np.array([nearest_route_s(route_xy, cum, s.lon, s.lat) for s in stops], dtype=float)
    stop_s.sort()

    # Travel window: distribute motion across the whole video (no static tail by default)
    travel_start = 0
    travel_end = frames
    hold_end = frames

    # head schedule: uniform speed with optional dwell
    travel_frames = travel_end - travel_start
    dwell_frames = int(args.dwell)
    dwell_total = dwell_frames * (len(stop_s) - 1)
    move_frames = max(1, travel_frames - dwell_total)

    leg_dist = np.diff(stop_s)
    leg_dist = np.maximum(leg_dist, 1e-6)
    leg_frames = np.round(move_frames * (leg_dist / leg_dist.sum())).astype(int)
    while leg_frames.sum() < move_frames:
        leg_frames[np.argmax(leg_dist)] += 1
    while leg_frames.sum() > move_frames:
        leg_frames[np.argmax(leg_frames)] -= 1

    head_s = np.zeros(frames, dtype=float)
    head_s[:travel_start] = stop_s[0]
    f = travel_start
    cur_s = stop_s[0]
    for i in range(len(leg_dist)):
        frames_i = int(leg_frames[i])
        next_s = stop_s[i + 1]
        for k in range(frames_i):
            t = (k + 1) / frames_i
            if f >= frames:
                break
            head_s[f] = cur_s * (1 - t) + next_s * t
            f += 1
        cur_s = next_s
        for _ in range(dwell_frames):
            if f >= travel_end:
                break
            head_s[f] = cur_s
            f += 1
    while f < travel_end:
        head_s[f] = stop_s[-1]
        f += 1
    head_s[travel_end:hold_end] = stop_s[-1]

    head_xy = np.array([point_at_s(route_xy, cum, total, s) for s in head_s])

    # camera follow
    minx_all, maxx_all = route_xy[:, 0].min(), route_xy[:, 0].max()
    miny_all, maxy_all = route_xy[:, 1].min(), route_xy[:, 1].max()

    aspect = w / h
    base_scale = max(maxy_all - miny_all, (maxx_all - minx_all) / aspect) * 0.22

    def cam_window(center: np.ndarray) -> Tuple[float, float, float, float]:
        half_h = base_scale
        half_w = half_h * aspect
        return (center[0] - half_w, center[0] + half_w, center[1] - half_h, center[1] + half_h)

    cam_xy = np.zeros_like(head_xy)
    alpha = 0.14
    for i in range(frames):
        target = point_at_s(route_xy, cum, total, head_s[i] + args.lookahead * total)
        if i == 0:
            cam_xy[i] = target
        else:
            cam_xy[i] = cam_xy[i - 1] * (1 - alpha) + target * alpha

    cam_xy[:, 0] -= base_scale * 0.35
    cam_xy[:, 1] += base_scale * 0.08

    # basemap
    tile_cache_dir = Path(".tile-cache")

    # OpenTopoMap doesn't guarantee all zoom levels globally; if a zoom fails (e.g. HTTP 400/404),
    # fall back to a lower zoom automatically.
    basemap_np = None
    basemap_extent = None
    zoom_used = int(args.zoom)
    for z in range(int(args.zoom), 6, -1):
        try:
            basemap_np, basemap_extent = build_basemap(
                minx_all,
                maxx_all,
                miny_all,
                maxy_all,
                session,
                z,
                tile_cache_dir,
                color_mult=args.basemap_color,
                contrast_mult=args.basemap_contrast,
                sharpness_mult=args.basemap_sharpness,
            )
            zoom_used = z
            break
        except requests.RequestException as e:
            if z <= 7:
                raise
            print(f"Basemap fetch failed at zoom={z} ({e}); retrying with zoom={z-1}")

    assert basemap_np is not None and basemap_extent is not None

    # font
    font = FontProperties(fname=args.font)

    # render frames
    frames_dir = Path("frames")
    frames_dir.mkdir(exist_ok=True)

    BG = "#0b1320"
    TEXT = "#e5e7eb"
    ACCENT = "#ef4444"
    ACCENT_DOT = "#2dd4bf"

    stop_route_s = np.array([nearest_route_s(route_xy, cum, st.lon, st.lat) for st in stops], dtype=float)

    def stop_for_s(sv: float) -> Stop:
        # latest stop reached (by stop_s)
        idx = 0
        for i, ss in enumerate(stop_s):
            if ss <= sv:
                idx = i
        # map back to original stop by nearest s
        target = stop_s[idx]
        j = int(np.argmin(np.abs(stop_route_s - target)))
        return stops[j]

    for i in range(frames):
        if i % 30 == 0:
            print(f"Rendering {i}/{frames}")

        fig = plt.figure(figsize=(w / 100, h / 100), dpi=100)
        ax = fig.add_axes([0, 0, 1, 1])
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)
        ax.set_xticks([])
        ax.set_yticks([])

        if args.no_follow:
            # show full route
            pad = 0.12
            minx, maxx = minx_all, maxx_all
            miny, maxy = miny_all, maxy_all
            spanx, spany = maxx - minx, maxy - miny
            minx -= spanx * pad
            maxx += spanx * pad
            miny -= spany * pad
            maxy += spany * pad
            ax.set_xlim(minx, maxx)
            ax.set_ylim(miny, maxy)
        else:
            x0, x1, y0, y1 = cam_window(cam_xy[i])
            ax.set_xlim(x0, x1)
            ax.set_ylim(y0, y1)

        bx0, bx1, by0, by1 = basemap_extent
        # At low zoom levels the terrain tiles become visually subtle; use a lighter dark-overlay
        # so the basemap remains readable.
        basemap_alpha = 0.55
        overlay_alpha = 0.55
        if zoom_used <= 12:
            basemap_alpha = 0.82
            overlay_alpha = 0.38
        elif zoom_used <= 14:
            basemap_alpha = 0.70
            overlay_alpha = 0.45

        # user overrides
        if args.basemap_alpha is not None:
            basemap_alpha = float(args.basemap_alpha)
        if args.overlay_alpha is not None:
            overlay_alpha = float(args.overlay_alpha)

        ax.imshow(
            basemap_np,
            extent=(bx0, bx1, by0, by1),
            # nearest keeps labels/crisp edges more readable than bilinear
            interpolation="nearest",
            alpha=float(basemap_alpha),
            zorder=0,
        )

        # dark overlay to reduce noise
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        ax.add_patch(
            plt.Rectangle(
                (x0, y0),
                x1 - x0,
                y1 - y0,
                color=BG,
                alpha=float(overlay_alpha),
                zorder=1,
            )
        )

        s_now = head_s[i]
        pts = polyline_up_to_s(route_xy, cum, total, s_now)
        # glow + main
        ax.plot(pts[:, 0], pts[:, 1], color=(239 / 255, 68 / 255, 68 / 255, 0.35), linewidth=7.5, solid_capstyle="round", zorder=3)
        ax.plot(pts[:, 0], pts[:, 1], color=ACCENT, linewidth=3.8, solid_capstyle="round", zorder=4)

        hx, hy = head_xy[i]
        ax.scatter([hx], [hy], s=55, c=ACCENT_DOT, edgecolors="none", zorder=6)
        ax.scatter([hx], [hy], s=260, facecolors="none", edgecolors=(0.18, 0.89, 0.82, 0.22), linewidths=1.6, zorder=5)

        # stop markers
        for st in stops:
            x, y = mercator(st.lon, st.lat)
            ax.scatter([x], [y], s=90, c=BG, edgecolors=(1, 1, 1, 0.75), linewidths=1.2, zorder=4)
            ax.scatter([x], [y], s=220, facecolors="none", edgecolors=(0.18, 0.89, 0.82, 0.12), linewidths=1.4, zorder=3)
            ax.text(x, y, st.id, ha="center", va="center", color=TEXT, fontsize=12, fontweight="bold", zorder=7, fontproperties=font)

        # title plate
        intro_op = 1.0
        if i < travel_start:
            t = i / max(1, travel_start)
            intro_op = t * t * (3 - 2 * t)

        if args.title:
            fig.text(
                0.04,
                0.93,
                args.title,
                color=TEXT,
                fontsize=36,
                fontweight="bold",
                ha="left",
                va="top",
                alpha=float(intro_op),
                fontproperties=font,
                bbox=dict(
                    boxstyle="round,pad=0.55,rounding_size=0.9",
                    facecolor=(11 / 255, 19 / 255, 32 / 255, 0.55),
                    edgecolor=(1, 1, 1, 0.10),
                    linewidth=1.0,
                ),
            )

        # current stop pill
        if i >= travel_start:
            cur = stop_for_s(s_now)
            fig.text(
                0.04,
                0.08,
                f"{cur.id}  {cur.name}",
                color=TEXT,
                fontsize=22,
                ha="left",
                va="bottom",
                fontproperties=font,
                bbox=dict(
                    boxstyle="round,pad=0.55,rounding_size=0.9",
                    facecolor=(11 / 255, 19 / 255, 32 / 255, 0.72),
                    edgecolor=(1, 1, 1, 0.18),
                    linewidth=1.0,
                ),
            )

        mode_label = (
            "交通连线（道路路径）· 极简示意"
            if not args.route
            else f"轨迹连线（GPX/KML）· 极简示意 · z{zoom_used}"
        )
        fig.text(
            0.965,
            0.065,
            mode_label,
            color=(229 / 255, 231 / 255, 235 / 255, 0.55),
            fontsize=16,
            ha="right",
            va="bottom",
            fontproperties=font,
        )

        out_frame = frames_dir / f"{i:05d}.png"
        fig.savefig(out_frame, dpi=100)
        plt.close(fig)

    # encode
    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(fps),
        "-i",
        str(frames_dir / "%05d.png"),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "18",
        "-preset",
        "medium",
        str(out_path),
    ]
    print("Encoding video...")
    subprocess.check_call(cmd)
    print("Done:", out_path)


if __name__ == "__main__":
    main()
