---
name: quorum
description: Multi-agent validation framework. Spawns independent AI critics to evaluate artifacts (documents, configs, code, research) against rubrics with evidence-grounded findings.
metadata: {"openclaw":{"requires":{"bins":["python3","pip"],"env":["ANTHROPIC_API_KEY","OPENAI_API_KEY"]},"install":[{"id":"clone-repo","kind":"shell","command":"git clone https://github.com/SharedIntellect/quorum.git /tmp/quorum-install && cd /tmp/quorum-install/reference-implementation && pip install -r requirements.txt","label":"Clone Quorum repo and install Python dependencies"}],"source":"https://github.com/SharedIntellect/quorum"}}
---

# Quorum — Multi-Agent Validation

Quorum validates AI agent outputs by spawning multiple independent critics that evaluate artifacts against rubrics. Every criticism must cite evidence. You get a structured verdict.

## Quick Start

Clone the repository and install:

```bash
git clone https://github.com/SharedIntellect/quorum.git
cd quorum/reference-implementation
pip install -r requirements.txt
```

Run a quorum check on any file:

```bash
python -m quorum.cli run --target <path-to-artifact> --rubric <rubric-name>
```

### Built-in Rubrics

- `research-synthesis` — Research reports, literature reviews, technical analyses
- `agent-config` — Agent configurations, YAML specs, system prompts

### Depth Profiles

- `quick` — 3 critics, no fix rounds, 5-15 min
- `standard` — 6 critics, 1 fix round on CRITICAL, 15-30 min (default)
- `thorough` — All 9 critics + external validator, ≤2 fix rounds, 45-90 min

### Examples

```bash
# Validate a research report
python -m quorum.cli run --target my-report.md --rubric research-synthesis

# Quick check (faster, fewer critics)
python -m quorum.cli run --target my-report.md --rubric research-synthesis --depth quick

# List available rubrics
python -m quorum.cli rubrics list

# Initialize config interactively
python -m quorum.cli config init
```

## Configuration

On first run, Quorum prompts for your preferred models and writes `quorum-config.yaml`. You can also create it manually:

```yaml
models:
  tier_1: anthropic/claude-sonnet-4-6    # Judgment roles
  tier_2: anthropic/claude-sonnet-4-6    # Evaluation roles
depth: standard
```

Set your API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# or
export OPENAI_API_KEY=sk-...
```

## Output

Quorum produces a structured verdict:

- **PASS** — No significant issues found
- **PASS_WITH_NOTES** — Minor issues, artifact is usable
- **FAIL** — Critical or high-severity issues that need resolution

Each finding includes: severity (CRITICAL/HIGH/MEDIUM/LOW), evidence citations pointing to specific locations in the artifact, and remediation suggestions.

## More Information

- [SPEC.md](https://github.com/SharedIntellect/quorum/blob/main/SPEC.md) — Full architectural specification
- [MODEL_REQUIREMENTS.md](https://github.com/SharedIntellect/quorum/blob/main/docs/MODEL_REQUIREMENTS.md) — Supported models and tiers
- [CONFIG_REFERENCE.md](https://github.com/SharedIntellect/quorum/blob/main/docs/CONFIG_REFERENCE.md) — All configuration options
- [FOR_BEGINNERS.md](https://github.com/SharedIntellect/quorum/blob/main/docs/FOR_BEGINNERS.md) — New to agent validation? Start here


---

> ⚖️ **LICENSE** — Not part of the operational specification above.
> This file is part of [Quorum](https://github.com/SharedIntellect/quorum).
> Copyright 2026 SharedIntellect. MIT License.
> See [LICENSE](https://github.com/SharedIntellect/quorum/blob/main/LICENSE) for full terms.
