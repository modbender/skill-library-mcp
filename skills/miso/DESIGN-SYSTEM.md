# MISO Design System — Telegram Safe

## Principles
1. **Left-aligned** only. No space alignment.
2. **Emojis** carry structure. No box-drawing characters.
3. **`——————————————`** as separator (14 em-dashes).
4. **`↳`** for hierarchy.
5. **Unicode bold** for section names and agent names.
6. **Small caps** for footer.
7. **Reactions** for at-a-glance phase identification.

## Why These Rules?

Telegram renders messages differently across iOS, Android, macOS, and Web. Monospace is inconsistent, spaces collapse, and box-drawing characters break on mobile. MISO's design system avoids all known rendering pitfalls.

## 4+1 Layer UX Model

MISO uses a layered information architecture. Each layer has a different read speed and information density.

```
Layer 0  📌 Pin        → "Something is happening" (instant, chat open)
Layer 0.5 👀 ackReaction → "Message received" (instant, on receive)
Layer 1  🔥🎉❌ Reaction → "What state is it in" (instant, chat list)
Layer 2  Message body   → "Details and progress" (seconds, read)
Layer 3  Inline buttons → "Take action" (tap to interact)
```

### Layer 0: Pin (Existence)
- Pin = "A mission exists and is active"
- Unpin = "Mission is complete or aborted"
- Master ticket = permanent pin (mission dashboard)
- Individual missions = temporary pin (unpin on complete)

### Layer 0.5: ackReaction (Receipt)
- 👀 on every received message = "I got your message"
- Auto-removed after reply
- Fastest possible feedback loop
- Config: `messages.ackReaction: "👀"`, `messages.ackReactionScope: "all"`

### Layer 1: Reaction (State)
- 🔥 = Running/Active
- 👀 = Awaiting approval
- 🎉 = Complete
- ❌ = Error
- Visible from chat list without opening the message

### Layer 2: Message Body (Detail)
- Progress bars, agent status, thinking output
- Updated via message edit (single message, no spam)
- Contains cost, time, agent count

### Layer 3: Inline Buttons (Action)
- Approval gate: ✅ Approve / 👁 Preview / ✏️ Revise / ❌ Abort
- Error recovery: 🔄 Retry / ⏭ Skip / 📄 Partial complete / ❌ Abort

## Visual Elements

### Progress Bar
16 fixed segments using block characters:
```
░░░░░░░░░░░░░░░░  0%
▓▓▓▓░░░░░░░░░░░░  25%
▓▓▓▓▓▓▓▓░░░░░░░░  50%
▓▓▓▓▓▓▓▓▓▓▓▓░░░░  75%
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  100%
```
Formula: `filled = round(percent / 100 * 16)`

### Separator
```
——————————————
```
14 em-dashes (U+2014). Not hyphens. Not en-dashes.

### Hierarchy
```
↳ Subordinate item
```
Use `↳` (U+21B3) for indentation. Never use spaces or tabs.

### Section Headers
Use Unicode Mathematical Bold (U+1D5D4 range):
```
𝗠𝗜𝗦𝗦𝗜𝗢𝗡 𝗖𝗢𝗡𝗧𝗥𝗢𝗟
𝗔𝗚𝗘𝗡𝗧𝗦
𝗗𝗘𝗟𝗜𝗩𝗘𝗥𝗔𝗕𝗟𝗘𝗦
𝗞𝗘𝗬 𝗜𝗡𝗦𝗜𝗚𝗛𝗧𝗦
```

### Footer
Small caps for branding:
```
🌸 ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴍɪʏᴀʙɪ
```

### Status Icons

| State | Icon | Label |
|-------|------|-------|
| Initializing | ⏳ | INIT |
| Running | 🔥 | RUNNING |
| Writing | ✏️ | WRITING |
| Waiting | ⏸️ | WAITING |
| Done | ✅ | DONE |
| Error | ❌ | ERROR |
| Retry | 🔄 | RETRY |
| Awaiting Approval | ⏸️ | AWAITING APPROVAL |

### Strikethrough for Completion
Use Telegram `~text~` for completed tasks in WBS-style tickets:
```
~✅ Task 1 — Complete~
👉 🔥 Task 2 — IN PROGRESS
⬜ Task 3 — Not started
```

## Channel Integration

### Privacy Rules
Channel posts must NOT contain:
- 💰 Cost information
- ❌ Error details
- ⏸️ Approval gates
- 🧠 Agent thinking output

Channel receives only:
- 🚀 Mission started (description + agent count)
- ✅ Mission complete (description + key insights)

### Master Ticket (WBS Style)

Goal-driven structure with milestone tracking:

```
🎯 𝗚𝗢𝗔𝗟: {project goal}
——————————————

📌 𝗠𝗶𝗹𝗲𝘀𝘁𝗼𝗻𝗲 𝟭: {name}
~✅ T1: {task}~
~✅ T2: {task}~

📌 𝗠𝗶𝗹𝗲𝘀𝘁𝗼𝗻𝗲 𝟮: {name}
👉 🔥 T3: {task} — IN PROGRESS
⬜ T4: {task}

——————————————
Updated: {timestamp}
Next: {next milestone}
🌸 ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴍɪʏᴀʙɪ
```

## Forbidden Patterns

### ❌ Box-drawing characters
```
┏━━━━━━━━━━━━━━━━━━━━┓
┃  Breaks on mobile    ┃
┗━━━━━━━━━━━━━━━━━━━━┛
```

### ❌ Space alignment
```
Agent 1    ████░░░░  50%
Agent 2    ██░░░░░░  25%
```
Spaces render differently across clients.

### ❌ DAG ASCII art
```
    T1 ──┐
    T2 ──┼──→ T5 ──→ T6
    T3 ──┤
    T4 ──┘
```
Collapses on mobile. Use inline text instead: `T1-4 (parallel) → T5 → T6`

### ❌ Markdown tables
Tables don't render in Telegram. Use vertical lists instead.

## Tested Platforms
- ✅ Telegram iOS
- ✅ Telegram Android
- ✅ Telegram macOS
- ✅ Telegram Web
- ✅ Telegram Desktop (Windows/Linux)
