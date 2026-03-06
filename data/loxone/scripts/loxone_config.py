#!/usr/bin/env python3
"""Shared config helpers for the Loxone skill.

Supports two connection modes:

1) Local LAN:
   host: "192.168.0.222" (or hostname)
   use_https: false

2) Cloud DNS tunnel (do NOT hard-code the IP):
   host: "dns.loxonecloud.com/<SERIAL>"  (or just the serial "<SERIAL>")
   use_https: true

When a Cloud DNS host is used, we resolve the current IP/port via:
  https://dns.loxonecloud.com/?getip&snr=<SERIAL>&json=true

and derive the certificate-matching hostname:
  <ip-with-dashes>.<SERIAL>.dyndns.<datacenter>[:port]

This keeps TLS verification working while avoiding hard-coded IPs in config.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, Tuple

import requests


_CLOUD_DNS_RE = re.compile(r"(?i)(?:https?://)?dns\.loxonecloud\.com/(?P<snr>[0-9a-f]+)$")
_SNR_RE = re.compile(r"(?i)^[0-9a-f]{8,16}$")


@dataclass
class ResolvedHost:
    host: str
    use_https: bool


def _extract_snr(host_value: str) -> str | None:
    s = (host_value or "").strip()
    m = _CLOUD_DNS_RE.match(s)
    if m:
        return m.group("snr").upper()
    if _SNR_RE.match(s):
        return s.upper()
    return None


def resolve_cloud_dns_host(*, snr: str, timeout: float = 5.0) -> ResolvedHost:
    url = f"https://dns.loxonecloud.com/?getip&snr={snr}&json=true"
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    data: Dict[str, Any] = r.json()

    code = int(data.get("Code", 0) or 0)
    if code != 200:
        raise RuntimeError(f"Loxone Cloud DNS returned Code={code} for snr={snr}")

    datacenter = (data.get("DataCenter") or "loxonecloud.com").strip()

    if data.get("PortOpenHTTPS") and data.get("IPHTTPS"):
        ip_https = str(data.get("IPHTTPS"))
        ip, port = (ip_https.split(":", 1) + ["443"])[:2]
        use_https = True
    elif data.get("PortOpen") and data.get("IP"):
        ip_plain = str(data.get("IP"))
        ip, port = (ip_plain.split(":", 1) + ["80"])[:2]
        use_https = False
    else:
        raise RuntimeError(f"Loxone Cloud DNS returned no open port for snr={snr}")

    ip_dash = ip.replace(".", "-")
    host = f"{ip_dash}.{snr}.dyndns.{datacenter}:{port}"
    return ResolvedHost(host=host, use_https=use_https)


def resolve_config(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve a config dict.

    If `host` is a Cloud DNS shorthand, replace it with the derived dyndns hostname.
    If raw doesn't specify use_https, adopt the resolved recommendation.
    """

    cfg = dict(raw or {})
    host_value = str(cfg.get("host") or "").strip()
    snr = _extract_snr(host_value)
    if not snr:
        return cfg

    resolved = resolve_cloud_dns_host(snr=snr)
    cfg["host"] = resolved.host

    # If config did not specify, set to the resolved scheme. If the user explicitly
    # sets use_https, keep it (they may want to force LAN HTTP while keeping snr around).
    if "use_https" not in cfg:
        cfg["use_https"] = resolved.use_https

    return cfg


def load_config_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return resolve_config(raw)
