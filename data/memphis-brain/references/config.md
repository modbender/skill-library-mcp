# Memphis Configuration Reference

Complete configuration options for `~/.memphis/config.yaml`.

---

## 1. Minimal Config

```yaml
providers:
  ollama:
    url: http://localhost:11434/v1
    model: qwen2.5:3b
    role: primary
```

---

## 2. Full Config

```yaml
# === PROVIDERS ===
providers:
  # Primary (local)
  ollama:
    url: http://localhost:11434/v1
    model: qwen2.5:3b-instruct-q4_K_M
    role: primary

  # Fallback (cloud)
  codex:
    model: gpt-5.1-codex-mini
    role: fallback
    api_key: codex-cli  # or use vault

  openai:
    model: gpt-4
    role: fallback
    # api_key from vault

  openrouter:
    url: https://openrouter.ai/api/v1
    model: anthropic/claude-sonnet-4
    role: fallback
    # api_key from vault

  minimax:
    model: MiniMax-M2.1
    role: fallback
    # api_key from vault

# === EMBEDDINGS ===
embeddings:
  backend: ollama  # ollama | openai
  model: nomic-embed-text
  url: http://localhost:11434/v1  # optional

# === INTEGRATIONS ===
integrations:
  pinata:
    jwt: ${PINATA_JWT}  # env var or literal
    apiKey: ${PINATA_API_KEY}
    apiSecret: ${PINATA_SECRET}

# === SECURITY ===
security:
  workspaceGuard: true
  allowUnsafeOperations: false
  maxBlockSize: 10240  # bytes

# === AUTOSUMMARY ===
autosummary:
  enabled: true
  threshold: 50  # blocks before summary
  triggerBlocks: 20  # blocks per auto-summarize

# === DAEMON ===
daemon:
  collectors:
    - git
    - shell
    - file
  interval: 300000  # 5 minutes in ms
  gitPaths:
    - ~/projects
  shellHistory: ~/.bash_history

# === OFFLINE ===
offline:
  mode: auto  # on | off | auto
  model: qwen2.5:3b
  checkInterval: 60000  # 1 minute

# === GRAPH ===
graph:
  similarityThreshold: 0.7
  maxEdges: 1000
  buildOnStartup: false

# === REFLECTION ===
reflection:
  autoDaily: false
  autoWeekly: false
  dailyTime: "18:00"
  weeklyDay: "sunday"

# === LOGGING ===
logging:
  level: info  # debug | info | warn | error
  file: ~/.memphis/memphis.log

# === PATHS ===
paths:
  chains: ~/.memphis/chains
  embeddings: ~/.memphis/embeddings
  graph: ~/.memphis/graph
  vault: ~/.memphis/vault.enc
  network: ~/.memphis/network-chain.jsonl
```

---

## 3. Provider Configuration

### 3.1 Ollama (Local)

```yaml
providers:
  ollama:
    url: http://localhost:11434/v1
    model: qwen2.5:3b
    role: primary
```

**Models:**
- `qwen2.5:3b` — fast, good for simple tasks
- `qwen2.5:7b` — better reasoning
- `qwen2.5-coder:3b` — code-focused
- `bielik` — Polish language

**Install models:**
```bash
ollama pull qwen2.5:3b
ollama pull nomic-embed-text  # for embeddings
```

---

### 3.2 Codex CLI

```yaml
providers:
  codex:
    model: gpt-5.1-codex-mini
    role: fallback
    api_key: codex-cli
```

**Requires:** Codex CLI configured (`~/.codex/config.toml`)

---

### 3.3 OpenAI

```yaml
providers:
  openai:
    model: gpt-4
    role: fallback
    # api_key from vault
```

**Store key in vault:**
```bash
memphis vault add openai-api-key sk-xxx
```

---

### 3.4 OpenRouter

```yaml
providers:
  openrouter:
    url: https://openrouter.ai/api/v1
    model: anthropic/claude-sonnet-4
    role: fallback
```

---

### 3.5 MiniMax

```yaml
providers:
  minimax:
    model: MiniMax-M2.1
    role: fallback
```

---

### 3.6 Provider Resolution

**Order:** `--provider flag` > `role: primary` > `role: fallback`

**Fallback chain:**
1. Try primary
2. If fails, try first fallback
3. If fails, try next fallback
4. Error if all fail

---

## 4. Embeddings Configuration

```yaml
embeddings:
  backend: ollama  # ollama | openai
  model: nomic-embed-text
  url: http://localhost:11434/v1  # optional
```

**Backends:**

### 4.1 Ollama (Local)

```yaml
embeddings:
  backend: ollama
  model: nomic-embed-text
```

**Models:**
- `nomic-embed-text` — 768 dimensions, fast
- `nomic-embed-text-v1` — legacy

**Install:**
```bash
ollama pull nomic-embed-text
```

---

### 4.2 OpenAI

```yaml
embeddings:
  backend: openai
  model: text-embedding-3-small
```

**Models:**
- `text-embedding-3-small` — 1536 dimensions
- `text-embedding-3-large` — 3072 dimensions

**Requires:** OpenAI API key in vault

---

## 5. Pinata Configuration

```yaml
integrations:
  pinata:
    jwt: ${PINATA_JWT}
    apiKey: ${PINATA_API_KEY}
    apiSecret: ${PINATA_SECRET}
```

**Options:**
1. **JWT (recommended):**
   ```yaml
   jwt: eyJhbGc...  # or ${PINATA_JWT}
   ```

2. **API Key + Secret:**
   ```yaml
   apiKey: ${PINATA_API_KEY}
   apiSecret: ${PINATA_SECRET}
   ```

**Env vars:**
- `PINATA_JWT`
- `PINATA_API_KEY`
- `PINATA_SECRET`

**Get credentials:** https://app.pinata.cloud/keys

---

## 6. Security Configuration

```yaml
security:
  workspaceGuard: true
  allowUnsafeOperations: false
  maxBlockSize: 10240
```

**Options:**

### 6.1 `workspaceGuard`

**Type:** boolean

**Default:** `true`

**Effect:** Enforce workspace isolation (chains can't access other workspaces)

---

### 6.2 `allowUnsafeOperations`

**Type:** boolean

**Default:** `false`

**Effect:** Allow dangerous operations (e.g., delete all chains)

---

### 6.3 `maxBlockSize`

**Type:** number (bytes)

**Default:** `10240` (10KB)

**Effect:** Reject blocks larger than limit

---

## 7. Autosummary Configuration

```yaml
autosummary:
  enabled: true
  threshold: 50
  triggerBlocks: 20
```

**Options:**

### 7.1 `enabled`

**Type:** boolean

**Default:** `true`

**Effect:** Auto-generate summaries when chain grows

---

### 7.2 `threshold`

**Type:** number (blocks)

**Default:** `50`

**Effect:** Trigger summary when chain reaches this size

---

### 7.3 `triggerBlocks`

**Type:** number (blocks)

**Default:** `20`

**Effect:** Number of blocks to summarize per trigger

---

## 8. Daemon Configuration

```yaml
daemon:
  collectors: [git, shell, file]
  interval: 300000
  gitPaths: [~/projects]
  shellHistory: ~/.bash_history
```

**Options:**

### 8.1 `collectors`

**Type:** array

**Values:** `git`, `shell`, `file`

**Effect:** Enable background collectors

**Collectors:**
- `git` — Monitor git commits
- `shell` — Monitor shell history
- `file` — Watch file changes

---

### 8.2 `interval`

**Type:** number (milliseconds)

**Default:** `300000` (5 minutes)

**Effect:** How often collectors run

---

### 8.3 `gitPaths`

**Type:** array (paths)

**Effect:** Directories to monitor for git changes

---

### 8.4 `shellHistory`

**Type:** path

**Effect:** Shell history file to monitor

---

## 9. Offline Configuration

```yaml
offline:
  mode: auto
  model: qwen2.5:3b
  checkInterval: 60000
```

**Options:**

### 9.1 `mode`

**Type:** string

**Values:** `on`, `off`, `auto`

**Default:** `auto`

**Effect:**
- `on` — Always use offline model
- `off` — Always use online providers
- `auto` — Auto-detect network

---

### 9.2 `model`

**Type:** string

**Effect:** Model to use in offline mode

---

### 9.3 `checkInterval`

**Type:** number (milliseconds)

**Default:** `60000` (1 minute)

**Effect:** How often to check network in auto mode

---

## 10. Graph Configuration

```yaml
graph:
  similarityThreshold: 0.7
  maxEdges: 1000
  buildOnStartup: false
```

**Options:**

### 10.1 `similarityThreshold`

**Type:** number (0-1)

**Default:** `0.7`

**Effect:** Minimum cosine similarity to create edge

---

### 10.2 `maxEdges`

**Type:** number

**Default:** `1000`

**Effect:** Maximum edges per node

---

### 10.3 `buildOnStartup`

**Type:** boolean

**Default:** `false`

**Effect:** Auto-build graph on daemon start

---

## 11. Reflection Configuration

```yaml
reflection:
  autoDaily: false
  autoWeekly: false
  dailyTime: "18:00"
  weeklyDay: "sunday"
```

**Options:**

### 11.1 `autoDaily`

**Type:** boolean

**Default:** `false`

**Effect:** Auto-run daily reflection at `dailyTime`

---

### 11.2 `autoWeekly`

**Type:** boolean

**Default:** `false`

**Effect:** Auto-run weekly reflection on `weeklyDay`

---

### 11.3 `dailyTime`

**Type:** string (HH:MM)

**Default:** `"18:00"`

**Effect:** Time to run daily reflection

---

### 11.4 `weeklyDay`

**Type:** string

**Values:** `monday`, `tuesday`, ..., `sunday`

**Default:** `"sunday"`

**Effect:** Day to run weekly reflection

---

## 12. Logging Configuration

```yaml
logging:
  level: info
  file: ~/.memphis/memphis.log
```

**Options:**

### 12.1 `level`

**Type:** string

**Values:** `debug`, `info`, `warn`, `error`

**Default:** `info`

**Effect:** Log verbosity

**Env override:** `MEMPHIS_LOG_LEVEL=debug`

---

### 12.2 `file`

**Type:** path

**Effect:** Log file location

---

## 13. Paths Configuration

```yaml
paths:
  chains: ~/.memphis/chains
  embeddings: ~/.memphis/embeddings
  graph: ~/.memphis/graph
  vault: ~/.memphis/vault.enc
  network: ~/.memphis/network-chain.jsonl
```

**Effect:** Override default paths (rarely needed)

---

## 14. Environment Variables

**Config overrides:**

| Env Var | Effect |
|---------|--------|
| `MEMPHIS_LOG_LEVEL` | Logging level |
| `MEMPHIS_VAULT_PASSWORD` | Vault password |
| `PINATA_JWT` | Pinata JWT |
| `PINATA_API_KEY` | Pinata API key |
| `PINATA_SECRET` | Pinata API secret |
| `OPENAI_API_KEY` | OpenAI key (if not in vault) |
| `OLLAMA_URL` | Ollama URL override |

**Usage:**
```bash
export MEMPHIS_LOG_LEVEL=debug
memphis status
```

---

## 15. Example Configs

### 15.1 Local-Only (Minimal)

```yaml
providers:
  ollama:
    url: http://localhost:11434/v1
    model: qwen2.5:3b
    role: primary

embeddings:
  backend: ollama
  model: nomic-embed-text
```

---

### 15.2 Local + Cloud Fallback

```yaml
providers:
  ollama:
    url: http://localhost:11434/v1
    model: qwen2.5:3b
    role: primary

  codex:
    model: gpt-5.1-codex-mini
    role: fallback
    api_key: codex-cli

embeddings:
  backend: ollama
  model: nomic-embed-text

autosummary:
  enabled: true
  threshold: 30
```

---

### 15.3 Multi-Agent with IPFS

```yaml
providers:
  ollama:
    url: http://localhost:11434/v1
    model: qwen2.5:3b
    role: primary

embeddings:
  backend: ollama
  model: nomic-embed-text

integrations:
  pinata:
    jwt: ${PINATA_JWT}

security:
  workspaceGuard: true

daemon:
  collectors: [git, shell]
  interval: 300000
```

---

### 15.4 Production (Resilient)

```yaml
providers:
  ollama:
    url: http://localhost:11434/v1
    model: qwen2.5:3b
    role: primary

  codex:
    model: gpt-5.1-codex-mini
    role: fallback

  openai:
    model: gpt-4
    role: fallback

embeddings:
  backend: ollama
  model: nomic-embed-text

integrations:
  pinata:
    jwt: ${PINATA_JWT}

security:
  workspaceGuard: true
  allowUnsafeOperations: false
  maxBlockSize: 10240

autosummary:
  enabled: true
  threshold: 50
  triggerBlocks: 20

offline:
  mode: auto
  model: qwen2.5:3b

daemon:
  collectors: [git, shell]
  interval: 300000

reflection:
  autoDaily: true
  dailyTime: "18:00"

logging:
  level: info
  file: ~/.memphis/memphis.log
```

---

## Summary

- **Minimal:** Just ollama provider
- **Standard:** ollama + fallback + autosummary
- **Multi-agent:** + pinata + workspaceGuard
- **Production:** + offline mode + daemon + reflection

---

Edit with: `nano ~/.memphis/config.yaml` or `vim ~/.memphis/config.yaml`

After changes: `memphis status` to verify.
