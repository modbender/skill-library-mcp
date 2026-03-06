---
name: Innovation Catalyst
description: Analyzes system state (memory, tools, events) and generates
  strategic innovation proposals to break evolution stagnation plateaus.
---

# Innovation Catalyst

Analyzes system state (memory, tools, events) and generates strategic innovation proposals to break evolution stagnation plateaus.

## Features

- **Gap Analysis:** Identifies under-represented skill categories.
- **Stall Detection:** Finds blocked tasks or recurring failures.
- **Strategic Proposals:** Generates actionable suggestions (new skills, optimizations, structural changes).
- **Feishu Integration:** Sends a rich Feishu card report.

## Usage

```bash
# Run manually
node skills/innovation-catalyst/index.js

# Target a specific user/group
node skills/innovation-catalyst/index.js --target "ou_xxx"
```

## Protocol Integration

This skill is designed to be triggered by the `gene_gep_innovate_from_opportunity` gene when `stable_success_plateau` is detected. It provides the "seed" for subsequent evolution cycles.

## Dependencies

- `skills/feishu-evolver-wrapper/feishu-helper.js` (for card sending)
- System memory files (`MEMORY.md`, `TOOLS.md`, `RECENT_EVENTS.md`)
