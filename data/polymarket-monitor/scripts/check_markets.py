#!/usr/bin/env python3
"""
Fetch current Yes probabilities for Polymarket markets by conditionId.
Uses the CLOB API: https://clob.polymarket.com/markets/<conditionId>

Usage: python3 check_markets.py <conditionId1> [conditionId2 ...]
Output: JSON array of {conditionId, question, yes_prob, no_prob, url}
"""
import sys, json, urllib.request, re

CLOB_BASE = "https://clob.polymarket.com/markets/"
MARKET_URL = "https://polymarket.com/event/"
CONDITIONID_RE = re.compile(r'^[0-9a-fA-F]{64}$')

results = []
for cid in sys.argv[1:]:
    if not CONDITIONID_RE.match(cid):
        results.append({"conditionId": cid, "error": "invalid conditionId format"})
        continue
    url = CLOB_BASE + cid
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "polymarket-monitor-skill/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            m = json.loads(r.read())
        tokens = m.get("tokens", [])
        yes_price = next((t["price"] for t in tokens if t["outcome"] == "Yes"), None)
        no_price = next((t["price"] for t in tokens if t["outcome"] == "No"), None)
        results.append({
            "conditionId": cid,
            "question": m.get("question", ""),
            "yes_prob": yes_price,
            "no_prob": no_price,
            "url": MARKET_URL + m.get("market_slug", cid),
            "active": m.get("active", True),
            "closed": m.get("closed", False),
        })
    except Exception as e:
        results.append({"conditionId": cid, "error": str(e)})

print(json.dumps(results, indent=2))
