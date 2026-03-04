---
name: agent-lightning
description: Microsoft Research's agent training framework. Optimizes AI agents with Reinforcement Learning, Automatic Prompt Optimization, and Supervised Fine-tuning. Zero code change required. Works with LangChain, AutoGen, CrewAI, OpenAI Agent SDK.
version: "1.0.0"
author: "Microsoft Research"
license: "MIT"
repository: "https://github.com/microsoft/agent-lightning"
homepage: "https://microsoft.github.io/agent-lightning/"
tags:
  - "agent-training"
  - "reinforcement-learning"
  - "prompt-optimization"
  - "fine-tuning"
  - "microsoft"
  - "rlhf"
  - "agent-improvement"
keywords:
  - "AI agent training"
  - "reinforcement learning agents"
  - "automatic prompt optimization"
  - "agent fine-tuning"
  - "RL for agents"
category: "ai-training"
---

# Agent Lightning ⚡

Microsoft Research's agent training framework. Turn your AI agents into optimizable beasts with (almost) zero code changes.

## Core Features

- **🔌 Universal Compatibility**: Works with LangChain, OpenAI Agent SDK, AutoGen, CrewAI, Microsoft Agent Framework, or plain Python OpenAI
- **🎯 Selective Optimization**: Optimize one or more agents in a multi-agent system
- **🧠 Multiple Algorithms**: Reinforcement Learning (RL), Automatic Prompt Optimization (APO), Supervised Fine-tuning (SFT)
- **⚡ Zero Code Change**: Add `agl.emit_xxx()` helpers or use tracer — your agent keeps running as usual

## Installation

```bash
pip install agentlightning
```

For latest nightly build:
```bash
pip install --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ --pre agentlightning
```

## Quick Start

### 1. Instrument Your Agent

**Option A: Add emit helpers (recommended)**
```python
import agentlightning as agl

# In your agent's tool calls
response = agl.emit_tool_call(
    model=model,
    messages=messages,
    tools=tools,
    context={"task": "search"}
)
```

**Option B: Use tracer (zero code change)**
```python
from agentlightning import tracer

# Wrap your agent with tracer
with tracer.trace("my-agent", input_data):
    result = your_agent.run(user_query)
```

### 2. Create Training Config

```yaml
# config.yaml
agent:
  name: "my-agent"
  type: "openai"  # openai, langchain, autogen, crewai

training:
  algorithm: "grpo"  # grpo, apo, sft, rloo
  episodes: 100
  batch_size: 16
  
environment:
  eval_tasks:
    - "math"
    - "coding"
    - "reasoning"
```

### 3. Run Training

```bash
agent-lightning train --config config.yaml
```

## Algorithms

| Algorithm | Use Case | Description |
|-----------|----------|-------------|
| **GRPO** | General RL | Group Relative Policy Optimization — stable, works well for most agents |
| **APO** | Prompt Tuning | Automatic Prompt Optimization — improves system prompts |
| **SFT** | Supervised Fine-tuning | Supervised Fine-tuning with preference data |
| **RLOO** | Long-horizon | RLOO for tasks with sparse rewards |

## Usage Commands

### `agent-lightning train`
Train your agent with configured algorithm.

### `agent-lightning eval`
Evaluate agent on benchmark tasks.

### `agent-lightning export`
Export trained model/prompts for deployment.

### `agent-lightning serve`
Launch serving endpoint for trained agent.

## Example: SQL Agent Training

See full example: [Train SQL Agent with RL](https://microsoft.github.io/agent-lightning/stable/how-to/train-sql-agent/)

```python
from agentlightning import Agent, RLConfig, GRPOTrainer

# 1. Define your agent
sql_agent = Agent(
    name="sql-agent",
    system_prompt="You are a SQL expert...",
    tools=[execute_sql, query_schema]
)

# 2. Configure RL training
config = RLConfig(
    algorithm="grpo",
    episodes=500,
    learning_rate=1e-4
)

# 3. Train
trainer = GRPOTrainer(config=config)
trainer.train(sql_agent, eval_tasks=["sql-generation"])
```

## Integration with Clawdbot

### Environment Variables

```bash
# Required for training
export OPENAI_API_KEY="sk-..."

# Optional: for remote storage
export AGL_STORAGE="s3://my-bucket/agent-lightning/"
```

### Python API

```python
from agentlightning import LightningStore, GRPOTrainer

# LightningStore keeps tasks, resources, and traces in sync
store = LightningStore()

# Read traces, learn, and update prompts
trainer = GRPOTrainer(store=store)
trainer.train(agent=my_agent)
```

## Monitoring Training

```bash
# Launch dashboard
agent-lightning dashboard --port 8080

# View logs
tail -f ~/.agent-lightning/logs/training.log
```

## Best Practices

1. **Start Small**: Begin with 10-50 episodes to verify setup
2. **Define Clear Rewards**: Design reward functions that match your goal
3. **Use Evaluation Tasks**: Always eval on held-out tasks
4. **Checkpoint Frequently**: Save model every N episodes
5. **Monitor Convergence**: Watch loss curves in dashboard

## Resources

- [Documentation](https://microsoft.github.io/agent-lightning/)
- [Examples](https://github.com/microsoft/agent-lightning/tree/main/examples)
- [API Reference](https://microsoft.github.io/agent-lightning/stable/reference/)
- [ArXiv Paper](https://arxiv.org/abs/2508.03680)
- [Discord Community](https://discord.gg/RYkC7dvDR7)

## Citation

If you use Agent Lightning in research:

```bibtex
@misc{luo2025agentlightningtrainai,
  title={Agent Lightning: Train ANY AI Agents with Reinforcement Learning},
  author={Xufang Luo and Yuge Zhang and Zhiyuan He and Zilong Wang and Siyun Zhao and Dongsheng Li and Luna K. Qiu and Yuqing Yang},
  year={2025},
  eprint={2508.03680},
  archivePrefix={arXiv},
  primaryClass={cs.AI}
}
```
