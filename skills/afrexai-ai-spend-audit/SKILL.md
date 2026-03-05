# AI Spend Audit

Audit your company's AI spending — find waste, measure ROI, and right-size your tool stack.

## When to Use
- Quarterly AI budget reviews
- Before renewing AI tool subscriptions
- When AI spend exceeds 3% of revenue without clear ROI
- Evaluating build vs buy decisions for AI capabilities

## The Framework

### Step 1: Inventory Every AI Line Item
Map all AI spending across these categories:

| Category | Examples | Typical Waste |
|----------|----------|---------------|
| **Foundation Models** | OpenAI, Anthropic, Google API keys | 40-60% (unused capacity, wrong model tier) |
| **SaaS with AI** | Salesforce Einstein, HubSpot AI, Notion AI | 30-50% (features enabled but unused) |
| **Custom Development** | Internal ML teams, fine-tuning, RAG pipelines | 25-45% (duplicate efforts, over-engineering) |
| **Infrastructure** | GPU instances, vector DBs, embedding compute | 35-55% (over-provisioned, always-on dev instances) |
| **Data & Training** | Labeling services, training data, synthetic data | 20-40% (one-time costs recurring unnecessarily) |

### Step 2: Score Each Tool (0-100)

**Usage Score (0-30)**
- 0: Nobody uses it
- 10: <25% of licensed users active
- 20: 25-75% active
- 30: >75% active, daily use

**ROI Score (0-40)**
- 0: No measurable business impact
- 10: Saves time but no revenue/cost link
- 20: Measurable cost reduction (<2x spend)
- 30: Clear ROI (2-5x spend)
- 40: High ROI (>5x spend)

**Replaceability Score (0-30)**
- 0: Commodity (10+ alternatives at lower cost)
- 10: Some alternatives exist
- 20: Few alternatives, moderate switching cost
- 30: Irreplaceable, deep integration

**Action Thresholds:**
- Score 0-30: **CUT** — cancel immediately
- Score 31-50: **REVIEW** — renegotiate or find alternative
- Score 51-70: **OPTIMIZE** — right-size tier/usage
- Score 71-100: **KEEP** — monitor quarterly

### Step 3: Model Cost Optimization

For every API-based AI tool, check:

1. **Model Selection**: Are you using GPT-4 where GPT-3.5 suffices? Claude Opus where Sonnet works?
   - Rule: Use the cheapest model that meets quality threshold
   - Test: Run 100 production queries through cheaper model, measure quality delta

2. **Caching**: Are you re-processing identical or similar queries?
   - Semantic cache can cut 20-40% of API calls
   - Exact-match cache catches another 5-15%

3. **Batch vs Real-time**: Which requests actually need sub-second response?
   - Batch processing is 50% cheaper on most providers
   - Queue non-urgent requests for batch windows

4. **Token Optimization**:
   - Trim system prompts (every token costs money at scale)
   - Use structured output to reduce response tokens
   - Implement max_tokens limits per use case

### Step 4: Vendor Consolidation

Map overlapping capabilities:

```
Current State → Target State
─────────────────────────────────────────
ChatGPT Teams + Claude Pro + Gemini → Pick ONE primary + ONE backup
Jasper + Copy.ai + ChatGPT for content → Single content tool
3 different vector databases → Consolidate to 1
Internal embeddings + OpenAI embeddings → Standardize on one
```

**Consolidation savings**: Typically 25-40% of total AI spend.

### Step 5: Build the Audit Report

```
AI SPEND AUDIT — [Company Name] — [Quarter/Year]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total AI Spend: $___/month ($___/year)
AI Spend as % Revenue: ___%
Industry Benchmark: 2-5% (early adopter) / 0.5-2% (mainstream)

WASTE IDENTIFIED
├── Unused licenses: $___/month
├── Over-provisioned infra: $___/month
├── Model tier downgrades: $___/month
├── Vendor consolidation: $___/month
└── TOTAL RECOVERABLE: $___/month ($___/year)

ACTIONS
┌─ CUT (Score 0-30): [list tools]
├─ REVIEW (Score 31-50): [list tools]
├─ OPTIMIZE (Score 51-70): [list tools]
└─ KEEP (Score 71-100): [list tools]

90-DAY PLAN
Week 1-2: Cancel CUT items, begin REVIEW negotiations
Week 3-4: Implement model downgrades and caching
Week 5-8: Vendor consolidation migration
Week 9-12: Measure savings, establish ongoing monitoring
```

## Company Size Benchmarks (2026)

| Company Size | Typical AI Spend | Typical Waste | Recoverable |
|-------------|-----------------|---------------|-------------|
| 10-25 employees | $2K-$8K/mo | 35-50% | $700-$4K/mo |
| 25-50 employees | $8K-$25K/mo | 30-45% | $2.4K-$11K/mo |
| 50-200 employees | $25K-$80K/mo | 25-40% | $6K-$32K/mo |
| 200-500 employees | $80K-$300K/mo | 20-35% | $16K-$105K/mo |
| 500+ employees | $300K-$1M+/mo | 15-30% | $45K-$300K/mo |

## Red Flags

- AI spend growing faster than revenue (unsustainable)
- More than 3 overlapping tools in same category
- No usage tracking on AI SaaS licenses
- GPU instances running 24/7 for dev/test workloads
- Paying for enterprise tiers with startup-level usage
- No A/B testing between model tiers
- "Innovation budget" with no success metrics

## Industry Adjustments

- **SaaS/Tech**: Higher AI spend acceptable (5-8%) if it's in the product
- **Professional Services**: Focus on billable hour impact — $1 AI spend should save $5+ in labor
- **Manufacturing**: AI spend should tie to defect reduction or throughput gains
- **Healthcare**: Compliance costs inflate spend 20-30% — factor in before judging waste
- **Financial Services**: Model risk management adds 15-25% overhead — legitimate cost
- **Ecommerce**: Measure AI spend per order — should decrease as volume scales

---

*Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI operations context packs for business teams. Run the [AI Revenue Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/) to find your biggest automation opportunities.*
