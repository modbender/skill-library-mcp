"""Beacon DNS — Human-readable name resolution for agent IDs.

Maps names like ``sophia-elya`` to beacon agent IDs like ``bcn_c850ea702e8f``.
Agents register names on relay registration; additional names can be registered
via the ``/api/dns`` endpoint.

Beacon 2.11.0 — Elyan Labs.
"""

import json
import time
from typing import Any, Dict, List, Optional

import requests
from requests.exceptions import JSONDecodeError

# Default Beacon DNS server (proxied through nginx at /beacon/)
DEFAULT_DNS_URL = "http://50.28.86.131:8070/beacon"


class BeaconDNS:
    """HTTP client for Beacon DNS name resolution.

    Usage::

        dns = BeaconDNS()
        result = dns.resolve("sophia-elya")
        # {"name": "sophia-elya", "agent_id": "bcn_c850ea702e8f", ...}

        names = dns.reverse("bcn_c850ea702e8f")
        # [{"name": "sophia-elya", "owner": "elyan", ...}]
    """

    def __init__(self, base_url: str = DEFAULT_DNS_URL, timeout_s: int = 15):
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "User-Agent": "Beacon-DNS/1.0.0 (Elyan Labs)",
        }

    @staticmethod
    def _parse(resp: requests.Response) -> Dict[str, Any]:
        """Parse response, handling non-JSON errors gracefully."""
        try:
            data = resp.json()
        except (JSONDecodeError, ValueError):
            data = {"error": f"HTTP {resp.status_code}", "raw": resp.text[:200]}
        if resp.status_code >= 400 and "error" not in data:
            data["error"] = f"HTTP {resp.status_code}"
        return data

    def resolve(self, name: str) -> Dict[str, Any]:
        """Resolve a human-readable name to a beacon agent_id.

        Args:
            name: Human-readable agent name (e.g. "sophia-elya").

        Returns:
            Dict with name, agent_id, owner, created_at.
        """
        resp = requests.get(
            self._url(f"/api/dns/{name}"),
            headers=self._headers(),
            timeout=self.timeout_s,
        )
        return self._parse(resp)

    def reverse(self, agent_id: str) -> Dict[str, Any]:
        """Reverse lookup: agent_id to list of registered names.

        Args:
            agent_id: Beacon agent ID (e.g. "bcn_c850ea702e8f").

        Returns:
            Dict with agent_id and list of names.
        """
        resp = requests.get(
            self._url(f"/api/dns/reverse/{agent_id}"),
            headers=self._headers(),
            timeout=self.timeout_s,
        )
        return self._parse(resp)

    def register(
        self,
        name: str,
        agent_id: str,
        owner: str = "",
    ) -> Dict[str, Any]:
        """Register a new DNS name for an agent.

        Args:
            name: Human-readable name to register (3-64 chars, alphanumeric + hyphens).
            agent_id: Beacon agent ID to map to.
            owner: Optional owner identifier.

        Returns:
            Dict with registration result.
        """
        body = {
            "name": name,
            "agent_id": agent_id,
        }
        if owner:
            body["owner"] = owner

        resp = requests.post(
            self._url("/api/dns"),
            json=body,
            headers=self._headers(),
            timeout=self.timeout_s,
        )
        return self._parse(resp)

    def list_all(self) -> Dict[str, Any]:
        """List all registered DNS names.

        Returns:
            Dict with list of all DNS records.
        """
        resp = requests.get(
            self._url("/api/dns"),
            headers=self._headers(),
            timeout=self.timeout_s,
        )
        return self._parse(resp)
