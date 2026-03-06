#!/usr/bin/env python3
"""
Track football bet slips, results, and cumulative statistics.

Modes:
  save     -- Save a new bet slip to data/bets/YYYY-MM-DD.json
  result   -- Mark a pick's result (win, loss, void)
  stats    -- Show cumulative statistics (hitrate, ROI, monthly budget)
  history  -- Show bet history for the last N days
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
BETS_DIR = DATA_DIR / "bets"
STATS_FILE = DATA_DIR / "stats.json"
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "settings.json"


def _ensure_dirs():
    BETS_DIR.mkdir(parents=True, exist_ok=True)


def _load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_bet_file(date_str: str) -> Dict[str, Any]:
    path = BETS_DIR / f"{date_str}.json"
    if not path.exists():
        return {"date": date_str, "slips": []}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_bet_file(date_str: str, data: Dict[str, Any]):
    _ensure_dirs()
    path = BETS_DIR / f"{date_str}.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def _load_stats() -> Dict[str, Any]:
    if not STATS_FILE.exists():
        return {
            "total_slips": 0,
            "total_picks": 0,
            "wins": 0,
            "losses": 0,
            "voids": 0,
            "pending": 0,
            "total_staked": 0.0,
            "total_returned": 0.0,
            "monthly": {},
        }
    with open(STATS_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_stats(stats: Dict[str, Any]):
    _ensure_dirs()
    with open(STATS_FILE, "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2, ensure_ascii=False)


def save_bet(data_json: str) -> Dict[str, Any]:
    """Save a new bet slip.

    Expected JSON structure:
    {
      "type": "main" | "backup",
      "stake": 5.0,
      "picks": [
        {
          "match": "Ajax - PSV",
          "competition": "Eredivisie",
          "pick": "BTTS Yes",
          "odds": 1.85,
          "estimated_probability": 0.52,
          "motivation": "Both teams scored in 8 of last 10 matches",
          "risk": "medium"
        }
      ],
      "total_odds": 12.5,
      "notes": "optional notes"
    }
    """
    try:
        slip = json.loads(data_json)
    except json.JSONDecodeError as exc:
        return {"status": "error", "code": "invalid_json", "message": str(exc)}

    if "picks" not in slip or not slip["picks"]:
        return {"status": "error", "code": "no_picks", "message": "Bet slip must contain picks"}

    today = datetime.utcnow().date().isoformat()
    bet_data = _load_bet_file(today)

    total_odds = slip.get("total_odds", 1.0)
    if total_odds <= 0:
        combined = 1.0
        for pick in slip["picks"]:
            combined *= pick.get("odds", 1.0)
        total_odds = round(combined, 2)

    slip_record = {
        "id": len(bet_data["slips"]) + 1,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "type": slip.get("type", "main"),
        "stake": slip.get("stake", 5.0),
        "total_odds": total_odds,
        "potential_return": round(slip.get("stake", 5.0) * total_odds, 2),
        "result": "pending",
        "picks": [],
        "notes": slip.get("notes", ""),
    }

    for pick in slip["picks"]:
        slip_record["picks"].append({
            "match": pick.get("match", ""),
            "competition": pick.get("competition", ""),
            "pick": pick.get("pick", ""),
            "odds": pick.get("odds", 1.0),
            "estimated_probability": pick.get("estimated_probability", 0.0),
            "motivation": pick.get("motivation", ""),
            "risk": pick.get("risk", "medium"),
            "result": "pending",
        })

    bet_data["slips"].append(slip_record)
    _save_bet_file(today, bet_data)

    stats = _load_stats()
    stats["total_slips"] += 1
    stats["total_picks"] += len(slip_record["picks"])
    stats["pending"] += len(slip_record["picks"])
    stats["total_staked"] += slip_record["stake"]

    month_key = today[:7]
    if month_key not in stats["monthly"]:
        stats["monthly"][month_key] = {
            "slips": 0, "picks": 0, "wins": 0, "losses": 0,
            "staked": 0.0, "returned": 0.0,
        }
    stats["monthly"][month_key]["slips"] += 1
    stats["monthly"][month_key]["picks"] += len(slip_record["picks"])
    stats["monthly"][month_key]["staked"] += slip_record["stake"]
    _save_stats(stats)

    return {
        "status": "ok",
        "message": f"Bet slip #{slip_record['id']} saved for {today}",
        "slip": slip_record,
    }


def mark_result(date_str: str, slip_idx: int, pick_idx: Optional[int],
                result: str) -> Dict[str, Any]:
    """Mark result for a pick or entire slip.

    Args:
        date_str: Date of the bet file (YYYY-MM-DD)
        slip_idx: 1-based slip index
        pick_idx: 1-based pick index within the slip (None = mark entire slip)
        result: "win", "loss", or "void"
    """
    if result not in ("win", "loss", "void"):
        return {"status": "error", "code": "invalid_result",
                "message": f"Result must be win, loss, or void. Got: {result}"}

    bet_data = _load_bet_file(date_str)
    if not bet_data["slips"]:
        return {"status": "error", "code": "no_slips",
                "message": f"No bet slips found for {date_str}"}

    idx = slip_idx - 1
    if idx < 0 or idx >= len(bet_data["slips"]):
        return {"status": "error", "code": "invalid_index",
                "message": f"Slip index {slip_idx} out of range (1-{len(bet_data['slips'])})"}

    slip = bet_data["slips"][idx]
    stats = _load_stats()
    month_key = date_str[:7]
    if month_key not in stats["monthly"]:
        stats["monthly"][month_key] = {
            "slips": 0, "picks": 0, "wins": 0, "losses": 0,
            "staked": 0.0, "returned": 0.0,
        }

    updated_picks = []

    if pick_idx is not None:
        pidx = pick_idx - 1
        if pidx < 0 or pidx >= len(slip["picks"]):
            return {"status": "error", "code": "invalid_pick_index",
                    "message": f"Pick index {pick_idx} out of range (1-{len(slip['picks'])})"}

        old_result = slip["picks"][pidx]["result"]
        slip["picks"][pidx]["result"] = result
        updated_picks.append(pick_idx)

        if old_result == "pending":
            stats["pending"] -= 1
        elif old_result == "win":
            stats["wins"] -= 1
            stats["monthly"][month_key]["wins"] -= 1
        elif old_result == "loss":
            stats["losses"] -= 1
            stats["monthly"][month_key]["losses"] -= 1

        if result == "win":
            stats["wins"] += 1
            stats["monthly"][month_key]["wins"] += 1
        elif result == "loss":
            stats["losses"] += 1
            stats["monthly"][month_key]["losses"] += 1
        elif result == "void":
            stats["voids"] += 1
    else:
        for i, pick in enumerate(slip["picks"]):
            old_result = pick["result"]
            pick["result"] = result
            updated_picks.append(i + 1)

            if old_result == "pending":
                stats["pending"] -= 1
            elif old_result == "win":
                stats["wins"] -= 1
                stats["monthly"][month_key]["wins"] -= 1
            elif old_result == "loss":
                stats["losses"] -= 1
                stats["monthly"][month_key]["losses"] -= 1

            if result == "win":
                stats["wins"] += 1
                stats["monthly"][month_key]["wins"] += 1
            elif result == "loss":
                stats["losses"] += 1
                stats["monthly"][month_key]["losses"] += 1
            elif result == "void":
                stats["voids"] += 1

    all_results = [p["result"] for p in slip["picks"]]
    if all(r == "win" for r in all_results):
        slip["result"] = "win"
        returned = slip["stake"] * slip["total_odds"]
        slip["actual_return"] = round(returned, 2)
        slip["profit"] = round(returned - slip["stake"], 2)
        stats["total_returned"] += returned
        stats["monthly"][month_key]["returned"] += returned
    elif any(r == "loss" for r in all_results):
        slip["result"] = "loss"
        slip["actual_return"] = 0.0
        slip["profit"] = -slip["stake"]
    elif all(r == "void" for r in all_results):
        slip["result"] = "void"
        slip["actual_return"] = slip["stake"]
        slip["profit"] = 0.0
        stats["total_returned"] += slip["stake"]
        stats["monthly"][month_key]["returned"] += slip["stake"]
    elif any(r == "pending" for r in all_results):
        slip["result"] = "pending"
    else:
        slip["result"] = "partial"

    _save_bet_file(date_str, bet_data)
    _save_stats(stats)

    return {
        "status": "ok",
        "message": f"Updated slip #{slip_idx} picks {updated_picks} to '{result}'",
        "slip_result": slip["result"],
        "slip": slip,
    }


def get_stats() -> Dict[str, Any]:
    """Return cumulative statistics."""
    stats = _load_stats()
    config = _load_config()
    budget = config.get("budget", {})
    monthly_limit = budget.get("monthly_limit", 75)

    current_month = datetime.utcnow().date().isoformat()[:7]
    month_data = stats.get("monthly", {}).get(current_month, {
        "slips": 0, "picks": 0, "wins": 0, "losses": 0,
        "staked": 0.0, "returned": 0.0,
    })

    total_decided = stats["wins"] + stats["losses"]
    hitrate = (stats["wins"] / total_decided * 100) if total_decided > 0 else 0.0
    roi = ((stats["total_returned"] - stats["total_staked"]) / stats["total_staked"] * 100) \
        if stats["total_staked"] > 0 else 0.0

    month_decided = month_data.get("wins", 0) + month_data.get("losses", 0)
    month_hitrate = (month_data.get("wins", 0) / month_decided * 100) if month_decided > 0 else 0.0
    month_roi = ((month_data.get("returned", 0) - month_data.get("staked", 0)) /
                 month_data.get("staked", 0) * 100) if month_data.get("staked", 0) > 0 else 0.0

    best_month = None
    worst_month = None
    for mk, md in stats.get("monthly", {}).items():
        profit = md.get("returned", 0) - md.get("staked", 0)
        if best_month is None or profit > best_month["profit"]:
            best_month = {"month": mk, "profit": round(profit, 2)}
        if worst_month is None or profit < worst_month["profit"]:
            worst_month = {"month": mk, "profit": round(profit, 2)}

    return {
        "mode": "stats",
        "all_time": {
            "total_slips": stats["total_slips"],
            "total_picks": stats["total_picks"],
            "wins": stats["wins"],
            "losses": stats["losses"],
            "voids": stats["voids"],
            "pending": stats["pending"],
            "hitrate_pct": round(hitrate, 1),
            "total_staked": round(stats["total_staked"], 2),
            "total_returned": round(stats["total_returned"], 2),
            "profit": round(stats["total_returned"] - stats["total_staked"], 2),
            "roi_pct": round(roi, 1),
        },
        "current_month": {
            "month": current_month,
            "slips": month_data.get("slips", 0),
            "picks": month_data.get("picks", 0),
            "wins": month_data.get("wins", 0),
            "losses": month_data.get("losses", 0),
            "hitrate_pct": round(month_hitrate, 1),
            "staked": round(month_data.get("staked", 0), 2),
            "returned": round(month_data.get("returned", 0), 2),
            "profit": round(month_data.get("returned", 0) - month_data.get("staked", 0), 2),
            "roi_pct": round(month_roi, 1),
            "budget_limit": monthly_limit,
            "budget_remaining": round(monthly_limit - month_data.get("staked", 0), 2),
            "budget_used_pct": round(month_data.get("staked", 0) / monthly_limit * 100, 1)
                if monthly_limit > 0 else 0.0,
        },
        "best_month": best_month,
        "worst_month": worst_month,
    }


def get_history(days: int = 30) -> Dict[str, Any]:
    """Show bet history for the last N days."""
    _ensure_dirs()
    today = datetime.utcnow().date()
    slips_all = []

    for i in range(days):
        date = (today - timedelta(days=i)).isoformat()
        bet_data = _load_bet_file(date)
        for slip in bet_data.get("slips", []):
            slip["date"] = date
            slips_all.append(slip)

    total_staked = sum(s.get("stake", 0) for s in slips_all)
    total_returned = sum(s.get("actual_return", 0) for s in slips_all if s.get("actual_return"))
    wins = sum(1 for s in slips_all if s.get("result") == "win")
    losses = sum(1 for s in slips_all if s.get("result") == "loss")

    return {
        "mode": "history",
        "days": days,
        "total_slips": len(slips_all),
        "wins": wins,
        "losses": losses,
        "pending": sum(1 for s in slips_all if s.get("result") == "pending"),
        "total_staked": round(total_staked, 2),
        "total_returned": round(total_returned, 2),
        "profit": round(total_returned - total_staked, 2),
        "slips": slips_all,
    }


def main():
    parser = argparse.ArgumentParser(description="Track football bets")
    parser.add_argument("--mode", required=True, choices=["save", "result", "stats", "history"],
                        help="Tracking mode")
    parser.add_argument("--data", type=str, help="JSON data for save mode")
    parser.add_argument("--date", type=str, help="Date (YYYY-MM-DD) for result mode")
    parser.add_argument("--slip-idx", type=int, help="1-based slip index for result mode")
    parser.add_argument("--pick-idx", type=int, help="1-based pick index for result mode (omit for entire slip)")
    parser.add_argument("--result", type=str, choices=["win", "loss", "void"],
                        help="Result for result mode")
    parser.add_argument("--days", type=int, default=30, help="Number of days for history mode")

    args = parser.parse_args()

    if args.mode == "save":
        if not args.data:
            output = {"status": "error", "code": "missing_data",
                      "message": "--data is required for save mode"}
        else:
            output = save_bet(args.data)
    elif args.mode == "result":
        if not args.date or not args.slip_idx or not args.result:
            output = {"status": "error", "code": "missing_params",
                      "message": "--date, --slip-idx, and --result are required for result mode"}
        else:
            output = mark_result(args.date, args.slip_idx, args.pick_idx, args.result)
    elif args.mode == "stats":
        output = get_stats()
    elif args.mode == "history":
        output = get_history(args.days)
    else:
        output = {"status": "error", "code": "unknown_mode", "message": f"Unknown mode: {args.mode}"}

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
