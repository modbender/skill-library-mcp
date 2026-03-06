#!/usr/bin/env python3
"""
XT.COM 合约交易 CLI (USDT-M 永续合约)
Base URL: https://fapi.xt.com
认证优先级：构造参数 > 环境变量(XT_ACCESS_KEY/XT_SECRET_KEY) > ~/.xt-exchange/credentials.json
注意：合约 API 头部前缀为 validate-* (无 xt- 前缀)
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
    ak = os.environ.get("XT_ACCESS_KEY", "")
    sk = os.environ.get("XT_SECRET_KEY", "")
    if ak and sk:
        return ak, sk

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


DEFAULT_HOST = "https://fapi.xt.com"


# ──────────────────────────────────────────────
# 核心客户端
# ──────────────────────────────────────────────

class XtFutures:
    def __init__(self, host=None, access_key=None, secret_key=None):
        self.host = host or os.environ.get("XT_FUTURES_HOST", DEFAULT_HOST)
        if access_key and secret_key:
            self.access_key, self.secret_key = access_key, secret_key
        else:
            self.access_key, self.secret_key = load_credentials()
        self.anonymous = not (self.access_key and self.secret_key)
        self.timeout = 10

    # ── 合约签名（与现货不同）──
    # sign = HMAC-SHA256( "xt-validate-appkey={ak}&xt-validate-timestamp={ts}#{path}[#{sorted_params}]" )
    # hexdigest lowercase，POST 用 form-data 而非 JSON
    def _make_sign(self, path, params=None):
        ts = str(int(time.time() * 1000))
        msg = f"xt-validate-appkey={self.access_key}&xt-validate-timestamp={ts}"
        if params:
            param_str = "&".join(f"{k}={params[k]}" for k in sorted(params))
            msg += f"#{path}#{param_str}"
        else:
            msg += f"#{path}"
        sig = hmac.new(
            self.secret_key.encode("utf-8"), msg.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return ts, sig

    def _auth_headers(self, path, params=None):
        ts, sig = self._make_sign(path, params)
        return {
            "Content-type": "application/x-www-form-urlencoded",
            "xt-validate-appkey": self.access_key,
            "xt-validate-timestamp": ts,
            "xt-validate-signature": sig,
            "xt-validate-algorithms": "HmacSHA256",
            "xt-validate-recvwindow": "60000",
        }

    def _req(self, path, method="GET", params=None, auth=True):
        if auth and self.anonymous:
            raise RuntimeError(
                f"需要 API Key。请创建凭证文件 {CREDENTIALS_FILE}，"
                "或设置环境变量 XT_ACCESS_KEY 和 XT_SECRET_KEY"
            )
        full_url = self.host + path

        if auth:
            headers = self._auth_headers(path, params)
            if method == "GET":
                resp = requests.get(full_url, params=params, headers=headers, timeout=self.timeout)
            else:  # POST
                resp = requests.post(full_url, params=params, headers=headers, timeout=self.timeout)
        else:
            headers = {"Content-type": "application/json"}
            resp = requests.request(method, full_url, params=params, headers=headers, timeout=self.timeout)

        resp.raise_for_status()
        res = resp.json()
        rc = res.get("returnCode", res.get("rc", 0))
        if rc != 0:
            mc = res.get("msgInfo", res.get("mc", "UNKNOWN"))
            raise RuntimeError(f"API 错误 [{mc}]: {res}")
        return res.get("result", res.get("data", res))

    # ── 公开接口 ──
    def ticker(self, symbol):
        return self._req("/future/market/v1/public/q/ticker", params={"symbol": symbol}, auth=False)

    def depth(self, symbol, limit=20):
        return self._req("/future/market/v1/public/q/depth", params={"symbol": symbol, "level": limit}, auth=False)

    def funding_rate(self, symbol):
        return self._req("/future/market/v1/public/q/funding-rate", params={"symbol": symbol}, auth=False)

    def klines(self, symbol, interval="1h", limit=24):
        return self._req(
            "/future/market/v1/public/q/kline",
            params={"symbol": symbol, "interval": interval, "limit": limit},
            auth=False,
        )

    # ── 认证接口 ──
    def account(self):
        return self._req("/future/user/v1/balance/list")

    def positions(self, symbol=None):
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self._req("/future/user/v1/position/list", params=params)

    def open_orders(self, symbol=None):
        params = {"state": "UNFINISHED", "page": 1, "size": 50}
        if symbol:
            params["symbol"] = symbol
        return self._req("/future/trade/v1/order-entrust/list", params=params)

    def place_order(self, symbol, side, position_side, order_type, qty, price=None):
        """
        side: BUY / SELL  (orderSide)
        position_side: LONG / SHORT
        order_type: LIMIT / MARKET  (orderType)
        """
        # origQty 必须为整数（quantityPrecision=0），避免传 "1.0" 导致签名/参数错误
        params = {
            "symbol": symbol,
            "orderSide": side,
            "positionSide": position_side,
            "orderType": order_type,
            "origQty": int(qty),
        }
        if price and order_type == "LIMIT":
            params["price"] = str(price)
        return self._req("/future/trade/v1/order/create", method="POST", params=params)

    def cancel_order(self, order_id):
        return self._req("/future/trade/v1/order/cancel", method="POST", params={"orderId": str(order_id)})

    def history_orders(self, symbol=None, limit=20):
        params = {"page": 1, "size": limit}
        if symbol:
            params["symbol"] = symbol
        return self._req("/future/trade/v1/order/list-history", params=params)


# ──────────────────────────────────────────────
# 输出格式化
# ──────────────────────────────────────────────

def fmt_table(rows, headers):
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    sep = "  "
    print(sep.join(h.ljust(col_widths[i]) for i, h in enumerate(headers)))
    print(sep.join("-" * w for w in col_widths))
    for row in rows:
        print(sep.join(str(c).ljust(col_widths[i]) for i, c in enumerate(row)))


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
    if isinstance(result, list):
        result = result[0]
    # 实际字段: c=最新价, h=最高, l=最低, o=开盘, r=涨跌幅, a=成交量(张), v=成交额
    cr = result.get("r", result.get("cr", "-"))
    try:
        cr_pct = f"{float(cr)*100:.2f}%"
    except Exception:
        cr_pct = str(cr)
    print(f"合约: {result.get('s', args.symbol)}")
    print(f"  最新价: \033[1m{result.get('c', '')}\033[0m")
    print(f"  24h最高: {result.get('h', '-')}   最低: {result.get('l', '-')}")
    print(f"  开盘: {result.get('o', '-')}   涨跌幅: {cr_pct}")
    print(f"  成交量(张): {result.get('a', '-')}   成交额(USDT): {result.get('v', '-')}")


def cmd_depth(client, args):
    result = client.depth(args.symbol)
    if isinstance(result, dict):
        # 合约盘口字段: b=bids, a=asks（与现货不同）
        bids = (result.get("b") or result.get("bids", []))[:10]
        asks = (result.get("a") or result.get("asks", []))[:10]
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    print("── 卖盘 (asks) ──")
    for item in reversed(asks):
        p, q = (item[0], item[1]) if isinstance(item, list) else (item.get("price"), item.get("quantity"))
        print(f"  {p:>16}  {q}")
    print("── 买盘 (bids) ──")
    for item in bids:
        p, q = (item[0], item[1]) if isinstance(item, list) else (item.get("price"), item.get("quantity"))
        print(f"  {p:>16}  {q}")


def cmd_funding_rate(client, args):
    result = client.funding_rate(args.symbol)
    if isinstance(result, list):
        result = result[0]
    # 实际字段: fundingRate, nextCollectionTime, collectionInternal
    rate = result.get("fundingRate", "-")
    try:
        rate_pct = f"{float(rate)*100:.6f}%"
    except Exception:
        rate_pct = str(rate)
    print(f"合约: {result.get('symbol', args.symbol)}")
    print(f"  当前资金费率: \033[1m{rate_pct}\033[0m")
    print(f"  下次结算: {ts_to_str(result.get('nextCollectionTime'))}")
    print(f"  结算周期: 每 {result.get('collectionInternal', '-')} 小时")


def cmd_klines(client, args):
    result = client.klines(args.symbol, interval=args.interval, limit=args.limit)
    items = result if isinstance(result, list) else result.get("items", [])
    rows = []
    for k in items[-20:]:
        if isinstance(k, list):
            rows.append([ts_to_str(k[0]), k[1], k[2], k[3], k[4], k[5]])
        else:
            # 合约 kline 字段: t=时间, o=开, c=收, h=高, l=低, a=成交量(张), v=成交额
            rows.append([ts_to_str(k.get("t")), k.get("o"), k.get("h"), k.get("l"), k.get("c"), k.get("a")])
    fmt_table(rows, ["时间(UTC)", "开盘", "最高", "最低", "收盘", "成交量(张)"])


def cmd_account(client, args):
    result = client.account()
    if isinstance(result, list):
        result = result[0]
    print("合约账户权益:")
    for k, v in (result.items() if isinstance(result, dict) else {}.items()):
        print(f"  {k}: {v}")
    if not isinstance(result, dict):
        print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_positions(client, args):
    result = client.positions()
    items = result if isinstance(result, list) else result.get("items", [result] if result else [])
    # 实际字段: positionSize, entryPrice, positionSide, leverage, availableCloseSize
    open_pos = [p for p in items if float(p.get("positionSize", 0) or 0) != 0]
    if not open_pos:
        print("暂无持仓")
        return
    fmt_table(
        [[p.get("symbol"), p.get("positionSide"),
          p.get("positionSize"), p.get("availableCloseSize"),
          p.get("entryPrice"), p.get("leverage")]
         for p in open_pos],
        ["Symbol", "方向", "持仓(张)", "可平(张)", "开仓均价", "杠杆"],
    )


def cmd_orders(client, args):
    result = client.open_orders(symbol=args.symbol)
    items = result if isinstance(result, list) else result.get("items", [])
    if not items:
        print("暂无委托")
        return
    # 实际字段: orderSide, positionSide, orderType, price, origQty, state
    fmt_table(
        [[o.get("symbol"), o.get("orderSide"), o.get("positionSide"), o.get("orderType"),
          o.get("price"), o.get("origQty"), o.get("state"), o.get("orderId")]
         for o in items],
        ["Symbol", "方向", "仓位", "类型", "价格", "数量", "状态", "订单ID"],
    )


def cmd_open_long(client, args):
    order_type = "MARKET" if args.market else "LIMIT"
    result = client.place_order(
        symbol=args.symbol, side="BUY", position_side="LONG",
        order_type=order_type, qty=args.qty, price=args.price,
    )
    print(f"✅ 开多成功: orderId={result}")


def cmd_open_short(client, args):
    order_type = "MARKET" if args.market else "LIMIT"
    result = client.place_order(
        symbol=args.symbol, side="SELL", position_side="SHORT",
        order_type=order_type, qty=args.qty, price=args.price,
    )
    print(f"✅ 开空成功: orderId={result}")


def cmd_close_long(client, args):
    order_type = "MARKET" if args.market else "LIMIT"
    result = client.place_order(
        symbol=args.symbol, side="SELL", position_side="LONG",
        order_type=order_type, qty=args.qty, price=args.price,
    )
    print(f"✅ 平多成功: orderId={result}")


def cmd_cancel(client, args):
    result = client.cancel_order(args.id)
    print(f"✅ 撤单成功: {result}")


def cmd_history(client, args):
    result = client.history_orders(symbol=args.symbol, limit=args.limit)
    items = result if isinstance(result, list) else result.get("items", [])
    if not items:
        print("无历史委托")
        return
    fmt_table(
        [[o.get("symbol"), o.get("orderSide"), o.get("positionSide"), o.get("avgPrice") or o.get("price"),
          o.get("origQty"), o.get("state", o.get("status")), ts_to_str(o.get("updatedTime", o.get("updateTime")))]
         for o in items],
        ["Symbol", "方向", "仓向", "均价", "数量", "状态", "时间"],
    )


# ──────────────────────────────────────────────
# CLI 入口
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="XT 合约 CLI (fapi.xt.com, USDT-M 永续)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # 公开接口
    p = sub.add_parser("ticker", help="合约行情")
    p.add_argument("symbol")

    p = sub.add_parser("depth", help="合约盘口")
    p.add_argument("symbol")

    p = sub.add_parser("funding_rate", help="资金费率")
    p.add_argument("symbol")

    p = sub.add_parser("klines", help="K线数据")
    p.add_argument("symbol")
    p.add_argument("--interval", default="1h")
    p.add_argument("--limit", type=int, default=24)

    # 认证接口
    sub.add_parser("account", help="账户权益")

    p = sub.add_parser("positions", help="当前持仓")
    p.add_argument("--symbol")

    p = sub.add_parser("orders", help="当前委托")
    p.add_argument("--symbol")

    p = sub.add_parser("open_long", help="开多")
    p.add_argument("symbol")
    p.add_argument("--qty", type=float, required=True)
    p.add_argument("--price", type=float)
    p.add_argument("--market", action="store_true")

    p = sub.add_parser("open_short", help="开空")
    p.add_argument("symbol")
    p.add_argument("--qty", type=float, required=True)
    p.add_argument("--price", type=float)
    p.add_argument("--market", action="store_true")

    p = sub.add_parser("close_long", help="平多")
    p.add_argument("symbol")
    p.add_argument("--qty", type=float, required=True)
    p.add_argument("--price", type=float)
    p.add_argument("--market", action="store_true")

    p = sub.add_parser("cancel", help="撤销委托")
    p.add_argument("--id", required=True)

    p = sub.add_parser("history", help="历史委托")
    p.add_argument("--symbol")
    p.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()
    client = XtFutures()

    handlers = {
        "ticker": cmd_ticker,
        "depth": cmd_depth,
        "funding_rate": cmd_funding_rate,
        "klines": cmd_klines,
        "account": cmd_account,
        "positions": cmd_positions,
        "orders": cmd_orders,
        "open_long": cmd_open_long,
        "open_short": cmd_open_short,
        "close_long": cmd_close_long,
        "cancel": cmd_cancel,
        "history": cmd_history,
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
