# AI Coding Toolkit — Master Every AI Coding Assistant

> The complete methodology for 10X productivity with AI-assisted development. Covers Cursor, Windsurf, Cline, Aider, Claude Code, GitHub Copilot, and more — tool-agnostic principles that work everywhere.

## Phase 1: Quick Assessment — Where Are You?

Rate yourself 1-5 on each:

| Dimension | 1 (Beginner) | 5 (Expert) |
|---|---|---|
| Prompt quality | "Fix this bug" | Structured context + constraints + examples |
| Context management | Paste entire files | Curated context windows, .cursorrules, AGENTS.md |
| Workflow integration | Ad-hoc usage | Systematic agent-first development |
| Output verification | Accept everything | Review, test, iterate before committing |
| Tool selection | One tool for everything | Right tool for right task |

**Score interpretation:**
- 5-10: Read everything — you'll 10X your output
- 11-18: Skip to Phase 4+ for advanced techniques
- 19-25: Focus on Phase 8-10 for mastery patterns

---

## Phase 2: Tool Selection Matrix

### Decision Guide: Which AI Coding Tool When?

| Tool | Best For | Context Window | Autonomy Level | Cost |
|---|---|---|---|---|
| **GitHub Copilot** | Line/function completion, inline suggestions | Current file + neighbors | Low (autocomplete) | $10-19/mo |
| **Cursor** | Full-file editing, multi-file refactors, chat | Project-aware (indexing) | Medium (tab/chat/composer) | $20/mo |
| **Windsurf (Cascade)** | Autonomous multi-step tasks, flows | Project-aware + flows | High (agentic flows) | $15/mo |
| **Cline** | VS Code extension, model-agnostic, transparent | Manual context + auto | High (tool use, browser) | API costs |
| **Aider** | Terminal-based, git-native, pair programming | Repo map + selected files | Medium-High (git commits) | API costs |
| **Claude Code** | CLI agent, complex multi-file tasks | Workspace-aware | High (full agent) | API costs |
| **OpenClaw** | Persistent agent, cron, multi-surface | Workspace + memory + tools | Very High (autonomous) | API costs |

### Selection Decision Tree

```
Need autocomplete while typing?
  → GitHub Copilot (layer it with any other tool)

Working in VS Code/IDE?
  ├─ Want integrated editor experience? → Cursor or Windsurf
  ├─ Want model flexibility + transparency? → Cline
  └─ Want minimal config, just works? → Cursor

Working in terminal?
  ├─ Want git-native pair programming? → Aider
  ├─ Want full agent with tools? → Claude Code
  └─ Want persistent autonomous agent? → OpenClaw

Building complex multi-file features?
  → Cursor Composer or Windsurf Cascade or Claude Code

Need autonomous background work?
  → OpenClaw (cron, heartbeats, multi-session)
```

### Recommended Stack (Layer These)

**Solo developer:**
1. GitHub Copilot (always-on autocomplete)
2. Cursor OR Windsurf (primary IDE)
3. Claude Code OR Aider (terminal agent for complex tasks)

**Team:**
1. GitHub Copilot (org-wide)
2. Cursor (primary IDE, .cursorrules in repo)
3. CI/CD AI review (automated PR review)

---

## Phase 3: Context Engineering — The #1 Skill

Context is everything. The quality of AI output is directly proportional to the quality of context you provide.

### The Context Hierarchy (Most → Least Important)

1. **System instructions** (.cursorrules, AGENTS.md, CLAUDE.md, .windsurfrules)
2. **Explicit context** (files you @mention or add to chat)
3. **Implicit context** (open tabs, recent edits, project index)
4. **Model knowledge** (training data — least reliable for your codebase)

### Project Rules File Template

Create at project root. Name depends on tool:
- Cursor: `.cursorrules`
- Windsurf: `.windsurfrules`
- Claude Code: `CLAUDE.md`
- Aider: `.aider.conf.yml` + convention docs
- OpenClaw: `AGENTS.md`

```yaml
# [PROJECT] — AI Coding Context

## Project Overview
- Name: [project name]
- Stack: [e.g., Next.js 14 + TypeScript + Tailwind + Drizzle + PostgreSQL]
- Architecture: [e.g., App Router, server components by default]
- Monorepo: [yes/no, structure if yes]

## Code Standards (ENFORCE STRICTLY)
- TypeScript strict mode (`tsc --noEmit --strict`)
- Max 50 lines per function, 300 lines per file
- One responsibility per file
- Naming: camelCase functions, PascalCase types, SCREAMING_SNAKE constants
- Imports: named imports, no default exports
- Error handling: explicit try/catch, typed errors, no silent catches

## Patterns to Follow
- [Pattern 1 with example]
- [Pattern 2 with example]
- [Pattern 3 with example]

## Anti-Patterns (NEVER DO)
- [Anti-pattern 1]
- [Anti-pattern 2]
- [Anti-pattern 3]

## File Structure
```
src/
  components/     # React components
  lib/            # Shared utilities
  server/         # Server-only code
  db/             # Database schema + queries
  types/          # Shared TypeScript types
```

## Testing
- Framework: [vitest/jest/pytest]
- Pattern: AAA (Arrange, Act, Assert)
- Naming: `should [expected behavior] when [condition]`
- Coverage target: [80%+]

## Dependencies
- Approved: [list]
- Banned: [list with reasons]

## Common Commands
- `npm run dev` — start dev server
- `npm run test` — run tests
- `npm run lint` — lint + typecheck
- `npm run build` — production build
```

### Context Window Management

**The 80/20 Rule:** 80% of your context should be the specific files/functions relevant to the task. 20% is project conventions and standards.

**Context Compression Techniques:**
1. **Summarize, don't dump** — Instead of pasting a 500-line file, describe what it does and paste only the relevant section
2. **Use @mentions** — `@file.ts` instead of copy-paste (tool-specific)
3. **Create reference docs** — One-page architecture summaries the AI can reference
4. **Prune conversation** — Start new chats for new tasks; stale context = hallucinations
5. **Tree command** — Give the AI your project structure: `tree -I node_modules -L 3`

### The Context Refresh Rule

> Every 5-10 messages, check: Is the AI still tracking correctly?
> If it starts hallucinating file names, functions, or making wrong assumptions — **start a new chat with fresh context.**
> Context is milk. It spoils.

---

## Phase 4: Prompt Engineering for Code

### The SPEC Framework (Structure, Precision, Examples, Constraints)

**Bad prompt:**
```
Fix the login bug
```

**Good prompt (SPEC):**
```
## Structure
Fix the authentication flow in `src/auth/login.ts`

## Precision
- The login function throws "user not found" even when the user exists
- Error occurs on line 42 when querying by email (case-sensitive match)
- PostgreSQL query uses exact match but emails are stored lowercase

## Examples
- Input: "User@Example.com" → should match "user@example.com" in DB
- Current behavior: returns null
- Expected: returns user record

## Constraints
- Don't change the database schema
- Use the existing `normalizeEmail()` utility from `src/utils/email.ts`
- Add a test case for case-insensitive lookup
- Keep the existing error handling pattern (throw AppError)
```

### Prompt Templates by Task Type

**Feature Implementation:**
```
Implement [feature] in [file/location].

Requirements:
1. [Requirement with acceptance criteria]
2. [Requirement with acceptance criteria]
3. [Requirement with acceptance criteria]

Constraints:
- Follow existing patterns in [reference file]
- Use [specific library/approach]
- Include error handling for [edge cases]
- Write tests in [test file location]

Reference: Here's how similar feature [X] was implemented:
[paste relevant code snippet]
```

**Bug Fix:**
```
Bug: [description]
File: [path]
Steps to reproduce: [1, 2, 3]
Expected: [behavior]
Actual: [behavior]
Error: [paste error message/stack trace]

Fix constraints:
- Don't change [protected areas]
- Add regression test
- Explain root cause before fixing
```

**Refactoring:**
```
Refactor [file/module] to [goal].

Current state: [describe current architecture]
Target state: [describe desired architecture]
Motivation: [why — performance, readability, maintainability]

Rules:
- Preserve all existing behavior (no functional changes)
- Keep all existing tests passing
- Break into small, reviewable commits
- Each commit should be independently deployable
```

**Code Review:**
```
Review this code for:
1. Correctness — logic errors, edge cases, race conditions
2. Security — injection, auth bypass, data exposure
3. Performance — N+1 queries, unnecessary allocations, missing indexes
4. Maintainability — naming, complexity, test coverage

Be specific: quote the line, explain the issue, suggest the fix.
Skip style/formatting — linter handles that.

[paste code]
```

---

## Phase 5: Workflow Patterns — Agent-First Development

### Pattern 1: Test-Driven AI Development (TDD-AI)

```
1. Write the test first (yourself or with AI help)
2. Ask AI to implement the code that passes the test
3. Run tests — verify green
4. Ask AI to refactor while keeping tests green
5. Review the final code yourself
```

**Why this works:** Tests are specifications. The AI writes better code when it has a concrete target. You catch hallucinations immediately.

### Pattern 2: Scaffold → Fill → Review

```
1. Ask AI to scaffold the architecture (file structure, interfaces, types)
2. Review and approve the scaffold
3. Ask AI to fill in implementation file by file
4. Review each file individually
5. Integration test the full feature
```

**Why this works:** You maintain architectural control. The AI handles the grunt work. Errors are caught at each layer.

### Pattern 3: Conversation Threading

```
Chat 1: Architecture discussion → decisions documented
Chat 2: Implementation of Component A (reference architecture doc)
Chat 3: Implementation of Component B (reference architecture doc)
Chat 4: Integration + testing
```

**Why this works:** Fresh context per component prevents drift. Architecture doc provides continuity.

### Pattern 4: AI Pair Programming (Aider/Claude Code)

```
1. Start session with repo context
2. Describe the task in natural language
3. AI proposes changes as git diffs
4. Review each diff before accepting
5. AI commits with meaningful messages
6. You handle edge cases and integration
```

### Pattern 5: Autonomous Agent Workflow (OpenClaw/Claude Code)

```
1. Define task in structured format (acceptance criteria, constraints)
2. Agent plans → executes → verifies (reads files, runs tests)
3. Agent creates PR/branch with changes
4. You review the complete changeset
5. Iterate on feedback
```

---

## Phase 6: Tool-Specific Power Moves

### Cursor

| Feature | Power Move |
|---|---|
| **Tab completion** | Let it complete 3-5 tokens before accepting — catches wrong predictions early |
| **Cmd+K** (inline edit) | Select ONLY the exact lines to change — less context = more accurate |
| **Chat** | @file to add context, @codebase for project-wide questions |
| **Composer** | Multi-file changes — describe the full feature, let it edit across files |
| **.cursorrules** | Project-specific AI instructions — commit to repo for team alignment |
| **Notepads** | Reusable context (API docs, design docs) — attach to any chat |

**Cursor Pro Tips:**
- Use `@git` to reference recent changes
- Use `@docs` to reference official library documentation
- Create `.cursor/rules/` directory for multiple rule files by domain
- "Apply" button to accept chat suggestions directly into code

### Windsurf (Cascade)

| Feature | Power Move |
|---|---|
| **Cascade flows** | Multi-step autonomous tasks — it can read, write, run terminal |
| **Write mode** | Direct file editing with AI |
| **Chat mode** | Discussion without editing |
| **.windsurfrules** | Project context file |
| **Turbo mode** | Faster, less accurate — good for simple tasks |

**Windsurf Pro Tips:**
- Cascade excels at multi-file refactors — give it the full scope
- Use "undo flow" to revert entire multi-step changes
- Pin important files in context
- Let it read error output from terminal to self-fix

### Cline

| Feature | Power Move |
|---|---|
| **Model selection** | Switch models per task (cheap for simple, expensive for complex) |
| **Tool use** | Reads files, runs commands, opens browser — full agent |
| **Transparency** | Shows every action before executing — audit everything |
| **Custom instructions** | Per-project system prompts |
| **Auto-approve** | Configure which actions need approval |

**Cline Pro Tips:**
- Set spending limits to prevent runaway API costs
- Use cheaper models (Haiku/GPT-4o-mini) for simple tasks
- Enable "diff mode" to see exact changes before applying
- Create task-specific instruction files

### Aider

| Feature | Power Move |
|---|---|
| **`/add` files** | Explicitly control which files the AI can see/edit |
| **`/read` files** | Read-only context (reference files) |
| **`/architect`** | Two-model approach — architect plans, editor implements |
| **Repo map** | Auto-generates codebase summary for context |
| **Git integration** | Every change is a commit — easy rollback |

**Aider Pro Tips:**
- Use `--architect` flag for complex features (planner + implementer)
- `/drop` files you don't need to free context window
- `--map-tokens` to control repo map size
- Run `aider --model claude-sonnet-4-20250514` for best code quality

### Claude Code

| Feature | Power Move |
|---|---|
| **Full agent** | Reads files, writes code, runs tests, git operations |
| **CLAUDE.md** | Project instructions file — auto-loaded |
| **Sub-agents** | Spawn parallel workers for complex tasks |
| **Memory** | Persistent across sessions (project-level) |

**Claude Code Pro Tips:**
- Write a comprehensive CLAUDE.md — it's your biggest leverage
- Use "plan mode" first for complex tasks, then "implement"
- Let it run tests and self-correct — don't interrupt the loop
- Use `/compact` when context gets long

---

## Phase 7: Code Quality Guardrails

### The Trust-But-Verify Checklist

After every AI-generated change:

- [ ] **Read every line** — don't blindly accept. AI hallucinates plausible-looking code
- [ ] **Check imports** — AI often imports non-existent modules or wrong versions
- [ ] **Verify function signatures** — parameter names, types, return types
- [ ] **Test edge cases** — AI optimizes for the happy path
- [ ] **Check for security** — hardcoded secrets, missing auth checks, SQL injection
- [ ] **Run the tests** — if tests pass, good. If no tests exist, write them first
- [ ] **Check for drift** — did it change files you didn't ask it to change?
- [ ] **Verify dependencies** — did it add packages? Are they real? Are they secure?

### Common AI Code Failures

| Failure | Detection | Fix |
|---|---|---|
| Hallucinated API | Code uses functions that don't exist | Check library docs before accepting |
| Outdated patterns | Uses deprecated APIs (React class components) | Specify versions in context |
| Missing error handling | Happy path only, no try/catch | Ask specifically for error cases |
| Security holes | Inline secrets, missing auth, XSS | Security review as separate step |
| Over-engineering | 5 files for a 20-line solution | Ask for simplest possible solution |
| Wrong abstractions | Premature generalization | Specify "don't abstract, keep concrete" |
| Test theater | Tests that pass but test nothing | Review test assertions specifically |
| Copy-paste bugs | Duplicated logic with subtle differences | Check for patterns, extract helpers |

### The 3-Read Review

1. **Skim read** — Does the structure make sense? Right files, right approach?
2. **Logic read** — Does each function do what it claims? Edge cases handled?
3. **Integration read** — Does it work with the rest of the codebase? Breaking changes?

---

## Phase 8: Cost Optimization

### Token Cost Awareness

| Model | Input $/1M tokens | Output $/1M tokens | Best For |
|---|---|---|---|
| GPT-4o mini | $0.15 | $0.60 | Simple completions, formatting |
| Claude Haiku | $0.25 | $1.25 | Quick edits, simple questions |
| GPT-4o | $2.50 | $10.00 | Complex code generation |
| Claude Sonnet | $3.00 | $15.00 | Complex code, long context |
| Claude Opus | $15.00 | $75.00 | Architecture, hardest problems |
| o3 | $10.00 | $40.00 | Complex reasoning, algorithms |

### Cost Reduction Strategies

1. **Tier your usage** — Simple tasks → cheap model. Complex → expensive model
2. **Reduce context** — Every unnecessary file in context costs money
3. **Start new chats** — Long conversations accumulate expensive history
4. **Use autocomplete for simple stuff** — Copilot is flat-rate, much cheaper per completion
5. **Cache project context** — Use rules files instead of re-explaining every chat
6. **Batch related tasks** — Handle related changes in one conversation

### Monthly Cost Benchmarks (Full-Time Developer)

| Usage Level | Estimated Monthly Cost |
|---|---|
| Light (Copilot + occasional chat) | $20-40 |
| Medium (Cursor Pro + daily chat) | $40-80 |
| Heavy (API-based agents, complex tasks) | $80-200 |
| Power user (autonomous agents, all day) | $200-500+ |

---

## Phase 9: Team Adoption

### Rolling Out AI Coding Tools to a Team

**Week 1-2: Foundation**
- Choose primary tool (Cursor or Windsurf recommended for teams)
- Create `.cursorrules` / `.windsurfrules` committed to repo
- Run a 1-hour workshop: basics, prompt techniques, verification
- Set team guidelines (review requirements, security rules)

**Week 3-4: Practice**
- Daily 15-min "AI wins" standup share
- Pair sessions: experienced + new user
- Collect common prompts into team prompt library
- Monitor and address concerns (quality, dependency)

**Month 2: Optimization**
- Measure: time-to-PR, bugs-per-feature, developer satisfaction
- Iterate on .cursorrules based on team feedback
- Create task-specific prompt templates in shared docs
- Address skill gaps: who's using it well, who needs help?

**Month 3: Systemization**
- AI-assisted PR review as CI step
- Automated test generation for new features
- Custom slash commands / snippets for team workflows
- Quarterly review: ROI, quality metrics, tooling updates

### Team Guidelines Template

```markdown
# AI Coding Guidelines — [Team Name]

## Approved Tools
- [Tool 1] for [use case]
- [Tool 2] for [use case]

## Rules
1. AI-generated code gets the SAME review rigor as human code
2. Never paste proprietary/customer data into AI tools without approved data handling
3. All AI-generated tests must be reviewed for assertion quality
4. Security-sensitive code (auth, payments, PII) requires human-first approach
5. Commit messages should NOT mention AI — own the code you commit

## Quality Gates
- [ ] Typecheck passes (`tsc --noEmit --strict`)
- [ ] All tests pass
- [ ] No new warnings
- [ ] Manual review of all AI-generated code
- [ ] Security-sensitive areas reviewed by security champion
```

---

## Phase 10: Advanced Patterns

### Multi-Agent Architecture for Development

```
Task: Build feature X

Agent 1 (Architect): Plans the approach, defines interfaces
Agent 2 (Implementer): Writes the code
Agent 3 (Tester): Writes and runs tests
Agent 4 (Reviewer): Reviews for quality, security, patterns

Orchestrator: Coordinates, resolves conflicts, maintains context
```

### Self-Healing Development Loop

```
1. Agent writes code
2. Agent runs tests
3. Tests fail → agent reads error, fixes code
4. Repeat until tests pass
5. Agent runs linter
6. Lint fails → agent fixes
7. All green → create PR
```

### The Prompt Library Pattern

Maintain a `prompts/` directory in your project:

```
prompts/
  feature-implementation.md
  bug-fix.md
  refactoring.md
  code-review.md
  test-generation.md
  migration.md
  documentation.md
```

Each file is a reusable prompt template. Reference them: "Follow the template in prompts/feature-implementation.md"

### Model Routing Strategy

```yaml
task_routing:
  autocomplete: copilot  # Always-on, flat rate
  simple_edit: haiku     # Quick, cheap
  feature_impl: sonnet   # Good balance
  architecture: opus     # When it matters
  debugging: sonnet      # Needs to reason about code
  documentation: haiku   # Simple transformation
  security_review: opus  # Can't afford mistakes
  test_generation: sonnet # Needs understanding of code logic
```

---

## Phase 11: Anti-Patterns — What NOT to Do

| Anti-Pattern | Why It Fails | Do This Instead |
|---|---|---|
| **Prompt and pray** | No verification = bugs in production | Always review, always test |
| **Paste the whole codebase** | Overwhelms context, increases cost | Curate relevant files only |
| **Never start new chats** | Stale context → hallucinations | New task = new chat |
| **Trust without reading** | AI generates plausible but wrong code | Read every line |
| **Skip tests because AI wrote it** | AI code has bugs too | Test AI code MORE, not less |
| **Use one model for everything** | Waste money on simple tasks | Tier models by complexity |
| **No project rules file** | AI guesses your conventions | Write .cursorrules / CLAUDE.md |
| **Vague prompts** | Garbage in, garbage out | Use SPEC framework |
| **Over-reliance** | Skill atrophy, can't debug AI output | Understand what AI generates |
| **Ignoring security** | AI doesn't prioritize security | Explicit security review step |

---

## Phase 12: Scoring & Continuous Improvement

### AI-Assisted Development Quality Score (0-100)

| Dimension | Weight | Criteria |
|---|---|---|
| Context engineering | 20% | Rules files, curated context, fresh chats |
| Prompt quality | 15% | SPEC framework, task-appropriate templates |
| Verification rigor | 20% | Review checklist, test coverage, security review |
| Tool selection | 10% | Right tool for task, model routing |
| Cost efficiency | 10% | Tiered usage, context management, batch tasks |
| Output quality | 15% | Code correctness, maintainability, no drift |
| Workflow integration | 10% | Systematic process, team alignment |

### Weekly Self-Review Questions

1. What was my best AI-assisted output this week? What made it good?
2. Where did AI waste my time? What went wrong with context/prompts?
3. Am I reviewing thoroughly enough, or rubber-stamping?
4. What prompt patterns worked well? Add to prompt library.
5. Am I over-relying on AI for things I should understand deeply?

### Monthly Metrics

- **Acceleration factor**: Tasks completed per day vs pre-AI baseline
- **Bug rate**: Bugs in AI-assisted code vs manual code
- **Cost per feature**: API spend / features shipped
- **Context efficiency**: Average conversation length before drift
- **Coverage**: % of codebase with AI-assisted tests

---

## Quick Reference: Natural Language Commands

1. "Set up AI coding for [project]" — Generate rules file + tool recommendations
2. "Write a prompt for [task type]" — Generate SPEC-formatted prompt template
3. "Review this AI output" — Run the Trust-But-Verify checklist
4. "Compare [tool A] vs [tool B] for [use case]" — Tool selection analysis
5. "Optimize my AI coding costs" — Analyze usage and suggest model routing
6. "Create a team AI coding guide" — Generate team guidelines document
7. "Debug why AI keeps [hallucinating X]" — Context diagnosis
8. "Set up test-driven AI workflow for [feature]" — TDD-AI pattern guide
9. "Create prompt library for [project type]" — Generate prompt templates
10. "Score my AI coding maturity" — Run the quality assessment
11. "Onboard [person] to AI coding" — Generate training plan
12. "Audit AI coding security practices" — Security review checklist
