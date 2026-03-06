#!/usr/bin/env python3
"""
Kraken OpenClaw Skill - CLI
Portfolio, market data, order history, ledger, and earn/staking.
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from decimal import Decimal

from kraken.spot import Market, User, Earn, Funding, Trade


class KrakenCLI:
    def __init__(self):
        self.market = Market()
        self.user = None
        self.earn = None
        self.funding = None
        self.trade = None

    def load_credentials(self):
        api_key = os.getenv('KRAKEN_API_KEY')
        api_secret = os.getenv('KRAKEN_API_SECRET')

        if api_key and api_secret:
            self.user = User(key=api_key, secret=api_secret)
            self.earn = Earn(key=api_key, secret=api_secret)
            self.funding = Funding(key=api_key, secret=api_secret)
            self.trade = Trade(key=api_key, secret=api_secret)
            return True
        return False

    def require_auth(self):
        if not self.load_credentials():
            print("Error: KRAKEN_API_KEY and KRAKEN_API_SECRET environment variables are required.", file=sys.stderr)
            sys.exit(1)

    def output_json(self, data, as_json=False):
        if as_json:
            print(json.dumps(data, indent=2, default=str))
            return True
        return False

    def fmt(self, amount, decimals=2):
        try:
            return f"{Decimal(str(amount)):,.{decimals}f}"
        except:
            return str(amount)

    # ── Portfolio ──

    def cmd_summary(self, args):
        self.require_auth()

        # Trade balance gives USD equity (includes flex earn)
        trade_bal = self.user.get_trade_balance(asset="USD")
        equity = float(trade_bal.get("eb", 0))

        # Get earn allocations for bonded positions
        bonded_value = 0.0
        flex_value = 0.0
        staking_rewards = 0.0
        earn_items = []

        try:
            # Get strategies to determine lock types
            strategies = self.earn.list_earn_strategies()
            lock_types = {}
            for s in strategies.get("items", []):
                lock_types[s.get("id")] = s.get("lock_type", {}).get("type", "unknown")

            allocs = self.earn.list_earn_allocations(
                converted_asset="USD",
                hide_zero_allocations="true"
            )
            staking_rewards = float(allocs.get("total_rewarded", 0))

            for item in allocs.get("items", []):
                strat_id = item.get("strategy_id", "")
                lock_type = lock_types.get(strat_id, "unknown")
                is_bonded = lock_type == "bonded"
                usd_val = float(item.get("amount_allocated", {}).get("total", {}).get("converted", 0))
                rewards = float(item.get("total_rewarded", {}).get("converted", 0))

                earn_items.append({
                    "asset": item.get("native_asset", "?"),
                    "usd_value": usd_val,
                    "rewards": rewards,
                    "lock_type": lock_type,
                    "is_bonded": is_bonded,
                })

                if is_bonded:
                    bonded_value += usd_val
                else:
                    flex_value += usd_val
        except Exception:
            pass

        total = equity + bonded_value

        if self.output_json({
            "main_equity": equity, "bonded_staking": bonded_value,
            "flex_earn": flex_value, "total": total,
            "staking_rewards": staking_rewards, "earn_items": earn_items
        }, args.json):
            return

        print("=" * 50)
        print("         KRAKEN PORTFOLIO SUMMARY")
        print("=" * 50)
        print()
        print("TOTAL NET WORTH")
        print(f"  Main Wallet (Equity):    ${self.fmt(equity)}")
        print(f"  Earn Wallet (Bonded):    ${self.fmt(bonded_value)}")
        print(f"  {'─' * 35}")
        print(f"  TOTAL:                   ${self.fmt(total)}")
        print()

        flex = [e for e in earn_items if not e["is_bonded"]]
        bonded = [e for e in earn_items if e["is_bonded"]]

        if flex:
            print("AUTO EARN (Flexible) — in Main Wallet")
            for e in sorted(flex, key=lambda x: x["usd_value"], reverse=True):
                if e["usd_value"] > 0.01:
                    print(f"  {e['asset']:6s}: ${self.fmt(e['usd_value'])}  (rewards: ${self.fmt(e['rewards'])})")
            print()

        if bonded:
            print("BONDED STAKING — in Earn Wallet")
            for e in sorted(bonded, key=lambda x: x["usd_value"], reverse=True):
                if e["usd_value"] > 0.01:
                    print(f"  {e['asset']:6s}: ${self.fmt(e['usd_value'])}  (rewards: ${self.fmt(e['rewards'])})")
            print()

        if staking_rewards > 0:
            print(f"  Total Staking Rewards:   ${self.fmt(staking_rewards)}")

    def cmd_net_worth(self, args):
        self.require_auth()

        trade_bal = self.user.get_trade_balance(asset="USD")
        equity = float(trade_bal.get("eb", 0))

        bonded = 0.0
        try:
            strategies = self.earn.list_earn_strategies()
            lock_types = {s["id"]: s.get("lock_type", {}).get("type", "unknown") for s in strategies.get("items", [])}
            allocs = self.earn.list_earn_allocations(converted_asset="USD", hide_zero_allocations="true")
            for item in allocs.get("items", []):
                if lock_types.get(item.get("strategy_id"), "") == "bonded":
                    bonded += float(item.get("amount_allocated", {}).get("total", {}).get("converted", 0))
        except:
            pass

        total = equity + bonded
        if self.output_json({"net_worth": total, "equity": equity, "bonded": bonded}, args.json):
            return
        print(f"${self.fmt(total)}")

    def cmd_holdings(self, args):
        self.require_auth()
        balances = self.user.get_account_balance()

        if self.output_json(balances, args.json):
            return

        print("=" * 50)
        print("HOLDINGS")
        print("=" * 50)
        for asset, amount in sorted(balances.items(), key=lambda x: float(x[1]), reverse=True):
            if float(amount) > 0:
                print(f"  {asset:12s} {self.fmt(amount, 8)}")

    def cmd_balance(self, args):
        self.require_auth()
        balances = self.user.get_account_balance()

        if self.output_json(balances, args.json):
            return
        for asset, amount in sorted(balances.items()):
            if float(amount) > 0:
                print(f"{asset}: {amount}")

    # ── Market Data ──

    def cmd_ticker(self, args):
        data = self.market.get_ticker(pair=args.pair)

        if self.output_json(data, args.json):
            return

        if not data:
            print(f"No data for pair: {args.pair}")
            return

        pair_key = list(data.keys())[0]
        t = data[pair_key]
        print(f"{'─' * 40}")
        print(f" {args.pair}")
        print(f"{'─' * 40}")
        print(f"  Last:    {t.get('c', ['?'])[0]}")
        print(f"  High:    {t.get('h', ['?', '?'])[1]}")
        print(f"  Low:     {t.get('l', ['?', '?'])[1]}")
        print(f"  Volume:  {t.get('v', ['?', '?'])[1]}")
        print(f"  VWAP:    {t.get('p', ['?', '?'])[1]}")

    def cmd_pairs(self, args):
        data = self.market.get_asset_pairs()
        if self.output_json(data, args.json):
            return
        print(f"Trading pairs: {len(data)}\n")
        for pair in sorted(data.keys())[:50]:
            info = data[pair]
            print(f"  {pair:20s} {info.get('base','')}/{info.get('quote','')}")
        if len(data) > 50:
            print(f"\n  ... {len(data) - 50} more (use --json for all)")

    def cmd_assets(self, args):
        data = self.market.get_assets()
        if self.output_json(data, args.json):
            return
        print(f"Assets: {len(data)}\n")
        for asset in sorted(data.keys())[:50]:
            info = data[asset]
            print(f"  {asset:12s} {info.get('altname', '')}")
        if len(data) > 50:
            print(f"\n  ... {len(data) - 50} more (use --json for all)")

    # ── Order History ──

    def cmd_open_orders(self, args):
        self.require_auth()
        data = self.user.get_open_orders()

        if self.output_json(data, args.json):
            return

        orders = data.get("open", {})
        print(f"Open Orders: {len(orders)}")
        if not orders:
            return

        for oid, o in orders.items():
            d = o.get("descr", {})
            ts = datetime.fromtimestamp(o.get("opentm", 0)).strftime("%Y-%m-%d %H:%M")
            side = d.get("type", "").upper()
            print(f"\n  [{side:4s}] {ts}  {d.get('pair','')}  {o.get('vol','')} @ {d.get('price','market')}  ({o.get('status','')})")

    def cmd_closed_orders(self, args):
        self.require_auth()
        data = self.user.get_closed_orders()

        if self.output_json(data, args.json):
            return

        orders = data.get("closed", {})
        limit = args.limit or 20
        print(f"Closed Orders (showing {min(limit, len(orders))} of {len(orders)})")

        for oid, o in list(orders.items())[:limit]:
            d = o.get("descr", {})
            ts = datetime.fromtimestamp(o.get("closetm", 0)).strftime("%Y-%m-%d %H:%M")
            side = d.get("type", "").upper()
            print(f"  [{side:4s}] {ts}  {d.get('pair','')}  {o.get('vol','')} @ {d.get('price','')}  [{o.get('status','')}]")

    def cmd_trades(self, args):
        self.require_auth()
        data = self.user.get_trades_history()
        trades = data.get("trades", {})
        limit = args.limit or 20

        if self.output_json(data, args.json):
            return

        if getattr(args, 'csv', False):
            writer = csv.writer(sys.stdout)
            writer.writerow(["trade_id", "time", "pair", "type", "ordertype", "price", "cost", "fee", "vol", "margin"])
            for tid, t in list(trades.items())[:limit]:
                writer.writerow([tid, t.get("time",""), t.get("pair",""), t.get("type",""),
                    t.get("ordertype",""), t.get("price",""), t.get("cost",""),
                    t.get("fee",""), t.get("vol",""), t.get("margin","")])
            return
        print(f"Trade History (showing {min(limit, len(trades))} of {len(trades)})")

        for tid, t in list(trades.items())[:limit]:
            ts = datetime.fromtimestamp(t.get("time", 0)).strftime("%Y-%m-%d %H:%M")
            side = t.get("type", "").upper()
            print(f"  [{side:4s}] {ts}  {t.get('pair','')}  {t.get('vol','')} @ {t.get('price','')}  cost={t.get('cost','')} fee={t.get('fee','')}")

    # ── Ledger ──

    def cmd_ledger(self, args):
        self.require_auth()

        params = {}
        if args.start:
            try:
                params["start"] = int(datetime.strptime(args.start, "%Y-%m-%d").timestamp())
            except ValueError:
                print("Error: --start must be YYYY-MM-DD", file=sys.stderr)
                sys.exit(1)
        if args.end:
            try:
                params["end"] = int(datetime.strptime(args.end, "%Y-%m-%d").timestamp())
            except ValueError:
                print("Error: --end must be YYYY-MM-DD", file=sys.stderr)
                sys.exit(1)
        if args.asset:
            params["asset"] = args.asset
        if args.type:
            params["type_"] = args.type

        # Paginate
        all_items = {}
        limit = args.limit or 999999
        offset = 0

        while len(all_items) < limit:
            params["ofs"] = offset
            result = self.user.get_ledgers_info(**params)
            batch = result.get("ledger", {})
            if not batch:
                break
            all_items.update(batch)
            if len(batch) < 50:
                break
            offset += 50

        # Trim
        items = dict(list(all_items.items())[:limit])

        # Sort by time
        items = dict(sorted(items.items(), key=lambda x: x[1].get("time", 0)))

        # CSV output
        if args.csv:
            writer = csv.writer(sys.stdout)
            writer.writerow(["refid", "time", "type", "subtype", "aclass", "asset", "amount", "fee", "balance"])
            for rid, e in items.items():
                writer.writerow([
                    rid, e.get("time", ""), e.get("type", ""), e.get("subtype", ""),
                    e.get("aclass", ""), e.get("asset", ""), e.get("amount", ""),
                    e.get("fee", ""), e.get("balance", "")
                ])
            return

        if self.output_json({"count": len(items), "ledger": items}, args.json):
            return

        print(f"Ledger: {len(items)} entries")
        print("─" * 80)
        for rid, e in items.items():
            ts = datetime.fromtimestamp(e.get("time", 0)).strftime("%Y-%m-%d %H:%M")
            print(f"  {ts}  {e.get('type',''):12s} {e.get('asset',''):8s} {e.get('amount',''):>14s}  fee={e.get('fee','')}  bal={e.get('balance','')}")

        if len(all_items) > limit:
            print(f"\n  (limited to {limit}, {len(all_items)} total available)")

    # ── Earn/Staking ──

    def cmd_earn_positions(self, args):
        self.require_auth()
        data = self.earn.list_earn_allocations(converted_asset="USD", hide_zero_allocations="true")

        if self.output_json(data, args.json):
            return

        items = data.get("items", [])
        print(f"Earn Positions: {len(items)}")
        print("─" * 50)
        for item in items:
            amt = item.get("amount_allocated", {}).get("total", {})
            rewards = item.get("total_rewarded", {})
            print(f"\n  {item.get('native_asset', '?')}")
            print(f"    Amount:  {amt.get('native', 0)} (${self.fmt(float(amt.get('converted', 0)))})")
            print(f"    Rewards: ${self.fmt(float(rewards.get('converted', 0)))}")

    def cmd_earn_strategies(self, args):
        self.require_auth()
        data = self.earn.list_earn_strategies()

        if self.output_json(data, args.json):
            return

        items = data.get("items", [])
        print(f"Earn Strategies: {len(items)}")
        print("─" * 50)
        for s in items:
            lock = s.get("lock_type", {}).get("type", "?")
            apr = s.get("apr_estimate", {}).get("current", "?")
            print(f"  {s.get('asset','?'):8s} {lock:8s} APR: {apr}%  [{s.get('id','')}]")

    def cmd_earn_status(self, args):
        self.require_auth()
        data = self.earn.list_earn_allocations(hide_zero_allocations="true")

        if self.output_json(data, args.json):
            return

        items = data.get("items", [])
        pending = []
        for item in items:
            amt = item.get("amount_allocated", {}).get("total", {})
            p_alloc = float(amt.get("allocating", 0))
            p_dealloc = float(amt.get("deallocating", 0))
            if p_alloc > 0 or p_dealloc > 0:
                pending.append({"asset": item.get("native_asset"), "allocating": p_alloc, "deallocating": p_dealloc})

        print(f"Pending Earn Requests: {len(pending)}")
        if not pending:
            print("  None")
            return
        for p in pending:
            print(f"  {p['asset']}: allocating={p['allocating']} deallocating={p['deallocating']}")

    def _require_confirm(self, action):
        """Exit with error if --confirm not set."""
        print(f"Error: --confirm flag is required for {action}", file=sys.stderr)
        sys.exit(1)

    def _earn_action(self, args, action):
        """Shared handler for allocate/deallocate with confirmation."""
        if not args.confirm:
            self._require_confirm(f"earn-{action}")

        fn = self.earn.allocate_earn_funds if action == "allocate" else self.earn.deallocate_earn_funds
        try:
            result = fn(strategy_id=args.strategy_id, amount=str(args.amount))
            if self.output_json(result, args.json):
                return
            print(f"✓ Earn {action} successful")
            print(f"  Strategy: {args.strategy_id}  Amount: {args.amount}")
            if isinstance(result, dict) and result.get("pending"):
                print("  Status: Pending")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    def cmd_earn_allocate(self, args):
        self.require_auth()
        self._earn_action(args, "allocate")

    def cmd_earn_deallocate(self, args):
        self.require_auth()
        self._earn_action(args, "deallocate")

    # ── Funding ──

    def cmd_deposit_methods(self, args):
        self.require_auth()
        try:
            data = self.funding.get_deposit_methods(asset=args.asset)
            if self.output_json(data, args.json):
                return
            print(f"Deposit Methods: {args.asset}")
            if not data:
                print("  None available")
                return
            for m in data:
                print(f"  {m.get('method', '?')}" + (f" (limit: {m['limit']})" if m.get('limit') else ''))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    def cmd_deposit_address(self, args):
        self.require_auth()
        try:
            methods = self.funding.get_deposit_methods(asset=args.asset)
            if not methods:
                print(f"Error: No deposit methods for {args.asset}", file=sys.stderr)
                sys.exit(1)

            # Pick method: use --method if provided, otherwise first available
            if args.method:
                match = [m for m in methods if args.method.lower() in m.get('method', '').lower()]
                if not match:
                    print(f"Error: No method matching '{args.method}' for {args.asset}", file=sys.stderr)
                    print(f"Available methods:", file=sys.stderr)
                    for m in methods:
                        print(f"  {m.get('method')}", file=sys.stderr)
                    sys.exit(1)
                method_name = match[0].get('method')
            else:
                method_name = methods[0].get('method')

            data = self.funding.get_deposit_address(asset=args.asset, method=method_name)
            if self.output_json(data, args.json):
                return

            addr = data[0] if isinstance(data, list) and data else data
            print(f"Deposit Address: {args.asset} ({method_name})")
            print(f"  Address: {addr.get('address', '?')}")
            if addr.get('tag'):
                print(f"  Tag:     {addr.get('tag')}")
            exp = int(addr.get('expiretm', 0))
            if exp > 0:
                print(f"  Expires: {datetime.fromtimestamp(exp).strftime('%Y-%m-%d %H:%M')}")
            else:
                print(f"  Expires: Never")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    def cmd_withdraw(self, args):
        self.require_auth()
        if not args.confirm:
            self._require_confirm("withdraw")
        try:
            result = self.funding.withdraw_funds(asset=args.asset, key=args.key, amount=str(args.amount))
            if self.output_json(result, args.json):
                return
            print(f"✓ Withdrawal initiated")
            print(f"  {args.amount} {args.asset} → {args.key}")
            if result.get('refid'):
                print(f"  Ref: {result['refid']}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    def cmd_withdraw_status(self, args):
        self.require_auth()
        try:
            data = self.funding.get_recent_withdraw_status()
            if self.output_json(data, args.json):
                return
            if not data:
                print("No recent withdrawals")
                return
            print("Recent Withdrawals:")
            for w in data:
                ts = datetime.fromtimestamp(w.get("time", 0)).strftime("%Y-%m-%d %H:%M")
                print(f"  {ts} | {w.get('asset', '?')} {w.get('amount', '?')} | {w.get('status', '?')} | ref: {w.get('refid', '?')}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # ── Trading ──

    def _place_order(self, args, side):
        self.require_auth()

        if not args.confirm:
            print("Error: --confirm flag is required for all trading commands", file=sys.stderr)
            sys.exit(1)

        # Check minimum order size before attempting
        try:
            pair_info = self.market.get_asset_pairs(pair=args.pair)
            if pair_info:
                info = list(pair_info.values())[0]
                ordermin = float(info.get("ordermin", 0))
                costmin = float(info.get("costmin", 0))
                if ordermin and args.amount < ordermin:
                    print(f"Error: Amount {args.amount} is below minimum order size of {ordermin} for {args.pair}", file=sys.stderr)
                    sys.exit(1)
        except Exception:
            pass  # Non-critical, let the API catch it if we can't pre-check

        params = {
            "ordertype": args.type, "side": side,
            "pair": args.pair, "volume": str(args.amount),
            "validate": args.validate
        }

        if args.type == "limit":
            if not args.price:
                print("Error: --price is required for limit orders", file=sys.stderr)
                sys.exit(1)
            params["price"] = str(args.price)

        try:
            result = self.trade.create_order(**params)
            if self.output_json(result, args.json):
                return

            label = side.upper()
            details = f"  Side:      {label}\n  Type:      {args.type.upper()}\n  Pair:      {args.pair}\n  Amount:    {args.amount}"
            if args.type == "limit":
                details += f"\n  Price:     {args.price}"

            if args.validate:
                print(f"✓ Order validation successful (dry run)\n\nOrder Details:\n{details}\n\nStatus:    VALIDATED (not placed)")
            else:
                txids = result.get("txid", [])
                print(f"✓ {label} order placed successfully\n\nOrder ID(s): {', '.join(txids)}\n{details}")
        except Exception as e:
            print(f"Error placing order: {e}", file=sys.stderr)
            sys.exit(1)

    def cmd_buy(self, args):
        self._place_order(args, "buy")

    def cmd_sell(self, args):
        self._place_order(args, "sell")

    def cmd_cancel_order(self, args):
        self.require_auth()
        
        if not args.confirm:
            print("Error: --confirm flag is required for all trading commands", file=sys.stderr)
            sys.exit(1)

        try:
            result = self.trade.cancel_order(txid=args.id)
            
            if self.output_json(result, args.json):
                return
                
            print(f"✓ Order cancelled successfully")
            print(f"  Order ID: {args.id}")
            count = result.get("count", 0)
            if count:
                print(f"  Cancelled: {count} order(s)")
        except Exception as e:
            print(f"Error cancelling order: {e}", file=sys.stderr)
            sys.exit(1)

    def cmd_cancel_all(self, args):
        self.require_auth()
        
        if not args.confirm:
            print("Error: --confirm flag is required for all trading commands", file=sys.stderr)
            sys.exit(1)

        try:
            result = self.trade.cancel_all_orders()
            
            if self.output_json(result, args.json):
                return
                
            count = result.get("count", 0)
            print(f"✓ All orders cancelled successfully")
            print(f"  Total cancelled: {count} order(s)")
        except Exception as e:
            print(f"Error cancelling all orders: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Kraken CLI")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    sub = parser.add_subparsers(dest="command")

    # Portfolio
    sub.add_parser("summary")
    sub.add_parser("net-worth")
    sub.add_parser("holdings")
    sub.add_parser("balance")

    # Market
    t = sub.add_parser("ticker")
    t.add_argument("--pair", required=True)
    sub.add_parser("pairs")
    sub.add_parser("assets")

    # Orders
    sub.add_parser("open-orders")
    co = sub.add_parser("closed-orders")
    co.add_argument("--limit", type=int)
    tr = sub.add_parser("trades")
    tr.add_argument("--limit", type=int)
    tr.add_argument("--csv", action="store_true", help="Output as CSV")

    # Ledger
    lg = sub.add_parser("ledger")
    lg.add_argument("--start")
    lg.add_argument("--end")
    lg.add_argument("--asset")
    lg.add_argument("--type")
    lg.add_argument("--csv", action="store_true")
    lg.add_argument("--limit", type=int)

    # Earn
    sub.add_parser("earn-positions")
    sub.add_parser("earn-strategies")
    sub.add_parser("earn-status")

    earn_alloc = sub.add_parser("earn-allocate")
    earn_alloc.add_argument("--strategy-id", required=True, help="Earn strategy ID")
    earn_alloc.add_argument("--amount", required=True, type=float, help="Amount to allocate")
    earn_alloc.add_argument("--confirm", action="store_true", help="Required to confirm allocation")

    earn_dealloc = sub.add_parser("earn-deallocate")
    earn_dealloc.add_argument("--strategy-id", required=True, help="Earn strategy ID")
    earn_dealloc.add_argument("--amount", required=True, type=float, help="Amount to deallocate")
    earn_dealloc.add_argument("--confirm", action="store_true", help="Required to confirm deallocation")

    # Funding
    dep_methods = sub.add_parser("deposit-methods")
    dep_methods.add_argument("--asset", required=True, help="Asset symbol (e.g., BTC)")

    dep_addr = sub.add_parser("deposit-address")
    dep_addr.add_argument("--asset", required=True, help="Asset symbol (e.g., BTC)")
    dep_addr.add_argument("--method", help="Network/method filter (e.g., SPL, Solana, Ethereum)")

    withdraw = sub.add_parser("withdraw")
    withdraw.add_argument("--asset", required=True, help="Asset symbol (e.g., BTC)")
    withdraw.add_argument("--key", required=True, help="Withdrawal address key name")
    withdraw.add_argument("--amount", required=True, type=float, help="Amount to withdraw")
    withdraw.add_argument("--confirm", action="store_true", help="Required to confirm withdrawal")

    sub.add_parser("withdraw-status")

    # Trading
    buy = sub.add_parser("buy")
    buy.add_argument("--pair", required=True, help="Trading pair (e.g., XBTUSD)")
    buy.add_argument("--type", required=True, choices=["market", "limit"], help="Order type")
    buy.add_argument("--amount", required=True, type=float, help="Amount to buy")
    buy.add_argument("--price", type=float, help="Price for limit orders")
    buy.add_argument("--validate", action="store_true", help="Dry run (validate only)")
    buy.add_argument("--confirm", action="store_true", help="Required to place order")

    sell = sub.add_parser("sell")
    sell.add_argument("--pair", required=True, help="Trading pair (e.g., XBTUSD)")
    sell.add_argument("--type", required=True, choices=["market", "limit"], help="Order type")
    sell.add_argument("--amount", required=True, type=float, help="Amount to sell")
    sell.add_argument("--price", type=float, help="Price for limit orders")
    sell.add_argument("--validate", action="store_true", help="Dry run (validate only)")
    sell.add_argument("--confirm", action="store_true", help="Required to place order")

    cancel = sub.add_parser("cancel-order")
    cancel.add_argument("--id", required=True, help="Order ID to cancel")
    cancel.add_argument("--confirm", action="store_true", help="Required to cancel order")

    cancel_all = sub.add_parser("cancel-all")
    cancel_all.add_argument("--confirm", action="store_true", help="Required to cancel all orders")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cli = KrakenCLI()
    commands = {
        "summary": cli.cmd_summary, "net-worth": cli.cmd_net_worth,
        "holdings": cli.cmd_holdings, "balance": cli.cmd_balance,
        "ticker": cli.cmd_ticker, "pairs": cli.cmd_pairs, "assets": cli.cmd_assets,
        "open-orders": cli.cmd_open_orders, "closed-orders": cli.cmd_closed_orders,
        "trades": cli.cmd_trades, "ledger": cli.cmd_ledger,
        "earn-positions": cli.cmd_earn_positions, "earn-strategies": cli.cmd_earn_strategies,
        "earn-status": cli.cmd_earn_status, "earn-allocate": cli.cmd_earn_allocate,
        "earn-deallocate": cli.cmd_earn_deallocate,
        "deposit-methods": cli.cmd_deposit_methods, "deposit-address": cli.cmd_deposit_address,
        "withdraw": cli.cmd_withdraw, "withdraw-status": cli.cmd_withdraw_status,
        "buy": cli.cmd_buy, "sell": cli.cmd_sell,
        "cancel-order": cli.cmd_cancel_order, "cancel-all": cli.cmd_cancel_all,
    }

    handler = commands.get(args.command)
    if handler:
        try:
            handler(args)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
