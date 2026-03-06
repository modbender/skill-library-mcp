# aimlapi-llm-reasoning

This skill provides a helper script for AIMLAPI chat + reasoning workflows.

## Security & Credentials

- This skill requires an `AIMLAPI_API_KEY` environment variable.
- Be cautious when using the `--apikey-file` flag; ensure the provided path is correct and secure.
- Avoid including sensitive or private data in `--extra-json`, as this payload is sent to the remote API.

## New instructions

- Every HTTP request sends a `User-Agent` header (configurable via `--user-agent`).
- `run_chat.py` supports retries, API key from `--apikey-file`, and verbose logs.
- Use `--extra-json` for reasoning/tooling/provider-specific fields.

See `SKILL.md` for examples.
