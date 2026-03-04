#!/usr/bin/env python3
"""
Analyze the last CS2 demo for a player via Leetify API + demoparser2.

Usage:
  python3 analyze_last_demo.py --username <tg_username> [--match-index 0] [--round N]

Outputs compact text log suitable for LLM analysis.
Caches parsed logs in leetify/matches/ to avoid re-downloading.
"""

import argparse
import gc
import json
import os
import subprocess
import sys
import math
import tempfile
import urllib.request
import urllib.parse
from collections import defaultdict

try:
    from demoparser2 import DemoParser
except ImportError:
    print("ERROR: demoparser2 not installed. Run: pip install demoparser2", file=sys.stderr)
    sys.exit(1)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STEAM_IDS_SCRIPT = os.path.join(SCRIPT_DIR, "steam_ids.py")
MATCHES_DIR = os.path.join(SCRIPT_DIR, "..", "matches")
API_BASE = "https://api-public.cs-prod.leetify.com"

TRADE_WINDOW_TICKS = 5 * 64  # ~5 seconds at 64 tick
STEAM_IDS_JSON = os.path.join(SCRIPT_DIR, "..", "data", "steam_ids.json")


def load_known_players() -> dict:
    """Load steam_id -> @username mapping from steam_ids.json"""
    sid_to_username = {}
    try:
        with open(STEAM_IDS_JSON, "r") as f:
            data = json.load(f)
        for uname, info in data.items():
            sid = info.get("steam_id", "")
            if sid:
                sid_to_username[sid] = f"@{uname}"
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return sid_to_username

# Short item names for compact output
ITEM_SHORT = {
    "High Explosive Grenade": "HE",
    "Smoke Grenade": "Smoke",
    "Incendiary Grenade": "Molly",
    "Molotov": "Molly",
    "Flashbang": "Flash",
    "Decoy Grenade": "Decoy",
    "Kevlar Vest": "Kevlar",
    "Kevlar & Helmet": "Kevlar+H",
    "Zeus x27": "Zeus",
    "Defuse Kit": "Kit",
    "Desert Eagle": "Deagle",
    "Dual Berettas": "Dualies",
    "CZ75-Auto": "CZ75",
    "R8 Revolver": "R8",
    "Five-SeveN": "5-7",
    "Sawed-Off": "Sawed",
    "PP-Bizon": "Bizon",
}


def short_item(name: str) -> str:
    return ITEM_SHORT.get(name, name)


def safe_int(v, default=0):
    """Convert to int, handling NaN/None gracefully."""
    try:
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return default
        return int(v)
    except (ValueError, TypeError):
        return default


# ==========================================
#  Leetify API helpers
# ==========================================

def get_steam_id(username: str) -> str:
    result = subprocess.run(
        [sys.executable, STEAM_IDS_SCRIPT, "get", "--username", username],
        capture_output=True, text=True
    )
    steam_id = result.stdout.strip()
    if not steam_id or result.returncode != 0:
        print(f"❌ Steam ID не найден для @{username}", file=sys.stderr)
        sys.exit(1)
    return steam_id


def fetch_matches(steam_id: str, limit: int = 5) -> list:
    url = f"{API_BASE}/v3/profile/matches?{urllib.parse.urlencode({'steam64_id': steam_id, 'limit': limit})}"
    req = urllib.request.Request(url, headers={'accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"❌ Ошибка API Leetify: {e}", file=sys.stderr)
        sys.exit(1)


def download_demo(replay_url: str, tmp_dir: str) -> str:
    filename = os.path.basename(replay_url).split('?')[0]
    local_path = os.path.join(tmp_dir, filename)

    print(f"⬇️  Скачиваю демку: {replay_url}", file=sys.stderr)
    urllib.request.urlretrieve(replay_url, local_path)

    if local_path.endswith('.bz2'):
        print("📦 Распаковка .bz2...", file=sys.stderr)
        subprocess.run(['bunzip2', '-f', local_path], check=True)
        local_path = local_path[:-4]
    elif local_path.endswith('.gz'):
        print("📦 Распаковка .gz...", file=sys.stderr)
        subprocess.run(['gunzip', '-f', local_path], check=True)
        local_path = local_path[:-3]

    if not os.path.isfile(local_path):
        print(f"❌ Файл не найден после распаковки: {local_path}", file=sys.stderr)
        sys.exit(1)

    size_mb = os.path.getsize(local_path) / (1024 * 1024)
    print(f"✅ Демка готова: {size_mb:.1f} MB", file=sys.stderr)
    return local_path


# ==========================================
#  Demo parsing
# ==========================================

def parse_demo_to_log(demo_path: str, leetify_match: dict) -> str:
    """Parse demo and return compact text log."""
    parser = DemoParser(demo_path)
    header = parser.parse_header()
    map_name = header.get("map_name", "unknown")

    # ── Kill feed ──
    # Optimization: removed X, Y, Z, added pitch/yaw
    player_fields = ["last_place_name", "team_num", "pitch", "yaw"]
    try:
        deaths_df = parser.parse_event("player_death", player=player_fields, other=["total_rounds_played"])
    except Exception:
        deaths_df = parser.parse_event("player_death", other=["total_rounds_played"])

    kills = []
    for _, row in deaths_df.iterrows():
        kills.append({
            "round": int(row.get("total_rounds_played", 0)),
            "tick": int(row.get("tick", 0)),
            "attacker": row.get("attacker_name", "") or "",
            "attacker_sid": str(row.get("attacker_steamid", "")),
            "attacker_loc": row.get("attacker_last_place_name", "") or "",
            "attacker_team": safe_int(row.get("attacker_team_num", 0)) if "attacker_team_num" in row.index else 0,
            "attacker_view": (round(row.get("attacker_pitch", 0), 1), round(row.get("attacker_yaw", 0), 1)),
            "victim": row.get("user_name", "") or "",
            "victim_sid": str(row.get("user_steamid", "")),
            "victim_loc": row.get("user_last_place_name", "") or "",
            "victim_team": safe_int(row.get("user_team_num", 0)) if "user_team_num" in row.index else 0,
            "victim_view": (round(row.get("user_pitch", 0), 1), round(row.get("user_yaw", 0), 1)),
            "weapon": row.get("weapon", ""),
            "headshot": bool(row.get("headshot", False)),
            "penetrated": int(row.get("penetrated", 0)),
            "noscope": bool(row.get("noscope", False)),
            "thrusmoke": bool(row.get("thrusmoke", False)),
            "attackerblind": bool(row.get("attackerblind", False)),
            "assister": row.get("assister_name", None),
            "distance": float(row.get("distance", 0)),
            "dmg_health": int(row.get("dmg_health", 0)),
        })

    del deaths_df; gc.collect()

    # ── Round ends ──
    # NOTE: total_rounds_played in round_end is already incremented (round N ends → total=N+1)
    try:
        rounds_df = parser.parse_event("round_end", other=["total_rounds_played"])
        rounds = []
        for _, row in rounds_df.iterrows():
            rnd = int(row.get("total_rounds_played", 1)) - 1  # fix off-by-one
            winner = str(row.get("winner", ""))  # can be "T", "CT", or int
            reason = str(row.get("reason", ""))
            rounds.append({
                "round": rnd,
                "winner": winner,
                "reason": reason,
            })
        del rounds_df
    except Exception:
        rounds = []

    total_rounds = len(rounds) if rounds else (max((k["round"] for k in kills), default=0) + 1)

    # ── Round start ticks (for timing) ──
    round_start_tick = {}
    try:
        rfe_df = parser.parse_event("round_freeze_end", other=["total_rounds_played"])
        for _, row in rfe_df.iterrows():
            rnd = int(row.get("total_rounds_played", 0))
            round_start_tick[rnd] = int(row.get("tick", 0))
    except Exception:
        pass

    def tick_to_sec(tick: int, rnd: int) -> str:
        """Convert tick to seconds relative to round start."""
        start = round_start_tick.get(rnd, 0)
        if start and tick >= start:
            sec = (tick - start) / 64.0
            return f"{sec:.0f}s"
        return ""

    # ── Grenade events ──
    grenades = []
    nade_events = {
        "smokegrenade_detonate": "smoke",
        "flashbang_detonate": "flash",
        "hegrenade_detonate": "HE",
        "inferno_startburn": "molly",
    }
    # Parsing chunks to save memory
    try:
        # We need coordinates (x, y, z) and player info
        for event_name, nade_type in nade_events.items():
            df = parser.parse_event(event_name, other=["total_rounds_played", "x", "y", "z"])
            for _, row in df.iterrows():
                grenades.append({
                    "round": int(row.get("total_rounds_played", 0)),
                    "tick": int(row.get("tick", 0)),
                    "player": row.get("user_name", "") or "",
                    "type": nade_type,
                    "x": round(row.get("x", 0), 1),
                    "y": round(row.get("y", 0), 1),
                    "z": round(row.get("z", 0), 1),
                })
            del df
            gc.collect()
    except Exception:
        pass

    # ── Flash blindness events ──
    blinds = []
    try:
        blind_df = parser.parse_event("player_blind", other=["total_rounds_played"])
        for _, row in blind_df.iterrows():
            dur = float(row.get("blind_duration", 0))
            if dur < 0.5:
                continue
            blinds.append({
                "round": int(row.get("total_rounds_played", 0)),
                "tick": int(row.get("tick", 0)),
                "attacker": row.get("attacker_name", "") or "",
                "victim": row.get("user_name", "") or "",
                "victim_sid": str(row.get("user_steamid", "")),
                "attacker_sid": str(row.get("attacker_steamid", "")),
                "duration": dur,
            })
        del blind_df
    except Exception:
        pass

    # ── Damage events (player_hurt) ──
    hurts = []
    try:
        hurt_df = parser.parse_event("player_hurt", other=["total_rounds_played"])
        for _, row in hurt_df.iterrows():
            health_after = int(row.get("health", 0))
            hurts.append({
                "round": int(row.get("total_rounds_played", 0)),
                "tick": int(row.get("tick", 0)),
                "attacker": row.get("attacker_name", "") or "",
                "attacker_sid": str(row.get("attacker_steamid", "")),
                "victim": row.get("user_name", "") or "",
                "victim_sid": str(row.get("user_steamid", "")),
                "dmg": int(row.get("dmg_health", 0)),
                "health_after": health_after,
                "hitgroup": row.get("hitgroup", "") or "",
                "weapon": row.get("weapon", "") or "",
                "lethal": health_after == 0,
            })
        del hurt_df
    except Exception:
        pass
    gc.collect()

    # ── Bomb events ──
    bomb_events = []
    SITE_MAP = {168: "A", 169: "B", 181: "A", 182: "B", "A": "A", "B": "B"}
    for evt, evt_type in [("bomb_planted", "plant"), ("bomb_exploded", "explode"), ("bomb_defused", "defuse")]:
        try:
            df = parser.parse_event(evt, other=["total_rounds_played"])
            if isinstance(df, list):
                continue  # empty
            for _, row in df.iterrows():
                site_raw = row.get("site", "")
                site = SITE_MAP.get(site_raw, str(site_raw))
                bomb_events.append({
                    "round": int(row.get("total_rounds_played", 0)),
                    "tick": int(row.get("tick", 0)),
                    "type": evt_type,
                    "player": row.get("user_name", "") or "",
                    "player_sid": str(row.get("user_steamid", "")),
                    "site": site,
                })
        except Exception:
            pass

    # ── Economy per round ──
    round_economy = {}
    round_player_econ = defaultdict(dict)
    freeze_ticks = list(round_start_tick.items())
    if freeze_ticks:
        econ_fields = ["current_equip_value", "cash_spent_this_round", "balance",
                        "has_helmet", "has_defuser", "armor_value",
                        "player_name", "team_num", "player_steamid"]
        # Parse in chunks of 2 rounds to limit memory (optimization)
        ECON_CHUNK = 2
        for ci in range(0, len(freeze_ticks), ECON_CHUNK):
            chunk = freeze_ticks[ci:ci + ECON_CHUNK]
            try:
                econ_df = parser.parse_ticks(econ_fields, ticks=[t for _, t in chunk])
                for rnd, tick in chunk:
                    rnd_data = econ_df[econ_df["tick"] == tick]
                    for _, row in rnd_data.iterrows():
                        sid = str(row.get("player_steamid", ""))
                        if not sid or sid == "0":
                            continue
                        team_num_val = safe_int(row.get("team_num", 0))
                        if team_num_val not in (2, 3):
                            continue
                        round_player_econ[rnd][sid] = {
                            "name": row.get("player_name", ""),
                            "team": team_num_val,
                            "equip": safe_int(row.get("current_equip_value", 0)),
                            "spent": safe_int(row.get("cash_spent_this_round", 0)),
                            "balance": safe_int(row.get("balance", 0)),
                            "armor": safe_int(row.get("armor_value", 0)),
                            "helmet": bool(row.get("has_helmet", False)),
                            "defuser": bool(row.get("has_defuser", False)),
                        }

                    for team_num in [2, 3]:
                        team_data = rnd_data[rnd_data["team_num"].fillna(0) == team_num]
                        if len(team_data) > 0:
                            avg_equip = team_data["current_equip_value"].mean()
                            if rnd not in round_economy:
                                round_economy[rnd] = {}
                            round_economy[rnd][f"team{team_num}_equip"] = int(avg_equip)
                            if rnd == 0 or rnd == 12:
                                buy_type = "pistol"
                            elif avg_equip <= 1500:
                                buy_type = "eco"
                            elif avg_equip <= 3500:
                                buy_type = "half"
                            elif avg_equip <= 4500:
                                buy_type = "force"
                            else:
                                buy_type = "full"
                            round_economy[rnd][f"team{team_num}_type"] = buy_type
                del econ_df
            except Exception:
                pass
            gc.collect()
        gc.collect()

    # ── Item purchases per round (buy phase only) ──
    round_purchases = defaultdict(lambda: defaultdict(list))
    try:
        # 1. Collect all purchases
        purchases_df = parser.parse_event("item_purchase", other=["total_rounds_played"])
        for _, row in purchases_df.iterrows():
            rnd = int(row.get("total_rounds_played", 0))
            tick = int(row.get("tick", 0))
            freeze_tick = round_start_tick.get(rnd, 0)
            if freeze_tick and tick > freeze_tick:
                continue
            sid = str(row.get("steamid", ""))
            item = row.get("item_name", "") or row.get("name", "") or ""
            if sid and item:
                round_purchases[rnd][sid].append(item)
        del purchases_df

        # 2. Process refunds (remove refunded items)
        # Note: CS2 doesn't always have 'item_refund', sometimes it's implied.
        # But if it exists, we use it. We'll try 'item_pickup' with verify? No.
        # Let's try parsing item_refund event (it exists in Source 2)
        try:
            refunds_df = parser.parse_event("item_refund", other=["total_rounds_played"])
            for _, row in refunds_df.iterrows():
                rnd = int(row.get("total_rounds_played", 0))
                sid = str(row.get("steamid", ""))
                item = row.get("item_name", "") or row.get("name", "") or ""
                if sid and item and sid in round_purchases[rnd]:
                    # Remove ONE instance of this item from the list (from the end)
                    items_list = round_purchases[rnd][sid]
                    if item in items_list:
                        # Find last index to remove (most recent buy)
                        for i in range(len(items_list) - 1, -1, -1):
                            if items_list[i] == item:
                                del items_list[i]
                                break
            del refunds_df
        except Exception:
            pass  # Event might not exist or parser error

    except Exception:
        pass
    gc.collect()

    # ── Player movement (per-player location changes) ──
    # {round -> [(tick, name, team, new_loc), ...]}
    round_movements = defaultdict(list)
    # Collect round end ticks
    round_end_tick = {}
    for r in rounds:
        round_end_tick[r["round"]] = 0
    try:
        re_df = parser.parse_event("round_end", other=["total_rounds_played"])
        for _, row in re_df.iterrows():
            rnd = int(row.get("total_rounds_played", 1)) - 1
            round_end_tick[rnd] = int(row.get("tick", 0))
    except Exception:
        pass

    POSITION_SAMPLE_INTERVAL = 192  # ~3 seconds at 64 tick (High detail)
    sample_ticks_all = []
    sample_tick_to_round = {}
    for rnd in range(total_rounds):
        start = round_start_tick.get(rnd, 0)
        end = round_end_tick.get(rnd, 0)
        if not start or not end or end <= start:
            continue
        t = start
        while t <= end:
            sample_ticks_all.append(t)
            sample_tick_to_round[t] = rnd
            t += POSITION_SAMPLE_INTERVAL

    if sample_ticks_all:
        # Parse one round at a time with minimal fields to avoid OOM
        round_ticks = defaultdict(list)
        for t in sample_ticks_all:
            round_ticks[sample_tick_to_round[t]].append(t)

        player_last_loc = {}  # (rnd, name) -> loc
        for rnd in sorted(round_ticks.keys()):
            ticks_chunk = round_ticks[rnd]
            try:
                pos_df = parser.parse_ticks(
                    ["last_place_name", "player_name", "team_num", "is_alive"],
                    ticks=ticks_chunk
                )
                for tick_val in ticks_chunk:
                    tick_data = pos_df[pos_df["tick"] == tick_val]
                    for _, row in tick_data.iterrows():
                        name = row.get("player_name", "")
                        alive = row.get("is_alive", True)
                        if not name or name == "GOTV" or not alive:
                            continue
                        loc = row.get("last_place_name", "") or ""
                        team = safe_int(row.get("team_num", 0))
                        key = (rnd, name)
                        prev = player_last_loc.get(key)
                        if prev != loc:
                            player_last_loc[key] = loc
                            round_movements[rnd].append((tick_val, name, team, loc))
                del pos_df
            except Exception:
                pass

    # ── Team mapping from ticks ──
    team_map = {}  # steamid -> team_num
    try:
        last_tick = max(1, header.get("playback_ticks", 1) - 64)
        team_df = parser.parse_ticks(["player_name", "player_steamid", "team_num"], ticks=[last_tick])
        for _, row in team_df.iterrows():
            name = row.get("player_name", "")
            sid = str(row.get("player_steamid", ""))
            if name and name != "GOTV" and sid:
                team_map[sid] = int(row.get("team_num", 0))
        del team_df
    except Exception:
        pass
    gc.collect()

    # ── Build scoreboard from kill feed ──
    players = {}
    for k in kills:
        atk = k["attacker"]
        atk_sid = k["attacker_sid"]
        vic = k["victim"]
        vic_sid = k["victim_sid"]

        if atk and atk_sid and atk_sid != "0":
            if atk_sid not in players:
                players[atk_sid] = {"name": atk, "sid": atk_sid, "kills": 0, "deaths": 0,
                                     "assists": 0, "hs_kills": 0, "damage": 0}
            players[atk_sid]["kills"] += 1
            if k["headshot"]:
                players[atk_sid]["hs_kills"] += 1
            players[atk_sid]["damage"] += k["dmg_health"]

        if vic and vic_sid:
            if vic_sid not in players:
                players[vic_sid] = {"name": vic, "sid": vic_sid, "kills": 0, "deaths": 0,
                                     "assists": 0, "hs_kills": 0, "damage": 0}
            players[vic_sid]["deaths"] += 1

        ass = k.get("assister")
        if ass:
            # Find assister steamid from other kills
            for k2 in kills:
                if k2["attacker"] == ass and k2["attacker_sid"]:
                    if k2["attacker_sid"] not in players:
                        players[k2["attacker_sid"]] = {"name": ass, "sid": k2["attacker_sid"],
                                                        "kills": 0, "deaths": 0, "assists": 0,
                                                        "hs_kills": 0, "damage": 0}
                    players[k2["attacker_sid"]]["assists"] += 1
                    break

    scoreboard = list(players.values())

    # Add team from team_map
    for p in scoreboard:
        p["team"] = team_map.get(p["sid"], 0)

    # ── Real damage from hurt events (capped at victim HP) ──
    real_damage = defaultdict(int)  # sid -> total damage
    round_damage = defaultdict(lambda: defaultdict(int))  # round -> sid -> damage
    # Track victim HP to cap overkill damage
    victim_hp = {}  # (round, victim_sid) -> current_hp
    for h in sorted(hurts, key=lambda x: (x["round"], x["tick"])):
        rnd = h["round"]
        vic_key = (rnd, h["victim_sid"])
        hp_before = victim_hp.get(vic_key, 100)
        actual_dmg = min(h["dmg"], hp_before)
        h["actual_dmg"] = actual_dmg  # store for display
        hp_after = hp_before - actual_dmg
        victim_hp[vic_key] = max(hp_after, 0)
        if h["attacker_sid"] and h["attacker_sid"] != "0" and h["attacker_sid"] != h["victim_sid"]:
            # Exclude team damage from ADR
            atk_team = team_map.get(h["attacker_sid"], 0)
            vic_team = team_map.get(h["victim_sid"], 0)
            if atk_team != vic_team or atk_team == 0:
                real_damage[h["attacker_sid"]] += actual_dmg
                round_damage[rnd][h["attacker_sid"]] += actual_dmg

    # Derive ADR (real damage), HS%, KD
    for p in scoreboard:
        p["damage"] = real_damage.get(p["sid"], p["damage"])  # prefer real damage
        p["adr"] = round(p["damage"] / max(total_rounds, 1))
        p["hs_pct"] = round(p["hs_kills"] / max(p["kills"], 1) * 100)
        p["kd_diff"] = p["kills"] - p["deaths"]

    # ── Round kill map ──
    round_kills_map = defaultdict(list)
    for k in kills:
        round_kills_map[k["round"]].append(k)

    # ── Hurt map (non-lethal only, for timeline) ──
    round_hurts_map = defaultdict(list)
    for h in hurts:
        if not h["lethal"]:  # lethal damage already shown as KILL
            round_hurts_map[h["round"]].append(h)

    # ── Bomb events map ──
    round_bomb_map = defaultdict(list)
    for b in bomb_events:
        round_bomb_map[b["round"]].append(b)

    # ── Per-round annotations (opening, trade) ──
    round_annotations = {}
    for rnd in range(total_rounds):
        rk = round_kills_map.get(rnd, [])
        annotations = defaultdict(list)

        # Opening kill
        if rk:
            annotations[0].append("opening")

        # Trade detection: for every death, check if killer dies within 5 sec
        for i, k in enumerate(rk):
            for m in range(i + 1, len(rk)):
                nxt = rk[m]
                if nxt["tick"] - k["tick"] > TRADE_WINDOW_TICKS:
                    break
                if nxt["victim_sid"] == k["attacker_sid"]:
                    annotations[m].append("trade")
                    break

        round_annotations[rnd] = annotations

    # ── Multikills per round per player ──
    # {sid -> {2: count, 3: count, 4: count, 5: count}}
    multikill_stats = defaultdict(lambda: defaultdict(int))
    for rnd in range(total_rounds):
        rk = round_kills_map.get(rnd, [])
        kills_by_player = defaultdict(int)
        for k in rk:
            if k["attacker_sid"] and k["attacker_sid"] != "0":
                kills_by_player[k["attacker_sid"]] += 1
        for sid, cnt in kills_by_player.items():
            if cnt >= 2:
                multikill_stats[sid][cnt] += 1

    # ── Clutch detection ──
    # A clutch = player is the last alive on their team, faces 1+ enemies, round result known
    clutch_events = {}  # rnd -> {player, sid, team, vs, won}
    for rnd in range(total_rounds):
        rk = round_kills_map.get(rnd, [])
        if not rk:
            continue
        round_info = next((r for r in rounds if r["round"] == rnd), None)
        if not round_info:
            continue
        winner = str(round_info.get("winner", ""))

        # Track alive players by simulating kills in order
        alive = {}  # sid -> team
        # Use actual teams from round_player_econ for this round
        rpe = round_player_econ.get(rnd, {})
        if rpe:
            for sid, info in rpe.items():
                t = info.get("team", 0)
                if t in (2, 3):
                    alive[sid] = t
        else:
            for sid, t in team_map.items():
                if t in (2, 3):
                    alive[sid] = t

        for k in rk:
            vic_sid = k["victim_sid"]
            if vic_sid in alive:
                del alive[vic_sid]
            # After this kill, check if one team has exactly 1 player
            for team_num in [2, 3]:
                team_alive = [s for s, t in alive.items() if t == team_num]
                other_alive = [s for s, t in alive.items() if t != team_num and t in (2, 3)]
                if len(team_alive) == 1 and len(other_alive) >= 1:
                    cand_sid = team_alive[0]
                    cand_name = players.get(cand_sid, {}).get("name", "Unknown")
                    vs = len(other_alive)
                    if rnd not in clutch_events or clutch_events[rnd].get("vs", 0) < vs:
                        # winner can be "T", "CT" or team_num
                        w_str = str(winner)
                        won_team_num = 2 if w_str in ("2", "T") else 3 if w_str in ("3", "CT") else 0
                        clutch_events[rnd] = {
                            "player": cand_name,
                            "sid": cand_sid,
                            "team": team_num,
                            "vs": vs,
                            "won": won_team_num == team_num,
                        }

    # ── KAST computation ──
    # K=kill, A=assist, S=survived, T=traded (died but teammate traded within 5s)
    player_kast = defaultdict(int)  # sid -> rounds with KAST
    for rnd in range(total_rounds):
        rk = round_kills_map.get(rnd, [])
        round_dead = set()
        round_killers = set()
        round_assisters = set()
        traded_sids = set()

        for i, k in enumerate(rk):
            if k["attacker_sid"] and k["attacker_sid"] != "0":
                round_killers.add(k["attacker_sid"])
            if k["victim_sid"]:
                round_dead.add(k["victim_sid"])
            # Check if this victim's death was traded
            if k["victim_sid"]:
                for m in range(i + 1, len(rk)):
                    nxt = rk[m]
                    if nxt["tick"] - k["tick"] > TRADE_WINDOW_TICKS:
                        break
                    if nxt["victim_sid"] == k["attacker_sid"]:
                        traded_sids.add(k["victim_sid"])
                        break

        # Find assisters
        for k in rk:
            ass = k.get("assister")
            if ass:
                for sid, info in players.items():
                    if info["name"] == ass:
                        round_assisters.add(sid)
                        break

        for sid in players:
            has_k = sid in round_killers
            has_a = sid in round_assisters
            has_s = sid not in round_dead
            has_t = sid in traded_sids
            if has_k or has_a or has_s or has_t:
                player_kast[sid] += 1

    # Add KAST%, multikills, clutches to scoreboard
    for p in scoreboard:
        sid = p["sid"]
        p["kast"] = round(player_kast.get(sid, 0) / max(total_rounds, 1) * 100)
        mk = multikill_stats.get(sid, {})
        p["2k"] = mk.get(2, 0)
        p["3k"] = mk.get(3, 0)
        p["4k"] = mk.get(4, 0)
        p["5k"] = mk.get(5, 0)
        # Clutch stats
        clutch_attempts = sum(1 for c in clutch_events.values() if c["sid"] == sid)
        clutch_wins = sum(1 for c in clutch_events.values() if c["sid"] == sid and c["won"])
        p["clutch_w"] = clutch_wins
        p["clutch_a"] = clutch_attempts

    scoreboard.sort(key=lambda x: x["kills"], reverse=True)

    # ── Score ──
    # Calculate team-based score (accounting for side swaps at half/OT)
    # Team A starts T-side (R0-11), switches to CT (R12-23), then OT alternates every 3
    team_a_score = 0  # Team that started T-side
    team_b_score = 0  # Team that started CT-side
    for r in rounds:
        rnd = r["round"]
        w = str(r.get("winner", ""))
        if not w:
            continue
        # Determine which side Team A is on this round
        if rnd < 12:
            # First half: Team A = T
            team_a_side = "T"
        elif rnd < 24:
            # Second half: Team A = CT
            team_a_side = "CT"
        else:
            # Overtime: MR3 format, alternates every 3 rounds
            ot_round = rnd - 24
            ot_half = ot_round // 3  # 0,1,2,3,...
            # Even OT halves: Team A = CT, Odd: Team A = T
            team_a_side = "CT" if ot_half % 2 == 0 else "T"
        if w == team_a_side:
            team_a_score += 1
        else:
            team_b_score += 1

    score_str = f"{team_a_score}-{team_b_score}"
    # Fallback to Leetify data if no round winners parsed
    if team_a_score == 0 and team_b_score == 0:
        team_scores = leetify_match.get('team_scores', [])
        if team_scores:
            score_str = "-".join(str(ts['score']) for ts in team_scores)
        else:
            score_str = "?"

    # ======================================
    #  FORMAT COMPACT TEXT LOG
    # ======================================
    lines = []

    # Half scores
    first_half = [r for r in rounds if r["round"] < 12]
    second_half = [r for r in rounds if 12 <= r["round"] < 24]
    ot_rounds = [r for r in rounds if r["round"] >= 24]
    t_first = sum(1 for r in first_half if str(r.get("winner")) == "T")
    ct_first = sum(1 for r in first_half if str(r.get("winner")) == "CT")
    t_second = sum(1 for r in second_half if str(r.get("winner")) == "T")
    ct_second = sum(1 for r in second_half if str(r.get("winner")) == "CT")

    # Header
    lines.append(f"=== MATCH: {map_name} | {score_str} | {total_rounds} rounds ===")
    halves_str = f"HALVES: 1st T {t_first}-{ct_first} CT | 2nd T {t_second}-{ct_second} CT"
    if ot_rounds:
        halves_str += f" | OT {len(ot_rounds)} rounds"
    lines.append(halves_str)
    lines.append("")

    # ── Determine team rosters from first round economy/kills ──
    # In R0: team_num 2 = T, team_num 3 = CT. These are "Team A" and "Team B".
    # After halftime team_num stays the same but side flips.
    # Use first-round player economy to map steamid -> team roster.
    r0_economy = round_player_econ.get(0, {})
    team_a_sids = set()  # team_num=2 in R0 (T-start)
    team_b_sids = set()  # team_num=3 in R0 (CT-start)
    for sid, econ in r0_economy.items():
        tn = econ.get("team", 0)
        if tn == 2:
            team_a_sids.add(sid)
        elif tn == 3:
            team_b_sids.add(sid)
    # Fallback: use kills from R0 if economy is empty
    if not team_a_sids and not team_b_sids:
        for k in kills:
            if k["round"] == 0:
                if k.get("attacker_team") == 2:
                    team_a_sids.add(k["attacker_sid"])
                elif k.get("attacker_team") == 3:
                    team_a_sids.discard(k["attacker_sid"])
                    team_b_sids.add(k["attacker_sid"])
    # Assign roster tag to scoreboard
    for p in scoreboard:
        if p["sid"] in team_a_sids:
            p["roster"] = "A"
        elif p["sid"] in team_b_sids:
            p["roster"] = "B"
        else:
            p["roster"] = "?"

    # Scoreboard - grouped by team
    team_a_players = [p for p in scoreboard if p["roster"] == "A"]
    team_b_players = [p for p in scoreboard if p["roster"] == "B"]
    team_a_players.sort(key=lambda x: x["kills"], reverse=True)
    team_b_players.sort(key=lambda x: x["kills"], reverse=True)

    known_players = load_known_players()

    def format_scoreboard_line(p):
        t = {2: "T", 3: "CT"}.get(p["team"], "?")
        name = p["name"][:18]
        sid = p.get("sid", "")
        tg = known_players.get(sid)
        name_display = f"{name} ({tg})" if tg else name
        mk_parts = []
        for mk_key in ["2k", "3k", "4k", "5k"]:
            if p.get(mk_key, 0) > 0:
                mk_parts.append(f"{mk_key}:{p[mk_key]}")
        mk_str = f" {' '.join(mk_parts)}" if mk_parts else ""
        clutch_str = f" CL:{p['clutch_w']}/{p['clutch_a']}" if p.get("clutch_a", 0) > 0 else ""
        return (
            f"  {t:>2} {name_display:<30} {p['kills']:>2}/{p['deaths']:>2}/{p['assists']:>2} "
            f"ADR:{p['adr']:>3} HS:{p['hs_pct']:>2}% KAST:{p['kast']:>2}%{mk_str}{clutch_str}"
        )

    lines.append(f"SCOREBOARD: Team A {team_a_score} (T→CT) vs Team B {team_b_score} (CT→T)")
    lines.append(f"── Team A ({team_a_score}) ──")
    for p in team_a_players:
        lines.append(format_scoreboard_line(p))
    lines.append(f"── Team B ({team_b_score}) ──")
    for p in team_b_players:
        lines.append(format_scoreboard_line(p))
    lines.append("")

    # Build per-round grenade and blind maps
    round_grenades = defaultdict(list)
    for g in grenades:
        round_grenades[g["round"]].append(g)

    round_blinds = defaultdict(list)
    for b in blinds:
        round_blinds[b["round"]].append(b)

    # Round-by-round event log
    for rnd in range(total_rounds):
        rk = round_kills_map.get(rnd, [])
        rg = round_grenades.get(rnd, [])
        rb = round_blinds.get(rnd, [])
        round_info = next((r for r in rounds if r["round"] == rnd), None)

        # Round result
        result_str = ""
        if round_info:
            winner_str = str(round_info.get("winner", ""))
            reason = str(round_info.get("reason", ""))
            result_str = f"{winner_str}_win({reason})"

        # Economy tags
        econ = round_economy.get(rnd, {})
        t2_type = econ.get("team2_type", "")
        t3_type = econ.get("team3_type", "")
        t2_equip = econ.get("team2_equip", 0)
        t3_equip = econ.get("team3_equip", 0)
        econ_tag = f" | T:{t2_type}(${t2_equip}) CT:{t3_type}(${t3_equip})" if t2_type else ""

        lines.append(f"--- R{rnd}{econ_tag} ---")

        # Per-player economy
        rpe = round_player_econ.get(rnd, {})
        rp = round_purchases.get(rnd, {})
        if rpe:
            for team_num in [2, 3]:
                team_label = {2: "T", 3: "CT"}.get(team_num, "?")
                team_players = [(sid, info) for sid, info in rpe.items() if info["team"] == team_num]
                team_players.sort(key=lambda x: x[1]["equip"], reverse=True)
                for sid, info in team_players:
                    items = [short_item(i) for i in rp.get(sid, [])]
                    # Remove armor/kit from items list (shown as flags)
                    items = [i for i in items if i not in ("Kevlar", "Kevlar+H", "Kit")]
                    items_str = ",".join(items) if items else "-"
                    armor_str = ""
                    if info["armor"] > 0:
                        armor_str = "+H" if info["helmet"] else "+K"
                    defuser_str = "+D" if info["defuser"] else ""
                    lines.append(
                        f"  ${info['balance']:>5}|{team_label} {info['name']:<16} "
                        f"eq:{info['equip']:<5} sp:{info['spent']:<5}"
                        f"{armor_str}{defuser_str} | {items_str}"
                    )

        annotations = round_annotations.get(rnd, {})

        # Merge all events by tick and output chronologically
        events = []

        for i, k in enumerate(rk):
            events.append(("kill", k["tick"], i, k))

        for g in rg:
            events.append(("nade", g["tick"], 0, g))

        # Group blinds by tick (same flash → multiple victims)
        blind_by_tick = defaultdict(list)
        for b in rb:
            blind_by_tick[b["tick"]].append(b)
        for tick, blist in blind_by_tick.items():
            events.append(("blind", tick, 0, blist))

        # Add player movement events
        for mov_tick, mov_name, mov_team, mov_loc in round_movements.get(rnd, []):
            events.append(("move", mov_tick, 0, (mov_name, mov_team, mov_loc)))

        # Add bomb events
        for b in round_bomb_map.get(rnd, []):
            events.append(("bomb", b["tick"], 0, b))

        # Add non-lethal damage events (significant only, >=20 dmg)
        for h in round_hurts_map.get(rnd, []):
            if h["dmg"] >= 20:
                events.append(("hurt", h["tick"], 0, h))

        events.sort(key=lambda x: x[1])

        # Group MOVE events by tick for compact output
        move_groups = defaultdict(list)  # tick -> [(name, team, loc)]
        non_move_events = []
        for etype, tick, idx, data in events:
            if etype == "move":
                mov_name, mov_team, mov_loc = data
                # Skip spawn positions at round start
                if "Spawn" in mov_loc and tick == round_start_tick.get(rnd, 0):
                    continue
                move_groups[tick].append((mov_name, mov_team, mov_loc))
            else:
                non_move_events.append((etype, tick, idx, data))

        # Merge moves back as grouped events
        all_events = list(non_move_events)
        for mv_tick, mv_list in move_groups.items():
            all_events.append(("move_group", mv_tick, 0, mv_list))
        all_events.sort(key=lambda x: x[1])

        for etype, tick, idx, data in all_events:
            t = tick_to_sec(tick, rnd)
            t_prefix = f"[{t:>4}] " if t else "       "

            if etype == "kill":
                k = data
                tags = []
                if k["headshot"]:
                    tags.append("HS")
                if k["penetrated"]:
                    tags.append("WB")
                if k["noscope"]:
                    tags.append("NS")
                if k["thrusmoke"]:
                    tags.append("SM")
                if k["attackerblind"]:
                    tags.append("BL")

                tag_str = f" {' '.join(tags)}" if tags else ""

                atk = k['attacker'] or "?"
                atk_loc = f"@{k['attacker_loc']}" if k["attacker_loc"] else ""
                vic_loc = f"@{k['victim_loc']}" if k["victim_loc"] else ""

                assist_str = f" (+{k['assister']})" if k.get("assister") else ""

                ann = annotations.get(idx, [])
                ann_str = f" ←{','.join(ann)}" if ann else ""

                # View angles (pitch/yaw)
                view_str = ""
                if k.get("attacker_view"):
                    # pitch: positive=down, negative=up. yaw: rotation (-180 to 180)
                    view_str = f" VIEW:{k['attacker_view'][0]}/{k['attacker_view'][1]}"

                lines.append(
                    f"  {t_prefix}KILL {atk}{atk_loc}→{k['victim']}{vic_loc} "
                    f"[{k['weapon']}]{tag_str}{assist_str}{ann_str}{view_str}"
                )

            elif etype == "nade":
                g = data
                from_str = f"@{g['from_loc']}" if g.get("from_loc") else ""
                # Coordinates
                pos_str = ""
                if "x" in g:
                    pos_str = f" POS:{g['x']}/{g['y']}/{g['z']}"
                lines.append(f"  {t_prefix}NADE {g['player']}{from_str} [{g['type']}] {pos_str}")

            elif etype == "move_group":
                # Group by team: T: a→X, b→Y | CT: c→Z
                t_moves = []
                ct_moves = []
                for mv_name, mv_team, mv_loc in data:
                    entry = f"{mv_name}→{mv_loc}"
                    if mv_team == 2:
                        t_moves.append(entry)
                    else:
                        ct_moves.append(entry)
                parts = []
                if t_moves:
                    parts.append(f"T: {', '.join(t_moves)}")
                if ct_moves:
                    parts.append(f"CT: {', '.join(ct_moves)}")
                if parts:
                    lines.append(f"  {t_prefix}POS {' | '.join(parts)}")

            elif etype == "bomb":
                b = data
                if b["type"] == "plant":
                    lines.append(f"  {t_prefix}💣 PLANT {b['player']}→{b['site']}")
                elif b["type"] == "defuse":
                    lines.append(f"  {t_prefix}🔧 DEFUSE {b['player']}→{b['site']}")
                elif b["type"] == "explode":
                    lines.append(f"  {t_prefix}💥 EXPLODE {b['site']}")

            elif etype == "hurt":
                h = data
                atk = h['attacker'] or "?"
                dmg_show = h.get("actual_dmg", h["dmg"])
                lines.append(
                    f"  {t_prefix}DMG {atk}→{h['victim']} "
                    f"-{dmg_show}hp({h['health_after']}hp) [{h['weapon']}] {h['hitgroup']}"
                )

            elif etype == "blind":
                blist = data
                if blist:
                    attacker = blist[0]["attacker"] or "?"
                    atk_sid = blist[0]["attacker_sid"]
                    rpe = round_player_econ.get(rnd, {})
                    atk_team = rpe.get(atk_sid, {}).get("team", 0) or team_map.get(atk_sid, 0)

                    victims = []
                    for b in blist:
                        vic_team = rpe.get(b["victim_sid"], {}).get("team", 0) or team_map.get(b["victim_sid"], 0)
                        team_tag = " TEAM!" if (vic_team == atk_team and vic_team != 0) else ""
                        victims.append(f"{b['victim']}({b['duration']:.1f}s{team_tag})")

                    lines.append(f"  {t_prefix}FLASH {attacker}→{', '.join(victims)}")

        if result_str:
            clutch = clutch_events.get(rnd)
            clutch_str = ""
            if clutch:
                outcome = "✅" if clutch["won"] else "❌"
                clutch_str = f" | CLUTCH 1v{clutch['vs']} {clutch['player']} {outcome}"
            lines.append(f"  RESULT: {result_str}{clutch_str}")

    return "\n".join(lines)


# ==========================================
#  Cache
# ==========================================

def get_cache_path(match_id: str) -> str:
    os.makedirs(MATCHES_DIR, exist_ok=True)
    return os.path.join(MATCHES_DIR, f"{match_id}.txt")


def load_cache(match_id: str) -> str | None:
    path = get_cache_path(match_id)
    if os.path.isfile(path):
        with open(path, "r") as f:
            return f.read()
    return None


def save_cache(match_id: str, log: str):
    path = get_cache_path(match_id)
    with open(path, "w") as f:
        f.write(log)


# ==========================================
#  Main
# ==========================================

def main():
    ap = argparse.ArgumentParser(description="Analyze last CS2 demo via Leetify + demoparser2")
    ap.add_argument("--username", required=True, help="Telegram username")
    ap.add_argument("--match-index", type=int, default=0, help="0=last, 1=before last, etc.")
    ap.add_argument("--round", type=int, default=None, help="Show only specific round")
    ap.add_argument("--no-cache", action="store_true", help="Force re-download and re-parse")
    args, unknown = ap.parse_known_args()

    username = args.username.lstrip('@')

    # 1. Resolve Steam ID
    steam_id = get_steam_id(username)
    print(f"🎮 Steam ID: {steam_id}", file=sys.stderr)

    # 2. Fetch matches
    matches = fetch_matches(steam_id, limit=max(args.match_index + 1, 5))
    if not matches or args.match_index >= len(matches):
        print(f"❌ Матч с индексом {args.match_index} не найден", file=sys.stderr)
        sys.exit(1)

    match = matches[args.match_index]
    match_id = match.get("id", "unknown")
    replay_url = match.get('replay_url')

    # 3. Check cache
    log = None
    if not args.no_cache:
        log = load_cache(match_id)
        if log:
            print(f"📦 Загружен из кеша: {match_id}", file=sys.stderr)

    # 4. Download & parse if not cached
    if log is None:
        if not replay_url:
            print("❌ Нет ссылки на демку", file=sys.stderr)
            sys.exit(1)

        with tempfile.TemporaryDirectory(prefix="cs2demo_") as tmp_dir:
            demo_path = download_demo(replay_url, tmp_dir)
            print("🔍 Парсинг демки...", file=sys.stderr)
            log = parse_demo_to_log(demo_path, match)

        save_cache(match_id, log)
        print(f"💾 Сохранено: {get_cache_path(match_id)}", file=sys.stderr)

    # 5. Output (optionally filter by round)
    if args.round is not None:
        # Extract specific round from log
        in_round = False
        round_marker = f"--- R{args.round} "
        filtered = []
        for line in log.split("\n"):
            if line.startswith("--- R"):
                in_round = line.startswith(round_marker)
            if in_round:
                filtered.append(line)

        # Also include header (everything before first round)
        header_lines = []
        for line in log.split("\n"):
            if line.startswith("--- R"):
                break
            header_lines.append(line)

        print("\n".join(header_lines))
        print()
        print("\n".join(filtered))
    else:
        print(log)

    print("\n✅ Анализ завершен!", file=sys.stderr)


if __name__ == "__main__":
    main()
