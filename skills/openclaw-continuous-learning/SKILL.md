---
name: openclaw-continuous-learning
slug: openclaw-continuous-learning
version: 1.1.0
description: |
  Instinct-based learning system for OpenClaw. Analyzes sessions, detects patterns, creates atomic learnings with confidence scoring, and suggests optimizations for self-evolution.
  
  Use when: you want your AI agent to learn from its own behavior, improve over time, discover optimization opportunities, or build a self-improving automation system.
  
  Don't use when: static agent behavior is preferred.
triggers:
  - continuous learning
  - self improving agent
  - agent evolution
  - pattern detection
  - session analysis
  - ai learning
  - agent optimization
  - automation improvement
  - self evolution
metadata:
  openclaw:
    emoji: "🧠"
    requires:
      bins: ["node"]
---

# Continuous Learning for AI Agents

An instinct-based learning system that helps AI agents improve themselves through observation and pattern detection.

## What This Skill Does

- **Analyzes session history** - Reviews agent interactions and outputs
- **Detects patterns** - Identifies recurring behaviors, preferences, workflows
- **Creates instincts** - Atomic learnings with confidence scores
- **Suggests optimizations** - Based on observed behavior patterns
- **Enables self-evolution** - Converts insights into improvements

## When to Use

**Use when:**
- Building self-improving AI agents
- Want agent to learn from interactions
- Discovering optimization opportunities
- Creating adaptive automation
- Tracking behavioral patterns

**Skip when:**
- Static, unchanging behavior preferred
- No session history available
- Simple, deterministic workflows only

## Architecture

```
Session Activity
 │
 ▼
┌─────────────────────────────────────────┐
│ Session Analysis                         │
│ • Read interaction logs                  │
│ • Detect patterns                       │
│ • Create instincts                       │
└─────────────────────────────────────────┘
 │
 ▼
┌─────────────────────────────────────────┐
│ Instinct Storage                         │
│ • instincts.jsonl (atomic learnings)     │
│ • patterns.json (aggregated)             │
│ • optimizations.json (suggestions)       │
└─────────────────────────────────────────┘
 │
 ▼
┌─────────────────────────────────────────┐
│ Optimization Delivery                    │
│ • Daily tips                            │
│ • Configuration suggestions             │
│ • Workflow improvements                 │
└─────────────────────────────────────────┘
```

## Confidence Scoring

| Score | Meaning | Behavior |
|-------|---------|----------|
| 0.3 | Tentative | Suggested but not enforced |
| 0.5 | Moderate | Applied when relevant |
| 0.7 | Strong | Auto-approved |
| 0.9 | Core behavior | Always apply |

**Confidence increases when:**
- Pattern observed repeatedly
- User doesn't correct behavior
- Multiple observations agree

**Confidence decreases when:**
- User explicitly corrects
- Pattern not observed recently
- Contradicting evidence appears

## Key Concepts

### Instincts

An instinct is a small learned behavior:

```yaml
id: prefer-simplicity
trigger: "when solving problems"
confidence: 0.7
domain: problem_solving
---
# Prefer Simple Solutions

## Action
Always choose the simplest solution that meets requirements.

## Evidence
- Observed preference for minimal code
- User corrected over-engineered approaches
```

### Patterns

Aggregated observations grouped by category:
- code_style
- testing
- git
- debugging
- workflow
- communication

### Optimizations

Actionable improvements derived from patterns.

## Use Cases

### 1. Agent Self-Improvement

```
Agent observes its own sessions:
- What works consistently?
- What gets corrected?
- What patterns emerge?

Creates instincts → Applies high-confidence patterns
```

### 2. User Preference Learning

```
Learn user preferences from interactions:
- Coding style preferences
- Communication preferences
- Workflow preferences

Adapt behavior accordingly
```

### 3. Performance Optimization

```
Detect performance patterns:
- Slow operations
- Bottlenecks
- Optimization opportunities

Suggest improvements
```

### 4. Error Pattern Detection

```
Track error patterns:
- Common failures
- Resolution strategies
- Prevention approaches

Build error-handling instincts
```

## Quick Start

```bash
# Analyze sessions
node /path/to/scripts/analyze.mjs

# List learned instincts
node /path/to/scripts/analyze.mjs instincts

# Show optimizations
node /path/to/scripts/analyze.mjs list
```

## Setup

### 1. Create storage directory

```bash
mkdir -p ~/.openclaw/workspace/memory/learning
```

### 2. Schedule analysis

Add to cron for periodic analysis:

```json
{
  "id": "continuous-learning",
  "schedule": "0 22 * * *"
}
```

### 3. Integrate with daily tips

Connect to daily summary for optimization delivery.

## File Structure

```
~/.openclaw/workspace/
└── memory/
    └── learning/
        ├── instincts.jsonl    # Atomic learnings
        ├── patterns.json      # Aggregated patterns
        └── optimizations.json # Suggestions
```

## Example Output

```
🧠 Learning Report

Patterns Detected:
- prefer-simplicity (0.7) ↑2
- test-first (0.5) ↑1
- commit-often (0.3) new

Confidence Changes:
- minimal-code: 0.5 → 0.7

Suggested:
1. Prioritize simple solutions
2. Add pre-commit hooks
3. Enable stricter typing
```

## Best Practices

1. **Start simple** - Few patterns, low confidence
2. **Validate often** - Check if patterns still hold
3. **Review suggestions** - Don't auto-apply everything
4. **Track confidence** - Update based on results
5. **Export/share** - Build library of common patterns

## FAQ

**How is this different from memory?**
Memory stores facts. This learns behavioral patterns and preferences.

**How long to see results?**
Depends on session volume. Typically 1-2 weeks for meaningful patterns.

**Is it safe to auto-apply?**
Only high-confidence (0.7+) patterns. Always review suggestions first.

## Related Skills

- **skill-engineer** - Quality-gated skill development
- **compound-engineering** - Session review and learning
- **memory-setup** - Memory configuration
- **openclaw-daily-tips** - Daily optimization tips

---

**Version:** 1.1.0  
**Inspired by:** Anthropic's continuous learning patterns, Claude Code homunculus
