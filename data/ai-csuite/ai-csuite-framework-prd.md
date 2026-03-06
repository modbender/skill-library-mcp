# AI C-Suite Framework PRD

**Version:** 2.0.0  
**Status:** Implemented (script-backed local runtime)  
**Last Updated:** 2026-02-26  
**Scope:** `ai-csuite` skill folder

---

## 1. Product Summary

`ai-csuite` is a script-backed decision support skill for SaaS founders and small teams.  
It generates a structured executive-style debate and final CEO decision artifact from:

- a decision topic
- company context (`config/company.yaml`)
- stage-based roster rules

The current implementation is deterministic and template-driven in Python (stdlib-only).  
It does not call external APIs and does not require third-party packages.

---

## 2. Goals

1. Provide a repeatable strategic decision workflow with clear sections and ownership.
2. Enforce a consistent output contract (`DATA BRIEF`, `CEO BRIEF`, `CEO DECISION`).
3. Keep runtime simple and safe for GitHub distribution and VirusTotal scanning.
4. Work offline with local files and CLI commands.

---

## 3. Non-Goals (Current Version)

1. No real multi-agent LLM orchestration runtime.
2. No persistent memory database.
3. No per-token API billing telemetry.
4. No live customer/finance system integrations.
5. No OpenClaw standalone deployment artifacts.

These can be added in future versions.

---

## 4. Implemented Runtime Architecture

### 4.1 Components

| Component | File | Responsibility |
|---|---|---|
| Shared config/runtime helpers | `scripts/common.py` | Stage profiles, company parsing, validation helpers |
| Session prep | `scripts/prepare_session.py` | Validate context, derive roster, rounds, squads |
| Debate generator | `scripts/run_debate.py` | Build data brief, rounds, CoS brief, CEO decision markdown |
| Output validator | `scripts/validate_output.py` | Assert required markers and key decision metadata |
| Security scanner | `scripts/security_scan.py` | Flag suspicious patterns and non-stdlib imports |
| Company template | `config/company.yaml` | Required input schema for all runs |

### 4.2 Runtime Flow

1. `security_scan.py` verifies repository safety signals.
2. `prepare_session.py` validates company context and builds session packet.
3. `run_debate.py` generates structured decision output in `logs/*.md`.
4. `validate_output.py` verifies output contract before acceptance.

---

## 5. Input Contract

Required company fields:

- `company_name`
- `product`
- `stage`
- `arr_or_mrr`
- `runway_months`
- `team_size`
- `constraints` (YAML list)

Supported stage aliases are normalized to:

- `solo`
- `pre-seed`
- `seed`
- `series-a`

If required fields are missing or stage is unsupported, session prep fails fast.

---

## 6. Stage Profiles and Debate Topology

### 6.1 Debate Agents by Stage

| Stage | Debate Agents | Rounds |
|---|---|---|
| `solo` | CEO, CTO, CPO, CFO, CoS | 2 |
| `pre-seed` | CEO, CTO, CPO, CoS, CV | 2 |
| `seed` | CEO, CTO, CPO, CMO, CRO, CoS, CV | 3 |
| `series-a` | CEO, CTO, CPO, CFO, CMO, CRO, COO, CSA, CISO, CoS, CV | 3 |

### 6.2 Data Brief Agents

Data brief always includes:

- CV signal summary
- CFO financial context summary

If either agent is not in the debate roster for the selected stage, it still appears as data-only.

### 6.3 Squad Mapping

| Squad | Members |
|---|---|
| Strategy | CEO, CFO, COO, CoS |
| Product | CTO, CPO, CSA, CISO |
| Growth | CMO, CRO, CV |

Active squads are inferred from topic keywords and printed in session packet output.

---

## 7. Output Contract

Generated markdown must contain all of the following sections:

- `DATA BRIEF (Pre-Round)`
- Round 1 per active debater
- Round 2 per active debater
- Round 3 per active debater (3-round stages only)
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

`validate_output.py` enforces this contract and returns non-zero on violation.

---

## 8. Decision Behavior (Current Logic)

1. Topic is classified to one category: pricing, hiring, architecture, security, growth, or general.
2. Recommendations are selected from category defaults.
3. Round 1 creates role-based analyses with confidence labels.
4. Round 2 creates agreement/challenge updates.
5. Round 3 adds convergence language for 3-round stages.
6. Consensus is selected from recommendation frequency.
7. Runway-sensitive override logic applies when runway is below 6 months.
8. Reversibility is assigned by topic category.

This is deterministic template logic, not autonomous agent reasoning.

---

## 9. Safety Model and VirusTotal Readiness

### 9.1 Implemented Safety Controls

`security_scan.py` checks:

- suspicious runtime patterns in text and code files
- imports outside Python stdlib (plus local module `common`)
- UTF-8 readability for scanned text files

### 9.2 Intended Distribution Properties

1. Plaintext markdown, YAML, and Python source.
2. No automatic outbound network behavior.
3. No credentials required for runtime.
4. Local file operations scoped to skill directory inputs/outputs.

Note: VirusTotal results ultimately depend on uploaded artifact state and scanner versions.

---

## 10. CI and Verification

GitHub Actions workflow (`.github/workflows/ci.yml`) runs:

1. security scan
2. session preparation
3. debate generation
4. output validation

This ensures baseline runtime correctness on push and pull request events affecting `ai-csuite`.

---

## 11. Current File Structure

```text
ai-csuite/
├── .github/workflows/ci.yml
├── .gitignore
├── LICENSE
├── README.md
├── SKILL.md
├── ai-csuite-framework-prd.md
├── config/
│   └── company.yaml
├── logs/
│   └── .gitkeep
└── scripts/
    ├── common.py
    ├── prepare_session.py
    ├── run_debate.py
    ├── security_scan.py
    └── validate_output.py
```

---

## 12. Future Extensions

1. Optional API-backed reasoning mode behind explicit configuration.
2. Persistent decision journal with searchable history.
3. Structured JSON output mode in addition to markdown.
4. Richer validation rules for escalation and contradiction handling.
5. Topic-specific playbooks and configurable recommendation libraries.

// TODO: split ai-csuite-framework-prd.md into smaller modules/components
