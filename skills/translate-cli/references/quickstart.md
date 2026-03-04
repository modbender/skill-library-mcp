# Quickstart

## Provider credentials (if required)

Set API keys before running network providers:

```bash
export OPENAI_API_KEY="your_openai_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
export DEEPL_API_KEY="your_deepl_key"
```

Notes:

- `openai` needs `OPENAI_API_KEY`
- `anthropic` needs `ANTHROPIC_API_KEY`
- `deepl` needs `DEEPL_API_KEY`
- `ollama` usually does not need an API key
- `apple-translate` and `apple-intelligence` do not use API keys
- Put options before positional input(s) in examples and real commands (for example, `translate --to de README.md`).

## Translate inline text

```bash
translate --text --from tr --to en "Merhaba dunya"
```

## Auto-detect source language

```bash
translate --text --to fr "Hello world"
```

## Translate from stdin

```bash
echo "Merhaba dunya" | translate --to en
```

## Translate one file to stdout

```bash
translate --to de docs/input.md
```

## Stream one stdout translation explicitly

```bash
translate --stream --to de docs/input.md
```

## Translate one file to a destination file

```bash
translate --to de --output docs/input.de.md docs/input.md
```

## Overwrite a file in place

```bash
translate --to de --in-place --yes docs/input.md
```

## Translate many files with per-file outputs

```bash
translate --to fr --suffix _fr --jobs 4 docs/*.md
```

## Force tool-side glob expansion

```bash
translate --to fr "docs/**/*.md"
```

## Use a preset

```bash
translate --preset markdown --to fr README.md
```

## Use custom prompt templates from files

```bash
translate --text --to en \
  --system-prompt @./prompts/system.txt \
  --user-prompt @./prompts/user.txt \
  "Merhaba dunya"
```

## Use a named openai-compatible endpoint from config

```bash
translate --provider lmstudio --to en "Merhaba dunya"
```

## Dry run before sending any request

```bash
translate --provider ollama --text --to en --dry-run "Merhaba dunya"
```

## Translate Xcode string catalogs

```bash
translate --preset xcode-strings --to fr Localizable.xcstrings
```

## Configure defaults once

```bash
translate config set defaults.provider anthropic
translate config set defaults.to fr
translate config set defaults.stream true
translate config set defaults.jobs 4
```

## Streaming override model

- Use `translate config set defaults.stream true` to make streaming the default.
- Use `--stream` to force it on for one command.
- Use `--no-stream` to force it off for one command.
- The two flags are not redundant: they exist so a global default can still be overridden in either direction without editing config.

## Provider quick setup

### OpenAI

```bash
export OPENAI_API_KEY="your_openai_key"
translate --provider openai --text --to fr "Hello world"
```

### Anthropic

```bash
export ANTHROPIC_API_KEY="your_anthropic_key"
translate --provider anthropic --text --to fr "Hello world"
```

### Ollama

```bash
translate --provider ollama --model llama3.2 --text --to fr "Hello world"
```

### DeepL

```bash
export DEEPL_API_KEY="your_deepl_key"
translate --provider deepl --text --to fr "Hello world"
```

### OpenAI-compatible (ad-hoc endpoint)

```bash
translate \
  --provider openai-compatible \
  --base-url http://localhost:1234/v1 \
  --model llama3.1 \
  --text --to fr "Hello world"
```

### OpenAI-compatible (named endpoint in config)

```bash
translate config set providers.openai-compatible.lmstudio.base_url http://localhost:1234/v1
translate config set providers.openai-compatible.lmstudio.model llama3.1
translate --provider lmstudio --text --to fr "Hello world"
```

### Apple providers (macOS 26+)

```bash
translate --provider apple-translate --text --to fr "Hello world"
translate --provider apple-intelligence --text --to fr "Hello world"
```
