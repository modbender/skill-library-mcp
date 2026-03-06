# Buffer

**Your agent forgets everything between sessions.** It doesn't know what happened yesterday, what was decided, or what to do next. The context window fills up, memory bloats, and skills stop firing.

Buffer fixes this.

- **Session continuity** — sessions seamlessly pick up where the last one left off
- **Reliable skill execution** — agents use skills instead of forgetting about them
- **Lower token costs** — fewer wasted tokens means lower API bills

## Install

```bash
clawhub install buffer
```

Or clone and copy:

```bash
git clone https://github.com/sigmalabs-ai/buffer.git
cp -r buffer/buffer ~/.openclaw/workspace/skills/
```

Ask your agent to run buffer. On first run, it sets up your workspace and starts managing sessions immediately. It also extracts a companion audit skill (`buffer-optimizer`) for periodic workspace health checks.

## What Buffer Does

Buffer recovers context on start, monitors the context window during work, writes structured handoffs at the end, and periodically audits your workspace for problems that silently degrade performance.

- Reads HANDOFF.md on start so the agent knows where it left off
- Tracks context window usage and wraps before quality drops
- Enforces skill checkpoints so installed skills actually get used
- Keeps boot files, memory, and config lean through periodic audits

## How It Works

One install, two skills:

**`buffer`** is the runtime — it manages your sessions. Instant context recovery, context monitoring with research-backed thresholds, and structured wraps that bridge to the next session. Lightweight — loads every session with minimal overhead.

**`buffer-optimizer`** is the auditor — extracted automatically on first run. Measures boot payload, checks AGENTS.md structure, classifies skills, validates memory files. Run it when things feel off or every week or two.

```
[First Run]
    ↓
buffer → Extract buffer-optimizer → Setup workspace → Report
    ↓
[Every Session After]
    ↓
buffer (Start) → Read HANDOFF → Read MEMORY → Orient
    ↓
buffer (Monitor) → Intake discipline, thresholds, degradation signals
    ↓
buffer (Wrap) → Extract outcomes → Write HANDOFF → Update MEMORY if needed
    ↓
[Session Ends]
    ↓
[Next Session] → buffer reads what the last session wrote
```

## Research

Buffer's thresholds and degradation model are informed by:

- [Context Rot — Chroma Research](https://research.trychroma.com/context-rot) (July 2025)
- [How Long Contexts Fail — Drew Breunig](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html) (June 2025)

## Requirements

- OpenClaw with workspace file support
- File system + shell access
- No external dependencies
- Works with any model and context window size

## License

Apache 2.0
