"""
Mootdx Setup & Verification Script

Usage:
    python setup_and_verify.py              # Install + verify + connectivity test
    python setup_and_verify.py --check      # Verify only (no install)
    python setup_and_verify.py --demo       # Run a full API demo after verification
"""

import subprocess
import sys
import argparse


# ── Install ──────────────────────────────────────────────────────────────────

def install():
    """Install mootdx via pip."""
    print("Installing mootdx...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mootdx"])
    print()


# ── Verify ───────────────────────────────────────────────────────────────────

def verify() -> bool:
    """Check that all required packages are importable."""
    ok = True
    for pkg, label in [("mootdx", "mootdx"), ("tdxpy", "tdxpy (internal dep)"), ("pandas", "pandas")]:
        try:
            mod = __import__(pkg)
            ver = getattr(mod, "__version__", "OK")
            print(f"  [OK] {label} — {ver}")
        except ImportError:
            print(f"  [FAIL] {label} — not installed")
            ok = False
    return ok


# ── Time-frame Patch ─────────────────────────────────────────────────────────

def apply_time_frame_patch():
    """
    Bypass tdxpy's trading-hour check.
    Without this, transaction() / transactions() silently return empty
    results when the server timezone != Asia/Shanghai.
    """
    import tdxpy.hq
    tdxpy.hq.time_frame = lambda: True
    print("  [OK] time_frame patch applied (trading-hour bypass)")


# ── Connectivity Test ────────────────────────────────────────────────────────

def test_connectivity() -> bool:
    """Quick TDX server connection test using daily bars."""
    from mootdx.quotes import Quotes

    print("\nTesting TDX server connectivity...")
    try:
        client = Quotes.factory(market='std')
        df = client.bars(symbol='000001', frequency=9, start=0, offset=1)
        if not df.empty:
            row = df.iloc[0]
            print(f"  [OK] Received data — 000001 (Ping An Bank)")
            print(f"       datetime={row.get('datetime')}, close={row.get('close')}")
            return True
        else:
            print("  [WARN] Connected but received empty data (may be outside trading hours)")
            return True  # connection itself worked
    except Exception as e:
        print(f"  [FAIL] Connection failed: {e}")
        return False


# ── Full API Demo ────────────────────────────────────────────────────────────

def run_demo():
    """
    Demonstrate all major mootdx APIs.
    This is the most useful part for a model — it shows correct calling
    patterns with real output, so the model can copy/adapt them.
    """
    from mootdx.quotes import Quotes
    import tdxpy.hq

    # Always apply patch first
    tdxpy.hq.time_frame = lambda: True

    client = Quotes.factory(market='std')
    symbol = '000001'  # Ping An Bank

    print("\n" + "=" * 60)
    print("MOOTDX API DEMO — All raw APIs return pandas DataFrames")
    print("=" * 60)

    # 1. Daily bars
    print("\n── 1. Daily K-line bars (frequency=9, last 5 days) ──")
    df = client.bars(symbol=symbol, frequency=9, start=0, offset=5)
    print(df.to_string(index=False))

    # 2. 1-minute bars
    print("\n── 2. 1-Minute K-line bars (frequency=7, last 10 bars) ──")
    df = client.bars(symbol=symbol, frequency=7, start=0, offset=10)
    print(df.to_string(index=False))

    # 3. Real-time quote (single)
    print("\n── 3. Real-time quote (single stock) ──")
    df = client.quotes(symbol=symbol)
    if not df.empty:
        cols = ['code', 'price', 'open', 'high', 'low', 'vol', 'bid1', 'ask1']
        available_cols = [c for c in cols if c in df.columns]
        print(df[available_cols].to_string(index=False))
    else:
        print("  (empty — market may be closed)")

    # 4. Real-time quotes (batch)
    print("\n── 4. Real-time quotes (batch — native multi-symbol) ──")
    df = client.quotes(symbol=['000001', '600519', '300750'])
    if not df.empty:
        cols = ['code', 'price', 'open', 'high', 'low', 'vol']
        available_cols = [c for c in cols if c in df.columns]
        print(df[available_cols].to_string(index=False))
    else:
        print("  (empty — market may be closed)")

    # 5. Real-time tick transactions
    print("\n── 5. Real-time tick transactions (last 10) ──")
    df = client.transaction(symbol=symbol, start=0, offset=10)
    if df is not None and not df.empty:
        print(df.to_string(index=False))
    else:
        print("  (empty — market may be closed)")

    # 6. Historical tick transactions
    print("\n── 6. Historical tick transactions ──")
    # Use a recent trading day
    from datetime import datetime, timedelta
    # Try last 5 weekdays to find a trading day
    for i in range(1, 6):
        d = datetime.now() - timedelta(days=i)
        if d.weekday() < 5:  # skip weekends
            date_str = d.strftime('%Y%m%d')
            df = client.transactions(symbol=symbol, start=0, offset=10, date=date_str)
            if df is not None and not df.empty:
                print(f"  Date: {date_str}")
                print(df.to_string(index=False))
                break
    else:
        print("  (no recent trading day data found)")

    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Mootdx setup & verification")
    parser.add_argument("--check", action="store_true", help="Verify only, skip install")
    parser.add_argument("--demo", action="store_true", help="Run full API demo after verification")
    args = parser.parse_args()

    if not args.check:
        install()

    print("Verifying packages...")
    if not verify():
        print("\nSome packages are missing. Run without --check to install.")
        sys.exit(1)

    apply_time_frame_patch()

    if not test_connectivity():
        print("\nConnectivity test failed. Check network or TDX server status.")
        sys.exit(1)

    if args.demo:
        run_demo()

    print("\nAll good. mootdx is ready to use.")


if __name__ == "__main__":
    main()
