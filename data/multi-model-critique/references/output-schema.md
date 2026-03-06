# Output Schema (JSON)

Use this schema when callers need machine-parseable results.

```json
{
  "schemaVersion": "1.0.0",
  "question": "string",
  "models": [
    {
      "name": "codex",
      "agentId": "acp-codex",
      "status": "ok|failed",
      "scores": {
        "accuracy": 1,
        "coverage": 1,
        "evidence": 1,
        "actionability": 1,
        "weighted": 1.0
      },
      "draft": "string",
      "critique": "string",
      "revised": "string",
      "error": "string|null"
    }
  ],
  "final": {
    "answer": "string",
    "keyImprovements": ["string"],
    "uncertainties": ["string"],
    "nextSteps": ["string"],
    "confidence": "low|medium|high"
  },
  "ops": {
    "timeoutSec": 180,
    "maxRetries": 1,
    "maxRounds": 4,
    "budgetUsd": null
  },
  "timestamps": {
    "startedAt": "ISO-8601",
    "finishedAt": "ISO-8601"
  }
}
```

## Notes
- Keep `scores.*` on a 1-5 scale, except `weighted` which is a float.
- Use `status="failed"` with `error` when a model round fails.
- Keep text fields concise if the payload is sent through chat channels.
