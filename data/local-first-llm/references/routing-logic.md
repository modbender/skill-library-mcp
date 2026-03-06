# Routing Decision Logic

## Complexity Scoring

Each request is scored before routing. Higher = more complex = prefer cloud.

| Factor                                                                                                                                                                                   | Score Change |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| Keyword match: `analyze`, `synthesize`, `compare`, `reason`, `architecture`, `code review`, `multi-step`, `evaluate`, `critique`, `refactor`, `design`, `implement`, `debug`, `strategy` | +2 per match |
| Keyword match: `summarize`, `translate`, `list`, `what is`, `define`, `explain briefly`, `convert`, `format`, `reformat`, `spell check`                                                  | −1 per match |
| Token count > 4,000                                                                                                                                                                      | +2           |
| Token count < 500                                                                                                                                                                        | −1           |

## Decision Tree

```
Is a local provider available?
  → No  → ☁️  Cloud  ("No local LLM provider is running")

  → Yes → Does prompt contain sensitive keywords?
            → Yes → 🏠 Local  ("Contains sensitive data — routing locally for privacy")

            → No  → complexity score ≥ 3?
                      → Yes → ☁️  Cloud  ("High complexity — routing to cloud")
                      → No  → 🏠 Local   ("Simple/moderate — local model sufficient")
```

## Sensitivity Keywords

Any of these in the prompt forces local routing regardless of complexity:

```
password  secret  private  confidential  internal
ssn  api key  token  credential  salary  medical
```

## Adjusting Thresholds

To change the cloud-routing threshold, edit `scripts/route_request.py`:

- `complexity >= 3` → raise number to send more to local, lower to send more to cloud
- Add keywords to `COMPLEX_KEYWORDS` / `SIMPLE_KEYWORDS` / `SENSITIVE_KEYWORDS` lists

## Supported Local Providers (priority order)

| Provider  | Port  | Detection URL                     |
| --------- | ----- | --------------------------------- |
| Ollama    | 11434 | `http://localhost:11434/api/tags` |
| LM Studio | 1234  | `http://localhost:1234/v1/models` |
| llamafile | 8080  | `http://localhost:8080/v1/models` |

The first provider that responds is used as `"best"`.
