# Local memory search (OpenClaw)

## Why

Local embeddings keep memory search private and remove dependency on external APIs. The tradeoff is local compute and disk usage.

## What it does

- Enables session memory search (index transcripts).
- Forces local embedding provider with no fallback.
- Sets compaction memory flush before compaction.

## Helper script

Run:

- `{baseDir}/scripts/setup-openclaw-local-memory.sh`

The script:

- Downloads a local embedding GGUF file into `~/.openclaw/models`.
- Sets OpenClaw config keys using `openclaw config set`.
- Prints next steps to restart the gateway and reindex memory.

## Notes

- If you already have a preferred local embedding model, set `OPENCLAW_MEMORY_MODEL_URL` before running the script.
- If memory search is not needed, keep it disabled and skip this step.
- After changing memory settings, restart the gateway and run a memory index for your main agent.

