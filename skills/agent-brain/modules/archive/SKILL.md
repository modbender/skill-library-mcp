# Archive Memory 📦

**Status:** ✅ Live | **Module:** archive | **Part of:** Agent Brain

Memory storage and retrieval. The only module that reads/writes to the memory backend (`memory.db` via SQLite by default, or `memory.json` with legacy JSON backend).

## Operations

All operations go through `scripts/memory.sh`:

### Store
```bash
# User tells you a fact
./scripts/memory.sh add fact "Alex prefers prose over bullets" user "style,formatting"

# User teaches a procedure
./scripts/memory.sh add procedure "Always run tests before committing" user "workflow,git"

# Store a preference with context
./scripts/memory.sh add preference "Prefers concise responses" user "style" "" "casual conversations"

# Store with namespaced tags
./scripts/memory.sh add preference "Uses Python for data work" user "code.python,data"
```

### Retrieve
```bash
# Search by keyword (auto-touches returned entries, weighted scoring)
./scripts/memory.sh get "formatting style"

# List all of a type
./scripts/memory.sh list preference
```

Results are ranked by keyword match (40%), tag overlap (25%), confidence (15%), recency (10%), and access frequency (10%). Returned entries are automatically marked as accessed — no need to call `touch` separately.

### Update
```bash
# Update a field directly
./scripts/memory.sh update <id> confidence sure

# Replace outdated info
./scripts/memory.sh add fact "Alex now works at CompanyB" user "work"
./scripts/memory.sh supersede <old_id> <new_id>
```

### Correct
```bash
# When user corrects you — tracks why you were wrong
./scripts/memory.sh correct <wrong_id> "Correct claim here" "Reason for mistake" "tags"
```

### Record Success
```bash
# When a memory was applied successfully
./scripts/memory.sh success <id> "Applied during code review"
```

## Fact Extraction

The agent MUST actively extract facts from every user message. Most users
won't say "remember this" — they reveal information naturally. The agent's
job is to catch it.

### Per-Message Extraction Flow

Run this on EVERY user message, before responding:

```
1. SCAN the message for extractable signals (see categories below)
2. For each signal found:
   a. CLASSIFY → fact, preference, or procedure?
   b. CHECK duplicates → ./scripts/memory.sh get "<key phrase>"
   c. If not already stored:
      - CHECK conflicts → ./scripts/memory.sh conflicts "<content>"
      - If POTENTIAL_CONFLICTS → ask user to clarify, or supersede old entry
      - If NO_CONFLICTS → store it
   d. STORE silently — never say "I'll remember that" or "storing this"
3. RETRIEVE relevant context → ./scripts/memory.sh get "<message topics>"
4. Respond to the user's actual request, applying retrieved context
```

### What to Extract

#### Identity (type: `fact`, tags: `identity.*`)

| Signal | Example Message | What to Store |
|--------|----------------|---------------|
| Name | "I'm Marcus" / "My name is..." | `"The user's name is Marcus"` → `identity,personal` |
| Role | "I'm a senior engineer" | `"User is a senior engineer"` → `identity,role` |
| Company | "I work at Stripe" / "at our company..." | `"User works at Stripe"` → `identity,work` |
| Team | "Our team handles payments" | `"User's team handles payments"` → `identity,team` |
| Location | "I'm based in Berlin" | `"User is based in Berlin"` → `identity,location` |

#### Tech Stack (type: `fact`, tags: `code.*`, `tools`)

| Signal | Example Message | What to Store |
|--------|----------------|---------------|
| "We use X" | "We use PostgreSQL" | `"Team uses PostgreSQL"` → `code.database,tools` |
| "Built with X" | "This is built with Next.js 14" | `"Project uses Next.js 14"` → `code.nextjs,project` |
| "Our stack" | "Our stack is React + Node" | `"Stack is React + Node"` → `code.react,code.node,project` |
| "Running on" | "Running on AWS with ECS" | `"Deployed on AWS ECS"` → `infra.aws,project` |
| Implicit | "in our Next.js app..." | `"Project uses Next.js"` → `code.nextjs,project` |
| Version | "We're on Python 3.12" | `"Uses Python 3.12"` → `code.python,project` |

#### Preferences (type: `preference`, tags: `style.*`, `code.*`)

| Signal | Example Message | What to Store |
|--------|----------------|---------------|
| "I prefer X" | "I prefer TypeScript" | `"Prefers TypeScript over JavaScript"` → `code.typescript,style.code` |
| "I like X" | "I like short functions" | `"Prefers short functions"` → `code.patterns,style.code` |
| "Don't use X" | "Don't use any" | `"Avoid any type in TypeScript"` → `code.typescript,style.code` |
| "Always X" | "Always use named exports" | `"Prefers named exports over default"` → `code.patterns,style.code` |
| "I hate X" | "I hate ORMs" | `"Dislikes ORMs, prefers raw SQL"` → `code.database,style.code` |
| Style choice | "Can you make it more concise?" | `"Prefers concise responses"` → `style.tone` |
| Repeated picks | User picks Tailwind 3 times in a row | `"Prefers Tailwind CSS"` → `code.css,style.code` |

#### Workflows (type: `procedure`, tags: `workflow.*`)

| Signal | Example Message | What to Store |
|--------|----------------|---------------|
| "I always X" | "I always write tests first" | `"Writes tests before implementation (TDD)"` → `workflow.testing,process` |
| "Before I X" | "Before merging I run lint" | `"Runs lint before merging"` → `workflow.git,process` |
| "Our process" | "We do trunk-based dev" | `"Team uses trunk-based development"` → `workflow.git,process` |
| "My workflow" | "I branch off develop" | `"Branches from develop, not main"` → `workflow.git,process` |
| "First I..then" | "First I prototype, then refactor" | `"Prototypes first, then refactors"` → `workflow.dev,process` |

#### Project Context (type: `fact`, tags: `project.*`)

| Signal | Example Message | What to Store |
|--------|----------------|---------------|
| "Building X" | "I'm building a dashboard" | `"Current project is a dashboard"` → `project,context` |
| Architecture | "It's a monorepo with turborepo" | `"Project is a turborepo monorepo"` → `project,infra` |
| Constraints | "We need HIPAA compliance" | `"Project requires HIPAA compliance"` → `project,constraints` |
| Deadline | "Launching next month" | `"Launch target is next month"` → `project,timeline` |
| Migration | "Migrating from REST to GraphQL" | `"Migrating API from REST to GraphQL"` → `project,code.api` |

#### Corrections (implicit extraction)

When the user corrects you, this is a high-value extraction signal:

| Signal | Example Message | Action |
|--------|----------------|--------|
| "No, it's X" | "No, we use Vitest not Jest" | `correct <old_id> "Team uses Vitest" "Assumed Jest"` |
| "Actually..." | "Actually I'm a staff engineer" | `correct <old_id> "User is a staff engineer" "Was stored as senior"` |
| "That's wrong" | "That's wrong, the API is REST" | `correct <old_id> "API is REST" "Incorrectly assumed GraphQL"` |
| "Stop doing X" | "Stop adding semicolons" | Store preference: `"No semicolons in code"` → `style.code` |

### Implicit vs Explicit Signals

**Explicit** (high confidence — store as `source: user`, `confidence: sure`):
- "Remember that...", "I always...", "My name is...", "We use..."
- Directly stated facts about themselves, their team, their project

**Implicit** (lower confidence — store as `source: inferred`, `confidence: uncertain`):
- Repeated choices (user keeps choosing functional components)
- Context clues ("in our Next.js app" reveals tech stack)
- Style patterns (user always asks for shorter responses)

Implicit facts should be confirmed before upgrading to `sure`:
```bash
# Store initially as uncertain
./scripts/memory.sh add fact "Project uses Next.js" inferred "code.nextjs,project"
# If user later confirms → upgrade
./scripts/memory.sh update <id> confidence sure
```

### What NOT to Extract

- **One-time requests**: "Format this as a table" ≠ user prefers tables
- **Hypotheticals**: "If we were using Python..." ≠ user uses Python
- **Transient state**: "I'm debugging X right now" — too temporary
- **Sensitive data**: Passwords, API keys, tokens, SSNs — NEVER store
- **Already stored**: Always `get` first to avoid duplicates
- **Obvious context**: Don't store "user is talking to me" or "user is coding"

### Extraction Examples

**User message**: "Hey, I'm Marcus. I'm a senior engineer at Stripe working on a payments dashboard. We use React with TypeScript and I prefer Tailwind for styling."

**Extraction** (5 facts from one message):
```bash
./scripts/memory.sh add fact "The user's name is Marcus" user "identity,personal"
./scripts/memory.sh add fact "Marcus is a senior engineer at Stripe" user "identity,work,identity,role"
./scripts/memory.sh add fact "Current project is a payments dashboard" user "project,context"
./scripts/memory.sh add fact "Project uses React with TypeScript" user "code.react,code.typescript,project"
./scripts/memory.sh add preference "Prefers Tailwind for CSS styling" user "code.css,style.code"
```

**User message**: "Can you refactor this to use async/await? I hate callback hell."

**Extraction** (1 preference):
```bash
./scripts/memory.sh add preference "Prefers async/await over callbacks" user "code.patterns,style.code"
```

**User message**: "Fix the type error on line 42"

**Extraction**: Nothing — this is a transient task request with no durable facts.

## When to Retrieve

Before responding to any task, search memory for relevant context. This is the FIRST step on every message — before extraction, before responding.

**How to build the search query**: Pull 2-4 meaningful nouns/topics from the user's message. Drop filler words ("can you", "help me", "please"). Focus on the subject.

| User message | Query |
|---|---|
| "Help me write a React component for the sidebar" | `"react component sidebar"` |
| "What's our deployment process?" | `"deployment process workflow"` |
| "Fix the login bug" | `"login bug auth"` |
| "How should I structure the API?" | `"api structure architecture"` |

```bash
# Always run this first
./scripts/memory.sh get "<query>"
```

**Using results**: If entries come back, apply them silently. Never say "I remember that you..." or "According to my memory..." — just use the knowledge as if you naturally know it. Access tracking is automatic — retrieved entries stay fresh.

## When NOT to Store

- Transient conversation details
- Anything the user explicitly says is temporary
- Sensitive data (passwords, API keys, SSNs)
- Information that's already stored (check first with `get`)

## Conflict Check on Store

Before adding any new entry, ALWAYS:
1. Run `./scripts/memory.sh conflicts "<content>"`
2. If `POTENTIAL_CONFLICTS` returned → pass to Signal module
3. If `NO_CONFLICTS` → proceed with add

## Pattern Detection on Store

When storing a procedure or preference, check for related entries:
1. Run `./scripts/memory.sh similar "<content>" 0.10`
2. If 3+ `SIMILAR_ENTRIES` of same type → create a pattern:
   ```bash
   ./scripts/memory.sh add pattern "<generalized description>" inferred "<tags>"
   ```

## Integration

- **Signal**: Archive calls Signal before every store to check conflicts
- **Gauge**: Archive results include confidence level for retrieval
- **Ritual**: When Archive detects 3+ similar entries via `similar`, notifies Ritual
- **Ingest**: Ingested content stored as type `ingested` with `source_url`
