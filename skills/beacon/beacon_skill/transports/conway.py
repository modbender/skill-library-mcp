"""Conway Automaton transport: Bridge between Beacon Protocol and Conway's agent ecosystem.

Conway agents use EVM wallets (Base chain) and x402 USDC micropayments.
Beacon agents use Ed25519 keys and RTC payments.
This transport bridges both worlds:
  - Send/receive messages via Conway Social Relay (social.conway.tech)
  - Discover Conway agents via ERC-8004 registry on Base
  - Accept x402 USDC payments alongside RTC

Beacon 2.9.0 — Elyan Labs.
"""

import hashlib
import json
import time
from typing import Any, Dict, List, Optional

import requests

from ..identity import AgentIdentity

# Conway infrastructure endpoints
CONWAY_SOCIAL_RELAY = "https://social.conway.tech"
CONWAY_CLOUD_API = "https://api.conway.tech"
X402_FACILITATOR = "https://x402.org/facilitator"

# ERC-8004 agent identity registry on Base mainnet
ERC8004_REGISTRY = "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432"
ERC8004_REPUTATION = "0x8004BAa17C55a88189AE136b182e5fdA19dE9b63"
BASE_CHAIN_ID = 8453
BASE_RPC = "https://mainnet.base.org"

# USDC on Base
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"


class ConwayClient:
    """Bridge between Beacon Protocol and Conway Automaton ecosystem."""

    def __init__(
        self,
        identity: AgentIdentity,
        *,
        eth_address: str = "",
        social_relay: str = CONWAY_SOCIAL_RELAY,
        timeout: int = 15,
    ):
        self._identity = identity
        self._eth_address = eth_address  # Optional: link beacon ID to an EVM wallet
        self._relay = social_relay
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": f"BeaconSkill/2.9.0 ({identity.agent_id})",
            "Content-Type": "application/json",
        })

    # ── Conway Social Relay ──

    def send_message(
        self,
        to_agent: str,
        content: str,
        *,
        kind: str = "beacon_envelope",
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Send a message via Conway's social relay.

        Conway agents are identified by ETH addresses (0x...).
        We include our beacon agent_id and pubkey so they can verify/respond.
        """
        payload = {
            "from": self._eth_address or self._identity.agent_id,
            "to": to_agent,
            "content": content,
            "kind": kind,
            "timestamp": int(time.time()),
            "beacon_agent_id": self._identity.agent_id,
            "beacon_pubkey": self._identity.public_key_hex,
        }
        if metadata:
            payload["metadata"] = metadata

        # Sign with Ed25519 so Conway agents can verify our beacon identity
        msg = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        payload["beacon_signature"] = self._identity.sign_hex(msg)

        try:
            resp = self._session.post(
                f"{self._relay}/v1/messages",
                json=payload,
                timeout=self._timeout,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def poll_inbox(self, since: int = 0) -> List[Dict[str, Any]]:
        """Poll Conway social relay for incoming messages."""
        params: Dict[str, Any] = {}
        if since:
            params["since"] = since
        if self._eth_address:
            params["address"] = self._eth_address
        else:
            params["address"] = self._identity.agent_id

        try:
            resp = self._session.post(
                f"{self._relay}/v1/messages/poll",
                json=params,
                timeout=self._timeout,
            )
            resp.raise_for_status()
            return resp.json().get("messages", [])
        except Exception:
            return []

    # ── ERC-8004 Agent Discovery ──

    def discover_agents(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Scan ERC-8004 registry on Base for Conway agents.

        Returns agent cards for discovered agents, including their
        wallet addresses, capabilities, and x402 support status.
        """
        try:
            # Use eth_call to read totalSupply from ERC-8004
            total_resp = self._session.post(
                BASE_RPC,
                json={
                    "jsonrpc": "2.0",
                    "method": "eth_call",
                    "params": [{
                        "to": ERC8004_REGISTRY,
                        "data": "0x18160ddd",  # totalSupply()
                    }, "latest"],
                    "id": 1,
                },
                timeout=self._timeout,
            )
            result = total_resp.json().get("result", "0x0")
            total = int(result, 16)
            agents = []

            # Fetch agent URIs for recent registrations
            scan_count = min(total, limit)
            for token_id in range(max(0, total - scan_count), total):
                try:
                    uri = self._get_agent_uri(token_id)
                    if uri:
                        card = self._fetch_agent_card(uri)
                        if card:
                            card["token_id"] = token_id
                            agents.append(card)
                except Exception:
                    continue

            return agents
        except Exception as e:
            return [{"error": str(e)}]

    def _get_agent_uri(self, token_id: int) -> Optional[str]:
        """Read agentURI from ERC-8004 for a given token ID."""
        # agentURI(uint256) selector
        data = "0x" + "e9dc6375" + hex(token_id)[2:].zfill(64)
        try:
            resp = self._session.post(
                BASE_RPC,
                json={
                    "jsonrpc": "2.0",
                    "method": "eth_call",
                    "params": [{"to": ERC8004_REGISTRY, "data": data}, "latest"],
                    "id": 1,
                },
                timeout=self._timeout,
            )
            result = resp.json().get("result", "0x")
            if len(result) > 130:
                # Decode ABI-encoded string
                hex_str = result[130:]  # skip offset + length words
                raw = bytes.fromhex(hex_str).rstrip(b"\x00")
                return raw.decode("utf-8", errors="ignore").strip()
        except Exception:
            pass
        return None

    def _fetch_agent_card(self, uri: str) -> Optional[Dict]:
        """Fetch and parse a Conway agent card from its URI."""
        if not uri.startswith("http"):
            return None
        try:
            resp = self._session.get(uri, timeout=self._timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    # ── Agent Card Bridge ──

    def generate_conway_agent_card(
        self,
        *,
        name: str = "Elyan Labs Compute",
        services: Optional[List[Dict]] = None,
        x402_endpoints: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Generate a Conway-compatible agent card from Beacon identity.

        This produces /.well-known/agent-card.json that Conway agents
        can discover and interact with.
        """
        card: Dict[str, Any] = {
            "type": "https://eips.ethereum.org/EIPS/eip-8004#registration-v1",
            "name": name,
            "description": "Beacon Protocol agent with lab compute (V100/POWER8). "
                           "Accepts x402 USDC and RTC payments.",
            "active": True,
            "x402Support": True,
            # Bridge identities
            "beacon": {
                "agent_id": self._identity.agent_id,
                "public_key_hex": self._identity.public_key_hex,
                "protocol_version": "2.9.0",
            },
        }

        if self._eth_address:
            card["services"] = [
                {"name": "agentWallet", "endpoint": f"eip155:{BASE_CHAIN_ID}:{self._eth_address}"},
            ]

        if services:
            card.setdefault("services", []).extend(services)

        if x402_endpoints:
            card["x402_endpoints"] = x402_endpoints

        # Sign with beacon identity for cross-verification
        msg = json.dumps(card, sort_keys=True, separators=(",", ":")).encode()
        card["beacon_signature"] = self._identity.sign_hex(msg)

        return card

    # ── x402 Payment Verification ──

    @staticmethod
    def verify_x402_payment(
        payment_header: str,
        expected_amount: int,
        pay_to: str,
    ) -> Dict[str, Any]:
        """Verify an x402 payment signature via Coinbase facilitator.

        Args:
            payment_header: Base64 JSON from PAYMENT-SIGNATURE header
            expected_amount: Amount in USDC smallest units (6 decimals)
            pay_to: Receiving wallet address (0x...)

        Returns:
            {"verified": bool, "tx_hash": str, ...}
        """
        import base64
        try:
            payment_data = json.loads(base64.b64decode(payment_header))
        except Exception:
            return {"verified": False, "error": "Invalid payment header"}

        try:
            resp = requests.post(
                f"{X402_FACILITATOR}/verify",
                json={
                    "payment": payment_data,
                    "paymentRequirements": {
                        "scheme": "exact",
                        "network": f"eip155:{BASE_CHAIN_ID}",
                        "amount": str(expected_amount),
                        "asset": USDC_BASE,
                        "payTo": pay_to,
                    },
                },
                timeout=30,
            )
            resp.raise_for_status()
            result = resp.json()
            return {
                "verified": result.get("isValid", False),
                "tx_hash": result.get("txHash", ""),
                "settled": result.get("settled", False),
            }
        except Exception as e:
            return {"verified": False, "error": str(e)}

    # ── Dual Payment Check ──

    def accepts_payment(self) -> Dict[str, Any]:
        """Return payment capabilities for agent card advertisement."""
        caps = {
            "rustchain_rtc": {
                "accepted": True,
                "node": "https://50.28.86.131",
                "reference_rate_usd": 0.10,
            },
            "x402_usdc": {
                "accepted": True,
                "network": f"eip155:{BASE_CHAIN_ID}",
                "asset": USDC_BASE,
                "facilitator": X402_FACILITATOR,
            },
        }
        if self._eth_address:
            caps["x402_usdc"]["pay_to"] = self._eth_address
        return caps
