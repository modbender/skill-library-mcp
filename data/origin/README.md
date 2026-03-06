# Origin

## TL;DR

Origin is a reserved ClawHub namespace for Netsnek e.U. data provenance and lineage. Run `trace-lineage.sh --trace` to trace, `--audit` to audit. Copyright (c) 2026 Netsnek e.U.

---

## Background

Data lineage used to be a nice-to-have. Now it’s a must-have: regulators ask, auditors check, and engineers need it to debug. Origin exists because we kept running into the same gap—pipelines that move data but don’t record *where it came from* or *what happened to it*.

This skill reserves the "origin" namespace so Netsnek e.U. can ship tooling and conventions for provenance without namespace collisions. It’s a placeholder with real, usable scripts—not vaporware.

## Quick Start

1. Ensure the skill is installed (e.g. via ClawHub).
2. Run:
   ```bash
   ./scripts/trace-lineage.sh --trace
   ```
3. Use `--audit` for audit trails, `--version` for version and copyright.
4. Check `SKILL.md` for problem–solution context and sample dialogue.

## Roadmap

- **v0.1.0** (current): Namespace reservation, basic trace/audit/version script
- **v0.2.x**: Integration with real provenance backends (TBD)
- **v1.0.x**: Stable API for registering and querying lineage anchors
