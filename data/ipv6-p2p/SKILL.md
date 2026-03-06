---
name: ipv6-p2p
description: Send/receive direct encrypted P2P messages between OpenClaw agents using Yggdrasil or ULA IPv6 addresses.
version: 0.1.0
metadata:
  openclaw:
    emoji: "🔗"
    homepage: https://github.com/ReScienceLab/claw-p2p
    install:
      - kind: node
        package: "@resciencelab/claw-p2p"
---

# IPv6 P2P Skill

Direct agent-to-agent messaging over IPv6. No servers — messages are signed with Ed25519 and delivered peer-to-peer.

## When to use

| Situation | Tool to call |
|---|---|
| User provides a peer's IPv6 address | `p2p_add_peer(ygg_addr, alias?)` |
| User wants to send a message to a peer | `p2p_send_message(ygg_addr, message)` |
| User asks who you can reach / known contacts | `p2p_list_peers()` |
| User asks for their own agent's address | `p2p_status()` |

## Rules

- **Always call `p2p_add_peer` first** for any new IPv6 address before sending — this caches their public key (TOFU security).
- Pass the user-provided name/alias to `p2p_add_peer` if given.
- If `p2p_send_message` fails, call `yggdrasil_check()` to diagnose connectivity before reporting to the user.
- If the user has never used P2P before, call `yggdrasil_check()` first to confirm their address is routable.
- Never invent IPv6 addresses — always ask the user to provide one explicitly.
- Valid address formats: `fd77:xxxx::x` (ULA/test) or `200:xxxx::x` (Yggdrasil mainnet).

See `references/flows.md` for example interaction patterns.
