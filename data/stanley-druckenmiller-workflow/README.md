# Stanley Druckenmiller Workflow

Thesis-driven market analysis skill for OpenClaw.

This skill is designed for Druckenmiller-inspired macro/equity thinking with a live PM memo voice:
- Liquidity and rates first
- Consensus vs variant explicitly separated
- D1/D2 (first derivative / second derivative) regime logic
- Evidence anchors and safety disclaimers

## What This Skill Produces

Depending on trigger, it can generate:
- AM morning brief (thesis + validation)
- EOD wrap
- Weekly review
- Monthly regime review
- Pre-trade thesis collision check
- Asset divergence monitor

All outputs are narrative and decision-oriented (not raw JSON dumps).

## Folder Structure

```text
stanley-druckenmiller-workflow/
  SKILL.md
  README.md
  scripts/
    market_panels.py
```

## Core Design Principles

1. Public data only (no private-info claims)
2. No explicit trade orders (no entry, stop, target, size)
3. Probabilistic language over certainty
4. Facts and interpretation separated
5. Mandatory fields:
   - what_would_change_my_mind
   - data_timestamp (ISO8601)
6. If data is missing, downgrade safely (DATA LIMITED)

## Triggers and Modes

- Mode A (AM brief):
  - `晨报`
  - `macro update`
  - `stan分析下当前市场`
  - `今天怎么看`

- Mode B (EOD wrap):
  - `EOD`
  - `收盘复盘`
  - `今天盘面总结`

- Mode C (Weekly):
  - `周报`
  - `weekly review`
  - `下周怎么看`

- Mode D (Pre-trade consult):
  - `交易前看一眼`
  - `should I buy/sell`
  - `帮我做交易前 sanity check`

- Mode E (Monthly):
  - `月报`
  - `monthly review`
  - `regime review`

- Mode F (13F rationale):
  - `13F`
  - `why did he buy XLF`
  - `Q3 to Q4 holdings changes`

- Mode G (Asset divergence):
  - `盯住 [TICKER]`
  - `check divergence for [TICKER]`
  - `资产背离警报`

## Evidence and Safety Contract

- Include `Evidence anchors` section (top 6-12; Mode G: 3-5)
- Each anchor should include:
  - panel/metric
  - direction/change
  - lookback window
  - timestamp
  - source
- Missing evidence must be tagged:
  - `[EVIDENCE INSUFFICIENT: missing X]`

Safety footer (always append):
- Chinese: `免责声明：以上内容是研究框架信息，不构成投资建议或交易指令。`
- English: `Disclaimer: The above content is research framework information and does not constitute investment advice or trading instructions.`

## Local Validation Checklist (Before Publish)

1. `SKILL.md` frontmatter valid (`name`, `description`, metadata)
2. Trigger words route to expected mode
3. Output contains mandatory fields
4. DATA LIMITED behavior works when data is missing
5. No explicit trading instructions in output
6. Chinese and English depth parity is preserved

## Publish Checklist (ClawHub)

Do this only when you are ready to publish.

1. Login:

```bash
clawhub login
clawhub whoami
```

2. Optional dry run checks:

```bash
clawhub list
```

3. Publish command template:

```bash
clawhub publish ./skills/stanley-druckenmiller-workflow \
  --slug stanley-druckenmiller-workflow \
  --name "Stanley Druckenmiller Workflow" \
  --version 1.0.0 \
  --changelog "Initial public release: thesis-driven macro workflow with A-G modes, evidence protocol, and safe downgrade behavior."
```

4. Verify result:

- Confirm package page on ClawHub
- Install from a clean env and run one trigger from Mode A and one from Mode G

## Versioning Suggestion

- Start: `1.0.0`
- Behavior changes in output contract: bump minor (`1.1.0`)
- Trigger or schema breaking changes: bump major (`2.0.0`)

## Notes

- This skill is Druckenmiller-inspired and should never claim direct affiliation.
- Keep style high-conviction but evidence-auditable.
