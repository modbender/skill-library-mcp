# TOML Configuration

## Contents

- [Path resolution](#path-resolution)
- [Effective precedence during translation](#effective-precedence-during-translation)
- [Supported schema](#supported-schema)
- [Config key usage helpers](#config-key-usage-helpers)
- [Notes](#notes)

## Path resolution

Config path precedence (highest to lowest):

1. CLI flag: `--config /path/to/config.toml`
2. Environment variable: `TRANSLATE_CONFIG=/path/to/config.toml`
3. Default: `~/.config/translate/config.toml`

Inspect current path:

```bash
translate config path
```

## Effective precedence during translation

For overlapping settings, runtime resolution is:

1. CLI flags
2. Preset values
3. `[defaults]` in config
4. Built-in defaults

## Supported schema

```toml
[defaults]
provider = "openai"
from = "auto"
to = "en"
preset = "general"
format = "auto"
stream = false
yes = false
jobs = 1

[network]
timeout_seconds = 120
retries = 3
retry_base_delay_seconds = 1

[providers.openai]
base_url = "https://api.openai.com"
model = "gpt-4o-mini"
api_key = ""

[providers.anthropic]
base_url = "https://api.anthropic.com"
model = "claude-3-5-haiku-latest"
api_key = ""

[providers.ollama]
base_url = "http://localhost:11434"
model = "llama3.2"
api_key = ""

[providers.deepl]
api_key = ""

[providers.openai-compatible]
base_url = ""
model = ""
api_key = ""

[providers.openai-compatible.lmstudio]
base_url = "http://localhost:1234/v1"
model = "llama3.1"
api_key = ""

[presets.markdown-custom]
system_prompt = "..."
system_prompt_file = "prompts/system.txt"
user_prompt = "..."
user_prompt_file = "prompts/user.txt"
provider = "openai"
model = "gpt-4o-mini"
from = "auto"
to = "en"
format = "markdown"
```

## Config key usage helpers

- Read key: `translate config get defaults.provider`
- Read stream default: `translate config get defaults.stream`
- Set scalar key: `translate config set defaults.jobs 4`
- Set stream default: `translate config set defaults.stream true`
- Remove key: `translate config unset defaults.jobs`
- Edit full file: `translate config edit`
- Print effective config (built-ins merged): `translate config show`

`translate config set` parses scalar values as:

- `true` / `false` -> bool
- integer -> int
- decimal with `.` -> double
- anything else -> string

Use `config edit` for complex TOML values or large preset blocks.

## Notes

- Config file is written as UTF-8.
- On macOS, new config files are created with `0600` permissions.
- Named openai-compatible endpoints that collide with built-in provider names emit warnings and are ignored.
- Streaming precedence is: `--no-stream` > `--stream` > `[defaults].stream` > built-in default (`false`).
- Both `--stream` and `--no-stream` exist because the config file can set a global default, and users still need a one-command override in either direction.
