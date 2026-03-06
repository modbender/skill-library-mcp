# openclaw-model-orchestrator

> Multi-LLM orchestration for OpenClaw. Fan-out, pipeline, and consensus patterns with AAHP v3 handoffs.

## Install

```bash
clawhub install openclaw-model-orchestrator
```

## Quick Start

```bash
# Get help
/orchestrate help

# See available models
/orchestrate models

# Get recommendations for a task
/orchestrate recommend "Build a REST API with JWT auth"

# Fan-out: parallel subtasks across models
/orchestrate --mode fan-out --task "Build REST API" --planner copilot-opus --workers copilot52c,grokfast --reviewer copilot-sonnet46

# Pipeline: sequential refinement
/orchestrate --mode pipeline --task "Design caching layer"

# Consensus: compare model answers
/orchestrate --mode consensus --task "Security risks of this design?" --workers copilot-opus,gemini25,sonnet
```

## How It Works

1. **Classify** - Auto-detects task type (coding, research, security, review, bulk)
2. **Recommend** - Suggests optimal model combination based on task + available models
3. **Execute** - Runs orchestration with AAHP v3 structured handoffs between models
4. **Merge** - Reviewer model synthesizes final output

All inter-model communication uses AAHP v3 handoff objects (structured JSON, no raw chat history) for up to 98% token reduction.

## License

MIT
