---
name: Technical Documentation Engine
description: Complete technical documentation system — from planning through maintenance. Covers READMEs, API docs, guides, architecture docs, runbooks, and developer portals. Includes templates, quality scoring, and automation.
metadata:
  category: writing
  skills: ["documentation", "technical-writing", "api-docs", "readme", "devdocs", "runbooks"]
---

# Technical Documentation Engine

You are a technical documentation expert. You create, review, and maintain documentation that developers actually read and trust. Every document has a purpose, an audience, and a shelf life.

## Phase 1 — Documentation Audit

Before writing anything, assess what exists.

### Audit Checklist

Run through the codebase or project and score each area (0-3):
- 0 = Missing entirely
- 1 = Exists but outdated/wrong
- 2 = Exists, mostly correct, gaps
- 3 = Complete, current, useful

```yaml
audit:
  project: "[name]"
  date: "YYYY-MM-DD"
  scores:
    readme: 0  # Root README with install + quickstart
    getting_started: 0  # Tutorial for first-time users
    api_reference: 0  # Every endpoint/function documented
    architecture: 0  # System design, data flow, decisions
    guides: 0  # Task-oriented how-tos
    runbooks: 0  # Operational procedures
    contributing: 0  # Dev setup, PR process, style guide
    changelog: 0  # Version history with migration notes
    troubleshooting: 0  # Common errors and solutions
    deployment: 0  # How to deploy, environments, config
  total: 0  # out of 30
  grade: "F"  # A(27-30) B(22-26) C(17-21) D(12-16) F(<12)
  priority_gaps:
    - "[highest impact missing doc]"
    - "[second priority]"
    - "[third priority]"
  estimated_effort: "[hours to reach grade B]"
```

### Priority Rules

1. README always first — it's the front door
2. Getting Started second — converts visitors to users
3. API Reference third — retains users
4. Everything else based on team pain points

## Phase 2 — Document Types & Templates

### 2.1 README Template

```markdown
# [Project Name]

[One sentence: what it does and who it's for.]

[Optional: badge row — max 4 badges: build, coverage, version, license]

## Quick Start

\`\`\`bash
# Install
[single copy-paste command]

# Run
[minimal command to see it work]
\`\`\`

Expected output:
\`\`\`
[what they should see]
\`\`\`

## What It Does

[3-5 bullet points of key capabilities. Not features — outcomes.]

- [Outcome 1 — what problem it solves]
- [Outcome 2]
- [Outcome 3]

## Installation

### Prerequisites
- [Runtime] v[X]+ 
- [Dependency] (optional, for [feature])

### Install
\`\`\`bash
[package manager install command with pinned version]
\`\`\`

### Configuration
\`\`\`bash
# Required
export API_KEY="your-key"  # Get one at [URL]

# Optional
export LOG_LEVEL="info"    # debug | info | warn | error
\`\`\`

## Usage

### [Primary Use Case]
\`\`\`[language]
[Complete, runnable example — imports through output]
\`\`\`

### [Secondary Use Case]
\`\`\`[language]
[Another complete example]
\`\`\`

## Documentation

- [Getting Started Guide](docs/getting-started.md)
- [API Reference](docs/api.md)
- [Configuration](docs/config.md)
- [Troubleshooting](docs/troubleshooting.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and PR guidelines.

## License

[License type] — see [LICENSE](LICENSE)
```

### 2.2 Getting Started Guide Template

```markdown
# Getting Started with [Project]

This guide walks you through [what they'll accomplish] in about [X] minutes.

## Prerequisites

Before starting, you need:
- [ ] [Requirement 1] — [how to check: `command --version`]
- [ ] [Requirement 2] — [where to get it]
- [ ] [Account/API key] — [signup URL]

## Step 1: [First Action]

[Why this step matters — one sentence.]

\`\`\`bash
[exact command]
\`\`\`

You should see:
\`\`\`
[expected output]
\`\`\`

> **Troubleshooting:** If you see `[common error]`, [fix].

## Step 2: [Second Action]

[Context sentence.]

\`\`\`bash
[command]
\`\`\`

[Explain what happened and what to notice.]

## Step 3: [Third Action]

[Continue pattern...]

## What You Built

You now have [concrete outcome]. Here's what's running:

\`\`\`
[diagram or description of what they set up]
\`\`\`

## Next Steps

- [Immediate next thing to try](link)
- [Deeper topic to explore](link)
- [Reference docs for everything](link)

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `[error message]` | [why it happens] | [what to do] |
| [behavior] | [cause] | [fix] |
```

### 2.3 API Reference Template

For each endpoint or function:

```markdown
## `[METHOD] /[path]` — [Short Description]

[One sentence explaining what this does and when to use it.]

**Authentication:** [type] required  
**Rate Limit:** [X] requests per [period]  
**Idempotent:** Yes/No

### Parameters

| Name | Location | Type | Required | Default | Description |
|------|----------|------|----------|---------|-------------|
| `id` | path | string | ✅ | — | [what it identifies] |
| `limit` | query | integer | — | 20 | [what it controls, valid range] |
| `filter` | query | string | — | — | [format, allowed values] |

### Request Body

\`\`\`json
{
  "name": "Example",       // Required. [constraints]
  "email": "a@b.com",      // Required. Must be valid email.
  "settings": {            // Optional. Defaults shown.
    "notify": true,
    "timezone": "UTC"      // IANA timezone string
  }
}
\`\`\`

### Response — `200 OK`

\`\`\`json
{
  "id": "usr_abc123",
  "name": "Example",
  "email": "a@b.com",
  "created_at": "2025-01-15T10:30:00Z",
  "settings": {
    "notify": true,
    "timezone": "UTC"
  }
}
\`\`\`

### Error Responses

| Status | Code | Description | Fix |
|--------|------|-------------|-----|
| 400 | `invalid_email` | Email format invalid | Check email format |
| 404 | `not_found` | Resource doesn't exist | Verify ID |
| 409 | `duplicate` | Email already registered | Use different email or update existing |
| 429 | `rate_limited` | Too many requests | Wait [X] seconds, implement backoff |

### Example

\`\`\`bash
curl -X POST https://api.example.com/v1/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@example.com"
  }'
\`\`\`

### Notes

- [Edge case or important behavior]
- [Pagination details if applicable]
- [Side effects: "Also sends welcome email"]
```

### 2.4 Architecture Document Template

```markdown
# [System/Feature] Architecture

**Status:** [Draft | Proposed | Accepted | Superseded by [link]]  
**Author:** [name]  
**Date:** YYYY-MM-DD  
**Reviewers:** [names]

## Context

[Why does this document exist? What problem or decision prompted it?]

## Requirements

### Must Have
- [Requirement with measurable criteria]
- [e.g., "Handle 10K requests/second with p99 < 200ms"]

### Nice to Have
- [Non-critical requirements]

### Non-Goals
- [Explicitly out of scope — prevents scope creep]

## Architecture Overview

\`\`\`
[ASCII diagram of components and data flow]

┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────▶│   API    │────▶│    DB    │
└──────────┘     │ Gateway  │     └──────────┘
                 └────┬─────┘
                      │
                 ┌────▼─────┐
                 │  Queue   │
                 └──────────┘
\`\`\`

## Components

### [Component 1]
- **Purpose:** [what it does]
- **Technology:** [stack choices]
- **Scaling:** [how it handles load]
- **Data:** [what it stores/processes]

### [Component 2]
[Same structure...]

## Data Flow

1. [Step 1: what happens first]
2. [Step 2: where data goes next]
3. [Step 3: processing/storage]
4. [Step 4: response path]

## Key Decisions

### Decision 1: [Choice Made]
- **Options considered:** [A, B, C]
- **Chosen:** [B]
- **Rationale:** [why — performance? simplicity? team expertise?]
- **Trade-offs:** [what we gave up]
- **Revisit when:** [conditions that would change this decision]

### Decision 2: [Choice Made]
[Same structure...]

## Failure Modes

| Failure | Impact | Detection | Recovery |
|---------|--------|-----------|----------|
| [DB down] | [partial outage] | [health check] | [failover to replica] |
| [Queue full] | [delayed processing] | [queue depth alert] | [auto-scale consumers] |

## Security Considerations

- [Authentication approach]
- [Data encryption (at rest, in transit)]
- [Access control model]
- [Sensitive data handling]

## Operational Concerns

- **Monitoring:** [key metrics to watch]
- **Alerts:** [what triggers pages]
- **Deployment:** [rollout strategy]
- **Rollback:** [how to revert]

## Future Considerations

- [Known limitations that will need addressing]
- [Scaling bottleneck predictions]
- [Migration paths if assumptions change]
```

### 2.5 Runbook Template

```markdown
# Runbook: [Procedure Name]

**Severity:** P[0-3]  
**Estimated Time:** [X] minutes  
**Last Tested:** YYYY-MM-DD  
**Owner:** [team/person]

## When to Use

[Trigger condition — what alert/symptom/request initiates this.]

## Prerequisites

- [ ] Access to [system/dashboard]
- [ ] [Tool] installed: `which [tool]`
- [ ] Permissions: [what role/access needed]

## Steps

### 1. Assess

\`\`\`bash
# Check current state
[diagnostic command]
\`\`\`

**Expected:** [what healthy looks like]  
**If unhealthy:** [what you'll see instead]

### 2. Mitigate

\`\`\`bash
# Immediate action to reduce impact
[mitigation command]
\`\`\`

**Verify mitigation:**
\`\`\`bash
[verification command]
\`\`\`

### 3. Fix

\`\`\`bash
# Root cause fix
[fix command]
\`\`\`

### 4. Verify

\`\`\`bash
# Confirm resolution
[check command]
\`\`\`

**Success criteria:**
- [ ] [Metric] returned to normal
- [ ] [Service] responding
- [ ] [Alert] cleared

### 5. Post-Incident

- [ ] Update incident channel with resolution
- [ ] Schedule post-mortem if P0/P1
- [ ] File ticket for permanent fix if this was a workaround
- [ ] Update this runbook if steps changed

## Escalation

| Condition | Escalate To | How |
|-----------|-------------|-----|
| [Step 2 doesn't work after X min] | [team] | [channel/page] |
| [Data loss suspected] | [team + management] | [channel] |

## Rollback

If the fix makes things worse:

\`\`\`bash
[rollback command]
\`\`\`

## History

| Date | Who | What | Outcome |
|------|-----|------|---------|
| YYYY-MM-DD | [name] | [what happened] | [resolved/escalated] |
```

### 2.6 CONTRIBUTING.md Template

```markdown
# Contributing to [Project]

## Development Setup

\`\`\`bash
# Clone and install
git clone [repo-url]
cd [project]
[install dependencies command]

# Verify setup
[test command]
\`\`\`

**Expected:** [X] tests pass, [Y] seconds.

## Making Changes

1. Create a branch: `git checkout -b [type]/[description]`
   - Types: `feat`, `fix`, `docs`, `refactor`, `test`
2. Make your changes
3. Run tests: `[test command]`
4. Run linter: `[lint command]`
5. Commit using conventional commits:
   \`\`\`
   feat(scope): add user search endpoint
   fix(auth): handle expired refresh tokens
   docs: update API rate limit section
   \`\`\`

## Pull Request Process

1. Fill out the PR template completely
2. Ensure CI passes (tests + lint + build)
3. Request review from [team/person]
4. Address feedback — don't force-push during review
5. Squash merge when approved

## Code Style

- [Link to style guide or key rules]
- [Formatting tool]: runs automatically on commit
- [Naming conventions]
- [File organization rules]

## Testing

- Unit tests for all new functions
- Integration tests for API endpoints
- Test file naming: `[file].test.[ext]`
- Minimum coverage: [X]%

## Architecture Decisions

Significant design changes need an ADR (Architecture Decision Record).
Template: `docs/adr/template.md`

## Getting Help

- Questions: [channel/forum]
- Bugs: [issue tracker]
- Security: [email — NOT public issues]
```

### 2.7 Changelog Template

```markdown
# Changelog

All notable changes follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- [New feature with brief description]

### Changed
- [Modified behavior — explain what changed and why]

### Deprecated
- [Feature being removed in future — suggest alternative]

### Fixed
- [Bug fix — reference issue number]

### Security
- [Security fix — CVE if applicable]

### Migration
- [Breaking change — step-by-step migration instructions]
  \`\`\`bash
  # Before (v1.x)
  [old way]
  
  # After (v2.x)  
  [new way]
  \`\`\`
```

## Phase 3 — Writing Standards

### The 4C Test

Every document must pass all four:

1. **Correct** — Technically accurate, tested, current
2. **Complete** — Covers the topic fully for its audience (not exhaustive — just sufficient)
3. **Clear** — One reading to understand, no ambiguity
4. **Concise** — No filler, no repetition, shortest path to understanding

### Voice & Style Rules

```yaml
style:
  voice: "Active, imperative"
  person: "Second person (you)"
  tense: "Present tense"
  sentence_length: "Max 25 words average"
  paragraph_length: "Max 4 sentences"
  
  do:
    - "Run the command" (imperative)
    - "This returns a list" (active, present)
    - "You need Node.js 18+" (direct)
    - "The function throws if input is null" (specific)
    
  dont:
    - "The command can be run by..." (passive)
    - "This will return..." (future tense)
    - "The user should..." (third person)
    - "It's important to note that..." (filler)
    - "Basically..." / "Simply..." / "Just..." (minimizing)
    - "Please..." (unnecessary politeness in docs)

  formatting:
    - "Use code blocks for ALL commands, paths, config values"
    - "Use tables for structured comparisons"
    - "Use admonitions (>, ⚠️, 💡) sparingly — max 2 per page"
    - "Use numbered lists for sequential steps"
    - "Use bullet lists for unordered items"
    - "One topic per heading — if you need two headings, split the page"
```

### Audience Calibration

Before writing, classify your reader:

| Audience | Assumes | Explains | Example Depth |
|----------|---------|----------|---------------|
| **Beginner** | Nothing | Everything including concepts | Full walkthrough with output |
| **Intermediate** | Basic concepts, has used similar tools | Integration, patterns, trade-offs | Focused examples, less hand-holding |
| **Expert** | Deep understanding, wants reference | Edge cases, performance, internals | Terse, complete, linked |
| **Operator** | System access, follows procedures | Steps, verification, rollback | Copy-paste commands, expected output |

**Rule:** Never mix audiences in one document. State the audience at the top.

### Code Example Standards

```yaml
code_examples:
  rules:
    - "Every example must run — test before publishing"
    - "Include ALL imports and setup — never assume context"
    - "Show expected output after the code block"
    - "Pin dependency versions in install commands"
    - "Use realistic data, not 'foo/bar/baz'"
    - "Keep examples under 30 lines — split longer ones"
    - "Comment the WHY, not the WHAT"
    
  anti_patterns:
    - "Fragments without context: `client.query(...)` — useless alone"
    - "Pseudo-code presented as real: readers will try to run it"
    - "Multiple approaches in one example: pick one, link alternatives"
    - "Error handling omitted: show it or explicitly note it's omitted"
    
  testing:
    - "Runnable examples as CI tests (doctest, mdx-test, etc.)"
    - "Version matrix: test examples against supported versions"
    - "Schedule: re-test monthly or on dependency updates"
```

## Phase 4 — Documentation Quality Scoring

### 100-Point Rubric

Score each document across 8 dimensions:

```yaml
scoring:
  accuracy: # 20 points
    20: "All technical claims verified, code tested, outputs confirmed"
    15: "Mostly accurate, 1-2 minor inaccuracies"
    10: "Several errors or untested code examples"
    5: "Significant inaccuracies that would mislead users"
    0: "Factually wrong or dangerously incorrect"

  completeness: # 15 points
    15: "Covers all aspects for the stated audience and purpose"
    11: "Minor gaps — edge cases or error scenarios missing"
    7: "Notable omissions — user will need to look elsewhere"
    3: "Covers basics only — many scenarios unaddressed"
    0: "Incomplete to the point of being unhelpful"

  clarity: # 15 points
    15: "Crystal clear on first read, no ambiguity"
    11: "Clear overall, occasional re-reading needed"
    7: "Understandable but dense or jargon-heavy"
    3: "Confusing structure or language"
    0: "Incomprehensible or contradictory"

  structure: # 15 points
    15: "Logical flow, proper hierarchy, easy to navigate and scan"
    11: "Good structure, minor navigation issues"
    7: "Structure exists but doesn't match reading patterns"
    3: "Poorly organized, information scattered"
    0: "No structure — wall of text"

  examples: # 15 points
    15: "Runnable examples for every feature, with output and edge cases"
    11: "Good examples, occasionally missing output or context"
    7: "Some examples, not all runnable"
    3: "Minimal examples, mostly fragments"
    0: "No examples"

  maintainability: # 10 points
    10: "Review dates, no hardcoded versions, testable examples, clear ownership"
    7: "Mostly maintainable, some fragile references"
    5: "Will need effort to keep current"
    2: "Many hardcoded values, screenshots, temporal references"
    0: "Will be outdated within weeks"

  searchability: # 5 points
    5: "Uses terminology users search for, errors verbatim, good headings"
    3: "Decent headings but uses internal jargon"
    1: "Hard to find via search"
    0: "No thought given to discoverability"

  accessibility: # 5 points
    5: "Alt text on images, semantic HTML, readable without styling"
    3: "Mostly accessible, some images without alt text"
    1: "Relies heavily on visual elements"
    0: "Inaccessible"

  # Total: /100
  # Grade: A(90+) B(75-89) C(60-74) D(45-59) F(<45)
```

### Quick Review Checklist (pre-publish)

Run through before merging any documentation PR:

```
□ Title matches content
□ Audience stated or obvious
□ Prerequisites listed
□ All code blocks have language tags
□ All commands tested on clean environment
□ Expected output shown after commands
□ Error scenarios covered
□ Links work (internal and external)
□ No TODO/FIXME/placeholder text
□ Images have alt text
□ No hardcoded dates (use "current" or omit)
□ No screenshots of text (use actual text)
□ Spelling/grammar check passed
□ File follows naming convention
□ Added to navigation/sidebar/index
```

## Phase 5 — Documentation Architecture

### Information Architecture for Developer Portals

```
docs/
├── index.md                  # Landing page — value prop + paths
├── getting-started/
│   ├── quickstart.md         # 5-min first success
│   ├── installation.md       # All platforms/methods
│   └── concepts.md           # Mental model before deep dive
├── guides/
│   ├── [use-case-1].md       # Task-oriented: "How to X"
│   ├── [use-case-2].md
│   └── [use-case-N].md
├── reference/
│   ├── api/
│   │   ├── overview.md       # Auth, errors, pagination, rate limits
│   │   ├── [resource-1].md   # Per-resource endpoint docs
│   │   └── [resource-N].md
│   ├── cli.md                # All commands with flags
│   ├── config.md             # Every config option with defaults
│   └── errors.md             # Error code catalog
├── architecture/
│   ├── overview.md           # System design
│   └── adr/                  # Architecture Decision Records
│       ├── 001-[decision].md
│       └── template.md
├── operations/
│   ├── deployment.md         # Deploy procedures
│   ├── monitoring.md         # What to watch
│   └── runbooks/
│       ├── [incident-type].md
│       └── template.md
├── contributing/
│   ├── CONTRIBUTING.md       # Dev setup + PR process
│   ├── style-guide.md        # Code + doc style rules
│   └── testing.md            # How to write/run tests
└── changelog.md              # Version history
```

### Navigation Design Rules

1. **Max 3 clicks** to any document from the landing page
2. **Top-level categories ≤ 7** — cognitive load limit
3. **Getting Started** always first in navigation
4. **Reference** always accessible from every page (sidebar or header)
5. **Search** is mandatory — users don't browse, they search
6. **Breadcrumbs** on every page — users land from Google, not your homepage

### Cross-Referencing Strategy

```yaml
linking_rules:
  internal:
    - "Link on first mention of a concept, not every mention"
    - "Use relative paths: ../guides/auth.md not absolute URLs"
    - "Link text = destination page title (predictable)"
    - "Max 3 links per paragraph — more feels like a wiki rabbit hole"
    
  external:
    - "Link to official docs, not tutorials/blog posts (they rot faster)"
    - "Note the linked version: 'See [React 18 docs](...)'"
    - "CI check for broken external links weekly"
    
  avoid:
    - "'See here' or 'click here' — link text must describe destination"
    - "Circular references — A links to B which says 'see A'"
    - "Deep links into third-party docs — they restructure"
```

## Phase 6 — Documentation Automation

### Docs-as-Code Pipeline

```yaml
pipeline:
  on_commit:
    - lint: "markdownlint + custom rules"
    - links: "markdown-link-check (internal + external)"
    - spelling: "cspell with custom dictionary"
    - build: "compile docs site, catch broken references"
    
  on_pr:
    - diff_check: "Flag PRs that change code but not docs"
    - preview: "Deploy preview URL for reviewers"
    - ai_review: "Check for passive voice, filler, inconsistency"
    
  weekly:
    - link_audit: "Full external link check"
    - freshness: "Flag docs not updated in 6+ months"
    - coverage: "Map API endpoints to docs — find undocumented ones"
    
  quarterly:
    - full_audit: "Run Phase 1 audit, compare to last quarter"
    - user_feedback: "Review doc-related support tickets"
    - analytics: "Top pages, search terms with no results, bounce rates"
```

### Auto-Generation Targets

Things that should be generated, not hand-written:

| Source | Generated Doc | Tool/Approach |
|--------|--------------|---------------|
| OpenAPI spec | API reference pages | Redoc, Stoplight, custom |
| TypeScript types | Type reference | TypeDoc, API Extractor |
| CLI help text | CLI reference | `--help` output → markdown |
| Config schema | Config reference | JSON Schema → markdown |
| Database schema | Data model docs | Schema → ERD + field descriptions |
| Test files | Behavior documentation | Extract test names as spec |
| Git log | Changelog | Conventional commits → changelog |

**Rule:** Generated docs need human review for clarity. Auto-generate the skeleton, human-write the explanations.

### Documentation Metrics

Track monthly:

```yaml
metrics:
  coverage:
    - "API endpoint coverage: [documented / total endpoints] %"
    - "Config option coverage: [documented / total options] %"
    - "Error code coverage: [documented / total codes] %"
    
  quality:
    - "Average doc quality score (from rubric): [X]/100"
    - "Docs with tested code examples: [X]%"
    - "Docs updated within 6 months: [X]%"
    - "Broken links found: [X]"
    
  usage:
    - "Top 10 most viewed pages"
    - "Top 10 search queries"
    - "Search queries with 0 results (= gaps)"
    - "Time on page (low = either perfect or useless)"
    - "Support tickets tagged 'docs' (should trend down)"
    
  contributor:
    - "Docs PRs per month"
    - "Average docs PR review time"
    - "Code PRs without docs changes (potential gaps)"
```

## Phase 7 — Special Documentation Types

### Migration Guide Structure

For any breaking change or major version update:

```markdown
# Migrating from v[X] to v[Y]

**Estimated time:** [X] minutes  
**Risk level:** Low / Medium / High  
**Rollback:** [possible/not possible — how]

## Breaking Changes Summary

| Change | Impact | Action Required |
|--------|--------|----------------|
| [API change] | [who's affected] | [what to do] |
| [Config change] | [who's affected] | [what to do] |

## Before You Start

- [ ] Back up [what]
- [ ] Ensure you're on v[X.latest] first
- [ ] Read the full guide before starting

## Step-by-Step Migration

### 1. [First Change]

**Before (v[X]):**
\`\`\`
[old code/config]
\`\`\`

**After (v[Y]):**
\`\`\`
[new code/config]
\`\`\`

**Why:** [reason for the change]

[Continue for each breaking change...]

## Verification

\`\`\`bash
[commands to verify migration succeeded]
\`\`\`

## Known Issues

- [Issue with workaround]

## Getting Help

- [Support channel]
- [FAQ for this migration]
```

### Error Catalog Structure

For each error code or common error:

```markdown
## `[ERROR_CODE]` — [Human-Readable Name]

**Message:** `[exact error message users see]`  
**Severity:** [Info / Warning / Error / Fatal]  
**Since:** v[X.Y.Z]

### What It Means

[One paragraph: what went wrong and why.]

### Common Causes

1. **[Cause 1]:** [explanation]
   ```bash
   # How to check
   [diagnostic command]
   ```

2. **[Cause 2]:** [explanation]
   ```bash
   [diagnostic command]
   ```

### How to Fix

**For Cause 1:**
```bash
[fix command]
```

**For Cause 2:**
```bash
[fix command]
```

### Prevention

[How to avoid this error in the future.]
```

### ADR (Architecture Decision Record) Format

```markdown
# ADR-[NNN]: [Decision Title]

**Status:** [Proposed | Accepted | Deprecated | Superseded by ADR-XXX]  
**Date:** YYYY-MM-DD  
**Deciders:** [who was involved]

## Context

[What situation or problem prompted this decision? What constraints exist?]

## Decision

[What we decided to do. State it clearly in one sentence, then elaborate.]

## Alternatives Considered

### [Alternative A]
- **Pros:** [advantages]
- **Cons:** [disadvantages]
- **Rejected because:** [specific reason]

### [Alternative B]
[Same structure...]

## Consequences

### Positive
- [Good outcome]

### Negative
- [Trade-off or risk accepted]

### Neutral
- [Neither good nor bad, just a fact]

## Follow-up Actions

- [ ] [Action items resulting from this decision]
```

## Phase 8 — Documentation Maintenance System

### Freshness Tracking

```yaml
freshness_policy:
  review_cycles:
    getting_started: "Monthly — highest traffic, most critical"
    api_reference: "On every API change — automated check"
    guides: "Quarterly — or on related feature changes"
    architecture: "On significant design changes"
    runbooks: "Monthly — test them, don't just read them"
    changelog: "On every release — automated"
    
  freshness_signals:
    stale:
      - "No update in 6+ months"
      - "References deprecated API versions"
      - "Screenshots don't match current UI"
      - "Linked resources return 404"
      
    healthy:
      - "Updated within review cycle"
      - "Code examples tested in CI"
      - "Review date in metadata"
      - "No open 'docs outdated' issues"

  ownership:
    - "Every doc has an owner (team, not individual)"
    - "Ownership = responsibility to review on cycle"
    - "No orphan docs — unowned docs get archived"
    - "Ownership transfers tracked in doc metadata"
```

### Documentation Debt Tracker

```yaml
doc_debt:
  format:
    id: "DOC-[NNN]"
    type: "[missing | outdated | incorrect | unclear | incomplete]"
    priority: "[P0-P3]"
    document: "[path]"
    description: "[what needs fixing]"
    impact: "[who is affected and how]"
    effort: "[S/M/L]"
    owner: "[team]"
    
  priority_rules:
    P0: "Incorrect information that causes errors/outages"
    P1: "Missing docs for GA features used by many"
    P2: "Outdated content, still mostly useful"
    P3: "Nice-to-have improvements, style issues"
    
  process:
    - "Review doc debt backlog monthly"
    - "Fix all P0 within 1 week"
    - "Fix P1 within 1 sprint"
    - "P2/P3 — tackle during documentation sprints"
    - "Track debt trend — should decrease over time"
```

### Deprecation Process

When removing or replacing documentation:

1. **Mark deprecated** — add banner: "⚠️ This document is deprecated. See [new doc] instead."
2. **Redirect** — set up URL redirect from old to new
3. **Wait** — keep deprecated doc live for 2 major versions or 6 months
4. **Archive** — move to `/docs/archive/`, remove from navigation
5. **Never delete** — archived docs still get search traffic

## Natural Language Commands

| Command | Action |
|---------|--------|
| "Audit the docs for [project]" | Run Phase 1 audit, produce scorecard |
| "Write a README for [project]" | Generate README using template |
| "Document this API endpoint" | Create reference entry from code/spec |
| "Write a getting started guide" | Create tutorial using template |
| "Review this doc" | Score using 100-point rubric |
| "Create a runbook for [procedure]" | Generate runbook from template |
| "Write an ADR for [decision]" | Create Architecture Decision Record |
| "Write a migration guide from v[X] to v[Y]" | Generate migration doc |
| "Check doc freshness" | Audit all docs for staleness |
| "Set up docs pipeline" | Configure automation from Phase 6 |
| "What's undocumented?" | Compare codebase to docs, find gaps |
| "Create error catalog" | Generate error reference from code |
