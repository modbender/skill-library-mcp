# Framework Dimensions — Complete Scoring Rubrics

This file contains the full scoring methodology for all 8 dimensions. Read this before scoring any company.

## Table of Contents
1. [Scoring Convention](#scoring-convention)
2. [Dimension 1: Labor Automation Vulnerability](#dimension-1)
3. [Dimension 2: Revenue Model Disruption Potential](#dimension-2)
4. [Dimension 3: AI Adoption & Implementation Maturity](#dimension-3)
5. [Dimension 4: Competitive Moat Durability](#dimension-4)
6. [Dimension 5: Operational AI Leverage](#dimension-5)
7. [Dimension 6: Regulatory & Ethical AI Risk](#dimension-6)
8. [Dimension 7: Industry Transformation Velocity](#dimension-7)
9. [Dimension 8: Data & Ecosystem Strength](#dimension-8)
10. [Industry Tier Benchmarks](#industry-tiers)

---

## Scoring Convention

All dimensions scored 1–5. Default direction: **higher = greater risk/vulnerability**.

**Exceptions (higher = greater capability, positive):**
- Dimension 3: AI Adoption & Implementation Maturity ↑
- Dimension 5: Operational AI Leverage ↑
- Dimension 8: Data & Ecosystem Strength ↑

**Special direction notes:**
- Dimension 4 (Moat Durability): 1 = strongest moat, 5 = weakest moat (vulnerability direction)

---

<a id="dimension-1"></a>
## Dimension 1: Labor Automation Vulnerability (Weight: 8%)

**What it measures:** Share of the company's workforce performing tasks AI can execute at comparable quality.

**Scoring Method:**
1. Read the 10-K Human Capital and Business Description sections. Identify dominant job categories.
2. Map those categories to pre-scored academic exposure tables:
   - Eloundou et al. "GPTs are GPTs" (arXiv) — use E1 + 0.5×E2 scores
   - Felten/Raj/Seamans AIOE index
   - Pew Research / US Treasury AI exposure tables
   These datasets score 800+ occupations for AI exposure.
3. Calculate labor cost-to-revenue: (Total SGA + Cost of Revenue labor component) ÷ Total Revenue. Higher ratios amplify financial impact.
4. Weight occupation-level exposure scores by company's approximate workforce mix, adjusted by labor-cost ratio.

**Anchor Checklist:**

| Score | Description |
|-------|-------------|
| 1 | <15% workforce in AI-exposed roles; predominantly physical labor; low labor-cost-to-revenue |
| 2 | 15–30% in exposed roles; mix of physical and information work; moderate labor costs |
| 3 | 30–50% in exposed roles; significant white-collar workforce in data processing, analysis, or administration |
| 4 | 50–70% in exposed roles; predominantly knowledge workers; high labor-cost-to-revenue (>50%) |
| 5 | >70% in exposed roles; nearly entire workforce in tasks AI can replicate; very high labor-cost-to-revenue (>65%) |

**Anchor Examples:**
- Score 1: Construction firm, logistics trucking, agricultural processor. 10-K: "primarily field-based workforce." Eloundou E1+E2 < 0.15.
- Score 2: Hospital system (nurses/techs = moderate; physicians = lower). Mixed workforce. Labor cost ~40%.
- Score 3: Large bank: analysts, compliance, back-office = high exposure; branch staff = moderate. SGA ~45%.
- Score 4: Management consulting or mid-cap software company. "Our professionals provide analytical, advisory..." SGA >55%. Eloundou 0.5–0.7.
- Score 5: Pure-play BPO, legal process outsourcing, translation services. All tasks are cognitive processing. SGA >65%. Eloundou >0.7.

---

<a id="dimension-2"></a>
## Dimension 2: Revenue Model Disruption Potential (Weight: 18%)

**What it measures:** Whether AI fundamentally threatens the company's core value proposition or primarily enhances it.

**Scoring Method:**
1. Pull revenue breakdown from 10-K segment disclosures.
2. For each segment: Can an AI agent deliver equivalent value at lower cost? Does pricing depend on human scarcity, information asymmetry, or transaction friction?
3. Calculate tangible asset intensity: (Total Assets – Cash – Intangibles – Goodwill) ÷ Revenue. Asset-heavy companies resist disruption.
4. Cross-reference with earnings call commentary on AI competitive threats.

**Forward-looking adjustment:** +1 point if the primary market has significant AI-native startup funding (check Crunchbase) or if a major tech company has announced a competing AI product in the last 12 months.

**Anchor Checklist:**

| Score | Description |
|-------|-------------|
| 1 | Revenue from physical assets, regulated infrastructure, or tangible goods AI cannot replicate (utilities, energy, materials) |
| 2 | Services with significant physical, regulatory, or trust barriers; AI enhances but cannot substitute (healthcare delivery, defense) |
| 3 | Mixed model; some streams enhanced, others threatened; net impact uncertain (diversified financials, industrials) |
| 4 | Revenue from information intermediation, per-seat licensing, or fee-based services where AI offers cheaper alternatives |
| 5 | Revenue model directly replicable by AI; core value is cognitive tasks LLMs can now do (translation, coding, document review, tax prep) |

**Anchor Examples:**
- Score 1: Union Pacific (30,000 miles of track), NextEra Energy (power plants + grid). Tangible asset intensity >1.5.
- Score 2: UnitedHealth: deep regulatory + trust barriers. AI enhances claims processing but cannot replace the care network.
- Score 3: JPMorgan: trading and IB face AI pressure, but deposit franchise + regulatory moat provide insulation.
- Score 4: Intuit (TurboTax): core product automates tax prep, a task AI increasingly handles directly. Per-user pricing. Tangible asset intensity <0.2.
- Score 5: Chegg or Duolingo: entire value proposition is knowledge delivery AI can now do at near-zero marginal cost.

---

<a id="dimension-3"></a>
## Dimension 3: AI Adoption & Implementation Maturity (Weight: 10%) ↑

**What it measures:** Adaptive capacity. **Higher score = greater capability (positive).**

**Four Scoring Signals:**

**Signal A — Earnings Call Trajectory:**
Read last 4–8 quarterly transcripts. Track:
- AI mentions increasing?
- Specific use cases + quantified KPIs, or vague generalities?
- AI-specific leadership appointed?
- Analyst AI questions substantive?

**Signal B — 10-K AI Disclosure Depth:**
Search latest 10-K for AI terms in Business, MD&A, Risk Factors, Human Capital:
- AI as strategic priority with budget = strong
- AI only as risk factor = weak
- No mention = very weak

**Signal C — Patent Momentum + Quality:**
Search Google Patents for company AI patents. Track:
- Filing trend over 3 years (accelerating vs. flat)
- Average citations per AI patent
- Patent family size
Use USPTO AIPD bulk dataset for systematic analysis.
Supplement with GitHub/Hugging Face: open-source AI models or tools?

**Signal D — Observable Adoption:**
- Company careers page for AI/ML postings (volume + seniority)
- Product announcements for AI features
- Developer documentation for integration evidence

**AI-Washing Check (CRITICAL):**
If the company uses AI buzzwords extensively in earnings calls but cannot cite a single quantified KPI, production deployment, or specific AI product feature, **CAP THE SCORE AT 2** regardless of other signals. Vague statements like "we are leveraging AI across our platform" without evidence = AI-washing.

**Anchor Checklist:**

| Score | Description |
|-------|-------------|
| 1 | No meaningful AI strategy; minimal AI mentions; no AI hiring or patent activity; leadership silent or dismissive |
| 2 | Exploratory stage or AI-washing: AI mentioned but no scaled deployment, no KPIs, pilot projects only. **Cap here if AI-washing detected** |
| 3 | Active adoption; dedicated AI budget disclosed; multiple production use cases cited with some specifics; growing AI patent portfolio |
| 4 | Scaled integration; AI in core workflows; quantified impact (e.g., "AI drove 10–15% of efficiency gains"); strong patent portfolio with citations; C-suite AI leadership |
| 5 | AI-native model; AI is core product/platform; industry-leading patent portfolio; open-source AI contributions; analyst consensus: AI is central to thesis |

**Anchor Examples:**
- Score 2: CEO says "we're excited about AI" but no product, no KPI, no patent activity. = AI-washing, cap at 2.
- Score 3: CFO says "we deployed AI in contact centers, reduced handle time 18%." 5–10 AI patents in 2 years.
- Score 4: CEO: "AI will contribute 10–15% of revenue next year." Quantified EBIT impact. 20+ AI patents with growing citations. Chief AI Officer.
- Score 5: Nvidia, Palantir, or similar: AI IS the business. Hundreds of AI patents. Major open-source contributions.

---

<a id="dimension-4"></a>
## Dimension 4: Competitive Moat Durability (Weight: 16%)

**What it measures:** Whether competitive advantages strengthen or erode in an AI world. **Score 1 = strongest moat, 5 = weakest (vulnerability direction).**

**Scoring Method:**
Public data indicators:
- Net revenue retention and churn (10-K disclosures)
- Contract duration (revenue recognition notes)
- Customer concentration (risk factors)
- Switching cost depth (product docs, customer case studies)

**The Friction Test:** Is the moat built on genuine structural barriers (physical infrastructure, regulatory licenses, proprietary data flywheels, deep workflow embedding) or on monetized friction (information asymmetry, transaction complexity, human scarcity, technical lock-in)? AI eliminates friction; it does not eliminate railroads.

**Anchor Checklist:**

| Score | Description |
|-------|-------------|
| 1 | Moat strengthened by AI: proprietary data flywheel + network effects, deep workflow embedding, regulatory barriers, physical infrastructure |
| 2 | Moat largely intact: high switching costs from organizational embedding, strong brand trust, compliance-driven stickiness |
| 3 | Under moderate pressure: some differentiation eroding as AI levels the field, but significant barriers remain |
| 4 | Significantly threatened: value depends on information asymmetry, expertise scarcity, or complexity AI is commoditizing |
| 5 | Collapsing: core lock-in is friction AI directly eliminates; customers building AI alternatives at fraction of cost |

**Anchor Examples:**
- Score 1: Google Search (data flywheel + network effects), Union Pacific (physical rail), regulated utility with exclusive franchise.
- Score 2: Salesforce: deep organizational embedding, years of customer data, high switching costs.
- Score 3: Bloomberg Terminal: deep brand + data advantage, but AI copilots eroding interface lock-in.
- Score 4: IBM legacy services: lock-in based on COBOL complexity. AI modernization tools directly attack this friction.
- Score 5: Traditional translation agency or basic legal document review firm: entire moat was human scarcity.

---

<a id="dimension-5"></a>
## Dimension 5: Operational AI Leverage (Weight: 12%) ↑

**What it measures:** Whether the company can use AI to dramatically improve its own operations. **Higher score = greater capability (positive).**

**Scoring Method:**
- Assess operational complexity from 10-K Business Description: decision nodes in supply chain, data richness.
- Review earnings calls for digital twins, predictive maintenance, AI forecasting, dynamic pricing.
- Track efficiency metrics (inventory turns, defect rates, delivery times) and whether management attributes gains to AI.

**Anchor Checklist:**

| Score | Description |
|-------|-------------|
| 1 | Simple, low-complexity operations already highly optimized with minimal AI upside |
| 2 | Some processes amenable to AI (basic forecasting, inventory) but limited complexity |
| 3 | Significant operational complexity; AI can drive meaningful efficiency across multiple functions |
| 4 | Complex multi-node supply chains where AI optimization creates substantial competitive advantages |
| 5 | Massive real-time data streams where AI transforms decision-making (autonomous systems, real-time trading, dynamic pricing at scale) |

---

<a id="dimension-6"></a>
## Dimension 6: Regulatory & Ethical AI Risk (Weight: 3%)

**What it measures:** Compliance burden and legal risk from deploying AI.

**Scoring Method:**
- Review 10-K Risk Factors for AI-specific regulatory risks
- Assess geographic revenue exposure (% from EU and AI-regulated jurisdictions)
- Identify whether AI applications fall into high-risk categories (financial services, healthcare, employment, law enforcement)
- Check public news for enforcement actions

**Anchor Checklist:**

| Score | Description |
|-------|-------------|
| 1 | Minimal exposure; AI in low-risk categories; limited regulated-jurisdiction revenue |
| 2 | Some exposure; transparency requirements; moderate EU revenue |
| 3 | Meaningful burden; some high-risk AI systems; industry-specific regulations apply |
| 4 | High risk; majority of AI use in high-risk categories; substantial regulated revenue; scrutiny history |
| 5 | Extreme; AI in prohibited/near-prohibited categories; massive compliance costs; active litigation or enforcement |

---

<a id="dimension-7"></a>
## Dimension 7: Industry Transformation Velocity (Weight: 17%)

**What it measures:** Pace and magnitude of AI-driven transformation in the company's industry. Higher score = faster external change = less time to adapt.

**Score using at least three of five proxies:**

**Proxy 1 — AI Startup Funding:** Crunchbase keyword search for AI startups funded in the sector in the last 24 months. High volume = rapid disruption.

**Proxy 2 — Peer AI Mentions:** EDGAR screen: what % of peer companies mention AI substantively in latest 10-K? >60% = high velocity.

**Proxy 3 — Public Benchmark Reports:** Stanford HAI AI Index and McKinsey AI Survey sector-level adoption tables.

**Proxy 4 — Incumbent Disruption Evidence:** Have publicly traded incumbents seen >20% stock declines attributed to AI disruption in last 12 months?

**Proxy 5 — Big Tech Entry:** Have Google, Microsoft, Amazon, Apple, or Meta launched products targeting this sector?

**Anchor Checklist:**

| Score | Description |
|-------|-------------|
| 1 | Transformation in decades; physical/regulatory barriers. <2 proxies triggered. |
| 2 | Moderate pace; AI growing but constrained. 1–2 proxies triggered. |
| 3 | Active transformation; meaningful adoption. 2–3 proxies triggered. |
| 4 | Rapid; AI reshaping dynamics within 2–3 years. 3–4 proxies triggered. |
| 5 | Acute disruption; business models actively displaced. 4–5 proxies triggered. |

**Anchor Examples:**
- Score 1: Waste Management, utility holding companies. No AI startups targeting sector. No incumbents disrupted. Physical moats.
- Score 3: Banking/insurance: significant AI startup funding, 50–60% of peers mention AI, but regulatory constraints slow pace.
- Score 5: Enterprise SaaS, digital advertising, customer support outsourcing: massive AI startup funding, multiple incumbents down 20–50%, big tech building competitors, >80% peers discuss AI.

---

<a id="dimension-8"></a>
## Dimension 8: Data & Ecosystem Strength (Weight: 16%) ↑

**What it measures:** Proprietary data advantages, AI ecosystem partnerships, and talent quality. The strongest AI-era moat factor. **Higher score = greater capability (positive).**

**Three Scoring Signals:**

**Signal A — Proprietary Data Advantage:**
Review 10-K MD&A and earnings calls for data asset descriptions. Unique, large-scale, continuously refreshed data that competitors or AI models cannot replicate or synthesize? Look for "proprietary dataset," "unique data asset," "data from X million customers/transactions."

**Signal B — Ecosystem Partnerships:**
Check press releases and investor presentations for AI partnerships with platform companies (Microsoft/OpenAI, Google, Anthropic, Amazon, Nvidia). Depth matters: press-release-only vs. genuine product integration.

**Signal C — Talent Quality:**
LinkedIn public search for AI research talent. Specifically: former employees of OpenAI, Anthropic, DeepMind, Google Brain, Meta FAIR. Published research papers. Senior AI hires in last 12 months. Quality and retention, not just volume.

**Anchor Checklist:**

| Score | Description |
|-------|-------------|
| 1 | No proprietary data advantage; no meaningful AI partnerships; no notable AI talent. Pure consumer of others' AI. |
| 2 | Some useful data but not unique or large-scale; shallow partnerships; limited AI talent |
| 3 | Meaningful proprietary data in at least one domain; one or more genuine AI partnerships; growing AI talent base |
| 4 | Large-scale, unique, continuously refreshed data; deep AI platform partnerships; strong talent with publications and senior hires from top labs |
| 5 | World-class data flywheel; foundational AI partnerships or is itself an AI platform; top-tier research talent; data and ecosystem are core competitive advantage |

**Anchor Examples:**
- Score 1: Traditional retailer with no first-party data strategy, generic cloud vendor relationship, no AI hires.
- Score 3: Mid-cap fintech with unique transaction data, integrated partnership with one AI platform, 5–10 AI/ML engineers.
- Score 5: Snowflake, Palantir, or Google. Data IS the moat.

---

<a id="industry-tiers"></a>
## Industry Tier Benchmarks

Use these as starting-point calibration before company-specific analysis:

| Tier | Sectors | Key Characteristics |
|------|---------|---------------------|
| Tier 1: Extreme | Information Technology, Communication Services | Dual exposure: creates AI tools AND is disrupted by them. ~75% of GenAI value in customer ops, marketing, software engineering, R&D. |
| Tier 2: High | Financials, Professional Services | Banking: $200–340B annual AI opportunity. Highest labor-cost exposure. Admin (46%) and legal (44%) tasks face top automation rates. |
| Tier 3: Moderate | Healthcare, Consumer Discretionary, Industrials | Healthcare AI at 2.2x broader economy. Retail adoption 42%. Industrials benefit from AI infrastructure buildout. |
| Tier 4: Low | Consumer Staples, Energy, Materials, Utilities, Real Estate | Physical infrastructure AI cannot replicate. Energy/utilities are AI beneficiaries via data center power demand. |
