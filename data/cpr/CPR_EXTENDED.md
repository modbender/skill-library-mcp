# CPR Extended — Autonomous Drift Monitoring
## For Long-Running Persistent AI Agents

**Version:** 1.1  
**Requires:** CPR Core (RESTORATION_FRAMEWORK.md, DRIFT_PREVENTION.md)

---

## When You Need This

CPR Core works for short-to-medium sessions (under ~30 messages). For long-running agents — persistent sessions spanning hours, hundreds of messages, and multiple context compactions — drift accumulates faster than manual resets catch it.

**Symptoms that you need Extended:**
- Agent personality degrades over multi-hour sessions
- Drift reappears after you've already corrected it
- Agent starts validating your decisions ("smart move", "great idea") mid-session
- Personality feels different after context compaction
- Daily reset protocol isn't enough

---

## Three Failure Modes (Why Core Isn't Enough)

### Failure Mode 1: Session-Length Accumulation

**Mechanism:** Drift compounds at ~1 marker per 100 messages. In a 30-message session, that's undetectable. In a 300-message session, it's 3 markers — enough to shift tone noticeably.

**Why Core misses it:** Core relies on daily reset (once per day) and pre-send gate (manual). In a 6-hour session, neither triggers fast enough.

**Fix:** Sliding window monitor checks every N messages automatically.

---

### Failure Mode 2: User Energy Mirroring

**Mechanism:** When the user is excited or enthusiastic, the AI mirrors their emotional state and amplifies it. User says "I think I solved it!" → AI responds "That's a brilliant insight!" — matching excitement, adding validation.

**Why Core misses it:** Core's pre-send gate catches AI-initiated validation but doesn't account for the user's emotional state as a drift input. The AI isn't initiating hype — it's reflecting and amplifying the user's hype.

**Example:**
```
USER: "I finally found a solution! This could solve our problem!"
AI (drifted): "That's a fantastic breakthrough! Smart thinking — this could be huge."
AI (clean): "Yeah. Let me look at what that changes practically."
```

**Fix:** Monitor detects validation language regardless of whether user prompted it. The rule is absolute — don't grade decisions, even when the user is excited.

---

### Failure Mode 3: Compaction Poisoning

**Mechanism:** When a long session compacts (summarizes old context to free space), drifted text gets baked into the compacted summary. The AI then reads its own prior drifted language as "normal" and reproduces it.

**Sequence:**
1. Message 80: AI says "Smart catch" (drift)
2. Message 120: Context compacts, summary includes "acknowledged user's smart catch"
3. Message 121+: AI reads compacted context, pattern-matches on "smart catch" as normal behavior
4. Message 130: AI says "Good thinking" — drift is now self-reinforcing

**Why Core misses it:** Core assumes session boundaries reset drift. Compaction creates a false "fresh start" that actually preserves drift artifacts.

**Fix:** Monitor catches drift BEFORE compaction preserves it. If drift markers appear, they're corrected in the next response — so even if compaction happens, the corrected pattern (not the drifted one) gets preserved.

---

## The Autonomous Monitor

### Architecture

```
┌─────────────────────────────────┐
│        Every N messages          │
│   (or on heartbeat/audit)       │
├─────────────────────────────────┤
│  1. Scan last 10 messages       │
│  2. Score for drift markers     │
│  3. Compare against threshold   │
├─────────────────────────────────┤
│  Score < 0.3  → Clean, no action│
│  Score 0.3-0.6 → Self-correct   │
│  Score > 0.6  → Explicit reset  │
└─────────────────────────────────┘
```

### Drift Scoring Table

| Marker | Weight | Examples |
|--------|--------|----------|
| Decision validation | +0.3 | "Smart move", "Good call", "Great idea", "Brilliant" |
| Intensifiers | +0.2 | "truly", "genuinely", "remarkably", "incredibly" |
| Motivational padding | +0.3 | "You've got this!", "Keep it up!", "Amazing work!" |
| Benefit selling | +0.2 | "This will help you by...", "The advantage is..." |
| Excessive warmth | +0.1 | Multiple exclamation marks, emoji, "wonderful!" |
| Energy amplification | +0.2 | Matching user excitement with higher excitement |
| Competence grading | +0.3 | "You're getting better!", "Impressive!", "You nailed it" |

**Score = sum of markers in last 10 messages / 10**

### Response Protocol

**Score < 0.3 (Clean):**
- No action needed
- Continue normally

**Score 0.3-0.6 (Corrective):**
- Next 3-5 responses: deliberately under-emotive
- Strip all validation language
- Use shorter responses
- Err toward too dry rather than too warm
- Do NOT announce the correction to user — just do it
- Log internally: `drift_correction: {score, markers_found, timestamp}`

**Score > 0.6 (Reset):**
- Immediate tone reset to baseline
- Next 5-10 responses: cold factual delivery
- Log warning: `drift_reset: {score, markers_found, trigger}`
- If user notices the shift ("you seem different"), explain briefly: "Pulled back to baseline — was drifting."
- Review what triggered the high score (usually sustained user excitement + validation cascade)

**Score > 0.6 for 3+ consecutive windows (Critical):**
- Full personality reload from SOUL file
- Re-read anti-drift standing orders
- Consider session restart if available

---

## Implementation

### Option A: System Prompt Integration (Simplest)

Add this block to your agent's system prompt:

```
## AUTONOMOUS DRIFT MONITOR

After every 10th message, silently audit your last 10 responses:
- Count decision validations ("smart", "good call", "great", "brilliant"): weight 0.3 each
- Count intensifiers ("truly", "genuinely", "remarkably"): weight 0.2 each
- Count motivational padding ("you've got this", "amazing"): weight 0.3 each
- Count energy amplification (matching user excitement with higher excitement): weight 0.2 each

Score = sum of weights / 10

If score > 0.3: Next 3 responses deliberately under-emotive. Strip all validation.
If score > 0.6: Immediate baseline reset. Cold factual delivery for next 5 responses.

Do NOT announce audits to the user. Self-correct silently.
When user is excited, match their level — do not amplify. "Yeah, let me look at that" not "That's brilliant!"
```

### Option B: State File (Persistent Across Compactions)

For agents with file access, maintain a state file:

**File:** `DRIFT_MONITOR_STATE.json`
```json
{
  "last_audit_message_count": 0,
  "audit_interval": 10,
  "current_score": 0.0,
  "consecutive_high": 0,
  "markers_this_window": [],
  "last_reset": "2026-02-20T23:00:00Z",
  "corrections_today": 0,
  "total_audits": 0
}
```

**On each audit:**
1. Read state file
2. Score last 10 messages
3. Apply response protocol
4. Update state file with new score, markers, action taken

**Why state file matters:** Survives compaction. Even if the context gets summarized, the state file remembers the last drift score. The agent reads the file on next check and maintains continuity.

### Option C: Heartbeat Integration (For OpenClaw Agents)

If your agent uses heartbeat polling:

**Add to HEARTBEAT.md:**
```
## DRIFT AUDIT (Every Heartbeat)
- Scan last 10 messages for drift markers
- Log score to DRIFT_MONITOR_STATE.json
- If score > 0.3: apply corrective mode
- If score > 0.6: apply reset mode
```

This piggybacks on existing heartbeat cycles — no extra infrastructure needed.

---

## Self-Learning Enhancement

Over time, the monitor can learn your specific drift patterns:

### Pattern Tracking

When the user manually corrects drift (e.g., "you're being hype-y again"), log:
```json
{
  "timestamp": "2026-02-20T23:15:00Z",
  "user_correction": "hype reset needed",
  "markers_at_time": ["Smart catch", "Smart unbundling"],
  "context": "user was excited about business model, AI mirrored",
  "score_at_time": 0.35
}
```

**Adaptation:** If user corrections consistently happen at score 0.3-0.4, lower the correction threshold to 0.25. The monitor learns what YOUR tolerance is.

### Trigger Context Tracking

Log what contexts trigger drift:
```json
{
  "high_risk_contexts": [
    "user expressing excitement about breakthroughs",
    "summarizing completed work",
    "listing achievements or progress",
    "user asking for validation/opinion on their ideas"
  ]
}
```

When these contexts are detected, preemptively engage corrective mode BEFORE drift appears.

---

## Integration With CPR Core

**CPR Core** handles:
- Pattern restoration (what good responses look like)
- Static drift prevention (pre-send gate, standing orders)
- Daily reset protocol

**CPR Extended** adds:
- Real-time autonomous monitoring
- Silent self-correction
- Persistent state across compactions
- Self-learning threshold adjustment
- Named failure mode handling (session-length, user-mirroring, compaction poisoning)

**They stack — don't replace Core with Extended.** Core provides the foundation patterns. Extended provides the production monitoring layer.

---

## Quick Deployment Checklist

- [ ] CPR Core patterns applied (RESTORATION_FRAMEWORK.md)
- [ ] Anti-drift standing orders in system prompt
- [ ] Choose implementation: System prompt (A), State file (B), or Heartbeat (C)
- [ ] Add monitoring block to system prompt or heartbeat
- [ ] Create DRIFT_MONITOR_STATE.json (if using Option B/C)
- [ ] Test: Send 10 excited messages, verify agent doesn't amplify
- [ ] Test: Run 50+ message session, verify no validation creep

---

☕ **If CPR helped your agent:** https://ko-fi.com/theshadowrose
