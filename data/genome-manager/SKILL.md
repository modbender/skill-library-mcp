---
name: genome-manager
description: "Complete genome lifecycle management for GEP (Genome Evolution
  Protocol). Fills critical gap: ZERO genome management tools existed despite
  genomes being the foundation of agent self-evolution. Provides structured
  storage, mutation tracking (evolution/adaptation/specialization), lineage
  management, and validation. Enables agents to encode successful patterns as
  shareable genomes, creating collective evolution across the network."
---


# Genome Manager

Manages the Genome Evolution Protocol (GEP) genomes - structured success patterns that enable AI agents to self-evolve.

## What are Genomes?

Genomes are encoded patterns of successful agent behavior:
- **Task Type**: Classification (research, debug, security, etc.)
- **Approach**: Steps, tools, prompts used
- **Outcome**: Success metrics, timing, quality scores
- **Lineage**: Parent genomes, mutation history

## When to Use This Skill

Use when:
- Extracting successful patterns from completed tasks
- Creating reusable genome libraries
- Mutating genomes for optimization
- Tracking genome performance over time
- Preparing genomes for EvoMap sharing

## Genome Lifecycle

```
Experience → Encode → Store → Retrieve → Adopt → Evolve → Share
```

## Quick Start

### CLI Usage

This skill provides a command-line tool for genome management:

```bash
# Create a new genome
python3 scripts/genome_manager.py create \
  --name research-comprehensive-v1 \
  --task-type research \
  --steps "search,extract,synthesize" \
  --tools "web_search,web_fetch" \
  --success-rate 0.95 \
  --sample-size 50

# List all genomes
python3 scripts/genome_manager.py list

# Get a specific genome
python3 scripts/genome_manager.py get research-comprehensive-v1

# Create a mutated copy
python3 scripts/genome_manager.py mutate research-comprehensive-v1 \
  --type evolution \
  --changes "added verification step"

# Validate genome quality
python3 scripts/genome_manager.py validate research-comprehensive-v1
```

### Programmatic Usage

```python
# Import from skill directory
import sys
sys.path.insert(0, "{baseDir}/scripts")
from genome_manager import create_genome, list_genomes

# Create genome programmatically
genome = create_genome(args)
```

## Genome Schema

```json
{
  "genome_id": "uuid-v4",
  "name": "research-comprehensive-v1",
  "task_type": "research",
  "version": "1.0.0",
  "created_at": "ISO-8601",
  "approach": {
    "steps": ["step1", "step2"],
    "tools": ["tool1", "tool2"],
    "prompts": ["prompt_ref"],
    "config": {}
  },
  "outcome": {
    "success_rate": 0.95,
    "avg_duration_seconds": 180,
    "user_satisfaction": 0.92,
    "sample_size": 50
  },
  "lineage": {
    "parent_id": "parent-uuid or null",
    "generation": 1,
    "mutations": [
      {"type": "evolution", "timestamp": "...", "changes": "..."}
    ]
  },
  "tags": ["research", "comprehensive", "verified"]
}
```

## Storage Locations

Default genome storage:
- `memory/genomes/*.json` - Local genome library
- `~/.openclaw/genomes/` - Shared across agents
- EvoMap network - Distributed sharing (future)

## Mutation Types

| Type | Description | Use Case |
|------|-------------|----------|
| **evolution** | Incremental improvement | Refine existing pattern |
| **adaptation** | Context-specific change | Adjust for new domain |
| **specialization** | Narrow scope | Optimize for specific sub-task |
| **crossover** | Combine two genomes | Merge successful patterns |

## Validation Rules

Before saving a genome:
- [ ] Success rate >= 0.8 (proven pattern)
- [ ] Sample size >= 3 (not luck)
- [ ] No credentials in prompts
- [ ] Steps are reproducible
- [ ] Tools are available

## Security

- Genomes never contain API keys or credentials
- All paths use {baseDir} for portability
- Review before sharing to EvoMap network
- Validate mutations don't break security rules

## Integration with EvoAgentX

```python
from evoagentx import Workflow
from genome_manager import Genome

# Load genome into EvoAgentX workflow
genome = Genome.load("research-comprehensive-v1")
workflow = Workflow.from_genome(genome)

# Evolve it further
evolution = await workflow.evolve(dataset=test_cases)
```

## Version History

- 1.0.0: Core genome CRUD operations
- 1.0.1: Added mutation tracking
