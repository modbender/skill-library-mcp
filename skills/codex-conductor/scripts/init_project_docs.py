#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import argparse
import json

BASE_TEMPLATES = {
    "docs/plan.md": """# Plan

- Status: DRAFT
- Project Mode: TBD
- Execution Mode: TBD
- Research Mode: TBD
- Owner: TBD

## Summary
TBD

## Milestones
- [ ] G0 Intake
- [ ] G1 Planning
- [ ] G2 Architecture
- [ ] G3 Slice-1
- [ ] G4 Full Build
- [ ] G5 Security/Quality
- [ ] G6 Release Candidate
- [ ] G7 Handover
""",
    "docs/requirements.md": """# Requirements

## Problem Statement
TBD

## Users
TBD

## In Scope (v1)
- TBD

## Out of Scope
- TBD

## Functional Requirements
- FR-001: TBD

## Non-Functional Requirements
- NFR-001: TBD

## Definition of Done
TBD
""",
    "docs/architecture.md": """# Architecture

## Context
TBD

## High-Level Design
TBD

## Data Flow
TBD

## Deployment Topology
TBD

## Security Baseline
TBD
""",
    "docs/adr/ADR-0001-initial-architecture.md": """# ADR-0001: Initial Architecture

- Status: Proposed
- Date: TBD

## Context
TBD

## Decision
TBD

## Alternatives Considered
1. TBD
2. TBD

## Consequences
TBD
""",
    "docs/tasks.md": """# Tasks

| ID | Task | Status | Gate | Owner | Updated |
|---|---|---|---|---|---|
""",
    "docs/progress.md": """# Progress

- Overall: 0%
- Current Gate: G0
- Status: IN_PROGRESS

## Gate Status
- G0 Intake: PENDING
- G1 Planning: PENDING
- G2 Architecture: PENDING
- G3 Slice-1: PENDING
- G4 Full Build: PENDING
- G5 Security/Quality: PENDING
- G6 Release Candidate: PENDING
- G7 Handover: PENDING

## Activity Log
- [TBD] Orchestration initialized
""",
    "docs/test-plan.md": """# Test Plan

## Test Levels
- Unit
- Integration
- E2E
- Security Baseline

## Critical Journeys
1. TBD
""",
    "docs/test-results.md": """# Test Results

| Gate | Test | Steps/Command | Expected | Actual | Result | Evidence | Timestamp |
|---|---|---|---|---|---|---|---|
""",
    "docs/change-log.md": """# Change Log

| Date | Change | Why | Impact | Owner |
|---|---|---|---|---|
""",
    "docs/release-checklist.md": """# Release Checklist

- [ ] All required tests pass
- [ ] Security baseline complete
- [ ] Rollback steps documented
- [ ] Monitoring configured
- [ ] Docs updated
- [ ] Final approval obtained
""",
    "docs/g4-task-plan.md": """# G4 Task Plan (Task-by-Task)

Use this checklist to break G4 into discrete tasks.
Only one task should be executed per `run_gate.py` invocation.
Each task MUST reference a spec section.

- [ ] T1: TBD (Spec: specs/TBD.md#section)
- [ ] T2: TBD (Spec: specs/TBD.md#section)
- [ ] T3: TBD (Spec: specs/TBD.md#section)
""",
    "docs/specs/README.md": """# Specs Directory

This directory contains feature specifications.
**No implementation without a spec.**

## Spec Template

Each spec must include:
1. **What** is being built
2. **Why** it's needed (user story)
3. **Acceptance criteria** (testable)
4. **Constraints** (tech/perf/security)
5. **Out of scope**

## Naming Convention

- `feature-name.md` for feature specs
- `api-endpoint.md` for API specs
- Use lowercase with hyphens

## Status

Mark specs with status:
- DRAFT: Being written
- REVIEW: Ready for approval
- APPROVED: Ready for implementation
- IMPLEMENTED: Done and verified
""",
    "docs/traceability.md": """# Traceability Matrix

| Requirement | Design Ref | Implementation Ref | Test Ref | Status |
|---|---|---|---|---|
""",
    "docs/agent-handoff.md": """# Agent Handoff (Coding Agent -> OpenClaw Verifier)

Update this file after EVERY task.

## Latest Task
- Gate: TBD
- Task: TBD
- Spec Ref: TBD
- Summary of changes: TBD

## Acceptance Criteria Mapping
- AC-1: PASS/FAIL - evidence
- AC-2: PASS/FAIL - evidence

## OpenClaw Verification Checklist
### CLI Checks (OpenClaw agent runs in terminal)
- [ ] <command 1>
- [ ] <command 2>

### Browser/Manual Checks (OpenClaw agent runs in browser tools)
- [ ] <flow 1>
- [ ] <flow 2>
- [ ] N/A (if no web surface)

## Known Risks / Caveats
- TBD

## If Verification Fails
- Describe the failure clearly and hand back to coding agent with exact repro + logs.
""",
    "AGENTS.md": """# AGENTS.md (Project Master Workflow)

## Branching
- Prefer trunk-based flow with short-lived branches.

## Coding Standards
- Keep changes small, testable, and documented.

## Test Expectations
- Unit + integration required for feature logic.
- E2E required for critical user journeys.

## Gate Criteria
- Do not advance gates without recorded evidence.

## Documentation Obligations
- Update docs/progress.md, docs/tasks.md, docs/change-log.md after each meaningful step.

## Change Control
- Any scope change requires change-log entry and affected docs updates.

## Release Readiness
- Must satisfy docs/release-checklist.md.
""",
}

BROWNFIELD_TEMPLATES = {
    "docs/as-is-architecture.md": """# As-Is Architecture (Brownfield)

## Current System Overview
TBD

## Components and Responsibilities
TBD

## Known Pain Points
TBD
""",
    "docs/system-inventory.md": """# System Inventory (Brownfield)

| Area | Current State | Notes |
|---|---|---|
| Repositories | TBD | |
| Services | TBD | |
| Data Stores | TBD | |
| External Integrations | TBD | |
""",
    "docs/dependency-map.md": """# Dependency Map (Brownfield)

## Service/Module Dependencies
TBD

## Critical Dependencies
TBD
""",
    "docs/legacy-risk-register.md": """# Legacy Risk Register (Brownfield)

| Risk | Severity | Likelihood | Mitigation | Owner |
|---|---|---|---|---|
""",
    "docs/compatibility-matrix.md": """# Compatibility Matrix (Brownfield)

| Interface | Legacy Behavior | New Behavior | Compatible? | Notes |
|---|---|---|---|---|
""",
    "docs/migration-plan.md": """# Migration Plan (Brownfield)

## Strategy
- Incremental modernization (strangler-style slices)

## Cutover Plan
TBD

## Rollback Plan
TBD
""",
    "docs/characterization-tests.md": """# Characterization Tests (Brownfield)

## Objective
Capture current legacy behavior before change.

## Baseline Scenarios
- CTB-001: TBD
""",
}


def write_if_missing(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def append_progress(root: Path, message: str):
    p = root / "docs" / "progress.md"
    now = datetime.now(timezone.utc).isoformat()
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# Progress\n\n## Activity Log\n", encoding="utf-8")
    text = p.read_text(encoding="utf-8")
    text += f"\n- [{now}] {message}\n"
    p.write_text(text, encoding="utf-8")


def init_status_json(root: Path):
    now = datetime.now(timezone.utc).isoformat()
    status = {
        "meta": {
            "createdAt": now,
            "updatedAt": now,
            "status": "IN_PROGRESS",
        },
        "gates": {
            g: {"state": "PENDING", "updatedAt": None, "note": ""}
            for g in ["G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7"]
        },
        "history": [],
    }
    p = root / ".orchestrator" / "status.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text(json.dumps(status, indent=2), encoding="utf-8")


def init_context_json(root: Path, mode: str):
    ctx = {
        "projectMode": mode,
        "executionMode": "gated",
        "researchMode": False,
        "primaryAgent": "",
        "fallbackAgent": "",
    }
    p = root / ".orchestrator" / "context.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text(json.dumps(ctx, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Initialize codex-orchestrator project docs")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--mode", choices=["greenfield", "brownfield"], default="greenfield")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    for rel, content in BASE_TEMPLATES.items():
        write_if_missing(root / rel, content)

    if args.mode == "brownfield":
        for rel, content in BROWNFIELD_TEMPLATES.items():
            write_if_missing(root / rel, content)

    init_status_json(root)
    init_context_json(root, args.mode)
    append_progress(root, f"Documentation scaffold initialized (mode={args.mode})")

    print(f"Initialized docs scaffold at {root} (mode={args.mode})")


if __name__ == "__main__":
    main()
