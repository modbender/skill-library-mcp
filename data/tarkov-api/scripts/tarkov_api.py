#!/usr/bin/env python3
import argparse
import csv
import json
import os
import sys
import time
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List

DEFAULT_ENDPOINT = "https://api.tarkov.dev/graphql"
MAX_LIMIT = 100
SAFE_ENDPOINT_PREFIXES = (
    "https://api.tarkov.dev/graphql",
    "https://api.tarkov.dev/",
)

WIKI_API = "https://escapefromtarkov.fandom.com/api.php"
SAFE_WIKI_PREFIXES = (
    "https://escapefromtarkov.fandom.com/api.php",
)


def die(msg: str, code: int = 1) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def clamp_limit(n: int, default: int = 20) -> int:
    if n is None:
        return default
    if n < 1:
        return 1
    if n > MAX_LIMIT:
        return MAX_LIMIT
    return n


def safe_endpoint(endpoint: str, allow_unsafe: bool) -> str:
    endpoint = endpoint.strip()
    if allow_unsafe:
        return endpoint
    if not endpoint.startswith(SAFE_ENDPOINT_PREFIXES):
        die(
            "Refusing unsafe endpoint. Use --allow-unsafe-endpoint only for trusted local testing."
        )
    return endpoint


def safe_wiki_endpoint(endpoint: str, allow_unsafe: bool) -> str:
    endpoint = endpoint.strip()
    if allow_unsafe:
        return endpoint
    if not endpoint.startswith(SAFE_WIKI_PREFIXES):
        die("Refusing unsafe wiki endpoint. Use --allow-unsafe-endpoint only for trusted testing.")
    return endpoint


def get_json_url(url: str, timeout: int, retries: int) -> Dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "accept": "application/json",
            "user-agent": "openclaw-tarkov-skill/1.0",
        },
        method="GET",
    )

    last_err = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                return json.loads(raw)
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
            last_err = e
            if attempt < retries:
                time.sleep(0.6 * (attempt + 1))
            else:
                break

    die(f"HTTP JSON request failed: {last_err}")
    return {}


def post_graphql(
    endpoint: str,
    query: str,
    variables: Dict[str, Any],
    timeout: int,
    retries: int,
) -> Dict[str, Any]:
    vars_local = dict(variables or {})
    original_limit = vars_local.get("limit")

    last_err = None
    for attempt in range(retries + 1):
        payload = json.dumps({"query": query, "variables": vars_local}).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=payload,
            headers={
                "content-type": "application/json",
                "accept": "application/json",
                "user-agent": "openclaw-tarkov-skill/1.0",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                data = json.loads(raw)
                if "errors" in data:
                    err_msg = "; ".join(
                        e.get("message", "GraphQL error") for e in data.get("errors", [])
                    )
                    raise RuntimeError(err_msg)
                return data.get("data", {})
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            RuntimeError,
            json.JSONDecodeError,
            TimeoutError,
            socket.timeout,
        ) as e:
            last_err = e

            # Timeout-specific fallback: reduce limit for the next attempt.
            is_timeout = isinstance(e, (TimeoutError, socket.timeout))
            current_limit = vars_local.get("limit")
            if is_timeout and isinstance(current_limit, int) and current_limit > 20:
                vars_local["limit"] = max(20, current_limit // 2)

            if attempt < retries:
                time.sleep(0.6 * (attempt + 1))
            else:
                break

    final_limit = vars_local.get("limit")
    if isinstance(original_limit, int) and isinstance(final_limit, int) and final_limit < original_limit:
        die(
            f"GraphQL request failed after retries: {last_err} "
            f"(limit auto-reduced from {original_limit} to {final_limit})"
        )
    die(f"GraphQL request failed after retries: {last_err}")
    return {}


def print_json(obj: Any) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def fmt_rub(v: Any) -> str:
    if v is None:
        return "-"
    try:
        return f"{int(v):,}₽"
    except Exception:
        return str(v)


def load_stash_items(path: str) -> List[Dict[str, Any]]:
    """
    Supports:
    - JSON array: [{"name":"LEDX Skin Transilluminator","count":2}, ...]
    - CSV: name,count
    """
    if not os.path.exists(path):
        die(f"stash file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    if not raw:
        die("stash file is empty")

    # Try JSON first
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            out = []
            for row in parsed:
                if not isinstance(row, dict):
                    continue
                name = str(row.get("name", "")).strip()
                count = int(row.get("count", 0) or 0)
                if name and count > 0:
                    out.append({"name": name, "count": count})
            if out:
                return out
    except Exception:
        pass

    # Fallback to CSV
    out = []
    reader = csv.DictReader(raw.splitlines())
    for row in reader:
        name = str(row.get("name", "")).strip()
        try:
            count = int(row.get("count", 0) or 0)
        except Exception:
            count = 0
        if name and count > 0:
            out.append({"name": name, "count": count})

    if not out:
        die("stash file parse failed. Expected JSON array or CSV with columns: name,count")
    return out


def best_match_item(candidates: List[Dict[str, Any]], requested_name: str) -> Dict[str, Any]:
    if not candidates:
        return {}
    needle = requested_name.strip().lower()
    for it in candidates:
        if (it.get("name") or "").strip().lower() == needle:
            return it
    for it in candidates:
        if (it.get("shortName") or "").strip().lower() == needle:
            return it
    for it in candidates:
        if needle in (it.get("name") or "").strip().lower():
            return it
    return candidates[0]


def cmd_status(args):
    query = """
    query {
      status {
        currentStatuses { name statusCode message }
      }
    }
    """
    data = post_graphql(args.endpoint, query, {}, args.timeout, args.retries)
    statuses = data.get("status", {}).get("currentStatuses", [])
    if args.json:
        print_json(statuses)
        return
    print("Tarkov Service Status")
    print("-" * 60)
    for s in statuses:
        name = s.get("name", "?")
        code = s.get("statusCode", "?")
        msg = s.get("message") or ""
        print(f"{name:24} {code:10} {msg}")


def cmd_item_search(args):
    query = """
    query($name: String!, $lang: LanguageCode, $gm: GameMode, $limit: Int) {
      items(name: $name, lang: $lang, gameMode: $gm, limit: $limit) {
        id
        name
        shortName
        normalizedName
        types
        avg24hPrice
        low24hPrice
        high24hPrice
        lastLowPrice
        lastOfferCount
        wikiLink
      }
    }
    """
    vars_ = {
        "name": args.name,
        "lang": args.lang,
        "gm": args.game_mode,
        "limit": clamp_limit(args.limit, 20),
    }
    data = post_graphql(args.endpoint, query, vars_, args.timeout, args.retries)
    items = data.get("items", [])

    if args.json:
        print_json(items)
        return

    print(f"Items matching '{args.name}' (mode={args.game_mode}, lang={args.lang})")
    print("-" * 110)
    for it in items:
        print(
            f"{it.get('name','?')[:40]:40} "
            f"avg:{fmt_rub(it.get('avg24hPrice')):>12} "
            f"low:{fmt_rub(it.get('low24hPrice')):>12} "
            f"offers:{str(it.get('lastOfferCount','-')):>6}"
        )


def cmd_item_price(args):
    query = """
    query($name: String!, $lang: LanguageCode, $gm: GameMode, $limit: Int) {
      items(name: $name, lang: $lang, gameMode: $gm, limit: $limit) {
        name
        shortName
        avg24hPrice
        low24hPrice
        high24hPrice
        lastLowPrice
        lastOfferCount
        sellFor {
          price
          priceRUB
          currency
          vendor { name normalizedName }
        }
      }
    }
    """
    vars_ = {
        "name": args.name,
        "lang": args.lang,
        "gm": args.game_mode,
        "limit": clamp_limit(args.limit, 8),
    }
    data = post_graphql(args.endpoint, query, vars_, args.timeout, args.retries)
    items = data.get("items", [])

    if args.json:
        print_json(items)
        return

    if not items:
        print("No matching items.")
        return

    for it in items:
        print("=" * 80)
        print(f"{it.get('name')} ({it.get('shortName')})")
        print(
            f"Avg24h: {fmt_rub(it.get('avg24hPrice'))} | "
            f"Low24h: {fmt_rub(it.get('low24hPrice'))} | "
            f"High24h: {fmt_rub(it.get('high24hPrice'))} | "
            f"Last offer count: {it.get('lastOfferCount','-')}"
        )
        offers = sorted(
            (it.get("sellFor") or []),
            key=lambda x: (x.get("priceRUB") or 0),
            reverse=True,
        )
        print("Best sell routes:")
        for o in offers[:8]:
            vendor = (o.get("vendor") or {}).get("name", "?")
            print(
                f"  - {vendor:16} {fmt_rub(o.get('priceRUB')):>10} "
                f"({o.get('price','-')} {o.get('currency','')})"
            )


def cmd_ammo_compare(args):
    if len(args.names) < 2:
        die("Provide at least 2 ammo names for comparison.")

    query = """
    query($names: [String!], $lang: LanguageCode, $gm: GameMode, $limit: Int) {
      items(names: $names, lang: $lang, gameMode: $gm, limit: $limit) {
        name
        shortName
        avg24hPrice
        properties {
          __typename
          ... on ItemPropertiesAmmo {
            damage
            penetrationPower
            armorDamage
            fragmentationChance
            ricochetChance
            initialSpeed
            lightBleedModifier
            heavyBleedModifier
          }
        }
      }
    }
    """
    vars_ = {
        "names": args.names,
        "lang": args.lang,
        "gm": args.game_mode,
        "limit": clamp_limit(args.limit, 40),
    }
    data = post_graphql(args.endpoint, query, vars_, args.timeout, args.retries)
    items = data.get("items", [])

    rows = []
    for it in items:
        props = it.get("properties") or {}
        if props.get("__typename") != "ItemPropertiesAmmo":
            continue
        pen = props.get("penetrationPower") or 0
        dmg = props.get("damage") or 0
        score = (pen * 1.9) + (dmg * 0.7)
        rows.append(
            {
                "name": it.get("name"),
                "short": it.get("shortName"),
                "price": it.get("avg24hPrice"),
                "pen": pen,
                "dmg": dmg,
                "armorDmg": props.get("armorDamage"),
                "frag": props.get("fragmentationChance"),
                "speed": props.get("initialSpeed"),
                "score": round(score, 2),
            }
        )

    rows.sort(key=lambda r: r["score"], reverse=True)

    if args.json:
        print_json(rows)
        return

    print("Ammo compare (higher score favors pen + damage balance)")
    print("-" * 110)
    print(f"{'Ammo':34} {'Pen':>4} {'Dmg':>4} {'Armor':>5} {'Frag%':>6} {'Speed':>7} {'Price':>12} {'Score':>7}")
    for r in rows:
        print(
            f"{(r['name'] or '?')[:34]:34} "
            f"{str(r['pen']):>4} {str(r['dmg']):>4} {str(r['armorDmg'] or '-'):>5} "
            f"{str(r['frag'] or '-'):>6} {str(r['speed'] or '-'):>7} "
            f"{fmt_rub(r['price']):>12} {str(r['score']):>7}"
        )


def cmd_task_lookup(args):
    query = """
    query($lang: LanguageCode, $gm: GameMode, $limit: Int) {
      tasks(lang: $lang, gameMode: $gm, limit: $limit) {
        id
        name
        normalizedName
        minPlayerLevel
        kappaRequired
        lightkeeperRequired
        trader { name }
        map { name }
        taskRequirements { task { name } status }
      }
    }
    """
    vars_ = {
        "lang": args.lang,
        "gm": args.game_mode,
        "limit": clamp_limit(args.limit, 200),
    }
    data = post_graphql(args.endpoint, query, vars_, args.timeout, args.retries)
    tasks = data.get("tasks", [])

    needle = args.name.lower()
    filtered = [t for t in tasks if needle in (t.get("name", "").lower())]

    if args.json:
        print_json(filtered)
        return

    if not filtered:
        print("No task matches.")
        return

    for t in filtered[:20]:
        print("=" * 100)
        print(f"{t.get('name')} | Trader: {(t.get('trader') or {}).get('name','?')} | Map: {(t.get('map') or {}).get('name','Any')}")
        print(
            f"Min level: {t.get('minPlayerLevel','-')} | "
            f"Kappa req: {t.get('kappaRequired')} | "
            f"Lightkeeper req: {t.get('lightkeeperRequired')}"
        )
        reqs = t.get("taskRequirements") or []
        if reqs:
            print("Prerequisites:")
            for r in reqs[:12]:
                rname = ((r.get("task") or {}).get("name") or "?")
                status = ",".join(r.get("status") or [])
                print(f"  - {rname} [{status}]")


def cmd_map_bosses(args):
    query = """
    query($name: [String!], $lang: LanguageCode, $gm: GameMode, $limit: Int) {
      maps(name: $name, lang: $lang, gameMode: $gm, limit: $limit) {
        name
        bosses {
          boss { name normalizedName }
          spawnChance
          spawnTime
          spawnTimeRandom
          spawnLocations { name chance }
        }
      }
    }
    """
    vars_ = {
        "name": [args.map_name],
        "lang": args.lang,
        "gm": args.game_mode,
        "limit": 10,
    }
    data = post_graphql(args.endpoint, query, vars_, args.timeout, args.retries)
    maps = data.get("maps", [])

    if args.json:
        print_json(maps)
        return

    if not maps:
        print("No map match.")
        return

    for m in maps:
        print(f"Map: {m.get('name')}")
        print("-" * 80)
        for b in m.get("bosses", []):
            boss = (b.get("boss") or {}).get("name", "?")
            chance = b.get("spawnChance")
            stime = b.get("spawnTime")
            srand = b.get("spawnTimeRandom")
            print(f"{boss:20} spawnChance={chance} spawnTime={stime} random={srand}")
            locs = b.get("spawnLocations") or []
            for loc in locs[:4]:
                print(f"  - {loc.get('name','?')} ({loc.get('chance','?')}%)")


def cmd_stash_value(args):
    stash_rows = load_stash_items(args.items_file)

    query = """
    query($names: [String], $lang: LanguageCode, $gm: GameMode, $limit: Int) {
      items(names: $names, lang: $lang, gameMode: $gm, limit: $limit) {
        id
        name
        shortName
        avg24hPrice
        low24hPrice
        high24hPrice
        sellFor {
          priceRUB
          vendor { name normalizedName }
        }
      }
    }
    """

    unique_names = list({r["name"] for r in stash_rows})
    vars_ = {
        "names": unique_names,
        "lang": args.lang,
        "gm": args.game_mode,
        "limit": clamp_limit(max(len(unique_names) * 3, 40), 100),
    }
    data = post_graphql(args.endpoint, query, vars_, args.timeout, args.retries)
    candidates = data.get("items", [])

    valued = []
    missing = []
    for row in stash_rows:
        item = best_match_item(candidates, row["name"])
        if not item:
            missing.append(row)
            continue

        count = row["count"]
        avg24 = item.get("avg24hPrice") or 0
        low24 = item.get("low24hPrice") or 0
        best_sell = max([(s.get("priceRUB") or 0) for s in (item.get("sellFor") or [])] + [0])

        valued.append(
            {
                "inputName": row["name"],
                "matchedName": item.get("name"),
                "count": count,
                "avg24hUnit": avg24,
                "low24hUnit": low24,
                "bestSellUnit": best_sell,
                "avg24hTotal": avg24 * count,
                "low24hTotal": low24 * count,
                "bestSellTotal": best_sell * count,
            }
        )

    totals = {
        "itemsValued": len(valued),
        "itemsMissing": len(missing),
        "avg24hTotal": sum(v["avg24hTotal"] for v in valued),
        "low24hTotal": sum(v["low24hTotal"] for v in valued),
        "bestSellTotal": sum(v["bestSellTotal"] for v in valued),
    }

    result = {"totals": totals, "valued": valued, "missing": missing}
    if args.json:
        print_json(result)
        return

    print("Stash Value Snapshot")
    print("-" * 90)
    print(
        f"Items valued: {totals['itemsValued']} | Missing: {totals['itemsMissing']} | "
        f"Low24h total: {fmt_rub(totals['low24hTotal'])} | "
        f"Avg24h total: {fmt_rub(totals['avg24hTotal'])} | "
        f"Best-sell total: {fmt_rub(totals['bestSellTotal'])}"
    )
    print("Top value items (by low24h total):")
    for row in sorted(valued, key=lambda x: x["low24hTotal"], reverse=True)[:15]:
        print(
            f"  - {(row['matchedName'] or '?')[:40]:40} x{row['count']:<4} "
            f"low24h:{fmt_rub(row['low24hTotal']):>12} best:{fmt_rub(row['bestSellTotal']):>12}"
        )
    if missing:
        print("Unmatched stash rows:")
        for m in missing[:20]:
            print(f"  - {m['name']} x{m['count']}")


def cmd_trader_flip(args):
    query = """
    query($name: String!, $lang: LanguageCode, $gm: GameMode, $limit: Int) {
      items(name: $name, lang: $lang, gameMode: $gm, limit: $limit) {
        name
        shortName
        avg24hPrice
        buyFor {
          priceRUB
          currency
          vendor { name normalizedName }
        }
        sellFor {
          priceRUB
          currency
          vendor { name normalizedName }
        }
      }
    }
    """
    vars_ = {
        "name": args.name,
        "lang": args.lang,
        "gm": args.game_mode,
        "limit": clamp_limit(args.limit, 60),
    }
    data = post_graphql(args.endpoint, query, vars_, args.timeout, args.retries)
    items = data.get("items", [])

    flips = []
    for it in items:
        buys = [b for b in (it.get("buyFor") or []) if (b.get("priceRUB") or 0) > 0]
        if not args.include_flea_buy:
            buys = [
                b for b in buys
                if (b.get("vendor") or {}).get("normalizedName") not in ("fleaMarket", "flea market")
                and (b.get("vendor") or {}).get("name", "").lower() != "flea market"
            ]
        sells = [s for s in (it.get("sellFor") or []) if (s.get("priceRUB") or 0) > 0]
        if not buys or not sells:
            continue

        best_buy = min(buys, key=lambda x: x.get("priceRUB") or 10**12)
        best_sell = max(sells, key=lambda x: x.get("priceRUB") or 0)

        buy_rub = best_buy.get("priceRUB") or 0
        sell_rub = best_sell.get("priceRUB") or 0
        spread = sell_rub - buy_rub
        roi = ((spread / buy_rub) * 100.0) if buy_rub > 0 else 0.0

        if spread < args.min_spread:
            continue

        flips.append(
            {
                "name": it.get("name"),
                "buyFrom": (best_buy.get("vendor") or {}).get("name"),
                "buyRUB": buy_rub,
                "sellTo": (best_sell.get("vendor") or {}).get("name"),
                "sellRUB": sell_rub,
                "spreadRUB": spread,
                "roiPercent": round(roi, 2),
            }
        )

    flips.sort(key=lambda x: (x["spreadRUB"], x["roiPercent"]), reverse=True)

    if args.json:
        print_json(flips)
        return

    print("Trader Flip Detector (gross spread only; fees/limits not included)")
    print("-" * 110)
    if not flips:
        print("No candidates met your minimum spread.")
        return
    print(f"{'Item':34} {'Buy From':14} {'Buy':>10} {'Sell To':14} {'Sell':>10} {'Spread':>11} {'ROI%':>7}")
    for f in flips[: args.top]:
        print(
            f"{(f['name'] or '?')[:34]:34} {str(f['buyFrom'] or '?')[:14]:14} {fmt_rub(f['buyRUB']):>10} "
            f"{str(f['sellTo'] or '?')[:14]:14} {fmt_rub(f['sellRUB']):>10} {fmt_rub(f['spreadRUB']):>11} {str(f['roiPercent']):>7}"
        )


def cmd_map_risk(args):
    map_query = """
    query($name: [String!], $lang: LanguageCode, $gm: GameMode) {
      maps(name: $name, lang: $lang, gameMode: $gm, limit: 5) {
        name
        bosses {
          boss { name }
          spawnChance
        }
      }
    }
    """
    task_query = """
    query($lang: LanguageCode, $gm: GameMode, $limit: Int) {
      tasks(lang: $lang, gameMode: $gm, limit: $limit) {
        name
        map { name }
        objectives { maps { name } }
      }
    }
    """

    mvars = {"name": [args.map_name], "lang": args.lang, "gm": args.game_mode}
    tvars = {"lang": args.lang, "gm": args.game_mode, "limit": clamp_limit(args.task_limit, 400)}

    mdata = post_graphql(args.endpoint, map_query, mvars, args.timeout, args.retries)
    tdata = post_graphql(args.endpoint, task_query, tvars, args.timeout, args.retries)

    maps = mdata.get("maps", [])
    if not maps:
        die("Map not found for risk scoring.")
    m = maps[0]
    map_name = (m.get("name") or args.map_name).strip().lower()

    bosses = m.get("bosses") or []
    probs = []
    for b in bosses:
        ch = b.get("spawnChance")
        if ch is None:
            continue
        try:
            p = float(ch)
            if p > 1.0:
                p = p / 100.0
            p = max(0.0, min(1.0, p))
            probs.append(p)
        except Exception:
            pass

    boss_presence = 1.0
    for p in probs:
        boss_presence *= (1.0 - p)
    boss_presence = 1.0 - boss_presence if probs else 0.0

    focus_terms = [x.strip().lower() for x in (args.task_focus or []) if x.strip()]
    tasks = tdata.get("tasks", [])
    map_task_count = 0
    focused_overlap = 0

    for t in tasks:
        tname = (t.get("name") or "").strip()
        tname_l = tname.lower()

        map_hits = set()
        if (t.get("map") or {}).get("name"):
            map_hits.add(((t.get("map") or {}).get("name") or "").strip().lower())

        for obj in (t.get("objectives") or []):
            for om in (obj.get("maps") or []):
                n = (om.get("name") or "").strip().lower()
                if n:
                    map_hits.add(n)

        touches_map = map_name in map_hits
        if not touches_map:
            continue

        map_task_count += 1
        if focus_terms:
            if any(term in tname_l for term in focus_terms):
                focused_overlap += 1

    base_task_component = map_task_count * 0.2
    focus_task_component = focused_overlap * 5.0
    task_component = min(30.0, base_task_component + focus_task_component)

    boss_component = min(70.0, boss_presence * 70.0)
    score = round(boss_component + task_component, 2)

    risk_band = "LOW"
    if score >= 65:
        risk_band = "HIGH"
    elif score >= 40:
        risk_band = "MEDIUM"

    result = {
        "map": m.get("name"),
        "riskScore": score,
        "riskBand": risk_band,
        "bossComponent": round(boss_component, 2),
        "taskComponent": round(task_component, 2),
        "bossPresenceProbability": round(boss_presence, 4),
        "bossCount": len(bosses),
        "mapTaskCount": map_task_count,
        "focusedTaskOverlap": focused_overlap,
        "focusTerms": focus_terms,
    }

    if args.json:
        print_json(result)
        return

    print(f"Map Risk Score: {result['map']} -> {result['riskScore']} ({result['riskBand']})")
    print("-" * 90)
    print(
        f"Boss pressure: {result['bossComponent']} / 70 (presence≈{round(result['bossPresenceProbability']*100,1)}%) | "
        f"Task pressure: {result['taskComponent']} / 30"
    )
    print(
        f"Bosses tracked: {result['bossCount']} | Map task matches: {result['mapTaskCount']}"
        + (f" | Focus overlap: {result['focusedTaskOverlap']}" if focus_terms else "")
    )
    print("Interpretation: combine this score with your kit value and objective urgency.")


def cmd_raid_kit(args):
    if len(args.ammo_names) < 1:
        die("Provide at least one ammo option via --ammo-names")

    # 1) Ammo snapshot
    ammo_query = """
    query($names: [String!], $lang: LanguageCode, $gm: GameMode, $limit: Int) {
      items(names: $names, lang: $lang, gameMode: $gm, limit: $limit) {
        name
        shortName
        avg24hPrice
        properties {
          __typename
          ... on ItemPropertiesAmmo {
            damage
            penetrationPower
            armorDamage
            fragmentationChance
            initialSpeed
          }
        }
      }
    }
    """

    ammo_vars = {
        "names": args.ammo_names,
        "lang": args.lang,
        "gm": args.game_mode,
        "limit": clamp_limit(max(20, len(args.ammo_names) * 3), 80),
    }
    ammo_data = post_graphql(args.endpoint, ammo_query, ammo_vars, args.timeout, args.retries)
    items = ammo_data.get("items", [])

    ammo_rows = []
    for it in items:
        p = it.get("properties") or {}
        if p.get("__typename") != "ItemPropertiesAmmo":
            continue
        pen = p.get("penetrationPower") or 0
        dmg = p.get("damage") or 0
        price = it.get("avg24hPrice") or 0
        # efficiency rewards high pen/dmg while penalizing expensive rounds
        efficiency = ((pen * 2.0) + (dmg * 0.8)) - (price / 12000.0)
        ammo_rows.append(
            {
                "name": it.get("name"),
                "pen": pen,
                "dmg": dmg,
                "price": price,
                "armor": p.get("armorDamage") or 0,
                "frag": p.get("fragmentationChance") or 0,
                "speed": p.get("initialSpeed") or 0,
                "efficiency": round(efficiency, 2),
            }
        )

    if not ammo_rows:
        die("No ammo options resolved from your input names.")

    ammo_rows.sort(key=lambda x: x["efficiency"], reverse=True)

    # 2) Map risk snapshot
    risk_args = argparse.Namespace(
        endpoint=args.endpoint,
        timeout=args.timeout,
        retries=args.retries,
        map_name=args.map_name,
        task_focus=args.task_focus,
        task_limit=args.task_limit,
        lang=args.lang,
        game_mode=args.game_mode,
        json=True,
    )

    # reuse map-risk logic without printing
    map_query = """
    query($name: [String!], $lang: LanguageCode, $gm: GameMode) {
      maps(name: $name, lang: $lang, gameMode: $gm, limit: 5) {
        name
        bosses { boss { name } spawnChance }
      }
    }
    """
    task_query = """
    query($lang: LanguageCode, $gm: GameMode, $limit: Int) {
      tasks(lang: $lang, gameMode: $gm, limit: $limit) {
        name
        map { name }
        objectives { maps { name } }
      }
    }
    """

    mvars = {"name": [risk_args.map_name], "lang": risk_args.lang, "gm": risk_args.game_mode}
    tvars = {"lang": risk_args.lang, "gm": risk_args.game_mode, "limit": clamp_limit(risk_args.task_limit, 400)}

    mdata = post_graphql(args.endpoint, map_query, mvars, args.timeout, args.retries)
    tdata = post_graphql(args.endpoint, task_query, tvars, args.timeout, args.retries)

    maps = mdata.get("maps", [])
    if not maps:
        die("Map not found for raid-kit recommendation.")
    m = maps[0]
    map_name_l = (m.get("name") or args.map_name).strip().lower()

    probs = []
    for b in (m.get("bosses") or []):
        ch = b.get("spawnChance")
        if ch is None:
            continue
        try:
            p = float(ch)
            if p > 1.0:
                p = p / 100.0
            probs.append(max(0.0, min(1.0, p)))
        except Exception:
            pass

    boss_presence = 1.0
    for p in probs:
        boss_presence *= (1.0 - p)
    boss_presence = 1.0 - boss_presence if probs else 0.0

    focus_terms = [x.strip().lower() for x in (args.task_focus or []) if x.strip()]
    map_task_count = 0
    focused_overlap = 0
    for t in (tdata.get("tasks") or []):
        tname = (t.get("name") or "").lower()
        map_hits = set()
        if (t.get("map") or {}).get("name"):
            map_hits.add(((t.get("map") or {}).get("name") or "").strip().lower())
        for obj in (t.get("objectives") or []):
            for om in (obj.get("maps") or []):
                n = (om.get("name") or "").strip().lower()
                if n:
                    map_hits.add(n)
        if map_name_l not in map_hits:
            continue
        map_task_count += 1
        if focus_terms and any(term in tname for term in focus_terms):
            focused_overlap += 1

    task_component = min(30.0, (map_task_count * 0.2) + (focused_overlap * 5.0))
    boss_component = min(70.0, boss_presence * 70.0)
    risk_score = round(task_component + boss_component, 2)

    # 3) Recommendation policy
    best = ammo_rows[0]
    conservative = min(ammo_rows, key=lambda x: x["price"] if x["price"] > 0 else 10**9)

    if risk_score >= 70:
        posture = "SURVIVE-FIRST"
        chosen = conservative if conservative["price"] > 0 else best
        armor_tier = "Class 5+ if available"
        meds = "Heavy bleed + painkiller + extra CMS/surv"
        utility = "2x nades max, prioritize mobility and extract discipline"
    elif risk_score >= 45:
        posture = "BALANCED"
        chosen = best
        armor_tier = "Class 4-5"
        meds = "Standard bleed kit + painkiller + CMS"
        utility = "2-3 nades, controlled fights only"
    else:
        posture = "AGGRESSION-WINDOW"
        chosen = best
        armor_tier = "Class 4 acceptable, optimize ergo"
        meds = "Standard med stack"
        utility = "Bring extra ammo and pressure tools"

    result = {
        "map": m.get("name"),
        "riskScore": risk_score,
        "posture": posture,
        "recommendedAmmo": chosen,
        "bestAmmoByEfficiency": best,
        "lowestCostAmmo": conservative,
        "armorGuidance": armor_tier,
        "medGuidance": meds,
        "utilityGuidance": utility,
        "ammoTable": ammo_rows,
        "taskContext": {
            "mapTaskCount": map_task_count,
            "focusTerms": focus_terms,
            "focusedTaskOverlap": focused_overlap,
        },
    }

    if args.json:
        print_json(result)
        return

    print(f"Raid Kit Recommendation: {result['map']} | Risk {result['riskScore']} | {posture}")
    print("-" * 110)
    print(
        f"Recommended ammo: {chosen['name']} (pen={chosen['pen']}, dmg={chosen['dmg']}, avg={fmt_rub(chosen['price'])})"
    )
    print(f"Armor: {armor_tier}")
    print(f"Meds:  {meds}")
    print(f"Utility:{utility}")
    print("\nAmmo candidates:")
    print(f"{'Ammo':34} {'Pen':>4} {'Dmg':>4} {'Avg':>12} {'Eff':>8}")
    for r in ammo_rows[:12]:
        print(f"{(r['name'] or '?')[:34]:34} {str(r['pen']):>4} {str(r['dmg']):>4} {fmt_rub(r['price']):>12} {str(r['efficiency']):>8}")


def cmd_wiki_search(args):
    wiki_api = safe_wiki_endpoint(args.wiki_api, args.allow_unsafe_endpoint)
    params = {
        "action": "query",
        "list": "search",
        "srsearch": args.query,
        "srlimit": clamp_limit(args.limit, 10),
        "format": "json",
    }
    url = wiki_api + "?" + urllib.parse.urlencode(params)
    data = get_json_url(url, args.timeout, args.retries)
    rows = data.get("query", {}).get("search", [])

    if args.json:
        print_json(rows)
        return

    print(f"Wiki search: {args.query}")
    print("-" * 100)
    for r in rows:
        title = r.get("title", "?")
        ts = r.get("timestamp", "")
        size = r.get("size", "")
        print(f"{title:50} updated:{ts:20} size:{size}")


def cmd_wiki_intro(args):
    wiki_api = safe_wiki_endpoint(args.wiki_api, args.allow_unsafe_endpoint)
    params = {
        "action": "query",
        "prop": "extracts|revisions",
        "exintro": 1,
        "explaintext": 1,
        "titles": args.title,
        "rvprop": "timestamp|user|comment",
        "rvlimit": args.revisions,
        "formatversion": 2,
        "format": "json",
    }
    url = wiki_api + "?" + urllib.parse.urlencode(params)
    data = get_json_url(url, args.timeout, args.retries)
    pages = data.get("query", {}).get("pages", [])
    if not pages:
        die("No wiki page found")
    p = pages[0]

    out = {
        "title": p.get("title"),
        "extract": p.get("extract", ""),
        "revisions": p.get("revisions", []),
        "url": f"https://escapefromtarkov.fandom.com/wiki/{(p.get('title') or '').replace(' ', '_')}",
    }

    if args.json:
        print_json(out)
        return

    print(f"Wiki intro: {out['title']}")
    print("-" * 100)
    print(out["extract"] or "(No extract text returned)")
    print("\nRecent revisions:")
    for r in out["revisions"][: args.revisions]:
        print(f"  - {r.get('timestamp','?')} by {r.get('user','?')} | {r.get('comment','')}")
    print(f"\nPage: {out['url']}")


def cmd_wiki_recent(args):
    wiki_api = safe_wiki_endpoint(args.wiki_api, args.allow_unsafe_endpoint)
    params = {
        "action": "query",
        "list": "recentchanges",
        "rcnamespace": 0,
        "rclimit": clamp_limit(args.limit, 20),
        "rcprop": "title|timestamp|user|comment|sizes|flags",
        "format": "json",
    }
    url = wiki_api + "?" + urllib.parse.urlencode(params)
    data = get_json_url(url, args.timeout, args.retries)
    rows = data.get("query", {}).get("recentchanges", [])

    if args.json:
        print_json(rows)
        return

    print("Wiki recent changes (articles namespace)")
    print("-" * 120)
    for r in rows:
        print(
            f"{(r.get('title') or '?')[:45]:45} {r.get('timestamp','?'):20} "
            f"{(r.get('user') or '?')[:18]:18} {(r.get('comment') or '')[:45]}"
        )


def cmd_raw(args):
    if args.query_file:
        with open(args.query_file, "r", encoding="utf-8") as f:
            query = f.read()
    else:
        query = args.query

    if not query.strip():
        die("Raw mode requires --query or --query-file")

    vars_ = {}
    if args.variables:
        vars_ = json.loads(args.variables)

    data = post_graphql(args.endpoint, query, vars_, args.timeout, args.retries)
    print_json(data)


def build_parser():
    p = argparse.ArgumentParser(
        description="Secure helper for Tarkov.dev GraphQL API (hardcore-friendly presets)."
    )
    p.add_argument(
        "--endpoint",
        default=os.environ.get("TARKOV_API_ENDPOINT", DEFAULT_ENDPOINT),
        help="GraphQL endpoint (default: https://api.tarkov.dev/graphql)",
    )
    p.add_argument("--timeout", type=int, default=20, help="HTTP timeout seconds")
    p.add_argument("--retries", type=int, default=2, help="Retry count on transient failures")
    p.add_argument(
        "--wiki-api",
        default=os.environ.get("TARKOV_WIKI_API", WIKI_API),
        help="Wiki API endpoint (default: escapefromtarkov.fandom.com/api.php)",
    )
    p.add_argument(
        "--allow-unsafe-endpoint",
        action="store_true",
        help="Allow non-tarkov.dev endpoint (for trusted local testing only)",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("status", help="Show EFT service statuses")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("item-search", help="Search items with price context")
    s.add_argument("--name", required=True)
    s.add_argument("--lang", default="en")
    s.add_argument("--game-mode", default="regular", choices=["regular", "pve"])
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_item_search)

    s = sub.add_parser("item-price", help="Deep price and sell-route view for item(s)")
    s.add_argument("--name", required=True)
    s.add_argument("--lang", default="en")
    s.add_argument("--game-mode", default="regular", choices=["regular", "pve"])
    s.add_argument("--limit", type=int, default=8)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_item_price)

    s = sub.add_parser("ammo-compare", help="Compare ammo by pen/dmg/price")
    s.add_argument("--names", nargs="+", required=True)
    s.add_argument("--lang", default="en")
    s.add_argument("--game-mode", default="regular", choices=["regular", "pve"])
    s.add_argument("--limit", type=int, default=40)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_ammo_compare)

    s = sub.add_parser("task-lookup", help="Task lookup with prerequisite chain")
    s.add_argument("--name", required=True)
    s.add_argument("--lang", default="en")
    s.add_argument("--game-mode", default="regular", choices=["regular", "pve"])
    s.add_argument("--limit", type=int, default=200)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_task_lookup)

    s = sub.add_parser("map-bosses", help="Boss spawn summary for a map")
    s.add_argument("--map-name", required=True)
    s.add_argument("--lang", default="en")
    s.add_argument("--game-mode", default="regular", choices=["regular", "pve"])
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_map_bosses)

    s = sub.add_parser("stash-value", help="Estimate stash value from JSON/CSV item list")
    s.add_argument("--items-file", required=True, help="Path to JSON/CSV stash list")
    s.add_argument("--lang", default="en")
    s.add_argument("--game-mode", default="regular", choices=["regular", "pve"])
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_stash_value)

    s = sub.add_parser("trader-flip", help="Find high-spread trader flip candidates")
    s.add_argument("--name", required=True, help="Broad item search seed, e.g. ammo, keycard")
    s.add_argument("--lang", default="en")
    s.add_argument("--game-mode", default="regular", choices=["regular", "pve"])
    s.add_argument("--limit", type=int, default=60)
    s.add_argument("--min-spread", type=int, default=10000)
    s.add_argument("--top", type=int, default=20)
    s.add_argument("--include-flea-buy", action="store_true", help="Include flea market as buy source")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_trader_flip)

    s = sub.add_parser("map-risk", help="Composite map risk from boss pressure + task overlap")
    s.add_argument("--map-name", required=True)
    s.add_argument("--task-focus", nargs="*", default=[], help="Optional task name fragments")
    s.add_argument("--task-limit", type=int, default=400)
    s.add_argument("--lang", default="en")
    s.add_argument("--game-mode", default="regular", choices=["regular", "pve"])
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_map_risk)

    s = sub.add_parser("raid-kit", help="Recommend raid kit posture from map risk + ammo options")
    s.add_argument("--map-name", required=True)
    s.add_argument("--ammo-names", nargs="+", required=True, help="Ammo options to evaluate")
    s.add_argument("--task-focus", nargs="*", default=[], help="Optional task name fragments")
    s.add_argument("--task-limit", type=int, default=400)
    s.add_argument("--lang", default="en")
    s.add_argument("--game-mode", default="regular", choices=["regular", "pve"])
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_raid_kit)

    s = sub.add_parser("wiki-search", help="Search EFT wiki pages by query")
    s.add_argument("--query", required=True)
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_wiki_search)

    s = sub.add_parser("wiki-intro", help="Fetch wiki page intro + recent revision metadata")
    s.add_argument("--title", required=True)
    s.add_argument("--revisions", type=int, default=3)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_wiki_intro)

    s = sub.add_parser("wiki-recent", help="Show recently edited wiki articles")
    s.add_argument("--limit", type=int, default=15)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_wiki_recent)

    s = sub.add_parser("raw", help="Run raw GraphQL query (power users)")
    s.add_argument("--query")
    s.add_argument("--query-file")
    s.add_argument("--variables", help="JSON string of GraphQL variables")
    s.set_defaults(func=cmd_raw)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.endpoint = safe_endpoint(args.endpoint, args.allow_unsafe_endpoint)

    try:
        args.func(args)
    except SystemExit:
        raise
    except Exception as e:
        die(f"Command '{args.cmd}' failed: {e}")


if __name__ == "__main__":
    main()
