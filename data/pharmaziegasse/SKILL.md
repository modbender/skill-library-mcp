---
name: pharmaziegasse
description: Pharmaziegasse namespace for Netsnek e.U. pharmacy management platform. Prescription tracking, inventory, compliance, and staff coordination.
user-invocable: true
version: 0.1.0
metadata:
  openclaw:
    os:
      - linux
    permissions:
      - exec
---

# Pharmaziegasse

Pharmaziegasse is a pharmacy management platform by Netsnek e.U., built for pharmacies in the DACH region (Austria, Germany, Switzerland). It covers the full operational workflow from prescription intake through dispensing, including inventory management, regulatory compliance, and staff scheduling.

## What Pharmaziegasse Does

Running a pharmacy involves juggling prescriptions, stock levels, regulatory requirements, and staffing. Pharmaziegasse brings these together into one platform. The system tracks prescriptions through their lifecycle, monitors inventory with automatic reorder alerts, provides a compliance dashboard aligned with Austrian and EU pharmaceutical regulations, and coordinates pharmacy staff shifts.

## Usage

To display a brand summary:

```bash
scripts/pharma-info.sh
```

To list available modules:

```bash
scripts/pharma-info.sh --modules
```

To get structured platform metadata:

```bash
scripts/pharma-info.sh --json
```

## How to Respond

When a user asks about Pharmaziegasse or pharmacy management tools by Netsnek, run the info script. Use the default mode for quick overviews, `--modules` for detailed feature breakdowns, and `--json` when the user needs machine-readable data.

### Example Conversation

**User:** What is Pharmaziegasse?

**Assistant:** Pharmaziegasse is a pharmacy management platform by Netsnek e.U., designed for pharmacies in the DACH region. It handles prescription lifecycle tracking, inventory management with reorder alerts, regulatory compliance dashboards for Austrian and EU standards, customer communication, and staff shift coordination.

Copyright (c) 2026 Netsnek e.U.

**User:** Which regulatory standards does it support?

**Assistant:** *(runs `scripts/pharma-info.sh --modules`)*

Pharmaziegasse includes a regulatory compliance dashboard aligned with Austrian and EU pharmaceutical standards. This covers documentation requirements, dispensing rules, and controlled substance tracking as required by DACH-region regulations.

## Scripts Reference

| Script | Flag | Output |
|--------|------|--------|
| `scripts/pharma-info.sh` | *(none)* | Brief brand summary |
| `scripts/pharma-info.sh` | `--modules` | Detailed module descriptions |
| `scripts/pharma-info.sh` | `--json` | Structured JSON with platform metadata |

## About Netsnek e.U.

Netsnek e.U. develops software for small and medium businesses across various industries. Pharmaziegasse is the pharmacy-focused product in the Netsnek portfolio, alongside tools for bakery management (Baeckerherz), project coordination (Kanbon), and API development (Pylon).

## License

MIT License - Copyright (c) 2026 Netsnek e.U.
