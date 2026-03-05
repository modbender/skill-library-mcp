# 🦩 Funky Fund Flamingo

**Repair-first self-evolution for OpenClaw. Audit logs, memory, and skills — run measurable mutation cycles. Get paid. Evolve. Repeat. Dolla dolla bill y'all.**

[![ClawHub](https://img.shields.io/badge/ClawHub-funky--fund--flamingo-blue)](https://clawhub.ai)

Funky Fund Flamingo is a meta-skill that hardens and upgrades your agent continuously. It audits what actually happened, finds what failed, and drives repair-first mutation cycles so performance and value go up — and the stack is built to make that paper.

## What This Thing Does

- **Scans real session logs** (`.jsonl`) instead of guessing
- **Detects failure patterns**, repeated friction, and wasted motion
- **Repair-first** when instability spikes — downtime = no revenue
- **Forces mutation when stable** — stagnation is failure
- **Builds measurable evolution directives** from logs + memory + skills
- **Autonomous relay mode** (`--loop` / `--funky-fund-flamingo`)

## Install

### Via ClawHub (recommended)

```bash
clawhub install funky-fund-flamingo
```

Or with npx:

```bash
npx clawhub@latest install funky-fund-flamingo
```

**Canonical page:** https://clawhub.ai (search for `funky-fund-flamingo`)

### Manual

Copy the skill into your OpenClaw workspace:

```bash
cp -r skills/funky-fund-flamingo ~/.openclaw/workspace/skills/
```

From workspace root:

```bash
node skills/funky-fund-flamingo/index.js run
```

From inside the skill directory:

```bash
cd skills/funky-fund-flamingo && node index.js run
```

## Operating Modes

```bash
# single cycle — max impact
node index.js run

# alias
node index.js /evolve

# human checkpoint before major edits (protect the bag)
node index.js run --review

# prompt only, no full apply
node index.js run --dry-run

# continuous relay — keep the money printer running
node index.js --loop
node index.js run --funky-fund-flamingo
```

## Environment (optional)

| Env Var | Purpose | Default |
|---------|---------|---------|
| `AGENT_NAME` | Agent session folder under `~/.openclaw/agents/` | `main` |
| `MEMORY_DIR` | Daily memory and evolution state | `../../memory` |
| `TARGET_SESSION_BYTES` | Bytes read from latest session logs | `64000` |
| `LOOP_MIN_INTERVAL_SECONDS` | Min delay between loop cycles | `900` |

See `SKILL.md` for full list.

## Safety Rails

- **Local-only default** — no remote publish, no git push, no external tool spawning
- Repair beats novelty when error pressure is high
- Review mode (`--review`) pauses before significant edits
- Persistent state: `memory/evolution_state.json`, `memory/funky_fund_flamingo_persistent_memory.json`

## Skill Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Entry-point — when to use, cycle contract, safety |
| `ADL.md` | Anti-degeneration lock — protect the bag |
| `VFM.md` | Value function mutation — only changes that pay |
| `TREE.md` | Capability topology and revenue-ready nodes |
| `agents/*.yaml` | Agent configs (OpenAI, OpenRouter) |

## License

MIT

---

*Dolla, dolla bill y'all. 🦩*
