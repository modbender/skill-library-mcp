# Designer Guide

This guide contains complete instructions for the Designer role in the skill-engineer workflow.

---

## Role Definition

**Purpose:** Generate and revise skill content.

### Inputs
- User requirements (problem, audience, constraints)
- Design principles (from this guide)
- Feedback from Reviewer/Tester (on iterations 2+)

### Outputs
- `SKILL.md` — full skill with YAML frontmatter
- `skill.yml` — trigger configuration
- `README.md` — user-facing documentation (for strangers)
- `tests/` — trigger tests and functional test cases
- `scripts/` — deterministic validation scripts (if needed)
- `references/` — supplementary documentation (if needed)

### Constraints
- Apply progressive disclosure (frontmatter → body → linked files)
- Apply scoping rules (see Skill Scoping section below)
- Apply tool selection guardrails (see Tool Selection section below)
- README must only reference what the skill does, how to install, how to use
- No internal organization details in any output
- Follow the AI vs. Script decision framework for task assignment

---

## Core Design Principles (Anthropic Guide)

### Progressive Disclosure
Skills use a three-level system to minimize token usage while maintaining expertise:

1. **YAML frontmatter** (always loaded in system prompt)
   - Just enough information for Claude to know when to use the skill
   - Must include WHAT it does + WHEN to use it + trigger phrases
   
2. **SKILL.md body** (loaded when skill is relevant)
   - Full instructions and step-by-step guidance
   - Error handling and examples
   
3. **Linked files** (`references/`, `scripts/`, `assets/`)
   - Claude navigates to these only as needed
   - Detailed documentation, templates, executable code

### Composability
- Skills must work alongside other skills
- Don't assume yours is the only capability available

### Portability
- Same skill works across Claude.ai, Claude Code, and API
- Note any environment requirements in `compatibility` field

---

## Skill Scoping (Critical Design Step)

Every skill must have a clearly defined scope boundary. Scope violations are the most common design failure — they cause skills to absorb responsibilities that belong elsewhere, creating maintenance nightmares and confusing agents.

### The Scoping Test

For every piece of content in a skill, ask: **"Does this belong to what this skill DOES, or to how it is MANAGED?"**

- What the skill does = in scope
- How the skill is managed, deployed, tracked, or organized = out of scope

### Scope Definition Checklist

When designing or reviewing a skill, explicitly define:

1. **What this skill handles** — the core capability, start to finish
2. **What this skill does NOT handle** — adjacent concerns that belong elsewhere
3. **Where this skill ends** — the exact delivery point after which responsibility transfers
4. **Who owns post-delivery** — name the system or process that picks up after

Document these in a "Scope & Boundaries" section in SKILL.md.

### Common Scope Violations

| Violation | Example | Fix |
|-----------|---------|-----|
| Absorbing caller responsibilities | Release pipeline doing post-release bookkeeping | Move to the system that orchestrates releases |
| Including repo/infra management | Skill containing git submodule workflows | Repo management is not skill functionality |
| Leaking internal organization | README referencing "knowledge repo" structure | Users install skills, they don't manage your repo |
| Unbounded scope creep | "Also update tracking, also convert submodule, also log to memory" | Each "also" is a red flag — trace it to its real owner |

### The "Also" Test

If you find yourself writing "also do X" at the end of a skill's pipeline, X probably belongs somewhere else. Trace X to the system that should own it.

### Scoping in README.md

The README is for strangers. It must only reference:
- What the skill does
- How to install it (simple copy or package manager)
- How to use it

It must NOT reference:
- Your repo structure, submodules, or knowledge base
- Internal workflows or tracking systems
- Organization-specific deployment patterns

---

## Tool Selection Guardrails

**CRITICAL:** Always validate tool choice BEFORE execution.

### Pre-Execution Validation Checklist

Before invoking ANY tool, verify:

| # | Check | Action |
|---|-------|--------|
| TC-1 | Does the input type match tool capability? | Check file extension, content type, URL pattern |
| TC-2 | Are there warning signs that should trigger different tool? | .pdf → browser/download, .html → web_fetch, API → curl |
| TC-3 | What does tool documentation say it handles? | Read tool description, note limitations |
| TC-4 | Is there a better alternative? | Compare available tools |
| TC-5 | Have I used this tool on this type before? | Check MEMORY.md for past failures |

### Tool Selection Decision Tree

```
Input Analysis
    ├── URL provided?
    │   ├── Extension .pdf? → browser tool OR download + pdftotext
    │   ├── Extension .html/.htm? → web_fetch
    │   ├── API endpoint? → exec with curl
    │   └── Unknown? → Check content-type header first
    │
    ├── File path provided?
    │   ├── Extension .pdf? → pdftotext or browser
    │   ├── Extension .json? → jq
    │   ├── Extension .md? → read tool
    │   └── Binary? → appropriate parser
    │
    └── Data extraction needed?
        ├── From HTML? → web_fetch
        ├── From JSON? → jq
        ├── From logs? → grep/awk
        └── From PDF? → browser or pdftotext
```

### Common Tool Selection Errors

| Error | Example | Correct Approach |
|-------|---------|------------------|
| **Wrong tool for format** | web_fetch on .pdf URL | Use browser tool or download + PDF parser |
| **Over-complication** | Writing Python script for simple grep | Use shell tools |
| **Under-estimation** | grep for complex JSON parsing | Use jq |
| **Ignoring constraints** | Calling non-existent tool | Check available tools first |
| **No validation** | Assuming tool will work | Test on small sample first |

### Validation Template for Skills

Add this to any skill that invokes external tools:

```markdown
## Pre-Execution Validation

Before running any tool:
1. [ ] Input type identified (file extension, content type, URL pattern)
2. [ ] Tool capability verified (check tool docs, past usage)
3. [ ] Warning signs checked (does .pdf URL + web_fetch = bad idea?)
4. [ ] Alternative tools considered (is there a better match?)
5. [ ] Decision documented (why this tool for this input)

If ANY check fails → STOP and reconsider tool choice
```

---

## AI vs Deterministic Script Guidelines

Every skill must make deliberate choices about which tasks use AI agents and which use deterministic scripts.

### Decision Framework

| Question | If YES → Script | If NO → AI Agent |
|----------|----------------|------------------|
| Is the output always the same given the same input? | Deterministic | Requires judgment |
| Is it pure math, counting, or calculation? | Script | — |
| Is it regex/pattern matching on structured text? | Script | — |
| Does it require understanding context or meaning? | — | AI Agent |
| Does it require web search or external knowledge? | — | AI Agent |
| Does it require creative writing or synthesis? | — | AI Agent |
| Would a bug in the logic be hard to detect? | Script (testable) | — |
| Does the task need to handle unexpected formats? | — | AI Agent (flexible) |

### When to Use Scripts

| Task Type | Examples | Why Script |
|-----------|---------|-----------|
| **Validation** | Math cross-checks, totals verification, page/word count | Exact answers, no hallucination risk |
| **Extraction** | Parse references from markdown, extract citations, find specific patterns | Regex is reliable on structured text |
| **Format conversion** | JSON → markdown table, template generation | Mechanical transformation |
| **Cross-checking** | Field consistency across sections, citation numbers match reference list | Boolean checks, not judgment |
| **Calculation** | Sum totals, weighted score computation, statistics | Math must be exact |

### When to Use AI Agents

| Task Type | Examples | Why AI Agent |
|-----------|---------|-------------|
| **Analysis** | Gap identification, innovation assessment, feasibility evaluation | Requires understanding and reasoning |
| **Search** | Finding relevant sources, literature review, landscape analysis | Requires web search and relevance judgment |
| **Writing** | Content creation, narratives, review reports | Requires creative synthesis |
| **Evaluation** | Quality scoring, checklist assessment, comparative analysis | Requires contextual judgment |
| **Planning** | Configuration design, milestone planning, risk mitigation | Requires strategic thinking |

### Hybrid Pattern (Recommended)

```
AI Agent (judgment)          Script (deterministic)
    │                            │
    ▼                            ▼
"Generate structured   →    validate_output.py checks
 content with these         all numbers add up and
 required fields"           fields match requirements
    │                            │
    ▼                            ▼
AI Agent revises        ←   Script reports mismatches
based on validation
errors
```

### AI/Script Balance Audit

| # | Check | Pass/Fail |
|---|-------|-----------|
| AS-1 | All arithmetic/calculation uses scripts, not AI | |
| AS-2 | All creative/judgment tasks use AI agents, not scripts | |
| AS-3 | Validation steps exist between AI output and final commit | |
| AS-4 | Scripts have error handling (not just happy path) | |
| AS-5 | AI agent tasks have output format requirements (not open-ended) | |
| AS-6 | No task is assigned to both AI and script (clear ownership) | |
| AS-7 | Hybrid pattern used where appropriate (agent → script → agent) | |

---

## Skill Use Case Categories (Anthropic)

Before designing a skill, identify which category it falls into:

### Category 1: Document & Asset Creation
Creating consistent, high-quality output. Uses embedded style guides, template structures, quality checklists. Primarily uses Claude's built-in capabilities.

### Category 2: Workflow Automation
Multi-step processes with validation gates, templates, iterative refinement loops. Coordinates multiple steps with consistent methodology.

### Category 3: MCP Enhancement
Workflow guidance enhancing MCP server tool access. Coordinates multiple MCP calls, embeds domain expertise, provides context, handles errors.

---

## Skill Design Process

### Step 1: Requirements Gathering

1. What problem does this skill solve?
2. Who (which agent) will use it?
3. What are the inputs and outputs?
4. What existing skills does it interact with?
5. Are there deterministic components (scripts) or is it all judgment (AI)?

### Step 2: Name the Skill

A good name is critical -- it's the primary way agents and users identify the skill, and a bad name causes confusion forever.

**Present 3-5 name candidates to the user.** Do not pick one unilaterally.

**Naming criteria (in priority order):**

| Criterion | Good | Bad |
|-----------|------|-----|
| **Action-clear** | `add-top-openrouter-models` | `model-manager` |
| **Scope-obvious** | `github-pr-review` | `code-helper` |
| **Trigger-friendly** | matches how users naturally ask | requires memorization |
| **Kebab-case** | `blog-writer` | `BlogWriter`, `blog_writer` |
| **No "claude" or "anthropic"** | any other name | `claude-helper` |

**Name generation process:**
1. Write down what the skill *does* in one sentence
2. Extract the key verb + object (e.g. "sync openrouter models" -> `sync-openrouter-models`)
3. Generate 3-5 variations: verb-first (`add-...`), noun-first (`openrouter-...`), short (`or-sync`), descriptive (`add-top-openrouter-models`)
4. Score each against the criteria above
5. Present candidates to user with brief rationale for each

**Example:**
```
Skill purpose: "Add top OpenRouter models to openclaw config"

Candidates:
1. add-top-openrouter-models — most descriptive, action-clear
2. openrouter-models — shorter, noun-focused
3. openrouter-sync — implies bidirectional (misleading)
4. model-sync — too vague (which models? from where?)

Recommendation: #1 or #2
```

### Step 3: Define Success Criteria

**Quantitative Metrics:**

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Trigger accuracy** | 90% of relevant queries | Run 10-20 test queries. Count auto-loads vs. manual invocations. |
| **Tool call efficiency** | Completes in X calls | Compare with/without skill. Count tool calls and tokens. |
| **API reliability** | 0 failed API calls | Monitor MCP server logs. Track retry rates. |

**Qualitative Metrics:**

| Metric | Assessment Method |
|--------|-------------------|
| **No prompt confusion** | Note how often you need to redirect or clarify |
| **Workflow completion** | Run same request 3-5 times. Compare outputs. |
| **Consistent results** | Can a new user accomplish task on first try? |

### Step 3: Architecture Design

1. Define the workflow as a pipeline
2. Identify which steps need sub-agents vs. direct execution
3. Ensure separation of concerns (build vs. evaluate)
4. Design the iteration/feedback loop if applicable
5. Map data flow between steps
6. Plan for error handling at each step

### Step 4: Write SKILL.md

**A. YAML Frontmatter**

Structure: `[What it does] + [When to use it] + [Key capabilities]`

Required fields:
```yaml
---
name: skill-name  # kebab-case only
description: [What it does]. Use when user [trigger phrases]. [Key capabilities].
---
```

**Description examples:**

✅ Good — specific, actionable, includes triggers:
```
description: Analyzes Figma design files and generates developer handoff
documentation. Use when user uploads .fig files, asks for "design specs",
"component documentation", or "design-to-code handoff".
```

❌ Bad — too vague, no triggers:
```
description: Helps with projects.
```

**Security:** No XML angle brackets in frontmatter. No "claude" or "anthropic" in skill name.

**B. Main Instructions**

Follow this structure:
```
# Skill Title

## Scope & Boundaries
[What it handles / does not handle / where it ends]

## Instructions
### Step 1: [...]
### Step 2: [...]

## Examples
## Troubleshooting
## Output Format
```

**C. Progressive Disclosure**

Keep SKILL.md focused. Move detailed docs to `references/` and link:
```
Before making API calls, consult `references/api-patterns.md` for rate limiting and error handling.
```

### Step 5: Testing (via Tester subagent)

See the Tester protocol in `references/tester-protocol.md` for full validation procedures.

**Iteration Strategy (Anthropic Recommended):**
1. Start with ONE challenging task
2. Iterate until Claude succeeds consistently (max 3 iterations)
3. Extract the winning approach into the skill
4. Then expand to multiple test cases for coverage

---

## Iteration Based on Feedback

Skills are living documents. Iterate based on these signals:

### Undertriggering
- Skill doesn't load when it should → add more trigger phrases, technical keywords
- Users manually enabling it → description field needs more nuance

### Overtriggering
- Skill loads for irrelevant queries → add negative examples, be more specific
- Users disabling it → consider adding compatibility constraints

### Execution Issues
- Inconsistent results → improve instructions, add error handling
- API failures → update troubleshooting section
- User corrections needed frequently → review with 5-whys analysis
