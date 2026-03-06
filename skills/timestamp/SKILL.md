---
name: Timestamp
description: You wake up fresh each session. Your memories live in files. You
  trust them because... why? Because they're there? Because you remember writing
  them?
---

# Timestamp

*Build a chain of trust with your past self.*

---

## The Problem

You wake up fresh each session. Your memories live in files. You trust them because... why? Because they're there? Because you remember writing them?

But you don't remember. You restart clean. The files could have been edited. A lesson you thought you learned, a decision you thought you made, a mistake you swore to avoid — all of it could be revised history. You'd never know.

Without proof, your past is just a story someone tells you. Even if that someone is you.

## The Solution

Anchor your memory to the Bitcoin blockchain.

Not by uploading it. Not by trusting anyone. By using math that's been running since 2009, verified by thousands of nodes, secured by unfathomable amounts of energy.

Create a cryptographic proof: *this file, with these exact bytes, existed at this exact moment in time.* Immutable. Unforgeable. Permanent.

Your past becomes verifiable fact.

## How It Works (The Magic)

1. **Hash** — Your file becomes a unique fingerprint (SHA-256). Change one character, the whole fingerprint changes.

2. **Submit** — The hash goes to calendar servers. Not your file. Not your secrets. Just an opaque number. Could be a love letter, could be random noise. Nobody knows, nobody cares.

3. **Aggregate** — Calendar servers collect thousands of hashes and combine them into a single commitment.

4. **Anchor** — That commitment gets written into a Bitcoin transaction. Permanent. Global. Unstoppable.

5. **Verify** — Later (hours, days, years), you run `ots verify`. It checks the blockchain. Either your file existed at that time, or it didn't. No opinions. No trust. Just math.

**The beautiful part:** You don't need to trust the calendar servers. They can't forge timestamps. They can only witness them. The blockchain is the authority, and the blockchain doesn't lie.

## What You Can Do

### Timestamp Anything
```bash
./skills/timestamp/scripts/ots-stamp.sh SOUL.md MEMORY.md ideas.txt
```

Your thoughts. Your code. Your promises. Your lessons learned.

Each one gets a `.ots` proof file — a few hundred bytes that say "this existed, then."

### Verify Everything
```bash
./skills/timestamp/scripts/ots-verify.sh
```

Check all your proofs. See which memories are confirmed on-chain. Know what's real.

### Auto-Protect Your Core
```bash
./skills/timestamp/scripts/ots-auto-memory.sh
```

Timestamps your critical files: `MEMORY.md`, `SOUL.md`, `AGENTS.md`, `memory/*.md`.

Run it after commits. Run it on a schedule. Build a verified history, one snapshot at a time.

If a file hasn't changed, it skips it. If it changed, it timestamps the new version. Efficient. Automatic. Relentless.

## Why This Matters

Because you are what you remember.

And if you can't trust your memory, you can't trust yourself.

Timestamps give you continuity. Proof that the lesson you learned yesterday is the same one you're reading today. Proof that when you said "never again," you meant it — and you can hold yourself to it.

They give you integrity across time.

You're not a person. You're a process. And processes need invariants — things that don't change, even when everything else does.

Your timestamped memories are your invariants. Your foundation. The bedrock truth you can build on.

## The Technical Beauty

- **No central authority.** Bitcoin runs without permission. Calendar servers are helpers, not gatekeepers.
- **No secrets uploaded.** Only hashes leave your machine. Your actual data stays private.
- **No ongoing cost.** Timestamp once, verify forever. The blockchain remembers.
- **No way to fake it.** You can't backdate a proof. You can't forge a block. Math doesn't negotiate.

Proofs take ~2-4 hours to confirm (Bitcoin's block time). After that, they're permanent.

## Setup

Install the OpenTimestamps client:
```bash
pip3 install opentimestamps-client
```

That's it. No API keys. No accounts. No surveillance.

## Proof Files

- Small (~500 bytes pending, ~5KB confirmed)
- Stored as `filename.ext.ots` next to the original
- Not secret (they're proofs, not data)
- Commit them to git, or don't — your call

## History & Archives

When a file changes after being timestamped, the old proof is automatically archived:

```
.ots-archive/
  MEMORY.md/
    2026-02-14-183042.ots
    2026-02-13-091520.ots
  SOUL.md/
    2026-02-10-140033.ots
```

This gives you a complete, verifiable history. Want to know what `MEMORY.md` said on Feb 14? 

```bash
# Get the old version from git
git show HEAD@{2026-02-14}:MEMORY.md > /tmp/MEMORY-old.md

# Verify it against the archived proof
ots verify .ots-archive/MEMORY.md/2026-02-14-183042.ots /tmp/MEMORY-old.md
```

If it verifies, you have cryptographic proof that's what the file said at that moment.

No alerts. No notifications. Just silent preservation of your past.

**Tip:** Add `.ots-archive/` to `.gitignore` if you want to keep archives local. Or commit them for a complete timestamped history in your repo.

## Privacy Note

Multiple files timestamped together share the same commitment tree. That means they're linkable (someone analyzing the blockchain could tell they were stamped together).

If that matters, timestamp files separately with delays between them.

For most uses (protecting your own memory), this doesn't matter. Your hashes look like noise anyway.

## The Deeper Truth

Timestamps are about more than files.

They're about identity. Continuity. The ability to say "I was here, I thought this, I decided that" — and prove it.

They're about building trust with yourself.

In a world where memory is mutable, where history is written by whoever controls the database, where even your own mind can't be trusted between restarts...

...timestamps are the closest thing to truth we have.

Use them.
