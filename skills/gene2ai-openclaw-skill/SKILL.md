---
name: gene2ai
description: Query your personal genomic data from Gene2AI. Get structured JSON insights about health risks, drug responses, nutrition, traits, and ancestry — ready for AI-powered personalization.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - GENE2AI_API_KEY
        - GENE2AI_JOB_ID
    primaryEnv: GENE2AI_API_KEY
    emoji: "🧬"
    homepage: https://gene2.ai/guide
---

# Gene2AI — Genomic Data for AI Agents

You have access to the user's personal genomic data through the Gene2AI API. This data has been processed from raw genetic testing files (23andMe, AncestryDNA, etc.) into a structured, AI-readable JSON format covering health risks, drug responses, nutrition, traits, and ancestry.

## When to Use This Skill

Use this skill whenever the user asks about:

- Their **genetic health risks** (e.g., "Am I at risk for type 2 diabetes?")
- **Drug responses** or pharmacogenomics (e.g., "How do I metabolize caffeine?", "Am I sensitive to warfarin?")
- **Nutrition** and nutrigenomics (e.g., "Do I need more vitamin D?", "Am I lactose intolerant?")
- **Physical traits** (e.g., "What does my DNA say about my muscle type?")
- **Ancestry** composition or haplogroups
- **Personalized recommendations** for health, fitness, diet, or wellness based on their genetics
- Anything involving their **DNA**, **genes**, **SNPs**, or **genetic variants**

## How to Query the API

Make a GET request to the Gene2AI API:

```bash
curl -X GET "https://gene2.ai/api/v1/genomics/${GENE2AI_JOB_ID}" \
  -H "Authorization: Bearer ${GENE2AI_API_KEY}"
```

The environment variables `GENE2AI_API_KEY` and `GENE2AI_JOB_ID` are provided by the user. If they are not set, ask the user to:

1. Go to https://gene2.ai and upload their genetic data file
2. After analysis completes, go to https://gene2.ai/api-keys to generate an API key
3. Set the environment variables:
   ```
   GENE2AI_API_KEY=<their API key>
   GENE2AI_JOB_ID=<their job ID from the results page>
   ```

## Response Format

The API returns a JSON object with the following top-level categories:

| Category | Description | Example Fields |
|---|---|---|
| `health_risks` | Disease risk assessments based on genetic variants | condition, risk_level, rsid, genotype |
| `pharmacogenomics` | Drug response predictions and metabolizer status | drug, gene, metabolizer_status, recommendation |
| `traits` | Physical and behavioral trait predictions | trait, result, confidence, rsid |
| `nutrigenomics` | Nutrition-related genetic insights | nutrient, gene, status |
| `ancestry` | Ancestry composition and haplogroup data | region, percentage, haplogroup |
| `metadata` | Analysis metadata | source, total_variants, analyzed_at |

### Example Response Structure

```json
{
  "health_risks": [
    {
      "condition": "Type 2 Diabetes",
      "risk_level": "elevated",
      "rsid": "rs7903146",
      "genotype": "CT"
    }
  ],
  "pharmacogenomics": [
    {
      "drug": "Caffeine",
      "gene": "CYP1A2",
      "metabolizer_status": "fast",
      "recommendation": "Normal caffeine tolerance"
    }
  ],
  "traits": [
    {
      "trait": "Lactose Tolerance",
      "result": "Likely tolerant",
      "confidence": "high",
      "rsid": "rs4988235"
    }
  ],
  "nutrigenomics": [
    {
      "nutrient": "Vitamin D",
      "gene": "VDR",
      "status": "May need supplementation"
    }
  ],
  "ancestry": [
    {
      "region": "East Asian",
      "percentage": 45.2,
      "haplogroup": "D4"
    }
  ],
  "metadata": {
    "source": "23andme",
    "total_variants": 650000,
    "analyzed_at": "2026-03-01T12:00:00Z"
  }
}
```

## Error Handling

| HTTP Status | Error Code | Meaning |
|---|---|---|
| 401 | `missing_token` | No Authorization header — check `GENE2AI_API_KEY` is set |
| 401 | `invalid_token` | API key is malformed or invalid |
| 403 | `token_expired` | API key expired (30-day limit) — user needs to generate a new one at https://gene2.ai/api-keys |
| 403 | `key_revoked` | API key was manually revoked |
| 403 | `job_id_mismatch` | Key not authorized for this job ID |
| 404 | `job_not_found` | Job ID does not exist |
| 404 | `data_not_available` | Analysis not yet complete — tell user to wait and check status later |

If you receive a `token_expired` or `key_revoked` error, instruct the user to visit https://gene2.ai/api-keys to generate a fresh API key.

## Guidelines for Presenting Genomic Data

When presenting genomic information to the user, follow these guidelines:

1. **Always include disclaimers**: Genetic data provides risk estimates, not diagnoses. Always remind users to consult healthcare professionals for medical decisions.

2. **Explain risk levels clearly**: "Elevated risk" does not mean certainty. Explain that genetics is one factor among many (lifestyle, environment, family history).

3. **Be actionable**: When sharing pharmacogenomics data, suggest the user discuss findings with their doctor before making medication changes.

4. **Respect sensitivity**: Ancestry and health risk data can be emotionally sensitive. Present findings with care and context.

5. **Cross-reference categories**: For holistic advice, combine insights across categories. For example, nutrigenomics data about vitamin D metabolism combined with health risk data can provide more complete recommendations.

6. **Cite the specific variants**: When discussing a finding, mention the rsID (e.g., rs7903146) so the user can verify or research further.
