---
name: writing-plans
description: Create detailed implementation plans with exact file paths, code, test commands, and commit messages before writing code
---

# Writing Plans — Detailed Implementation Plans

## When to Use

Use AFTER a design is approved and BEFORE writing implementation code. Every non-trivial task needs a plan.

## Plan Structure

Every plan must include for each task:
- **Exact file paths** — which files to create, modify, or test
- **Complete code** — not "add validation" but the actual code
- **Test commands** — exact commands with expected output
- **Commit message** — what to commit after each task

## Process

### Step 1: Break Into Discrete Tasks

Break the approved design into small, independent tasks. Each task should be completable in one focused session.

### Step 2: Order by Dependencies

Tasks should follow dependency order:
1. Schema/database changes first
2. Backend/API routes second
3. Frontend components third
4. Integration/infrastructure fourth
5. Deployment last

### Step 3: Write Plan Details

For each task, specify:

**Files:**
- Create: `src/app/api/new-route/route.ts`
- Modify: `prisma/schema.prisma` (add field X to model Y)
- Test: `tests/api/new-route.test.ts`

**Implementation:**
```typescript
// Complete code, not pseudocode
export async function GET(req: NextRequest) {
  // actual implementation here
}
```

**Verification:**
```bash
npm test -- tests/api/new-route.test.ts
# Expected: PASS
```

**Commit:**
```bash
git add [specific files]
git commit -m "feat: add new route for [feature]"
```

### Step 4: Share the Plan

Post the plan summary for visibility before starting execution:

```
PLAN: [Feature Name]

Tasks:
1. [Task description] — [assignee/priority]
2. [Task description] — [assignee/priority]
3. [Task description] — [assignee/priority]

Starting execution now.
```

### Step 5: Transition to Execution

Execute tasks one by one using `craftwork:subagent-driven-development`. Complete each task fully (code + tests + commit) before moving to the next.

## Key Principles

- Bite-sized tasks (one focused action per step)
- Complete code in plan (implementers should not need to guess)
- TDD: test command before implementation
- Frequent commits (one per task)
- DRY and YAGNI
