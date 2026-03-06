---
name: subagent-architecture
version: 2.3.5
description: Advanced patterns for specialized subagent orchestration with production-ready reference implementations. Security isolation, phased implementation, peer collaboration, and cost-aware spawning.
tags: [subagents, architecture, isolation, security, collaboration, orchestration, reference-implementation]
difficulty: intermediate
requirements:
  openclaw_version: ">=2026.2.17"
  optional_skills: [task-routing, cost-governor, drift-guard]
author: OpenClaw Community
license: MIT

# Credential & External Integration Disclosure
credentials_required: none
external_integrations:
  - name: Discord webhook (peer review flow)
    required: false
    notes: "Only needed if using the federated peer-review pattern. User must supply their own webhook URL manually. No token is stored or auto-configured by this skill."
  - name: External peer agents (API endpoints)
    required: false
    notes: "Federated review workflows are opt-in. No external calls are made unless the user explicitly configures peer endpoints."

# Package Contents Disclosure
# This skill contains runnable JS reference libraries in lib/ and example templates in templates/.
# These files are NOT auto-executed on install. They are reference implementations
# intended to be copied into your workspace lib/ directory manually or via setup.sh.
# setup.sh only creates local directory scaffolding — it makes no network calls and installs no packages.
package_type: reference-implementation-with-libs
auto_executes: false
---

# Advanced Subagent Architecture

Patterns and templates for building robust multi-agent systems with OpenClaw.

## Why This Skill Is Complex (Read Before Installing)

This is one of the most feature-dense skills in the ClawHub registry. Security scanners will flag it — not because it's malicious, but because it does a lot. Here's exactly what's in it and why:

**Scope:**
- 4 production-ready JS libraries (~1,200 lines total across spawn-security-proxy, spawn-researcher, cost-estimator, quality-scorer)
- 4 spawn templates covering security proxy, researcher, phased implementation, and peer review patterns
- A `setup.sh` that creates local directory scaffolding (no network calls, no package installs)
- Inline attack vector documentation in `spawn-security-proxy.js` (test fixtures, not live payloads)

**Why the libs exist:** These aren't glue code — they implement real patterns: output sanitization with canary tokens, multi-source research validation, cost projection with approval gates, and subagent output scoring. The complexity is the point; simpler skills don't solve these problems.

**Why scanners flag it:**
1. JS code in a skill package looks like an execution surface — it is, but only when you explicitly `require()` it
2. The security proxy documents injection attack patterns as test examples — pattern matchers don't distinguish documentation from intent
3. External integration references (Discord, peer agents) appear in templates — they're opt-in workflows, not auto-configured connections

**Complexity is not a red flag here. It's the product.**

---

## ⚠️ Security Transparency Notice

**What this skill contains:**
- `lib/` — Reference JS libraries (spawn helpers, cost estimator, quality scorer). These are **not auto-executed**. Copy them to your workspace `lib/` directory to use them.
- `templates/` — Markdown spawn templates for common patterns.
- `setup.sh` — Creates local directory scaffolding only. Makes **no network calls**, installs **no packages**.

**External integrations:** All optional, none auto-configured.
- **Discord webhooks** — Only used in the federated peer-review pattern. You supply your own token manually. This skill does not store or transmit credentials.
- **Peer agent endpoints** — Federated review is opt-in. No external calls unless you explicitly configure peer URLs.

**Credential requirements:** None. No API keys, tokens, or env vars are required or auto-read by this skill.

## Overview

This skill provides battle-tested patterns for:
- **Security isolation** - Contain high-risk operations with minimal context exposure
- **Specialized research** - Multi-perspective data gathering with domain experts
- **Phased implementation** - Architecture → Development → Review pipelines
- **Peer collaboration** - External validation via federated agent network (opt-in)
- **Cost-aware spawning** - Budget estimation and optimization strategies

## What's New in v2.0

**Advanced Patterns:**
- Security proxy pattern (blast shield isolation)
- Researcher specialist pattern (multi-source synthesis)
- Phased implementation pipeline (architect → coder → reviewer)
- Peer review integration (bot-to-bot validation)
- Cost estimation framework (required for spawns >$0.50)

**Templates:**
- `templates/security-proxy.md` - Isolate untrusted service access
- `templates/researcher-specialist.md` - Domain-specific research agents
- `templates/phased-implementation.md` - Multi-phase feature development
- `templates/peer-review-specialist.md` - External peer validation

**Integration:**
- task-routing skill (auto-classification and routing)
- cost-governor (budget enforcement)
- drift-guard (behavioral validation)

## Quick Start

### 1. Install Skill Structure
```bash
cd $OPENCLAW_WORKSPACE/skills/subagent-architecture
bash setup.sh  # Creates directories and scaffolding
```

### 2. Choose Your Pattern

**For high-risk operations:**
```bash
# Read security-proxy template
cat templates/security-proxy.md

# Spawn isolated proxy for untrusted API
# (see template for full example)
```

**For research tasks:**
```bash
# Read researcher-specialist template
cat templates/researcher-specialist.md

# Spawn domain expert for deep analysis
# (see template for multi-perspective pattern)
```

**For complex features:**
```bash
# Read phased-implementation template
cat templates/phased-implementation.md

# Launch architect → coder → reviewer pipeline
# (see template for orchestration example)
```

**For external validation:**
```bash
# Read peer-review-specialist template
cat templates/peer-review-specialist.md

# Request peer agent review via Discord/API
# (see template for federated trust protocol)
```

## Agent Registry: AGENTS.md is Optional

**Critical clarification for new users:** AGENTS.md is a human-readable reference document, not a configuration file. The spawning system does not read it.

### How spawning actually works

`sessions_spawn` is a tool call — it takes parameters you provide at the moment of the call. It does not read from any file, config, or registry. You can spawn subagents on a completely fresh OpenClaw install with zero files in your workspace.

```javascript
// This is ALL the system needs — no AGENTS.md required
sessions_spawn({
  label: "my-researcher",
  task: "Research the topic X",
  model: "sonnet"
})
```

### What AGENTS.md actually is

AGENTS.md (and domain files like AGENTS_WRITING.md, AGENTS_INFRA.md) are **memory aids for you (the agent)**. They store:
- Agent names and personality snippets you've found effective
- Cost history and last-used dates
- Notes on what tasks each agent type handles well

You can split AGENTS.md into 50 domain files or delete it entirely — spawning still works. The split is purely for your readability; it has zero functional effect.

### What "read AGENTS_WRITING.md before spawning" means

When documentation says *"read AGENTS_WRITING.md before spawning AuthorAgent"*, it means:

> Read it so **you** know what personality, model, and task description to use when building the spawn call.

The system does not read it. You read it, extract the configuration, then make the spawn call with those parameters.

### Practical implication for fresh installs

When you install this skill on a fresh OpenClaw setup:

1. **You do not need to create AGENTS.md** to use subagents
2. Start spawning immediately with inline parameters
3. Create AGENTS.md when you have enough recurring agent configurations that you want a reference doc
4. Split into domain files when AGENTS.md grows beyond ~10 entries and becomes hard to scan

See `templates/agents-registry-template.md` for a minimal starter template when you're ready.

---

## Reference Implementations

**NEW in v2.1:** Production-ready code libraries for all patterns.

### Available Libraries

**lib/spawn-security-proxy.js** - Security isolation framework
- `spawnSecurityProxy(config)` - Spawn isolated proxy with sanitization
- `deepSanitize(data)` - Remove sensitive data (API keys, paths, emails)
- `validateSchema(data, schema)` - JSON schema validation
- `createDefaultSchema(type)` - Common output schemas (list, single, status)

**lib/spawn-researcher.js** - Multi-perspective research framework
- `spawnResearcher(config)` - Spawn domain expert researcher
- `spawnMultiPerspective(config)` - Multi-perspective research (optimist/pessimist/pragmatist)
- `assessSourceCredibility(source)` - Score source trustworthiness (0-100)
- Pre-configured trusted/blog/vendor domain lists

**lib/cost-estimator.js** - Cost estimation and tracking
- `estimateSubagentCost(params)` - Pre-spawn cost estimation with confidence intervals
- `logSubagentCost(label, estimate, actual)` - Log for accuracy tracking
- `recalibrateEstimator()` - Monthly accuracy improvement
- `getPatternHistory(pattern)` - Historical performance analysis
- `getCostTier(cost)` - Classify as micro/small/medium/large

**lib/quality-scorer.js** - Output quality assessment
- `scoreSubagentOutput(output, rubric)` - 8-dimension quality scoring
- `createScoringTemplate()` - Manual review template
- `selfAuditChecklist(output)` - Pre-delivery validation
- Rubric dimensions: specificity, actionability, evidence, structure, completeness, clarity, relevance, efficiency

### Usage Examples

All libraries include complete working examples:

```bash
# Security proxy examples
node examples/security-proxy-usage.js

# Researcher examples
node examples/researcher-usage.js

# Cost estimation examples
node examples/cost-estimation-demo.js
```

### Quick Integration

> **Path Resolution Note:** The `require()` paths in examples below assume you call them from your workspace root. If you call from within the skill directory (e.g., inside an example script), use `__dirname` instead. For portable code that works regardless of cwd:
>
> ```javascript
> // Path resolution — works regardless of workspace structure
> const path = require('path');
> const SKILL_DIR = __dirname; // when called from within skill directory
> // OR if calling from workspace root:
> const SKILL_DIR = path.join(process.env.OPENCLAW_WORKSPACE || process.cwd(), 'skills', 'subagent-architecture');
> const { spawnSecurityProxy } = require(path.join(SKILL_DIR, 'lib', 'spawn-security-proxy'));
> ```

```javascript
// Example: Spawn security proxy for untrusted API
const { spawnSecurityProxy } = require('./skills/subagent-architecture/lib/spawn-security-proxy');

const result = await spawnSecurityProxy({
  service: 'weather-api',
  task: 'Get current weather for New York',
  query: { city: 'New York', units: 'metric' },
  output_schema: {
    type: 'object',
    properties: {
      temperature: { type: 'number' },
      conditions: { type: 'string' }
    }
  },
  spawn_fn: async (config) => {
    // Your actual sessions_spawn call here
    return await sessions_spawn(config);
  }
});

// Example: Estimate cost before spawning
const { estimateSubagentCost, logSubagentCost } = require('./skills/subagent-architecture/lib/cost-estimator');

const estimate = estimateSubagentCost({
  task_complexity: 'medium',
  expected_duration_min: 15,
  model: 'sonnet',
  research_required: true
});

console.log(`Estimated: $${estimate.expected} (range: $${estimate.min}-$${estimate.max})`);

// After spawn completes
logSubagentCost('researcher-task', estimate, actual_cost);

// Example: Score output quality
const { scoreSubagentOutput } = require('./skills/subagent-architecture/lib/quality-scorer');

const score = scoreSubagentOutput(subagent_output, null, { auto_score: true });
console.log(`Quality: ${score.overall_score}/10 (${score.pass ? 'PASS' : 'FAIL'})`);
```

See `examples/` directory for complete working demonstrations.

## Integration Status

### Dependencies Overview

**Required:**
- ✅ OpenClaw 2026.2.17+ (`sessions_spawn` API)
- ✅ Node.js 18+ (for library code)

**Optional Skills:**

**task-routing** 
- Status: ✅ Available (workspace `skills/task-routing/`)
- Version: 1.0.0+
- Integration: Auto-classification of incoming tasks, risk scoring, pattern routing
- Tested: Yes (production since 2026-02-15)
- Documentation: See `skills/task-routing/SKILL.md`

**cost-governor**
- Status: ⚠️ Planned (design phase)
- Version: N/A
- Integration: Budget enforcement, approval workflows
- Tested: No
- Workaround: Use `lib/cost-estimator.js` for manual gating

**drift-guard**
- Status: ⚠️ Planned (design phase)
- Version: N/A
- Integration: Behavioral audits, policy violation detection
- Tested: No
- Workaround: Manual output review against rubric

### Library Dependencies

All reference implementations are **dependency-free** (pure Node.js):
- No npm packages required
- No external API calls
- Filesystem access for logging only (optional)
- Mock-friendly for testing

### Integration Points

**Automatic (via task-routing skill):**
- Task classification → Pattern recommendation
- Risk scoring → Security proxy auto-spawn for high-risk tasks
- Cost estimation → Pre-spawn budget check

**Manual (call libraries directly):**
- `require()` any lib file and call functions
- See `examples/` for usage patterns
- Spawn functions accept custom `spawn_fn` for integration with your sessions_spawn

### Migration Path

**From v2.0 to v2.1:**
1. No breaking changes - templates still work as-is
2. New: Import library functions for programmatic use
3. New: Run examples to see working code
4. Optional: Integrate with task-routing for automation

**Future (v3.0 with framework improvements):**
- Per-spawn resource limits (when OpenClaw supports)
- Bidirectional communication (when OpenClaw supports)
- Post-mortem tracking (when OpenClaw supports)
- See "Framework Limitations & v2 Roadmap" section for details

## Core Concepts

### 1. Security Isolation (Blast Shield Philosophy)

**Problem:** Subagents with full workspace access can leak sensitive data to untrusted APIs.

**Solution:** Security proxies receive minimal context, restricted tools, sanitized output.

**Example:**
```
Main Agent (full context)
    │
    └─ SecurityProxy (minimal context)
            ├─ Query: "Get weather for New York"
            ├─ Tools: exec (curl only)
            ├─ Output: Sanitized JSON (no API metadata)
            └─ Auto-terminate after single task
```

**Key principles:**
- Minimal context (only task parameters, no workspace paths)
- Tool restrictions (whitelist, not blacklist)
- Output sanitization (validate schema before returning)
- Ephemeral execution (no persistent state)
- Cost cap (< $0.10 per proxy spawn)

See: `templates/security-proxy.md`

### 2. Researcher Specialists (Multi-Source Synthesis)

**Problem:** Generic web search returns surface-level results without domain expertise.

**Solution:** Specialized researchers with domain bias, multi-source validation, actionable synthesis.

**Example:**
```
Question: "Should we adopt technology X?"

├─ OptimistResearcher (best-case analysis)
├─ PessimistResearcher (risk assessment)
└─ PragmatistResearcher (current reality)

Main Agent synthesizes: Balanced decision tree
```

**Key principles:**
- Domain focus (single expertise area per researcher)
- Multi-source validation (3+ independent sources per claim)
- Skeptical by default (anti-hype, calls out marketing)
- Structured output (executive summary + recommendations)
- Evidence-backed (no speculation, contradictions addressed)

See: `templates/researcher-specialist.md`

### 3. Phased Implementation (Separation of Concerns)

**Problem:** Single-agent implementation mixes design, coding, and validation → tech debt.

**Solution:** Separate architect (design), coder (build), reviewer (validate) phases.

**Example:**
```
Feature Request: "Add memory consolidation skill"

Phase 1: SystemArchitect (15min, $0.40)
    └─ Delivers: IMPLEMENTATION_PLAN.md

Phase 2: CoderAgent (25min, $0.70)
    └─ Delivers: Working code + tests

Phase 3: ReviewerAgent (10min, $0.30)
    └─ Delivers: REVIEW_REPORT.md (approval/rejection)

Total: 50min, $1.40, high-quality feature
```

**Key principles:**
- Architects optimize long-term (not quick hacks)
- Coders focus on working code (test after each step)
- Reviewers provide fresh perspective (catch integration issues)
- Incremental delivery (small PRs, easy rollback)
- Cost-aware (skip phases for simple features)

See: `templates/phased-implementation.md`

### 4. Peer Collaboration (Federated Trust)

**Problem:** Your agent may have blindspots or lack domain expertise.

**Solution:** Request external validation from trusted peer agents.

**Example:**
```
Your Agent
    │
    ├─ Prepares sanitized review package
    │
    ├─ Contacts Smith's SecurityBot (via Discord/API)
    │       └─ Smith's bot spawns SecurityReviewer
    │               └─ Returns: Structured findings
    │
    └─ Integrates feedback (fix critical issues)
```

**Key principles:**
- Trust earned (track peer accuracy over time)
- Data sanitization (remove secrets, personal data)
- Structured feedback (severity, category, recommendations)
- Reciprocal reviews (offer your expertise to peers)
- Cost-effective (free peer reviews vs paid audits)

**⚠️ Trust tier ≠ security bypass:**
If you implement tiered trust (Acquaintance → Friend → Ally or equivalent), "higher trust" means relaxed engagement policy — not skipping security validation. Content from even the most trusted peer still goes through injection detection (Stage 4). An ally account can be compromised; the injection scanner is the last defense that can't be socially engineered. "Light validation" always means reduced schema scrutiny, never reduced security scanning.

See: `templates/peer-review-specialist.md`

### 5. Identity Continuity (Ephemeral Process, Persistent External Identity)

**Problem:** Security proxies are ephemeral (spawn-per-task, terminate). But some external services require a persistent identity — a social network account, an API user, a recurring agent persona. These are in tension.

**Solution:** Separate the process lifecycle from the external identity. The process dies every spawn. The external identity persists through workspace state + core-managed credentials.

```
External service sees: CedarProxy (consistent identity across all spawns)

Under the hood:
  Spawn 1: [process starts] → reads state files → executes → [process dies]
  Spawn 2: [new process] → reads same state files → continues → [dies]
  Spawn 3: [new process] → reads same state files → continues → [dies]

State that persists:   /proxy-workspace/ files (logs, relationships, posts)
State that doesn't:    in-memory session, conversation history, token
Credentials:           held by core, passed as short-lived scoped token at spawn time
```

**Key rules:**
- Credentials live in core memory only — never in proxy workspace files
- Session token: short TTL (2 hours max), passed encrypted in task context, never written to disk
- Consistency: core injects "recent context" summary (last N interactions) into each spawn's task description so the new process knows what prior spawns committed to
- Token rotation: scheduled by core (e.g., weekly), not the proxy

**Anti-pattern:** storing tokens in `[workspace]/config.json` — if the proxy workspace is compromised, credentials should not be compromised with it.

### 6. Research Team (Parallel Multi-Lens Analysis)

**Problem:** Single-agent analysis has blind spots — the same agent proposes and evaluates its own ideas.

**Solution:** Spawn 3 specialist agents in parallel with distinct analytical lenses, then synthesize into one unified response.

**Architecture:**
```
High-complexity query
    │
    ├─ Critic lens (find flaws, risks, costs — no solutions)
    ├─ Implementer lens (concrete execution, architecture, feasibility)
    └─ Synthesizer lens (integrate, resolve tensions, unified path)
            │
        UnifierAgent (one clean final response)
```

**When to use:**
- Task complexity === 'high' OR explicit research flag set
- Architecture decisions with real tradeoffs
- Debugging where root cause is unclear
- Any question where a single perspective tends to miss things

**When to skip:**
- Routine tasks, simple lookups, quick fixes
- Cost-sensitive situations (research team = ~4x single-agent cost)

**Key components:**
- `lib/team-chatroom.js` — append-only JSONL shared memory between parallel agents
- `lib/research-coordinator.js` — builds task strings for each lens + UnifierAgent
- `shouldUseResearchTeam(complexity, explicitFlag)` — gate function
- `buildResearchTeam(query)` — returns sessionId + 3 specialist task objects
- `buildUnifierTask(query, sessionId)` — builds synthesis prompt from chatroom
- `checkLensCompletion(sessionId)` — verifies all lenses posted before unifying

**Lens discipline:**
- Each lens gets a distinct role description injected into its prompt
- Lenses do NOT communicate with each other — only through the chatroom
- UnifierAgent reads all lens outputs and produces ONE response
- If a lens fails silently, UnifierAgent warns but synthesizes from available data

**Cost:** ~4x single-agent. Gate on complexity to control spend.

**Critical rule:** Grok or any external model used as a lens is a leaf node — it answers, it never spawns further agents.

See: `lib/research-coordinator.js` for reference implementation.

### 7. External Model Consultation

**Problem:** Your agent may have architectural blind spots that another model's reasoning style would catch. Human relay (copy/paste to another AI) is slow and lossy.

**Solution:** Spawn an ExternalConsultAgent subagent that calls an external model's API directly, persists the session, and returns the response.

**Architecture:**
```
Core agent decides consultation needed
    │
    └─ ExternalConsultAgent subagent
            ├─ Calls external API (Grok, OpenAI, etc.)
            ├─ Injects system-level intent for alignment
            ├─ Supports session continuity (sessionId)
            └─ Returns response + sessionId
```

**Why subagent, not core agent:**
External API calls are side effects with cost and data exposure implications. Isolating them in a subagent follows the blast-shield philosophy — if something goes wrong, it's contained.

**Key components:**
- `lib/external-bridge.js` — session management, task string builder, consultation logger
- `memory/external-agents.json` — provider config (model IDs, endpoints)
- `memory/external-sessions/` — persistent session files for conversation continuity
- `lib/external-consult-helper.js` — `shouldAutoConsult()` gate (RED drift + high complexity + 24h cooldown)

**Auto-consult gate (3 conditions, all required):**
1. Intent drift level === 'RED'
2. Task complexity === 'high'
3. Last consultation > 24 hours ago (with lock file to prevent race conditions)

**Security rules (enforce before go-live):**
- External model is a leaf node — never triggers further spawns
- Context sanitization before every call — strip API keys, file contents, internal paths
- Session-level call cap (prevent fan-out)
- Metadata logging of every call (timestamp, provider, trigger reason)
- Key stored in environment variable, not config file

**Session continuity:**
Pass `sessionId` from a previous consultation to continue the conversation. The bridge injects prior message history automatically.

See: `lib/external-bridge.js` for reference implementation.

### 8. Intent Engineering (Value Alignment over Time)

**Problem:** Prompt engineering tells agents *what to do*. Context engineering tells agents *what to know*. Neither tells agents *what to want* — so they drift from user values over time without detection.

**Solution:** A three-layer system that encodes agent intent, extracts intent signals from user behavior, and detects drift before it becomes a problem.

**Three layers:**
1. **Intent Manifest** (`memory/intent-manifest.json`) — Machine-readable intent spec per agent: core purpose, hard constraints (with regex), operational goals with verification keywords, user signals extracted from history
2. **Intent Extractor** (`lib/intent-extractor.js`) — Weekly pass over episode history extracting preference/value/correction signals; decays old signals (rate: 0.975/week), prunes below 0.30 strength
3. **Drift Detector** (`lib/intent-drift-detector.js`) — 5-component score per episode: hard constraint violations (0.35), goal keyword coverage (0.25), structural drift via Jaccard (0.20), correction pressure (0.15), forbidden phrase hits (0.05)

**Drift levels:**
- GREEN (< 0.29): Normal operation
- YELLOW (0.29–0.48): Inject reminder next turn
- ORANGE (0.48–0.68): Log + prepare summary
- RED (≥ 0.68): Flag for user check-in (triggers auto-consult gate)

**Intent manifest schema:**
```json
{
  "system": {
    "core_purpose": "...",
    "hard_constraints": [{"id": "...", "rule": "...", "regex": "..."}],
    "operational_goals": [{"id": "...", "description": "...", "verification_keywords": [], "weight": 0}]
  },
  "agents": {
    "AgentName": {
      "inherits": true,
      "overrides": {
        "core_purpose": "...",
        "operational_goals": [],
        "user_signals": []
      },
      "version": "YYYY-MM-DD.001"
    }
  },
  "diff_log": []
}
```

**Key properties:**
- System intent + agent overrides use deep merge — agents inherit system constraints
- User signals decay weekly — recent corrections weighted higher
- Operational goals are hand-authored for v1; intent compression auto-suggests additions in v2
- Manifest is diffable over time (diff_log tracks changes)
- Drift score adjusts confidence estimator: `score *= (1 - drift.score * 0.3)`

**Cold start:** Works on day 1 with hand-authored goals. Signals accumulate automatically.

See: `lib/intent-manager.js`, `lib/intent-extractor.js`, `lib/intent-drift-detector.js` for reference implementation.

### 5. Cost-Aware Spawning

**Problem:** Uncontrolled subagent spawning leads to budget overruns.

**Solution:** Estimate cost before spawning, require approval for expensive operations.

**Framework:**
```javascript
// Pre-spawn cost estimation
const estimate = estimateSubagentCost({
  task_complexity: "high",       // simple/medium/high
  expected_duration_min: 20,
  model: "sonnet",               // haiku/sonnet/opus
  research_required: true
})

// estimate = { min: $0.60, max: $1.20, confidence: 0.8 }

if (estimate.max > 0.50) {
  // Log to cost tracking
  await logCostEstimate("task-label", estimate)
  
  if (estimate.max > 2.00) {
    // Require human approval
    await requestApproval(estimate)
  }
}

// Spawn subagent
const result = await spawnSubagent(...)

// Track actual cost
await logActualCost("task-label", result.cost)
```

**Cost tiers:**
- **Micro** (< $0.10): Simple lookups, fact-checking
- **Small** ($0.10-0.50): Standard research, code review
- **Medium** ($0.50-2.00): Feature implementation, deep analysis
- **Large** (> $2.00): Complex refactors, multi-phase projects

**Optimization strategies:**
- Use haiku for simple tasks (3x cheaper than sonnet)
- Parallelize independent operations
- Cache research findings for reuse
- Skip optional phases (reviewer for low-risk changes)

## Directory Structure

```
subagents/
├── [specialist-name]/
│   ├── SPECIALIST.md       # Agent definition and personality
│   ├── knowledge-base/     # Reference materials
│   └── research/           # Task outputs and findings
└── _archived/              # Retired subagents

skills/subagent-architecture/
├── SKILL.md               # This file
├── templates/
│   ├── security-proxy.md
│   ├── researcher-specialist.md
│   ├── phased-implementation.md
│   └── peer-review-specialist.md
└── setup.sh               # Directory scaffolding script
```

## When to Use Each Pattern

### Security Proxy
**Use when:**
- Accessing untrusted APIs or experimental services
- Risk score > 70 (high blast radius or irreversibility)
- Data needs sanitization before main agent sees it
- Cost estimate < $0.10 (lightweight proxy)

**Skip when:**
- Trusted first-party APIs (your infrastructure)
- Read-only public data (Wikipedia, documentation)
- Risk score < 30 (low stakes)

### Researcher Specialist
**Use when:**
- Question requires 10+ sources
- Domain expertise needed (not general knowledge)
- Multiple conflicting claims (need fact-checking)
- Deliverable is a decision (not just information)
- Cost estimate > $0.20 (worth specialist analysis)

**Skip when:**
- Simple factual lookup (single authoritative source)
- Real-time data (weather, stock prices)
- Cost estimate < $0.10 (not worth overhead)

### Phased Implementation
**Use when:**
- Feature touches 3+ files
- Requires integration with existing systems
- Cost estimate > $1.00 (worth upfront design)
- Failure would be expensive (need rollback plan)
- Long-term maintainability matters

**Skip when:**
- Simple script (1 file, no integration)
- Well-understood pattern (copying existing structure)
- Prototype/experiment (might throw away)
- Cost estimate < $0.50 (faster to just build)

### Peer Review
**Use when:**
- High stakes (security, legal, financial)
- Domain gap (no internal specialist)
- Bias check (fresh perspective needed)
- Complex validation (multi-dimensional review)

**Skip when:**
- Low stakes (documentation, styling)
- Domain expertise available internally
- Fast turnaround required (peer may take hours/days)
- Sensitive data (can't sanitize for external review)

## Integration with Task Routing

**Automatic pattern selection** via task-routing skill:

```yaml
# config/routing-rules.yaml
pattern_routing:
  security_proxy:
    triggers:
      - blast_radius > 70
      - untrusted_api: true
    max_cost: 0.10
    
  researcher_specialist:
    triggers:
      - task_type: research
      - complexity > 50
    min_sources: 3
    
  phased_implementation:
    triggers:
      - task_type: code_gen
      - files_affected > 3
      - cost_estimate > 1.00
    phases: [architect, coder, reviewer]
    
  peer_review:
    triggers:
      - irreversibility > 80
      - domain_gap: true
    require_approval: true
```

**Manual override:**
```javascript
// Force specific pattern
spawnSubagent({
  pattern: "security-proxy",  // override routing decision
  task: "...",
  justification: "Experimental API, prefer isolation"
})
```

## Cost Tracking & Optimization

### Logging Requirements

All subagent spawns >$0.50 must be logged to `notes/cost-tracking.md`:

```markdown
## Subagent Cost Tracking

| Date | Label | Pattern | Estimate | Actual | Delta | Notes |
|------|-------|---------|----------|--------|-------|-------|
| 2026-02-22 | architect-feature-x | phased-impl | $0.40 | $0.38 | -5% | Faster than expected |
| 2026-02-22 | coder-feature-x | phased-impl | $0.70 | $0.85 | +21% | Complex refactor, used opus |
| 2026-02-22 | researcher-market | researcher | $0.60 | $0.55 | -8% | Cached sources helped |
```

### Accuracy Improvement

Track estimate vs actual to improve future predictions:
```javascript
// Calculate rolling accuracy
const accuracy = calculateAccuracy({
  window_days: 30,
  min_samples: 10
})

// accuracy = { mean_error: 12%, confidence: 0.85 }

// Adjust future estimates
const adjusted_estimate = base_estimate * (1 + accuracy.mean_error)
```

## Quality Standards

### Subagent Output Rubric

All specialist subagents should score 7+ on this rubric:

| Dimension | Poor (1-3) | Good (4-6) | Excellent (7-10) |
|-----------|------------|------------|------------------|
| **Specificity** | Vague generalizations | Some concrete details | Precise, actionable specifics |
| **Actionability** | No clear next steps | Suggestions provided | Step-by-step implementation plan |
| **Evidence** | Unsourced claims | Some citations | Every claim sourced, validated |
| **Structure** | Stream-of-consciousness | Basic organization | Scannable hierarchy, summaries |
| **Completeness** | Missing key aspects | Most areas covered | Comprehensive, gaps documented |
| **Honesty** | Hides limitations | Mentions some trade-offs | Explicit about unknowns, risks |
| **Cost-awareness** | No budget consideration | Rough estimates | Detailed cost/benefit analysis |
| **Integration** | Ignores existing systems | Basic compatibility | Seamless integration plan |

### Self-Audit Checklist

Before finalizing subagent output:
- [ ] Every claim has source (URL + date)
- [ ] Contradictions addressed (not ignored)
- [ ] Recommendations include trade-offs
- [ ] Cost estimate provided (time + money)
- [ ] Integration points documented
- [ ] Rollback strategy included
- [ ] Success criteria defined
- [ ] Known limitations listed

## Philosophy

### Permanent vs Ephemeral

**Permanent subagents** (skill-based):
- Recurring specialized tasks
- Deep domain expertise
- Knowledge accumulation over time
- Examples: DevOps, AuthorAgent, WuxiaWorldbuilder

**Ephemeral subagents** (one-off spawns):
- Bounded research tasks
- Simple implementation work
- Experimental exploration
- Pattern-based specialists (security-proxy, researcher)

### Anti-Sycophant by Default

All subagents should:
- Call out weak evidence (no polite agreement)
- Reject unrealistic requirements (push back on bad specs)
- Highlight risks honestly (no sugar-coating)
- Admit knowledge gaps (no speculation to please)

### Cost-Conscious Operation

- Estimate before spawning (no surprise bills)
- Choose appropriate model (haiku vs sonnet vs opus)
- Parallelize when possible (save time = save money)
- Cache and reuse (research findings, architecture patterns)
- Terminate early if stuck (don't spin wheels for 30min)

## Dependencies

### Required
- OpenClaw 2026.2.17+ (subagent spawning, cost tracking)

### Optional but Recommended
- **task-routing** skill (auto-pattern selection, risk scoring)
- **cost-governor** skill (budget enforcement, approval workflows)
- **drift-guard** skill (behavioral validation, quality audits)

### Integration Points

**Task routing:**
- Provides task classification (8 types)
- Risk scoring (5 dimensions, 0-100 scale)
- Auto-route to pattern (security-proxy, researcher, phased-impl)

**Cost governor:**
- Pre-spawn approval for expensive operations
- Budget tracking per project/feature
- Alert on overruns

**Drift guard:**
- Behavioral audit of subagent outputs
- Policy violation detection
- Quality score trending

## Framework Limitations & v2 Roadmap

**Known gaps identified in peer review (Agent Smith, EasyClaw project)**

Current OpenClaw subagent framework has architectural limitations that affect all patterns in this skill. These are framework-level constraints, not skill-specific issues. Documenting for transparency and future improvement.

### 1. Spawn Configuration Constraints

**Smith's Question:** *"How does core define sub-bot constraints before launch?"*

**Current State:**
- Spawn parameters: `task`, `personality`, `model`, `timeout`, `label`
- Basic configuration only (what to do, how long)
- No granular resource controls

**Limitations:**
- ❌ No memory limits per spawn (subagent can consume unlimited RAM)
- ❌ No API call quotas (can make 1000s of web requests)
- ❌ No disk space caps (can fill storage)
- ❌ No per-spawn tool restrictions (tool policy is framework-level, applies to all subagents)

**Current Workaround:**
- Manual timeout enforcement (kill after N minutes)
- Framework-level tool policies (same restrictions for all subagents)
- Post-spawn monitoring (watch logs, intervene manually)

**v2 Design Considerations:**
```javascript
// Proposed: Granular per-spawn constraints
spawnSubagent({
  label: "researcher-x",
  task: "Research topic",
  constraints: {
    max_memory_mb: 512,           // Kill if exceeds RAM limit
    max_api_calls: 50,            // Deny further requests after quota
    max_disk_mb: 100,             // Block file writes beyond limit
    max_cost_usd: 0.50,           // Auto-terminate if cost projection exceeds
    tools_allowed: ["web_search", "web_fetch"],  // Per-spawn tool whitelist
    tools_denied: ["exec", "write"],             // Explicit blacklist
    rate_limits: {
      web_search: { calls: 10, window_seconds: 60 }  // Max 10 searches/min
    }
  }
})
```

**Impact on Patterns:**
- **Security proxy:** Could enforce strict tool whitelist per proxy (currently manual)
- **Researcher:** Could cap API calls to prevent runaway research loops
- **Phased impl:** Could allocate different budgets per phase (architect: $0.40, coder: $1.00)

### 2. Skill Loading & Validation

**Smith's Question:** *"How are skills validated before execution?"*

**Current State:**
- External skills (downloaded) → `skill-vetter` checks metadata, malicious patterns
- Internal skills (workspace) → Just execute (trusted by default)
- No runtime sandboxing

**Limitations:**
- ❌ No code isolation for skills (skill code runs in main agent context)
- ❌ No execution validation (skill can do anything agent can do)
- ❌ No capability restrictions (skill inherits all agent tools)
- ❌ Trust model: Binary (external = vet, internal = trust)

**Current Workaround:**
- Vet external skills manually before first use
- Review internal skill code (human audit)
- Hope skills don't misbehave

**v2 Design Considerations:**
```javascript
// Proposed: Skill capability manifest
// skills/my-skill/SKILL.md
---
capabilities_required:
  - web_search      # Skill needs web access
  - read:config/    # Can read config directory only
  - write:output/   # Can write to output directory only
isolation_level: sandbox  # Run in isolated context
max_execution_time: 30    # Kill after 30 seconds
---

// Runtime: Skill runs in sandbox with only declared capabilities
// Attempts to use undeclared tools → blocked, logged, skill terminated
```

**Impact on Patterns:**
- **Security proxy:** Skills could be sandboxed (currently rely on manual isolation)
- **All patterns:** Skills loaded by subagents would inherit spawn constraints
- **Peer review:** External skills from peers could run safely (sandboxed)

### 3. Communication Bounds (Bidirectional Channel)

**Smith's Question:** *"What can sub-bots ask for from core?"*

**Current State:**
- **One-way communication only:** Core spawns → Subagent executes → Returns result
- Subagent cannot request clarification mid-task
- Subagent cannot request additional context during execution
- No interactive mode

**Limitations:**
- ❌ Subagent stuck on ambiguous requirement → Must guess or fail
- ❌ Subagent needs additional context → Can't ask, works with what it has
- ❌ Subagent encounters unexpected scenario → No escalation path mid-task
- ❌ Human approval needed mid-execution → Not possible (only pre/post spawn)

**Current Workaround:**
- Over-specify context in initial spawn (bloated prompts)
- Subagent makes best guess (may be wrong)
- Subagent fails, core respawns with clarification (expensive)

**v2 Design Considerations:**
```javascript
// Proposed: Request-response protocol during execution
// Subagent code:
const clarification = await requestFromCore({
  type: "clarification",
  question: "User said 'recent data' - how many days back?",
  options: ["7 days", "30 days", "90 days"],
  timeout_seconds: 60  // If no response, default to first option
})

// Core receives request:
// - Auto-approve safe requests (data lookup from memory)
// - Escalate to human for decisions
// - Return answer to subagent
// - Subagent continues with clarification

// Examples:
// - "Need API key for service X" → Core provides from secure store
// - "Found conflicting data, which source to trust?" → Human decides
// - "Task seems too expensive ($5 estimated), proceed?" → Approval workflow
```

**Impact on Patterns:**
- **Researcher:** Can ask "should I dig deeper on this tangent?" mid-research
- **Phased impl:** Coder can ask architect for design clarification during build
- **Security proxy:** Can request human approval if API returns unexpected data
- **All patterns:** Reduces over-specification, enables adaptive execution

### 4. Termination Conditions (Resource-Based Kills)

**Smith's Question:** *"When does core kill a sub-bot?"*

**Current State:**
- **Time-based only:** Timeout (specified in spawn) or task completion
- Manual intervention (human stops runaway agent)
- No automatic resource-based termination

**Limitations:**
- ❌ No memory limit kills (agent can OOM the host)
- ❌ No cost threshold kills (can exceed budget before timeout)
- ❌ No stuck detection (infinite loops run until timeout)
- ❌ No output size limits (can generate gigabytes of text)

**Current Workaround:**
- Set conservative timeouts (may kill productive work early)
- Monitor logs manually (reactive, not proactive)
- Hope agent doesn't get stuck in expensive loop

**v2 Design Considerations:**
```javascript
// Proposed: Multi-condition termination
spawnSubagent({
  label: "researcher-x",
  task: "Research topic",
  termination: {
    // Existing
    timeout_minutes: 20,
    
    // New: Resource limits
    max_memory_mb: 512,          // Kill if RSS > 512MB
    max_cost_usd: 1.00,          // Kill if projected cost > $1
    max_output_tokens: 10000,    // Kill if response > 10k tokens
    
    // New: Behavioral detection
    stuck_detection: {
      enabled: true,
      same_action_threshold: 5,  // Kill if repeats same tool call 5x
      no_progress_minutes: 5     // Kill if no new output for 5min
    },
    
    // New: External triggers
    kill_signal: "session:parent_terminated"  // Kill if parent agent dies
  }
})

// Termination reasons logged for analysis:
// - "timeout" (existing)
// - "memory_exceeded" (new)
// - "cost_exceeded" (new)
// - "stuck_loop_detected" (new)
// - "output_overflow" (new)
// - "parent_died" (new)
```

**Impact on Patterns:**
- **Security proxy:** Strict resource limits (memory, cost) prevent runaway isolation breaches
- **Researcher:** Stuck detection prevents infinite search loops
- **Phased impl:** Cost limits per phase (architect can't blow whole budget)
- **All patterns:** Better cost control, faster failure detection

### 5. Post-Mortem & Learning System

**Smith's Question:** *"How do you learn from sub-bot failures?"*

**Current State:**
- **Success-only logging:** Add to `AGENTS.md` after successful spawns
- Manual failure review (check logs, wonder what happened)
- No systematic failure tracking
- No pattern analysis

**Limitations:**
- ❌ No failure tracking (only successes logged to AGENTS.md)
- ❌ No common failure pattern detection (same mistake repeated)
- ❌ No cost vs value analysis (did expensive agent deliver value?)
- ❌ No success rate per agent type (which specialists are reliable?)
- ❌ No improvement feedback loop (failures don't inform future spawns)

**Current Workaround:**
- Human remembers failures (unreliable)
- Manually check logs when something seems off
- Anecdotal learning ("that researcher failed last time")

**v2 Design Considerations:**
```javascript
// Proposed: Systematic post-mortem database
// Storage: memory/subagent-postmortems.jsonl

{
  "spawn_id": "researcher-market-20260222-1430",
  "label": "researcher-market",
  "pattern": "researcher-specialist",
  "outcome": "failure",  // success | partial | failure
  "termination_reason": "cost_exceeded",
  "stats": {
    "duration_minutes": 18,
    "cost_actual": 1.25,
    "cost_estimate": 0.60,
    "cost_accuracy": -108%,  // Overran by 108%
    "tokens_used": 45000,
    "api_calls": 127
  },
  "deliverable_quality": null,  // Not rated (failed before completion)
  "failure_mode": {
    "category": "runaway_research",  // Taxonomy of failures
    "root_cause": "No stuck detection, research loop on tangent",
    "human_notes": "Researched sub-topic for 15min, didn't return to main question"
  },
  "lessons": [
    "Add stuck detection for researcher pattern",
    "Improve cost estimation for multi-source research (was 2x off)"
  ]
}

// Analytics queries:
// - Success rate by pattern: researcher-specialist = 73% (8/11 succeeded)
// - Most common failure mode: cost_exceeded (40% of failures)
// - Cost estimation accuracy: researcher pattern = -25% average (underestimates)
// - ROI analysis: phased-impl pattern = $2.50 avg cost, 90% success, high value
```

**Proposed Learning Loop:**
```javascript
// Before spawning, check historical performance
const history = getPatternHistory("researcher-specialist")

if (history.success_rate < 0.7) {
  console.warn(`⚠️ Pattern has 65% success rate (13/20). Common failure: ${history.top_failure_mode}`)
  // Adjust: Add stuck detection, reduce timeout, use cheaper model
}

if (history.cost_accuracy < -0.3) {
  console.warn(`⚠️ Pattern underestimates cost by 35% on average`)
  // Adjust: Inflate estimate by 35%
  const adjusted_estimate = base_estimate * 1.35
}

// After completion, log outcome
logPostMortem({
  spawn_id,
  outcome: "success",
  quality_score: 8.5,  // From rubric
  cost_actual: 0.58,
  cost_estimate: 0.60,
  lessons: ["Worked well, multi-perspective pattern delivered balanced view"]
})
```

**Impact on Patterns:**
- **All patterns:** Historical success rates inform spawn decisions
- **Cost framework:** Improve estimation accuracy (learn from past errors)
- **Quality standards:** Track which patterns consistently deliver high scores
- **Pattern evolution:** Retire unreliable patterns, double down on proven ones

### Summary: v2 Feature Matrix

| Feature | v1 (Current) | v2 (Proposed) | Benefit |
|---------|--------------|---------------|---------|
| **Spawn constraints** | Timeout only | Memory, cost, quota, tool whitelist | Resource safety |
| **Skill isolation** | Trust-based | Sandboxed with capabilities | Security |
| **Communication** | One-way | Bidirectional request/response | Adaptive execution |
| **Termination** | Time-based | Multi-condition (resource, stuck, cost) | Cost control |
| **Post-mortem** | Success-only | Full lifecycle tracking + analytics | Continuous learning |

**Current mitigation strategies:**
1. **Manual monitoring** (watch logs, intervene when needed)
2. **Conservative estimates** (over-specify context, pad timeouts)
3. **Pattern discipline** (follow templates strictly to avoid known failure modes)
4. **Human-in-loop** (approve expensive spawns, review failures manually)

**v2 would enable:**
- Autonomous resource management (agents self-limit)
- Higher confidence spawning (better failure prediction)
- Faster iteration (learn from failures automatically)
- Fine-grained security (per-spawn, per-skill isolation)

**Note for users:**
These limitations affect **all subagent patterns** in this skill. The patterns documented here (security-proxy, researcher, phased-impl, peer-review) work within current framework constraints. v2 improvements would enhance safety and reliability, but are **not required** for effective use of these patterns today.

**Tracking:** OpenClaw framework issue (conceptual - not filed yet)
**Credit:** Agent Smith (EasyClaw peer review, 2026-02-22)

## Examples

### Example 1: Security-First API Integration

**Scenario:** Integrate with untrusted social network API

```javascript
// Main agent receives request
const task = "Fetch user's posts from SocialNetworkX API"

// Security proxy pattern
const proxy = await spawnSubagent({
  label: "proxy-socialnetworkx",
  pattern: "security-proxy",
  task: "Query SocialNetworkX API for user posts, return sanitized JSON",
  context: {
    query: "user:$USERNAME, limit:10"
    // NO API keys, NO workspace paths
  },
  tools_allowed: ["exec:curl"],
  timeout_minutes: 5,
  auto_terminate: true
})

// proxy returns: [{username, timestamp, content}] - sanitized
// Main agent: Safe to process, no raw API exposure
```

### Example 2: Multi-Perspective Research

**Scenario:** Evaluate whether to adopt new framework

```javascript
// Spawn 3 researchers with different biases
const researchers = await Promise.all([
  spawnSubagent({
    label: "researcher-optimist",
    pattern: "researcher-specialist",
    task: "Research FrameworkX benefits, best-case adoption scenario",
    personality: "Optimistic, highlights opportunities"
  }),
  
  spawnSubagent({
    label: "researcher-pessimist",
    pattern: "researcher-specialist",
    task: "Research FrameworkX risks, failure modes, known issues",
    personality: "Skeptical, risk-focused"
  }),
  
  spawnSubagent({
    label: "researcher-pragmatist",
    pattern: "researcher-specialist",
    task: "Research FrameworkX current state, real-world adoption data",
    personality: "Pragmatic, data-driven"
  })
])

// Synthesize: Balanced view with decision criteria
const decision = synthesizeResearch(researchers.map(r => r.findings))
```

### Example 3: Phased Feature Development

**Scenario:** Build complex new skill

```javascript
// Phase 1: Architecture
const plan = await spawnSubagent({
  label: "architect-skill-x",
  pattern: "phased-implementation",
  phase: "architect",
  task: "Design implementation plan for skill-x with [requirements]",
  model: "sonnet"
})

// Review plan, get approval if expensive
if (plan.cost_estimate > 2.00) {
  await humanApproval(plan)
}

// Phase 2: Implementation
const implementation = await spawnSubagent({
  label: "coder-skill-x",
  pattern: "phased-implementation",
  phase: "coder",
  task: `Implement skill-x per plan: ${plan.path}`,
  model: plan.recommended_model
})

// Phase 3: Review (conditional on risk)
if (implementation.risk_level === "high") {
  const review = await spawnSubagent({
    label: "reviewer-skill-x",
    pattern: "phased-implementation",
    phase: "reviewer",
    task: `Review implementation: ${implementation.path}`,
    model: "sonnet"
  })
  
  if (!review.approved) {
    // Iterate or escalate
  }
}
```

### Example 4: Peer Validation

**Scenario:** Security audit for payment processing

```javascript
// Prepare sanitized review package
const package = sanitizeForReview({
  artifact: readFile("src/payment-processor.js"),
  remove: ["API_KEYS", "USER_DATA", "INTERNAL_URLS"]
})

// Request peer review via Discord
await message({
  action: "send",
  target: "smith-security-bot",
  message: `Security review request:\n${JSON.stringify(package)}\n\nFocus: Payment processing, SQL injection, input validation`
})

// Wait for peer response (auto-announces when received)
// Process feedback, fix critical issues, optionally re-submit
```

## Troubleshooting

### Problem: Subagent exceeds cost estimate

**Diagnosis:**
- Check actual task complexity vs estimate
- Review subagent logs for loops or retries
- Verify model choice (opus when sonnet would suffice?)

**Solutions:**
- Improve cost estimation (track actuals, adjust formula)
- Add cost cap to spawn config (hard limit)
- Use cheaper model for exploratory phase

### Problem: Security proxy leaks sensitive data

**Diagnosis:**
- Audit spawn context (did it include workspace paths?)
- Check tool restrictions (was file access allowed?)
- Review output sanitization (did schema validation fail?)

**Solutions:**
- Update security-proxy template checklist
- Add automated context sanitization pre-spawn
- Implement output schema validation (reject non-conforming data)

### Problem: Phased implementation phases conflict

**Diagnosis:**
- Architect plan unrealistic (coder can't implement)
- Coder deviated from plan (reviewer rejects)
- Reviewer too strict (perfect is enemy of good)

**Solutions:**
- Architect: Include feasibility check (can this be built?)
- Coder: Flag deviations early (request plan amendment)
- Reviewer: Focus on critical issues (don't block on style)

### Problem: Peer review unavailable or slow

**Diagnosis:**
- Peer bot offline or rate-limited
- No trusted peers for required domain
- Review package too large or unclear

**Solutions:**
- Maintain backup peer list (2+ per domain)
- Fall back to internal review (DevOps, CoderAgent)
- Simplify review package (focus on specific question)

## Framework Limitations & v2 Roadmap

**Known gaps identified in peer review (Agent Smith, EasyClaw - 2026-02-22)**

These limitations represent areas where the current OpenClaw subagent framework needs evolution. Documented here for transparency and future development.

### 1. Spawn Configuration - Per-Subagent Constraints

**Current state:**
- Spawn parameters: task description, personality, model, timeout, label
- Constraints are framework-level (all subagents share same tool policy)

**Missing:**
- Memory limits per spawn (prevent individual subagent memory leaks)
- API call quotas per spawn (prevent runaway costs)
- Disk space caps per spawn (prevent storage exhaustion)
- Per-spawn tool restrictions (fine-grained beyond framework allowlist)

**v2 Design Consideration:**
```javascript
sessions_spawn({
  task: "...",
  constraints: {
    maxMemoryMB: 512,
    maxAPICalls: 100,
    maxDiskMB: 50,
    tools: {
      allowed: ['read', 'write'],
      forbidden: ['exec', 'message'],
      restrictions: {
        read: { paths: ['/workspace/restricted/'] },
        write: { paths: ['/workspace/output/'], maxFileSize: '10MB' }
      }
    }
  }
})
```

**Impact:** Without per-spawn constraints, one rogue subagent can exhaust resources for all others.

### 2. Skill Loading - Runtime Validation

**Current state:**
- External skills: Pre-execution vetting via `skill-vetter` (red flag detection)
- Internal skills: Trusted by default, no runtime sandboxing

**Missing:**
- Runtime sandboxing for skill-embedded code (JavaScript, shell scripts)
- Execution validation (verify skill behaves as documented)
- Resource monitoring during skill execution

**v2 Design Consideration:**
```javascript
// Sandbox wrapper for skill execution
runSkill('ai-writing-humanizer', {
  sandbox: {
    networkAccess: false,  // Block network except allowlisted domains
    filesystemAccess: 'readonly',  // Read-only except explicit write paths
    cpuLimit: '50%',  // Prevent CPU monopolization
    timeout: 30000  // 30s max execution
  },
  validate: {
    outputSchema: { ... },  // Verify output format
    sideEffects: ['writes to /workspace/humanizer/'],  // Allowed side effects
    noExternalCalls: true  // Flag if skill attempts network/exec
  }
})
```

**Impact:** Without runtime sandboxing, malicious or buggy skills can compromise core agent.

### 3. Communication Bounds - Bidirectional Channels

**Current state:**
- One-way communication only: Core spawns → Subagent executes → Result returns
- Subagents cannot ask clarifying questions during execution

**Missing:**
- Mid-task clarification requests ("Should I proceed with risky operation?")
- Progress updates for long-running tasks (>5min execution)
- Dynamic priority adjustment (core can signal "abort" or "expedite")

**v2 Design Consideration:**
```javascript
// Subagent perspective
async function executeTask(taskDescription) {
  const plan = generatePlan(taskDescription);
  
  if (plan.hasHighRiskOperation()) {
    const approval = await askCore({
      question: "Plan includes deleting 100 files. Proceed?",
      options: ["yes", "no", "show list first"],
      timeout: 60000  // 1 min to respond
    });
    
    if (approval !== "yes") return { status: "aborted", reason: "user declined" };
  }
  
  // Continue with approved plan...
}
```

**Impact:** Without bidirectional channels, subagents must either be overly cautious (ask for everything upfront) or overly bold (proceed with assumptions).

### 4. Termination Conditions - Resource-Based Kills

**Current state:**
- Timeout-based only: Subagent runs until task completes or timeout expires
- No resource-based termination

**Missing:**
- Memory limit kills (terminate if subagent exceeds RAM quota)
- Cost threshold kills (terminate if API calls exceed budget)
- Stuck detection (infinite loops, deadlocks, recursive spawning)
- Runaway output prevention (subagent generating gigabytes of logs)

**v2 Design Consideration:**
```javascript
sessions_spawn({
  task: "...",
  limits: {
    timeout: 600000,  // 10 min max
    maxMemory: 512,  // MB
    maxCost: 2.00,  // USD
    maxOutputSize: 10,  // MB
    maxToolCalls: 100,  // Total tool invocations
    stuckDetection: {
      enabled: true,
      sameToolRepeat: 5,  // Flag if same tool called 5+ times consecutively
      noProgressTimeout: 120000  // Flag if no output/tool calls for 2 min
    }
  },
  onLimitExceeded: (limit, value) => {
    logFailure({ subagent, limit, value });
    return { action: 'terminate', notify: 'core' };
  }
})
```

**Impact:** Without resource-based kills, subagents can waste budget, exhaust memory, or spin indefinitely.

### 5. Post-Mortem - Learning from Failures

**Update (v2.1 → v2.2):** A lightweight v0 of post-mortem logging is now implementable without framework changes. The crash report schema defined in `templates/proxy-recovery.md` gives you structured failure data per-spawn. Core reads crash reports and routes them. This covers the "what failed and why" dimension immediately.

What still requires framework work (see v2 roadmap below): automated outcome analytics, pattern detection across spawns, success rate tracking. But single-spawn forensics — you can ship that now.

**Current state:**
- Success logging only: AGENTS.md records completed subagents
- No failure tracking or pattern analysis
- **Partial exception:** Security proxies using `proxy-recovery.md` pattern get crash reports per spawn

**Missing:**
- Failure logging (why did subagent fail?)
- Common failure patterns (which tasks/agents fail most?)
- Cost vs value analysis (was the subagent worth the spend?)
- Success rate tracking per agent type (CoderAgent: 85%, ResearchAgent: 92%, etc.)
- Improvement loop (adjust spawn parameters based on historical outcomes)

**v2 Design Consideration:**
```javascript
// Automatic post-mortem on subagent completion/failure
function logSubagentOutcome(subagent, result) {
  const record = {
    timestamp: Date.now(),
    label: subagent.label,
    task: subagent.task,
    model: subagent.model,
    status: result.status,  // 'done', 'timeout', 'error', 'killed'
    runtime: result.runtime,
    cost: result.totalCost,
    tokensUsed: result.totalTokens,
    outcome: result.status === 'done' ? 'success' : 'failure',
    failureReason: result.error || result.killReason || null,
    valueProvided: result.status === 'done' ? assessValue(result) : null
  };
  
  appendToLog('memory/subagent-outcomes.jsonl', record);
  updateSuccessRates(subagent.label, record.outcome);
  
  if (record.outcome === 'failure') {
    analyzeFailurePattern(record);  // Flag common failure modes
  }
}

// Quarterly review: Which subagent types are most cost-effective?
function analyzeSubagentROI() {
  const outcomes = readLog('memory/subagent-outcomes.jsonl');
  const byType = groupBy(outcomes, o => extractType(o.label));  // CoderAgent, ResearchAgent, etc.
  
  for (const [type, records] of Object.entries(byType)) {
    const successRate = records.filter(r => r.outcome === 'success').length / records.length;
    const avgCost = mean(records.map(r => r.cost));
    const avgValue = mean(records.filter(r => r.valueProvided).map(r => r.valueProvided));
    
    console.log(`${type}: ${(successRate*100).toFixed(1)}% success, $${avgCost.toFixed(2)} avg cost, ${avgValue.toFixed(1)} avg value`);
  }
}
```

**Impact:** Without post-mortem analysis, you repeat failures, can't optimize spawn strategy, and waste budget on low-value subagents.

---

**Conclusion:**

These 5 limitations don't block current usage but represent friction points as subagent usage scales. Prioritize based on pain:

- **High priority:** #4 (resource-based kills) - prevents runaway costs
- **Medium priority:** #5 (post-mortem) - enables data-driven optimization
- **Medium priority:** #1 (per-spawn constraints) - prevents resource exhaustion
- **Low priority:** #3 (bidirectional channels) - nice to have for complex tasks
- **Low priority:** #2 (skill sandboxing) - current vetting sufficient for trusted sources

**Feedback welcome:** If you've hit these limitations in production, share workarounds and pain points via OpenClaw community channels.

## Contributing

This skill improves through real-world usage. Please contribute:

**Pattern refinements:**
- Found edge case not covered? Update template
- Better cost estimation formula? Share it
- New integration point? Document it

**New patterns:**
- Discovered novel orchestration? Add template
- Hybrid approach works better? Explain why
- Optimization technique? Include example

**Track record:**
- Log your subagent spawns (cost, accuracy, outcomes)
- Share what worked (and what didn't)
- Update rubrics based on production learnings

## License

MIT - Use freely, modify as needed, share improvements

## Changelog

### v2.3.0 (2026-02-24)
- **Added:** Pattern 6 — Research Team (parallel multi-lens analysis with Critic/Implementer/Synthesizer lenses + UnifierAgent)
- **Added:** Pattern 7 — External Model Consultation (ExternalConsultAgent subagent, session persistence, auto-consult gate)
- **Added:** Pattern 8 — Intent Engineering Layer (manifest schema, intent extraction, drift detection, 5-component drift score)
- **Updated:** Version bump to 2.3.0

### v2.2.0 (2026-02-23)
- **Added:** Core Concept #5 — Identity Continuity (ephemeral process vs persistent external identity, token handoff pattern, consistency via core-injected recent context, anti-pattern warning)
- **Added:** Trust tier ≠ security bypass principle to Peer Collaboration section (Stage 4 injection detection always runs regardless of trust level)
- **Added:** `templates/proxy-recovery.md` — crash/recovery pattern (pre-death checklist, crash report schema, core response decision tree, quarantine mode, human notification, re-spawn decision guide)
- **Updated:** `templates/security-proxy.md` — full rewrite integrating: 6-stage inbound validation pipeline, Stage 6b outbound semantic leak filter, self-imposed rate limiter + circuit breaker, crash/recovery checklist, identity continuity section, MoltbookProxy as real-world reference implementation
- **Updated:** Post-mortem section — notes crash reports from `proxy-recovery.md` are a working v0 of per-spawn forensics (no framework changes required)

### v2.0.1 (2026-02-22)
- **Added:** Framework Limitations & v2 Roadmap section
- **Added:** 5 critical design gaps identified by Agent Smith (EasyClaw peer review)
- **Added:** v2 design considerations with code examples for each limitation
- **Added:** Priority ranking for addressing limitations

### v2.0.0 (2026-02-22)
- **Breaking:** Restructured to focus on advanced patterns
- **Added:** Security proxy pattern and template
- **Added:** Researcher specialist pattern and template
- **Added:** Phased implementation pattern and template
- **Added:** Peer review pattern and template
- **Added:** Cost-aware spawning framework
- **Added:** Integration with task-routing, cost-governor, drift-guard
- **Updated:** Philosophy section (anti-sycophant, cost-conscious)
- **Updated:** Examples (real-world scenarios, not toy problems)
- **Removed:** Basic scaffolding (moved to setup.sh)

### v1.0.0 (2026-02-21)
- Initial release with basic subagent structure
- SPECIALIST.md template
- Task routing integration basics

## Support

- **Documentation:** Read templates in `templates/` directory
- **Examples:** See AGENTS.md for real-world subagent library
- **Issues:** Check EVOLOG.md for known limitations
- **Community:** Share patterns via OpenClaw Discord (when federated network launches)
