# ollama-memory-embeddings

Installable OpenClaw skill to use **Ollama as the embeddings server** for
memory search (OpenAI-compatible `/v1/embeddings`).

> **Embeddings only** — chat/completions routing is not affected.

This skill is available on [GitHub](https://github.com/vidarbrekke/OpenClaw-Ollama-Memory-Embeddings) under the MIT license.

## Features

- Interactive embedding model selection:
  - `embeddinggemma` (default — closest to OpenClaw built-in)
  - `nomic-embed-text` (strong quality, efficient)
  - `all-minilm` (smallest/fastest)
  - `mxbai-embed-large` (highest quality, larger)
- Optional import of a local embedding GGUF into Ollama (`ollama create`)
  - Detects: embeddinggemma, nomic-embed, all-minilm, mxbai-embed GGUFs
- Model name normalization (handles `:latest` tag automatically)
- Surgical OpenClaw config update (`agents.defaults.memorySearch`)
- Post-write config sanity check
- Smart gateway restart (detects available restart method)
- Two-step verification: model existence + endpoint response
- Non-interactive mode for automation (GGUF import is opt-in)
- Optional memory reindex during install (`--reindex-memory auto|yes|no`)
- Idempotent drift enforcement (`enforce.sh`)
- Optional auto-heal watchdog (`watchdog.sh`, launchd on macOS)
- Read-only audit report (`audit.sh`) — JSON or text, no config changes
- Optional structured logging (`LOG_FORMAT=json` for ndjson to stderr)

## Install

```bash
bash ~/.openclaw/skills/ollama-memory-embeddings/install.sh
```

Safer defaults are used unless explicitly overridden:
- No gateway restart (`--restart-gateway no`)
- No local GGUF scan/import (`--import-local-gguf no`)
- No watchdog install (unless `--install-watchdog`)

Preview everything without changing anything:

```bash
bash ~/.openclaw/skills/ollama-memory-embeddings/install.sh --dry-run
```

Bulletproof install (enforce + watchdog):

```bash
bash ~/.openclaw/skills/ollama-memory-embeddings/install.sh \
  --non-interactive \
  --model embeddinggemma \
  --reindex-memory auto \
  --install-watchdog \
  --watchdog-interval 60
```

From repo (run from project root):

```bash
bash dist/install.sh
```

## Non-interactive example

```bash
bash ~/.openclaw/skills/ollama-memory-embeddings/install.sh \
  --non-interactive \
  --model embeddinggemma \
  --reindex-memory auto \
  --import-local-gguf yes   # explicit opt-in; "auto" = "no" in non-interactive
```

## Verify

```bash
~/.openclaw/skills/ollama-memory-embeddings/verify.sh
~/.openclaw/skills/ollama-memory-embeddings/verify.sh --verbose   # dump raw response on failure
```

## Drift guard and self-heal

One-time check/heal:

```bash
~/.openclaw/skills/ollama-memory-embeddings/watchdog.sh --once --model embeddinggemma
```

Manual enforce (idempotent):

```bash
~/.openclaw/skills/ollama-memory-embeddings/enforce.sh --model embeddinggemma
```

Install launchd watchdog (macOS):

```bash
~/.openclaw/skills/ollama-memory-embeddings/watchdog.sh \
  --install-launchd \
  --model embeddinggemma \
  --interval-sec 60
```

Remove launchd watchdog:

```bash
~/.openclaw/skills/ollama-memory-embeddings/watchdog.sh --uninstall-launchd
```

## Uninstall / Revert

Best-effort revert using latest config backup:

```bash
~/.openclaw/skills/ollama-memory-embeddings/uninstall.sh
```

Optional restart after revert:

```bash
~/.openclaw/skills/ollama-memory-embeddings/uninstall.sh --restart-gateway yes
```

## Verify memory/embeddings (troubleshooting)

If an agent reports it can’t confirm memory/embeddings (e.g. “Operation not allowed” when running diagnostics), possible causes include tool permissions, gateway state, or a transient error—not necessarily a problem with the embeddings service. You can verify locally:

1. **Skill verification** (reads config, calls Ollama):
   ```bash
   ~/.openclaw/skills/ollama-memory-embeddings/verify.sh
   ~/.openclaw/skills/ollama-memory-embeddings/verify.sh --verbose   # dump response on failure
   ```
2. **Model present in Ollama:**
   ```bash
   ollama list
   ollama show nomic-embed-text   # or embeddinggemma, etc.
   ```
3. **Direct endpoint check:**
   ```bash
   curl -s -X POST http://127.0.0.1:11434/v1/embeddings \
     -H "Content-Type: application/json" \
     -d '{"model":"nomic-embed-text:latest","input":"test"}' | head -c 200
   ```
   A valid response includes `"object":"list"` and `"embedding":[...]`.

Common causes of memory search failure:
- **Model not in Ollama:** config says e.g. `nomic-embed-text:latest` but `ollama list` doesn’t show it → run `ollama pull nomic-embed-text`.
- **Wrong `provider`:** OpenClaw only accepts `memorySearch.provider: "openai"` for OpenAI-compatible endpoints (e.g. Ollama). Any other value (e.g. `remote`) causes config validation to fail (“Invalid input”) and can prevent the gateway from starting. Run `enforce.sh` to fix.
- **Ollama down or unreachable:** start Ollama and ensure `baseUrl` (e.g. `http://127.0.0.1:11434/v1/`) is correct.

## Audit (read-only)

Report commands, config drift, and recommended actions without changing anything:

```bash
~/.openclaw/skills/ollama-memory-embeddings/audit.sh
```

- **JSON** (default): one object to stdout (schema version 1.0.0; see project repo for full contract).
- **Text**: set `AUDIT_OUTPUT=text` for a human-readable summary.
- **Desired state**: set `AUDIT_MODEL` and `AUDIT_BASE_URL` to compare against specific values; exit 0 only when status is `ok`.

## Important: re-embed when changing model

If you switch embedding model, existing vectors may be incompatible with the new
vector space. Rebuild/re-embed your memory index after model changes to avoid
retrieval quality regressions.

Installer behavior:
- `--reindex-memory auto` (default): reindex only when embedding fingerprint changed (`provider`, `model`, `baseUrl`, `apiKey presence`).
- `--reindex-memory yes`: always run `openclaw memory index --force --verbose`.
- `--reindex-memory no`: never reindex automatically.

Notes:
- **Logging**: set `LOG_FORMAT=json` to emit one JSON log line per message (ndjson) to stderr: `{"ts":"...","level":"INFO|WARN|ERROR","msg":"..."}` for CI/automation.
- `enforce.sh --check-only` treats apiKey drift as **missing apiKey** (empty), not strict equality to `"ollama"`.
- Backups are created only when config changes are actually written.
- Legacy config fallback supported: if canonical `agents.defaults.memorySearch` is missing,
  scripts read known legacy paths and mirror updates for compatibility.
