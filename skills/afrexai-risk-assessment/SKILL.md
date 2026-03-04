# Risk Assessment Framework

Comprehensive risk assessment for business operations, projects, and strategic decisions. Identifies, scores, and prioritizes risks with mitigation plans.

## What It Does

When triggered, the agent:
1. Identifies risks across categories (operational, financial, technical, regulatory, reputational, strategic)
2. Scores each risk using Likelihood × Impact matrix (1-5 scale, 25-point max)
3. Classifies into Critical (20-25), High (15-19), Medium (8-14), Low (1-7)
4. Generates mitigation strategies with owners, deadlines, and cost estimates
5. Produces a risk register ready for board reporting or investor updates

## Usage

Tell your agent: "Run a risk assessment on [project/business/decision]"

### Input
Provide context about what you're assessing:
- Business or project description
- Known concerns or past incidents
- Industry and regulatory environment
- Timeline and budget constraints

### Output Format

**Risk Register:**

| # | Risk | Category | L | I | Score | Priority | Mitigation | Owner | Deadline | Cost |
|---|------|----------|---|---|-------|----------|------------|-------|----------|------|

**Risk Heat Map:**
- 🔴 Critical (20-25): Immediate action required
- 🟠 High (15-19): Mitigation plan within 7 days
- 🟡 Medium (8-14): Monitor and review monthly
- 🟢 Low (1-7): Accept or monitor quarterly

**Residual Risk:** After mitigation, re-score to show risk reduction.

## Scoring Guide

**Likelihood (L):**
1. Rare (<5%) — Hasn't happened, unlikely to
2. Unlikely (5-20%) — Could happen but no history
3. Possible (20-50%) — Has happened elsewhere
4. Likely (50-80%) — Has happened before or conditions exist
5. Almost Certain (>80%) — Expected to happen

**Impact (I):**
1. Negligible — <$10K loss, no disruption
2. Minor — $10K-$50K, minor delays
3. Moderate — $50K-$250K, partial service disruption
4. Major — $250K-$1M, significant operational impact
5. Severe — >$1M, existential threat or regulatory action

## Industries Covered
- SaaS & Technology
- Financial Services
- Healthcare & Life Sciences
- Construction & Engineering
- Professional Services
- Manufacturing
- Real Estate
- Legal & Compliance

## Want More?

This skill pairs well with industry-specific AI context packs that include pre-built risk libraries, compliance checklists, and regulatory frameworks:

→ **Browse context packs**: https://afrexai-cto.github.io/context-packs/
→ **Calculate your AI ROI**: https://afrexai-cto.github.io/ai-revenue-calculator/
→ **Set up your AI agent**: https://afrexai-cto.github.io/agent-setup/
