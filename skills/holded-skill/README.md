# holded-skill

`holded-skill` is an AI skill that operates Holded ERP through [`holdedcli`](https://github.com/jaumecornado/holdedcli).

It supports:

- Reading ERP data (contacts, invoices, products, CRM, projects, team, accounting)
- Updating ERP data through Holded API actions
- Safe execution with structured command output (`--json`)
- Action discovery and parameter inspection before execution (`actions list` + `actions describe`)
- Purchase receipt handling: enforce `docType=purchase` and `"isReceipt": true`

## Safety Policy

This skill always asks for explicit user confirmation before any write operation (`POST`, `PUT`, `PATCH`, `DELETE`).

No write command should run without a clear affirmative confirmation from the user.

This skill also verifies action availability and accepted parameters before execution using:

- `holded actions list`
- `holded actions describe <action> --json`

## Repository Structure

- `SKILL.md`: Core behavior, workflow, and mandatory confirmation protocol
- `agents/openai.yaml`: Skill UI metadata and default prompt
- `references/holdedcli-reference.md`: Quick command reference and OpenClaw config example

## OpenClaw

This repository is designed to be used directly as an OpenClaw skill repository with `SKILL.md` at the root.

The skill metadata includes:

- Skill name: `holded-skill`
- Homepage: `https://github.com/jaumecornado/holded-skill`
- Required binary: `holded`
- Primary environment variable: `HOLDED_API_KEY`
