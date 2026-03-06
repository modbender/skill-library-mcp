# Reddit Post Finals — Self-Evolving Agent v3.0

> Status: FINAL (post-feedback integration)  
> Target: r/AI_Agents (primary), r/ClaudeAI (secondary)  
> Best posting window: Tuesday–Thursday, 9–11 AM EST  
> Tone: honest builder, not marketer

---

## 📌 Final Title

> **I built a skill that makes my OpenClaw review its own mistakes weekly — here's the honest results (including what it gets wrong)**

---

## 📝 r/AI_Agents — Primary Post

---

**Title:** I built a skill that makes my OpenClaw review its own mistakes weekly — here's the honest results (including what it gets wrong)

---

**Body:**

TL;DR: I got tired of correcting my AI for the same mistakes over and over. Built a tool that reads the logs weekly and proposes specific rule changes. Here's what it found, what it missed, and why I'm calling it "useful, not revolutionary."

---

**The problem I was trying to solve:**

> Monday: "Stop retrying the same command when it fails"  
> AI: "Got it!"  
> Next Monday: 119 consecutive exec retries on the same broken command.

Corrections die with the conversation. The fix is to write permanent rules. But writing rules manually requires you to:
- Notice the pattern
- Remember to write it down
- Write it clearly enough that it actually sticks

I automated that loop. Imperfectly. But here's what it found that I never would have caught manually.

---

**The thing that made v3.0 worth building:**

I added exec retry detection to the latest version. When I ran it on my actual logs, it found this:

```
📊 exec retry analysis (7-day window):
   Sessions with 3+ consecutive exec retries: 221
   Maximum consecutive retries in one session: 119
   Total retry events: 405
```

119 consecutive retries. Same command. Same failure. The agent was stuck in a loop and just... kept going. That's not something you notice by scrolling logs manually. The tool generated this proposal:

```diff
+ ## ⚡ exec Consecutive Retry Limit
+
+ If the same exec command fails 3+ times in a row:
+ 1. Report the error immediately — don't retry silently
+ 2. Second attempt must use a different approach
+ 3. Third failure = STOP. Ask for manual confirmation.
```

I approved it. The retry loops stopped.

---

**Here's what the full week's analysis found (real numbers):**

| What | Count |
|------|-------|
| exec retry events | 405 |
| Max retries in one session | 119 |
| Active cron errors | 3 |
| Same log error repeating | 18× (heartbeat bug) |
| Sessions with 20+ compactions | 3 |
| Proposals generated | 3 |
| Proposals I accepted | 2 |

The third proposal I rejected — it misidentified normal git documentation in transcripts as "git rule violations." False positive. Which brings me to the honest part.

---

**What it gets wrong:**

1. **False positives on keyword matching** — The word "다시" (again) catches user frustration *and* normal phrases like "let me try again." My tests showed the complaint count was inflated ~40% by assistant-generated text being included in the scan.

2. **Missed the most important pattern entirely** — My most common frustration with the agent is "stop asking me and just do it." That pattern — the agent over-checking instead of executing — appeared constantly in my logs. The tool completely missed it because those keywords weren't in the default list.

3. **Generic proposals on quiet weeks** — When there aren't many complaint signals, the proposals become vague ("consider improving memory management"). Not useful.

4. **No improvement measurement** — It proposes. You apply. Whether things actually got better? You'll have to judge that yourself.

---

**How it actually works (no magic):**

It's cron + keyword pattern matching + one Claude API call to draft the proposal. That's it. The "self-evolving" name is aspirational; "self-reviewing-with-human-approval" is more accurate. I'm keeping the name because it communicates the goal, but I'm not going to pretend it's semantic AI.

Every Sunday at 22:00:
1. Shell script scans 7 days of chat logs for complaint keywords and exec retry patterns
2. Reads cron error logs for recurring failures
3. Cross-references AGENTS.md rules against actual behavior
4. Calls Claude once to draft a diff-format proposal
5. Sends to Discord → you approve or reject

**AGENTS.md is never modified without your explicit approval.** That's a hard design constraint.

---

**vs. self-improving-agent (which I also use):**

`self-improving-agent` = session microscope. Scores each session as it ends, in real-time.  
`self-evolving-agent` = system telescope. Looks across all sessions over 7+ days, finds systemic patterns, proposes permanent rule changes.

They're complementary. Self-improving generates session quality data → self-evolving aggregates it and finds what's going wrong at the system level.

---

**Install (if you want to try it):**

```bash
openclaw skill install self-evolving-agent
bash ~/openclaw/skills/self-evolving-agent/scripts/register-cron.sh
```

Open source, MIT. The full analysis script is ~300 lines of shell — readable in 10 minutes. I'd recommend reading it before running anything that touches your logs.

If your logs are English (mine are Korean), the default complaint keywords will be mostly useless. Add your own to `config.yaml` — "stop doing that", "you forgot again", "same mistake" — and it becomes actually useful.

---

**Honest assessment after 3+ months of use:**

The cron error detection and exec retry detection are genuinely useful. Finding out I had 405 retry events in one week was worth building the whole thing.

The complaint keyword analysis is noisier than I'd like. F1 score is probably around 50% on my dataset. The "semantic" version (embedding-based instead of keyword-based) is on the roadmap but I haven't built it yet.

Would I recommend installing it? If you have an established OpenClaw setup with meaningful logs and you're willing to tune the keyword list for your patterns — yes. If you're just starting out or hoping for something that just works — wait for v4.0.

GitHub: [link]  
ClawHub: [link]

Happy to answer questions, especially about tuning the complaint patterns.

---

## 📝 r/ClaudeAI — Secondary Post

---

**Title:** I automated the AGENTS.md update loop — weekly log analysis that proposes specific rule changes. Here's what it found in 405 exec retries I never noticed.

---

**Body:**

One of the quiet pain points with Claude as a persistent assistant: corrections don't stick between sessions.

You fix something → it works → next session the context is gone → same problem. The solution is to write permanent rules in AGENTS.md / CLAUDE.md. But doing that manually means you have to notice the pattern, remember to do it, and write it clearly enough that it actually helps.

I automated that loop. Here's what it found that I never would have caught on my own.

---

**The finding that justified the whole project:**

The latest version of the tool added exec retry tracking. When it scanned my week's logs:

```
Sessions with 3+ consecutive exec retries: 221
Maximum retries in one session: 119
Total retry events: 405
```

119 consecutive retries. Same failed command. Claude was stuck in a loop and kept hammering it without giving up. I had no idea — I wasn't watching every session in real-time.

The rule it proposed:

```diff
+ ## exec Retry Limit
+ 
+ Same command fails 3× → STOP. Report to user. Don't retry blindly.
```

Applied it. Loops stopped.

---

**How it works:**

Weekly cron. Reads your chat logs + error logs. Finds:
- Repeated complaint keywords ("you forgot", "same mistake", "stop doing that")
- Consecutive exec retries (new in v3.0)
- Cron jobs with persistent errors
- AGENTS.md rules that exist but aren't being followed

Then calls Claude once to write a diff-format proposal. Sends it to your Discord. You approve or reject.

**AGENTS.md is never modified without explicit approval.** Every proposal cites the evidence (real counts from real logs) and shows before/after.

---

**The honest version of what it gets wrong:**

The keyword matching generates false positives — "again" appears in both "stop doing that again!" and "let me try again." I estimate ~40% inflation in complaint counts from assistant text being included in the scan.

It also missed what turned out to be my biggest real pattern — the agent asking for confirmation too much instead of just executing. That wasn't in the default keyword list.

The rule of thumb: the detection quality is proportional to how well you tune the keyword list for your own frustration patterns.

---

It's open source (MIT), ~300 lines of shell scripts. Works on OpenClaw.

If anyone's building similar feedback loops for their Claude setups, curious what patterns you're tracking. The "what does the AI keep getting wrong systematically" problem feels unsolved for most people.

GitHub: [link] | ClawHub: [link]

---

## 📌 Posting Strategy

- **Platform priority:** r/AI_Agents first, r/ClaudeAI same day (different post, different angle)
- **Timing:** Tuesday–Thursday, 9–11 AM EST (peak engagement window)
- **First comment to drop immediately:**

```
For anyone curious about the keyword list — the defaults are tuned for Korean
(my setup). If you're running English logs, replace with:

"again?", "you forgot", "same mistake", "stop doing that", 
"how many times", "you already did", "wrong again"

Add to config.yaml under complaint_patterns. That's where most
of the signal quality improvement comes from.
```

- **Engage every comment in the first 2 hours** — Reddit's algorithm rewards early engagement density
- **If asked "is this actually AI?"** — be direct: "No, it's keyword matching + one Claude API call to write the proposal draft. The AI is in the proposal writing, not the detection."
- **Flair:** r/AI_Agents → "Tool/Project" | r/ClaudeAI → "Tool/Extension"

---

## ❌ Things NOT to say

- "Revolutionary" / "game-changing" — it's a useful cron, not a breakthrough
- "Full feedback loop" — there's no measurement of whether proposals actually helped
- "AI self-reflection" — it's keyword matching; say that plainly
- Version numbers > what's actually live — don't claim v4.0 features that don't exist yet
