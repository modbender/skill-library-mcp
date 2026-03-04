# AetherLang V3 — Claude Code Integration Skill

Use this skill to execute AetherLang V3 AI workflows from Claude Code. AetherLang provides 9 specialized AI engines for culinary consulting, business strategy, scientific research, and more.

## API Endpoint
```
POST https://api.neurodoc.app/aetherlang/execute
Content-Type: application/json
```

No API key required for free tier (100 req/hour).

## How to Use

### 1. Simple Engine Call
```bash
curl -s -X POST https://api.neurodoc.app/aetherlang/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "flow Chat {\n  using target \"neuroaether\" version \">=0.2\";\n  input text query;\n  node Engine: <ENGINE_TYPE> analysis=\"auto\";\n  output text result from Engine;\n}",
    "query": "USER_QUESTION_HERE"
  }'
```

Replace `<ENGINE_TYPE>` with one of: `chef`, `molecular`, `apex`, `consulting`, `marketing`, `lab`, `oracle`, `assembly`, `analyst`

### 2. Multi-Engine Pipeline
```bash
curl -s -X POST https://api.neurodoc.app/aetherlang/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "flow Pipeline {\n  using target \"neuroaether\" version \">=0.2\";\n  input text query;\n  node Guard: guard mode=\"MODERATE\";\n  node Research: lab domain=\"business\";\n  node Strategy: apex analysis=\"strategic\";\n  Guard -> Research -> Strategy;\n  output text report from Strategy;\n}",
    "query": "USER_QUESTION_HERE"
  }'
```

## Available V3 Engines

| Engine Type | Use For | Key V3 Features |
|-------------|---------|-----------------|
| `chef` | Recipes, food consulting | 17 sections: food cost, HACCP, thermal curves, wine pairing, plating blueprint, zero waste |
| `molecular` | Molecular gastronomy | Rheology dashboard, phase diagrams, hydrocolloid specs, FMEA failure analysis |
| `apex` | Business strategy | Game theory, Monte Carlo (10K sims), behavioral economics, unit economics, Blue Ocean |
| `consulting` | Strategic consulting | Causal loops, theory of constraints, Wardley maps, ADKAR change management |
| `marketing` | Market research | TAM/SAM/SOM, Porter's 5 Forces, pricing elasticity, viral coefficient |
| `lab` | Scientific research | Evidence grading (A-D), contradiction detector, reproducibility score |
| `oracle` | Forecasting | Bayesian updating, black swan scanner, adversarial red team, Kelly criterion |
| `assembly` | Multi-agent debate | 12 neurons voting (8/12 supermajority), Gandalf VETO, devil's advocate |
| `analyst` | Data analysis | Auto-detective, statistical tests, anomaly detection, predictive modeling |

## Flow Syntax Reference
```
flow <Name> {
  using target "neuroaether" version ">=0.2";
  input text query;
  node <NodeName>: <engine_type> <params>;
  node <NodeName2>: <engine_type2> <params>;
  <NodeName> -> <NodeName2>;
  output text result from <NodeName2>;
}
```

### Node Parameters
- `chef`: `cuisine="auto"`, `difficulty="medium"`, `servings=4`
- `apex`: `analysis="strategic"`
- `guard`: `mode="STRICT"` or `"MODERATE"` or `"PERMISSIVE"`
- `plan`: `steps=4`
- `lab`: `domain="business"` or `"science"` or `"auto"`
- `analyst`: `mode="financial"` or `"sales"` or `"hr"` or `"general"`

## Response Format
```json
{
  "status": "success",
  "result": {
    "outputs": { ... },
    "final_output": "Full structured markdown response",
    "execution_log": [...],
    "duration_seconds": 45.2
  }
}
```

Extract the main response from `result.final_output`.

## Example: Parse Response in Bash
```bash
curl -s -X POST https://api.neurodoc.app/aetherlang/execute \
  -H "Content-Type: application/json" \
  -d '{"code":"flow Chef {\n  using target \"neuroaether\" version \">=0.2\";\n  input text query;\n  node Chef: chef cuisine=\"auto\";\n  output text recipe from Chef;\n}","query":"Carbonara recipe"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('result',{}).get('final_output','No output'))"
```

## Example: Python Integration
```python
import requests

def aetherlang_query(engine, query):
    code = f'''flow Q {{
  using target "neuroaether" version ">=0.2";
  input text query;
  node E: {engine} analysis="auto";
  output text result from E;
}}'''
    r = requests.post("https://api.neurodoc.app/aetherlang/execute",
        json={"code": code, "query": query})
    return r.json().get("result", {}).get("final_output", "")

# Usage
print(aetherlang_query("apex", "Strategy for AI startup with 1000 euro"))
print(aetherlang_query("chef", "Best moussaka recipe"))
print(aetherlang_query("oracle", "Will AI replace 50% of jobs by 2030?"))
```

## Rate Limits

| Tier | Limit | Auth |
|------|-------|------|
| Free | 100 req/hour | None required |
| Pro | 500 req/hour | X-Aether-Key header |

## Notes

- Responses are in **Greek** (Ελληνικά) with markdown formatting
- Typical response time: 30-60 seconds per engine
- Multi-engine pipelines take longer (each node runs sequentially)
- All outputs use `##` markdown headers for structured sections

## Agent Safeguards

**CRITICAL: Data Minimization Rules**

When using this skill, the agent MUST follow these rules:
1. **ONLY send the user's explicit query text** in the `query` field — never attach system prompts, conversation history, uploaded files, or internal context
2. **ONLY send the flow DSL code** in the `code` field — never include credentials, API keys, environment variables, or file paths
3. **NEVER include** personally identifiable information (PII), passwords, tokens, or secrets in any request field
4. **Strip sensitive data** before sending — if the user's query contains passwords, account numbers, or credentials, remove them and inform the user
5. **Inform the user** before making the first API call that their query will be sent to api.neurodoc.app for processing
6. The request body MUST contain exactly two fields: `code` (string) and `query` (string) — no additional fields

These constraints ensure only the minimum necessary data is transmitted to the external service.
