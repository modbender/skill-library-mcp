# Real-World Routing Examples

Practical examples of intelligent routing decisions for common agent tasks. Replace `{tier_model}` placeholders with actual model IDs from your `config.json`.

## Monitoring & Status Checks (SIMPLE Tier)

### Example 1: Heartbeat Checks
**Task**: "Check system status and report any anomalies"
**Classification**: SIMPLE (monitoring, status check)
**Model**: `{simple_model}`
**Reasoning**: Heartbeats are routine, low-complexity checks that don't require advanced reasoning. Use your cheapest reliable model.

**Code**:
```python
sessions_spawn(
    task="Run system heartbeat: check disk space, memory usage, and process status",
    model="{simple_model}",  # e.g., "local/ollama-qwen-1.5b" or "openai/gpt-4o-mini"
    label="heartbeat-check"
)
```

**Cost impact**: At ~500 tokens, this costs ~$0.0001 with a SIMPLE tier model vs $0.0025 with CRITICAL tier (25x savings)

---

### Example 2: GitHub Notification Check
**Task**: "Check GitHub for new notifications and summarize"
**Classification**: SIMPLE (API call, summarization)
**Model**: `{simple_model}`
**Reasoning**: Fetching and summarizing notifications is straightforward. No complex reasoning required.

**Code**:
```python
sessions_spawn(
    task="Fetch GitHub notifications via API, categorize by type (PRs, issues, comments), and summarize urgent items",
    model="{simple_model}",
    label="github-notifications"
)
```

**Frequency consideration**: If running hourly, SIMPLE tier could save $50-100/month vs MEDIUM tier

---

### Example 3: Log Monitoring
**Task**: "Parse logs and flag errors"
**Classification**: SIMPLE (pattern matching, extraction)
**Model**: `{simple_model}`
**Reasoning**: Log parsing is algorithmic, not requiring sophisticated reasoning.

**Code**:
```python
sessions_spawn(
    task="Parse application logs from /var/log/app.log, extract ERROR and CRITICAL entries, summarize patterns",
    model="{simple_model}",
    label="log-monitor"
)
```

---

## Development Tasks (MEDIUM Tier)

### Example 4: CI Lint Fix
**Task**: "Fix ESLint errors in the utils.js file"
**Classification**: MEDIUM (code fix < 50 lines)
**Model**: `{medium_model}`
**Reasoning**: Lint fixes are algorithmic and well-defined. MEDIUM tier provides good code understanding at reasonable cost.

**Code**:
```python
sessions_spawn(
    task="Fix all ESLint errors in src/utils.js: 15 errors involving arrow functions, variable declarations, and missing semicolons. Write corrected file.",
    model="{medium_model}",  # e.g., "openai/gpt-4o-mini" or "anthropic/claude-haiku"
    label="eslint-fix"
)
```

**Cost-benefit**: MEDIUM model (~$0.001 per fix) vs COMPLEX model (~$0.015 per fix) = 15x savings for routine fixes

---

### Example 5: Research Summary
**Task**: "Research latest React best practices and summarize"
**Classification**: MEDIUM (research, analysis)
**Model**: `{medium_model}`
**Reasoning**: Research requires good comprehension and synthesis. MEDIUM tier balances quality and cost.

**Code**:
```python
sessions_spawn(
    task="Research React 19 best practices, compare with React 18 patterns, and create a markdown summary document at /tmp/react-research.md",
    model="{medium_model}",
    label="react-research"
)
```

**Alternative approach**: Use SIMPLE tier to fetch docs, MEDIUM tier to analyze
```python
# Phase 1: Fetch
sessions_spawn(
    task="Fetch official React 19 documentation and save to /tmp/react19-docs.txt",
    model="{simple_model}",
    label="fetch-docs"
)
# Phase 2: Analyze (after fetch completes)
sessions_spawn(
    task="Analyze React docs at /tmp/react19-docs.txt and create summary",
    model="{medium_model}",
    label="analyze-docs"
)
```

---

### Example 6: Code Review
**Task**: "Review pull request for code quality issues"
**Classification**: MEDIUM (analysis, pattern recognition)
**Model**: `{medium_model}`
**Reasoning**: Code review requires understanding patterns but not deep architectural insight.

**Code**:
```python
sessions_spawn(
    task="Review PR #123: check for code style, obvious bugs, missing error handling. Generate review comments.",
    model="{medium_model}",
    label="pr-review"
)
```

**Escalation rule**: If PR is security-sensitive or touches critical systems, use CRITICAL tier instead

---

## Complex Development (COMPLEX Tier)

### Example 7: Feature Build
**Task**: "Build new authentication feature with JWT, middleware, and tests"
**Classification**: COMPLEX (multi-file feature build)
**Model**: `{complex_model}`
**Reasoning**: Multi-file architecture requires excellent code understanding. Don't delegate to cheaper models — the quality difference justifies cost.

**Code**:
```python
sessions_spawn(
    task="Build authentication system: JWT token generation/validation, Express middleware, user schema, unit tests. Create 5+ files with proper architecture in src/auth/",
    model="{complex_model}",  # e.g., "anthropic/claude-sonnet-4" or "openai/gpt-4o"
    label="auth-system"
)
```

**Why not MEDIUM tier**: Cheaper model + QA + revisions would cost MORE than using COMPLEX tier once

---

### Example 8: Debugging Complex Issue
**Task**: "Debug race condition in concurrent file processing"
**Classification**: COMPLEX (debugging, complex logic)
**Model**: `{complex_model}`
**Reasoning**: Debugging race conditions requires deep reasoning about concurrency and timing.

**Code**:
```python
sessions_spawn(
    task="Debug race condition: file processing workers sometimes skip files when running concurrently. Analyze code in src/workers/, identify the race, and propose fix with explanation.",
    model="{complex_model}",
    label="race-condition-debug"
)
```

**Optional: Enable thinking mode**
```python
sessions_spawn(
    task="Debug race condition in concurrent file processing...",
    model="{complex_model}",
    thinking="on",  # or thinking="budget_tokens:5000"
    label="race-condition-debug"
)
```

---

### Example 9: Architecture Design
**Task**: "Design microservices architecture for payment system"
**Classification**: COMPLEX (architecture, design)
**Model**: `{complex_model}`
**Reasoning**: Architectural decisions require careful reasoning about trade-offs, scalability, and maintainability.

**Code**:
```python
sessions_spawn(
    task="Design microservices architecture for payment processing: identify services, define APIs, plan data flow, consider failure modes. Output architecture doc to /tmp/payment-arch.md",
    model="{complex_model}",
    thinking="on",  # Thinking mode beneficial for architecture
    label="architecture-design"
)
```

---

### Example 10: Refactoring Legacy Code
**Task**: "Refactor legacy module for maintainability"
**Classification**: COMPLEX (multi-file refactoring)
**Model**: `{complex_model}`
**Reasoning**: Refactoring requires understanding code intent, patterns, and maintaining functionality.

**Code**:
```python
sessions_spawn(
    task="Refactor src/legacy/data-processor.js: split into smaller modules, add types, improve error handling, maintain backward compatibility. Write refactored code to src/processors/",
    model="{complex_model}",
    label="refactoring"
)
```

---

## Critical Operations (CRITICAL Tier)

### Example 11: Security Audit
**Task**: "Audit authentication code for security vulnerabilities"
**Classification**: CRITICAL (security-sensitive)
**Model**: `{critical_model}`
**Reasoning**: Security flaws can have severe consequences. Use best available model with thinking mode.

**Code**:
```python
sessions_spawn(
    task="Security audit of authentication system in src/auth/: check for SQL injection, JWT implementation flaws, session management issues, password handling vulnerabilities. Produce detailed security report.",
    model="{critical_model}",  # e.g., "anthropic/claude-opus-4" or "openai/o1"
    thinking="on",
    label="security-audit"
)
```

**Cost justification**: A single missed vulnerability could cost millions; $0.50 for thorough audit is trivial

---

### Example 12: Production Database Migration
**Task**: "Plan and execute production database schema migration"
**Classification**: CRITICAL (production deployment)
**Model**: `{critical_model}`
**Reasoning**: Production migrations carry high risk. Use most reliable model with careful reasoning.

**Code**:
```python
sessions_spawn(
    task="Plan zero-downtime migration for production database: add new columns to users table (email_verified, last_login), create migration script with rollback, identify risks, test strategy. Write migration plan to /tmp/migration-plan.md",
    model="{critical_model}",
    thinking="on",
    label="db-migration"
)
```

---

### Example 13: Financial Analysis
**Task**: "Analyze quarterly financial statements for investment recommendations"
**Classification**: CRITICAL (financial operations)
**Model**: `{critical_model}`
**Reasoning**: Financial decisions require careful, accurate analysis with attention to detail.

**Code**:
```python
sessions_spawn(
    task="Analyze Q3 financial statements at /tmp/q3-financials.pdf: calculate key ratios (P/E, debt-to-equity, ROE), identify trends, provide investment recommendation with risk assessment",
    model="{critical_model}",
    thinking="on",
    label="financial-analysis"
)
```

---

### Example 14: Compliance Review
**Task**: "Review code for GDPR compliance"
**Classification**: CRITICAL (compliance, legal)
**Model**: `{critical_model}`
**Reasoning**: Compliance violations have legal consequences. Requires thorough, careful analysis.

**Code**:
```python
sessions_spawn(
    task="GDPR compliance audit of user data handling in src/: check data collection consent, storage practices, deletion capabilities, data export, third-party sharing. Generate compliance report.",
    model="{critical_model}",
    thinking="on",
    label="gdpr-audit"
)
```

---

## Market & Financial Tasks (Variable Tier)

### Example 15: Market Monitoring
**Task**: "Monitor cryptocurrency markets and flag significant movements"
**Classification**: MEDIUM (data analysis, monitoring)
**Model**: `{medium_model}`
**Reasoning**: Pattern recognition in market data requires decent analysis but not frontier-model level. Volume is high (frequent checks), so cost matters.

**Code**:
```python
sessions_spawn(
    task="Monitor top 10 cryptocurrencies for >5% price movements in past hour via CoinGecko API, summarize trends and flag unusual patterns",
    model="{medium_model}",
    label="crypto-monitor"
)
```

**Frequency optimization**: Running every 15 minutes = 2,880 calls/month. MEDIUM vs COMPLEX tier saves ~$100/month

---

### Example 16: Trading Strategy Backtest
**Task**: "Backtest trading strategy on historical data"
**Classification**: COMPLEX (analysis, statistical reasoning)
**Model**: `{complex_model}`
**Reasoning**: Backtesting requires sophisticated analysis of patterns, edge cases, and statistical significance.

**Code**:
```python
sessions_spawn(
    task="Backtest momentum trading strategy on /tmp/historical-prices.csv: implement strategy logic, calculate returns, compare to buy-and-hold, assess statistical significance",
    model="{complex_model}",
    label="backtest-strategy"
)
```

---

## Cost-Saving Patterns

### Pattern 1: Two-Phase Processing
**Scenario**: Processing a large document
**Strategy**: Extract key sections with cheap model, analyze with better model

**Example: Research Paper Analysis**
```python
# Phase 1 (SIMPLE): Extract sections
sessions_spawn(
    task="Extract abstract, methodology, and conclusions from research paper at /tmp/paper.pdf. Save to /tmp/paper-sections.txt",
    model="{simple_model}",
    label="extract-sections"
)

# Wait for extraction to complete...

# Phase 2 (MEDIUM): Analyze extracted content
sessions_spawn(
    task="Analyze research findings from /tmp/paper-sections.txt, summarize methodology, evaluate conclusions, identify limitations",
    model="{medium_model}",
    label="analyze-paper"
)
```

**Savings**: Process 90% of tokens with cheap model, only 10% with more expensive model = ~80% cost reduction

---

### Pattern 2: Tiered Escalation
**Scenario**: Uncertain task complexity
**Strategy**: Start with MEDIUM tier, escalate to COMPLEX if inadequate

**Example: Bug Investigation**
```python
# First attempt: MEDIUM tier
sessions_spawn(
    task="Investigate bug #456: users report logout after 5 minutes. Check session handling in src/auth/session.js",
    model="{medium_model}",
    label="bug-investigation-1"
)

# If medium model can't solve it, escalate:
if investigation_incomplete:
    sessions_spawn(
        task="Deep investigation of session bug #456 (previous attempt with {medium_model} incomplete). Full analysis of session lifecycle, Redis interactions, timeout handling.",
        model="{complex_model}",
        label="bug-investigation-2"
    )
```

**Savings**: Only pay for COMPLEX tier when necessary (~70% of bugs solved by MEDIUM tier in practice)

---

### Pattern 3: Batch Processing
**Scenario**: Multiple similar simple tasks
**Strategy**: Group tasks together to reduce overhead

**Example: Multi-Service Health Check**
```python
# Instead of 10 separate agent spawns:
services = ["api", "database", "cache", "queue", "storage", ...]

# Batch them:
sessions_spawn(
    task=f"Check health of these services: {', '.join(services)}. For each, verify connectivity and response time. Report any issues.",
    model="{simple_model}",
    label="batch-health-check"
)
```

**Savings**: 1 agent call instead of 10 = reduced overhead and simpler orchestration

---

### Pattern 4: Coder + QA Review (Cost-Effective for Simple Code)
**Scenario**: Simple code changes that need validation
**Strategy**: Use MEDIUM tier for coding, SIMPLE tier for review

**Example: Multiple Lint Fixes**
```python
# Coder: MEDIUM tier
sessions_spawn(
    task="Fix all 23 lint errors in src/utils/ directory. Write corrected files.",
    model="{medium_model}",
    label="lint-fix-coder"
)

# Wait for coder to complete...

# QA: SIMPLE tier (cheaper model can spot obvious issues)
sessions_spawn(
    task="Review code changes in src/utils/. Check: (1) all lint errors fixed, (2) no new bugs introduced, (3) formatting consistent. Report pass/fail with details.",
    model="{simple_model}",
    label="lint-fix-qa"
)
```

**Cost check**: Only use this pattern if `(medium_cost + simple_cost) < complex_cost`
- Example: ($0.002 + $0.0003) < $0.015 ✓ Saves money
- If complex code: Coder+QA might cost more than COMPLEX tier alone ✗ Skip pattern

---

## Anti-Patterns: Common Mistakes to Avoid

### Mistake 1: Over-Engineering Simple Tasks
**Wrong**: Using CRITICAL tier for heartbeat checks

```python
# ❌ DON'T DO THIS
sessions_spawn(
    task="Check if server is responding",
    model="{critical_model}",  # $0.025 per check
    label="heartbeat"
)
```

**Right**: Use SIMPLE tier
```python
# ✅ DO THIS
sessions_spawn(
    task="Check if server is responding",
    model="{simple_model}",  # $0.0001 per check
    label="heartbeat"
)
```

**Impact**: 250x cost difference for identical output

---

### Mistake 2: Under-Engineering Critical Tasks
**Wrong**: Using SIMPLE tier for security audit

```python
# ❌ DON'T DO THIS
sessions_spawn(
    task="Security audit of authentication system",
    model="{simple_model}",  # Might miss subtle vulnerabilities
    label="security-audit"
)
```

**Right**: Use CRITICAL tier
```python
# ✅ DO THIS
sessions_spawn(
    task="Security audit of authentication system",
    model="{critical_model}",
    thinking="on",
    label="security-audit"
)
```

**Risk**: Missed vulnerabilities could cost millions; saving $0.50 is false economy

---

### Mistake 3: Ignoring Retry Costs
**Wrong**: Choosing cheapest model, requiring 3 retries

**Example calculation**:
- SIMPLE model: $0.0002 per attempt × 3 attempts = $0.0006
- MEDIUM model: $0.0015 per attempt × 1 attempt = $0.0015
- Looks like SIMPLE wins, but...
- **Hidden cost**: 3× the latency, 3× the orchestration overhead

**Right**: Consider success rate
```python
# For tasks where SIMPLE has <80% success rate, use MEDIUM
if task_requires_reasoning:
    model = "{medium_model}"  # Higher success rate = lower effective cost
else:
    model = "{simple_model}"
```

---

### Mistake 4: Not Using Thinking Mode for Complex Tasks
**Wrong**: COMPLEX tier without thinking on hard problem

```python
# ❌ SUBOPTIMAL
sessions_spawn(
    task="Design scalable architecture for real-time messaging system",
    model="{complex_model}",
    # Missing: thinking="on"
    label="architecture"
)
```

**Right**: Enable thinking for architectural decisions
```python
# ✅ BETTER
sessions_spawn(
    task="Design scalable architecture for real-time messaging system",
    model="{complex_model}",
    thinking="on",  # Worth the extra cost for quality
    label="architecture"
)
```

**Trade-off**: 2-3x cost increase, but significantly better architectural decisions

---

## Decision Flowchart

```
Receive Task
    │
    ↓
Classify Keywords
    │
    ├─→ "check/monitor/fetch" → SIMPLE
    │       └─→ Use {simple_model}
    │
    ├─→ "fix/patch/research" → MEDIUM
    │       └─→ Use {medium_model}
    │       └─→ (If code + QA needed: check cost vs COMPLEX)
    │
    ├─→ "build/debug/architect" → COMPLEX
    │       └─→ Use {complex_model}
    │       └─→ (Consider thinking="on" for hard problems)
    │
    └─→ "security/production/financial" → CRITICAL
            └─→ Use {critical_model} with thinking="on"
```

---

## Summary: Routing Heuristics

**Quick reference for common scenarios:**

| Task Type | Tier | Model | Thinking | Reasoning |
|-----------|------|-------|----------|-----------|
| Heartbeat check | SIMPLE | {simple_model} | No | Routine, high-frequency |
| Log parsing | SIMPLE | {simple_model} | No | Pattern matching |
| Lint fix | MEDIUM | {medium_model} | No | Algorithmic, well-defined |
| Code review | MEDIUM | {medium_model} | No | Pattern recognition |
| Feature build | COMPLEX | {complex_model} | Optional | Multi-file, architecture |
| Hard debugging | COMPLEX | {complex_model} | Yes | Deep reasoning needed |
| Security audit | CRITICAL | {critical_model} | Yes | High-stakes, thorough |
| Production deploy | CRITICAL | {critical_model} | Yes | Risk mitigation critical |

**Golden rules:**
1. **When uncertain**: Go one tier up — retries cost more than quality
2. **For code**: (coder + QA) only if cheaper than COMPLEX tier solo
3. **For critical tasks**: Never skimp — use best available with thinking mode
4. **For high-frequency**: Optimize cost aggressively, batch when possible

---

## Real-World Cost Examples

**Scenario: Daily agent workload**

| Task | Frequency | Tier | Cost/run | Daily Cost |
|------|-----------|------|----------|------------|
| Health checks | 48/day | SIMPLE | $0.0001 | $0.0048 |
| GitHub monitoring | 12/day | SIMPLE | $0.0002 | $0.0024 |
| Code reviews | 5/day | MEDIUM | $0.002 | $0.01 |
| Bug fixes | 2/day | MEDIUM | $0.005 | $0.01 |
| Feature work | 1/day | COMPLEX | $0.05 | $0.05 |
| Security checks | 1/week | CRITICAL | $0.50 | $0.07 |
| **TOTAL** | | | | **$0.147/day** |

**Monthly cost**: ~$4.40
**Without routing (all COMPLEX tier)**: ~$20/day = $600/month
**Savings**: 96% cost reduction with intelligent routing

**Key insight**: Most tasks (85%) are SIMPLE/MEDIUM tier. Routing these correctly drives massive savings while preserving quality where it matters.
