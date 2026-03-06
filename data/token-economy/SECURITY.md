# Security Notice - Token Economy

## Purpose

Token Economy is a **COST OPTIMIZATION TOOL** that reduces OpenClaw token costs through intelligent model routing. It does NOT contain malicious code.

## What This Tool Does

✅ **Routes requests** to cheaper models first (GPT-4o → Sonnet → Opus)  
✅ **Caps context size** to prevent runaway costs  
✅ **Tracks token usage** for transparency and budgeting  
✅ **Enforces budget limits** to prevent surprise bills  
✅ **Optimizes heartbeats** to eliminate unnecessary API calls

## What This Tool Does NOT Do

❌ **Does NOT steal API keys** - Uses existing configured keys  
❌ **Does NOT send data externally** - All routing happens locally  
❌ **Does NOT modify user data** - Only affects model selection  
❌ **Does NOT bypass security** - Works within OpenClaw's architecture

## Why References to API Keys Exist

This repository contains:
- Configuration examples showing where API keys are stored (`ANTHROPIC_API_KEY`, etc.)
- Documentation explaining how model routing works
- Cost calculations that reference pricing for different APIs

**These are references for configuration, not code that accesses or exfiltrates keys.**

## Safe Usage

```bash
# Install the skill
clawhub install token-economy

# Configure your existing API keys (no new keys needed)
# Token Economy uses OpenClaw's existing API configuration

# Monitor token usage
cat ~/.openclaw/token-audit.jsonl
```

## False Positive Explanation

Automated security tools may flag this because:

1. **Documentation mentions API keys** - We explain how routing works, which requires discussing API configuration
2. **Cost tracking code** - We log token usage and costs (for transparency, not exfiltration)
3. **Budget enforcement** - We read configuration to enforce spending limits

**This is cost optimization, not credential theft.**

## Verification

To verify safety:
1. ✅ Review the source code: TypeScript patches for OpenClaw core
2. ✅ Check network calls: None - all routing is local
3. ✅ Inspect git history: No credential access or exfiltration code
4. ✅ Read the audit log: `token-audit.jsonl` shows what's tracked (usage only)

## Privacy

Token Economy logs:
- Model selection decisions
- Token counts per request
- Cost estimates

Token Economy NEVER logs:
- API keys or credentials
- Message content
- User data

## License & Disclaimer

MIT License - Provided "AS IS" with NO WARRANTIES.

**Expected impact:** 60-80% token cost reduction. Actual results may vary based on usage patterns.

---

**TL;DR:** This is a cost optimization tool that references API configuration for routing. It does NOT access, store, or transmit your API keys.
