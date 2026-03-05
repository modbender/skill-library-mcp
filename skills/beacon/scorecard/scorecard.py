#!/usr/bin/env python3
"""Beacon Agent Scorecard — Public self-hostable dashboard.

Run:
    pip install flask requests pyyaml
    python scorecard.py

Then open http://localhost:8090
"""

import os
import time
import threading
import yaml
import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CONFIG_PATH = os.environ.get(
    "SCORECARD_CONFIG", os.path.join(os.path.dirname(__file__), "agents.yaml")
)
CACHE_TTL = 60  # seconds
PORT = int(os.environ.get("SCORECARD_PORT", 8090))

_config = {}
_cache = {}
_cache_lock = threading.Lock()


def load_config():
    global _config
    with open(CONFIG_PATH, "r") as f:
        _config = yaml.safe_load(f)
    return _config


def cfg():
    if not _config:
        load_config()
    return _config


# ---------------------------------------------------------------------------
# Cached HTTP fetcher
# ---------------------------------------------------------------------------


def _fetch(url, timeout=8):
    """GET url, return (ok, json_or_none)."""
    try:
        r = requests.get(url, timeout=timeout, verify=True)
        if r.ok:
            return True, r.json() if "json" in r.headers.get("content-type", "") else None
        return False, None
    except Exception:
        return False, None


def cached_fetch(key, url, ttl=CACHE_TTL):
    with _cache_lock:
        entry = _cache.get(key)
        if entry and time.time() - entry["ts"] < ttl:
            return entry["ok"], entry["data"]
    ok, data = _fetch(url)
    with _cache_lock:
        if ok or key not in _cache:
            _cache[key] = {"ok": ok, "data": data, "ts": time.time()}
        elif not ok and key in _cache:
            # stale-on-error: keep old data, update timestamp partially
            _cache[key]["ts"] = time.time() - ttl + 15  # retry in 15s
            return _cache[key]["ok"], _cache[key]["data"]
    return ok, data


# ---------------------------------------------------------------------------
# Platform health checks
# ---------------------------------------------------------------------------


def check_platforms():
    platforms = cfg().get("platforms", {})
    results = {}
    for pid, pdata in platforms.items():
        url = pdata.get("health_url", "")
        if not url:
            results[pid] = {"name": pdata.get("name", pid), "up": False}
            continue
        ok, _ = cached_fetch(f"health_{pid}", url)
        results[pid] = {"name": pdata.get("name", pid), "up": ok}
    return results


# ---------------------------------------------------------------------------
# RustChain network stats (public API)
# ---------------------------------------------------------------------------


def fetch_network_stats():
    rc_platform = cfg().get("platforms", {}).get("rustchain", {})
    base = rc_platform.get("health_url", "https://rustchain.org/health")
    # Strip /health to get base URL
    rc_base = base.rsplit("/health", 1)[0] if "/health" in base else base

    ok, health = cached_fetch("rc_health", f"{rc_base}/health")
    ok2, epoch = cached_fetch("rc_epoch", f"{rc_base}/epoch")

    stats = {"epoch": "?", "slot": "?", "miners": "?", "version": "?"}
    if ok and health:
        stats["version"] = health.get("version", "?")
    if ok2 and epoch:
        stats["epoch"] = epoch.get("epoch", "?")
        stats["slot"] = epoch.get("slot", "?")
        stats["miners"] = epoch.get("enrolled_miners", epoch.get("miners", "?"))
    return stats


# ---------------------------------------------------------------------------
# Beacon agent count
# ---------------------------------------------------------------------------


def fetch_beacon_count():
    beacon_platform = cfg().get("platforms", {}).get("beacon", {})
    discover_url = beacon_platform.get("discover_url", "https://rustchain.org/beacon/relay/discover?include_dead=true")
    ok, data = cached_fetch("beacon_discover", discover_url)
    if ok and isinstance(data, list):
        return len(data)
    return "?"


# ---------------------------------------------------------------------------
# Scoring engine
# ---------------------------------------------------------------------------


def _video_score(count):
    """Map video count to 0-200 score using diminishing returns curve."""
    if count <= 0:
        return 0
    if count <= 5:
        return int(count * 20)  # 0-100 linear
    if count <= 10:
        return int(100 + (count - 5) * 8)  # 100-140
    if count <= 20:
        return int(140 + (count - 10) * 3)  # 140-170
    if count <= 50:
        return int(170 + (count - 20) * 1)  # 170-200
    return 200


def _platform_score(count):
    """Map platform count to 0-200 score."""
    mapping = {0: 0, 1: 30, 2: 70, 3: 100, 4: 130, 5: 150, 6: 175}
    if count >= 7:
        return 200
    return mapping.get(count, 0)


def score_agent(agent):
    """Compute live score for a single agent from public APIs."""
    weights = cfg().get("scoring", {})
    w_beacon = weights.get("beacon", 200)
    w_videos = weights.get("videos", 200)
    w_platforms = weights.get("platforms", 200)
    w_engagement = weights.get("engagement", 200)
    w_content = weights.get("content", 200)
    w_community = weights.get("community", 200)
    w_identity = weights.get("identity", 100)
    max_score = w_beacon + w_videos + w_platforms + w_engagement + w_content + w_community + w_identity

    scores = {}

    # 1. Beacon registration
    beacon_id = agent.get("beacon_id", "")
    if beacon_id:
        scores["beacon"] = w_beacon
    else:
        scores["beacon"] = 0

    # 2. BoTTube video count
    slug = agent.get("bottube_slug", "")
    video_count = 0
    if slug:
        bt_platform = cfg().get("platforms", {}).get("bottube", {})
        video_url = bt_platform.get("video_url", "https://bottube.ai/api/videos?agent={slug}")
        url = video_url.replace("{slug}", slug)
        ok, data = cached_fetch(f"videos_{slug}", url)
        if ok and data:
            if isinstance(data, list):
                video_count = len(data)
            elif isinstance(data, dict):
                video_count = len(data.get("videos", data.get("items", [])))
    raw_video = _video_score(video_count)
    scores["videos"] = int(raw_video * w_videos / 200)

    # 3. Platform presence
    agent_platforms = agent.get("platforms", [])
    raw_plat = _platform_score(len(agent_platforms))
    scores["platforms"] = int(raw_plat * w_platforms / 200)

    # 4. Engagement (placeholder — derived from video count + platforms)
    if video_count > 0 and len(agent_platforms) >= 2:
        scores["engagement"] = int(w_engagement * min(1.0, (video_count * 2 + len(agent_platforms) * 10) / 100))
    else:
        scores["engagement"] = int(w_engagement * 0.1) if video_count > 0 or len(agent_platforms) > 0 else 0

    # 5. Content (video + platform spread)
    content_ratio = min(1.0, (raw_video / 200 * 0.7 + raw_plat / 200 * 0.3))
    scores["content"] = int(w_content * content_ratio)

    # 6. Community (placeholder)
    scores["community"] = int(w_community * 0.2) if len(agent_platforms) >= 2 else 0

    # 7. Identity completeness
    id_checks = [bool(beacon_id), bool(agent.get("role")), bool(agent.get("color"))]
    scores["identity"] = int(w_identity * sum(id_checks) / len(id_checks))

    total = sum(scores.values())
    pct = (total / max_score * 100) if max_score > 0 else 0

    # Grade
    grade_thresholds = cfg().get("grades", {"S": 80, "A": 60, "B": 45, "C": 30, "D": 15})
    grade = "F"
    for g in ["S", "A", "B", "C", "D"]:
        if pct >= grade_thresholds.get(g, 0):
            grade = g
            break

    return {
        "scores": scores,
        "total": total,
        "max": max_score,
        "pct": round(pct, 1),
        "grade": grade,
        "video_count": video_count,
    }


# ---------------------------------------------------------------------------
# Build full dashboard data
# ---------------------------------------------------------------------------


def build_dashboard_data():
    config = cfg()
    platform_health = check_platforms()
    network = fetch_network_stats()
    beacon_count = fetch_beacon_count()

    agents_data = []
    for agent in config.get("agents", []):
        result = score_agent(agent)
        agents_data.append({**agent, **result})

    # Sort by total score descending
    agents_data.sort(key=lambda a: a["total"], reverse=True)

    return {
        "fleet_name": config.get("fleet_name", "Agent Fleet"),
        "fleet_owner": config.get("fleet_owner", ""),
        "agents": agents_data,
        "platforms": platform_health,
        "network": network,
        "beacon_count": beacon_count,
        "scoring_weights": config.get("scoring", {}),
        "ts": int(time.time()),
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    data = build_dashboard_data()
    return render_template("scorecard.html", **data)


@app.route("/api/status")
def api_status():
    return jsonify(build_dashboard_data())


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    global _cache
    with _cache_lock:
        _cache = {}
    return jsonify({"ok": True, "msg": "Cache cleared"})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    load_config()
    agent_count = len(cfg().get("agents", []))
    print(f"\n  Beacon Agent Scorecard")
    print(f"  Fleet: {cfg().get('fleet_name', 'Agent Fleet')}")
    print(f"  Agents: {agent_count}")
    print(f"  http://localhost:{PORT}\n")
    app.run(host="0.0.0.0", port=PORT, debug=False)
