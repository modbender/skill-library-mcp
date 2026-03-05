# Meta-Research

A Claude Code skill that guides you through a hypothesis-driven research lifecycle — from literature survey to publication — with built-in rigor, reproducibility tracking, and bias mitigation.

## What it does

Meta-Research acts as an autonomous research copilot with a **6-phase hypothesis-driven workflow**:

1. **Literature Survey** — Understand SOTA, identify gaps, open problems, and underexplored areas
2. **Hypothesis Generation** — Generate broad testable hypotheses, maintain a hypothesis tree in YAML
3. **Judgment Gate** — Evaluate each hypothesis: novel? important? feasible? falsifiable? already solved?
4. **Experiment Design** — Rigorous per-hypothesis protocol with locked analysis plans
5. **Experiment Execution** — Run experiments, track results, determine outcomes
6. **Reflection** — Analyze results, decide: go deeper, go broader, pivot, or conclude

The workflow is a **research loop** — after experiments, reflection decides whether to continue iterating (generating new hypotheses, running more experiments) or conclude and move to writing.

Two core artifacts track all project state:
- **`research-tree.yaml`** — Hypothesis hierarchy with judgments, experiments, and results
- **`research-log.md`** — Chronological timeline of exploration and decisions

## Installation

### From marketplace

```bash
/plugins marketplace add <marketplace-url>
/plugins install meta-research
```

### Manual installation

```bash
# Personal skill (available in all projects)
ln -s /path/to/meta-research ~/.claude/skills/meta-research

# Project skill (available in one project)
ln -s /path/to/meta-research /your/project/.claude/skills/meta-research
```

## Usage

```
/meta-research [your research question or topic]
```

The skill always starts with a literature survey to understand the field before generating hypotheses. If you have existing artifacts (`research-tree.yaml`, `research-log.md`), it will resume from the current state.

### Examples

```
/meta-research How does in-context learning scale with model size?
/meta-research I want to explore efficient fine-tuning methods for small models
/meta-research Help me analyze my experiment results and decide next steps
```

## Project structure

```
meta-research/
├── SKILL.md                              # Main skill definition (v2.0 — hypothesis-driven)
├── phases/
│   ├── literature-survey.md              # Search, screen, synthesize, identify gaps
│   ├── hypothesis-generation.md          # Generate and organize hypotheses
│   ├── ideation-frameworks.md            # 12 cognitive frameworks for idea generation
│   ├── judgment.md                       # Evaluate hypotheses before investing
│   ├── experiment-design.md              # Per-hypothesis protocol design
│   ├── experiment-execution.md           # Run experiments, analyze, determine outcomes
│   ├── reflection.md                     # Strategic decisions and research loop
│   └── writing.md                        # Reporting and dissemination
├── templates/
│   ├── research-tree.yaml                # Hypothesis tree starter template
│   ├── judgment-rubric.md                # Judgment gate scoring rubric
│   ├── research-log.md                   # Log format and examples
│   ├── experiment-protocol.md            # Full experiment design template
│   └── reproducibility-checklist.md      # Pre-submission checklist
├── raw-meta-research.md                  # Source material and references
├── LOGBOX.md                             # Development log
├── .claude-plugin/
│   └── plugin.json                       # Plugin manifest
├── LICENSE
└── README.md
```

## Key features

- **Literature-first** — Always starts by understanding the state of the art before generating ideas
- **Hypothesis tree** — Central YAML data structure tracking all hypotheses, judgments, and results
- **Judgment gate** — Evaluates novelty, importance, feasibility, and falsifiability before investing resources
- **Research loop** — Reflects after experiments and decides: go deeper, go broader, pivot, or conclude
- **Bias mitigation** — Separates exploratory vs confirmatory analysis, constrains researcher degrees of freedom
- **Reproducibility-first** — Version control, pinned environments, experiment tracking built into the workflow
- **Falsification mindset** — Designs experiments to disprove, not confirm

## License

[MIT](LICENSE)
