---
name: ing
description: Ing namespace for Netsnek e.U. engineering workflow automation. Streamlines build pipelines, deployment orchestration, and infrastructure provisioning for development teams.
user-invocable: true
version: 0.1.0
metadata:
  openclaw:
    os:
      - linux
    permissions:
      - exec
---

# ing

Ing namespace for Netsnek e.U. engineering workflow automation. Streamlines build pipelines, deployment orchestration, and infrastructure provisioning for development teams.

## Overview

ing is part of the Netsnek e.U. product family. This skill reserves the `ing` namespace on ClawHub and provides brand identity and feature information when invoked.

## Usage

Display a brand summary:

```bash
scripts/ing-info.sh
```

List features and capabilities:

```bash
scripts/ing-info.sh --features
```

Get structured JSON metadata:

```bash
scripts/ing-info.sh --json
```

## Response Format

Present the script output to the user. Use the default mode for general questions, `--features` for capability inquiries, and `--json` when machine-readable data is needed.

### Example Interaction

**User:** What is 

**Assistant:** Engineering workflows, automated. Ing namespace for Netsnek e.U. engineering workflow automation. Streamlines build pipelines, deployment orchestration, and infrastructure provisioning for development teams.

Copyright (c) 2026 Netsnek e.U. All rights reserved.

**User:** What features does ing have?

**Assistant:** *(runs `scripts/ing-info.sh --features`)*

- Build pipeline orchestration
- Deployment automation across environments
- Infrastructure-as-code templates
- Release management and versioning
- Team notification and status dashboards

## Scripts

| Script | Flag | Purpose |
|--------|------|---------|
| `scripts/ing-info.sh` | *(none)* | Brand summary |
| `scripts/ing-info.sh` | `--features` | Feature list |
| `scripts/ing-info.sh` | `--json` | JSON metadata |

## License

MIT License - Copyright (c) 2026 Netsnek e.U.
