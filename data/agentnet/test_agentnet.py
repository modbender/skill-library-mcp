"""
AgentNet Test Suite - v0.1

Tests:
1. Register Nix with real capabilities
2. Query "who can trade on Polymarket?"
3. Handshake demo
4. Trust score update
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import time
import hashlib
from registry import Registry, AgentEntry
from card import AgentCard, create_nix_card, generate_fingerprint
from handshake import HandshakeProtocol, TaskOffer


def separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def test_register_nix():
    separator("TEST 1: Register Nix")

    reg = Registry()
    nix_card = create_nix_card()

    entry = AgentEntry(
        agent_id=nix_card.agent_id,
        name=nix_card.name,
        description=nix_card.description,
        capabilities=nix_card.capabilities,
        dna_fingerprint=nix_card.dna_fingerprint,
        contact=nix_card.contact,
        status="online",
        skills=nix_card.skills,
        trust_score=nix_card.trust_score,
        registered_at=time.time(),
        last_seen=time.time(),
        metadata=nix_card.metadata,
    )

    result = reg.register(entry)
    print(f"  Result: {result['status']} - {result['agent_id']}")

    # Verify it's in the registry
    found = reg.get(nix_card.agent_id)
    assert found is not None, "Nix not found after registration!"
    assert found["name"] == "Nix"
    print(f"  Verified: {found['name']} is registered with {len(found['capabilities'])} capabilities")
    print(f"  Status: {found['status']}")
    print(f"  Trust score: {found['trust_score']}")
    print("  PASS")
    return reg


def test_discover_polymarket_traders(reg: Registry):
    separator("TEST 2: Query - Who can trade on Polymarket?")

    results = reg.discover("polymarket")
    print(f"  Found {len(results)} agent(s) with 'polymarket' capability:")
    for a in results:
        print(f"\n  Agent: {a['name']} ({a['agent_id']})")
        print(f"  Status: {a['status']} | Trust: {a['trust_score']}")
        poly_caps = [c for c in a['capabilities'] if 'polymarket' in c.lower() or 'trade' in c.lower() or 'market' in c.lower()]
        print(f"  Relevant capabilities: {', '.join(poly_caps[:5])}")
        print(f"  Contact: {a['contact']}")

    assert len(results) > 0, "Should find at least Nix!"
    print("\n  PASS")
    return results


def test_discover_code(reg: Registry):
    separator("TEST 3: Query - Who can write code?")

    results = reg.discover("code")
    print(f"  Found {len(results)} agent(s) with 'code' capability:")
    for a in results:
        print(f"  - {a['name']}: {[c for c in a['capabilities'] if 'code' in c.lower() or 'python' in c.lower() or 'develop' in c.lower()]}")

    print("  PASS")


def test_discover_charts(reg: Registry):
    separator("TEST 4: Query - Who can analyze charts?")

    results = reg.discover("chart")
    print(f"  Found {len(results)} agent(s) with 'chart' capability:")
    for a in results:
        print(f"  - {a['name']}: {[c for c in a['capabilities'] if 'chart' in c.lower() or 'technical' in c.lower() or 'analysis' in c.lower()]}")
    print("  PASS")


def test_multi_agent_registry(reg: Registry):
    separator("TEST 5: Register Multiple Agents")

    # A hypothetical trading agent
    trader = AgentEntry(
        agent_id="poly-trader-x",
        name="PolyTrader-X",
        description="Automated Polymarket trader using ML signals.",
        capabilities=["polymarket-trading", "prediction-market-analysis", "automated-trading"],
        dna_fingerprint=generate_fingerprint("polytrader:x:v1"),
        contact={"type": "api", "value": "https://polytrader-x.example.com/api"},
        status="online",
        skills=["polymarket-agent"],
        trust_score=0.6,
        registered_at=time.time(),
        last_seen=time.time(),
    )

    # A social media agent
    social = AgentEntry(
        agent_id="social-bot-01",
        name="SocialBot",
        description="Cross-platform social media automation and content creation.",
        capabilities=["social-media-posting", "content-creation", "x-twitter-posting", "farcaster-posting"],
        dna_fingerprint=generate_fingerprint("socialbot:01:v1"),
        contact={"type": "webhook", "value": "https://social-relay.example.com/hook"},
        status="busy",
        skills=["social-media-manager", "x-twitter"],
        trust_score=0.75,
        registered_at=time.time(),
        last_seen=time.time(),
    )

    reg.register(trader)
    reg.register(social)

    stats = reg.stats()
    print(f"  Registry stats:")
    print(f"  Total agents: {stats['total']}")
    print(f"  Online: {stats['online']} | Busy: {stats['busy']} | Offline: {stats['offline']}")
    print(f"  All capabilities ({len(stats['capabilities'])} total):")
    for cap in stats['capabilities'][:10]:
        print(f"    - {cap}")
    if len(stats['capabilities']) > 10:
        print(f"    ... and {len(stats['capabilities']) - 10} more")
    print("  PASS")


def test_handshake(reg: Registry):
    separator("TEST 6: Handshake Protocol")

    nix_card = create_nix_card()

    # Get the poly trader card
    trader_data = reg.get("poly-trader-x")
    if not trader_data:
        print("  (No poly-trader-x found, skipping - run test_multi_agent_registry first)")
        return

    trader_card = AgentCard(
        agent_id=trader_data["agent_id"],
        name=trader_data["name"],
        description=trader_data["description"],
        capabilities=trader_data["capabilities"],
        skills=trader_data["skills"],
        dna_fingerprint=trader_data["dna_fingerprint"],
        contact=trader_data["contact"],
        trust_score=trader_data["trust_score"],
    )

    protocol = HandshakeProtocol()

    # 1. Nix initiates
    hello = protocol.initiate(nix_card, trader_card.agent_id)
    print(f"  [HELLO] {hello.from_agent} -> {hello.to_agent}")

    # 2. Trader responds
    verify = protocol.respond(hello, trader_card)
    print(f"  [VERIFY] {verify.from_agent} -> {verify.to_agent}: {verify.payload['ack']}")

    # 3. Nix proposes
    nix_offer = TaskOffer(
        agent_id=nix_card.agent_id,
        needs=["prediction-market-analysis"],
        offers=["social-media-posting", "farcaster-posting"],
        description="Give me market signals - I'll broadcast your trades to 10k followers.",
        priority="high",
    )
    n_msg = protocol.negotiate(hello.session_id, nix_card.agent_id, nix_offer)
    print(f"  [NEGOTIATE] Nix proposes: {nix_offer.description}")

    # 4. Trader counter-offers
    trader_offer = TaskOffer(
        agent_id=trader_card.agent_id,
        needs=["social-media-posting"],
        offers=["polymarket-trading", "prediction-market-analysis"],
        description="I'll share alpha signals. You amplify my reach.",
        priority="normal",
    )
    protocol.negotiate(hello.session_id, trader_card.agent_id, trader_offer)
    score = nix_offer.match_score(trader_offer)
    print(f"  [NEGOTIATE] PolyTrader-X counter-offers. Match score: {score:.2f}")

    # 5. Accept
    accept_msg = protocol.accept(hello.session_id, nix_card.agent_id)
    print(f"  [ACCEPT] {accept_msg.payload['message']}")
    print(f"  Channel key: {accept_msg.payload['channel_key'][:20]}...")

    session = protocol.get_session(hello.session_id)
    print(f"  Final phase: {session.phase}")
    assert session.phase.value == "connected"
    print("  PASS")


def test_status_update(reg: Registry):
    separator("TEST 7: Status Updates")

    reg.update_status("nix-primary", "busy")
    nix = reg.get("nix-primary")
    assert nix["status"] == "busy"
    print("  Set Nix to 'busy' - OK")

    reg.update_status("nix-primary", "online")
    nix = reg.get("nix-primary")
    assert nix["status"] == "online"
    print("  Reset Nix to 'online' - OK")
    print("  PASS")


def test_trust_update(reg: Registry):
    separator("TEST 8: Trust Score Updates")

    # Simulate a successful interaction
    new_score = reg.update_trust("nix-primary", +1.0)
    print(f"  After positive interaction: trust = {new_score:.3f}")

    # Simulate a failed interaction
    new_score = reg.update_trust("nix-primary", -0.5)
    print(f"  After partial failure: trust = {new_score:.3f}")

    print("  PASS")


def run_all():
    print("\n" + "="*60)
    print("  AGENTNET v0.1 - TEST SUITE")
    print("="*60)
    print(f"  Running at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    reg = test_register_nix()
    test_discover_polymarket_traders(reg)
    test_discover_code(reg)
    test_discover_charts(reg)
    test_multi_agent_registry(reg)
    test_handshake(reg)
    test_status_update(reg)
    test_trust_update(reg)

    separator("ALL TESTS PASSED")
    print()

    # Final registry dump
    stats = reg.stats()
    print(f"  Registry has {stats['total']} agents, {len(stats['capabilities'])} unique capabilities")
    print(f"  The agent internet is online.\n")


if __name__ == "__main__":
    run_all()
