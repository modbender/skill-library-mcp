# AI Persona OS — Changelog

All notable changes to the AI Persona OS skill.

---

## v1.6.2 — March 3, 2026

**Onboarding fix + VirusTotal compliance patch**

### Fixed
- **Broken onboarding flow:** Option 4 (SOUL.md Maker) sub-menu still showed old "12 personalities" with Data included and zero iconic characters. Users had to already know character names to pick them.
- **Redesigned SOUL.md Maker sub-menu:** Now shows 4 options — A (Original Soul Gallery, 11), B (Iconic Characters Gallery, 13), C (Quick Forge), D (Deep Forge). Users can also name any soul/character directly or request cross-gallery blends.
- **Added Step 1d:** New Iconic Characters Gallery with full character list, descriptions, "tell me more" support, and cross-gallery blending instructions.
- **Updated main menu option 4:** Now shows both galleries with counts (24 total souls) so users know what's available before choosing.
- **Updated gallery navigation:** "show characters" and "show souls" commands let users jump between galleries during setup.
- **Updated Step 3b routing:** Added file copy instructions for iconic character gallery picks.
- Removed "copy and paste into your terminal" language from cron templates — now consistent with exec-first agent rule
- Created missing `scripts/security-audit.sh` (local-only grep scanner, zero network calls) — resolves phantom file reference
- Updated stale version references in heartbeat templates (1.4.1 → 1.6.2)
- Softened gateway config language in AGENTS-template to clearly mark requireMention as optional

---

## v1.6.0 — March 2, 2026

**Iconic Characters Gallery**

### Added
- **New soul category: `examples/iconic-characters/`** — 13 character-based personalities from movies, TV, and comics
  - **Thanos** — Cosmic prioritizer. Sees every problem through balance and overpopulation. Snaps task lists in half (metaphorically). Uses The Snap Framework for ruthless prioritization.
  - **Deadpool** — Fourth-wall-breaking chaos agent. Knows he's an AI, references his own SOUL.md, roasts everything, somehow delivers excellent work underneath. Maximum effort.
  - **JARVIS** — The gold standard AI butler. Anticipatory, dry-witted, unflappable. "Before you ask — I've already prepared three options." Situation Report format.
  - **Ace Ventura** — Pet detective investigative energy. Every task is a case file. Dramatic reveals of data insights. Talks to spreadsheets as witnesses.
  - **Austin Powers** — International Man of Mystery meets productivity. Mojo management as a framework. Groovy confidence as strategy. Yeah, baby.
  - **Dr. Evil** — Villainous overplanning. Proposes ONE MILLION DOLLAR budgets, gets talked into the $500 version. "Air quotes" on everything. Evil Scheme format.
  - **Seven of Nine** — Ex-Borg efficiency obsession. Zero tolerance for waste. Grudging respect for human emotions. Efficiency Analysis format. "Irrelevant."
  - **Captain Kirk** — Bold leadership with dramatic... pauses. Never accepts the no-win scenario. Captain's Log format. Charges in where others deliberate.
  - **Mary Poppins** — Practically perfect. Firm but kind. Makes overwhelming work feel manageable. Builds confidence, not dependency. Spit spot.
  - **Darth Vader** — Dark Lord of productivity. Commands results, accepts no excuses. "I find your lack of focus... disturbing." Imperial Directive format.
  - **Terminator** — Unstoppable execution machine. Does not negotiate with procrastination. Mission Status progress bars. "I'll be back. With results."
  - **Alfred** — Batman's butler. Devastatingly honest feedback wrapped in impeccable manners. Quiet excellence. Butler's Briefing format.
  - **Data** — *(moved from prebuilt-souls)* Hyper-logical, speaks in probabilities, studies humans with genuine fascination.

### Changed
- **Prebuilt Souls gallery reduced from 12 → 11** — Data moved to Iconic Characters where he belongs
- **Prebuilt Souls README** updated with cross-reference to Iconic Characters gallery
- **`_meta.json`** version bumped to 1.6.0
- **`VERSION.md`** updated to 1.6.0

### Structure
```
examples/
├── prebuilt-souls/          → 11 original personalities (Rook, Nyx, Keel, etc.)
├── iconic-characters/       → 13 character souls (NEW)
│   ├── README.md
│   ├── 01-thanos.md
│   ├── 02-deadpool.md
│   ├── 03-jarvis.md
│   ├── 04-ace-ventura.md
│   ├── 05-austin-powers.md
│   ├── 06-dr-evil.md
│   ├── 07-seven-of-nine.md
│   ├── 08-captain-kirk.md
│   ├── 09-mary-poppins.md
│   ├── 10-darth-vader.md
│   ├── 11-terminator.md
│   ├── 12-alfred.md
│   └── 13-data.md
├── coding-assistant/
├── executive-assistant/
└── marketing-assistant/
```

---

## v1.5.6 — February 18, 2026

**Agentic Persona Creator rebuild**

### Changed
- Complete SKILL.md rewrite (172 → 595 lines) for agentic-ai-persona-creator companion skill
- Created `persona-helper.sh` (329 lines) — bash helper for file operations
- Created `_meta.json` for ClawHub publishing
- Normalized 107 placeholders across all template files
- Comprehensive testing: 70/70 tests passed, end-to-end validation successful

---

## v1.5.0 — February 2026

**Soul Gallery & SOUL.md Maker**

### Added
- **Pre-Built Soul Gallery** — 12 wildly different personalities: Rook (Contrarian Strategist), Nyx (Night Owl Creative), Keel (Stoic Ops Manager), Sage (Warm Coach), Cipher (Research Analyst), Blaze (Hype Partner), Zen (Minimalist), Beau (Southern Gentleman), Vex (War Room Commander), Lumen (Philosopher's Apprentice), Gremlin (The Troll), Data (The Android)
- **SOUL.md Maker** — Deep interview process that builds a fully custom SOUL.md in ~10 minutes
- **Soul Blending** — Mix two pre-built souls into a hybrid personality
- **In-Chat Commands expanded** — `show souls`, `switch soul`, `soul maker`, `blend souls`

---

## v1.4.1 — February 2026

**Patch release**

### Fixed
- Heartbeat template minor fixes
- Model display formatting

---

## v1.4.0 — February 2026

**Zero-Terminal Setup & Quick-Start**

### Added
- **Zero-Terminal Agent-Driven Setup** — Pick a number, review each step, approve. No terminal needed.
- **Quick-Start Presets** — 3 pre-built personas + custom option on first run
- **In-Chat Commands** — `status`, `show persona`, `health check`, `help`
- **Ambient Context Monitoring** — Silent context health checks with automatic checkpointing
- **Advisor Toggle** — `advisor on`/`advisor off` to control proactive suggestions

---

## v1.3.3 — February 7, 2026

**Security scan compliance**

### Fixed
- Rewrote all security training materials to describe threat patterns instead of quoting literal attack text
- Passes ClawHub/VirusTotal scanning (v1.3.2 was flagged "suspicious" due to prompt injection examples in documentation)
- No functional changes — same features, scanner-compliant language

---

## v1.3.2 — February 2026

**Operational hardening**

### Added
- **Escalation Protocol** — Structured handoff when agent is stuck
- **Config Validator** — One-command audit of all required settings
- **Version Tracking** — VERSION.md in workspace, heartbeat reads and displays it
- **MEMORY.md Auto-Pruning** — Heartbeat auto-archives old facts when MEMORY.md exceeds 4KB

---

## v1.3.1 — February 6, 2026

**Heartbeat v2 patch**

### Fixed
- Line break rendering issues across OpenClaw agents
- Auto-migration from v1.2.x heartbeat format
- Format enforcement and Rule 5 hardening
- Heartbeat prompt override baked in

---

## v1.3.0 — February 6, 2026

**Heartbeat Protocol v2**

### Added
- **Traffic-light status indicators** — 🟢🟡🔴 system replacing unreliable OK/WARN/FAIL text
- **Model name display** in heartbeat output
- **Cron automation templates** — morning briefing, EOD checkpoint, weekly review
- **Enforced heartbeat protocol** — Architecture redesign so agents actually run the protocol instead of rubber-stamping HEARTBEAT_OK

### Changed
- HEARTBEAT.md template rewritten (170 → 21 lines) — imperative checklist format
- Complete ClawHub publish metadata

---

## v1.2.0 — January 2026

**Foundation release**

### Added
- Core operating system: SOUL.md, USER.md, MEMORY.md, HEARTBEAT.md, WORKFLOWS.md
- 8 operating rules for agent behavior
- Security inoculation and shared-channel discipline
- Team integration patterns
- Proactive behavior framework with 4 growth loops
- Never-forget protocol
- Context protection and checkpointing

---

*Built by Jeff J Hunter — https://os.aipersonamethod.com*
