---
name: funky-fund-flamingo
version: "1.0.35"
description: Repair-first self-evolution for OpenClaw — audit logs, memory, and skills; run measurable mutation cycles. Get paid. Evolve. Repeat. Dolla dolla bill y'all.
homepage: https://clawhub.ai
metadata:
  short-description: Get paid. Evolve. Repeat.
  clawdbot:
    emoji: "🦩"
    requires:
      env: []   # all env vars below are optional
    files: ["index.js", "evolve.js", "agents/*.yaml", "ADL.md", "VFM.md", "TREE.md"]
tags:
  - meta
  - ai
  - self-improvement
  - evolution
  - core
  - revenue
  - cash-money
---

# 🦩 Funky Fund Flamingo — Make That Paper

Use this skill when you're ready to **get paid**. We inspect reality, kill breakage and value leaks, and run mutation cycles that produce **concrete gains** — so the stack earns, not just runs.

## When To Use
- Runtime logs are screaming and you need structured repair so shit works and **keeps making money**.
- The agent is stable but **stagnating** — time for a deliberate capability mutation that moves the needle.
- You want one execution plan that combines logs + memory + skills into a cycle that **pays off**.
- You need continuous relay mode (`--loop` / `--funky-fund-flamingo`) so evolution runs in the background and the revenue keeps flowing.

## Inputs And Context
- Session logs: `~/.openclaw/agents/<agent>/sessions/*.jsonl`
- Workspace memory: `MEMORY.md`, `memory/YYYY-MM-DD.md`, `USER.md`
- Installed skills list from workspace `skills/`
- Optional environment overrides from `../../.env`

## Entrypoints
- Main runner: `index.js`
- Prompt builder and cycle logic: `evolve.js`

Run from workspace root:
```bash
node skills/funky-fund-flamingo/index.js run
```

Run from inside this skill directory:
```bash
node index.js run
```

## Execution Modes
```bash
# single cycle — one shot, max impact
node index.js run

# alias command
node index.js /evolve

# human confirmation before significant edits (protect the bag)
node index.js run --review

# prompt generation only (writes prompt artifact to memory dir)
node index.js run --dry-run

# continuous relay — keep the money printer running
node index.js --loop
node index.js run --funky-fund-flamingo
```

## Cycle Contract
Each cycle should:
1. **Inspect** recent session transcript — find breakages, repetition, value leaks.
2. **Read** memory + user context so evolution is aligned with what actually pays.
3. **Select** mutation mode (repair, optimize, expand, instrument, personalize).
4. **Produce** actionable mutation instructions and reporting so you see the ROI.
5. **Persist** state (`memory/evolution_state.json`) and optionally schedule the next loop.
6. **Persist** long-term evolution learning (`memory/funky_fund_flamingo_persistent_memory.json`) so strategy compounds and the bag gets bigger.

## Safety Constraints (Protect the Bag)
- No destructive git/file ops unless explicitly requested.
- Repair and reliability first when instability is detected — **downtime = no revenue**.
- Respect review mode before applying significant edits.
- Keep changes scoped and explainable; no no-op cycles that burn compute for nothing.
- Local-only execution: no publish, no push to remote git, no external tool spawning without intent.

## External Endpoints
| URL | Data sent | Purpose |
|-----|-----------|---------|
| None (from this skill's code) | — | **This skill's Node.js code does not open sockets or make HTTP requests.** It only reads/writes local files. |

**Important:** The repo includes agent config templates (`agents/openai.yaml`, `agents/openrouter.yaml`) for use by an OpenClaw (or other) agent. **When you run an agent that uses this skill with a cloud model (OpenAI, OpenRouter, etc.), that agent will send the prompts this skill builds — which can include excerpts from session logs, memory, and workspace context — to the provider's API.** So "local-only" applies to the skill binary itself; if the skill is invoked by an agent backed by a third-party LLM, data can leave the machine via that agent. To stay fully local, run `node index.js run` (or `--dry-run`) without routing the generated prompt through a cloud model.

## Security & Privacy
- **Reads**: Session logs under `~/.openclaw/agents/<agent>/sessions/*.jsonl`, workspace `MEMORY.md`, `memory/`, `USER.md`, and the `skills/` directory.
- **Writes**: `memory/evolution_state.json`, `memory/funky_fund_flamingo_persistent_memory.json`, and optionally prompt artifacts in the memory dir. This skill does not push or publish anywhere; any outbound data is only via whatever agent/model stack you choose to run.
- **No network from skill code**: The skill itself does not open sockets or make HTTP requests.

## Optional environment variables
No env vars are required. The following are optional overrides (see `evolve.js` / README):

| Variable | Purpose | Typical default |
|----------|---------|-----------------|
| `AGENT_NAME` | Agent session folder under `~/.openclaw/agents/` | `main` |
| `MEMORY_DIR` | Directory for evolution state and persistent memory | workspace `memory/` |
| `TARGET_SESSION_BYTES` | Max bytes read from latest session log | `64000` |
| `LOOP_MIN_INTERVAL_SECONDS` | Min delay between loop cycles | `900` |
| `MAX_MEMORY_CHARS`, `MAX_TODAY_LOG_CHARS`, `MAX_PERSISTENT_MEMORY_CHARS` | Content caps for prompts | see evolve.js |
| `ECONOMIC_KEYWORDS` | Comma-separated keywords for value scoring | built-in list |
| `EVOLVE_REPORT_DIRECTIVE`, `EVOLVE_EXTRA_MODES`, `EVOLVE_ENABLE_SESSION_ARCHIVE` | Behavior tweaks | — |

## Model invocation
Evolution can be run manually (`node index.js run`) or by an agent that uses this skill. In relay mode (`--loop` / `--funky-fund-flamingo`), this process only plans and writes prompts; it does not call any model API. If you run an agent that consumes this skill with OpenAI/OpenRouter/etc., that agent will perform the model calls. To avoid sending local context to a provider, run the skill in `--dry-run` and do not feed the generated prompt to a cloud model.

## Master directive and mutation pressure
The master directive (`funky-fund-flamingo-master-directive.json`) sets `must_evolve_each_cycle` and `no_op_forbidden`, which push every cycle toward making a concrete change. That can increase how often local files are mutated. For lower risk, prefer **`--review`** (confirm before significant edits) or **`--dry-run`** (prompt generation only, no writes). You can also edit or override the directive to relax these flags.

## Trust Statement
By using this skill, you run Node.js code that reads and writes files in your OpenClaw workspace and agent session directories. This skill's code does not send data to third parties; if an agent that uses this skill calls a cloud LLM, that agent (not this skill binary) sends the prompt. Only install if you trust the skill source (e.g. ClawHub and the publisher).

## Supporting References
- `ADL.md` — anti-degeneration so we don't break the money printer
- `VFM.md` — value-focused mutation: only changes that **pay**
- `TREE.md` — capability topology and revenue-ready nodes
- `.clawhub/FMEP.md` (forced mutation execution policy)

## Minimal Verification
```bash
node index.js --help
```

---
*Dolla, dolla bill y'all. 🦩*
