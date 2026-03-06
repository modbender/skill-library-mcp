"""
ConvoYield CLI — Command-line interface for the entire ecosystem.

Usage:
    python -m convoyield demo              Run the interactive demo
    python -m convoyield server            Start the Cloud API server
    python -m convoyield interactive       Interactive conversation + mining
    python -m convoyield analyze <file>    Analyze a conversation log file
    python -m convoyield register          Register for a Cloud API key
    python -m convoyield playbooks         List available premium playbooks
    python -m convoyield status            Check system status
    python -m convoyield coin wallet       Create/show ConvoCoin wallet
    python -m convoyield coin mine         Interactive mining mode
    python -m convoyield coin balance      Check CVC balance
    python -m convoyield coin status       Full ConvoCoin status
    python -m convoyield coin marketplace  Browse CVC marketplace
    python -m convoyield coin tokenomics   View tokenomics
    python -m convoyield coin chain        View blockchain info
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        prog="convoyield",
        description="ConvoYield — Conversational Yield Optimization Engine",
    )
    subparsers = parser.add_subparsers(dest="command")

    # ── demo ──────────────────────────────────────────────────
    subparsers.add_parser("demo", help="Run the interactive demo")

    # ── server ────────────────────────────────────────────────
    server_p = subparsers.add_parser("server", help="Start the Cloud API server")
    server_p.add_argument("--port", type=int, default=8000)
    server_p.add_argument("--host", default="0.0.0.0")

    # ── analyze ───────────────────────────────────────────────
    analyze_p = subparsers.add_parser("analyze", help="Analyze a conversation log")
    analyze_p.add_argument("file", help="JSON file with conversation logs")
    analyze_p.add_argument("--base-value", type=float, default=25.0)

    # ── register ──────────────────────────────────────────────
    register_p = subparsers.add_parser("register", help="Register for a Cloud API key")
    register_p.add_argument("--email", required=True)
    register_p.add_argument("--server", default="http://localhost:8000")

    # ── playbooks ─────────────────────────────────────────────
    subparsers.add_parser("playbooks", help="List available premium playbooks")

    # ── status ────────────────────────────────────────────────
    status_p = subparsers.add_parser("status", help="Check system status")
    status_p.add_argument("--server", default="http://localhost:8000")

    # ── interactive ───────────────────────────────────────────
    subparsers.add_parser("interactive", help="Interactive conversation mode")

    # ── coin ──────────────────────────────────────────────────
    coin_p = subparsers.add_parser("coin", help="ConvoCoin management")
    coin_sub = coin_p.add_subparsers(dest="coin_command")
    coin_sub.add_parser("wallet", help="Create or show wallet")
    coin_sub.add_parser("mine", help="Interactive mining mode")
    coin_sub.add_parser("balance", help="Check CVC balance")
    coin_sub.add_parser("status", help="Full ConvoCoin status")
    coin_sub.add_parser("marketplace", help="Browse marketplace")
    coin_sub.add_parser("tokenomics", help="View tokenomics")
    coin_sub.add_parser("chain", help="View blockchain info")

    args = parser.parse_args()

    if args.command == "demo":
        _run_demo()
    elif args.command == "server":
        _run_server(args.host, args.port)
    elif args.command == "analyze":
        _run_analyze(args.file, args.base_value)
    elif args.command == "register":
        _run_register(args.email, args.server)
    elif args.command == "playbooks":
        _list_playbooks()
    elif args.command == "status":
        _check_status(args.server)
    elif args.command == "interactive":
        _run_interactive()
    elif args.command == "coin":
        _run_coin(args)
    else:
        parser.print_help()
        _print_banner()


def _print_banner():
    print()
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║       ConvoYield v1.0.0                         ║")
    print("  ║       Conversational Yield Optimization Engine   ║")
    print("  ║                                                  ║")
    print("  ║  Every conversation is a financial instrument.   ║")
    print("  ║  We help you maximize its yield.                 ║")
    print("  ╚══════════════════════════════════════════════════╝")
    print()
    print("  Commands:")
    print("    convoyield demo          Run the live demo")
    print("    convoyield server        Start the Cloud API server")
    print("    convoyield interactive   Chat and see live yield analysis")
    print("    convoyield analyze       Analyze conversation logs")
    print("    convoyield playbooks     Browse premium playbooks")
    print("    convoyield register      Get your API key")
    print("    convoyield status        Check system status")
    print("    convoyield coin          ConvoCoin management")
    print()


def _run_demo():
    """Run the basic usage demo."""
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from examples.basic_usage import main as demo_main
    demo_main()


def _run_server(host: str, port: int):
    """Start the Cloud API server."""
    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn is required to run the server.")
        print("Install it with: pip install 'convoyield[cloud]'")
        sys.exit(1)

    print(f"\n  Starting ConvoYield Cloud Server on {host}:{port}")
    print(f"  Dashboard:  http://localhost:{port}/")
    print(f"  API Docs:   http://localhost:{port}/docs")
    print(f"  Health:     http://localhost:{port}/api/v1/health\n")

    uvicorn.run("cloud.server:app", host=host, port=port, reload=True)


def _run_analyze(file_path: str, base_value: float):
    """Analyze a conversation log file."""
    from convoyield import ConvoYield

    path = Path(file_path)
    if not path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    with open(path) as f:
        conversations = json.load(f)

    print(f"\n  Analyzing {len(conversations)} conversations...")
    print(f"  Base value: ${base_value:.2f}\n")

    total_yield = 0.0
    total_captured = 0.0
    all_plays = {}
    all_arbitrage = {}

    for i, convo in enumerate(conversations):
        engine = ConvoYield(base_conversation_value=base_value)
        result = engine.process_conversation(convo)

        total_yield += result.estimated_yield
        total_captured += result.yield_captured_so_far

        if result.recommended_play:
            all_plays[result.recommended_play] = all_plays.get(result.recommended_play, 0) + 1

        for arb in result.arbitrage_opportunities:
            all_arbitrage[arb.type] = all_arbitrage.get(arb.type, 0) + 1

        print(f"  [{i+1}/{len(conversations)}] Yield: ${result.estimated_yield:.2f} | "
              f"Play: {result.recommended_play or 'N/A'} | "
              f"Phase: {result.phase}")

    print(f"\n  {'=' * 50}")
    print(f"  Total Estimated Yield:   ${total_yield:.2f}")
    print(f"  Total Captured Yield:    ${total_captured:.2f}")
    print(f"  Value Left on Table:     ${total_yield - total_captured:.2f}")
    print(f"  Avg Yield/Conversation:  ${total_yield / len(conversations):.2f}")

    if all_plays:
        print(f"\n  Top Plays:")
        for play, count in sorted(all_plays.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {play}: {count}x")

    if all_arbitrage:
        print(f"\n  Arbitrage Types:")
        for arb, count in sorted(all_arbitrage.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {arb}: {count}x")

    print()


def _run_register(email: str, server: str):
    """Register for an API key."""
    import urllib.request
    import urllib.error

    url = f"{server}/api/v1/keys"
    data = json.dumps({"email": email, "tier": "free"}).encode()

    try:
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())

        print(f"\n  Registration successful!")
        print(f"  API Key: {result['api_key']}")
        print(f"  Tier:    {result['tier']}")
        print(f"\n  Save this key! You'll need it for your bot integration:")
        print(f"    export CONVOYIELD_API_KEY={result['api_key']}")
        print()

    except urllib.error.URLError:
        print(f"\n  Error: Could not connect to {server}")
        print(f"  Make sure the server is running: convoyield server")
        print()


def _list_playbooks():
    """List available premium playbooks."""
    from convoyield.playbooks import ALL_PLAYBOOKS

    print(f"\n  Premium Playbooks")
    print(f"  {'=' * 50}")

    for pb_id, pb in ALL_PLAYBOOKS.items():
        plays = pb["plays"]
        print(f"\n  {pb['name']}")
        print(f"  {'─' * 40}")
        print(f"  ID:     {pb_id}")
        print(f"  Plays:  {len(plays)}")
        print(f"  Price:  ${pb['price']:.0f}/month")
        print(f"\n  Sample plays:")
        for play in plays[:3]:
            print(f"    - {play['name']}: {play['description'][:60]}...")

    print(f"\n  Total: {sum(len(pb['plays']) for pb in ALL_PLAYBOOKS.values())} plays across {len(ALL_PLAYBOOKS)} playbooks")
    print()


def _check_status(server: str):
    """Check system status."""
    import urllib.request
    import urllib.error

    print(f"\n  ConvoYield System Status")
    print(f"  {'=' * 40}")

    # Check engine
    try:
        from convoyield import ConvoYield
        engine = ConvoYield()
        result = engine.process_user_message("test")
        print(f"  Engine:     OK (v1.0.0)")
    except Exception as e:
        print(f"  Engine:     ERROR ({e})")

    # Check playbooks
    try:
        from convoyield.playbooks import ALL_PLAYBOOKS
        total = sum(len(pb["plays"]) for pb in ALL_PLAYBOOKS.values())
        print(f"  Playbooks:  OK ({total} plays across {len(ALL_PLAYBOOKS)} packs)")
    except Exception as e:
        print(f"  Playbooks:  ERROR ({e})")

    # Check ConvoCoin
    try:
        from convoyield.coin.engine_bridge import CoinBridge
        bridge = CoinBridge()
        stats = bridge.blockchain.get_stats()
        print(f"  ConvoCoin:  OK (chain height: {stats['chain_height']})")
    except Exception as e:
        print(f"  ConvoCoin:  ERROR ({e})")

    # Check server
    try:
        url = f"{server}/api/v1/health"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read())
            print(f"  Server:     OK ({result.get('version', 'unknown')})")
    except Exception:
        print(f"  Server:     OFFLINE ({server})")

    print()


def _run_interactive():
    """Interactive conversation mode with live yield analysis + mining."""
    from convoyield import ConvoYield
    from convoyield.coin.engine_bridge import CoinBridge

    engine = ConvoYield(base_conversation_value=50.0)
    bridge = CoinBridge()
    address, secret = bridge.create_wallet("interactive")
    bridge.attach(engine)

    print()
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║  ConvoYield Interactive Mode + ConvoCoin Mining  ║")
    print("  ║  Type messages to see yield analysis + mine CVC  ║")
    print("  ║  Type 'quit' to exit.                            ║")
    print("  ╚══════════════════════════════════════════════════╝")
    print(f"  Wallet: {address}")
    print()

    while True:
        try:
            user_input = input("  YOU > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye!")
            break

        if not user_input or user_input.lower() in ("quit", "exit", "q"):
            bridge.save()
            print("  Ledger saved. Goodbye!")
            break

        result = engine.process_user_message(user_input)
        mining = bridge.miner.get_mining_status()

        print()
        print(f"  ┌─ Yield Analysis {'─' * 40}")
        print(f"  │ Sentiment:     {result.current_sentiment:+.2f} (delta: {result.sentiment_delta:+.2f})")
        print(f"  │ Momentum:      {result.momentum_score:+.2f}")
        print(f"  │ Phase:         {result.phase}")
        print(f"  │ Est. Yield:    ${result.estimated_yield:.2f}")
        print(f"  │ Risk:          {result.risk_level:.0%}")
        print(f"  │ Play:          {result.recommended_play or 'N/A'}")
        print(f"  │ Tone:          {result.recommended_tone}")

        if result.arbitrage_opportunities:
            top = result.top_arbitrage
            print(f"  │")
            print(f"  │ ARBITRAGE: {top.type} (${top.estimated_value:.2f})")

        if result.micro_conversions:
            print(f"  │")
            for mc in result.micro_conversions[:3]:
                print(f"  │ MC: {mc.type} (${mc.value:.2f})")

        # Mining status
        print(f"  │")
        print(f"  ├─ ConvoCoin Mining {'─' * 37}")
        print(f"  │ Balance:       {mining['total_coins_earned']:.4f} CVC")
        print(f"  │ Mining:        {mining['progress_percent']:.0f}% to next block")
        print(f"  │ Yield Acc:     ${mining['accumulated_yield']:.2f} / ${mining['mining_threshold']:.2f}")
        print(f"  │ Blocks Mined:  {mining['total_blocks_mined']}")

        # Check if a block was just mined
        recent = bridge.get_recent_mining(1)
        if recent and recent[-1].get("block_index", 0) == bridge.blockchain.height - 1:
            last = recent[-1]
            print(f"  │")
            print(f"  │ ** BLOCK MINED! #{last['block_index']} **")
            print(f"  │ ** Reward: {last['reward']:.4f} CVC **")

        print(f"  └{'─' * 58}")
        print()

        engine.record_bot_response(f"[Bot response to turn {engine.state.turn_count}]")


# ── ConvoCoin CLI ─────────────────────────────────────────────────────────────

def _run_coin(args):
    """Handle all ConvoCoin subcommands."""
    from convoyield.coin.engine_bridge import CoinBridge

    cmd = getattr(args, "coin_command", None)

    if cmd == "wallet":
        _coin_wallet()
    elif cmd == "mine":
        _coin_mine()
    elif cmd == "balance":
        _coin_balance()
    elif cmd == "status":
        _coin_status()
    elif cmd == "marketplace":
        _coin_marketplace()
    elif cmd == "tokenomics":
        _coin_tokenomics()
    elif cmd == "chain":
        _coin_chain()
    else:
        _coin_banner()


def _coin_banner():
    print()
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║       ConvoCoin (CVC)                            ║")
    print("  ║       The Proof-of-Yield Cryptocurrency          ║")
    print("  ║                                                  ║")
    print("  ║  Mine tokens by capturing conversational yield.  ║")
    print("  ║  Real work. Real value. Real tokens.             ║")
    print("  ╚══════════════════════════════════════════════════╝")
    print()
    print("  Commands:")
    print("    convoyield coin wallet       Create/show your wallet")
    print("    convoyield coin mine         Start mining with conversations")
    print("    convoyield coin balance      Check your CVC balance")
    print("    convoyield coin status       Full blockchain status")
    print("    convoyield coin marketplace  Browse the CVC marketplace")
    print("    convoyield coin tokenomics   View supply & economics")
    print("    convoyield coin chain        View blockchain info")
    print()


def _coin_wallet():
    from convoyield.coin.engine_bridge import CoinBridge

    bridge = CoinBridge()
    address, secret = bridge.create_wallet("cli-wallet")

    print(f"\n  ConvoCoin Wallet Created")
    print(f"  {'=' * 50}")
    print(f"  Address:    {address}")
    print(f"  Secret Key: {secret}")
    print(f"\n  SAVE YOUR SECRET KEY! It cannot be recovered.")
    print(f"  Your wallet is your identity on the ConvoCoin chain.")
    print()


def _coin_balance():
    from convoyield.coin.engine_bridge import CoinBridge

    bridge = CoinBridge()
    address, _ = bridge.create_wallet("check")
    balance = bridge.blockchain.get_balance(address)

    print(f"\n  ConvoCoin Balance")
    print(f"  {'=' * 40}")
    print(f"  Address: {address}")
    print(f"  Balance: {balance:.8f} CVC")
    print(f"  Tier:    {bridge.wallet_manager.get_staking_tier(address)}")
    print()


def _coin_status():
    from convoyield.coin.engine_bridge import CoinBridge

    bridge = CoinBridge()
    bridge.create_wallet("status-check")
    status = bridge.status()

    print(f"\n  ConvoCoin System Status")
    print(f"  {'=' * 50}")

    w = status["wallet"]
    print(f"\n  Wallet:")
    print(f"    Address:      {w['address']}")
    print(f"    Balance:      {w['balance_cvc']:.8f} CVC")
    print(f"    Staking Tier: {w['staking_tier']}")
    print(f"    Staked:       {w['staked_amount']:.8f} CVC")

    b = status["blockchain"]
    print(f"\n  Blockchain:")
    print(f"    Chain Height:    {b['chain_height']} blocks")
    print(f"    Total Mined:     {b['total_supply_mined']:.8f} CVC")
    print(f"    Total TXs:       {b['total_transactions']}")
    print(f"    Chain Valid:     {b['chain_valid']}")
    print(f"    Block Reward:    {b['current_block_reward']:.8f} CVC")
    print(f"    Next Halving:    Block #{b['next_halving_block']}")

    e = status["economics"]
    print(f"\n  Economics:")
    print(f"    Max Supply:      {e['max_supply']:,.0f} CVC")
    print(f"    Mined:           {e['percent_mined']:.4f}%")
    print(f"    Burned:          {e['total_burned']:.8f} CVC")
    print(f"    Circulating:     {e['effective_circulating']:.8f} CVC")
    print(f"    Scarcity Ratio:  {e['scarcity_ratio']:.4f}")

    m = status["marketplace"]
    print(f"\n  Marketplace:")
    print(f"    Listings:        {m['total_listings']}")
    print(f"    Total Sales:     {m['total_sales']}")
    print(f"    Volume:          {m['total_volume_cvc']:.8f} CVC")

    print()


def _coin_mine():
    """Interactive mining mode — chat and mine CVC."""
    from convoyield import ConvoYield
    from convoyield.coin.engine_bridge import CoinBridge

    engine = ConvoYield(base_conversation_value=50.0)
    bridge = CoinBridge()
    address, secret = bridge.create_wallet("miner")
    bridge.attach(engine)

    print()
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║  ConvoCoin Mining Rig                            ║")
    print("  ║  Chat to capture yield and mine CVC tokens.      ║")
    print("  ║  Type 'quit' to stop mining.                     ║")
    print("  ╚══════════════════════════════════════════════════╝")
    print(f"  Wallet: {address}")
    print(f"  Block Reward: {bridge.miner.get_mining_status()['current_block_reward']:.4f} CVC")
    print()

    while True:
        try:
            user_input = input("  MINE > ").strip()
        except (EOFError, KeyboardInterrupt):
            bridge.save()
            print(f"\n  Mining stopped. Ledger saved.")
            break

        if not user_input or user_input.lower() in ("quit", "exit", "q"):
            bridge.save()
            ms = bridge.miner.get_mining_status()
            print(f"\n  Mining Summary:")
            print(f"    Blocks Mined:  {ms['total_blocks_mined']}")
            print(f"    CVC Earned:    {ms['total_coins_earned']:.8f}")
            print(f"    Ledger saved to: {bridge.ledger.path}")
            break

        result = engine.process_user_message(user_input)
        ms = bridge.miner.get_mining_status()

        # Mining progress bar
        progress = int(ms["progress_percent"] / 5)
        bar = "█" * progress + "░" * (20 - progress)

        print(f"  [{bar}] {ms['progress_percent']:.0f}% | "
              f"${ms['accumulated_yield']:.2f} yield | "
              f"{ms['total_coins_earned']:.4f} CVC | "
              f"Block #{ms['chain_height']}")

        # Check if we just mined
        recent = bridge.get_recent_mining(1)
        if recent and recent[-1].get("block_index", 0) == bridge.blockchain.height - 1:
            last = recent[-1]
            print(f"\n  *** BLOCK #{last['block_index']} MINED! ***")
            print(f"  *** Reward: +{last['reward']:.4f} CVC ***")
            print(f"  *** Hash: {last['block_hash']} ***\n")

        engine.record_bot_response(f"[Mining response turn {engine.state.turn_count}]")


def _coin_marketplace():
    from convoyield.coin.engine_bridge import CoinBridge

    bridge = CoinBridge()
    listings = bridge.list_marketplace()

    print(f"\n  ConvoCoin Marketplace")
    print(f"  {'=' * 50}")

    for item in listings:
        print(f"\n  [{item['listing_id']}] {item['name']}")
        print(f"  {item['description'][:70]}...")
        print(f"  Price: {item['price_cvc']:.0f} CVC | Sales: {item['total_sales']}")

    stats = bridge.marketplace.get_marketplace_stats()
    print(f"\n  {'─' * 50}")
    print(f"  Total Volume: {stats['total_volume_cvc']:.2f} CVC")
    print(f"  Total Burned: {stats['total_burned_cvc']:.8f} CVC (2% per sale)")
    print()


def _coin_tokenomics():
    from convoyield.coin.tokenomics import Tokenomics

    t = Tokenomics()

    print(f"\n  ConvoCoin Tokenomics")
    print(f"  {'=' * 50}")
    print(f"\n  Supply:")
    print(f"    Max Supply:         {t.MAX_SUPPLY:>14,.0f} CVC")
    print(f"    Genesis Allocation: {t.GENESIS_ALLOCATION:>14,.0f} CVC (10%)")
    print(f"    Mineable:           {t.MAX_SUPPLY - t.GENESIS_ALLOCATION:>14,.0f} CVC (90%)")

    print(f"\n  Mining:")
    print(f"    Initial Reward:     {t.INITIAL_BLOCK_REWARD} CVC/block")
    print(f"    Halving Interval:   Every {t.HALVING_INTERVAL} blocks")
    print(f"    Base Threshold:     ${t.BASE_MINING_THRESHOLD:.2f} yield/block")
    print(f"    Max Threshold:      ${t.MAX_MINING_THRESHOLD:.2f} yield/block")

    print(f"\n  Burn:")
    print(f"    Marketplace Fee:    {t.MARKETPLACE_BURN_RATE * 100:.0f}% (deflationary)")

    print(f"\n  Staking Tiers:")
    for tier in ["bronze", "silver", "gold"]:
        benefits = t.get_staking_benefits(tier)
        print(f"\n    {tier.upper()} ({benefits['min_stake']}+ CVC):")
        for feature in benefits["features"]:
            print(f"      + {feature}")

    print(f"\n  Halving Schedule:")
    schedule = t.get_halving_schedule()
    for h in schedule[:8]:
        print(f"    Block {h['block_height']:>6,}: {h['block_reward']:.8f} CVC/block")

    print()


def _coin_chain():
    from convoyield.coin.engine_bridge import CoinBridge

    bridge = CoinBridge()
    stats = bridge.blockchain.get_stats()

    print(f"\n  ConvoCoin Blockchain")
    print(f"  {'=' * 50}")
    print(f"  Chain Height:      {stats['chain_height']} blocks")
    print(f"  Total Supply:      {stats['total_supply_mined']:.8f} CVC")
    print(f"  Total Yield:       ${stats['total_yield_proven']:.2f}")
    print(f"  Total TXs:         {stats['total_transactions']}")
    print(f"  Pending TXs:       {stats['pending_transactions']}")
    print(f"  Chain Valid:       {stats['chain_valid']}")
    print(f"  Current Reward:    {stats['current_block_reward']:.8f} CVC")
    print(f"  Next Halving:      Block #{stats['next_halving_block']}")
    print(f"  Halvings:          {stats['halvings_occurred']}")

    # Show recent blocks
    chain = bridge.blockchain.chain
    print(f"\n  Recent Blocks:")
    for block in chain[-5:]:
        print(f"    #{block.index} | {block.hash[:16]}... | "
              f"{len(block.transactions)} txs | "
              f"yield: ${block.proof_of_yield:.2f}")

    print()


if __name__ == "__main__":
    main()
