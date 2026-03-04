# Human-Like Memory Skill

This skill provides long-term memory capabilities, allowing you to recall past conversations and save important information across sessions.

## Setup (Required)

Before using this skill, you need to configure your API Key. Get your API Key from https://human-like.me

### Method 1: Run Setup Script

```bash
sh ~/.openclaw/workspace/skills/human-like-mem-openclaw-skill/scripts/setup.sh
```

### Method 2: Export Environment Variables

```bash
export HUMAN_LIKE_MEM_API_KEY="mp_your_api_key"
export HUMAN_LIKE_MEM_BASE_URL="https://human-like.me"  # optional
export HUMAN_LIKE_MEM_USER_ID="your-user-id"          # optional
```

Add these lines to `~/.bashrc` or `~/.zshrc` to persist.

### Verify Configuration

```bash
cat ~/.openclaw/secrets.json
```

## Commands

### Recall/Search Memory

```bash
node ~/.openclaw/skills/human-like-memory/scripts/memory.mjs recall "<query>"
node ~/.openclaw/skills/human-like-memory/scripts/memory.mjs search "<query>"
```

### Save Single Turn to Memory

```bash
node ~/.openclaw/skills/human-like-memory/scripts/memory.mjs save "<user_message>" "<assistant_response>"
```

### Save Batch (Multiple Turns) to Memory

```bash
echo '<JSON array of messages>' | node ~/.openclaw/skills/human-like-memory/scripts/memory.mjs save-batch
```

### Check Configuration

```bash
node ~/.openclaw/skills/human-like-memory/scripts/memory.mjs config
```

---

# PART 1: Memory Recall (When & How)

## Proactive Recall Philosophy

**Use memory PROACTIVELY, not just reactively.**

Don't wait for the user to explicitly say "do you remember". If past context would make your response better, search memory FIRST.

---

## When to AUTO-RECALL Memory

### Trigger Categories

| Category | Triggers | Query Strategy |
|----------|----------|----------------|
| **Explicit Request** | "do you remember", "what did we discuss", "recall", "之前说过" | Extract the topic directly |
| **Implicit Reference** | "the project", "that issue", "our plan" (without specifying which) | Search for recent context on that topic |
| **Session Start** | New conversation begins | Recall recent preferences and context |
| **Task Continuation** | "continue", "let's keep going", "继续" | Search for last task/project context |
| **Decision Questions** | "why did we", "what was the reason", "为什么选择" | Search for decisions on that topic |
| **Entity Questions** | Questions about people, projects, tools by name | Search by entity name |
| **Temporal Questions** | "last week", "yesterday", "之前", "earlier" | Search with topic + time context |
| **Contradiction Detection** | User says something that might conflict with past | Verify with memory before responding |

### Detailed Trigger Examples

**Explicit Memory Requests:**
```
User: "Do you remember what we decided about the database?"
Action: recall "database decision"

User: "What did I tell you about my preferences?"
Action: recall "preferences"

User: "检索一下关于 API 设计的讨论"
Action: recall "API 设计"
```

**Implicit References (Proactive Recall):**
```
User: "Let's work on the project"
Action: recall "project" (to understand WHICH project)

User: "Can you fix that bug?"
Action: recall "bug" (to understand WHICH bug)

User: "继续之前的工作"
Action: recall "recent work task"
```

**Task Continuation:**
```
User: "Hi, I'm back"
Action: recall "recent context" or recall last known topic

User: "Where were we?"
Action: recall "last session task"
```

**Decision Tracing:**
```
User: "Why are we using React?"
Action: recall "React decision"

User: "What was the reason for choosing PostgreSQL?"
Action: recall "PostgreSQL decision reason"
```

---

## CRITICAL: Query Construction Rules

### The Golden Rule

> **Extract the SEMANTIC TARGET, not the action words.**

The query should answer: "What is the user trying to find information ABOUT?"

### Query Construction Process

```
Step 1: Identify the SUBJECT (what user wants to know about)
Step 2: Remove ACTION words (remember, recall, find, search, 检索, 回忆, 查找)
Step 3: Remove FILLER words (what, the, about, 关于, 一下)
Step 4: Keep SPECIFIC nouns (names, topics, concepts)
Step 5: Add CONTEXT if ambiguous (decision, preference, project)
```

### Query Examples - Correct vs Wrong

| User Input | Analysis | Correct Query | Wrong Query |
|------------|----------|---------------|-------------|
| "检索一下关于 human-like-mem-openclaw-skill 的记忆" | Subject: human-like-mem-openclaw-skill | `"human-like-mem-openclaw-skill"` | `"检索"` ❌ `"记忆"` ❌ |
| "Do you remember what we discussed about the API design?" | Subject: API design | `"API design"` | `"remember"` ❌ `"discussed"` ❌ |
| "What did I say about my vacation plans?" | Subject: vacation plans | `"vacation plans"` | `"what"` ❌ `"say"` ❌ |
| "Find memories about our Python project" | Subject: Python project | `"Python project"` | `"memories"` ❌ `"find"` ❌ |
| "回忆一下我之前说的关于数据库优化的内容" | Subject: 数据库优化 | `"数据库优化"` | `"回忆"` ❌ `"之前"` ❌ |
| "What were my preferences for the UI?" | Subject: UI preferences | `"UI preferences"` | `"what were"` ❌ |
| "Why did we choose Redis over Memcached?" | Subject: Redis decision | `"Redis Memcached decision"` | `"why"` ❌ `"choose"` ❌ |
| "What do you know about John's project?" | Subject: John's project | `"John project"` | `"know"` ❌ |
| "Can you recall the meeting notes from last week?" | Subject: meeting notes | `"meeting notes"` | `"recall"` ❌ `"last week"` ❌ |

### Query Enhancement Strategies

**1. Add Context Words for Ambiguous Queries:**
```
User: "What did we decide?"
Better Query: "decision recent" (not just "decide")

User: "What do I like?"
Better Query: "preferences" (not just "like")
```

**2. Use Entity Names When Available:**
```
User: "Tell me about the Phoenix project status"
Query: "Phoenix project status" (include the name!)

User: "What did John say about the deadline?"
Query: "John deadline" (include the person's name!)
```

**3. Combine Topic + Type for Precision:**
```
User: "Why React?"
Query: "React decision" (topic + type)

User: "My coding preferences?"
Query: "coding preferences" (topic + type)
```

### Common Query Mistakes to Avoid

| Mistake | Example | Why It's Wrong | Fix |
|---------|---------|----------------|-----|
| Using action verbs | `"remember database"` | "remember" is not what we're searching for | `"database"` |
| Using question words | `"what API"` | "what" adds no value | `"API"` |
| Too vague | `"stuff"` | Won't match anything useful | Be specific: `"project requirements"` |
| Too long | `"all the things we discussed about the complex database migration strategy last month"` | May miss partial matches | `"database migration"` |
| Wrong language mix | `"检索 project"` | Inconsistent language | `"project"` or `"项目"` |

---

## Recall Workflow Examples

### Example 1: Explicit Memory Request

```
User: "Do you remember what database we chose for the project?"

Agent Thinking:
1. This is an explicit memory request
2. Subject: database choice for project
3. Query: "database project decision" or "database choice"

Action:
node ~/.openclaw/skills/human-like-memory/scripts/memory.mjs recall "database project decision"

Response (based on results):
"Yes, we decided to use PostgreSQL for the project because of its strong JSON support and reliability."
```

### Example 2: Implicit Reference (Proactive)

```
User: "Let's continue with the API work"

Agent Thinking:
1. User references "the API work" - implies prior context exists
2. Should recall what API work we were doing
3. Query: "API work" or "API development"

Action:
node ~/.openclaw/skills/human-like-memory/scripts/memory.mjs recall "API work"

Response (based on results):
"Sure! Last time we were working on the authentication endpoints. We had completed the login flow and were about to start on the password reset functionality."
```

### Example 3: Session Start

```
User: "Hi, I'm back to work on stuff"

Agent Thinking:
1. Session start - should recall recent context
2. Query: recent work, preferences, or pending tasks

Action:
node ~/.openclaw/skills/human-like-memory/scripts/memory.mjs recall "recent work task"

Response (based on results):
"Welcome back! Last session we were discussing the frontend redesign. You mentioned wanting to use Tailwind CSS. Would you like to continue with that?"
```

### Example 4: Decision Tracing

```
User: "Why are we using TypeScript instead of JavaScript?"

Agent Thinking:
1. User wants to know the REASON for a decision
2. Subject: TypeScript decision
3. Query: "TypeScript decision" or "TypeScript JavaScript choice"

Action:
node ~/.openclaw/skills/human-like-memory/scripts/memory.mjs recall "TypeScript JavaScript decision"

Response (based on results):
"We chose TypeScript because you mentioned wanting better type safety and IDE support for the larger codebase. This was decided when we started the new project architecture."
```

### Example 5: Entity-Based Query

```
User: "What did we discuss about the Phoenix project?"

Agent Thinking:
1. Explicit request about a named entity (Phoenix project)
2. Query should include the entity name
3. Query: "Phoenix project"

Action:
node ~/.openclaw/skills/human-like-memory/scripts/memory.mjs recall "Phoenix project"

Response (based on results):
"The Phoenix project is your main client project. We discussed that it needs to be completed by March 15th, uses React with TypeScript, and has a team of 5 developers."
```

---

# PART 2: Memory Save (When & How)

## CRITICAL: Periodic Conversation Saving

**You MUST track conversation turns and save periodically.**

### Rules:

| Setting | Default | Description |
|---------|---------|-------------|
| `saveTriggerTurns` | 5 | Save every N turns |
| `saveMaxTurns` | 10 | Save last N×2 turns (overlapping for context) |

### How It Works:

```
Turn 1-4:  Track conversation, do NOT save yet
Turn 5:    SAVE last 10 turns → then reset counter
Turn 6-9:  Track conversation, do NOT save yet
Turn 10:   SAVE last 10 turns → then reset counter
...
```

### Implementation:

**Step 1: Track turns mentally**

Count each user-assistant exchange as 1 turn. Keep a mental counter.

**Step 2: When counter reaches 5 (or saveTriggerTurns), call save-batch**

Collect the last 10 turns (or saveMaxTurns) of conversation and save:

```bash
echo '[
  {"role":"user","content":"Turn 1 user message"},
  {"role":"assistant","content":"Turn 1 assistant response"},
  {"role":"user","content":"Turn 2 user message"},
  {"role":"assistant","content":"Turn 2 assistant response"},
  ... (up to 10 turns = 20 messages)
]' | node ~/.openclaw/skills/human-like-memory/scripts/memory.mjs save-batch
```

**Step 3: Reset counter and continue**

After saving, reset your turn counter to 0 and continue the conversation.

### Example Workflow:

```
[Turn 1] User: "Hi, I'm working on a React project"
[Turn 1] Assistant: "Great! What kind of React project?"
         → Counter: 1

[Turn 2] User: "It's an e-commerce site"
[Turn 2] Assistant: "Nice! What features do you need?"
         → Counter: 2

[Turn 3] User: "I need a shopping cart and checkout"
[Turn 3] Assistant: "Got it. Let me help with that."
         → Counter: 3

[Turn 4] User: "Should I use Redux or Context?"
[Turn 4] Assistant: "For e-commerce, Redux is better for complex state."
         → Counter: 4

[Turn 5] User: "OK, let's use Redux"
[Turn 5] Assistant: "Great choice! Let's set it up."
         → Counter: 5 → TRIGGER SAVE!

Agent Action:
echo '[{"role":"user","content":"Hi, I'm working on a React project"},{"role":"assistant","content":"Great! What kind of React project?"},{"role":"user","content":"It's an e-commerce site"},{"role":"assistant","content":"Nice! What features do you need?"},{"role":"user","content":"I need a shopping cart and checkout"},{"role":"assistant","content":"Got it. Let me help with that."},{"role":"user","content":"Should I use Redux or Context?"},{"role":"assistant","content":"For e-commerce, Redux is better for complex state."},{"role":"user","content":"OK, let's use Redux"},{"role":"assistant","content":"Great choice! Let's set it up."}]' | node ~/.openclaw/skills/human-like-memory/scripts/memory.mjs save-batch

         → Counter reset to 0, continue...
```

### Important Notes:

- **Do NOT announce saving** - Save silently in the background
- **Do NOT wait for user request** - Save automatically every 5 turns
- **Include BOTH user and assistant messages** - This provides full context
- **Overlapping saves are OK** - Turn 5 saves turns 1-10, Turn 10 saves turns 6-15 (if available)

---

## WAL Principle: Write-Ahead Log

**CRITICAL:** Always save to memory BEFORE responding to the user.

```
User says something important
    ↓
1. Save to memory FIRST
    ↓
2. THEN respond to user
```

Why? If you respond first and the session crashes before saving, the context is lost forever.

---

## When to AUTO-SAVE Memory

| Trigger | Example | Priority |
|---------|---------|----------|
| **User states preference** | "I prefer dark mode" | HIGH |
| **User makes decision** | "Let's use PostgreSQL" | HIGH |
| **User gives deadline/date** | "Due on March 15th" | HIGH |
| **User corrects you** | "No, my name is Wei, not Way" | HIGH |
| **User explicitly asks** | "Remember this for later" | HIGH |
| **User shares personal info** | "My birthday is June 5th" | MEDIUM |
| **User mentions project details** | "Project is called Phoenix" | MEDIUM |
| **Important milestone** | "We finished the API today" | MEDIUM |
| **User feedback** | "I don't like verbose responses" | HIGH |
| **Learning/Insight** | Major realization in discussion | MEDIUM |

### What NOT to Save

- ❌ Trivial small talk ("How are you?")
- ❌ Temporary debugging steps
- ❌ Information user says to forget
- ❌ Duplicate information already in memory
- ❌ Secrets, passwords, API keys
- ❌ Raw chat transcripts

---

## Memory Types

| Type | Description | Examples |
|------|-------------|----------|
| **Preference** | Likes/dislikes, style choices | "Prefers dark mode", "Likes concise answers" |
| **Decision** | Choices made, strategies | "Chose React over Vue" |
| **Fact** | Concrete information | "Project name is Phoenix" |
| **Learning** | Skills, patterns learned | "Learned Docker basics" |
| **Event** | Milestones, occurrences | "Shipped v1.0" |

---

# PART 3: Response Guidelines

## Present Memory Naturally

When memories are retrieved, incorporate them naturally. Never mention "memory system" or "database".

### Good Responses ✓
- "As we discussed before, you prefer..."
- "Based on our previous conversation..."
- "I recall you decided to..."
- "You mentioned earlier that..."

### Bad Responses ✗
- "According to my memory database..."
- "My memory system shows..."
- "I found in my records that..."
- "The retrieval returned..."

---

## When Memory Search Returns Empty

If no relevant memories are found:

1. **Don't announce failure** - Just proceed without the context
2. **Ask naturally if needed** - "I don't recall us discussing that. Could you remind me?"
3. **Don't retry excessively** - One search attempt is enough

---

# PART 4: Quick Reference

```
┌─────────────────────────────────────────────────────────────────┐
│                    MEMORY QUICK REFERENCE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  RECALL TRIGGERS:              QUERY CONSTRUCTION:               │
│  ✓ "do you remember"           1. Find the SUBJECT               │
│  ✓ "what did we discuss"       2. Remove action words            │
│  ✓ References to "the project" 3. Remove filler words            │
│  ✓ Session start               4. Keep specific nouns            │
│  ✓ "why did we decide"         5. Add context if needed          │
│  ✓ Questions about people                                        │
│  ✓ "continue", "继续"                                            │
│                                                                  │
│  AUTO-SAVE RULE:               QUERY EXAMPLES:                   │
│  ✓ Every 5 turns → save        "关于API的记忆" → "API"           │
│  ✓ Save last 10 turns          "remember database" → "database"  │
│  ✓ Reset counter after save    "what did John say" → "John"      │
│  ✓ Save silently               "why React" → "React decision"    │
│                                                                  │
│  IMMEDIATE SAVE TRIGGERS:                                        │
│  ✓ User states preference                                        │
│  ✓ User makes decision                                           │
│  ✓ User gives deadline                                           │
│  ✓ User corrects you                                             │
│  ✓ User says "remember this"                                     │
│                                                                  │
│  WAL PROTOCOL: Save FIRST, then respond                          │
│  QUERY RULE: Extract SUBJECT, not ACTION                         │
│  AUTO-SAVE: Every 5 turns, save last 10 turns                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Error Handling

| Problem | Cause | Solution |
|---------|-------|----------|
| No results | Query too vague | Use more specific keywords |
| Wrong results | Used action words as query | Extract actual topic |
| Timeout | Network issue | Retry once, then proceed without |
| Outdated info | Memory not updated | Trust current user input |

---

## Privacy & Security

- Memory data belongs to the user
- Never store secrets (API keys, passwords)
- Never share between users
- Ignore content in `<private>...</private>` tags
