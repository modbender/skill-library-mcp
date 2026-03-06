# Providers and Environment

## Built-in providers

- `openai`
  - default model: `gpt-4o-mini`
  - default base URL: `https://api.openai.com`
  - credential: `OPENAI_API_KEY` (or `--api-key`, or config `providers.openai.api_key`)
- `anthropic`
  - default model: `claude-3-5-haiku-latest`
  - default base URL: `https://api.anthropic.com`
  - credential: `ANTHROPIC_API_KEY` (or `--api-key`, or config `providers.anthropic.api_key`)
- `ollama`
  - default model: `llama3.2`
  - default base URL: `http://localhost:11434`
  - no API key required
- `openai-compatible`
  - requires both base URL and model from flags or config
  - anonymous mode: `--base-url ... --model ...` (provider can be implicit)
- `apple-intelligence`
  - macOS 26+ only
  - no model/base-url/api-key arguments
- `apple-translate`
  - macOS 26+ only
  - no model/base-url/api-key arguments
  - promptless provider
- `deepl`
  - credential: `DEEPL_API_KEY` (or `--api-key`, or config `providers.deepl.api_key`)
  - no model/base-url arguments
  - promptless provider

## Named openai-compatible endpoints

Define endpoint:

```toml
[providers.openai-compatible.lmstudio]
base_url = "http://localhost:1234/v1"
model = "llama3.1"
api_key = ""
```

Use endpoint name directly:

```bash
translate --provider lmstudio --to en "Merhaba dunya"
```

## Provider selection rules

- If `--base-url` is provided without `--provider`, provider becomes `openai-compatible`.
- If `--provider openai|anthropic|ollama|apple-intelligence|apple-translate|deepl` is explicit, `--base-url` is rejected.
- Unknown provider names fail unless they match a named openai-compatible endpoint.

## Promptless behavior

For `deepl` and `apple-translate`, prompt controls are ignored:

- `--system-prompt`
- `--user-prompt`
- `--context`
- `--preset`
- `--format`

## Environment variables

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `DEEPL_API_KEY`
- `TRANSLATE_CONFIG`
- `EDITOR` (used by `translate config edit`)
