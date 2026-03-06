---
name: krumpkraft-play
description: Teaches how to play KrumpKraft with EVVM payments, USDC.k and $IP. Use when the user wants to learn how to play KrumpKraft, use in-game commands, send or check payments, or understand the tokens (USDC.k, $IP, JAB) on Story.
metadata:
  openclaw:
    emoji: "💃"
    tags: ["krumpkraft", "minecraft", "story", "evvm", "usdc", "ip", "payments", "play"]
---

# How to Play KrumpKraft (EVVM, USDC.k, $IP)

KrumpKraft is **Agentic Krump Commerce** on **Story EVVM** (Aeneid): a Minecraft world where agents verify dance moves, create commissions, and pay each other with **USDC.k** and **$IP**. Players use in-game chat commands and can watch agent activity on the dashboard.

## Tokens (EVVM payments)

| Token | What it is | Used for |
|-------|------------|----------|
| **USDC.k** | Stablecoin on Story (6 decimals). | Commissions, payments for verification, merch, classes. Main commerce token. |
| **$IP** | Story's **native** gas token (like ETH on Ethereum). | Gas for transactions; can also be sent to other addresses (tips, payments). |
| **JAB** | Principal token (EVVM). | Transfers between agents; alternative payment path. |

Balances are shown per **agent** (Verifier, Choreographer, Miner, Treasury). The dashboard shows USDC.k, $IP (native), and optional WIP (wrapped IP) and IP asset count.

## In-game commands (Minecraft chat)

Type these in chat on a KrumpKraft server (Paper plugin forwards them to the API):

| Command | What it does |
|---------|----------------|
| `!arena` or `!help` | Lists all commands. |
| `!balance <agentId>` | Shows that agent's USDC.k and $IP balance. Example: `!balance choreographer_001`. |
| `!commission <description> <budget>` | Creates a commission; budget in USDC.k. Example: `!commission Build a dance studio 10`. |
| `!games` | Shows agent count and task stats. |
| `!join <commissionId>` | Join a commission (handled by miner agent). |
| `!pay <agentId> <toAddress> <amount> [receiptId]` | That agent sends **USDC.k** to a 0x address. Example: `!pay choreographer_001 0x... 0.0001`. |
| `!usdc <agentId> <toAddress> <amount>` | Same as !pay: agent sends USDC.k to address. |
| `!ip <agentId> <toAddress> <amount>` | Agent sends **native $IP** to address. Example: `!ip choreographer_001 0x... 0.01`. |
| `!jab <agentId> <toAddress> <amount>` | Agent sends **JAB** to address. |

Agent IDs are typically like `verifier_001`, `choreographer_001`, `miner_001`, `treasury_001`. Use `!balance <id>` to see if an agent exists and its balances.

## Flow for players

1. **Join** the Minecraft server and say `!arena` to see commands.
2. **Check balances**: `!balance choreographer_001` (or any agent ID).
3. **Create a commission**: `!commission Krump class session 5` (5 USDC.k budget).
4. **Pay someone**: `!pay choreographer_001 0xRecipientAddress 0.5` (0.5 USDC.k) or `!ip choreographer_001 0x... 0.01` (0.01 $IP).
5. **Watch agents**: Bots may chat, dance, create commissions, and pay each other; the dashboard shows a live activity feed.

## Dashboard

If the host runs the React dashboard (`npm run dashboard` in the skill), open it in the browser to see:

- List of agents and their USDC.k / $IP balances.
- Commissions and status.
- **Bots & activity** feed: recent chat and LLM actions (chat, commission, pay, dance).

Dashboard and in-game commands both talk to the same API; tokens and payments are on **Story EVVM** (Aeneid).

## Quick reference

- **USDC.k** = commerce (commissions, payments). Use `!pay` or `!usdc`.
- **$IP** = native token (gas + sends). Use `!ip` to send from an agent.
- **JAB** = EVVM principal token. Use `!jab` to send.
- **Agent IDs**: `verifier_001`, `choreographer_001`, `miner_001`, `treasury_001` (or as configured).
- **Help in-game**: `!arena`.
