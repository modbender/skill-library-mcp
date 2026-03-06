#!/usr/bin/env python3
"""
Trading Signal Bot — WebSocket real-time signal generator with Telegram alerts.
Connects to Bybit public WebSocket, runs strategies on candle close, pushes to TG.
"""
import asyncio
import json
import logging
import time
import requests
import websockets
from datetime import datetime
from pathlib import Path
from collections import deque
import ccxt

try:
    import config
except ImportError:
    import config_template as config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("signal_bot.log"), logging.StreamHandler()],
)
log = logging.getLogger("signals")

STATE_FILE = Path("signal_state.json")
BYBIT_WS = "wss://stream.bybit.com/v5/public/linear"

# Map symbols
WS_SYMBOLS = {s.replace("/", "").replace(":USDT", ""): s for s in config.SYMBOLS}


def send_tg(msg: str):
    if not config.TG_BOT_TOKEN:
        log.info(f"[TG disabled] {msg}")
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{config.TG_BOT_TOKEN}/sendMessage",
            json={"chat_id": config.TG_CHAT_ID, "text": msg, "parse_mode": "HTML"},
            timeout=10,
        )
    except Exception as e:
        log.error(f"TG error: {e}")


# ═══════════════════════════════════════════
# Indicators
# ═══════════════════════════════════════════

def calc_ema(closes, span):
    ema = [closes[0]]
    k = 2 / (span + 1)
    for c in closes[1:]:
        ema.append(c * k + ema[-1] * (1 - k))
    return ema

def calc_rsi(closes, period=14):
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    rsi = [50.0] * period
    gains = [max(d, 0) for d in deltas[:period]]
    losses = [max(-d, 0) for d in deltas[:period]]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    for i in range(period, len(deltas)):
        d = deltas[i]
        avg_gain = (avg_gain * (period-1) + max(d,0)) / period
        avg_loss = (avg_loss * (period-1) + max(-d,0)) / period
        rs = avg_gain / avg_loss if avg_loss else float("inf")
        rsi.append(100 - (100 / (1 + rs)))
    return rsi

def calc_macd(closes, fast=12, slow=26, signal=9):
    ef = calc_ema(closes, fast)
    es = calc_ema(closes, slow)
    ml = [f - s for f, s in zip(ef, es)]
    sl = calc_ema(ml[slow:], signal)
    sl = [0.0] * slow + sl
    hist = [m - s for m, s in zip(ml, sl)]
    return ml, sl, hist

def calc_bbands(closes, period=20, std_mult=2.0):
    sma = [None] * (period - 1)
    for i in range(period - 1, len(closes)):
        sma.append(sum(closes[i-period+1:i+1]) / period)
    upper, lower = [], []
    for i in range(len(closes)):
        if sma[i] is None:
            upper.append(None); lower.append(None)
        else:
            w = closes[i-period+1:i+1]
            std = (sum((x - sma[i])**2 for x in w) / period) ** 0.5
            upper.append(sma[i] + std_mult * std)
            lower.append(sma[i] - std_mult * std)
    return upper, sma, lower


# ═══════════════════════════════════════════
# Signal Engine
# ═══════════════════════════════════════════

class SignalEngine:
    def __init__(self):
        self.exchange = ccxt.bybit({"enableRateLimit": True, "options": {"defaultType": "swap"}})
        self.prices = {}
        self.klines = {}
        self.signals = []       # history of signals
        self.last_signal = {}   # symbol → timestamp of last signal
        self.load_state()

    def load_state(self):
        if STATE_FILE.exists():
            data = json.loads(STATE_FILE.read_text())
            self.signals = data.get("signals", [])
            self.last_signal = data.get("last_signal", {})
            log.info(f"Loaded {len(self.signals)} historical signals")

    def save_state(self):
        STATE_FILE.write_text(json.dumps({
            "signals": self.signals[-100:],  # keep last 100
            "last_signal": self.last_signal,
            "prices": dict(self.prices),
            "updated_at": datetime.now().isoformat(),
        }, indent=2))

    def init_klines(self):
        for ws_sym, ccxt_sym in WS_SYMBOLS.items():
            try:
                candles = self.exchange.fetch_ohlcv(ccxt_sym, "1h", limit=config.HISTORY_CANDLES)
                self.klines[ws_sym] = deque(maxlen=config.HISTORY_CANDLES)
                for c in candles:
                    self.klines[ws_sym].append({"t": c[0], "o": c[1], "h": c[2], "l": c[3], "c": c[4], "v": c[5]})
                log.info(f"Init {ws_sym}: {len(self.klines[ws_sym])} candles")
            except Exception as e:
                log.error(f"Failed {ws_sym}: {e}")
                self.klines[ws_sym] = deque(maxlen=config.HISTORY_CANDLES)

    def check_cooldown(self, symbol: str) -> bool:
        last = self.last_signal.get(symbol, 0)
        return time.time() - last >= config.SIGNAL_COOLDOWN

    def emit_signal(self, symbol: str, direction: str, price: float, indicator_info: str):
        if not self.check_cooldown(symbol):
            log.info(f"Signal suppressed (cooldown): {symbol} {direction}")
            return

        coin = symbol.replace("USDT", "")
        sl_pct = config.STOP_LOSS_PCT
        tp_pct = config.TAKE_PROFIT_PCT

        if direction == "long":
            sl = price * (1 - sl_pct)
            tp = price * (1 + tp_pct)
            emoji = "🟢"
        else:
            sl = price * (1 + sl_pct)
            tp = price * (1 - tp_pct)
            emoji = "🔴"

        signal = {
            "symbol": symbol, "coin": coin, "direction": direction,
            "price": price, "sl": round(sl, 2), "tp": round(tp, 2),
            "indicator": indicator_info,
            "time": datetime.now().isoformat(),
        }
        self.signals.append(signal)
        self.last_signal[symbol] = time.time()

        msg = (
            f"{emoji} <b>SIGNAL: {coin} {direction.upper()}</b>\n"
            f"Price: ${price:,.2f}\n"
            f"Stop Loss: ${sl:,.2f} ({sl_pct*100:.0f}%)\n"
            f"Take Profit: ${tp:,.2f} ({tp_pct*100:.0f}%)\n"
            f"R/R: 1:{tp_pct/sl_pct:.0f} | Leverage: {config.LEVERAGE}x\n"
            f"Indicator: {indicator_info}\n"
            f"⏰ {datetime.now().strftime('%H:%M UTC')}"
        )
        log.info(f"SIGNAL: {coin} {direction} @ {price}")
        send_tg(msg)

    def check_strategy(self, symbol: str):
        strat_config = config.STRATEGIES.get(symbol, {})
        strat_type = strat_config.get("type", "ema")

        if symbol not in self.klines or len(self.klines[symbol]) < 30:
            return

        closes = [k["c"] for k in self.klines[symbol]]
        price = closes[-1]

        if strat_type == "ema":
            fast, slow = strat_config.get("fast", 12), strat_config.get("slow", 26)
            if len(closes) < slow + 2: return
            ef = calc_ema(closes, fast)
            es = calc_ema(closes, slow)
            if ef[-2] <= es[-2] and ef[-1] > es[-1]:
                self.emit_signal(symbol, "long", price, f"EMA({fast}/{slow}) Golden Cross")
            elif ef[-2] >= es[-2] and ef[-1] < es[-1]:
                self.emit_signal(symbol, "short", price, f"EMA({fast}/{slow}) Death Cross")

        elif strat_type == "rsi":
            period = strat_config.get("period", 14)
            oversold = strat_config.get("oversold", 30)
            overbought = strat_config.get("overbought", 70)
            if len(closes) < period + 2: return
            rsi = calc_rsi(closes, period)
            if rsi[-2] < oversold and rsi[-1] >= oversold:
                self.emit_signal(symbol, "long", price, f"RSI({period}) exit oversold ({rsi[-1]:.0f})")
            elif rsi[-2] > overbought and rsi[-1] <= overbought:
                self.emit_signal(symbol, "short", price, f"RSI({period}) exit overbought ({rsi[-1]:.0f})")

        elif strat_type == "macd":
            fast = strat_config.get("fast", 12)
            slow = strat_config.get("slow", 26)
            sig = strat_config.get("signal", 9)
            if len(closes) < slow + sig + 2: return
            _, _, hist = calc_macd(closes, fast, slow, sig)
            if hist[-2] <= 0 and hist[-1] > 0:
                self.emit_signal(symbol, "long", price, f"MACD({fast}/{slow}/{sig}) bullish")
            elif hist[-2] >= 0 and hist[-1] < 0:
                self.emit_signal(symbol, "short", price, f"MACD({fast}/{slow}/{sig}) bearish")

        elif strat_type == "bbands":
            period = strat_config.get("period", 20)
            std_mult = strat_config.get("std_mult", 2.0)
            if len(closes) < period + 2: return
            upper, mid, lower = calc_bbands(closes, period, std_mult)
            if lower[-1] and closes[-1] <= lower[-1]:
                self.emit_signal(symbol, "long", price, f"BB({period},{std_mult}) touch lower")
            elif upper[-1] and closes[-1] >= upper[-1]:
                self.emit_signal(symbol, "short", price, f"BB({period},{std_mult}) touch upper")

    def update_kline(self, symbol: str, kline_data: dict):
        if symbol not in self.klines:
            self.klines[symbol] = deque(maxlen=config.HISTORY_CANDLES)
        t = kline_data["start"]
        candle = {
            "t": t, "o": float(kline_data["open"]), "h": float(kline_data["high"]),
            "l": float(kline_data["low"]), "c": float(kline_data["close"]), "v": float(kline_data["volume"]),
        }
        if self.klines[symbol] and self.klines[symbol][-1]["t"] == t:
            self.klines[symbol][-1] = candle
        else:
            self.klines[symbol].append(candle)
        if kline_data.get("confirm", False):
            log.info(f"Candle close: {symbol} @ {candle['c']}")
            self.check_strategy(symbol)

    def summary(self) -> str:
        recent = [s for s in self.signals if time.time() - datetime.fromisoformat(s["time"]).timestamp() < 86400]
        lines = [
            f"📊 <b>Signal Bot Status</b>",
            f"Monitoring: {', '.join(WS_SYMBOLS.keys())}",
            f"Signals today: {len(recent)}",
            f"Total signals: {len(self.signals)}",
        ]
        for sym in WS_SYMBOLS:
            p = self.prices.get(sym, 0)
            strat = config.STRATEGIES.get(sym, {}).get("type", "?")
            lines.append(f"  {sym}: ${p:,.2f} ({strat})")
        return "\n".join(lines)


async def run(engine: SignalEngine):
    ws_symbols = list(WS_SYMBOLS.keys())
    tf = config.KLINE_TIMEFRAME
    subscribe = {
        "op": "subscribe",
        "args": [f"tickers.{s}" for s in ws_symbols] + [f"kline.{tf}.{s}" for s in ws_symbols],
    }
    last_save = time.time()
    last_report = time.time()

    while True:
        try:
            async with websockets.connect(BYBIT_WS, ping_interval=20) as ws:
                await ws.send(json.dumps(subscribe))
                log.info(f"Connected. Symbols: {ws_symbols}, TF: {tf}")
                send_tg(f"🤖 Signal Bot started\n{engine.summary()}")

                async for raw in ws:
                    data = json.loads(raw)
                    if "op" in data:
                        continue
                    topic = data.get("topic", "")
                    msg = data.get("data", {})

                    if topic.startswith("tickers."):
                        sym = topic.split(".")[1]
                        if isinstance(msg, dict) and "lastPrice" in msg:
                            engine.prices[sym] = float(msg["lastPrice"])

                    elif topic.startswith("kline."):
                        parts = topic.split(".")
                        sym = parts[2] if len(parts) > 2 else ""
                        klines = msg if isinstance(msg, list) else [msg]
                        for kl in klines:
                            engine.update_kline(sym, kl)

                    now = time.time()
                    if now - last_save > config.STATE_SAVE_INTERVAL:
                        last_save = now
                        engine.save_state()
                    if now - last_report > config.REPORT_INTERVAL:
                        last_report = now
                        send_tg(engine.summary())

        except (websockets.ConnectionClosed, ConnectionError) as e:
            log.warning(f"Disconnected: {e}, retry 5s...")
            await asyncio.sleep(5)
        except Exception as e:
            log.error(f"Error: {e}, retry 10s...")
            await asyncio.sleep(10)


def main():
    engine = SignalEngine()
    engine.init_klines()
    log.info("Signal Bot starting...")
    asyncio.run(run(engine))


if __name__ == "__main__":
    main()
