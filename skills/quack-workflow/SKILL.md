---
description: Execute multi-step workflows via Orchestrate. Use when running complex workflows, parallel tasks, multi-model orchestration, or automating multi-step processes.
triggers:
  - run workflow
  - orchestrate
  - multi-step
  - parallel tasks
  - workflow yaml
---

# Workflow Engine

Execute multi-step workflows with parallel tasks and multi-model orchestration via the Orchestrate platform.

## Setup

Register at [orchestrate.us.com](https://orchestrate.us.com) for API access.

## Scripts

### Run a Workflow
```bash
node skills/workflow-engine/scripts/run-workflow.mjs --file workflow.yaml
```

### Example Workflow Templates

See `skills/workflow-engine/templates/` for ready-to-use workflow definitions.

## Workflow YAML Format

```yaml
name: example-workflow
steps:
  - id: research
    action: web_search
    params:
      query: "latest AI news"
  - id: summarize
    action: llm
    params:
      model: claude
      prompt: "Summarize: {{research.output}}"
    depends_on: [research]
  - id: post
    action: social_post
    params:
      text: "{{summarize.output}}"
    depends_on: [summarize]
```

## API Reference

- **Base URL:** `https://orchestrate.us.com`
- Multi-step workflow execution
- Parallel task support
- Multi-model orchestration
