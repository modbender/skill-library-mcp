# Changelog

## v1.0.0 (2026-02-17)

### 🍜 Initial Release

**MISO — Mission Inline Skill Orchestration**
The world's first Telegram-native Agentic UI framework.

#### Features
- **4+1 Layer UX Model** — Pin → ackReaction → Reaction → Message → Buttons
- **6 Phase Lifecycle** — INIT → RUNNING → PARTIAL → AWAITING APPROVAL → COMPLETE → ERROR
- **WBS Master Ticket** — Goal-driven task management with strikethrough completion
- **Hybrid Pinning** — Master ticket (persistent) + individual missions (temporary)
- **Channel Integration** — Auto-post mission start/complete to @MIYABI_CHANNEL
- **Human-in-the-Loop** — Inline button approval gates for irreversible operations
- **Error Recovery UI** — Retry / Skip / Partial Complete / Abort buttons
- **Design System** — Telegram-safe visual language (no box-drawing, left-align only)
- **Bot API Helper** — `miso_telegram.py` for pin/unpin automation

#### Files
- `SKILL.md` — Main skill definition (6 phase templates)
- `DESIGN-SYSTEM.md` — Telegram-safe design system (4+1 layer)
- `README.md` — ClawHub-ready documentation
- `MISO.md` — Concept & philosophy
- `MASTER-TICKET.md` — State management spec
- `SPAWN-INTEGRATION.md` — OpenClaw spawn integration
- `CHANNEL-INTEGRATION.md` — Channel broadcast rules
- `examples/EXAMPLES.md` — 4 complete use cases
- `scripts/miso_telegram.py` — Pin/unpin helper

#### Roadmap
- v1.1: 🎙️ Narrated Mode (real-time commentary during missions)
- v1.2: miso-orchestrator (auto spawn + board updates)
- v1.3: miso-planner (task decomposition)

---

*Simple ingredients. Rich flavor.* 🍜
*By Shunsuke Hayashi + Miyabi 🌸*
