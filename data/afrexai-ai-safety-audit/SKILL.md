---
name: AI Safety Audit
description: Comprehensive AI safety and alignment audit framework for
  businesses deploying AI agents. Built around the UK AI Security Institute
  Alignment Project standards (2026), EU AI Act requirements, and N...
---

# AI Safety Audit

Comprehensive AI safety and alignment audit framework for businesses deploying AI agents. Built around the UK AI Security Institute Alignment Project standards (2026), EU AI Act requirements, and NIST AI RMF.

## What This Skill Does

When activated, the agent performs a structured safety audit of your AI deployment:

1. **AI System Inventory** — Catalogs all AI models, agents, and automated decision systems in use
2. **Risk Classification** — Maps each system to EU AI Act risk tiers (Unacceptable/High/Limited/Minimal)
3. **Safety Controls Assessment** — Evaluates 30 controls across 6 domains
4. **Gap Analysis** — Identifies missing safeguards with severity and remediation cost
5. **Compliance Roadmap** — Generates a prioritized 90-day action plan

## 6 Audit Domains (30 Controls)

### 1. Model Governance (5 controls)
- Model registry with version tracking
- Access control and deployment permissions
- Update and rollback procedures
- Vendor risk assessment for third-party models
- Model retirement and data deletion policy

### 2. Data Protection (5 controls)
- Data residency and sovereignty mapping
- PII detection and handling in AI pipelines
- Training data provenance documentation
- Data retention aligned with AI lifecycle
- Cross-border data transfer compliance

### 3. Output Safety (5 controls)
- Hallucination detection and mitigation
- Bias testing across protected characteristics
- Content filtering for harmful outputs
- Confidence scoring and uncertainty flagging
- Human-in-the-loop for high-stakes decisions

### 4. Security (5 controls)
- Prompt injection defense
- Model extraction prevention
- API rate limiting and abuse detection
- Adversarial input testing
- Supply chain security for AI dependencies

### 5. Monitoring & Observability (5 controls)
- Real-time output quality tracking
- Drift detection (data and model)
- Incident logging and alerting
- Performance degradation monitoring
- Cost tracking per AI workflow

### 6. Organizational Readiness (5 controls)
- Named AI safety officer
- Staff training program with completion tracking
- Board-level AI risk reporting
- Incident response playbook
- Third-party audit schedule

## Scoring

Each control scores 0-3:
- **0** — Not implemented
- **1** — Partially implemented, no documentation
- **2** — Implemented with documentation
- **3** — Implemented, documented, tested, and audited

**Total: 90 points max**
- 0-30: Critical risk — stop deploying until gaps are addressed
- 31-55: High risk — remediate within 30 days
- 56-75: Moderate risk — address within 90 days
- 76-90: Strong posture — maintain and iterate

## Regulatory Mapping

| Framework | Status | Key Requirements |
|-----------|--------|-----------------|
| EU AI Act | Enforcing 2026 | Risk classification, conformity assessment, transparency |
| UK AI Safety Institute | Active 2026 | Alignment testing, frontier model evaluation |
| NIST AI RMF | Published | Govern, Map, Measure, Manage lifecycle |
| ISO 42001 | Published | AI management system certification |
| SOC 2 + AI | Emerging | Agent-specific controls (CC6/CC7/CC8) |

## Cost Benchmarks

| Company Size | Full Audit Cost | Annual Compliance | Non-Compliance Risk |
|-------------|----------------|-------------------|-------------------|
| 15-50 employees | $8K – $20K | $18K – $45K | $200K+ |
| 50-200 employees | $20K – $55K | $45K – $120K | $500K – $2M |
| 200-1000 employees | $55K – $150K | $120K – $400K | $2M – $10M |

## Output Format

The agent delivers:
1. **Executive Summary** — Overall score, top 3 risks, recommended actions
2. **Detailed Scorecard** — All 30 controls with scores and evidence
3. **Gap Analysis** — Missing controls ranked by risk severity
4. **90-Day Roadmap** — Phased remediation plan with cost estimates
5. **Board Report Template** — One-page summary for leadership

## Industry Adjustments

The audit adjusts control weighting based on industry:
- **Healthcare**: Output safety and data protection weighted 2x
- **Financial Services**: Model governance and monitoring weighted 2x
- **Legal**: Output safety (hallucination) weighted 3x
- **Manufacturing**: Security and monitoring weighted 2x
- **Government/Defense**: All domains weighted equally at maximum

---

## Go Deeper

- **[AI Revenue Leak Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/)** — Quantify what safety gaps cost your business
- **[Industry Context Packs ($47)](https://afrexai-cto.github.io/context-packs/)** — Pre-built compliance frameworks for your specific vertical
- **[Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/)** — Deploy agents with safety controls from day one

### Bundles
- AI Playbook — $27
- Pick 3 Industries — $97
- All 10 Industries — $197
- Everything Bundle — $247
