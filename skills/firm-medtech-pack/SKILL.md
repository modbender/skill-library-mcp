---
name: firm-medtech-pack
version: 1.0.0
description: >
  Curated skill bundle for medical device companies, digital health startups and
  pharma R&D teams. Activates the firm pyramid with RA (Regulatory Affairs), Clinical,
  R&D and Quality agents pre-configured for FDA/CE compliance, clinical documentation
  and pharmacovigilance workflows.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    requires:
      env: []
      bins: []
    tools:
      - sessions_send
      - sessions_spawn
      - sessions_history
    primaryEnv: ""
tags:
  - medtech
  - healthtech
  - pharma
  - regulatory
  - fda
  - ce-marking
  - firm-pack
  - sector
---

# firm-medtech-pack

Sector bundle for **medical technology & digital health** environments.

## Activated departments

| Department | Services activated | Focus |
|---|---|---|
| RA | Regulatory Affairs · Compliance Legal | FDA 510(k), CE Marking, MDR |
| Research Development | Research Discovery · R&D Prototyping | Clinical evidence, biomarker research |
| Quality | Compliance Auditing · Reliability · Security | ISO 13485, IEC 62304 |
| Legal | Privacy/Data Protection · IP | HIPAA, patient data, patents |
| Operations | Documentation · SRE/Incident | DHF, adverse event reporting |

## Recommended ClawHub skills to install alongside

```bash
npx clawhub@latest install academic-research        # PubMed / clinical trial search
npx clawhub@latest install admet-prediction         # Drug candidate ADMET analysis
npx clawhub@latest install pdf-documents            # Clinical study PDF parsing
npx clawhub@latest install arc-security-audit       # 21 CFR Part 11 audit trail
npx clawhub@latest install firm-orchestration       # A2A orchestration backbone
```

## Firm configuration overlay

```json
{
  "agent": {
    "model": "anthropic/claude-opus-4-6",
    "workspace": "~/.openclaw/workspace/medtech-firm"
  },
  "agents": {
    "defaults": {
      "sandbox": { "mode": "non-main" }
    }
  }
}
```

## Prompt: regulatory submission prep

```
Use firm-orchestration with:
  objective: "Prepare 510(k) substantial equivalence summary for continuous glucose monitor"
  departments: ["ra", "research_development", "quality"]
  constraints: ["FDA guidance K020431 reference", "predicate device: Dexcom G6"]
  definition_of_done: "510(k) summary draft with predicate comparison table"
  delivery_format: "structured_document"
```

## Prompt: adverse event review

```
Use firm-orchestration with:
  objective: "Classify and triage Q4 adverse event reports against MDR Art. 87"
  departments: ["ra", "quality", "legal"]
  constraints: ["read-only access", "anonymize patient identifiers in output"]
  definition_of_done: "Triage matrix with reportability decisions per event"
  delivery_format: "markdown_report"
```

## Regulatory coverage

| Standard | Department | Service |
|---|---|---|
| FDA 510(k) / PMA | RA | Regulatory Affairs |
| EU MDR 2017/745 | RA + Legal | Regulatory + Privacy |
| ISO 13485:2016 | Quality | Compliance Auditing |
| IEC 62304 | Engineering | AI Engineering |
| HIPAA | Legal | Privacy/Data Protection |
| 21 CFR Part 11 | Quality | Security |
| ISO 14971 | RA + Quality | Risk Management |

## Security notes

- PHI (Protected Health Information): `SECURE_PRODUCTION_MODE=true` mandatory
- All outputs must be anonymized: enforce via `POLICY_BLOCKED_TOOLS` for export
- Audit trail required by 21 CFR Part 11: `AUDIT_ENABLED=true`

---

## 💎 Support

Si ce skill vous est utile, vous pouvez soutenir le développement :

**Dogecoin** : `DQBggqFNWsRNTPb6kkiwppnMo1Hm8edfWq`
