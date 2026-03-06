# Flags and Subcommands

## Main command

```bash
translate [OPTIONS] [TEXT]
translate [OPTIONS] [FILE...]
echo "text" | translate [OPTIONS]
```

Note: with the current parser shape, place options before positional input(s) for reliable parsing.

## Input and output flags

- `--text`: force positional argument to literal text mode (exactly one positional arg required).
- `-o, --output <FILE>`: write result to a file (single explicit file or inline/stdin only).
- `-i, --in-place`: overwrite input file(s) in place (file input only).
- `--suffix <SUFFIX>`: output filename suffix for per-file output naming.
- `--stream`: force streaming on for this command (stdout only).
- `--no-stream`: force streaming off for this command.
- `-y, --yes`: skip confirmations.
- `-j, --jobs <N>`: parallel file translations.

## Language flags

- `-f, --from <LANG>`: source language (`auto` allowed).
- `-t, --to <LANG>`: target language (`auto` is invalid).

Accepted language forms: language names (`French`), ISO 639-1 (`fr`), and BCP 47 tags (`zh-TW`).

## Provider flags

- `-p, --provider <NAME>`:
  - built-ins: `openai`, `anthropic`, `ollama`, `openai-compatible`, `apple-intelligence`, `apple-translate`, `deepl`
  - named endpoint from config: any key under `[providers.openai-compatible.<name>]`
- `-m, --model <ID>`: model override.
- `--base-url <URL>`: API base URL (mainly openai-compatible).
- `--api-key <KEY>`: API key override.

## Prompt and format flags

- `--preset <NAME>`: preset name (built-in or user-defined).
- `--system-prompt <TEMPLATE|@FILE>`: system prompt override.
- `--user-prompt <TEMPLATE|@FILE>`: user prompt override.
- `-c, --context <TEXT>`: context text injected into prompt placeholders.
- `--no-lang`: suppress missing `{from}/{to}` warning for custom prompts.
- `--format <auto|text|markdown|html>`: input format hint.

## Utility and global flags

- `--dry-run`: print resolved provider/model/prompts, no API call.
- `-v, --verbose`: print diagnostics and timing metadata.
- `-q, --quiet`: suppress warnings.
- `--config <FILE>`: override config path.
- `-h, --help`: show help.
- `--version`: show version.

## Subcommands

- `translate config show`
- `translate config path`
- `translate config get <key>`
- `translate config set <key> <value>`
- `translate config unset <key>`
- `translate config edit`
- `translate presets list`
- `translate presets show <name>`
- `translate presets which`

## Important constraints

- `--verbose` and `--quiet` cannot be combined.
- `--stream` and `--no-stream` cannot be combined.
- `--in-place` cannot be combined with `--output`.
- `--in-place` cannot be combined with `--suffix`.
- `--output` cannot be used with multi-file or glob input.
- `--jobs` warns and has no effect for inline text or stdin.
- `--stream` and `--no-stream` are intentionally both available because config may set `defaults.stream`, and each command needs an explicit override in either direction.
