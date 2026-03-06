# Council Deliberation Guide

Use multiple AI models as a "board of advisors" for technical decisions.

## When to Use Council Mode

- **Architecture decisions** - System design with long-term implications
- **Technology selection** - Choosing frameworks, databases, patterns
- **Risk assessment** - Security review, failure mode analysis
- **Complex tradeoffs** - No clear "right answer"
- **Breaking deadlocks** - When you're stuck between options

## Model Role Assignments

### The Architect (Opus)
```
Prompt prefix: "As a senior software architect with 20 years of experience, 
focusing on long-term maintainability, scalability, and edge cases..."
```
**Strengths**: Deep analysis, sees implications others miss
**Ask about**: Architecture patterns, security concerns, 5-year outlook

### The Pragmatist (Sonnet)
```
Prompt prefix: "As a practical senior engineer focused on shipping quality 
software efficiently, balancing ideal solutions with real-world constraints..."
```
**Strengths**: Time-to-market, pragmatic tradeoffs, MVP thinking
**Ask about**: Implementation effort, quick wins, technical debt balance

### The Challenger (GPT-5 / External Model)
```
Prompt prefix: "As an engineer from a different background, challenge 
assumptions and propose alternative approaches that might be overlooked..."
```
**Strengths**: Different training data, breaks groupthink
**Ask about**: Alternative patterns, industry practices, unconventional solutions

### The Specialist (Qwen / Domain-Specific)
```
Prompt prefix: "As an expert in [Chinese market / specific domain], 
considering local ecosystem, compliance, and cultural factors..."
```
**Strengths**: Domain expertise, local knowledge
**Ask about**: Regional requirements, specialized tooling

## Deliberation Workflow

### Phase 1: Frame the Question
```markdown
## Topic: [Decision Title]

### Background
[2-3 sentences of context]

### Options Under Consideration
1. Option A: [description]
2. Option B: [description]
3. Option C: [description]

### Evaluation Criteria
- Performance
- Maintainability
- Cost
- Time to implement
- Team familiarity

### Constraints
- [Budget, timeline, technical constraints]
```

### Phase 2: Parallel Consultation
Launch all models simultaneously with tailored prompts:

```bash
# Session setup
for role in opus sonnet gpt; do
  tmux new-session -d -s council-$role
done

# Opus query
tmux send-keys -t council-opus "agent --model claude-opus-4 -p '
You are a senior architect. Analyze this decision:

[Paste framed question]

Provide:
1. Your recommended option and detailed rationale
2. Long-term implications of each option
3. Edge cases and failure modes to consider
4. What would change your recommendation
' --force" Enter

# Sonnet query  
tmux send-keys -t council-sonnet "agent --model claude-sonnet-4 -p '
You are a pragmatic engineer. Evaluate this decision:

[Paste framed question]

Provide:
1. Your recommended option with implementation estimate
2. Quickest path to production-ready
3. Technical debt implications
4. What would you prototype first
' --force" Enter

# GPT query
tmux send-keys -t council-gpt "agent --model gpt-5 -p '
Challenge conventional thinking on this decision:

[Paste framed question]

Provide:
1. An alternative approach not listed
2. Assumptions that might be wrong
3. How other companies solve this differently
4. Contrarian perspective on the popular choice
' --force" Enter
```

### Phase 3: Collect & Synthesize

After all models respond (~2-5 minutes):

```bash
# Capture all outputs
for role in opus sonnet gpt; do
  echo "=== $role ===" >> council-output.md
  tmux capture-pane -t council-$role -p -S -500 >> council-output.md
done
```

### Phase 4: Synthesis Template

```markdown
## Council Summary: [Topic]

### Individual Recommendations

| Model | Recommendation | Confidence | Key Concern |
|-------|---------------|------------|-------------|
| Opus | Option B | High | Long-term scaling |
| Sonnet | Option A | Medium | Implementation speed |
| GPT | Option D (new) | Medium | Industry trend |

### Consensus Points
All models agree that:
- [Point 1]
- [Point 2]

### Key Divergences

**On [Topic 1]:**
- Opus: [view]
- Sonnet: [view]  
- GPT: [view]
- Analysis: [why they differ]

### Risks Identified
| Risk | Flagged By | Severity | Mitigation |
|------|-----------|----------|------------|
| [Risk 1] | Opus | High | [suggestion] |
| [Risk 2] | GPT | Medium | [suggestion] |

### Synthesized Recommendation

**Recommended: Option [X]**

Rationale:
1. [Key point from Opus]
2. [Practical consideration from Sonnet]
3. [Incorporated insight from GPT]

**With modifications:**
- [Adjustment based on council feedback]

### Open Questions for Human Decision
1. [Trade-off that requires human judgment]
2. [Business context only human knows]
```

## Advanced Patterns

### Debate Mode
Have models respond to each other:
```
Round 1: Each model gives initial position
Round 2: Each model critiques another's position
Round 3: Each model gives final recommendation considering critiques
```

### Red Team Mode
Assign one model to attack proposed solution:
```
Opus: Propose solution
GPT: Attack the solution, find weaknesses
Sonnet: Defend and patch weaknesses
```

### Consensus Building
Keep iterating until convergence:
```
Round N: Present all positions to each model
         Ask: "Given these perspectives, what's your updated view?"
Repeat until positions stabilize
```

## Cost Considerations

| Model | Relative Cost | When to Use |
|-------|--------------|-------------|
| Opus | $$$ | High-stakes decisions |
| Sonnet | $ | Quick consultations |
| GPT-5 | $$ | Diversity of perspective |

For budget-conscious councils:
- Use Sonnet for initial exploration
- Bring in Opus only for final deep-dive
- Use GPT sparingly for fresh perspectives
