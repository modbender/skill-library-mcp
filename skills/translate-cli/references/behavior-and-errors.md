# Behavior, Validation, and Errors

## Input resolution

- `--text` forces literal text mode and requires exactly one positional argument.
- No positional argument:
  - if stdin is piped, read stdin
  - if stdin is TTY, fail with "No input provided..."
- One positional argument without `--text`:
  - if it is a glob pattern, expand with tool-side globbing
  - if it is an existing file, use file mode
  - otherwise treat as inline text
- Multiple positional args:
  - each must be a file or glob match
  - non-file argument causes an error with `--text` guidance

## File inspection behavior

- Binary files are rejected.
- Invalid UTF-8 files are rejected.
- Empty files are skipped with warnings.
- Multi-file runs continue on per-file failures.

## Output planning

- Inline text and stdin default to stdout.
- Single explicit file defaults to stdout.
- Multi-file and glob inputs default to per-file writes.
- Default per-file suffix: `_<TO_CODE_UPPER>` (example: `_FR`).
- `--suffix` is ignored with single explicit file to stdout (warning emitted).

## Confirmation behavior

- Overwrite prompts are shown when destination exists unless `--yes`.
- `--in-place` on file batches asks one confirmation prompt unless `--yes`.
- In non-TTY mode without `--yes`, confirmation-required operations abort.

## Concurrency and partial failures

- `--jobs` controls parallel file processing.
- Jobs are clamped to at least 1.
- If any file fails in multi-file runs:
  - summary is printed to stderr
  - process exits with runtime error code
  - successful outputs are kept

## Streaming behavior

- Stdout mode may stream from providers that support streaming when streaming is enabled.
- File output modes buffer response first, then write.
- Streaming is enabled by `--stream` or by `defaults.stream = true`.
- `--no-stream` disables streaming for the current command, even if config enables it.
- Both flags are needed because global config and one-off command overrides are separate concerns.
- Wrapping markdown code fences from model output are stripped before final output.

## `.xcstrings` behavior

- `.xcstrings` files are processed by catalog workflow with best-effort mode.
- Catalog segment failures are summarized and reported as file failures.
- `--dry-run` for catalog files prints catalog-specific dry-run details.

## Common errors

- `OPENAI_API_KEY is required for provider 'openai'.`
- `ANTHROPIC_API_KEY is required for provider 'anthropic'.`
- `DEEPL_API_KEY is required for provider 'deepl'.`
- `'auto' is not valid for --to.`
- `--output can only be used with a single input.`
- `--in-place and --output cannot be used together.`
- `--in-place and --suffix cannot be used together.`
- `--stream and --no-stream cannot be used together.`
- `--verbose and --quiet cannot be used together.`

## Exit codes

- `0`: success
- `1`: runtime error
- `2`: invalid arguments
- `3`: aborted
