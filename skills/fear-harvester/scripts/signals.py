#!/usr/bin/env python3
"""Live Fear & Greed signal monitor for FearHarvester."""
import requests
import json
from datetime import datetime

def get_current_fear_greed() -> dict:
    resp = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5)
    data = resp.json()["data"][0]
    return {"value": int(data["value"]), "label": data["value_classification"], "timestamp": data["timestamp"]}

def get_btc_price() -> float:
    resp = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5)
    return float(resp.json()["price"])

def check_signal(fg_threshold: int = 10) -> dict:
    fg = get_current_fear_greed()
    price = get_btc_price()
    signal = "DCA_BUY" if fg["value"] <= fg_threshold else "HOLD"
    return {
        "timestamp": datetime.now().isoformat(),
        "fear_greed": fg["value"],
        "label": fg["label"],
        "btc_price": price,
        "signal": signal,
        "threshold": fg_threshold,
    }

if __name__ == "__main__":
    sig = check_signal()
    print(json.dumps(sig, indent=2))
    if sig["signal"] == "DCA_BUY":
        print(f"\n🚨 BUY SIGNAL: F&G={sig['fear_greed']} below threshold {sig['threshold']}!")
    else:
        print(f"\n✋ HOLD: F&G={sig['fear_greed']} above threshold. Waiting for fear...")
