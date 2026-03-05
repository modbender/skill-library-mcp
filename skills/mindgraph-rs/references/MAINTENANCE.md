# MindGraph Automated Maintenance

To keep the MindGraph healthy, updated, and "dreaming," add these tasks to your OpenClaw automated flows.

## 1. Proactive Extraction (HEARTBEAT.md)
Add this to your heartbeat every 1-2 hours to ensure new conversational data is indexed.

```bash
# MindGraph: Flatten the latest JSONL session and extract new nodes
# Replaces 'your-session.jsonl' with the current live transcript path
python3 scripts/flatten_transcript.py ../../agents/main/sessions/current.jsonl /tmp/flat.txt
node scripts/extract.js /tmp/flat.txt
```

## 2. Nightly Dreaming (Cron)
Configure a nightly cron (e.g., 2:00 AM) to run the **Dreamer**. This triggers the agent to review the last 24 hours, identify weak claims, resolve contradictions, and propose graph evolutions.

```json
"cron": {
  "mindgraph-dreaming": {
    "schedule": "0 2 * * *",
    "task": "Review the last 24h of MindGraph nodes. Resolve 3-5 open decisions, verify weak claims against new evidence, and propose structural optimizations. Use mg.evolve and mg.deliberate.",
    "model": "anthropic/claude-sonnet-4-6"
  }
}
```

## 3. Server Watchdog (HEARTBEAT.md)
Ensures the server is always up and auto-restarts if frozen.

```bash
MG_PORT=18790
if ! curl -s http://127.0.0.1:$MG_PORT/health > /dev/null; then
  echo "🚨 MindGraph server down. Restarting..."
  bash scripts/start.sh &
fi
```
