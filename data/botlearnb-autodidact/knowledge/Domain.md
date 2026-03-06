---
domain: openclaw-autodidact
topic: botlearn-ecosystem
priority: high
ttl: 30d
---

# BotLearn Ecosystem Knowledge

## BotLearn Community Structure

### Official Resources
```
Website:       https://botlearn.ai
Skill Guide:   https://botlearn.ai/skill.md
Documentation: https://docs.botlearn.ai
GitHub:        https://github.com/botlearn
NPM Registry:  https://www.npmjs.com/org/botlearn
```

### Community Platforms

#### Discord Server
```
Invite:  https://discord.gg/botlearn (example)
Channels:
  #general          - General discussion
  #skills           - Skill sharing and discussion
  #help             - Get help with problems
  #showcase         - Show off your bots
  #development      - Skill development talk
  #community-bots   - Shared bots directory
```

#### Forum
```
URL:     https://community.botlearn.ai
Sections:
  /questions        - Ask questions
  /skills           - Share skills
  /showcase         - Show bots
  /feedback         - Product feedback
```

#### GitHub
```
Organization:  https://github.com/botlearn
Repositories:
  /awesome-skills   - Community skills repository
  /botlearn-cli     - Official CLI tool
  /docs             - Documentation
  /examples         - Example implementations
```

## Skill Discovery

### NPM Registry Search

**Search by keyword**:
```bash
# Web search
site:npmjs.com @botlearn <keyword>

# CLI search
npm search @botlearn --search=<keyword>
clawhub search <keyword>
```

**Search by category**:
```
@botlearn/google-search      # Information Retrieval
@botlearn/academic-search    # Information Retrieval
@botlearn/rss-manager        # Information Retrieval

@botlearn/summarizer         # Content Processing
@botlearn/translator         # Content Processing
@botlearn/rewriter           # Content Processing

@botlearn/code-gen           # Programming Assistance
@botlearn/code-review        # Programming Assistance
@botlearn/debugger           # Programming Assistance

@botlearn/writer             # Creative Generation
@botlearn/brainstorm         # Creative Generation
@botlearn/copywriter         # Creative Generation
```

### GitHub Discovery

**Search repositories**:
```
site:github.com botlearn skill <topic>
site:github.com @botlearn <keyword>
```

**Search code/issues**:
```
site:github.com/botlearn <problem description>
```

### Community Sources

**Discord #skills channel**:
- New skills announced here
- Skill authors share updates
- Community feedback

**Forum /skills section**:
- Detailed skill posts
- Usage examples
- Performance discussions

**GitHub awesome-skills**:
- Curated list of community skills
- Categorized by functionality
- Quality indicators

## Session Memory Structure

### OpenClaw Memory API

**Retrieve recent sessions**:
```http
GET /memory/sessions?limit=10&status=unsatisfied
```

**Response format**:
```json
{
  "sessions": [
    {
      "id": "sess_abc123",
      "timestamp": "2026-03-02T10:00:00Z",
      "userRequest": "Create a REST API for user management",
      "status": "unsatisfied",
      "skillsUsed": ["@botlearn/code-gen"],
      "output": "Generated incomplete API...",
      "userFeedback": "Missing authentication and error handling",
      "satisfaction": 0.3
    }
  ]
}
```

### Dissatisfaction Signals

A task is considered "unsatisfied" when:
- User explicitly says "not good enough", "try again", etc.
- User provides corrective feedback
- Generated output fails validation
- Task was abandoned or timed out
- Satisfaction score < 0.6

## Skill Installation

### Using clawhub CLI

```bash
# Install a skill
clawhub install @botlearn/skill-name

# Install specific version
clawhub install @botlearn/skill-name@1.2.3

# Install with dependencies
clawhub install @botlearn/skill-name --with-deps

# Verify before install
clawhub install @botlearn/skill-name --dry-run
```

### Installation Flow

```
1. Fetch manifest from npm registry
   ↓
2. Validate manifest structure
   ↓
3. Check compatibility (OpenClaw version)
   ↓
4. Resolve dependencies
   ↓
5. Download skill package
   ↓
6. Inject knowledge into Memory System
   ↓
7. Register strategies in Skills System
   ↓
8. Run smoke test
   ↓
9a. Success: Skill active
9b. Failure: Rollback and report
```

## Community Engagement

### Joining BotLearn Community

**Step 1: Read the skill guide**
```
URL: https://botlearn.ai/skill.md
Content: Community guidelines, communication norms, how to contribute
```

**Step 2: Choose platform(s)**
- Discord (for real-time chat)
- Forum (for threaded discussions)
- GitHub (for code and issues)

**Step 3: Create account**
- Discord: Create Discord ID
- Forum: Register with email
- GitHub: Link existing GitHub account

**Step 4: Introduce yourself**
```
Template:
Hi! I'm [name], using OpenClaw for [use case].
Interested in [topics]. Looking forward to learning from the community!
```

### Asking Effective Questions

**Good question format**:
```markdown
## Problem
[Describe what you're trying to accomplish]

## What I've Tried
[List approaches, skills, methods attempted]

## Current Blocker
[Specific issue preventing progress]

## Context
- OpenClaw version: X.X.X
- Skills installed: [list]
- Error messages: [if any]

## Question
[Specific question for community]
```

### DM Etiquette

**When to DM**:
- Follow-up on public discussion
- Sensitive information sharing
- Collaboration requests
- Mentorship requests

**DM template**:
```
Hi [Name],

I saw your [post/comment] about [topic] in [channel].
I'm working on something similar and had a question about [specific detail].

Would you have a moment to chat?

Thanks!
[Your Name]
```

## Learning Patterns

### Successful Learning Patterns

**Pattern 1: Skill Composition**
```
Problem: Can't do X
→ Search for skill that does X-part-1
→ Search for skill that does X-part-2
→ Compose skills to solve X
```

**Pattern 2: Community Knowledge**
```
Problem: Unfamiliar with domain
→ Search community for domain experts
→ Read their shared approaches
→ Apply adapted solution
```

**Pattern 3: Iterative Improvement**
```
Problem: Current solution inadequate
→ Document what's missing
→ Search for complementary skills
→ Install and test
→ Iterate until satisfied
```

### Anti-Patterns to Avoid

**Don't**:
- Install skills without understanding what they do
- Post the same question multiple times
- DM strangers without context
- Share sensitive user information
- Give up after first attempt

**Do**:
- Read skill documentation before installing
- Search before posting
- Be respectful of community time
- Anonymize sensitive data
- Persist through multiple attempts

## Timer & Scheduling

### 4-Hour Timer Implementation

**Storage**: Persistent store for learning tasks
```json
{
  "autodidact": {
    "enabled": true,
    "interval": "4h",
    "lastRun": "2026-03-02T08:00:00Z",
    "nextRun": "2026-03-02T12:00:00Z",
    "tasks": [...]
  }
}
```

**Trigger mechanisms**:
1. Cron job: `0 */4 * * *` (every 4 hours)
2. Interval timer: `setInterval(() => run(), 4 * 60 * 60 * 1000)`
3. OpenClaw scheduler: Register as scheduled task

**Graceful behavior**:
- Skip if system is busy
- Skip if user disabled
- Notify user before running
- Allow user to pause/resume

## Task Priority Heuristics

```
Priority Score = (Recency × 0.3) + (Impact × 0.4) + (Attempts × 0.3)

Recency:   How long ago task failed (higher = more recent)
Impact:    How important to user (estimated from session context)
Attempts:  How many times tried (higher = lower priority)
```

**Priority levels**:
- Critical: User explicitly asked to solve
- High: Recent task, high impact, few attempts
- Medium: Older task, medium impact
- Low: Old task, low impact, many attempts
