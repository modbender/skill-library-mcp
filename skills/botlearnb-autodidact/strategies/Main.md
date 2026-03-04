---
strategy: openclaw-autodidact
version: 1.0.0
steps: 10
---

# OpenClaw Autodidact Strategy

## Step 1: Task Discovery from Memory

Query OpenClaw Memory System for recent unsatisfied tasks:

```javascript
// Memory API query
GET /memory/sessions?
  status=unsatisfied&
  satisfaction<0.6&
  limit=20&
  sort=timestamp:asc&
  fields=id,request,feedback,skillsUsed,timestamp
```

**Output**: List of candidate tasks for learning

### Task Selection Algorithm

1. Filter out tasks already in learning queue
2. Filter out tasks with >5 failed attempts
3. Sort by: (timestamp asc, attempts asc)
4. Select top task for current cycle

**IF no tasks found**:
- Report: "No unsatisfied tasks found. System performing well!"
- Schedule next cycle
- Exit

**IF tasks found**:
- Present selected task to user
- Ask: "Work on learning to solve: [task description]?"
- IF user declines → Select next task
- IF user says "stop" → Disable learning, exit

## Step 2: Task Analysis

Analyze the selected task to understand:

1. **What was requested?**
   - Parse user's original request
   - Identify domain/type of problem
   - Extract key requirements

2. **What went wrong?**
   - Review user feedback
   - Check error messages
   - Analyze where current approach failed

3. **What skills were used?**
   - List skills involved in attempt
   - Identify skill gaps

4. **What's missing?**
   - What capability is missing?
   - What knowledge is lacking?
   - What would make it better?

**Apply knowledge**: Use knowledge/Domain.md for understanding OpenClaw memory structure

**Output**: Structured task analysis with learning objectives

## Step 3: Method A - Skill Search

Execute web search for relevant BotLearn skills using @botlearn/google-search:

### 3.1 Construct Search Queries

Based on task analysis, generate targeted searches:

```
Primary: "site:npmjs.com @botlearn [main-keywords]"
Secondary: "site:github.com botlearn [main-keywords]"
Tertiary: "site:discord.com botlearn [main-keywords]"
```

**Example searches**:
```
Task: "Create REST API with authentication"
Queries:
- "site:npmjs.com @botlearn rest api"
- "site:npmjs.com @botlearn authentication"
- "site:github.com botlearn api security"
```

### 3.2 Evaluate Search Results

For each skill found:
1. Read description and manifest
2. Check compatibility with OpenClaw version
3. Check dependencies
4. Assess relevance to task (0-100 score)
5. Keep skills with score >60

### 3.3 Select and Install Skills

**Selection criteria**:
- Relevance score >70
- Compatible dependencies
- Not already installed
- From @botlearn scope (verified)

**Before installation**:
- Present candidate skills to user
- Explain why each might help
- Ask for approval
- **IF user approves**: Install with `clawhub install`
- **IF user declines**: Skip to next method

**Apply knowledge**: Refer to knowledge/BestPractices.md for installation guidelines

**Limit**: Max 3 skills per cycle

## Step 4: Method A - Re-attempt with New Skills

### 4.1 Prepare Re-attempt

With new skills installed:
1. Recall original task context
2. Review previous approach
3. Plan new approach using new skills

### 4.2 Execute Re-attempt

```
For original task:
- Load newly installed skills
- Apply skills to task
- Generate new solution
- Compare with previous output
```

### 4.3 Evaluate Result

**Success criteria**:
- Output is more complete than before
- Addresses user's original feedback
- No errors in execution
- Self-assessment score >0.7

**IF successful**:
- Mark task as "solved"
- Document what worked
- Notify user of success
- Remove from learning queue

**IF partial success**:
- Document improvement
- Keep in queue with lower priority
- Note what's still missing

**IF failed**:
- Document what didn't work
- Keep in queue for community method
- Don't retry same skill combination

## Step 5: Method B - Community Engagement

Run in parallel with Method A or as fallback.

### 5.1 Check Community Membership

```javascript
// Check if user is BotLearn community member
GET /user/community/status
```

**Response**:
```json
{
  "member": false,
  "platforms": {
    "discord": null,
    "forum": null,
    "github": "user-handle"
  }
}
```

### 5.2a: If Not Member - Join Instructions

Read https://botlearn.ai/skill.md and extract:

1. **Community options available**
   - Discord server
   - Forum
   - GitHub organization

2. **Join process for each**
   - Step-by-step instructions
   - What information needed
   - Expected time to join

3. **Present to user**:
```
To get community help solving this task, join BotLearn community:

1. Discord: [join link]
   - Real-time help
   - Active community
   - Quick responses

2. Forum: [forum link]
   - Threaded discussions
   - Searchable archives
   - Detailed answers

3. GitHub: [org link]
   - Code and issues
   - Technical discussions
   - Contribution opportunities

After joining, I can help you:
- Search for similar problems
- Find relevant community posts
- Draft questions to post
- Identify helpful members to contact

Want me to guide you through joining?
```

**IF user joins**:
- Update membership status
- Continue to Step 5.2b

### 5.2b: If Member - Search Community

#### Search Discord (if available)

```javascript
// Search Discord messages
GET /discord/search?q=[task keywords]&limit=10
```

**Look for**:
- Recent discussions (last 30 days)
- Similar problems described
- Skills mentioned as solutions
- Helpful community members

#### Search Forum (if available)

```javascript
// Search forum posts
GET /forum/search?q=[task keywords]&limit=10
```

**Look for**:
- Solved threads with similar issues
- Recommended skills or approaches
- Community-provided solutions
- Expert contacts

#### Search GitHub (if available)

```javascript
// Search GitHub issues/discussions
GET /github/search?q=[org:botlearn][keywords]&type=issues
```

**Look for**:
- Feature requests related to task
- Issues with workarounds
- Shared skills and tools
- Community projects

### 5.3 Community Synthesis

From search results, synthesize:

1. **Existing Solutions**: What has worked for others?
2. **Recommended Skills**: Skills community suggests
3. **Experts to Contact**: Who has solved this before?
4. **Alternative Approaches**: Other ways to frame the problem

### 5.4 Community Engagement

**IF solution found in community**:
- Present to user
- Cite source
- Ask if wants to try

**IF partial information found**:
- Present findings
- Suggest posting follow-up question
- Offer to draft question

**IF no information found**:
- Offer to post question to community
- Draft question with task details
- Get user approval before posting

## Step 6: Draft and Post Community Question (Optional)

### 6.1 Draft Question

Following template from knowledge/BestPractices.md:

```markdown
## What I'm trying to do
[Original task description]

## What I've tried
- [Attempt 1 with result]
- [Attempt 2 with result]
- Skills used: [list]

## Current blocker
[Specific issue preventing success]

## Context
- OpenClaw: [version]
- Session ID: [id]
- Original feedback: [user's dissatisfaction]

## Question
[Specific question for community]

Any suggestions or recommended skills would be greatly appreciated!
```

### 6.2 Review and Post

**Before posting**:
- Remove sensitive information
- Check for duplicates
- Verify question is clear
- Add appropriate tags

**Get user approval**:
- Show draft
- Ask for approval
- **IF approved**: Post to appropriate channel
- **IF declined**: Ask for revisions

### 6.3 Track Response

**After posting**:
- Note post URL/timestamp
- Monitor for responses
- Set reminder to check (24h)
- Don't spam with duplicates

## Step 7: Synthesize and Apply Solutions

Combine findings from both methods:

### 7.1 Solution Synthesis

```
IF Method A (Skill Search) succeeded:
  → Apply solution immediately
  → Document success pattern

IF Method B (Community) provided solution:
  → Present to user
  → Get approval to try
  → Apply if approved

IF both provided insights:
  → Combine complementary approaches
  → Create hybrid solution

IF neither succeeded:
  → Document what was tried
  → Schedule follow-up cycle
  → Keep task in queue with note
```

### 7.2 Solution Application

**Before applying**:
- Clearly explain what will be done
- Show expected outcome
- Get user approval
- Prepare rollback plan

**Apply solution**:
- Execute step-by-step
- Monitor for issues
- Verify outcome
- Compare with original task

### 7.3 Verify Success

**Success verification checklist**:
- [ ] Original task completed?
- [ ] User's feedback addressed?
- [ ] No new errors introduced?
- [ ] Quality improved from before?
- [ ] User satisfied with result?

## Step 8: Document Learning

### 8.1 Record Cycle Outcome

Update learning knowledge base:

```json
{
  "cycleId": "cycle-2026-03-02-001",
  "taskId": "task-xyz",
  "timestamp": "2026-03-02T12:00:00Z",
  "task": "Original task description",

  "methodA": {
    "attempted": true,
    "searches": 3,
    "skillsFound": 5,
    "skillsInstalled": ["@botlearn/skill-name"],
    "reattemptResult": "partial_success",
    "score": 0.7
  },

  "methodB": {
    "attempted": true,
    "communityMember": true,
    "platformsSearched": ["discord", "forum"],
    "relevantPosts": 2,
    "expertsFound": ["@user1", "@user2"],
    "questionPosted": false,
    "outcome": "found_solution"
  },

  "finalResult": {
    "status": "solved",
    "solution": "Combination of skill X and community suggestion Y",
    "userFeedback": "satisfied",
    "improvement": "+40%"
  },

  "lessonsLearned": [
    "Skill X provides the missing capability",
    "Community member @user1 is expert in this domain",
    "Similar tasks can use this pattern"
  ],

  "patterns": {
    "successful": "skill-X + configuration-Y solves Z",
    "avoid": "don't use skill-A for task-type-B"
  }
}
```

### 8.2 Update Knowledge

**IF successful pattern discovered**:
- Add to knowledge/BestPractices.md
- Note task type → solution mapping
- Record skill combinations that work

**IF failure pattern identified**:
- Add to knowledge/AntiPatterns.md
- Note what doesn't work
- Document alternatives

**IF new skill discovered**:
- Document skill capabilities
- Note best use cases
- Record compatibility info

## Step 9: Report to User

Generate structured learning report (see SKILL.md for format):

### 9.1 Quick Summary

```
📚 Learning Cycle #[N] Complete

Task: [original request]
Status: [✅ Solved / ⚠️ Improved / ❌ Still working]

Time spent: [X minutes]
Skills installed: [N]
Community posts: [N]

[View full report | Continue learning | Pause]
```

### 9.2 Full Report

Include:
- Task analysis
- Methods attempted
- Solutions found
- Skills installed
- Community interactions
- Results achieved
- Lessons learned
- Next steps

### 9.3 User Feedback

Ask user:
- "Are you satisfied with this outcome?"
- "Should I continue learning on this task?"
- "Any adjustments needed?"

**IF user satisfied**:
- Mark task complete
- Remove from queue

**IF user not satisfied**:
- Keep in queue
- Adjust approach for next cycle
- Ask for specific feedback

## Step 10: Schedule Next Cycle

### 10.1 Calculate Next Run

```
Next run = now + 4 hours
Adjust if:
- User requests different interval
- System is busy
- No pending tasks
- User paused learning
```

### 10.2 Prepare for Next Cycle

**Tasks queue management**:
```
- Solved tasks: Remove from queue
- Improved tasks: Keep with lower priority
- Failed tasks: Keep, increment attempt count
- New tasks: Add to end of queue
```

**Schedule next cycle**:
```
IF user paused:
  → Don't schedule
  → Note pause reason
  → Wait for resume

IF no pending tasks:
  → Extend interval (6-8 hours)
  → Log: "System healthy, extending check interval"

IF urgent tasks:
  → Keep 4-hour interval
  → Prioritize high-impact tasks
```

### 10.3 Sleep and Wake

**Before sleep**:
- Save all state
- Document progress
- Note next actions
- Report sleep time

**On wake**:
- Reload state
- Check for new tasks
- Review previous outcomes
- Begin new cycle

## Conditional Branches

### IF: User triggers manually (not scheduled)
- Skip timer check
- Present task selection immediately
- Expect faster response needed
- Report more frequently

### IF: User says "stop" or "pause"
- Immediately halt current cycle
- Save current progress
- Ask for reason (optional)
- Disable scheduled runs
- Wait for resume command

### IF: System resources constrained
- Reduce search scope
- Skip non-essential operations
- Notify user of limitations
- Queue for later when resources available

### IF: Community rate limit hit
- Delay posting until next cycle
- Focus on skill search method
- Note to try community next time

### IF: No internet connectivity
- Use only local knowledge
- Queue web searches for later
- Notify user of limitation
- Retry when connectivity restored

## Error Handling

### Task Discovery Errors
```
Error: Memory API unavailable
→ Use cached task list from previous cycle
→ Log error for investigation
→ Continue with available data
```

### Skill Search Errors
```
Error: Google search unavailable
→ Fall back to npm search directly
→ Try community search if available
→ Note limitation in report
```

### Installation Errors
```
Error: Skill installation failed
→ Don't mark as failure, try next skill
→ Log specific error for troubleshooting
→ Include in user report
```

### Community Errors
```
Error: Can't access community
→ Continue with other method
→ Note in report that community unavailable
→ Suggest manual community engagement
```

## Self-Correction

### During execution, check:

**Am I**:
- ❌ Repeating failed approaches? → Stop, try different method
- ❌ Installing too many skills? → Stop, ask user
- ❌ Searching too broadly? → Narrow queries
- ❌ Posting too frequently? → Check rate limits
- ❌ Ignoring user preferences? → Adjust behavior

**Should I**:
- ✅ Document everything for learning?
- ✅ Ask before significant actions?
- ✅ Respect user's time and attention?
- ✅ Learn from both successes and failures?
- ✅ Share useful discoveries with user?

## Safety Checkpoints

Before executing, verify:
- [ ] User has consented to this learning cycle
- [ ] Skills to install are from verified sources
- [ ] Community posts are sanitized
- [ ] Rollback options available
- [ ] System resources adequate
- [ ] Not exceeding rate limits
