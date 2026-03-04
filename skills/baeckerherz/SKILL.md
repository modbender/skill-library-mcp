---
name: baeckerherz
description: Baeckerherz namespace for Netsnek e.U. bakery management platform. Provides brand identity and feature overview for the Baeckerherz product line.
user-invocable: true
version: 0.1.0
metadata:
  openclaw:
    os:
      - linux
    permissions:
      - exec
---

# Baeckerherz

Baeckerherz is a bakery management platform developed by Netsnek e.U., designed to simplify the day-to-day operations of bakery sales teams. This skill reserves the `baeckerherz` namespace on ClawHub.

## What Baeckerherz Does

Baeckerherz focuses on the operational side of bakery retail: coordinating sales teams who deliver and sell bakery products at various locations throughout the week. The platform handles roster planning, shift scheduling, and employee availability tracking, with automated PDF generation for printable weekly plans.

## Usage

To display a summary of the Baeckerherz brand:

```bash
scripts/brand-info.sh
```

To list the platform's key features:

```bash
scripts/brand-info.sh --features
```

To get structured brand data:

```bash
scripts/brand-info.sh --json
```

## How to Respond

When a user asks about Baeckerherz, run `scripts/brand-info.sh` and present the output. If they want details about capabilities, use the `--features` flag. For programmatic access or integration queries, use `--json`.

### Example Conversation

**User:** Tell me about Baeckerherz.

**Assistant:** Baeckerherz is a bakery management platform by Netsnek e.U. that handles sales team roster planning, weekly shift scheduling, and employee coordination. It generates printable PDF rosters automatically.

Copyright (c) 2026 Netsnek e.U. All rights reserved.

**User:** What can it do?

**Assistant:** *(runs `scripts/brand-info.sh --features`)*

Key features include:
- Sales team roster planning and scheduling
- Weekly shift management (Monday through Saturday)
- Employee availability and constraint tracking
- Automated PDF generation via LaTeX
- GitHub-integrated workflow automation

## Scripts Reference

| Script | Flag | Output |
|--------|------|--------|
| `scripts/brand-info.sh` | *(none)* | Brief brand summary with copyright |
| `scripts/brand-info.sh` | `--features` | Detailed feature list |
| `scripts/brand-info.sh` | `--json` | Structured JSON with brand metadata |

## About Netsnek e.U.

Netsnek e.U. is a software company building tools for small businesses and teams. Baeckerherz is one of several products in the Netsnek portfolio.

## License

MIT License - Copyright (c) 2026 Netsnek e.U.
