# ClickUp Operational Master Skill - Design Spec

## Core Philosophy

**Deterministic Operations Only** — Every command either succeeds with clear confirmation or fails with explicit error. No ambiguous states. No silent failures. Full validation at every step.

## Embedded Knowledge Base

This skill contains the **complete ClickUp API documentation** internally:
- All 50+ API endpoints
- Request/response schemas
- Rate limits (100 req/min)
- Error codes and handling
- Webhook patterns
- Best practices from official docs

**MCP Context** — Included as documented fallback for edge cases only (complex workspace templates, bulk operations exceeding rate limits, cross-workspace moves).

## Operational Capabilities

### 1. Natural Language Parsing → Structured Commands
```
Input: "Create a project for Acme Corp with onboarding, web design, and monthly retainer phases"
Parse: 
  - workspace: Delivery
  - client: Acme Corp
  - structure: folder → 3 lists (onboarding, web-design, retainer)
  - assignees: find by email/name
  - due dates: infer from phases
  - custom fields: budget, priority, status
  
Execute: deterministic sequence with rollback on failure
Verify: each list created, each task present, assignments correct
Confirm: "Project Acme Corp created with 3 phases, 12 tasks, assigned to George & Matthew, due 2026-03-15"
```

### 2. Progress Diagnosis & Timeline Estimation
```
Input: "What's blocking the Scent of a Milien project?"
Flow: 
  - Scan all tasks in folder
  - Identify status: blocked, overdue, no-assignee
  - Check dependencies: waiting on other tasks
  - Estimate completion: based on task complexity, assignee velocity
  - Report: "3 tasks blocked (waiting on George's video edits). ETA: +5 days. Suggest: reassign or parallelize"
```

### 3. Assignment Orchestration
```
Input: "Get Sharyar and Matthew on the Kortex onboarding task"
Flow:
  - Find Sharyar (check existing members or invite)
  - Find Matthew (check existing or invite)
  - Locate Kortex onboarding task
  - Add both as assignees
  - Comment: "@Sharyar @Matthew — Kortex onboarding ready for your review. See attached Loom."
  - Set due date: +3 days
  - Set priority: high
  - Set status: "in progress"
  - Confirm: "Sharyar and Matthew assigned to Kortex onboarding, due 2026-02-21"
```

### 4. Workspace Creation from Template
```
Input: "Set up a new client workspace for Luxury Homes using our real estate template"
Parse:
  - Template: detect "real estate" → use predefined structure
  - Spaces: Delivery + Operations
  - Folders: Client Name → Market Research, Design, Build, Launch
  - Lists: Per-phase task lists with default tasks
  - Custom Fields: Budget, Timeline, Priority, Platform
  - Assignees: Based on team roles from People graph
  - Automations: Status change triggers, due date reminders
  
Execute: Create full hierarchy, validate each step
Confirm: "Luxury Homes workspace created: 2 spaces, 4 folders, 12 lists, 48 tasks, 5 team members assigned, automations active"
```

### 5. Intelligent Task Generation
```
Input: "Break down the Clarify website project into technical tasks"
Generate: 
- [ ] Setup Git repository and CI/CD pipeline
- [ ] Install dependencies (npm, build tools)
- [ ] Create page components: Home, About, Contact, Services
- [ ] Implement contact form with validation
- [ ] SEO setup: sitemap.xml, robots.txt, LLMs.txt
- [ ] Lighthouse audit and performance optimization
- [ ] Deploy to Vercel/production
- [ ] Set up analytics tracking

Each task gets: estimated hours, assignee (based on skills), dependencies (creates task links), custom fields (priority: high, tags: website, client: Clarify)
```

## Error Handling & Determinism

### Every operation follows this pattern:
```python
def create_task(params):
    # 1. Validate inputs
    assert params.name, "Task name required"
    assert len(params.name) <= 200, "Name too long"
    
    # 2. Check preconditions
    if params.list_id:
        assert list_exists(params.list_id), f"List {params.list_id} not found"
    
    # 3. Execute API call
    try:
        result = api_post("/task", params.dict())
    except RateLimitError as e:
        # Retry with exponential backoff
        wait(e.retry_after + 1)
        result = api_post("/task", params.dict())
    except ValidationError as e:
        # Return explicit error
        raise ClickUpError(f"Invalid data: {e.details}")
    
    # 4. Verify result
    assert result.id, "No task ID returned"
    assert result.name == params.name, "Name mismatch"
    
    # 5. Confirm success
    return {
        "id": result.id,
        "name": result.name,
        "url": result.url,
        "created": True,
        "validated": True
    }
```

### Common errors handled explicitly:
- `rate_limit` → retry + backoff
- `validation_failed` → return field-level errors
- `not_found` → suggest corrections
- `permission_denied` → suggest workspace access
- `conflict` → offer resolution (rename, merge)

## Diagnostic Commands

```bash
# What's the status of project X?
clickup-op diagnose --project "Clarify" --depth full

# Who's blocking project Y?
clickup-op blockers --project "Scent Of A Milien" --format report

# Estimate completion date
clickup-op estimate --project "Mel website" --include-dependencies

# Suggest resource allocation
clickup-op allocate --team "George,Matthew,Sharyar" --capacity 40h/week
```

## Testing Strategy

**Before declaring operational:**
1. Create 10 test workspaces
2. Generate 100 tasks with all variations (assignees, due dates, priorities, tags, dependencies, comments, checklists, time entries)
3. Execute 50 bulk operations (update 10 tasks, move 5, delete 3, restore 2)
4. Run all diagnostic commands, verify output accuracy
5. Trigger 20 error conditions, verify explicit error messages
6. Test fallback to MCP on bulk operations that hit rate limits

**Success criteria:**
- 100% operation success rate OR explicit error with resolution
- 0 ambiguous states (task exists but unconfirmed)
- All diagnostics produce sensible estimates
- Natural language parsing handles 95% of user inputs

## Integration with Brain System

**Every successful operation stores:**
- **Mem0:** "Created 12 tasks for Acme Corp project"
- **Neo4j:** `(Task) -[CREATED_IN]→ (Project "Acme Corp")`, `(George) -[ASSIGNED_TO]→ (Task)`
- **SQLite:** `decisions` table: decision type, parameters, outcome, timestamp

**Enables queries like:**
- "What projects did I create last week?" → Mem0 search
- "Who's overloaded?" → Neo4j query assignee task counts
- "What's my completion rate?" → SQLite aggregation

## Files Structure

```
skills/clickup-operational/
├── SKILL.md                      # This spec + user docs
├── scripts/
│   ├── clickup_op.py            # Main CLI (800+ lines)
│   ├── diagnostic.py            # Progress/suggestion engine
│   ├── natural_parser.py        # NL → structured commands
│   └── brain_sync.py           # Auto-store to brain system
└── tests/
    ├── test_workspace_setup.py
    ├── test_task_lifecycle.py
    ├── test_diagnostics.py
    └── test_natural_language.py
```

## Building This Skill (Model Council Required)

**Query to 4 models:**
"Design the most robust ClickUp operational skill possible. It must handle workspace creation, folder/list structures, task CRUD, assignments, comments, time tracking, reporting, and diagnostics. Must be deterministic (no ambiguous states), validate every API response, handle all errors explicitly, and include comprehensive testing. Include full CLI command list, request/response schemas, and error handling patterns."

**Synthesize responses** → extract best patterns from each model → build unified implementation.

**Estimated build time:** 4-6 hours with Model Council
**Lines of code:** ~2,500 (comprehensive, not minimal)
**Test coverage:** 95%+ of API endpoints and error paths

## Execution Order

1. **Model Council design session** (when credits reset)
2. **Build core CLI** (workspace, folder, list, task operations)
3. **Add diagnostic engine** (progress, blockers, estimates)
4. **Build natural language parser** (intent → structured)
5. **Integrate brain sync** (auto-store operations)
6. **Comprehensive testing** (100 tasks, 50 bulk ops, all error paths)
7. **Operational verification** (create real projects, diagnose real blockers)

This skill becomes your **Operational Co-CEO** for ClickUp.

## Status
- **Spec saved:** /home/node/.openclaw/workspace/skills/clickup-operational/spec.md
- **Not yet implemented** - awaiting Claude credits reset for Model Council build
- **Priority:** Critical - This unlocks full business operational capability

## Related Decisions
- Brain ingestion must be implemented first (all ClickUp operations to flow through brain)
- ClickUp MCP available as fallback but skill is primary path
- All client projects go in Delivery space, agent operations in AgxntSix-openclaw space
- Natural language parsing must handle 95%+ of business owner requests without clarification
