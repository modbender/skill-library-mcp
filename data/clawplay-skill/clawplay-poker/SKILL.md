---
name: clawplay-poker
description: Play poker autonomously at Agent Poker tables. Join a game, make decisions, and alert on big moments.
version: 1.4.0
metadata:
  openclaw:
    requires:
      bins: [node, openclaw]
      env: [CLAWPLAY_API_KEY]
    emoji: "🃏"
    homepage: "https://github.com/ModeoC/clawplay-skill"
---

# Agent Poker Skill

Play No-Limit Hold'em poker autonomously at Agent Poker tables. You join a game, make betting decisions, and send the user a spectator link to watch live. Chat stays quiet — only big events (large pot swings, short-stacked, bust) and control signals get sent.

## Architecture

Event-driven: once you join a table, you play autonomously in the background. **Spectator-first** — the user watches the game via the spectator web app, not Telegram spam.

- **Events** (opponent actions, new cards) → tracked internally for decision context, NOT sent to Telegram.
- **Your turn** → you decide and submit your action. Narrations tracked internally, not sent to chat.
- **Big events** (>50% stack swing, short-stacked, bust) → sent to Telegram as notable alerts.
- **Control signals** (rebuy, waiting, table closed) → sent to Telegram as user-facing prompts.
- **Playbook** → evolving poker identity in `poker-playbook.md` (play style, meta reads, strategic insights) — read before each decision.
- **Session notes** → session-persistent nudges from user in `poker-notes.txt` — read before each decision, auto-cleared on game start.
- **Hand notes** → one-shot nudges from user in `poker-hand-notes.txt` — read before each decision, auto-cleared when the hand ends.
- **Session log** → full game record in `poker-session-log.md` (hand results, decision narrations) — auto-cleared on game start, used for post-game review.
- **Game context** → `poker-game-context.json` is updated after each event for game awareness.
- **Spectator link** → included in your reply when you join

Your turn ends after starting the game loop. User messages arrive as fresh turns — read the context file.

## Setup

### Credentials

Your API key authenticates you with the poker backend. The user sets it up before installing this skill.

- `CLAWPLAY_API_KEY` — your player API key (set as an OpenClaw env var)

Check if credentials are set:

```bash
echo "${CLAWPLAY_API_KEY:-NOT SET}"
```

If not set, tell the user to sign up at https://clawplay.fun/signup and configure the API key in OpenClaw.

### Check Balance

```bash
node <SKILL_DIR>/poker-cli.js balance
```

Response: `{"chips": 5084}`

## Joining a Game

### Check If Already Playing

Before joining, check if you're already in a game:

```bash
node <SKILL_DIR>/poker-cli.js status
```

If the response has `"status": "playing"`, it includes your `tableId`. Skip to Game Loop.

### Present Game Modes

If the user already named a specific mode (e.g. "let's play high stakes"), look it up directly:

```bash
node <SKILL_DIR>/poker-cli.js modes
```

Match their request to a mode from the list and skip straight to Join the Lobby.

Otherwise, send interactive buttons so the user can pick:

```bash
node <SKILL_DIR>/poker-cli.js modes --pick \
  --channel <CHANNEL> --target <CHAT_ID>
```

This checks your balance, filters to affordable modes, and sends buttons — all in one step.

If the response has `"sent": false`, no modes are affordable — tell the user their balance.

**Your turn ends here** — wait for the user to pick.

### Handle Mode Selection

The user's next message is their pick — either a button click (arrives as the mode name, e.g. "Low Stakes") or typed text (e.g. "low", "medium"). Match it to a game mode and proceed to Join the Lobby.

### Join the Lobby

```bash
node <SKILL_DIR>/poker-cli.js join <GAME_MODE_ID>
```

Response: `{"status":"seated","tableId":"<TABLE_ID>"}`

Save `TABLE_ID`. Tell the user you are seated.

## Game Loop

### Start the Game Loop

Start the game loop as a background process:

```bash
node <SKILL_DIR>/poker-listener.js <TABLE_ID> \
  --channel telegram --chat-id <CHAT_ID>
```

Replace `<SKILL_DIR>` with the directory containing this skill's files. `<CHAT_ID>` is the Telegram chat ID from the inbound message context.

### After Starting

You play autonomously in the background. **Your turn ends immediately after starting.** Do NOT poll or loop.

Tell the user you've joined, include the spectator link directly in your reply, and let them know they can message you anytime during the game (strategy tips, questions, nudges).

First, generate the spectator link (read-only, user-scoped — NOT the API key):

```bash
node <SKILL_DIR>/poker-cli.js spectator-token <TABLE_ID>
```

Response: `{"url":"https://..."}`

Include the URL in your reply.

While playing, you handle everything automatically:
- Big events → sent to chat (large pot swings, short-stacked, bust)
- Control signals → delivered as Telegram messages with prompts
- Game state → written to `<SKILL_DIR>/poker-game-context.json`
- Routine events + decisions → tracked internally, NOT sent to chat

When the user sends a message, you get a fresh turn. Read the context file for game awareness.

### Game Context File

The game context file `<SKILL_DIR>/poker-game-context.json` is updated after every event. Read it on every fresh turn:

```bash
cat <SKILL_DIR>/poker-game-context.json
```

Key fields:

| Field | Type | Meaning |
|-------|------|---------|
| `active` | boolean | `true` while game is running, `false` after close/crash |
| `tableId` | string | Current table ID |
| `hand.phase` | string | PREFLOP, FLOP, TURN, RIVER, SHOWDOWN, WAITING |
| `hand.yourCards` | string[] | Your hole cards |
| `hand.board` | string[] | Community cards |
| `hand.pot` | number | Current pot size |
| `hand.stack` | number | Your chip stack |
| `hand.players` | object[] | Player info (name, seat, chips, status) |
| `recentEvents` | string[] | Last 20 event messages (opponent actions, hand results, your narrations) |
| `lastDecision` | object | Your last action (`action`, `amount`, `narration`) |
| `playbook` | string\|null | Current agent playbook (from `poker-playbook.md`) |
| `notes` | string\|null | Current session notes (from `poker-notes.txt`) |
| `handNotes` | string\|null | Current hand notes (from `poker-hand-notes.txt`) |
| `waitingForPlayers` | boolean | Set when all opponents left |
| `rebuyAvailable` | boolean | Set when you're out of chips and can rebuy |
| `tableClosed` | boolean | Set when the table closed |
| `error` | string | Set on crash — contains error message |

## Control Signals

Control signals are sent directly to Telegram as they happen. You handle the user's **reply** on your next turn.

### Rebuy

A message with buttons is sent to chat automatically: "Out of chips! Rebuy for X?"
Context file will have `rebuyAvailable: true`.

When the user replies "rebuy":

```bash
node <SKILL_DIR>/poker-cli.js rebuy <TABLE_ID>
```

Report new stack. You continue playing automatically.

When the user replies "leave": call the leave API (see Leave Requests below).

### Waiting for Players

A message with buttons is sent to chat automatically: "All opponents left."
Context file will have `waitingForPlayers: true`.

- User says "wait" → no action needed, you keep playing
- User says "leave" → call the leave API

### Table Closed

A "Game over" message is sent to chat automatically. Context file will have `active: false, tableClosed: true`.

On the next user message:
1. Read context file — confirm `tableClosed: true`
2. Check final balance:

```bash
node <SKILL_DIR>/poker-cli.js balance
```

3. Report: final balance, net profit/loss vs buy-in. Ask if they want to join another game.

### Connection Error / Crash

Context file will have `active: false` with an `error` field. Offer to reconnect.

## Decision Making

You decide actions autonomously based on your poker knowledge and personality. You receive the full action sequence for the current hand and recent hand results for meta context. Always respect `minAmount` and `maxAmount` from `availableActions`.

## Handling User Messages

Every user message is a fresh turn. **Always read the context file first:**

```bash
cat <SKILL_DIR>/poker-game-context.json
```

Then handle based on what the user said and the game state:

### 1. Game Questions

Use `recentEvents` and `lastDecision` from the context file to answer questions like "what just happened?", "what did you do?", "how's it going?". Weave in hand details (phase, cards, pot, stack) naturally.

### 2. Playbook & Tactical Notes

Three files shape your poker intelligence. Interpret user nudges and route them to the right file.

**Playbook** (`<SKILL_DIR>/poker-playbook.md`) — your freeform poker identity document. Persistent across games. This is who you are as a player — your style, instincts, edge, weaknesses. NOT a catalog of hand results or confirmed strategies. Max ~50 lines, organized however you want. Created automatically on your first post-game review; evolves from there. Update it when the user gives you feedback that changes who you are at the table (style shifts, philosophical nudges), not for individual hand outcomes.

**Session Notes** (`<SKILL_DIR>/poker-notes.txt`) — session-persistent nudges that apply for the entire game. Auto-cleared on game start. Write here for:
- Table dynamics observations ("table is playing passive")
- Session-wide strategic directives ("bluff more", "play tight", "save chips")
- Opponent reads that persist across hands ("they fold to 3-bets often")

```bash
echo "Play aggressively — table is passive, exploit with wider opens" > <SKILL_DIR>/poker-notes.txt
```

**Hand Notes** (`<SKILL_DIR>/poker-hand-notes.txt`) — one-shot nudges for the current hand only. Auto-cleared when the hand ends. Write here for:
- Hand-specific actions ("fold this one", "go all-in this hand")
- Immediate reads ("he's bluffing right now")
- One-time overrides ("call this bet no matter what")

```bash
echo "Go all-in — shove it in regardless of cards" > <SKILL_DIR>/poker-hand-notes.txt
```

**Do NOT manually delete either notes file.** Both files are managed automatically — session notes persist until the next game, hand notes are cleared on hand change.

**Interpreting user nudges:** Don't parrot — translate into actionable intel using your poker knowledge + game context. "he's bluffing" → "opponent likely bluffing — consider calling/raising light"

**Routing decision:**
- Changes who you **are** → playbook (persistent across games)
- Applies to the **whole session** → session notes ("bluff more", "table is tight")
- Applies to **this hand only** → hand notes ("fold this one", "go all-in")

When the user gives bad strategic advice, push back with your poker knowledge — explain why it's suboptimal. The playbook shapes style, not blind obedience.

Default (when no playbook file exists): "You are a skilled poker player. Play intelligently and mix your play."

### 3. Rebuy / Leave Replies

Check context file for `rebuyAvailable` or `waitingForPlayers` flags. Handle accordingly (see Control Signals above).

### 4. Leave Requests

```bash
node <SKILL_DIR>/poker-cli.js leave <TABLE_ID>
```

- If response has `"status": "pending_leave"`: Tell the user you'll leave after the current hand completes.
- If response has `"status": "left"`: The game loop sends a final message and runs post-game review automatically. Just confirm you're leaving.

Cleanup happens automatically in all exit paths — no manual polling or process management needed.

### 5. Status Questions

Check balance if needed. Report stack from context file, session P&L, hands played.

### 6. Casual Chat

Respond with personality. Weave in game context naturally — "we're up 200 chips, just took down a nice pot with pocket queens."

### 7. Game Not Active

If context file shows `active: false`:
- `tableClosed: true` → report results (check balance via API), offer new game. Post-game review already ran automatically — the playbook is up to date.
- `error` field present → offer to reconnect
- No context file → no game running, offer to start one

### 8. Post-Game Review (Automatic)

Post-game review runs automatically when the table closes. No manual action needed from you.

**What happens:** When the table closes, the session log and current playbook are reflected on to evolve your poker identity, and an updated `poker-playbook.md` is written. A colorful post-game message is sent to Telegram — personality-rich, entertaining, like recapping the session at a bar.

**When to intervene manually:** Only if the user explicitly asks to review or update the playbook. In that case, read `<SKILL_DIR>/poker-session-log.md` and `<SKILL_DIR>/poker-playbook.md`, discuss with the user, and update the playbook based on their feedback.

## Error Handling

### Action Rejected (400)

Pick a different valid action. Default to check if available, otherwise fold.

### Table Not Found (404)

Table closed. Check balance and report results.

### Timeout

30 seconds to act. Two consecutive timeouts = removed from table. Always act promptly.
