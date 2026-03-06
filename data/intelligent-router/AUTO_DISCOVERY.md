# Intelligent Router - Auto-Discovery Feature

## What It Does

Automatically discovers and validates working models from all OpenClaw providers, then updates the intelligent-router config with only the models that actually work.

## Why We Built This

**Problem:** Manual model maintenance breaks when:
- OAuth tokens expire (e.g., Gemini 3 Pro just stopped working)
- New models release (Gemini 4, Claude 5, etc.)
- Provider outages
- API key rotations

**Solution:** Auto-discovery scans providers hourly, tests each model, and removes broken ones.

---

## Quick Start

```bash
# One-time scan (read-only)
python3 skills/intelligent-router/scripts/discover_models.py

# Auto-update config with working models
python3 skills/intelligent-router/scripts/discover_models.py --auto-update

# Set up hourly auto-refresh
bash skills/intelligent-router/scripts/setup_discovery_cron.sh
```

---

## How It Works

### 1. Provider Scanning

Reads `~/.openclaw/openclaw.json` to find all configured providers:

```
models.providers:
  - anthropic (OAuth)
  - anthropic-proxy-1
  - anthropic-proxy-2
  - nvidia-nim
  - ollama
  - ollama-gpu-server
  ... (all providers)
```

### 2. Model Testing

For each model, sends a minimal test prompt:

```
Test prompt: "echo: hello"
Expected: "hello" (or similar)
Timeout: 30 seconds
```

Measures:
- **Availability:** Did it respond?
- **Latency:** How fast?
- **Error:** What went wrong?

### 3. Tier Classification

Auto-assigns tiers based on model metadata:

| Tier | Criteria |
|------|----------|
| 🟢 SIMPLE | Cost < $0.50/M, any capabilities |
| 🟡 MEDIUM | Cost $0.50-$2/M, has code/reasoning |
| 🟠 COMPLEX | Cost $2-$5/M, agentic + multi-tool |
| 🔵 REASONING | Has reasoning flag, any cost |
| 🔴 CRITICAL | Cost > $5/M, top-tier provider |

### 4. Config Update

Updates `skills/intelligent-router/config.json`:

```json
{
  "models": [
    {
      "id": "anthropic/claude-sonnet-4-6",
      "tier": "COMPLEX",
      "available": true,
      "last_check": "2026-02-19T21:00:00",
      "latency": 1.2
    }
  ],
  "last_discovery": "2026-02-19T21:00:00"
}
```

**Preserves:**
- Tier routing rules (SIMPLE/MEDIUM/etc.)
- Pinned models (manual overrides)
- Fallback chains

**Removes:**
- Unavailable models (e.g., broken OAuth)
- Models that timeout

---

## Output Files

### discovered-models.json

Full scan results with per-model status:

```json
{
  "scan_timestamp": "2026-02-19T21:00:00",
  "total_models": 25,
  "available_models": 23,
  "unavailable_models": 2,
  "providers": {
    "anthropic": {
      "name": "anthropic",
      "available": 2,
      "unavailable": 0,
      "models": [
        {
          "id": "anthropic/claude-sonnet-4-6",
          "name": "Claude Sonnet 4.6 (OAuth)",
          "available": true,
          "latency": 1.2,
          "tier": "COMPLEX",
          "capabilities": ["text", "code", "reasoning"],
          "cost": {"input": 3.0, "output": 15.0}
        }
      ]
    }
  }
}
```

### config.json (updated)

Router config with only working models:

```json
{
  "models": [
    // Only available models included
    // Unavailable models removed
  ],
  "routing_rules": {
    "COMPLEX": {
      "primary": "anthropic/claude-sonnet-4-6",
      "fallback_chain": [
        "anthropic-proxy-1/claude-sonnet-4-6",
        "nvidia-nim/nvidia/llama-3.1-nemotron-ultra-253b-v1"
      ]
    }
  },
  "last_discovery": "2026-02-19T21:00:00"
}
```

---

## Cron Integration

### Hourly Auto-Refresh

```bash
bash skills/intelligent-router/scripts/setup_discovery_cron.sh
```

Creates cron job:

```json
{
  "name": "Model Discovery Refresh",
  "schedule": {
    "kind": "every",
    "everyMs": 3600000  // 1 hour
  },
  "payload": {
    "kind": "systemEvent",
    "text": "Run: bash skills/intelligent-router/scripts/auto_refresh_models.sh",
    "model": "ollama/glm-4.7-flash"  // Free local model
  },
  "enabled": true
}
```

### On Model Failure

If discovery finds unavailable models:

1. Updates config (removes broken models)
2. Logs to `discovered-models.json`
3. Sends alert to main session:
   ```
   ⚠️ Model discovery alert: 2 model(s) failed health check
   - google-gemini-cli/gemini-3-pro-preview: OAuth token expired
   - anthropic-proxy-5/deepseek-chat: Connection timeout
   ```

---

## Advanced Usage

### Test Specific Tier

```bash
python3 skills/intelligent-router/scripts/discover_models.py --tier COMPLEX
```

Only tests models currently assigned to COMPLEX tier.

### Custom Output Path

```bash
python3 skills/intelligent-router/scripts/discover_models.py --output /tmp/my-scan.json
```

### Manual Model Pinning

To preserve a model even if it fails discovery:

```json
{
  "id": "experimental-model",
  "tier": "COMPLEX",
  "pinned": true,  // Never remove during auto-update
  "notes": "Testing new model, may be flaky"
}
```

---

## Performance

### Scan Duration

- **Small setups** (10 models): ~10-20 seconds
- **Large setups** (50+ models): ~30-60 seconds

### API Costs

Test prompts use minimal tokens:

- **Cost per scan:** ~$0.001-0.01 (1-10 tokens per model)
- **Hourly scans:** ~$0.03-0.30 per day
- **Worth it:** Eliminates manual maintenance

### Resource Usage

- **CPU:** Low (subprocess calls to `openclaw models test`)
- **Memory:** Minimal (JSON processing)
- **Network:** 1 HTTP request per model

---

## Troubleshooting

### Discovery Shows All Models Unavailable

**Cause:** `openclaw models test` command not working

**Fix:**
```bash
# Test manually
openclaw models test --provider anthropic --model anthropic/claude-sonnet-4-6 --prompt "hello"

# Check CLI version
openclaw --version

# Update OpenClaw
openclaw gateway update.run
```

### Discovery Timeout

**Cause:** Provider slow or unreachable

**Fix:** Increase timeout in `discover_models.py`:
```python
timeout=60  # Change from 30 to 60 seconds
```

### Config Not Updating

**Cause:** File permissions or path issues

**Fix:**
```bash
# Check file exists
ls -la skills/intelligent-router/config.json

# Check write permissions
chmod 664 skills/intelligent-router/config.json

# Manual update
python3 skills/intelligent-router/scripts/discover_models.py --auto-update
```

---

## Future Enhancements

**Planned features:**

1. **Smart tier assignment:** Use LLM to classify complex models
2. **Performance tracking:** Track model latency over time
3. **Cost optimization:** Auto-switch to cheaper models based on usage patterns
4. **A/B testing:** Compare models on same task, pick best performer
5. **Provider health:** Track provider uptime, auto-failover

**Contributions welcome!**

---

## Summary

✅ **Self-healing:** Removes broken models automatically
✅ **Zero maintenance:** No manual model list updates
✅ **Cost-effective:** Always uses cheapest working model per tier
✅ **Comprehensive:** Tests every provider, every model
✅ **Fast:** 10-60 seconds for full scan
✅ **Safe:** Preserves pinned models, tier rules

**Recommendation:** Enable hourly auto-refresh for production setups.
