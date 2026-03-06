# Setup Guides Index

This document lists all available setup guides and their recommended order.

## Recommended Priority

Apply guides in this order for best results:

### 1. Agent Swarm Architecture ⭐⭐⭐
**Guide**: [agent-swarm.md](agent-swarm.md)

**Why First**: Establishes the foundation for multi-agent collaboration, enabling you to delegate complex tasks to specialized workers.

**When to Apply**:
- You work on complex projects with multiple parallel tasks
- You want to leverage different AI models for different tasks
- You need task tracking and monitoring

**Changes**:
- Updates AGENTS.md with task tracking rules
- Creates .tasks/ directory structure
- Configures subagent settings
- Enables heartbeat monitoring

---

### 2. Memory Optimization ⭐⭐
**Guide**: [memory-optimized.md](memory-optimized.md)

**Why Second**: Enhances OpenClaw's memory capabilities, making it easier to maintain context across long sessions.

**When to Apply**:
- You work on long-running projects
- You need to reference past decisions frequently
- You want better context retention

**Changes**:
- Enables memorySearch
- Configures memoryFlush threshold
- Sets up memory indexing

---

### 3. Proactive Monitoring ⭐⭐
**Guide**: [monitor.md](monitor.md)

**Why Third**: Enables OpenClaw to proactively discover and work on tasks, not just respond to commands.

**When to Apply**:
- You want autonomous task discovery
- You need continuous monitoring
- You want automated error recovery

**Changes**:
- Configures cron jobs
- Sets up Ralph Loop V2
- Enables proactive scanning

---

### 4. Chinese Providers ⭐⭐
**Guide**: [chinese-providers.md](chinese-providers.md)

**When to Apply**:
- You prefer Chinese AI models
- You need better Chinese language support
- You want to use models like Qwen, GLM, etc.

**Changes**:
- Adds Chinese provider configurations
- Sets up API endpoints
- Configures model fallbacks

---

### 5. Cost Optimization ⭐
**Guide**: [cost-optimization.md](cost-optimization.md)

**When to Apply**:
- You want to reduce API costs
- You need to optimize token usage
- You're working with limited budget

**Changes**:
- Configures model fallbacks
- Enables caching
- Optimizes prompt strategies

---

## Quick Start

### Apply All Recommended Guides

```
Apply agent-swarm guide, then memory-optimized guide, then monitor guide
```

### Apply Specific Guide

```
Apply agent-swarm guide
```

### Check Current Configuration

```
Show me the current AGENTS.md
```

---

## Customization

After applying a guide, you can customize it:

1. Read the generated files in `workspace/`
2. Modify settings in `openclaw.json`
3. Adjust AGENTS.md rules
4. Test with simple tasks

The AI will respect your customizations while applying future guides.
