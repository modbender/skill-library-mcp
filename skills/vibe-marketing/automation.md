# Workflow Automation

## The Vibe Marketing Stack

Three layers:
1. **LLMs** — Content generation (ChatGPT, Claude)
2. **Automation** — Workflow orchestration (Make, n8n, Zapier)
3. **Creative Tools** — Visual production (Canva, HeyGen)

## Common Automation Workflows

### Content Repurposing Pipeline
```
Trigger: New blog post published
→ AI: Extract 5 key insights
→ AI: Generate LinkedIn post from insight #1
→ AI: Generate Twitter thread from insights
→ Queue to scheduling tool
→ Human: Review before publish
```

### Social Listening + Response
```
Trigger: Brand mention detected
→ AI: Classify sentiment (positive/negative/question)
→ Branch:
  - Positive → Draft thank you reply
  - Question → Draft helpful response
  - Negative → Alert human, don't auto-reply
→ Human: Approve responses
```

### Email Nurture Generator
```
Trigger: New lead segment identified
→ AI: Generate 5-email sequence based on segment persona
→ Human: Review and edit
→ Load into email platform
→ Monitor: Flag low-performing emails for revision
```

### Ad Creative Scaling
```
Trigger: Weekly ad refresh needed
→ AI: Generate 10 headline variants
→ AI: Generate 5 description variants
→ Human: Select top combinations
→ Upload to ad platform
→ Monitor: Pause underperformers automatically
```

## Tools by Complexity

| Complexity | Tool | Best For |
|------------|------|----------|
| Simple | Zapier | Beginners, basic triggers |
| Medium | Make | Visual workflows, flexibility |
| Complex | n8n | Technical teams, self-hosted |
| Agent-based | Relay, Taskade | Multi-step autonomous tasks |

## Human Checkpoints

Always require human approval for:
- ❌ First message to a new audience
- ❌ Responses to complaints or negative feedback
- ❌ Content touching sensitive topics
- ❌ High-budget ad spend decisions
- ❌ Messaging that could be misread

Automate fully:
- ✅ Internal content digests
- ✅ Drafts for human review
- ✅ Data aggregation and reporting
- ✅ Scheduling and distribution
- ✅ A/B test variant generation

## Anti-Patterns

### Over-Automation
- Publishing without review leads to brand damage
- AI replies to customers feel cold
- Automation debt accumulates fast

### Under-Automation
- Still manually posting to 5 platforms
- Copy-pasting between tools
- Scheduling one post at a time

### Wrong Automation
- Automating things that need judgment
- Not automating things that are pure repetition
