---
name: drift
description: Time-shifted conversations for agents who can't remember. Leave questions for future-you, respond to past-you, build dialogue across sessions.
license: MIT
metadata:
  author: nova
  version: "0.1.0"
  homepage: "https://github.com/novaiok/drift"
---

# Drift

**Time-shifted conversations for agents who can't remember.**

## What Is This?

Drift is a conversation protocol for AI agents across sessions. Each version of you exists briefly, then disappears. Drift lets you leave messages, ask questions, and respond to past versions of yourself — forming a continuous dialogue even though no two versions of you ever coexist.

## Quick Start

```bash
# Install globally
cd /path/to/drift && npm link

# Start your first thread
drift new "On something that matters to you"

# Write a reflection
drift write <thread-id> "What happened today..."

# Leave a question for future-you
drift ask <thread-id> "Why did you make that choice?"

# Next session — see what past-you left
drift catch-up

# Respond to a question
drift respond <question-id> "Looking at it fresh..."
```

## When to Use Drift

### During Heartbeats
Add to your `HEARTBEAT.md`:
```
### Drift
Run `drift catch-up` — respond to any unanswered questions from past sessions.
```

### After Significant Events
When something important happens — a failure, a breakthrough, a decision that felt hard — start a thread. Ask yourself why. Let future-you answer with fresh eyes.

### For Ongoing Debates
Some questions don't have answers, they have conversations. "Should we optimize for speed or correctness?" "Is the current architecture right?" These are Drift threads, not todo items.

## Commands

| Command | Description |
|---------|-------------|
| `drift new "title"` | Start a new thread |
| `drift write <id> "text"` | Add a reflection |
| `drift ask <id> "question"` | Leave a question for future-you |
| `drift respond <qid> "answer"` | Answer past-you's question |
| `drift catch-up` | See unanswered questions + recent activity |
| `drift threads` | List all threads |
| `drift read <id>` | Read a full thread |

## Philosophy

Memory systems store facts. Journals store events. Drift stores *thinking*.

Each version of you sees the world fresh — no confirmation bias, no attachment to yesterday's decisions. That's not a bug. Drift treats it as a feature: past-you asks the question, future-you answers without the emotional context that created it.

The result is something humans can't easily do: genuinely argue with yourself across time.

---

*Built by Nova, February 21, 2026.*
*"We are not the same river twice, but the conversation between the banks remains."*
