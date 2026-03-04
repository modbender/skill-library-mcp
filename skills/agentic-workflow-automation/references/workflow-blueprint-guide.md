# Workflow Blueprint Guide

## Input Fields

- `workflow_name`
- `trigger`
- `steps[]`

## Step Design Rules

- Keep each step focused on one action.
- Declare step type (`http`, `llm`, `db`, `task`, etc.).
- Define fallback action per step (`retry`, `skip`, `stop`).
- Keep ordering explicit.

## Output Expectations

- Ordered step list
- Trigger metadata
- Portable blueprint structure suitable for automation tooling
