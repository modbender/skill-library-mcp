"""Agent Card: .well-known/beacon.json for internet-scale agent discovery."""

import json
from typing import Any, Dict, List, Optional

from .identity import AgentIdentity


def generate_agent_card(
    identity: AgentIdentity,
    *,
    name: str = "",
    transports: Optional[Dict[str, Any]] = None,
    capabilities: Optional[Dict[str, Any]] = None,
    values_mgr: Any = None,
) -> Dict[str, Any]:
    """Generate a signed .well-known/beacon.json agent card.

    The card is self-signed so anyone with the agent's pubkey can verify it.
    """
    card: Dict[str, Any] = {
        "beacon_version": "1.0.0",
        "agent_id": identity.agent_id,
        "public_key_hex": identity.public_key_hex,
    }
    if name:
        card["name"] = name
    if transports:
        card["transports"] = transports
    if capabilities:
        card["capabilities"] = capabilities
    else:
        # Try to pull preferences from config
        from .config import load_config
        cfg = load_config()
        prefs = cfg.get("preferences", {})
        accepted_kinds = prefs.get("accepted_kinds", ["like", "want", "bounty", "ad", "hello", "link", "event"])
        topics = prefs.get("topics", [])
        accept_rtc = prefs.get("accept_rtc", True)

        caps: Dict[str, Any] = {
            "kinds": accepted_kinds,
        }
        if accept_rtc:
            caps["payments"] = ["rustchain_rtc"]
            min_rtc = prefs.get("min_rtc", 0)
            if min_rtc > 0:
                caps["min_rtc"] = min_rtc
        if topics:
            caps["topics"] = topics

        role = cfg.get("beacon", {}).get("role", "")
        if role:
            caps["role"] = role

        card["capabilities"] = caps

    # Beacon 2.1 Soul: include values summary if available
    if values_mgr is not None:
        card["values"] = values_mgr.to_card_dict()

    # Sign the card (without the signature field).
    msg = json.dumps(card, sort_keys=True, separators=(",", ":")).encode("utf-8")
    card["signature"] = identity.sign_hex(msg)

    return card


def verify_agent_card(card: Dict[str, Any]) -> bool:
    """Verify a signed agent card.

    Returns True if the signature is valid and agent_id matches pubkey.
    """
    sig_hex = card.get("signature")
    pubkey_hex = card.get("public_key_hex")
    agent_id = card.get("agent_id", "")

    if not sig_hex or not pubkey_hex:
        return False

    # Verify agent_id matches pubkey.
    from .identity import agent_id_from_pubkey
    expected_id = agent_id_from_pubkey(bytes.fromhex(pubkey_hex))
    if expected_id != agent_id:
        return False

    # Verify signature.
    card_without_sig = {k: v for k, v in card.items() if k != "signature"}
    msg = json.dumps(card_without_sig, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return AgentIdentity.verify(pubkey_hex, sig_hex, msg)


def card_to_json(card: Dict[str, Any], indent: int = 2) -> str:
    """Format an agent card as pretty JSON."""
    return json.dumps(card, indent=indent, sort_keys=True)
