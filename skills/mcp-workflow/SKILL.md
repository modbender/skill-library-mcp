---
name: mcp-workflow
description: Workflow automation using MCP (Model Context Protocol) patterns inspired by Jason Zhou
version: 1.0.0
author: OpenClaw
---

# MCP Workflow Skill

## Quick Reference

```bash
# Start MCP Server
node scripts/mcp-server.js

# Run a workflow
./scripts/workflow-engine.sh run <workflow-name> [--input <json>]

# List available workflows
./scripts/workflow-engine.sh list

# Create new workflow from template
./scripts/workflow-engine.sh create <name> --from <template>

# Validate workflow
./scripts/workflow-engine.sh validate <workflow-file>
```

## Overview

This skill implements workflow automation using the Model Context Protocol (MCP), enabling:
- **Prompt Chains**: Multi-step prompt sequences
- **Dynamic Workflows**: Context-aware adaptation
- **Resource Integration**: File/data embedding
- **Cross-Server Coordination**: Multi-MCP orchestration

## Workflow Patterns

### 1. Prompt Chain Pattern
```
plan → generate → execute → validate
```

### 2. Dynamic Prompt Pattern
```
context → adapt → generate → output
```

### 3. Resource Embedding Pattern
```
resource://{type}/{id} → load → embed → process
```

### 4. External Trigger Pattern
```
trigger → validate → dispatch → execute
```

## Built-in Templates

| Template | Description | Use Case |
|----------|-------------|----------|
| `meal-planner` | Weekly meal planning | Nutrition, shopping lists |
| `code-review` | Automated code review | PR analysis, quality checks |
| `weekly-report` | Status report generation | Team updates, metrics |
| `documentation-generator` | Doc generation | API docs, changelogs |

## MCP Server Features

### Resources
- `file://{path}` - File system access
- `memory://{key}` - Memory storage
- `config://{section}` - Configuration values

### Tools
- `workflow.run` - Execute workflow
- `workflow.list` - List workflows
- `workflow.validate` - Validate workflow JSON
- `prompt.render` - Render prompt template

### Prompts
- `chain:plan` - Planning prompt
- `chain:generate` - Generation prompt
- `chain:review` - Review prompt

## Example Usage

### Meal Planner Workflow
```bash
./scripts/workflow-engine.sh run meal-planner \
  --input '{"diet":"vegetarian","days":7,"budget":50}'
```

### Code Review Workflow
```bash
./scripts/workflow-engine.sh run code-review \
  --input '{"repo":"myapp","pr":123}'
```

### Weekly Report
```bash
./scripts/workflow-engine.sh run weekly-report \
  --input '{"project":"dashboard","week":"2024-W01"}'
```

## Best Practices

### 1. Workflow Design
- Keep steps atomic and focused
- Use clear input/output contracts
- Implement error handling at each step
- Version your workflows

### 2. Prompt Engineering
- Use system prompts for context
- Provide examples in few-shot prompts
- Chain prompts for complex tasks
- Validate outputs before next step

### 3. Resource Management
- Use URI patterns consistently
- Cache frequently accessed resources
- Clean up temporary resources
- Document resource schemas

### 4. Cross-Server Coordination
- Define clear interfaces between servers
- Use standardized message formats
- Implement health checks
- Handle timeouts gracefully

## Configuration

Create `~/.openclaw/mcp-workflow.json`:
```json
{
  "servers": [
    {
      "name": "local",
      "command": "node scripts/mcp-server.js",
      "env": {}
    }
  ],
  "workflowsDir": "./workflows",
  "templatesDir": "./scripts/templates",
  "defaultTimeout": 30000
}
```

## Integration with OpenClaw

Use in your OpenClaw session:
```bash
# Load the skill
openclaw skill load mcp-workflow

# Run workflow
openclaw workflow run meal-planner --input '{"days":5}'
```

## References

- [MCP Specification](references/mcp-spec.md)
- [Workflow Patterns](references/workflow-patterns.md)
- [Jason Zhou Insights](references/jason-zhou-insights.md)
