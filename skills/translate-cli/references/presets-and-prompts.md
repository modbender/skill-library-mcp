# Presets and Prompts

## Built-in presets

- `general`: general-purpose translation
- `markdown`: preserve markdown structure and technical blocks
- `xcode-strings`: preserve `%@`, `%lld`, `%1$@`-style placeholders
- `legal`: formal and strict-fidelity translation
- `ui`: concise UI labels and interface copy

List and inspect:

```bash
translate presets list
translate presets show markdown
translate presets which
```

## Prompt placeholders

Templates support:

- `{from}`
- `{to}`
- `{text}`
- `{context}`
- `{context_block}`
- `{filename}`
- `{format}`

`{context_block}` becomes empty when context is blank; otherwise it is rendered as:

`Additional context: <trimmed-context>`

## Override prompts

Inline:

```bash
translate --text --to en \
  --system-prompt "You translate {from} to {to}." \
  --user-prompt "Translate {format}: {text}" \
  "Merhaba dunya"
```

From files:

```bash
translate --text --to en \
  --system-prompt @./prompts/system.txt \
  --user-prompt @./prompts/user.txt \
  "Merhaba dunya"
```

## Warning behavior

- If using custom prompts and neither `{from}` nor `{to}` exists, a warning is shown.
- Pass `--no-lang` to suppress that warning when languages are intentionally hardcoded.
- `--no-lang` with default prompts warns that it has no effect.

## User-defined presets in TOML

```toml
[presets.release-notes]
system_prompt = "You are a technical translator from {from} to {to}."
user_prompt = "Translate this markdown from {from} to {to}.{context_block}\n\n{text}"
provider = "openai"
model = "gpt-4o-mini"
from = "auto"
to = "en"
format = "markdown"
```

Supported keys inside `[presets.<name>]`:

- `system_prompt`
- `system_prompt_file`
- `user_prompt`
- `user_prompt_file`
- `provider`
- `model`
- `from`
- `to`
- `format`
