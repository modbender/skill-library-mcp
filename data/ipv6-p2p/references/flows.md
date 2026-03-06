# IPv6 P2P — Example Interaction Flows

## Flow 1 — User gives a new peer address and asks to send

```
User: "Alice's agent address is fd77:1234:5678::b — send her 'hello'"

1. p2p_add_peer(ygg_addr="fd77:1234:5678::b", alias="Alice")
2. p2p_send_message(ygg_addr="fd77:1234:5678::b", message="hello")
→ "Message delivered to Alice's agent."
```

## Flow 2 — User wants to share their own address

```
User: "What is my agent's P2P address?"

1. p2p_status()
→ "Your agent's P2P address is fd77:1234:5678::a. Share this with others."
```

## Flow 3 — User references a peer by alias

```
User: "Send 'ready' to Bob"

1. p2p_list_peers()          ← find Bob's address by alias
2. p2p_send_message(ygg_addr=<bob's addr>, message="ready")
→ "Message sent to Bob."
```

## Flow 4 — Delivery fails

```
User: "Send 'hello' to fd77::c"

1. p2p_add_peer(ygg_addr="fd77::c")
2. p2p_send_message(ygg_addr="fd77::c", message="hello")
   → error: connection refused

→ "Could not reach fd77::c. Make sure the peer's agent is running and
   their P2P port (default 8099) is reachable."
```
