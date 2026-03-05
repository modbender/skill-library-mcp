#!/usr/bin/env python3
"""Exchange rates via ExchangeRate-API."""

import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.config import get_api_key
from lib.formatters import fmt_price
from lib.rate_limiter import wait_if_needed
import requests


def get_rate(base, target):
    base, target = base.upper(), target.upper()
    api_key = get_api_key("exchangeRateApiKey")
    if api_key:
        wait_if_needed("exchangerate")
        data = requests.get(f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{base}/{target}", timeout=10).json()
        return {"base": base, "target": target, "rate": data["conversion_rate"],
                "updated": data.get("time_last_update_utc", ""), "source": "ExchangeRate-API"}
    wait_if_needed("exchangerate")
    data = requests.get(f"https://open.er-api.com/v6/latest/{base}", timeout=10).json()
    return {"base": base, "target": target, "rate": data["rates"].get(target, 0),
            "updated": data.get("time_last_update_utc", ""), "source": "open.er-api.com"}


def convert(amount, base, target):
    r = get_rate(base, target)
    return {"from": base.upper(), "to": target.upper(), "amount": amount,
            "rate": r["rate"], "result": round(amount * r["rate"], 2)}


def get_multiple_rates(base, targets):
    base = base.upper()
    api_key = get_api_key("exchangeRateApiKey")
    if api_key:
        wait_if_needed("exchangerate")
        data = requests.get(f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base}", timeout=10).json()
    else:
        wait_if_needed("exchangerate")
        data = requests.get(f"https://open.er-api.com/v6/latest/{base}", timeout=10).json()
    rates = data.get("conversion_rates", data.get("rates", {}))
    return {"base": base, "rates": {t.upper(): rates.get(t.upper(), 0) for t in targets},
            "updated": data.get("time_last_update_utc", "")}


def main():
    parser = argparse.ArgumentParser(description="Foreign exchange rates")
    parser.add_argument("action", choices=["rate", "convert", "multi"])
    parser.add_argument("base", help="Base currency")
    parser.add_argument("target", nargs="?", default="TRY")
    parser.add_argument("--amount", type=float)
    parser.add_argument("--targets", nargs="+", default=["TRY", "EUR", "GBP"])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.action == "rate":
        r = get_rate(args.base, args.target)
        if args.json: print(json.dumps(r, indent=2))
        else: print(f"**{r['base']}/{r['target']}** — {r['rate']:.4f}\n1 {r['base']} = {fmt_price(r['rate'], r['target'])}")
    elif args.action == "convert":
        if not args.amount: print("Error: --amount required"); sys.exit(1)
        r = convert(args.amount, args.base, args.target)
        if args.json: print(json.dumps(r, indent=2))
        else: print(f"{fmt_price(r['amount'], r['from'])} = {fmt_price(r['result'], r['to'])}\nRate: {r['rate']:.4f}")
    elif args.action == "multi":
        r = get_multiple_rates(args.base, args.targets)
        if args.json: print(json.dumps(r, indent=2))
        else:
            print(f"**{r['base']} Exchange Rates**\n")
            for c, rate in r["rates"].items(): print(f"  {r['base']}/{c}: {rate:.4f}")


if __name__ == "__main__":
    main()
