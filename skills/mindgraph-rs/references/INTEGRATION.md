# MindGraph Integration Guide

## Before You Begin: What This Skill Does to Your Data

MindGraph has two modes. Choose what you're comfortable with before configuring:

| Mode | What it does | External calls? |
|------|-------------|-----------------|
| **Server only** | Stores and queries graph data locally | ❌ None |
| **+ Extraction** | Reads session transcripts, summarizes via your LLM provider, writes nodes to graph | ✅ To your configured LLM (Gemini/Anthropic/Moonshot) |
| **+ Heartbeat/Dreaming** | Runs extraction automatically on a schedule | ✅ Same as above, recurring |

All graph data stays on your machine. No data is sent to ClawHub or MindGraph maintainers.

---

## Step 1: Install the Binary

The server binary is not bundled in the skill (ClawHub only supports text files). Run setup once after installing:

```bash
bash skills/mindgraph-rs/scripts/setup.sh
```

This downloads the pre-built Linux x86_64 binary from [GitHub Releases](https://github.com/shuruheel/mindgraph-rs/releases). The binary is ~30MB. **macOS / ARM / other platforms** must build from source:

```bash
git clone https://github.com/shuruheel/mindgraph-rs.git
cd mindgraph-rs && cargo build --release
cp target/release/mindgraph-server skills/mindgraph-rs/scripts/
```

---

## Step 2: Start the Server

Add the following to your `~/.openclaw/openclaw.json` under the `"services"` key:

```json
"services": {
  "mindgraph": {
    "command": "bash skills/mindgraph-rs/scripts/start.sh",
    "restart": true
  }
}
```

On first start, `start.sh` generates a random `MINDGRAPH_TOKEN` and saves it to `skills/mindgraph-rs/data/mindgraph.json`. The server binds to `localhost:18790` by default — it is not accessible externally.

### Environment Variables (all optional)
| Variable | Default | Description |
|----------|---------|-------------|
| `MINDGRAPH_PORT` | `18790` | Port to listen on |
| `MINDGRAPH_DB_PATH` | `data/mindgraph.db` | CozoDB database path |
| `MINDGRAPH_TOKEN` | auto-generated | Bearer token for auth |
| `MINDGRAPH_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model name |

---

## Step 2 (Optional): Enable Extraction

> **Privacy note:** Extraction reads your session transcripts and sends excerpts to your LLM provider for summarization. This uses the same provider your agent already talks to. Only enable this if you are comfortable with that.

Add to your `HEARTBEAT.md`:

```bash
# MindGraph extraction — last 60 minutes only
TRANSCRIPT=$(ls -t ~/.openclaw/agents/main/sessions/*.jsonl | head -n 1)
python3 skills/mindgraph-rs/scripts/flatten_transcript.py "$TRANSCRIPT" \
  --since-minutes 60 \
  --output /tmp/mg_flat.txt
node skills/mindgraph-rs/scripts/extract.js /tmp/mg_flat.txt
```

**What `extract.js` does:**
1. Reads `~/.openclaw/openclaw.json` to find your model provider API key
2. If input > 40 KB: sends a summarization request to your LLM provider (Gemini Flash by default)
3. Sends the content (or summary) to your LLM provider for structured node extraction
4. Writes extracted nodes to the local graph — no external storage

**To use a specific provider key:**
```bash
MINDGRAPH_TOKEN=<token> GEMINI_API_KEY=<key> node scripts/extract.js /tmp/mg_flat.txt
```

---

## Step 3 (Optional): Bootstrap Sessions

Add to your `AGENTS.md` so every session starts with graph context:

```markdown
Before every session:
1. mg.retrieve('active_goals')
2. mg.retrieve('pending_approvals')
```

---

## Step 4 (Optional): Nightly Dreaming

> **Note:** This causes your agent to automatically read and reason over recent graph nodes on a schedule. Enable intentionally.

Add to your OpenClaw cron config:

```json
"cron": {
  "mindgraph-dreaming": {
    "schedule": "0 2 * * *",
    "task": "Review the last 24h of MindGraph nodes. Resolve 3-5 open decisions, verify weak claims against new evidence, and propose structural optimizations. Use mg.evolve and mg.deliberate.",
    "model": "anthropic/claude-sonnet-4-6"
  }
}
```

---

## Using Without Extraction (Manual Mode)

The server and client library work fully without extraction. You can write to the graph directly in your agent:

```javascript
const mg = require('./skills/mindgraph-rs/scripts/mindgraph-client.js');
await mg.ingest('Meeting Notes', 'Decided to launch in Q2.', 'observation');
await mg.deliberate({ action: 'open_decision', label: 'Q2 Launch Date', description: 'Confirm exact date.' });
```

This makes no external calls — it talks only to the local server.
