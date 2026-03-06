# Token Saver v3.0.0 — Upgrade Plan

## Overview
Upgrade from v2.0.1 to v3.0.0 with intelligent model awareness, dynamic thresholds, and robust detection.

## Current v2 Limitations
1. **Hardcoded model pricing** — no context window info, can't calculate % usage
2. **Fixed compaction presets** — 80K/120K/160K regardless of model's actual limits
3. **Fragile model detection** — checks env vars + config, no runtime fallback
4. **No model switching awareness** — doesn't know if user can afford suggested models

## v3 Features

### 1. Model Registry (NEW)
**File:** `models.json` — Comprehensive model data including context windows

```json
{
  "claude-opus-4-5": { "context": 200000, "input": 0.015, "output": 0.075, "tier": "premium" },
  "claude-sonnet-4": { "context": 200000, "input": 0.003, "output": 0.015, "tier": "standard" },
  "claude-haiku-3.5": { "context": 200000, "input": 0.0008, "output": 0.004, "tier": "budget" },
  "gemini-2.0-flash": { "context": 1000000, "input": 0, "output": 0, "tier": "free" },
  "gemini-2.5-pro": { "context": 1000000, "input": 0.00125, "output": 0.005, "tier": "standard" },
  "gpt-4o": { "context": 128000, "input": 0.0025, "output": 0.01, "tier": "standard" },
  "gpt-4o-mini": { "context": 128000, "input": 0.00015, "output": 0.0006, "tier": "budget" },
  "deepseek-v3": { "context": 64000, "input": 0.00014, "output": 0.00028, "tier": "budget" }
}
```

**Why:** Different models have different context limits. GPT-4o has 128K, Gemini has 1M, Claude has 200K. Compaction should adapt.

### 2. Dynamic Presets (% Based)
**Current:** Fixed values (80K, 120K, 160K)
**New:** Percentage of model's context window

| Preset | % of Context | Claude (200K) | GPT-4o (128K) | Gemini (1M) |
|--------|--------------|---------------|---------------|-------------|
| Aggressive | 40% | 80K | 51K | 400K |
| Balanced | 60% | 120K | 77K | 600K |
| Conservative | 80% | 160K | 102K | 800K |
| Off | 95% | 190K | 122K | 950K |

**Benefits:**
- Same UX experience regardless of model
- No memory loss surprises when switching models
- Proper utilization of Gemini's huge context

### 3. Auto-Detect + Fallback Chain
**Detection priority:**
1. Runtime injection (OpenClaw passes model to skill via env/arg)
2. Environment variables (`OPENCLAW_MODEL`, `DEFAULT_MODEL`)
3. Config file parsing (`~/.openclaw/openclaw.json`)
4. AGENTS.md/TOOLS.md inference (look for model mentions)
5. **Fallback: Claude Sonnet 4** (most common, safe default)

**Runtime injection hook:**
```javascript
// If OpenClaw passes model info, use it
const runtimeModel = process.env.SKILL_MODEL || args.find(a => a.startsWith('--model='));
```

### 4. Improved Dashboard
**Current issues:**
- Model suggestions show even when not applicable
- Savings estimates are rough
- No indication of current context usage %

**v3 improvements:**
- Show current context usage as % of model limit
- Context-aware savings (different models = different costs)
- Visual progress bar: `[████████░░░░░░░░░░░░] 42% (84K/200K)`
- Model-specific recommendations

### 5. Additional Improvements

#### 5a. Smart Compression Bypass
Skip compression on already-optimized files (check for token-saver marker):
```javascript
// If file contains marker, it's already compressed
if (content.includes('## 📝 Token Saver — Persistent Mode')) {
  return { skipped: true, reason: 'already-optimized' };
}
```

#### 5b. Cost Calculator Precision
Use actual model pricing from registry, not hardcoded estimates:
```javascript
const cost = (tokens * registry[model].input / 1000) * txPerDay * 30;
```

#### 5c. Export Config Command
New command: `/optimize export` — Generate OpenClaw config snippet:
```yaml
agents:
  defaults:
    context:
      compactionThreshold: 0.6
    model:
      primary: anthropic/claude-sonnet-4
```

## Implementation Plan

### Phase 1: Model Registry
- [ ] Create `models.json` with comprehensive model data
- [ ] Update `analyzer.js` to load/use registry
- [ ] Add context window info to model audit output

### Phase 2: Dynamic Presets
- [ ] Modify `showCompaction()` to calculate % of detected model's context
- [ ] Update preset display to show model-specific values
- [ ] Persist model detection for consistent experience

### Phase 3: Detection Chain
- [ ] Implement fallback chain in `detectCurrentModels()`
- [ ] Add runtime model injection support
- [ ] Log detection source for transparency

### Phase 4: Polish
- [ ] Update dashboard with context usage %
- [ ] Add visual progress bar
- [ ] Update SKILL.md documentation
- [ ] Bump version to 3.0.0

## Files to Modify
| File | Changes |
|------|---------|
| `scripts/models.json` | NEW — Model registry |
| `scripts/analyzer.js` | Load registry, context-aware analysis |
| `scripts/optimizer.js` | Dynamic presets, improved dashboard |
| `scripts/compressor.js` | Smart bypass for already-optimized |
| `SKILL.md` | Update documentation |
| `package.json` | Version bump |

## Risk Assessment
| Risk | Mitigation |
|------|------------|
| Model detection fails | Fallback to Claude Sonnet 4 (safe default) |
| Registry out of date | Keep registry easily updatable, add version |
| Breaking existing configs | Maintain backward compat with fixed presets |
| Model name variations | Normalize aliases (opus-4-5, opus-4.5, anthropic/claude-opus-4-5 → same) |
| Registry corruption | Inline defaults + external file, graceful degradation |
| Gemini context varies | Note: free tier may be 32K, paid 1M — detect tier if possible |

## Success Criteria
1. ✅ Model registry with context windows
2. ✅ Presets calculate dynamically based on model
3. ✅ Robust detection with clear fallback
4. ✅ Dashboard shows context % usage
5. ✅ All existing v2 functionality preserved
6. ✅ Tests pass on Claude, GPT-4o, and Gemini scenarios

## Estimated Effort
~2-3 hours implementation + testing

---
*Plan created: 2026-02-06*
*Status: READY FOR IMPLEMENTATION*
