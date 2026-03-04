# Release Notes: nova-act-usability v2.0.0

## Version Comparison: v1.1.0 → v2.0.0

**Release Date:** 2026-02-06

---

## Summary of Changes

| Metric | v1.1.0 | v2.0.0 | Change |
|--------|--------|--------|--------|
| Total Lines | ~2,000 | ~4,700 | +135% |
| Script Files | 7 | 10 | +3 new |
| SKILL.md | 364 lines | 908 lines | +149% |

---

## New Files

| File | Purpose |
|------|---------|
| `CHANGELOG.md` | Complete version history with architectural decisions |
| `setup.sh` | One-command dependency installation |
| `setup.py` | Python-based setup with Playwright browser install |
| `scripts/response_interpreter.py` | Structures raw responses for agent analysis |
| `scripts/status_reporter.py` | 60-second progress updates during long tests |

---

## Major Architectural Changes

### 1. Agent-Driven Interpretation (Breaking Change)

**Before (v1.x):**
- Script attempted hardcoded regex interpretation
- `overall_success` always set incorrectly
- Reports showed wrong pass/fail status

**After (v2.0):**
```
Script collects raw data → Agent interprets → Agent generates report
```

- Script outputs `needs_agent_analysis: true`
- Agent reads JSON, interprets each `raw_response`
- Agent sets `goal_achieved` and `overall_success`
- No hardcoded patterns, no extra API calls

### 2. Three-Phase Execution Flow

| Phase | Component | Responsibility |
|-------|-----------|----------------|
| Collect | `run_adaptive_test.py` | Browser automation, raw data capture |
| Interpret | Agent (Claude) | Contextual response interpretation |
| Report | `enhanced_report_generator.py` | HTML with interpreted results |

### 3. Simplified Nova Act Prompts

**Before:** "As a beginner user, can you easily find the documentation?"  
**After:** "Click the Documentation link in the navigation"

Nova Act is a browser automation tool, not a reasoning engine. The agent handles all reasoning.

---

## File-by-File Changes

### `run_adaptive_test.py` (+614 lines)
- Removed hardcoded `interpret_step_success()` function
- Added graceful shutdown with partial report generation
- Added signal handlers (SIGTERM/SIGINT)
- Added 60-second status updates via `status_reporter.py`
- Supports JSON persona files from agent
- AI-powered persona inference fallback
- Workflow detection (booking, checkout, posting)
- Safety stops before material impact actions

### `enhanced_report_generator.py` (+278 lines)
- Added `goal_achieved` field support
- Added "⏳ PENDING" status for un-interpreted tests
- Added "Awaiting agent interpretation" step warnings
- Fixed recording numbering: globally sequential (not per-test)
- Dynamic site category detection (sports, ecommerce, news, etc.)
- WSL-compatible file paths for trace links

### `SKILL.md` (+544 lines)
- Added v2.0.0 badge and "What's New" section
- Complete 4-phase workflow documentation
- Agent interpretation code templates
- Mandatory analysis workflow section
- Timeout guidance (30 minutes recommended)
- Persona generation tips by industry

### `dynamic_exploration.py` (+398 lines)
- Removed persona-specific prompt generation
- Generic fallback generates direct browser commands
- `adapt_prompt_for_persona()` returns prompts unchanged
- Workflow-aware test strategy generation

### `safe_nova_wrapper.py` (+116 lines)
- Added `ActResult`/`QueryResult` dataclasses
- Observation tracking in results
- Session health checks
- Timeout handling improvements

### `references/nova-act-cookbook.md` (+264 lines)
- Added "Principle #0: Nova Act is NOT a Reasoning Engine"
- Clear examples of wrong vs right prompts
- Workflow testing patterns
- Safety guardrail documentation

### `skill.json` (+4 lines)
- Version: 1.1.0 → 2.0.0
- Added `postInstall` configuration for setup.sh
- Updated description with workflow testing mention

---

## New Data Fields

| Field | Set By | Description |
|-------|--------|-------------|
| `raw_response` | Script | Actual Nova Act response text |
| `api_success` | Script | Did the API call complete? |
| `needs_agent_analysis` | Script | Always `true` |
| `goal_achieved` | Agent | Did response indicate success? |
| `goals_achieved` | Agent | Count of successful steps |
| `overall_success` | Agent | Test passed (≥50% goals) |

---

## Report Status Indicators

| Status | Meaning |
|--------|---------|
| ✅ PASSED | Agent interpreted, goals achieved |
| ❌ FAILED | Agent interpreted, goals not achieved |
| ⏳ PENDING | Awaiting agent interpretation |

---

## Breaking Changes

1. **Agent must interpret results** - Script no longer sets `overall_success`
2. **Report generation is manual** - Agent must call `generate_enhanced_report()`
3. **New required workflow** - 4-phase execution (setup → collect → interpret → report)

---

## Migration Guide

### From v1.x to v2.0

1. **Update skill files** - Copy all new files
2. **Run setup.sh** - Install dependencies
3. **Update workflow** - Add interpretation phase after running tests:

```python
# After test script completes:
with open('test_results_adaptive.json', 'r') as f:
    results = json.load(f)

# Agent interprets each step
for test in results:
    for step in test['steps']:
        raw = step.get('raw_response', '')
        # Interpret: "No" → False, actual content → True
        step['goal_achieved'] = ...  # Agent decides
    
    # Set overall success
    goals = sum(1 for s in test['steps'] if s.get('goal_achieved'))
    test['overall_success'] = goals / len(test['steps']) >= 0.5

# Generate report
from enhanced_report_generator import generate_enhanced_report
generate_enhanced_report(page_analysis, results, traces)
```

---

## Contributors

- Adi (author)
- Claude/OpenClaw (AI orchestration)
