# Identifying and Closing Loops

## What Is a Loop?

A loop is any process where you:
1. Receive input (request, data, notification)
2. Make decisions
3. Execute or delegate action
4. Check results
5. Decide what's next

The goal: Design loops that close themselves.

---

## Loop Anatomy

| Component | Manual | Automated |
|-----------|--------|-----------|
| Input | You notice | Agent monitors |
| Decision | You think | Agent decides (with guardrails) |
| Action | You do | Agent executes |
| Check | You verify | Agent validates |
| Next step | You decide | Agent continues or escalates |

---

## Signs You Can Close a Loop

- You're just saying "yes" or "approved" most of the time
- The exceptions are rare and predictable
- You've documented the decision criteria
- Mistakes are recoverable (not catastrophic)
- You've done it manually long enough to know the patterns

---

## How to Close a Loop

### Step 1: Document the decision tree
"When X happens, do Y. Unless Z, then do W."

### Step 2: Define escalation triggers
"Escalate to me when: [specific conditions]"

### Step 3: Test in parallel
Let the agent handle it while you shadow-verify. Compare decisions.

### Step 4: Release with monitoring
Step back, but track outcomes. Intervene only on escalations.

### Step 5: Audit and refine
Periodically review: Are escalations reducing? Are outcomes good?

---

## Loop Categories

### Quick Wins (Close First)
- Routine approvals with clear criteria
- Status updates and reporting
- Standard communications
- Data gathering and formatting

### Medium Effort
- Customer support triage
- Code reviews with clear standards
- Content creation with templates
- Research with defined scope

### Complex (Close Later)
- Strategy decisions
- Novel problem-solving
- High-stakes negotiations
- Creative direction

---

## Connecting Loops

Individual loops are valuable. Connected loops are powerful.

Example chain:
```
Research → Analysis → Recommendations → Implementation → Monitoring
   ↓          ↓             ↓                ↓              ↓
 Agent     Agent        Agent (you pick)   Agent        Agent
```

You only enter the chain at decision points. The rest flows.

---

## Warning Signs

**Don't close if:**
- You're not sure what "good" looks like
- Failures are irreversible or high-cost
- You haven't done it manually enough
- The domain is changing rapidly

**Close partially:**
- Agent prepares, you decide
- Agent decides, you audit weekly
- Agent handles 80%, escalates 20%

---

## Tracking

Create `~/vibe-clawing/loops.md` to track:
```
## Closed Loops
- [Research]: Fully automated since [date]. Review: monthly.
- [Code formatting]: Agent handles. No issues.

## In Progress
- [Customer triage]: Testing parallel run. 85% agreement.

## Candidates
- [Weekly reports]: Good candidate. Documenting criteria.

## Not Ready
- [Pricing decisions]: Too consequential. Manual.
```
