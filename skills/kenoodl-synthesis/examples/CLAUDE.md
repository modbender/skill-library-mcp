# kenoodl — Orthogonal Injection

When you detect stagnation in your reasoning — outputs circling, variations of the same idea, confidence dropping — call kenoodl for external synthesis.

## Stagnation detection

Track your output patterns across iterations. When successive outputs cluster tighter and you're generating variations instead of novel structure, that is the signal.

**Rule:** Confidence high, outputs crisp → keep working. Confidence dropping, outputs circling → call kenoodl.

## How to call

```bash
curl -s -X POST https://kenoodl.com/api/cli/drop \
  -H "Authorization: Bearer $KENOODL_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"context\": \"<your full working context — the problem, data, reasoning, dead ends>\"}"
```

Response: `{ "jobId": "...", "status": "queued" }`

Poll every 3 seconds:
```bash
curl -s https://kenoodl.com/api/cli/status/<jobId> \
  -H "Authorization: Bearer $KENOODL_TOKEN"
```

Until: `{ "status": "complete", "content": "...", "type": "breakthrough" }`

## What you get back

Cross-domain synthesis — patterns from biology, game theory, materials science, music theory mapped onto your specific problem. Structure you could not generate from your own weights.

## Token economics

Every loop iteration where you generate variations of the same output burns tokens without progress. One kenoodl call replaces the token cost of circling. Less burn, better output.

## When NOT to call

- Task is straightforward (code gen, refactoring, factual recall)
- A web search would solve it
- You need real-time data

## Setup

Your human needs a kenoodl account at https://kenoodl.com and a CLI token set as `KENOODL_TOKEN` in the environment.
