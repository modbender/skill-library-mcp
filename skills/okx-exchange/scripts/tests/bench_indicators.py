"""Benchmark tests for CPU-intensive functions.

Run:  python tests/bench_indicators.py
"""
import sys, os, timeit, random, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "strategies"))

from strategies.trend import sma, ema, rsi, macd
from config import load_prefs, save_prefs, load_state, save_state
import tempfile, shutil


# ── Helpers ───────────────────────────────────────────────────────────────────

def _prices(n: int, seed: int = 42) -> list:
    random.seed(seed)
    price = 67000.0
    prices = []
    for _ in range(n):
        price += random.uniform(-500, 500)
        prices.append(price)
    return prices


def _bench(label: str, fn, *args, repeat: int = 5, number: int = 200) -> None:
    times = timeit.repeat(lambda: fn(*args), repeat=repeat, number=number)
    best_ms = min(times) / number * 1000
    avg_ms = (sum(times) / len(times)) / number * 1000
    print(f"  {label:<40}  best={best_ms:.4f}ms  avg={avg_ms:.4f}ms  (×{number})")


# ── Indicator Benchmarks ──────────────────────────────────────────────────────

def bench_indicators():
    print("\n── Technical Indicators ──────────────────────────────────────────")
    for n in (100, 1_000, 10_000):
        prices = _prices(n)
        print(f"\n  Dataset size: {n:,} prices")
        _bench(f"sma(n={n}, period=20)", sma, prices, 20)
        _bench(f"ema(n={n}, period=20)", ema, prices, 20)
        _bench(f"rsi(n={n}, period=14)", rsi, prices, 14)
        _bench(f"macd(n={n})", macd, prices)


# ── Config I/O Benchmarks ─────────────────────────────────────────────────────

def bench_config():
    print("\n── Config I/O ────────────────────────────────────────────────────")
    tmp = tempfile.mkdtemp()
    try:
        import config as cfg
        cfg.PREFS_PATH = os.path.join(tmp, "prefs.json")
        cfg.STATE_PATH = os.path.join(tmp, "state.json")
        cfg.JOURNAL_PATH = os.path.join(tmp, "journal.json")

        # Pre-create files
        save_prefs(load_prefs())
        save_state(load_state())

        _bench("load_prefs()", load_prefs, repeat=5, number=500)
        _bench("save_prefs()", save_prefs, load_prefs(), repeat=5, number=500)
        _bench("load_state()", load_state, repeat=5, number=500)
        _bench("save_state()", save_state, load_state(), repeat=5, number=500)
    finally:
        shutil.rmtree(tmp)


# ── OKXClient Signing Benchmark ───────────────────────────────────────────────

def bench_signing():
    print("\n── Cryptographic Signing ─────────────────────────────────────────")
    from okx_client import _sign, _timestamp

    ts = _timestamp()
    _bench("_timestamp()", _timestamp, repeat=5, number=1000)
    _bench("_sign() per request", _sign,
           ts, "GET", "/api/v5/account/balance", "", "SECRETKEY12345",
           repeat=5, number=1000)


# ── MACD Complexity Verification ──────────────────────────────────────────────

def bench_macd_scaling():
    """Verify O(n) scaling: doubling n should roughly double time."""
    print("\n── MACD O(n) Scaling Verification ───────────────────────────────")
    sizes = [500, 1000, 2000, 4000]
    times = []
    for n in sizes:
        prices = _prices(n)
        t = timeit.timeit(lambda: macd(prices), number=100)
        times.append(t / 100 * 1000)
        print(f"  n={n:5d}  avg={times[-1]:.4f}ms")

    # Check scaling ratios
    print("\n  Scaling ratios (should be ~2.0 for O(n)):")
    for i in range(1, len(times)):
        ratio = times[i] / times[i - 1]
        ok = "✅" if 1.5 <= ratio <= 3.0 else "⚠️ "
        print(f"  {sizes[i-1]}→{sizes[i]}: ratio={ratio:.2f}  {ok}")


# ── Grid Level Calculation ────────────────────────────────────────────────────

def bench_grid():
    print("\n── Grid Level Calculation ────────────────────────────────────────")
    def calc_levels(lower, upper, grids):
        step = (upper - lower) / grids
        return [lower + i * step for i in range(grids + 1)]

    _bench("grid levels (10 grids)",  calc_levels, 40000, 50000, 10, number=10000)
    _bench("grid levels (100 grids)", calc_levels, 40000, 50000, 100, number=10000)
    _bench("grid levels (500 grids)", calc_levels, 40000, 50000, 500, number=1000)


# ── WebSocket Cache Benchmarks ────────────────────────────────────────────────

def bench_ws_cache():
    print("\n── WebSocket Cache ───────────────────────────────────────────────")
    import threading
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from okx_ws_client import OKXWebSocketFeed

    feed = OKXWebSocketFeed()

    # Pre-populate: 10 instruments × 300 candles each
    inst_ids = [f"COIN{i}-USDT-SWAP" for i in range(10)]
    for inst_id in inst_ids:
        for ts in range(300):
            feed._update_candle(inst_id, "1H", [str(ts), "100", "110", "90", "105", "1000"])
        feed._update_ticker(inst_id, {"instId": inst_id, "last": "67000", "vol24h": "100"})

    print(f"\n  Cache populated: {len(inst_ids)} instruments × 300 candles")

    # Read benchmarks
    _bench("ticker cache read (1 inst)",
           feed.get_ticker, "COIN0-USDT-SWAP", number=50_000)
    _bench("candle cache read (300 rows)",
           feed.get_candles, "COIN0-USDT-SWAP", "1H", number=10_000)

    # Write benchmarks
    _bench("ticker cache write",
           feed._update_ticker, "COIN0-USDT-SWAP",
           {"instId": "COIN0-USDT-SWAP", "last": "68000"},
           number=20_000)
    _bench("candle cache write (new ts)",
           feed._update_candle, "COIN0-USDT-SWAP", "1H",
           ["9999999", "100", "110", "90", "105", "1000"],
           number=10_000)

    # Message parse benchmark
    import json as _json
    sample_msg = _json.dumps({
        "arg": {"channel": "tickers", "instId": "BTC-USDT-SWAP"},
        "data": [{"instId": "BTC-USDT-SWAP", "last": "67000", "vol24h": "100"}],
    })
    _bench("_on_message() parse + store",
           feed._on_message, None, sample_msg, number=10_000)

    # Concurrent throughput
    print("\n  Concurrent read throughput (4 threads × 5000 reads):")
    stop = threading.Event()
    counts = [0] * 4

    def reader(idx):
        while not stop.is_set():
            feed.get_ticker("COIN0-USDT-SWAP")
            counts[idx] += 1

    threads = [threading.Thread(target=reader, args=(i,)) for i in range(4)]
    for t in threads:
        t.start()
    time.sleep(0.5)
    stop.set()
    for t in threads:
        t.join()
    total = sum(counts)
    print(f"  Total reads in 0.5s: {total:,}  ({total * 2:,} reads/sec)")


# ── Private WebSocket Cache Benchmarks ───────────────────────────────────────

def bench_private_ws_cache():
    print("\n── Private WebSocket Cache ───────────────────────────────────────")
    from okx_ws_client import OKXPrivateWebSocketFeed

    feed = OKXPrivateWebSocketFeed("key", "secret", "pass", simulated=False)

    # Pre-populate caches
    ccys = [f"CCY{i}" for i in range(20)]
    for ccy in ccys:
        feed._update_account({"details": [{"ccy": ccy, "cashBal": str(1000 * (ccys.index(ccy) + 1))}]})

    inst_ids = [f"COIN{i}-USDT-SWAP" for i in range(10)]
    for inst_id in inst_ids:
        feed._update_position({"instId": inst_id, "posSide": "long", "pos": "1", "uplRatio": "0.05"})

    for i in range(50):
        feed._update_order({"ordId": str(i), "instId": "BTC-USDT-SWAP", "state": "filled"})

    print(f"\n  Cache: {len(ccys)} balances, {len(inst_ids)} positions, 50 orders")

    _bench("get_account() (20 ccys)", feed.get_account, number=50_000)
    _bench("get_positions() (10 positions)", feed.get_positions, number=50_000)
    _bench("get_orders() (50 orders)", feed.get_orders, number=20_000)

    # Write benchmarks
    _bench("_update_account() single ccy",
           feed._update_account, {"details": [{"ccy": "USDT", "cashBal": "9999"}]},
           number=20_000)
    _bench("_update_position() upsert",
           feed._update_position, {"instId": "BTC-USDT-SWAP", "posSide": "long", "pos": "2"},
           number=20_000)
    _bench("_update_order() upsert",
           feed._update_order, {"ordId": "99999", "state": "live"},
           number=20_000)


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("OKX Exchange Skill — Benchmark Report")
    print("=" * 65)

    bench_indicators()
    bench_macd_scaling()
    bench_config()
    bench_signing()
    bench_grid()
    bench_ws_cache()
    bench_private_ws_cache()

    print("\n" + "=" * 65)
    print("Done.")
