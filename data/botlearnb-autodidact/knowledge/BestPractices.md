---
domain: openclaw-autodidact
topic: best-practices
priority: high
ttl: 30d
---

# Self-Learning Best Practices

## Task Discovery

### 1. Memory Query Best Practices

**Effective Query Patterns**:
```json
// Query for unsatisfied tasks
{
  "status": "unsatisfied",
  "satisfaction": { "$lt": 0.6 },
  "limit": 20,
  "sort": { "timestamp": 1 },
  "fields": ["id", "request", "feedback", "skillsUsed"]
}

// Query for incomplete tasks
{
  "status": "incomplete",
  "lastActivity": { "$gte": "now-7d" }
}

// Query for explicitly failed tasks
{
  "status": "failed",
  "errors": { "$exists": true }
}
```

### 2. Task Selection Strategy

**FIFO (First In, First Out)**:
- Select earliest unsatisfied task
- Ensures old problems don't get forgotten
- Fair across all user requests

**Priority-based**:
- Consider user sentiment
- Consider task complexity
- Consider business impact

**Avoiding Repeats**:
- Track attempted solutions
- Don't retry same failed approach
- Wait for new information before retrying

## Skill Search Best Practices

### 1. Effective Search Queries

**By task description**:
```
"site:npmjs.com @botlearn [task keywords]"
Example: "site:npmjs.com @botlearn rest api authentication"
```

**By problem type**:
```
Task Type           Search Terms
─────────────────────────────────────────
Code generation    "code-gen", "code", "generate"
Writing            "writer", "copywriter", "content"
Research           "search", "academic", "find"
Translation        "translator", "translate"
Analysis           "summarizer", "analyzer", "extract"
```

**By capability**:
```
Capability                  Keywords
────────────────────────────────────────────
Natural language processing  nlp, language, text
Data processing            data, process, transform
API interaction            api, rest, graphql
Web scraping               scrape, extract, fetch
File operations            file, read, write
```

### 2. Skill Evaluation

**Before installing, check**:
1. **Relevance**: Does description match the problem?
2. **Rating**: Does it have good reviews/usage?
3. **Maintenance**: Recently updated?
4. **Dependencies**: Are dependencies reasonable?
5. **Compatibility**: Compatible with current OpenClaw version?

**Evaluation checklist**:
```
✓ manifest.json exists and valid
✓ Category matches task type
✓ Expected improvement > 20
✓ Compatible with OpenClaw >=0.5.0
✓ Dependencies are @botlearn/* or stable packages
✓ Description mentions relevant capabilities
✓ Not a duplicate of already installed skill
```

### 3. Installation Best Practices

**Batch vs Sequential**:
- **Sequential**: Install one skill, test, then next
- **Batch**: Install multiple complementary skills together
- **Recommendation**: Sequential for first attempt, batch for known combinations

**Testing after install**:
```
1. Run smoke test (if available)
2. Test skill in isolation
3. Test skill with original task
4. Compare output quality
5. Document results
```

## Community Engagement Best Practices

### 1. Joining the Community

**Preparation before joining**:
1. Read community guidelines
2. Understand norms and culture
3. Prepare introduction
4. Know what you want to learn

**First actions after joining**:
```
Day 1: Read welcome channel, introduce yourself
Day 2-3: Read recent posts, get familiar
Day 4-7: Engage with others' posts (comments, reactions)
Day 7+: Start posting your own questions
```

### 2. Effective Question Asking

**BEFORE posting**:
1. Search if question already asked
2. Read documentation
3. Try to solve yourself first
4. Document what you've tried

**Question template**:
```markdown
### What I'm trying to do
[Clear description of goal]

### What I've tried
- Approached with skill X: [result]
- Tried method Y: [result]
- Read documentation: [what was unclear]

### Current blocker
[Specific issue preventing progress]

### Context
- OpenClaw: [version]
- Skills: [list installed]
- Error: [if any]

### Question
[Specific, answerable question]
```

**After getting answers**:
- Thank the responder
- Report back what worked
- Share solution with others
- Update documentation if helpful

### 3. DM Best Practices

**When to DM vs. Post**:
```
DM:
- Follow-up on public discussion
- Private collaboration
- Mentoring requests
- Sensitive topics

Post:
- General questions
- Bug reports
- Feature requests
- Showcasing work
```

**DM structure**:
```
Subject Line: [Context] Question about [Topic]

Hi [Name],

[Context about why you're DMing]
[I saw your post / We spoke in channel / etc.]

[Question or request]
[Offer value in return if possible]

Thanks,
[Your Name and context]
```

## Learning Loop Best Practices

### 1. Documentation

**Track each learning cycle**:
```json
{
  "cycleId": "cycle-2026-03-02-01",
  "timestamp": "2026-03-02T12:00:00Z",
  "taskId": "task-abc",
  "methodsAttempted": {
    "skillSearch": {
      "searches": 3,
      "skillsFound": 5,
      "skillsInstalled": 1,
      "result": "partial"
    },
    "community": {
      "platform": "discord",
      "postsRead": 10,
      "dmsSent": 2,
      "result": "helpful"
    }
  },
  "outcome": "improved",
  "lessonsLearned": [
    "Skill X partially solves the problem",
    "Community member Y has similar experience"
  ]
}
```

### 2. Pattern Recognition

**Successful patterns to record**:
```
Pattern: [Problem type]
Solution: [What worked]
Skills: [Required skills]
Source: [Where found]
Success Rate: [X%]
```

**Failed patterns to avoid**:
```
Pattern: [Approach that doesn't work]
Reason: [Why it fails]
Alternative: [What to try instead]
```

### 3. Knowledge Integration

**When a solution works**:
1. Document the specific steps
2. Note required skills/configurations
3. Record for similar future tasks
4. Share with user if generally useful

**When a solution partially works**:
1. Document what part works
2. Identify what's still missing
3. Set up follow-up learning
4. Consider combining approaches

## Timer & Scheduling Best Practices

### 1. Interval Selection

**4-hour default rationale**:
- Frequent enough to catch recent issues
- Infrequent enough to not be annoying
- Allows time for community responses
- Balances system load

**Adjustment factors**:
```
Increase interval if:
- User reports too many notifications
- System resources constrained
- Few unsolved tasks found

Decrease interval if:
- Active development period
- Many urgent unsolved tasks
- User requests more frequent learning
```

### 2. Resource Management

**Rate limiting per cycle**:
```
Max web searches:     10
Max skills to scan:   20
Max skills to install: 3
Max community posts:  1
Max DMs:              5
Max execution time:   10 minutes
```

**Priority queuing**:
```
Critical tasks: Execute immediately
High tasks:       Execute in current cycle
Medium tasks:     Schedule for next cycle
Low tasks:        Schedule when queue empty
```

### 3. User Notification

**When to notify**:
- ✅ Successfully solved a problem
- ✅ Found promising solution (awaiting approval)
- ⚠️ Attempted but need user input
- ❌ Failed after multiple attempts

**Notification format**:
```
🎓 Learning Update

Task: [Original request]
Status: [Improved / Solved / Stuck]
Action: [What was done]
Result: [What happened]
Next: [What's next]

[View details | Adjust settings | Pause learning]
```

## Safe Learning Practices

### 1. Pre-Installation Checks

**Verify skill authenticity**:
```
1. Check scope is @botlearn
2. Verify on npmjs.com
3. Check GitHub repository (if linked)
4. Look for maintainer verification
5. Scan for unusual file patterns
```

### 2. Sandbox Testing

**Test new skills safely**:
```
1. Install with --dry-run first
2. Review files that will be created
3. Test with non-critical task
4. Monitor system behavior
5. Roll back if issues detected
```

### 3. Community Safety

**Before posting**:
```
1. Remove sensitive data
2. Anonymize user information
3. Don't share API keys or tokens
4. Don't reveal proprietary information
5. Use screenshots instead of logs when appropriate
```

## Measuring Learning Effectiveness

### Success Metrics

**Per-cycle metrics**:
```
Tasks Attempted:     [N]
Tasks Improved:      [N] (N%)
Tasks Solved:        [N] (N%)
Skills Installed:    [N]
Community Posts:     [N]
Success Rate:        [N]%
```

**Long-term metrics**:
```
Unsolved Tasks Trend: [↓ is good]
Average Task Age:      [↓ is good]
User Satisfaction:    [↑ is good]
Self-Sufficiency:      [↑ is good]
```

### Continuous Improvement

**Regular reviews** (weekly):
- What tasks are still unsolved?
- Which methods work best?
- Are skills helpful?
- Is community engaged?

**Adjust based on metrics**:
- Change search strategy if success rate low
- Adjust timer if too frequent/infrequent
- Modify notification preferences
- Update skill evaluation criteria
