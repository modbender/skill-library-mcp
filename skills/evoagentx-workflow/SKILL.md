---
name: evoagentx-workflow
description: Bridge EvoAgentX (1000+ star open-source framework) with OpenClaw. Enables self-evolving agentic workflows - workflows that automatically improve over time through evolutionary optimization. Solves the gap where no EvoAgentX integration existed for OpenClaw (only 2 minimal EvoMap skills existed). Provides workflow autoconstruction, TextGrad/AFlow/MIPRO optimization algorithms, and GEP (Genome Evolution Protocol) integration.
metadata:
  {
    "openclaw":
    {
      "requires": { "bins": ["python3", "pip"] },
      "install":
      [
        {
          "id": "pip",
          "kind": "pip",
          "package": "evoagentx",
          "bins": ["python3"],
          "label": "Install EvoAgentX framework",
        },
      ],
    },
  }
---

# EvoAgentX Workflow Integration

Integrates the EvoAgentX framework with OpenClaw for self-evolving agentic workflows.

## When to Use This Skill

Use this skill when:
- Building multi-agent workflows that need to evolve over time
- Evaluating and optimizing existing agent workflows
- Implementing the Genome Evolution Protocol (GEP)
- Creating self-improving agent systems
- Migrating static workflows to self-evolving ones

## Quick Start

### CLI Usage

This skill provides a command-line interface for EvoAgentX operations:

```bash
# Check if EvoAgentX is installed
python3 scripts/evoagentx_cli.py status

# Get installation instructions
python3 scripts/evoagentx_cli.py install

# Show usage examples
python3 scripts/evoagentx_cli.py examples

# Create a workflow template
python3 scripts/evoagentx_cli.py create-workflow \
  --name ResearchWorkflow \
  --description "A research automation workflow"

# Check EvoAgentX status
python3 scripts/evoagentx_cli.py check
```

### Installation

```bash
# Install EvoAgentX framework
pip install evoagentx

# Verify installation
python3 -c "import evoagentx; print(evoagentx.__version__)"
```

### 1. Create a Basic Workflow

After running `create-workflow`, edit the generated Python file:

```python
from evoagentx import Agent, Workflow

class MyWorkflow(Workflow):
    async def execute(self, context):
        # Your workflow logic here
        result = await self.run_agents(context)
        return result
```

### 2. Enable Self-Evolution

```python
from evoagentx.evolution import EvolutionEngine

engine = EvolutionEngine()
optimized_workflow = await engine.evolve(
    workflow=MyWorkflow(),
    iterations=10,
    evaluation_criteria={"accuracy": 0.95}
)
```

## Core Concepts

### Workflows
- Multi-agent orchestration
- State management
- Tool integration

### Evolution Strategies
- **TextGrad**: Prompt optimization
- **AFlow**: Workflow structure optimization  
- **MIPRO**: Multi-step reasoning optimization

### Genomes
Encoded success patterns containing:
- Task type classification
- Approach methodology
- Outcome metrics
- Context requirements

## Common Patterns

### Pattern 1: Research Workflow Evolution
```python
# Start with basic research workflow
workflow = ResearchWorkflow()

# Evolve for better results
evolution = await workflow.evolve(
    dataset=research_queries,
    metric="comprehensiveness"
)
```

### Pattern 2: Tool Selection Optimization
```python
# EvoAgentX automatically selects optimal tools
workflow = AgentWorkflow(
    tools=["web_search", "browser", "file_io"],
    auto_select=True
)
```

## Security Considerations

- All evolution happens locally (no data exfiltration)
- Genomes contain no credentials
- Evaluation uses synthetic data when possible

## References

- EvoAgentX GitHub: https://github.com/EvoAgentX/EvoAgentX
- Documentation: https://evoagentx.github.io/EvoAgentX/
- arXiv Paper: https://arxiv.org/abs/2507.03616

## Version

1.0.0 - Initial release with core EvoAgentX integration
