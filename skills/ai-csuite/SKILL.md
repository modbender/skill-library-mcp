---
name: ai-csuite
description: >
  Runs a script-backed AI C-Suite strategic debate for SaaS teams.
  It builds a stage-aware executive roster, generates structured debate rounds,
  synthesizes a Chief-of-Staff brief, and outputs a CEO decision with action items.
  Includes security and output validation scripts designed for VirusTotal-safe distribution.
license: MIT
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task
metadata:
  version: 2.0.0
  mode: prompt-plus-scripts
  runtime: python3-stdlib
---

# AI C-Suite Multi-Agent Framework

Use this skill when the user needs a strategic decision on product, engineering, pricing,
go-to-market, hiring, operations, or competitive response.

The user's topic is: **$ARGUMENTS**

## Runtime Contract

This skill is operational via local scripts in `scripts/`:
- `prepare_session.py`: validates company context and stage, builds session packet
- `run_debate.py`: generates full multi-round debate + CEO decision
- `validate_output.py`: validates required output sections and fields
- `security_scan.py`: checks for suspicious code patterns for release safety

No hidden network execution, no obfuscation, and no credential reads are required.

## Required Inputs

Load company context from:
- `config/company.yaml`

If missing, ask the user for:
- company name + product line
- stage: `solo | pre-seed | seed | series-a`
- ARR or MRR
- runway (months)
- team size
- constraints list

## Stage Profiles

| Stage | Debate Agents | Rounds |
|---|---|---|
| solo | CEO, CTO, CPO, CFO, CoS | 2 |
| pre-seed | CEO, CTO, CPO, CoS, CV | 2 |
| seed | CEO, CTO, CPO, CMO, CRO, CoS, CV | 3 |
| series-a | CEO, CTO, CPO, CFO, CMO, CRO, COO, CSA, CISO, CoS, CV | 3 |

Data brief agents are always:
- `CV` for customer signals
- `CFO` for financial constraints

If `CV` or `CFO` are not in the debate roster for that stage, they still provide pre-round data.

## Squads

| Squad | Members | Lead |
|---|---|---|
| Strategy | CEO, CFO, COO, CoS | CFO |
| Product | CTO, CPO, CSA, CISO | CPO |
| Growth | CMO, CRO, CV | CRO |

Intra-squad challenges are direct. Cross-squad challenges are mediated by CoS.

## Execution Steps

1. Security pre-check:
```bash
python3 scripts/security_scan.py .
```

2. Build session packet:
```bash
python3 scripts/prepare_session.py --topic "$ARGUMENTS" --company-file config/company.yaml
```

3. Run full debate:
```bash
python3 scripts/run_debate.py --topic "$ARGUMENTS" --company-file config/company.yaml --output logs/latest-decision.md
```

4. Validate output integrity:
```bash
python3 scripts/validate_output.py --file logs/latest-decision.md
```

5. Present result to user and ask:
- accept
- challenge
- rerun with constraints

## Debate Protocol

Use this exact order:
1. Pre-round Data Brief (`CV` + `CFO`)
2. Round 1 independent positions (`3-5` sentences each)
3. Optional human checkpoint
4. Round 2 rebuttals and challenges (`3-5` sentences each)
5. Round 3 convergence (`2-3` sentences, only 3-round stages)
6. CoS synthesis to CEO Brief
7. CEO decision with action owners

## Mandatory Output Shape

The final output must include:
- `DATA BRIEF (Pre-Round)`
- `CEO BRIEF`
- `CEO DECISION`
- `DECISION`
- `RATIONALE`
- `WHAT I WEIGHED`
- `OVERRIDES`
- `NEXT STEPS`
- `REVIEW TRIGGER`
- `CONFIDENCE`
- `REVERSIBILITY`

## Escalation Rules

Always enforce:
1. CISO legal/compliance risk must appear in CEO Brief
2. CFO runway risk under 6 months must include explicit severity
3. CV contradiction with consensus must be shown in brief
4. Deadlock after final round must show both sides
5. Radical position flips must be flagged

## Quality Guardrails

1. Round 1 cannot be uniform agreement
2. No vague recommendations
3. Claims must tie to role or company context
4. CEO must state tradeoffs
5. CoS must probe for groupthink if consensus appears too early

## VirusTotal Safety Profile

Distribution-safe expectations:
- plaintext markdown and Python source only
- no encoded payloads, no runtime decoding
- no `eval`/`exec`/shell injection behavior
- no automatic outbound network calls
- only local read/write in skill directory (`config/`, `logs/`)

## Compatibility

- Claude Code (via .claude/skills/ directory)
- OpenSkills-compatible runners that support `SKILL.md`
