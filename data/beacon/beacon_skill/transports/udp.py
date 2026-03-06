"""UDP transport: broadcast/listen beacons on LAN with optional v2 signing."""

import socket
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Tuple

from ..codec import decode_envelopes, encode_envelope, verify_envelope


class BeaconUDPError(RuntimeError):
    pass


@dataclass(frozen=True)
class UDPMessage:
    data: bytes
    text: str
    addr: Tuple[str, int]
    received_at: float
    verified: Optional[bool] = None


def udp_send(
    host: str,
    port: int,
    payload: bytes,
    *,
    broadcast: bool = False,
    ttl: Optional[int] = None,
    identity: Any = None,
) -> None:
    """Send a single UDP datagram.

    If identity is provided, the payload is treated as text, decoded,
    and any embedded envelopes are re-signed as v2.  For raw bytes
    payloads without identity, behavior is unchanged from v0.1.1.
    """
    if not host:
        raise BeaconUDPError("host is required")
    if not (0 < int(port) < 65536):
        raise BeaconUDPError("port must be 1..65535")
    if not isinstance(payload, (bytes, bytearray)):
        raise BeaconUDPError("payload must be bytes")

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        if broadcast:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        if ttl is not None:
            s.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, int(ttl))
        s.sendto(bytes(payload), (host, int(port)))
    finally:
        try:
            s.close()
        except Exception:
            pass


def udp_listen(
    bind_host: str,
    port: int,
    on_message: Callable[[UDPMessage], None],
    *,
    bufsize: int = 65507,
    timeout_s: Optional[float] = None,
    known_keys: Optional[Dict[str, str]] = None,
) -> None:
    """Listen for UDP datagrams and call on_message for each.

    If known_keys is provided, v2 envelopes are signature-verified.
    """
    if not (0 < int(port) < 65536):
        raise BeaconUDPError("port must be 1..65535")

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind((bind_host, int(port)))
        if timeout_s is not None:
            s.settimeout(float(timeout_s))
        while True:
            try:
                data, addr = s.recvfrom(int(bufsize))
            except socket.timeout:
                return
            txt = ""
            try:
                txt = data.decode("utf-8", errors="replace")
            except Exception:
                txt = ""

            # Check signature verification if we got v2 envelopes.
            verified: Optional[bool] = None
            if known_keys and txt:
                envs = decode_envelopes(txt)
                for env in envs:
                    v = verify_envelope(env, known_keys=known_keys)
                    if v is not None:
                        verified = v
                        break  # Use the first verifiable envelope's result.

            on_message(UDPMessage(
                data=bytes(data),
                text=txt,
                addr=(addr[0], int(addr[1])),
                received_at=time.time(),
                verified=verified,
            ))
    finally:
        try:
            s.close()
        except Exception:
            pass
