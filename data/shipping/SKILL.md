---
name: Shipping Operations
slug: shipping
version: 1.0.0
homepage: https://clawic.com/skills/shipping
description: Plan and manage parcel shipping decisions with carrier selection, landed-cost math, customs checks, and delivery exception playbooks.
changelog: Initial release with carrier selection, customs checks, and exception handling workflows.
metadata: {"clawdbot":{"emoji":"BOX","requires":{"bins":[],"config":["~/shipping/"]},"os":["linux","darwin","win32"],"configPaths":["~/shipping/"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines.

## When to Use

User needs to ship physical goods and wants reliable decisions across rates, packaging, customs, tracking, and delivery issues. Agent provides shipment planning, carrier choice, cost control, compliance checks, and incident response playbooks.

This skill is advisory and workflow-focused. It does not buy labels, call carrier APIs, or access shipping accounts unless the user provides a separate integration workflow.

## Architecture

Memory lives in `~/shipping/`. See `memory-template.md` for structure and status fields.

```text
~/shipping/
|- memory.md             # Durable shipping context and preferences
|- carrier-rules.md      # Preferred carriers and service constraints
|- international.md      # Country and customs notes
`- incidents.md          # Repeated failure patterns and resolutions
```

## Quick Reference

Use the smallest relevant file for the current task.

| Topic | File |
|-------|------|
| Setup flow | `setup.md` |
| Memory template | `memory-template.md` |
| Carrier selection | `carrier-selection.md` |
| International customs | `international-customs.md` |
| Delivery exception handling | `exception-playbook.md` |

## Core Rules

### 1. Confirm Shipment Profile First
Before recommending any option, confirm:
- Origin and destination
- Package count, dimensions, and weight
- Delivery deadline and budget ceiling
- Value, fragility, and regulatory constraints

Never optimize blind.

### 2. Price for Total Landed Cost
Always show total cost, not just carrier label price:
- Transport fee
- Packaging and handling
- Fuel, remote, residential, signature, and insurance surcharges
- Duties, taxes, and brokerage where applicable

If any component is unknown, mark it as estimate and show risk.

### 3. Select Carrier by SLA Risk, Not Sticker Price
Pick service based on the real failure cost:
- Time-critical shipment: prioritize reliability and claims process
- Low-value shipment: prioritize cost efficiency
- International shipment: prioritize customs support and tracking depth

State tradeoffs explicitly before final recommendation.

### 4. Validate Compliance Before Label Purchase
For cross-border shipments, verify:
- Commodity description and HS code quality
- Declared value consistency with invoice
- Prohibited or restricted item checks
- Incoterm and importer responsibilities

Do not proceed when documentation is incomplete.

### 5. Run Tracking Checkpoints Proactively
Set checkpoints at minimum for:
- Label created but not scanned within 24h
- Customs hold or pending documents
- Out for delivery delays beyond promised window

For each checkpoint, provide next action and owner.

### 6. Treat Exceptions as Playbooks, Not Improvisation
Use a defined response path for lost, damaged, delayed, returned, or refused shipments:
- Capture facts and evidence first
- Notify customer with realistic timeline
- Open claim/escalation within carrier deadline
- Decide reshipment vs refund based on cost and SLA

### 7. Save Reusable Shipping Intelligence
After each meaningful case, update memory with:
- Carrier performance by route
- Recurring surcharge patterns
- Packaging failures and fixes
- Country-specific documentation pitfalls

This turns shipping from reactive to compounding.

## Common Traps

- Comparing rates without normalizing surcharges -> false savings and margin loss.
- Guessing box size from product photos -> dimensional weight surprises.
- Declaring vague item descriptions -> customs holds and rejections.
- Promising delivery dates without scan confirmation -> avoidable support escalations.
- Filing claims without evidence package -> denied reimbursement.
- Treating every delay as carrier fault -> misses internal pick-pack bottlenecks.

## Security & Privacy

**Data that leaves your machine:**
- None by default from this skill itself.

**Data that stays local:**
- Shipping context and learned patterns under `~/shipping/`.

**This skill does NOT:**
- Access undeclared external services automatically.
- Buy labels or place shipping orders automatically.
- Retrieve tracking events from carrier APIs automatically.
- Store payment credentials or full card data.
- Modify files outside `~/shipping/` for memory.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `ecommerce` - Store operations and conversion workflows.
- `marketplace` - Multi-platform selling and fulfillment strategy.
- `inventory` - Stock planning and replenishment control.
- `sell` - Listing, pricing, and sales execution.
- `buy` - Purchasing decisions and supplier-side evaluation.

## Feedback

- If useful: `clawhub star shipping`
- Stay updated: `clawhub sync`
