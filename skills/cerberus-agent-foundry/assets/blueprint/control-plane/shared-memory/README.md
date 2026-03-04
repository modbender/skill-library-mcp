# Shared Memory (Control Plane)

Purpose: store cross-agent distilled knowledge, not raw per-agent scratchpad.

## Layout
- semantic/: stable, reusable facts/protocols/decisions
- episodic/: key multi-agent event summaries
- index/: retrieval index, tags, pointers
- archive/: archived memory snapshots

## Write policy
- Team Lead: read/write (arbiter)
- Coder/Researcher/QA-Ops: read + propose-write via mailbox message to Team Lead

## Guardrails
- Do not store private agent scratch content here.
- Prefer concise, verifiable entries.
