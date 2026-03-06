# 🔑 ipeaky

**Secure API key management for [OpenClaw](https://openclaw.ai) agents.**

Keys never touch chat history, command arguments, or logs. Ever.

## Why

AI agents need API keys. Pasting them in chat is a security nightmare — they end up in conversation history, logs, and context windows. ipeaky solves this with a chat-native flow that keeps keys invisible end-to-end.

## How It Works

```
"Store my OpenAI key" → secure popup (hidden input) → config.patch → openclaw.json → done
```

1. **You say** "store my key" in chat
2. **Native macOS dialog** pops up with a hidden input field (dots, not plaintext)
3. **Key pipes through stdout** to OpenClaw's `gateway config.patch`
4. **Stored in `openclaw.json`** — OpenClaw's native config, auto-injected into all skills via `primaryEnv`
5. **Gateway reloads** — every skill picks up the key immediately, zero manual wiring

Keys never appear in chat, shell history, process lists, or logs.

## Scripts

### `secure_input_mac.sh` — Secure input popup (macOS)
```bash
bash scripts/secure_input_mac.sh OPENAI_API_KEY
# → Native macOS dialog with hidden input
# → Outputs key to stdout (captured by agent, never displayed)
```

### `test_key.sh` — Validate a key against the provider API
```bash
echo "$KEY" | bash scripts/test_key.sh openai
# → OK: OpenAI key (sk-7****) is valid.
```

Reads key from **stdin only**. Output always uses masked values (first 4 chars + `****`).

**Other operations** (list, delete) are handled agent-side via `gateway config.get` and `gateway config.patch` — no extra scripts needed.

## Supported Services

| Service | Test Endpoint | Auto-test |
|---------|--------------|-----------|
| OpenAI | `/v1/models` | ✅ |
| ElevenLabs | `/v1/user` | ✅ |
| Anthropic | `/v1/messages` | ✅ |
| Brave Search | `/res/v1/web/search` | ✅ |
| Gemini | `/v1/models` | ✅ |
| Any service | — | stored, no auto-test |

## Storage Model

ipeaky v3 stores keys in **OpenClaw's native config** (`openclaw.json`) via `gateway config.patch`:

- Keys are injected into skills automatically via OpenClaw's `primaryEnv` system
- One key can serve multiple skills (e.g., OpenAI key → whisper, image-gen, etc.)
- `config.patch` triggers a gateway reload — keys take effect immediately
- No separate credential files, no `source` commands, no manual env setup

**Trade-off:** Keys in `openclaw.json` are available to all skills that declare the matching `primaryEnv`. This is intentional — it's how OpenClaw's skill system works. If you need per-skill isolation, use a different approach.

## Security Model

- **Hidden input** — macOS native dialog with `with hidden answer` (dots, not plaintext)
- **stdin-only piping** — keys never appear in `ps`, `history`, or chat
- **Masked output** — display shows `sk-7****`, never full values
- **No eval** — scripts use no `eval` or dynamic execution
- **Strict mode** — all scripts use `set -euo pipefail`
- **Storage is local** — `openclaw.json` on disk, no external transmission
- **Tests are networked** — validation calls provider APIs (opt-in, read-only endpoints)

## 💎 Paid Tier (Coming Soon)

ipeaky core is free forever. A paid tier is in development with premium features for power users and teams — key rotation reminders, team sharing, usage analytics, breach monitoring, and cross-platform support.

See [`paid_tier/README-paid.md`](paid_tier/README-paid.md) for the full roadmap and setup.

## Testing

Run the full test suite (32 tests — static analysis, security audit, live key validation):

```bash
bash tests/run_tests.sh
```

## Install

```
clawhub install ipeaky
```

Or drop the `ipeaky/` folder into your OpenClaw skills directory.

## License

MIT — use it, fork it, secure your keys.
