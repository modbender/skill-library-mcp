# 🧠 HEARTBEAT.md for Skill: NeverForget (Ultimate Memory)
**Version:** 1.0.4
**Description:** This HEARTBEAT.md acts as the system's "Self-Check" monitor to ensure memory integrity, loop protection, and disk health.

---
## 🧠 Local Memory Pulse (NeverForget)

| Component | Status | Check Command |
| :--- | :--- | :--- |
| **Local Memory** | {{local_memory_status}} | `openclaw memory status` |
| **Vector Index** | {{chunk_count}} Chunks | `openclaw memory status --deep` |
| **Memory Sync** | {{last_index_time}} | `openclaw memory status` |
| **Disk Health** | {{disk_usage}} | `df -h / | awk 'NR==2 {print $5}'` |

### 🛠 Memory Recovery Logic

1. **If Index is 0:** The local vector store is empty. Trigger `openclaw memory index` immediately to crawl the defined workspace and sandboxed directories.

2. **If Paths are MISSING:** Confirm that the absolute paths in your `ULTIMATEMEMORY.md` match your disk. Do not use symlinks; use direct path indexing.

3. **Loop Protection Check:** If the gateway crashes during indexing, check `openclaw config get agents.defaults.memorySearch.exclude`. Ensure `**/.openclaw/memory/**` is listed to prevent the AI from indexing its own database.

4. **Disk Alert (>90%):** If disk usage exceeds 90%, do not run `openclaw memory index`. Manually prune large log files in `~/.openclaw/logs` before resuming.

5. **Provider Check:** If provider is not "local", run `openclaw config set agents.defaults.memorySearch.provider local` and restart the gateway.