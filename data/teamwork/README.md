# Teamwork Skill

A comprehensive AI agent team management skill for OpenClaw that enables dynamic team creation, intelligent model selection, and coordinated task execution.

## Features

- **Multi-Provider Support**: Configure multiple AI providers (OpenAI, Anthropic, Google, etc.)
- **Flexible Pricing Models**: Support for subscription, tiered usage, and pay-per-use pricing
- **8-Dimension Performance Evaluation**: Comprehensive model scoring system
- **Herald Communication System**: Centralized message relay and coordination
- **Complete Workflow Management**: From requirement analysis to final delivery
- **Template-Based Reporting**: Structured documentation for all activities

## Quick Start

### Installation

This skill is designed to be used with OpenClaw. Simply place it in your `.trae/skills/teamwork/` directory.

### Initial Setup

When first invoked, the skill will automatically guide you through configuration:

1. **Provider Setup**: Add your AI providers and API keys
2. **Model Configuration**: Configure models with pricing and capabilities
3. **Host Model Selection**: Choose your primary interaction model
4. **Budget Setup**: Set spending limits (optional)

### Usage

```javascript
// The skill is automatically invoked by OpenClaw when:
// - User requests multi-agent collaboration
// - Complex projects need coordinated execution
// - Tasks require specialized roles
```

## Directory Structure

```
.trae/skills/teamwork/
├── SKILL.md              # Main skill definition
├── package.json          # Node.js package configuration
├── scripts/              # Execution scripts
│   ├── init.js          # Initialization
│   ├── config-manager.js # Configuration management
│   ├── score-manager.js  # Performance scoring
│   ├── team-coordinator.js # Team coordination
│   └── herald.js        # Communication system
├── templates/            # Document templates
│   ├── task-report.md
│   ├── meeting-minutes.md
│   ├── failure-report.md
│   └── evaluation-form.md
└── utils/               # Utility functions
    ├── helpers.js
    ├── logger.js
    ├── template-renderer.js
    └── errors.js
```

## Configuration Files

### providers.json
Location: `.trae/config/providers.json`

Defines AI providers, models, and pricing:
- Provider credentials
- Model capabilities
- Pricing configurations
- Host model designation
- Budget limits

### team-roles.json
Location: `.trae/config/team-roles.json`

Defines team roles and requirements:
- Role descriptions
- Required capabilities
- Preferred model traits
- Workload estimates

### model_scores.json
Location: `.trae/data/model_scores.json`

Stores model performance data:
- Dimension scores
- Overall ratings
- Role fit history
- Evaluation history

## Workflow

1. **User Request** → Host model receives and analyzes request
2. **Task Decomposition** → Break down into phases and subtasks
3. **Team Assembly** → Convene available models for meeting
4. **Role Assignment** → Models self-nominate and vote on roles
5. **Herald Selection** → Choose fastest model as coordinator
6. **Execution** → Parallel task execution with herald coordination
7. **Review Meeting** → Evaluate performance and update scores

## API Reference

See [SKILL.md](./SKILL.md) for complete API documentation.

## License

MIT License
