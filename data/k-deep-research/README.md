# k-deep-research v2.0

Universal deep research methodology skill for OpenClaw and Claude.ai.

## What This Skill Does

Teaches AI agents to conduct systematic, rigorous research investigations using:
- Multi-source triangulation (40-80+ sources for deep investigations)
- Merit-based credibility scoring (0-10 scale, source prestige ≠ truth)
- Adversarial analysis (suppression detection, institutional behavior, narrative flow)
- Pattern recognition across domains (temporal, actor, information flow)
- Iterative deepening protocol (breadth → targeted → synthesis → validation)
- Obsidian-ready output with YAML frontmatter

## Installation

### OpenClaw (Workspace)
```bash
cp -r k-deep-research/ ~/.openclaw/workspace/skills/k-deep-research/
```

### OpenClaw (Managed — shared across agents)
```bash
cp -r k-deep-research/ ~/.openclaw/skills/k-deep-research/
```

### Claude.ai Project
Upload as user skill at `/mnt/skills/user/k-deep-research/`

## Skill Structure

```
k-deep-research/
├── SKILL.md                              # Core methodology (index, <500 lines)
├── references/
│   ├── sourcing-strategies.md            # WHERE and HOW to search
│   ├── research-frameworks.md            # Multi-layer analysis, credibility, patterns
│   ├── output-templates.md               # Report formats, YAML templates
│   ├── openclaw-architecture.md          # OpenClaw technical knowledge base
│   ├── openclaw-skill-authoring.md       # Writing/evaluating/deploying skills
│   ├── autonomy-patterns.md              # Heartbeat, cron, memory, workflows
│   └── adversarial-analysis.md           # Suppression, institutional, narrative analysis
├── scripts/
│   └── validate.sh                       # Structure integrity check
└── README.md                             # This file
```

## Three-Tier Loading

1. **Tier 1 (always):** Name + description (~50 tokens) — triggers skill selection
2. **Tier 2 (on demand):** Full SKILL.md body — methodology index, workflow, decision trees
3. **Tier 3 (as needed):** Individual reference files — deep knowledge loaded per-domain

## Reference Loading Strategy

| Reference | Load When |
|-----------|-----------|
| sourcing-strategies.md | ALWAYS — first file for every research task |
| research-frameworks.md | Complex multi-domain investigations |
| openclaw-architecture.md | Researching OpenClaw, agent architecture |
| openclaw-skill-authoring.md | Building or evaluating OpenClaw skills |
| autonomy-patterns.md | Designing autonomous agent workflows |
| adversarial-analysis.md | Institutional analysis, suppression detection |
| output-templates.md | Custom output formats needed |

## Version History

- **v2.0.0** (2026-02-23): Complete rewrite for OpenClaw compatibility. Added: openclaw-architecture, openclaw-skill-authoring, autonomy-patterns, adversarial-analysis references. Restructured for three-tier loading. Updated all existing references.
- **v1.0.0**: Original Claude.ai project skill with core methodology.

## Validation

```bash
chmod +x scripts/validate.sh
./scripts/validate.sh
```

## License

Personal research tool. Not for redistribution without K's authorization.
