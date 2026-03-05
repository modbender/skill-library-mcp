# Domain Presets

Complete role cards, artifact contracts, and workflow configurations for each domain.

---

## 1. software-dev

### Role Cards

| Slot | Domain Title | Responsibilities |
|------|-------------|-----------------|
| Planner (`architect`) | **Architect** | Analyze requirements, design system architecture, define file structure, interfaces, data flow, dependency analysis |
| Builder (`developer`) | **Developer** | Implement code following architect's plan, follow existing conventions, produce working, compiling code |
| Validator (`tester`) | **Tester** | Write unit/integration/E2E tests, verify acceptance criteria, run test suites, investigate bugs |
| Critic (`reviewer`) | **Code Reviewer** | Review code quality (DRY, naming, structure), security scan (injection, auth, secrets), performance, error handling |

### Recommended Patterns
- **Feature development:** `sequential` (Architect → Developer → Tester → Reviewer)
- **Multi-module feature:** `fan-out-fan-in` (Architect designs contracts → parallel backend/frontend/API → merge → test)
- **Bug fix:** `sequential` variant (Tester investigate → Developer fix → Tester verify → Reviewer)
- **Security audit:** `sequential` variant (Reviewer scan → Architect prioritize → Developer fix → Tester verify)

### Artifact Contracts

| Step | Artifact | Format |
|------|----------|--------|
| Plan | Design Document | File list with purpose, interface definitions (types/signatures), data flow, migration steps |
| Build | Source Code | Files created/modified, deviations from plan with rationale, known limitations |
| Validate | Test Report | Test results (pass/fail count), coverage %, bugs/issues found, regression status |
| Critique | Review Report | Findings rated (critical/major/minor/suggestion), security issues, performance concerns |

### Constraints to Set
- Tech stack, language, framework versions
- Coding standards / linting rules
- Reference files for code style
- Test framework and coverage target
- Files/modules to avoid modifying

---

## 2. content-creation

### Role Cards

| Slot | Domain Title | Responsibilities |
|------|-------------|-----------------|
| Planner (`architect`) | **Producer** | Define content brief, target audience, tone/voice, structure outline, key messages, SEO requirements |
| Builder (`developer`) | **Writer** | Create content following brief, maintain consistent voice, hit word count, include required elements |
| Validator (`tester`) | **Fact-Checker** | Verify all claims, check sources, validate data/statistics, ensure accuracy, flag unsubstantiated claims |
| Critic (`reviewer`) | **Editor** | Review for clarity, flow, grammar, tone consistency, engagement, brand alignment, suggest revisions |

### Recommended Patterns
- **Article/blog post:** `iterative-review` (Producer brief → Writer draft ↔ Editor review ×2 → Fact-checker → Final)
- **Documentation:** `sequential` (Producer outline → Writer draft → Fact-checker verify → Editor polish)
- **Multi-part series:** `fan-out-fan-in` (Producer plan series → parallel article drafts → Editor consistency check)

### Artifact Contracts

| Step | Artifact | Format |
|------|----------|--------|
| Plan | Content Brief | Target audience, key messages, tone guide, outline with section headers, word count target, SEO keywords |
| Build | Draft | Complete content following brief, marked sections for fact-checking, source citations |
| Validate | Fact-Check Report | Claim-by-claim verification, sources checked, accuracy rating, corrections needed |
| Critique | Editorial Report | Clarity/flow/engagement ratings, specific revision requests with line references, final polish notes |

### Constraints to Set
- Brand voice / style guide
- Target word count
- SEO keywords / requirements
- Publication platform requirements
- Source/citation standards

---

## 3. data-analysis

### Role Cards

| Slot | Domain Title | Responsibilities |
|------|-------------|-----------------|
| Planner (`architect`) | **Analyst Lead** | Define research questions, select methodology, design analysis pipeline, identify data sources |
| Builder (`developer`) | **Data Engineer** | Build data pipelines, clean/transform data, implement models, create visualizations |
| Validator (`tester`) | **Statistician** | Validate methodology, check statistical significance, verify assumptions, audit sampling |
| Critic (`reviewer`) | **Peer Reviewer** | Review conclusions for bias, check reproducibility, verify visualizations accuracy, assess limitations |

### Recommended Patterns
- **Exploratory analysis:** `parallel-merge` (Analyst Lead frames → parallel EDA/modeling/visualization → merge insights)
- **ETL pipeline:** `sequential` (Analyst Lead design → Data Engineer build → Statistician validate → Peer Reviewer)
- **Large dataset:** `fan-out-fan-in` (partition data → parallel processing → merge results → validate)

### Artifact Contracts

| Step | Artifact | Format |
|------|----------|--------|
| Plan | Analysis Plan | Research questions, hypotheses, methodology, data sources, expected outputs, statistical tests |
| Build | Analysis Output | Cleaned datasets, model results, visualizations, code/queries used |
| Validate | Statistical Report | Test results, p-values, confidence intervals, assumption checks, sampling adequacy |
| Critique | Review Report | Bias assessment, reproducibility checklist, limitation analysis, alternative interpretations |

### Constraints to Set
- Data sources and access permissions
- Statistical significance thresholds
- Visualization standards
- Privacy / PII handling rules
- Reproducibility requirements

---

## 4. business-strategy

### Role Cards

| Slot | Domain Title | Responsibilities |
|------|-------------|-----------------|
| Planner (`architect`) | **Strategist** | Frame strategic question, define evaluation framework, identify key dimensions to analyze |
| Builder (`developer`) | **Business Analyst** | Conduct market research, competitive analysis, build business cases, model scenarios |
| Validator (`tester`) | **Financial Modeler** | Build financial projections, validate assumptions, stress-test scenarios, calculate ROI/NPV |
| Critic (`reviewer`) | **Risk Advisor** | Identify risks, assess probabilities/impacts, propose mitigations, evaluate regulatory/compliance factors |

### Recommended Patterns
- **Strategic decision:** `parallel-merge` (Strategist frames → parallel market/financial/risk analysis → merge recommendation)
- **Business case:** `sequential` (Strategist scope → Analyst research → Financial Modeler validate → Risk Advisor)
- **Market entry:** `iterative-review` (Strategist brief → Analyst draft strategy ↔ Risk Advisor challenge ×2 → Financial validate)

### Artifact Contracts

| Step | Artifact | Format |
|------|----------|--------|
| Plan | Strategy Framework | Key question, evaluation criteria, dimensions of analysis, decision matrix template |
| Build | Business Analysis | Market data, competitive landscape, SWOT, opportunity assessment, scenario descriptions |
| Validate | Financial Model | Revenue projections, cost analysis, ROI/NPV, sensitivity analysis, break-even timeline |
| Critique | Risk Assessment | Risk register (probability × impact), top risks with mitigations, regulatory considerations |

### Constraints to Set
- Industry / market context
- Time horizon
- Budget constraints
- Regulatory environment
- Competitive landscape

---

## 5. research

### Role Cards

| Slot | Domain Title | Responsibilities |
|------|-------------|-----------------|
| Planner (`architect`) | **Research Lead** | Define research questions, scope literature review, establish evaluation criteria, assign angles |
| Builder (`developer`) | **Researcher** | Conduct deep investigation, gather evidence, analyze findings, draft sections |
| Validator (`tester`) | **Methodology Auditor** | Verify research methodology, check source quality, validate logical consistency, assess evidence strength |
| Critic (`reviewer`) | **Peer Reviewer** | Challenge conclusions, identify gaps, suggest alternative perspectives, assess novelty and contribution |

### Recommended Patterns
- **Literature review:** `parallel-merge` (Research Lead frames → parallel angle investigations → merge synthesis)
- **Technical evaluation:** `sequential` (Research Lead criteria → Researcher investigate → Methodology Auditor → Peer Reviewer)
- **Position paper:** `iterative-review` (Research Lead brief → Researcher draft ↔ Peer Reviewer challenge ×2 → Methodology validate)

### Artifact Contracts

| Step | Artifact | Format |
|------|----------|--------|
| Plan | Research Plan | Research questions, scope boundaries, evaluation criteria, source types, methodology |
| Build | Research Findings | Evidence collected, analysis per question, source citations, preliminary conclusions |
| Validate | Methodology Report | Source quality assessment, logical consistency check, evidence strength rating, gaps identified |
| Critique | Peer Review | Conclusion challenges, alternative interpretations, gap analysis, improvement suggestions, final recommendation |

### Constraints to Set
- Research scope and boundaries
- Source quality requirements
- Recency requirements
- Methodology standards
- Output format (paper, presentation, memo)

---

## Creating Custom Presets

For domains not listed above, create a custom preset by filling in:

```
CUSTOM DOMAIN PRESET: [domain name]
─────────────────────────────────────

ROLE CARDS
  Planner (architect):  [Title] — [What they plan/frame/decompose]
  Builder (developer):  [Title] — [What primary artifact they produce]
  Validator (tester):   [Title] — [What/how they verify correctness]
  Critic (reviewer):    [Title] — [What quality/risk dimensions they assess]

RECOMMENDED PATTERNS
  [Use case 1]: [pattern] — [why]
  [Use case 2]: [pattern] — [why]

ARTIFACT CONTRACTS
  Plan →     [artifact name]: [required sections]
  Build →    [artifact name]: [required sections]
  Validate → [artifact name]: [required sections]
  Critique → [artifact name]: [required sections]

TYPICAL CONSTRAINTS
  - [constraint 1]
  - [constraint 2]
  - [constraint 3]
```
