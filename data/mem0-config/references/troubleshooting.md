# openclaw-mem0 Troubleshooting

## SQLITE_CANTOPEN crash loop

**Symptoms:** Gateway restarts on every message. Logs show:
```
[openclaw] Uncaught exception: Error: SQLITE_CANTOPEN: unable to open database file
```
Always occurs right after `[hooks] running before_agent_start (2 handlers, sequential)`.

**Root cause:** `mem0ai`'s `DEFAULT_MEMORY_CONFIG` sets `historyStore.config.historyDbPath = "memory.db"` (relative). When the gateway runs as a macOS LaunchAgent with no `WorkingDirectory` set, `process.cwd()` is `/`. The relative path becomes `/memory.db`, which is unwritable (SIP). The `Memory` constructor always prefers `historyStore` over the top-level `historyDbPath` field, so setting `historyDbPath` alone has no effect (fixed in `@mem0/openclaw-mem0` >= 0.1.3).

**Fix (plugin >= 0.1.3):** Set `historyDbPath` to an absolute writable path:
```json5
"oss": {
  "historyDbPath": "/Users/you/.openclaw/memory/history.db"
}
```

**Workaround (older plugin versions):** Set both `historyDbPath` AND `historyStore` explicitly:
```json5
"oss": {
  "historyDbPath": "/Users/you/.openclaw/memory/history.db",
  "historyStore": {
    "provider": "sqlite",
    "config": { "historyDbPath": "/Users/you/.openclaw/memory/history.db" }
  }
}
```

**Verify fix:**
```bash
ls -la ~/.openclaw/memory/history.db   # should exist after first message
grep "SQLITE_CANTOPEN" ~/.openclaw/logs/gateway.err.log | tail -1  # should be old timestamp
```

---

## Qdrant not reachable

**Symptoms:** `openclaw mem0 stats` hangs or errors; memories not stored.

**Check:**
```bash
curl -s http://localhost:6333/health
```

**Fix:** Start Qdrant:
```bash
docker run -p 6333:6333 qdrant/qdrant
# or if installed via brew:
qdrant
```

---

## Ollama model not found

**Symptoms:** Memory extraction or embedding fails silently.

**Check:**
```bash
ollama list                         # confirm model is pulled
curl -s http://localhost:11434/     # confirm Ollama is running
```

**Fix:**
```bash
ollama pull bge-m3:latest          # embedder model
ollama pull llama3.2               # LLM model
```

---

## Memories not being recalled

**Check 1:** Confirm `autoRecall: true` (default):
```bash
openclaw mem0 stats | grep recall
```

**Check 2:** Check `searchThreshold` — default is `0.5`. Lower it if relevant memories are being missed:
```json5
"config": { "searchThreshold": 0.3 }
```

**Check 3:** Confirm memories exist:
```bash
openclaw mem0 stats       # check total memories count
openclaw mem0 search "topic you expect to be stored"
```

**Check 4:** Look for injection events in gateway log:
```bash
grep "openclaw-mem0: inject" ~/.openclaw/logs/gateway.log | tail -10
```

---

## Memories not being stored (autoCapture)

**Check:** Confirm Qdrant collection exists and has vectors:
```bash
curl -s http://localhost:6333/collections/hoai_an_memories | python3 -m json.tool
```

If the collection doesn't exist, mem0 creates it on first write. If it exists but `vectors_count` is 0, check Qdrant and Ollama connectivity above.

---

## Telegram `allowFrom` warning

**Symptom:**
```
Invalid allowFrom entry: "-1002011075227" - allowFrom/groupAllowFrom authorization
requires numeric Telegram sender IDs only.
```

**Fix:** Replace the group ID string with a proper numeric sender ID in `openclaw.json` under `telegram.allowFrom` / `groupAllowFrom`, or re-run `openclaw onboarding` to resolve it automatically.

---

## Gateway won't start — port already in use

```bash
openclaw gateway stop
# if still stuck:
launchctl bootout gui/$UID/ai.openclaw.gateway
# then:
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/ai.openclaw.gateway.plist
```

---

## Diagnosing live errors

```bash
# Real-time structured log (best for debugging)
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | \
  python3 -c "
import sys, json
for line in sys.stdin:
    try:
        d = json.loads(line.strip())
        lvl = d.get('_meta',{}).get('logLevelName','')
        msg = str(d.get('1', d.get('0','')))
        print(f'[{lvl}] {msg[:200]}')
    except: print(line.strip()[:200])
"

# Error log
tail -f ~/.openclaw/logs/gateway.err.log

# Filter for mem0 events only
grep "openclaw-mem0\|SQLITE\|mem0" /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | tail -20
```
