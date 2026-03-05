# Routing & Validation Logic

## Phase 1 — Pre-flight Routing (route_request.py)

Routes before the LLM runs based on complexity scoring and sensitivity detection.

### Complexity Scoring

Each request is scored. Higher = more complex = prefer cloud.

| Factor                                                                                                                                                                                   | Score Change |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| Keyword match: `analyze`, `synthesize`, `compare`, `reason`, `architecture`, `code review`, `multi-step`, `evaluate`, `critique`, `refactor`, `design`, `implement`, `debug`, `strategy` | +2 per match |
| Keyword match: `summarize`, `translate`, `list`, `what is`, `define`, `explain briefly`, `convert`, `format`, `reformat`, `spell check`                                                  | −1 per match |
| Token count > `token_high_watermark` (default 4,000)                                                                                                                                     | +2           |
| Token count < `token_low_watermark` (default 500)                                                                                                                                        | −1           |

### Decision Tree

```
Is a local provider available?
  → No  → ☁️  Cloud  ("No local LLM provider is running")

  → Yes → Does prompt contain sensitive keywords?
            → Yes → 🏠 Local  ("Contains sensitive data — routing locally for privacy")

            → No  → complexity score ≥ threshold (default 3)?
                      → Yes → ☁️  Cloud  ("High complexity — routing to cloud")
                      → No  → 🏠 Local   ("Simple/moderate — local model sufficient")
```

### Sensitivity Keywords

Any of these in the prompt forces local routing regardless of complexity:

```
password  secret  private  confidential  internal
ssn  api key  token  credential  salary  medical
```

When `redact_output: true` (default), any secret patterns are also stripped from
the JSON output so credentials never appear in logs.

---

## Phase 2 — Post-outcome Validation (validate_result.py)

After the local model runs, score the response quality before committing to it.
This mirrors the `validateHeuristic` logic from `adaptive-routing.ts` (PR #30185).

### Validation Scoring

| Signal                                    | Score Penalty |
| ----------------------------------------- | ------------- |
| Provider/process error (`exit-code != 0`) | −1.0          |
| Request timed out                         | −0.3          |
| Tool execution error                      | −0.6          |
| Empty response                            | −0.4          |

Pass threshold: score ≥ `min_score` (default **0.75**) AND no failure signals.

`should_escalate: true` when validation fails → caller re-runs with cloud model.

### Escalation Workflow

```
route_request.py → local
  ↓
Execute with local provider
  ↓
validate_result.py
  ├── passed=true  → use local result → track_savings.py log --kind local_success
  └── passed=false → re-run with cloud → track_savings.py log --kind escalated
```

---

## Configuration (config.json)

Stored at `~/.openclaw/adaptive-routing/config.json`. All fields optional.

```json
{
  "complexity_threshold": 3,
  "token_high_watermark": 4000,
  "token_low_watermark": 500,
  "redact_output": true
}
```

To send more traffic locally, raise `complexity_threshold`. To prefer cloud for
longer prompts, lower `token_high_watermark`.

---

## Supported Local Providers (priority order)

| Provider  | Port  | Detection URL                     |
| --------- | ----- | --------------------------------- |
| Ollama    | 11434 | `http://localhost:11434/api/tags` |
| LM Studio | 1234  | `http://localhost:1234/v1/models` |
| llamafile | 8080  | `http://localhost:8080/v1/models` |

The first provider that responds becomes `"best"`.
