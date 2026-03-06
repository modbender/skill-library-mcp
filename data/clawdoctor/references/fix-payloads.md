# Fix Payloads & Model Tiers

## Config Patch Payloads

All fixes are applied via exec tool:
```bash
openclaw gateway call config.patch --params '{"patch": <payload>}' --json --timeout 10000
```

| Fix | Payload |
|-----|---------|
| Switch agent to budget model | `{"agents":{"list":[{"id":"<agent>","model":{"primary":"google/gemini-2.5-flash-lite"}}]}}` |
| Switch agent to standard model | `{"agents":{"list":[{"id":"<agent>","model":{"primary":"google/gemini-3-flash"}}]}}` |
| Set tool budget (50 calls) | `{"agents":{"defaults":{"toolBudget":50}}}` |
| Set session timeout (5 min) | `{"agents":{"defaults":{"sessionTimeout":300}}}` |
| Set session timeout (1 hour) | `{"agents":{"defaults":{"sessionTimeout":3600}}}` |
| Enable prompt caching | `{"gateway":{"promptCaching":{"enabled":true}}}` |
| Add conciseness instruction | `{"agents":{"list":[{"id":"<agent>","systemPrompt":{"append":"Be concise. Under 500 tokens unless asked."}}]}}` |
| Switch heartbeat to budget model | `{"agents":{"defaults":{"heartbeat":{"model":"google/gemini-2.5-flash-lite"}}}}` |

## Model Cost Tiers

| Tier | Models | Cost | Analogy |
|------|--------|------|---------|
| Premium | gemini-3-pro-preview, gemini-2.5-pro | $$$ | PhD for every task |
| Standard | gemini-3-flash | $$ | Solid full-time employee |
| Budget | gemini-2.5-flash-lite | $ | Intern who's great at routine work |

Use **$6 per 1M tokens** as blended average when estimating waste.

### Cost Estimate for Analysis

When estimating analysis cost before running (Step 3b):
- Premium (gemini-3-pro): ~$10 per 1M tokens
- Standard (gemini-3-flash): ~$1 per 1M tokens
- Budget (gemini-2.5-flash-lite): ~$0.3 per 1M tokens

## State Files

### memory/pending-fixes.json

Write after every report:
```json
{
  "generatedAt": "<ISO>",
  "fleetGrade": "<grade>",
  "fixes": [
    {
      "number": 1,
      "laymanTitle": "<plain english>",
      "category": "<pattern>",
      "affectedAgents": ["<id>"],
      "keywords": ["<word1>", "<word2>"],
      "fixType": "config-patch",
      "fixPayload": { },
      "fixSummary": "<one line>",
      "estimatedSavings": "$<X>/month",
      "applied": false
    }
  ]
}
```

### memory/last-analysis.json

Write after every run:
```json
{
  "lastRunAt": "<ISO>",
  "fleetGrade": "<grade>",
  "analyzedSessions": 0,
  "totalWaste": 0,
  "topIssue": "<description>",
  "topIssueSavings": 0,
  "agentCosts": [{ "agentId": "<id>", "monthlyCost": 0 }]
}
```

## Fleet Grading Scale

| Grade | Criteria |
|-------|----------|
| A | <$50/month run rate, no critical patterns |
| B | <$100/month |
| C | <$200/month |
| D | <$500/month |
| F | >$500/month or critical behavioral patterns |

---
*ClawDoctor by [Faan AI](https://faan.ai)*
