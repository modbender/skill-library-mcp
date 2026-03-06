# ⚔️ War Room

**AI that argues back. Ships better.**

Multi-agent sessions with a built-in devil's advocate. Specialist agents collaborate in waves, a CHAOS agent attacks every decision, and 19 structured protocols force better thinking.

Free. Open source. MIT.

---

## What Happened

We ran the same project through a standard multi-agent session, then through War Room.

| | Standard | War Room |
|---|---|---|
| **Features** | 10 (over-scoped) | 8 (each justified) |
| **Cuts** | 0 features questioned | 6 cut (saved 5 dev-days) |
| **Risks** | Surface-level list | Root cause analysis + switch costs |
| **Timeline** | "16 days" (optimistic) | "18 days + buffer" (honest) |
| **Critical miss** | No auto-update | Auto-update moved INTO MVP |
| **Alternatives** | 0 explored | 3 counter-proposals, best kept as Plan B |

Same model. Same input. Different operating system.

---

## Quick Start

```bash
# 1. Initialize
bash skills/war-room/scripts/init_war_room.sh my-project

# 2. Write your brief
# Edit war-rooms/my-project/BRIEF.md — describe what you're building

# 3. Inject the DNA
# Copy skills/war-room/references/dna-template.md → war-rooms/my-project/DNA.md

# 4. Run it
# Tell your agent: "Run a war room on my-project"
```

The agent reads the skill, picks the right specialists, runs them in waves, unleashes CHAOS after each wave, and consolidates everything into a blueprint.

---

## How It Works

### Agents
You pick 4-13 specialists based on your problem:

| Role | When to use |
|------|-------------|
| **ARCH** | System architecture, tech choices |
| **PM** | Scope, requirements, roadmap |
| **DEV** | Implementation, code feasibility |
| **SEC** | Threats, compliance, privacy |
| **UX** | Interface, interaction design |
| **QA** | Testing, edge cases |
| **MKT** | Positioning, launch strategy |
| **RESEARCH** | Market/tech research, competitive |
| **FINANCE** | Costs, projections, pricing |
| **LEGAL** | Contracts, IP, regulatory |
| **CHAOS** | **Always. Non-negotiable.** |

Custom roles welcome: AI-ENG, AUDIO, DATA, OPS — whatever the problem needs.

### Waves
Agents don't all run at once. They run in dependency order:

```
Wave 1: Foundation (ARCH + SEC + PM)     → decisions that others depend on
Wave 2: Specialists (UX + AUDIO + AI)    → build on Wave 1 decisions
Wave 3: Builders (DEV + OPS)             → implement based on Wave 1+2
Wave 4: Validators (QA + MKT + CHAOS)    → stress-test everything
```

CHAOS shadows every wave. Not just the end.

### The CHAOS Agent
The devil's advocate. Attacks assumptions. Rates decisions:

- **SURVIVES** — withstands scrutiny
- **WOUNDED** — valid but has weaknesses
- **KILLED** — doesn't hold up, needs rethinking

CHAOS also produces **counter-proposals** — alternative approaches nobody considered.

---

## The Protocols

19 structured decision protocols across 4 pillars. Not suggestions — constraints that every agent must follow.

### Essential 7 (start here)

| Protocol | What it forces |
|----------|---------------|
| **Opposite Test** | State the opposite decision + its strongest argument |
| **Five Whys** | Dig to root cause, not symptoms |
| **Ignorance Declaration** | Declare KNOWN / UNKNOWN / ASSUMPTION before analyzing |
| **Via Negativa** | List 3 things to REMOVE before adding anything |
| **Plan B** | Every critical decision needs a backup + switch cost |
| **Pre-Mortem** | "How does this fail in production?" |
| **CHAOS** | Adversarial review of all decisions |

### Advanced 12 (power users)

The full DNA adds: Dialectic Obligation, Mirror Test, Ripple Analysis, Tension Map, Causal Chain Verification, Tempo Tagging, Create-Then-Constrain, Barbell Strategy, and Lessons Permanent.

Full protocol reference: [dna-template.md](references/dna-template.md)

---

## What It Produces

```
war-rooms/my-project/
├── BRIEF.md              ← Your project description
├── DNA.md                ← The operating protocols
├── DECISIONS.md          ← Append-only decision log
├── STATUS.md             ← Agent completion tracking
├── BLOCKERS.md           ← Issues requiring human input
├── TLDR.md               ← Executive summary
├── agents/
│   ├── arch/             ← Architecture specs
│   ├── pm/               ← Product requirements
│   ├── chaos/            ← Challenges + counter-proposals
│   └── [role]/           ← Any specialist
├── artifacts/
│   └── BLUEPRINT.md      ← Consolidated output
├── comms/                ← Inter-agent messages
└── lessons/              ← Post-mortem learnings
```

---

## When To Use It

**Use it when:**
- Decisions cost weeks of work if wrong
- You need multiple perspectives but don't have multiple people
- You need a PRD, architecture, or strategy that survives contact with reality
- You want to stress-test an existing plan before committing

**Don't use it when:**
- The task is simple and well-defined
- You need a quick answer, not deep analysis
- You've already decided and just need execution

---

## License

MIT. Use it, fork it, build on it.

---

> *"The unexamined life is not worth living."* — Socrates

> *"Wind extinguishes a candle and energizes fire."* — Nassim Taleb

> *"O melhor conhecimento é aquele que é passado adiante."* — Max Kleinz
