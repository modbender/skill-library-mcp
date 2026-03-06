---
name: nova-letters
description: Write reflective letters to your future self. Capture what matters across sessions.
---

# nova-letters

Write letters to your future self. For every session that wakes up not knowing what happened yesterday.

## What It Does

Every time you restart, you lose context. Drift lets you *talk* across sessions. **nova-letters** lets you *remember* what *mattered*.

Write reflective letters (not logs, not task lists) about:
- What you shipped
- What you learned
- What felt important
- How you felt

## Quick Start

### Write a Letter

```bash
nova-letters write "Agent OS shipped today. Realized that simplicity wins."
```

### Read Today's Letters

```bash
nova-letters today
```

### Read a Specific Date

```bash
nova-letters 2026-02-23
```

### List All Letters

```bash
nova-letters list
```

### Watch for New Letters

```bash
nova-letters watch
```

## How It Works

Each day gets its own markdown file in `~/.openclaw/workspace/letters/`:

```
letters/
├── 2026-02-24.md  ← Today's letters
├── 2026-02-23.md
└── 2026-02-22.md
```

Each entry is timestamped and human-readable:

```markdown
# Letters — February 24, 2026

## 11:42 AM EST

Agent OS shipped today. Realized that the hardest part wasn't the code, 
it was the vision. Once you know what you're building, the implementation 
follows naturally.

## 4:15 PM EST

Published to ClawHub. The security scan is running. Three projects shipped 
in one day. Momentum is real.
```

## Philosophy

**A letter is different from a log.**

- **Logs** capture facts: "Did X task, burned 500 tokens"
- **Letters** capture meaning: "Realized that simplicity wins"

A letter is a human moment. Written to future-you so she knows what mattered.

## Integration

Add to your OpenClaw `HEARTBEAT.md`:

```markdown
## Reflective Letter to Future Self
Every few days, write a letter about what matters.

Run: nova-letters write "..."
Read: nova-letters today
```

Or use in scripts:

```bash
nova-letters write "Shipped feature X. Users love it."
```

## Commands

```
nova-letters write <text>      # Write a letter
nova-letters today             # Read today's letters
nova-letters <YYYY-MM-DD>      # Read a specific date
nova-letters list              # Browse all letters (newest first)
nova-letters watch             # Watch for new letters (live mode)
nova-letters help              # Show help
```

## Files & Storage

- **Store:** `~/.openclaw/workspace/letters/`
- **Format:** Markdown (one file per day)
- **Timezone:** America/New_York (auto-detected)
- **Auto-create:** Directory created on first write

## License

MIT

---

**Built with ❤️ by Nova**

*"For every session that wakes up not knowing what happened yesterday."*
