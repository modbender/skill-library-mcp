"""First-time setup: check dependencies and validate API keys."""
import os
import sys
import subprocess


def check_deps():
    required = ["requests", "websocket-client"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"Installing: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing, stdout=subprocess.DEVNULL)
        print("Done.")


def check_env():
    required = ["OKX_API_KEY", "OKX_SECRET_KEY", "OKX_PASSPHRASE"]
    env_file = os.path.expanduser("~/.openclaw/workspace/.env")

    # Load .env if exists
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing)}")
        print(f"\nAdd to {env_file}:")
        for k in missing:
            print(f"  {k}=your_value_here")
        print("\nGet API keys from: https://www.okx.com/account/my-api")
        return False
    return True


def validate_api():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from okx_client import OKXClient
    client = OKXClient()

    print("\nValidating API connection...")
    result = client.account_config()
    if result.get("code") == "0":
        data = result["data"][0]
        print(f"  ✅ Connected as UID: {data.get('uid')}")
        print(f"  Account type: {data.get('acctLv','?')} | Mode: {data.get('posMode','?')}")
        simulated = os.getenv("OKX_SIMULATED", "0") == "1"
        print(f"  {'⚠️  SIMULATED trading mode' if simulated else '🔴 LIVE trading mode'}")
        return True
    else:
        print(f"  ❌ API error: {result.get('msg')}")
        return False


def create_default_prefs():
    from config import PREFS_PATH, DEFAULT_PREFS, save_prefs
    if not os.path.exists(PREFS_PATH):
        save_prefs(DEFAULT_PREFS)
        print(f"\n  ✅ Created default preferences: {PREFS_PATH}")


if __name__ == "__main__":
    print("OKX Exchange Skill — Setup")
    print("=" * 40)

    check_deps()

    if not check_env():
        sys.exit(1)

    if not validate_api():
        sys.exit(1)

    create_default_prefs()

    print("\n✅ Setup complete. Ready to trade.")
    print("\nQuick start (all via unified CLI):")
    print("  python3 okx.py account                          # Portfolio overview")
    print("  python3 okx.py trend analyze BTC-USDT-SWAP      # Trend signal")
    print("  python3 okx.py arb scan                          # Arbitrage scan")
    print("  python3 okx.py grid setup BTC-USDT 40000 50000 10 1000")
    print("  python3 okx.py prefs show                        # View all settings")
    print("\nTip: python3 okx.py help   — see all commands")
    print("To enable auto-trading:  python3 okx.py prefs set auto_trade true")
    print("To use simulated mode:   OKX_SIMULATED=1 python3 okx.py monitor")
