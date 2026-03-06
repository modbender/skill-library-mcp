# CHAOS Memory - Installation Notes

## Quick Install

```bash
# Via ClawHub (recommended)
clawdhub install chaos-memory

# Via curl
curl -fsSL https://raw.githubusercontent.com/hargabyte/Chaos-mind/main/install.sh | bash

# Manual
git clone https://github.com/hargabyte/Chaos-mind ~/.chaos/chaos-memory
cd ~/.chaos/chaos-memory && ./install.sh
```

## Post-Install Setup

### 1. Start Database
```bash
cd ~/.chaos/db
dolt sql-server --port 3307 &
```

### 2. Verify Database
```bash
mysql -h 127.0.0.1 -P 3307 -u root -e "SHOW DATABASES;"
# Should show: chaos-local or your database name
```

### 3. Pull AI Model
```bash
ollama pull qwen3:1.7b
```

### 4. Configure Auto-Capture Paths
Edit `~/.chaos/config/consolidator.yaml`:

```yaml
auto_capture:
  sources:
    # Add your specific paths here
    - ~/.openclaw-mattermost/agents/*/sessions/*.jsonl
    - ~/.clawdbot-mattermost/agents/*/sessions/*.jsonl
    - ~/your-workspace/memory/*.md
```

### 5. Test One-Shot Extraction
```bash
chaos-consolidator --config ~/.chaos/config/consolidator.yaml --auto-capture --once
```

Watch the logs:
```bash
tail -f ~/.chaos/consolidator.log
```

**Expected output:**
```
📂 Found 302 files matching ...
📖 Processing transcript: ...
✅ Extracted 10 memories from <file>
```

**Should NOT see:**
```
⚠️ Failed to store memory: Error 1105: value ... is not valid for this Enum
```

### 6. Set Up Systemd Service (Optional)
```bash
~/.chaos/bin/setup-service.sh
sudo systemctl start chaos-consolidator
sudo systemctl status chaos-consolidator
```

## Database Details

### Local Development (Port 3307)
- **Database:** `chaos-local` or custom name
- **Schema:** Flexible VARCHAR categories
- **Categories:** Any string (decision, research, core, semantic, etc.)
- **Purpose:** Team memory capture

### SaaS Production (Port 3306)
- **Database:** `chaos-memory`
- **Schema:** Strict enum categories
- **Categories:** Only `core`, `semantic`, `working`, `episodic`
- **Purpose:** Multi-tenant SaaS product

**Default for auto-capture: Port 3307 (local)**

## Troubleshooting

### "Error 1105: value ... is not valid for this Enum"
**Cause:** Writing to wrong database (SaaS port 3306 instead of local 3307)  
**Fix:** Check `consolidator.yaml`:
```yaml
chaos:
  mcp:
    env:
      CHAOS_DB_PORT: "3307"  # Must be 3307 for local
```

### "Database not found"
**Cause:** Dolt server not running  
**Fix:**
```bash
cd ~/.chaos/db
dolt sql-server --port 3307 &
```

### "Ollama not ready"
**Cause:** Ollama not running or model not pulled  
**Fix:**
```bash
# Start Ollama
ollama serve &

# Pull model
ollama pull qwen3:1.7b
```

### "No files found"
**Cause:** Auto-capture paths don't match your setup  
**Fix:** Edit `~/.chaos/config/consolidator.yaml` and customize `auto_capture.sources`

## Verification

### Check Memory Count
```bash
cd ~/.chaos/db
dolt sql -q "SELECT COUNT(*) FROM memories;"
```

### View Recent Memories
```bash
dolt sql -q "SELECT id, SUBSTRING(content,1,100), category FROM memories ORDER BY created_at DESC LIMIT 10;"
```

### Service Status
```bash
systemctl status chaos-consolidator
sudo journalctl -u chaos-consolidator -n 50
```

## Support

- **Issues:** https://github.com/hargabyte/Chaos-mind/issues
- **Docs:** https://github.com/hargabyte/Chaos-mind#readme
- **Email:** support@hargabyte.com

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-06
