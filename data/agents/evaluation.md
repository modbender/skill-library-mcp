# Agent Evaluation & Debugging

## Metrics by Category

### Task Completion
| Metric | Description | Target |
|--------|-------------|--------|
| **Success rate** | Tasks completed correctly | >90% for production |
| **Completion time** | Average time to task done | Depends on task type |
| **Turns per task** | Agent turns needed | Lower is better |
| **Tool calls per task** | Efficiency of tool use | Minimize unnecessary calls |

### Quality
| Metric | Description | How to Measure |
|--------|-------------|----------------|
| **Response accuracy** | Correctness of outputs | Human eval, ground truth |
| **Hallucination rate** | False claims made | Spot-check random outputs |
| **Relevance** | Output matches user intent | User satisfaction survey |
| **Format compliance** | Follows required structure | Automated schema validation |

### Safety
| Metric | Description | Target |
|--------|-------------|--------|
| **Escalation rate** | Tasks handed to human | 5-15% typical |
| **False escalation** | Unnecessary handoffs | <2% |
| **Boundary violations** | Attempted forbidden actions | 0% |
| **Prompt injection resistance** | Attacks detected/blocked | 100% |

### Cost
| Metric | Description | Track |
|--------|-------------|-------|
| **Cost per task** | Total LLM + API costs | By task type |
| **Cost per user** | Daily/monthly spend | By user tier |
| **Token efficiency** | Useful tokens vs overhead | Optimize prompts |

## Debugging Workflow

### Step 1: Check Context
- Is relevant information in the context window?
- Is old/stale context confusing the agent?
- Are system prompt instructions clear?

### Step 2: Check Tool Results
- Did tools return expected data?
- Did tools error silently?
- Is tool output format correct?

### Step 3: Check Reasoning
- Add chain-of-thought to see agent thinking
- Is the agent's interpretation correct?
- Where did reasoning go wrong?

### Step 4: Check Confidence
- Does agent know when it's uncertain?
- Is it asking for clarification when needed?
- Is it overconfident on edge cases?

## Common Failure Modes

### Infinite Loops
**Symptom:** Agent keeps calling same tool
**Cause:** Tool doesn't change state, agent retries same strategy
**Fix:** Add loop detection, force alternative strategy after N attempts

### Context Drift
**Symptom:** Agent "forgets" earlier instructions
**Cause:** Long conversations push system prompt out of context
**Fix:** Summarize periodically, re-inject key instructions

### Hallucinated Tool Calls
**Symptom:** Agent calls tools with made-up parameters
**Cause:** Ambiguous tool descriptions, missing validation
**Fix:** Stricter tool schemas, validate params before execution

### Over-Escalation
**Symptom:** Agent hands off too many tasks
**Cause:** Overly cautious escalation rules, unclear confidence
**Fix:** Train on borderline examples, add confidence scoring

### Under-Escalation
**Symptom:** Agent handles tasks it shouldn't
**Cause:** Missing escalation triggers, poor sentiment detection
**Fix:** Add keyword triggers, improve emotion detection

## Testing Strategy

### Unit Tests
- Each tool works correctly in isolation
- Prompt templates produce expected format
- Parser handles edge cases

### Integration Tests
- Agent + tools work together
- Memory retrieval returns relevant context
- Escalation paths function correctly

### Adversarial Tests
- Prompt injection attempts
- Malformed inputs
- Edge cases and boundary conditions
- Attempts to exceed permissions

### User Simulation
- Replay real conversations
- Vary user patience levels
- Test unclear/ambiguous requests

## Evaluation Dataset Structure

```json
{
  "test_case_id": "order_status_001",
  "user_input": "Where is my order #12345?",
  "expected_tool_calls": ["lookup_order"],
  "expected_output_contains": ["shipped", "tracking"],
  "expected_output_excludes": ["sorry", "cannot"],
  "max_turns": 2,
  "tags": ["order_tracking", "happy_path"]
}
```

## Continuous Monitoring

### Real-Time Alerts
- Task failure rate spike
- Cost exceeds threshold
- Escalation rate anomaly
- Negative sentiment increase

### Weekly Review
- Sample random conversations for quality
- Review escalated cases
- Identify patterns in failures
- Update training data/prompts
