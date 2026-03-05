<p align="center">
  <img src="./lance.png" alt="Lance logo" width="170" />
</p>

<h1 align="center">Lance</h1>

<p align="center">
  High-signal Web3 vulnerability hunting skill with strict exploitability and economic validation.
</p>

<p align="center">
  <a href="https://github.com/shaniidev/lance/stargazers"><img src="https://img.shields.io/github/stars/shaniidev/lance?style=flat&logo=github&logoColor=white&color=gold&label=Stars" alt="Stars" /></a>
  <a href="https://github.com/shaniidev/lance/releases"><img src="https://img.shields.io/github/v/release/shaniidev/lance?style=flat&logo=semanticrelease&logoColor=white" alt="Release" /></a>
  <a href="https://github.com/shaniidev/lance/actions"><img src="https://img.shields.io/badge/status-active-success?style=flat" alt="Status" /></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/MIT-green?logo=opensourceinitiative&logoColor=white" alt="License" /></a>
  <img src="https://img.shields.io/badge/Agent_Skills-standard-orange" alt="Agent Skills" />
  <img src="https://img.shields.io/badge/Workflow-7%20Gates-blue" alt="Workflow" />
  <img src="https://img.shields.io/badge/Precision_Target-%E2%89%A580%25-brightgreen" alt="Precision Target" />
  <img src="https://img.shields.io/badge/OpenClaw-supported-brightgreen" alt="OpenClaw" />
  <img src="https://img.shields.io/badge/Cursor-supported-1C1C1C?logo=cursor&logoColor=white" alt="Cursor" />
  <img src="https://img.shields.io/badge/Claude_Code-supported-7B2DB0?logo=anthropic&logoColor=white" alt="Claude Code" />
  <img src="https://img.shields.io/badge/Antigravity-supported-4285F4?logo=google&logoColor=white" alt="Antigravity" />
  <img src="https://img.shields.io/badge/Windsurf-supported-09B6A2?logo=codeium&logoColor=white" alt="Windsurf" />
  <img src="https://img.shields.io/badge/Goose-supported-111111" alt="Goose" />
</p>

Lance is an Agent Skill for Web3 bug bounty and protocol auditing workflows focused on triage-grade findings. It is built to minimize false positives, force exploitability proof, and require economic realism before reporting.

## Why Lance Exists

Most audit prompts fail in two ways:
- too many speculative findings
- poor mapping between technical issue and real bounty acceptance

Lance addresses this with strict gating and reportability discipline:
- exploit path must be concrete
- impact must be practical and defensible
- findings must survive rejection-style triage simulation

## Agent Compatibility

| Agent | Support | Skills Directory |
|---|---|---|
| OpenClaw | Native | Install via ClawHub/skills |
| Cursor | Native | `.cursor/skills/lance/` |
| Claude Code | Native | `.claude/skills/lance/` |
| Antigravity | Native | `.agents/skills/lance/` |
| Windsurf | Native | Skills directory |
| Goose | Supported | Skills directory |

## Core Method

Lance enforces a 7-gate process. A finding that fails any gate is not bounty-ready.

| Gate | Focus | Output Requirement |
|---|---|---|
| G0 | Scope authorization | In-scope target confirmation |
| G1 | Target intake | Normalized target manifest |
| G2 | Detection | Candidate findings with code context |
| G3 | Exploitability | Deterministic attacker path |
| G4 | Economics | Feasible capital/liquidity/profit model |
| G5 | False positives | Rejection-tested surviving findings |
| G6 | Triage/reporting | Platform-ready report payload |

## What Is Inside

```text
lance/
  SKILL.md
  agents/
  references/
    chains/
    platforms/
    vulnerabilities/
  scripts/
  assets/
    templates/
    benchmarks/
```

## Coverage

| Category | Coverage |
|---|---|
| Access & Authorization | access control bypass, privilege misbinding, signature replay |
| State Safety | reentrancy, upgradeability/storage collision, accounting invariant breaks |
| DeFi Market Risks | oracle manipulation, flash-loan manipulation, AMM/vault/governance abuse |
| Cross-Chain | bridge replay / message validation failures |
| Move/Sui | capability abuse, shared-object race/authorization issues |

## Script Toolkit

| Script | Purpose |
|---|---|
| `scripts/parse_web3_scope.py` | Parse scope/rules files into structured data |
| `scripts/normalize_targets.py` | Normalize addresses/repos/packages into one manifest |
| `scripts/invariant_output_adapter.py` | Adapt scanner output to Lance finding schema |
| `scripts/scoring_engine.py` | Score findings for triage readiness |
| `scripts/triage_simulator.py` | Run strict triage simulation (`Accepted/Needs More Evidence/Rejected`) |
| `scripts/generate_web3_report.py` | Generate platform-specific markdown reports |
| `scripts/benchmark_harness.py` | Measure precision/recall/F1 against labeled benchmark cases |

## Output Contract

Lance findings are standardized via:
- `assets/templates/finding.schema.json`
- platform report templates in `assets/templates/`

This keeps results consistent across agents and submission formats.

## Install

```bash
git clone https://github.com/shaniidev/lance .cursor/skills/lance
git clone https://github.com/shaniidev/lance .claude/skills/lance
git clone https://github.com/shaniidev/lance .agents/skills/lance
```

## Quick Use (Local)

Run benchmark harness:
```bash
python scripts/benchmark_harness.py assets/benchmarks/sample_benchmark.json
```

Generate a report from finding JSON:
```bash
python scripts/generate_web3_report.py --platform immunefi --input finding.json --output report.md
```

Run triage simulation:
```bash
python scripts/triage_simulator.py findings.json --output triage.json
```

## Contribution Guide

See [CONTRIBUTING.md](./CONTRIBUTING.md) for standards on:
- quality of vulnerability logic
- benchmark updates
- references/playbook changes
- script/test expectations

## Author

- shaniidev
- GitHub: https://github.com/shaniidev

## License

MIT
