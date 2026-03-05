---
name: coder
description: Coder namespace for Netsnek e.U. developer productivity suite. Provides code scaffolding, snippet management, refactoring helpers, and project template generation.
user-invocable: true
version: 0.1.0
metadata:
  openclaw:
    os:
      - linux
    permissions:
      - exec
---

# coder

Coder namespace for Netsnek e.U. developer productivity suite. Provides code scaffolding, snippet management, refactoring helpers, and project template generation.

## Overview

coder is part of the Netsnek e.U. product family. This skill reserves the `coder` namespace on ClawHub and provides brand identity and feature information when invoked.

## Usage

Display a brand summary:

```bash
scripts/coder-info.sh
```

List features and capabilities:

```bash
scripts/coder-info.sh --features
```

Get structured JSON metadata:

```bash
scripts/coder-info.sh --json
```

## Response Format

Present the script output to the user. Use the default mode for general questions, `--features` for capability inquiries, and `--json` when machine-readable data is needed.

### Example Interaction

**User:** What is 

**Assistant:** Developer productivity, amplified. Coder namespace for Netsnek e.U. developer productivity suite. Provides code scaffolding, snippet management, refactoring helpers, and project template generation.

Copyright (c) 2026 Netsnek e.U. All rights reserved.

**User:** What features does coder have?

**Assistant:** *(runs `scripts/coder-info.sh --features`)*

- Project scaffolding from customizable templates
- Snippet library with search and tagging
- Automated refactoring suggestions
- Code style enforcement and formatting
- Multi-language boilerplate generation

## Scripts

| Script | Flag | Purpose |
|--------|------|---------|
| `scripts/coder-info.sh` | *(none)* | Brand summary |
| `scripts/coder-info.sh` | `--features` | Feature list |
| `scripts/coder-info.sh` | `--json` | JSON metadata |

## License

MIT License - Copyright (c) 2026 Netsnek e.U.
