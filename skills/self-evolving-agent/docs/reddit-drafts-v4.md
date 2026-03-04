# Reddit Post Drafts — Self-Evolving Agent v4.0

> Status: DRAFT (ready for review)
> Target: r/AI_Agents (primary), r/ClaudeAI (secondary)
> Best posting window: Tuesday–Thursday, 9–11 AM EST
> Tone: honest builder, technical, slightly self-deprecating
> Link: https://github.com/Ramsbaby/self-evolving-agent

---

## 📌 Post 1: r/AI_Agents

**Title:** I built an AI that watches itself fail, then proposes its own fixes — with a closed feedback loop that measures if the fixes actually worked

---

**Body:**

TL;DR: My AI found 119 consecutive exec retries, 405 retry events in 7 days, and 18 repeated heartbeat errors — all on its own. v4.0 now measures whether the fixes it proposes actually work. It's 6 shell scripts + one Claude call per week. Not magic.

---

**Why I built this:**

Same mistake. Different week. For months.

```
Monday:   "Stop retrying the same command when it fails"
AI:       "Understood, I'll stop immediately."
Next Mon: 119 consecutive retries on the same broken command.
```

Corrections die with the session. The fix is permanent rules in AGENTS.md. But writing good rules requires you to notice the pattern, remember to document it, and phrase it clearly enough that it actually sticks.

I automated that loop. Imperfectly. But here's what the numbers looked like.

---

**The data that made this worth building:**

When I ran the v3 analysis on a week of real logs, it found:

```
📊 exec retry analysis (7-day window):
   Sessions with 3+ consecutive exec retries: 221
   Maximum consecutive retries in one session: 119
   Total retry events: 405
   Repeated heartbeat errors (same error, 7 days): 18×
```

119 consecutive retries. Same command. Same failure. The agent was stuck in a loop and just... kept going. I had no idea — I wasn't watching every session. The tool found it automatically and proposed this:

```diff
+ ## ⚡ exec Consecutive Retry Limit
+
+ If the same exec command fails 3+ times in a row:
+ 1. Report the error immediately — don't retry silently
+ 2. Second attempt must use a different approach
+ 3. Third failure = STOP. Ask for manual confirmation.
```

I approved it. Loops stopped. But I had no way to know *if it actually helped* until v4.0.

---

**What's new in v4.0: the feedback loop closes**

The thing that was missing in every version before this: **effect measurement**.

You can find patterns. You can propose rules. You can even apply them. But did the rule *work*? In v3, you'd have to scroll logs manually and guess. That's not a feedback loop — it's a suggestion box.

v4.0 adds a 4-stage pipeline:

```
Stage 1: COLLECT
   Shell scripts aggregate 7 days of logs
   → exec retries, error patterns, complaint signals, cron failures

Stage 2: ANALYZE  
   Heuristic analysis on the aggregated data
   → structural pattern matching with context awareness
   → frustration signals, exec loops, rule violations scored

Stage 3: BENCHMARK
   Compares current week vs. previous week for each active rule
   → "Last week: 405 retry events. This week: 12."
   → Flags rules that aren't working (pattern persists post-approval)

Stage 4: SYNTHESIZE
   Combines new proposals + effectiveness data into one weekly report
   → Shows you what's improving, what's regressing, what's new
```

Stage 3 is the one that matters. No other tool in this space actually tracks whether proposals worked. They find problems and make suggestions. The loop stays open.

---

**Honest architecture (it's not AGI, it's grep with opinions):**

```
cron (Sunday 22:00)
  ↓
collect.sh     → finds exec retries, heartbeat errors, cron failures
analyze.sh     → keyword scan on complaint patterns  
benchmark.sh   → diffs this week vs last week per active rule
claude API     → writes the proposal in diff format (1 call, ~$0.03)
Discord DM     → you approve or reject
```

Six shell scripts. One Claude API call. The "AI" part is in the proposal drafting, not the detection. The detection is grep.

Cost: **< $0.05/week** at current Claude pricing.

**AGENTS.md is never modified without explicit human approval.** That's a hard constraint, not a feature. The whole value of the tool is catching patterns you missed — you still make the call on whether the proposed fix makes sense.

---

**What it gets wrong (still):**

1. **False positives on keyword matching** — "again" appears in "stop doing that again" and "let me try again." Complaint counts are inflated ~40% when assistant text is included in the scan. The fix: `scan_user_only: true` in config.

2. **Misses semantic patterns** — My biggest real frustration ("stop asking for confirmation and just do it") never appeared in default keywords. You have to add your own patterns. The tool is only as good as your keyword list.

3. **Benchmark needs at least 2 weeks of data** — If you install today, Stage 3 does nothing until next week. That's not a bug, it's math.

4. **Generic proposals on quiet weeks** — Low signal = vague output. "Consider improving memory management" is not a useful proposal.

---

**vs. the alternatives I know of:**

- **Manual log review:** You'll do it once and then stop. I did.
- **self-improving-agent:** Session-level scoring (microscope). Complementary — its data feeds Stage 1 here.
- **self-evolving-agent v4:** System-level trends across 7+ days (telescope). Finds what session-level tools can't see.

---

**Install:**

```bash
# GitHub
git clone https://github.com/Ramsbaby/self-evolving-agent
bash scripts/register-cron.sh
```

Open source, MIT. The full pipeline is ~1,800 lines of core shell + analysis — readable in an hour. Read it before you run it. It touches your logs.

If your logs are in English, the default complaint keywords (tuned for Korean) will be mostly useless. Add your own to `config.yaml`:

```yaml
complaint_patterns:
  - "you forgot"
  - "again?"
  - "same mistake"
  - "stop doing that"
  - "how many times"
  - "you already"
  - "wrong again"
```

---

**Honest assessment:**

The exec retry detection and heartbeat error tracking are worth installing for alone. Finding 405 retry events in one week — events I had zero visibility into — was the moment this stopped being a toy project.

The benchmark stage (Stage 3) is new and will need tuning. The signal is real; the thresholds are my best guesses. If you run it and find the sensitivity is off, open an issue.

GitHub: https://github.com/Ramsbaby/self-evolving-agent

Questions welcome, especially about tuning keyword patterns for non-Korean setups.

---

## 📝 Post 2: r/ClaudeAI

**Title:** Automated AGENTS.md improvement loop — my AI reviews its own chat logs weekly and suggests rule changes

---

**Body:**

Since Karpathy's CLAUDE.md post went viral, a lot of people started thinking seriously about rule files for their Claude setups. The problem nobody talks about: how do you actually *improve* those rules over time?

You notice a problem → you update AGENTS.md → it works for a while → you forget you ever had that problem. Or: you notice a problem → you forget to update anything → same problem next month.

I built an automated version of that improvement cycle. Here's what it found.

---

**The finding that made it worth building:**

Weekly cron. Scans my chat logs. Found this:

```
exec retry events (7-day window): 405
Maximum consecutive retries in one session: 119
Repeated heartbeat errors (same error, 7 days): 18×
```

119 consecutive retries. Same failed command. Claude looping. I had no idea it was happening — I wasn't watching every session in real-time. The tool caught it automatically and proposed a specific rule:

```diff
+ ## exec Retry Limit
+
+ Same command fails 3× in a row → STOP.
+ Report to user. Ask for different approach.
+ Do NOT retry silently.
```

Applied it. Loops stopped.

But here's the part that was missing until v4.0: **how do I know the rule actually helped?**

---

**v4.0: the loop actually closes**

The old workflow: find pattern → propose rule → apply rule → hope.

The v4.0 workflow: find pattern → propose rule → apply rule → **measure effect next week**.

Stage 3 of the pipeline does a before/after comparison for every active rule. Last week's 405 exec retries vs. this week's 12. If the count went down, the rule is working. If the pattern persists, it flags the rule for revision.

No other tool in this space does this. They find problems. They suggest fixes. They don't close the loop.

---

**What it actually looks like (AGENTS.md angle):**

Every week you get a Discord message like this:

```
📋 AGENTS.md Weekly Review — 2026-02-16

🔴 NEW PROPOSALS (2):
   1. exec retry limit [evidence: 405 events, max 119 consecutive]
   2. heartbeat error suppression [evidence: 18× same error repeated]

📊 ACTIVE RULE EFFECTIVENESS:
   ✅ exec retry limit (applied 2026-02-09)
      Before: 405 events/week → After: 12 events/week (-97%)
   ⚠️  memory compaction rule (applied 2026-01-26)
      Pattern still present (3 sessions with 20+ compactions)
      → Consider revision

✅ Approve all / ❌ Reject all / Review individually
```

AGENTS.md is **never** modified without you clicking approve. The proposals come with evidence (real numbers from real logs). You make the call.

---

**The Karpathy angle:**

The CLAUDE.md post was about the value of explicit rules. But writing those rules requires noticing patterns — which requires attention you often don't have in the middle of actual work.

This automates the noticing. Not perfectly. Keyword matching generates false positives. Semantic patterns you didn't define will be missed. But it catches the quantitative stuff (retry loops, repeated errors, cron failures) that's genuinely hard to spot manually.

The rule quality is proportional to how well you tune `complaint_patterns` in the config. The defaults are Korean (my setup). English users: add your own.

```yaml
complaint_patterns:
  - "you forgot"
  - "again?"
  - "same mistake"  
  - "stop doing that"
  - "how many times"
```

---

**Works with any OpenClaw setup:**

The tool reads OpenClaw's standard log format. If you're running OpenClaw + Claude, it works out of the box. The analysis pipeline is:

```
collect.sh → analyze.sh → benchmark.sh → Claude API (1 call) → Discord
```

Cost: < $0.05/week. One Claude API call per run to draft the proposals.

**GitHub:** https://github.com/Ramsbaby/self-evolving-agent

Open source, MIT. ~1,800 lines of core shell + analysis.

---

**The honest version:**

It's not AGI. It's grep with opinions. The "self-evolving" name describes the goal, not the mechanism. The mechanism is: shell scripts find patterns, Claude writes a clean proposal, you decide whether to apply it.

What it does well: catches quantitative patterns (retry counts, error frequencies) that are hard to spot in raw logs. What it misses: qualitative patterns ("stop asking for confirmation") that require semantic understanding you have to define manually.

If you're building similar feedback loops for your CLAUDE.md setups, curious what patterns you're tracking. The "what does my AI keep getting wrong systematically" problem feels mostly unsolved for most setups.

---

## 📌 Posting Strategy

- **Platform priority:** r/AI_Agents first (technical audience, more upside), r/ClaudeAI same day
- **Timing:** Tuesday–Thursday, 9–11 AM EST
- **Flairs:** r/AI_Agents → "Tool/Project" | r/ClaudeAI → "Tool/Extension"

### First comment (drop immediately after posting on r/AI_Agents):

```
For English setups — the default keyword list is tuned for Korean (my logs).

Replace with these for English:
complaint_patterns:
  - "you forgot"
  - "again?"
  - "same mistake"
  - "stop doing that"
  - "how many times"
  - "wrong again"
  - "you already did this"

Add to config.yaml. That's where 80% of the signal quality improvement comes from.

Also: Stage 3 (benchmark) needs 2 weeks of data before it does anything useful.
If you install today, come back next week.
```

### Anticipated questions + honest answers:

**"Is this actually AI?"**
> The detection is grep and shell scripts. The proposal drafting is Claude (one API call). Say that plainly.

**"Doesn't Claude already remember things with Projects?"**
> Projects help within a workspace. This tracks patterns *across* sessions over time — the kind of systemic drift that doesn't show up in any single conversation. Different problem.

**"Why not just use memory/Projects?"**
> Memory is user-managed. This is automated pattern detection with evidence. You still update AGENTS.md manually — but with data instead of intuition.

**"Why shell scripts instead of Python?"**
> Portability and readability. Anyone can audit 400 lines of bash. I wanted it to be boring technology.

**"Could this go wrong?"**
> Only if you approve a bad proposal. AGENTS.md is never modified without explicit approval. The worst outcome is a useless proposal that you reject.

---

## ❌ Things NOT to say

- "Revolutionary" / "game-changing" — it's a useful cron, not a breakthrough
- "Full feedback loop" — Stage 3 is new and needs real-world validation
- "AI self-reflection" — it's keyword matching; say that plainly  
- "Self-improving" — it proposes, you improve; be precise about who does what
- "Works great out of the box" — keyword tuning is required for non-Korean setups
- Version numbers > what's live — don't claim features that aren't shipped

---

## 📊 Key Numbers to Lead With (v4.0)

| Metric | Value |
|--------|-------|
| exec retry events found | 405 |
| Max consecutive retries | 119 |
| Repeated heartbeat errors | 18× |
| Shell scripts in pipeline | 6 |
| Claude API calls per week | 1 |
| Cost per week | < $0.05 |
| Pipeline stages | 4 (collect→analyze→benchmark→synthesize) |
| Human approval required | Always |
