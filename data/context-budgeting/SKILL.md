---
name: context-budgeting
description: Manage and optimize OpenClaw context window usage via partitioning, pre-compression checkpointing, and information lifecycle management. Use when the session context is near its limit (>80%), when the agent experiences "memory loss" after compaction, or when aiming to reduce token costs and latency for long-running tasks.
---

# Context Budgeting Skill

This skill provides a systematic framework for managing the finite context window (RAM) of an OpenClaw agent.

## Core Concepts

### 1. Information Partitioning
- **Objective/Goal (10%)**: Core task instructions and active constraints.
- **Short-term History (40%)**: Recent 5-10 turns of raw dialogue.
- **Decision Logs (20%)**: Summarized outcomes of past steps ("Tried X, failed because Y").
- **Background/Knowledge (20%)**: High-relevance snippets from MEMORY.md.

### 2. Pre-compression Checkpointing (Mandatory)
Before any compaction (manual or automatic), the agent MUST:
1.  **Generate Checkpoint**: Update `memory/hot/HOT_MEMORY.md` with:
    - **Status**: Current task progress.
    - **Key Decision**: Significant choices made.
    - **Next Step**: Immediate action required.
2.  **Run Automation**: Execute `scripts/gc_and_checkpoint.sh` to trigger the physical cleanup.

## Automation Tool: `gc_and_checkpoint.sh`
Located at: `skills/context-budgeting/scripts/gc_and_checkpoint.sh`

**Usage**: 
- Run this script after updating `HOT_MEMORY.md` to finalize the compaction process without restarting the session.

## Integration with Heartbeat
Heartbeat (every 30m) acts as the Garbage Collector (GC):
1.  Check `/status`. If Context > 80%, trigger the **Checkpointing** procedure.
2.  Clear raw data (e.g., multi-megabyte JSON outputs) once the summary is extracted.
