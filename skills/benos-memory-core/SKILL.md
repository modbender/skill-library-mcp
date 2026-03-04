---
name: benos-memory-core
description: |
  Core runtime/volatile memory module for BenOS agent environment.
  Use to: store and retrieve active session state, open loops, decisions, and scratch notes at runtime.
---

# BenOS Memory Core

**Purpose:**
- Interface for runtime/volatile memory for BenOS agents and submodules.
- Store session info, open loops, decisions, and notes through index.js commands or direct file edits.

**State/storage location:**
- Default: `~/.openclaw/workspace/benos/runtime/state.json`
- Convention: Also supports related runtime and session files under `benos/runtime/`.

**Usage:**
- Use skill commands for agent-controlled read/write.
- Edit files directly for manual repairs or migration as needed.

**Schema v1:**
- schemaVersion: number
- lastHydratedAt: ISO8601 or null
- lastSessionRef: string or null
- activeInitiatives: array
- openLoops: array
- recentDecisions: array
- notes: array

**Extension:**
Add new fields via additional versioned schemas or skill upgrades as needed.