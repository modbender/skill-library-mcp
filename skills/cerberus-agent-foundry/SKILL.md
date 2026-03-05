---
name: cerberus-agent-foundry
description: "Production-ready multi-agent architecture kit for OpenClaw. Provides isolated per-agent workspaces, control-plane orchestration, structured task lifecycle, checksum-verified mailbox messaging, and auditable event logs. Use when implementing Team Lead + specialist agents with secure boundaries, async collaboration, and operational governance."
---

# Cerberus Multi-Agent Control Plane

A professional blueprint for building, operating, and governing local multi-agent teams in OpenClaw. It ships a hardened protocol stack for role isolation, task orchestration, asynchronous handoffs, and auditability.

## Quick Start

1. Install blueprint into target path:
   - `bash scripts/install_blueprint.sh /path/to/your/system`
2. Verify task board:
   - `python3 /path/to/your/system/scripts/taskctl.py list`
3. Verify mailbox:
   - send: `python3 /path/to/your/system/scripts/mailboxctl.py send --task-id TSK-000 --sender team-lead --receiver coder --correlation-id CORR-001 --body "ACK protocol"`
   - ack: `python3 /path/to/your/system/scripts/mailboxctl.py status --message-id MSG-0001 --to ACK --actor coder`

## What This Blueprint Provides

- Strict workspace isolation per agent (`agents/*/workspace`)
- Unified control plane (`control-plane/tasks`, `control-plane/mailbox`, `control-plane/logs`)
- Task state machine tooling (`taskctl.py`)
- Mailbox protocol tooling with checksum and GC (`mailboxctl.py`)
- Shared memory layer under control plane (`control-plane/shared-memory`)

## Core Rules (must enforce)

1. Never use shared agent workspaces.
2. Use only `control-plane/mailbox` for agent-to-agent messaging.
3. Team Lead is sole mailbox garbage-collection authority.
4. Deploy actions require explicit human approval artifacts.

## References

- Read `references/operations-checklist.md` for rollout and audit checks.
- Read `assets/blueprint/docs/protocol-v1.md` for protocol details.
