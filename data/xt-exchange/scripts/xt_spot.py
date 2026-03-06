#!/usr/bin/env python3
"""
XT.COM 现货交易 CLI
Base URL: https://sapi.xt.com (可由 XT_HOST 环境变量覆盖)
认证优先级：构造参数 > 环境变量(XT_ACCESS_KEY/XT_SECRET_KEY) > ~/.xt-exchange/credentials.json
"""
import argparse
import hashlib
import hmac
import json
import os
import sys
import time
from copy import deepcopy

import requests

# ──────────────────────────────────────────────
# 凭证加载
# ──────────────────────────────────────────────

CREDENTIALS_FILE = os.path.expanduser("~/.xt-exchange/credentials.json")


def load_credentials():
    """
    加载 API Key，优先级：环境变量 > 凭证文件
    返回 (access_key, secret_key)，未找到则返回 ("", "")
    """
    # 1. 环境变量
    ak = os.environ.get("XT_ACCESS_KEY", "")
    sk = os.environ.get("XT_SECRET_KEY", "")
    if ak and sk:
        return ak, sk

    # 2. 凭证文件
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE) as f:
                creds = json.load(f)
            ak = creds.get("access_key", "")
            sk = creds.get("secret_key", "")
            if ak and sk:
                return ak, sk
        except Exception as e:
            print(f"⚠️  读取凭证文件失败: {e}", file=sys.stderr)

    return "", ""


# ──────────────────────────────────────────────
# 核心客户端
# ──────────────────────────────────────────────

DEFAULT_HOST = "https://sapi.xt.com"


class XtSpot:
    def __init__(self, host=None, access_key=None, secret_key=None):
        self.host = host or os.environ.get("XT_HOST", DEFAULT_HOST)
        if access_key and secret_key:
            self.access_key, self.secret_key = access_key, secret_key
        else:
            self.access_key, self.secret_key = load_credentials()
        self.anonymous = not (self.access_key and self.secret_key)
        self.timeout = 10
        self.headers = {
            "Content-type": "application/json",
            "User-Agent": "xt-spot-cli/1.0",
        }

    # ── 签名 ──
    @staticmethod
    def _create_sign(url, method, sign_headers, secret_key, params=None, body=None):
        query_str = ""
        if params:
            query_str = "&".join(
                f"{k}={json.dumps(params[k]) if isinstance(params[k], (dict, list)) else params[k]}"
                for k in sorted(params)
            )
        body_str = json.dumps(body) if body else ""
        parts = [p for p in [method, url, query_str, body_str] if p]
        payload = "#" + "#".join(parts)
        header_str = "&".join(f"{k}={sign_headers[k]}" for k in sorted(sign_headers))
        sign_str = header_str + payload
        return hmac.new(
            secret_key.encode("utf-8"), sign_str.encode("utf-8"), hashlib.sha256
        ).hexdigest().upper()

    def _auth_headers(self, url, method, params=None, body=None):
        h = {
            "xt-validate-timestamp": str(int((time.time() - 30) * 1000)),
            "xt-validate-appkey": self.access_key,
            "xt-validate-recvwindow": "60000",
            "xt-validate-algorithms": "HmacSHA256",
        }
        h["xt-validate-signature"] = self._create_sign(
            url, method, h, self.secret_key, params=params, body=body
        )
        merged = deepcopy(self.headers)
        merged.update(h)
        return merged

    # ── 请求 ──
    def _req(self, url, method="GET", params=None, body=None, auth=True):
        if auth and self.anonymous:
            raise RuntimeError(
                f"需要 API Key。请创建凭证文件 {CREDENTIALS_FILE}，"
                "或设置环境变量 XT_ACCESS_KEY 和 XT_SECRET_KEY"
            )
        full_url = self.host + url
        if auth:
            headers = self._auth_headers(url, method, params=params, body=body)
        else:
            headers = self.headers

        kwargs = {"headers": headers, "timeout": self.timeout}
        if params:
            kwargs["params"] = params
        if body:
            kwargs["json"] = body

        resp = requests.request(method, full_url, **kwargs)
        resp.raise_for_status()
        res = resp.json()
        if res.get("rc", 0) != 0:
            mc = res.get("mc", "UNKNOWN")
            raise RuntimeError(f"API 错误 [{mc}]: {res}")
        return res.get("result")

    # ── 公开接口 ──
    def ticker(self, symbol):
        return self._req("/v4/public/ticker/price", params={"symbol": symbol}, auth=False)

    def ticker_24h(self, symbol):
        return self._req("/v4/public/ticker/24h", params={"symbol": symbol}, auth=False)

    def depth(self, symbol, limit=None):
        params = {"symbol": symbol}
        if limit:
            params["limit"] = limit
        return self._req("/v4/public/depth", params=params, auth=False)

    def klines(self, symbol, interval="1h", limit=24):
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        return self._req("/v4/public/kline", params=params, auth=False)

    def symbol_info(self, symbol):
        return self._req("/v4/public/symbol", params={"symbol": symbol}, auth=False)

    # ── 认证接口 ──
    def balance(self, currency=None):
        if currency:
            return self._req("/v4/balance", params={"currency": currency})
        return self._req("/v4/balances")

    def open_orders(self, symbol=None):
        params = {"bizType": "SPOT", "page": 1, "pageSize": 300}
        if symbol:
            params["symbol"] = symbol
        return self._req("/v4/open-order", params=params)

    def place_order(self, symbol, side, order_type, price=None, quantity=None, quote_qty=None):
        body = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "bizType": "SPOT",
            "timeInForce": "IOC" if order_type == "MARKET" else "GTC",
        }
        if price:
            body["price"] = str(price)
        if quantity:
            body["quantity"] = str(quantity)
        if quote_qty:
            body["quoteQty"] = str(quote_qty)
        return self._req("/v4/order", method="POST", body=body)

    def cancel_order(self, order_id):
        return self._req(f"/v4/order/{order_id}", method="DELETE")

    def cancel_all(self, symbol=None):
        body = {"bizType": "SPOT"}
        if symbol:
            body["symbol"] = symbol
        return self._req("/v4/open-order", method="DELETE", body=body)

    def history_orders(self, symbol=None, limit=20):
        params = {"bizType": "SPOT", "limit": limit}
        if symbol:
            params["symbol"] = symbol
        return self._req("/v4/history-order", params=params)

    def transfer(self, from_account, to_account, currency, amount):
        import uuid
        body = {
            "bizId": f"cli_{uuid.uuid4().hex[:16]}",
            "from": from_account,
            "to": to_account,
            "currency": currency.lower(),
            "amount": str(amount),
        }
        return self._req("/v4/balance/transfer", method="POST", body=body)

    def withdraw(self, currency, chain, amount, address):
        body = {
            "currency": currency.lower(),
            "chain": chain,
            "amount": str(amount),
            "address": address,
        }
        return self._req("/v4/withdraw", method="POST", body=body)


# ──────────────────────────────────────────────
# 输出格式化
# ──────────────────────────────────────────────

def fmt_table(rows, headers):
    """简单对齐表格输出"""
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    sep = "  "
    header_line = sep.join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    divider = sep.join("-" * w for w in col_widths)
    print(header_line)
    print(divider)
    for row in rows:
        print(sep.join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)))


def ts_to_str(ts):
    if not ts:
        return "-"
    from datetime import datetime, timezone
    return datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc).strftime("%m-%d %H:%M")


# ──────────────────────────────────────────────
# 命令处理
# ──────────────────────────────────────────────

def cmd_ticker(client, args):
    result = client.ticker(args.symbol)
    items = result if isinstance(result, list) else [result]
    fmt_table(
        [[i.get("s", ""), f"\033[1m{i.get('p', '')}\033[0m", i.get("t", "")] for i in items],
        ["Symbol", "Price", "Timestamp"],
    )


def cmd_ticker_24h(client, args):
    result = client.ticker_24h(args.symbol)
    items = result if isinstance(result, list) else [result]
    for i in items:
        print(f"交易对: {i.get('s')}")
        print(f"  最新价: \033[1m{i.get('c')}\033[0m")
        print(f"  开盘价: {i.get('o')}   最高: {i.get('h')}   最低: {i.get('l')}")
        print(f"  涨跌额: {i.get('cv')}  涨跌幅: {i.get('cr')}%")
        print(f"  成交量: {i.get('q')}   成交额: {i.get('v')}")


def cmd_depth(client, args):
    result = client.depth(args.symbol, limit=args.limit)
    bids = result.get("bids", [])[:10]
    asks = result.get("asks", [])[:10]
    print("── 卖盘 (asks) ──")
    for p, q in reversed(asks):
        print(f"  {p:>14}  {q}")
    print("── 买盘 (bids) ──")
    for p, q in bids:
        print(f"  {p:>14}  {q}")


def cmd_klines(client, args):
    result = client.klines(args.symbol, interval=args.interval, limit=args.limit)
    items = result.get("items", result) if isinstance(result, dict) else result
    fmt_table(
        [[ts_to_str(k.get("t")), k.get("o"), k.get("h"), k.get("l"), k.get("c"), k.get("q")] for k in items[-20:]],
        ["时间(UTC)", "开盘", "最高", "最低", "收盘", "成交量"],
    )


def cmd_symbol(client, args):
    result = client.symbol_info(args.symbol)
    items = result.get("symbols", result) if isinstance(result, dict) else result
    for s in (items if isinstance(items, list) else [items]):
        print(json.dumps(s, indent=2, ensure_ascii=False))


def cmd_balance(client, args):
    result = client.balance(args.currency if args.currency else None)
    # /v4/balances 返回 {totalUsdtAmount, assets: [...]}
    # /v4/balance  返回单个资产 dict 或包含在 assets 里
    if isinstance(result, dict) and "assets" in result:
        assets = result["assets"]
        total = result.get("totalUsdtAmount", "")
        rows = [(b.get("currency"), b.get("availableAmount"), b.get("frozenAmount"),
                 b.get("convertUsdtAmount", ""))
                for b in assets
                if float(b.get("availableAmount", 0) or 0) > 0
                or float(b.get("frozenAmount", 0) or 0) > 0]
        if not rows:
            print("所有余额为零")
            return
        if total:
            print(f"总资产: \033[1m{float(total):.2f} USDT\033[0m\n")
        fmt_table(rows, ["币种", "可用", "冻结", "折合USDT"])
    elif isinstance(result, list):
        rows = [(b.get("currency"), b.get("availableAmount"), b.get("frozenAmount"))
                for b in result if float(b.get("availableAmount", 0) or 0) > 0
                or float(b.get("frozenAmount", 0) or 0) > 0]
        if not rows:
            print("所有余额为零")
            return
        fmt_table(rows, ["币种", "可用", "冻结"])
    else:
        b = result or {}
        print(f"币种: {b.get('currency')}")
        print(f"  可用: \033[1m{b.get('availableAmount')}\033[0m")
        print(f"  冻结: {b.get('frozenAmount')}")


def cmd_orders(client, args):
    result = client.open_orders(symbol=args.symbol)
    items = result.get("items", result) if isinstance(result, dict) else result
    if not items:
        print("暂无挂单")
        return
    fmt_table(
        [[o.get("symbol"), o.get("side"), o.get("type"), o.get("price"), o.get("quantity"), o.get("state"), o.get("orderId")]
         for o in items],
        ["Symbol", "方向", "类型", "价格", "数量", "状态", "订单ID"],
    )


def cmd_buy(client, args):
    order_type = "MARKET" if args.market else "LIMIT"
    result = client.place_order(
        symbol=args.symbol,
        side="BUY",
        order_type=order_type,
        price=args.price,
        quantity=args.qty,
        quote_qty=args.quote_qty,
    )
    print(f"✅ 买单成功: orderId={result}")


def cmd_sell(client, args):
    order_type = "MARKET" if args.market else "LIMIT"
    result = client.place_order(
        symbol=args.symbol,
        side="SELL",
        order_type=order_type,
        price=args.price,
        quantity=args.qty,
    )
    print(f"✅ 卖单成功: orderId={result}")


def cmd_cancel(client, args):
    result = client.cancel_order(args.id)
    print(f"✅ 撤单成功: {result}")


def cmd_cancel_all(client, args):
    result = client.cancel_all(symbol=args.symbol)
    print(f"✅ 批量撤单成功: {result}")


def cmd_history(client, args):
    result = client.history_orders(symbol=args.symbol, limit=args.limit)
    items = result.get("items", result) if isinstance(result, dict) else result
    if not items:
        print("无历史订单")
        return
    # 实际字段: avgPrice=成交均价, tradeBase=成交量, origQuoteQty=下单金额, state, updatedTime
    fmt_table(
        [[o.get("symbol"), o.get("side"), o.get("type"),
          o.get("avgPrice") or o.get("price") or "-",
          o.get("tradeBase") or o.get("origQty") or "-",
          o.get("state"), ts_to_str(o.get("updatedTime"))]
         for o in items],
        ["Symbol", "方向", "类型", "成交均价", "成交量", "状态", "时间"],
    )


def cmd_transfer(client, args):
    result = client.transfer(args.from_, args.to, args.currency, args.amount)
    print(f"✅ 划转成功: transferId={result}")


def cmd_withdraw(client, args):
    result = client.withdraw(args.currency, args.chain, args.amount, args.address)
    print(f"✅ 提币申请成功: withdrawId={result}")


# ──────────────────────────────────────────────
# CLI 入口
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="XT 现货 CLI (sapi.xt.com)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # 公开接口
    p = sub.add_parser("ticker", help="最新价格")
    p.add_argument("symbol")

    p = sub.add_parser("ticker_24h", help="24h 行情")
    p.add_argument("symbol")

    p = sub.add_parser("depth", help="盘口深度")
    p.add_argument("symbol")
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("klines", help="K线数据")
    p.add_argument("symbol")
    p.add_argument("--interval", default="1h")
    p.add_argument("--limit", type=int, default=24)

    p = sub.add_parser("symbol", help="交易对信息")
    p.add_argument("symbol")

    # 认证接口
    p = sub.add_parser("balance", help="账户余额")
    p.add_argument("currency", nargs="?")

    p = sub.add_parser("orders", help="当前挂单")
    p.add_argument("--symbol")

    p = sub.add_parser("buy", help="买入")
    p.add_argument("symbol")
    p.add_argument("--price", type=float)
    p.add_argument("--qty", type=float)
    p.add_argument("--quote_qty", type=float)
    p.add_argument("--market", action="store_true")

    p = sub.add_parser("sell", help="卖出")
    p.add_argument("symbol")
    p.add_argument("--price", type=float)
    p.add_argument("--qty", type=float)
    p.add_argument("--market", action="store_true")

    p = sub.add_parser("cancel", help="撤单")
    p.add_argument("--id", required=True)

    p = sub.add_parser("cancel_all", help="全部撤单")
    p.add_argument("--symbol")

    p = sub.add_parser("history", help="历史订单")
    p.add_argument("--symbol")
    p.add_argument("--limit", type=int, default=20)

    p = sub.add_parser("transfer", help="账户划转")
    p.add_argument("--from", dest="from_", required=True)
    p.add_argument("--to", required=True)
    p.add_argument("--currency", required=True)
    p.add_argument("--amount", type=float, required=True)

    p = sub.add_parser("withdraw", help="提币")
    p.add_argument("--currency", required=True)
    p.add_argument("--chain", required=True)
    p.add_argument("--amount", type=float, required=True)
    p.add_argument("--address", required=True)

    args = parser.parse_args()
    client = XtSpot()

    handlers = {
        "ticker": cmd_ticker,
        "ticker_24h": cmd_ticker_24h,
        "depth": cmd_depth,
        "klines": cmd_klines,
        "symbol": cmd_symbol,
        "balance": cmd_balance,
        "orders": cmd_orders,
        "buy": cmd_buy,
        "sell": cmd_sell,
        "cancel": cmd_cancel,
        "cancel_all": cmd_cancel_all,
        "history": cmd_history,
        "transfer": cmd_transfer,
        "withdraw": cmd_withdraw,
    }

    try:
        handlers[args.cmd](client, args)
    except RuntimeError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except requests.HTTPError as e:
        print(f"❌ HTTP错误: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
