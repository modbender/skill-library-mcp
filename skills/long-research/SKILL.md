---
name: long-research
description: >
  [BETA] Deep research that actually reads pages instead of summarizing search results.
  Tell it how long to research (10 min, 2 hours, all night) and it works the full
  duration — searching, reading every result, following leads, cracking forums,
  cross-verifying findings, and writing progressively to a research file.
  Tree-style exploration: each page read spawns new searches, like a human researcher.
  Enforced read-to-search ratio prevents shallow search-spamming. Wall-clock time
  commitment — it won't finish early. Self-audit gate blocks delivery until quality
  checks pass. Works with web_search, web_fetch, and browser-use for JS-heavy sites.
dependencies:
  - browser-use
---

# Long Research

> ⚠️ **BETA** — This skill works as described but is under active development. Review the notes below before installing.

## Dependencies

- **web_search** — any search provider (Perplexity Sonar, Brave, etc.)
- **web_fetch** — built into most agent frameworks
- **browser-use** (REQUIRED) — install via `pip install browser-use && browser-use install`. Used for JS-heavy sites, login-gated forums, and retailer pricing. The skill will not function fully without it.

## Privacy & Trust Notes

**browser-use remote mode:**
The browser-use cascade tries 3 modes in order: `chromium` (local, free) → `real` (local, free) → `remote` (cloud-hosted, burns API credits). Remote mode sends page content to browser-use.com's cloud infrastructure. If you care about privacy, you can:
- Remove `remote` from the cascade and only use local modes
- Run in Interactive mode so the agent asks before escalating to remote
- The skill works fine with local-only browser modes for most sites

**Login-gated forums and browser profiles:**
The skill includes patterns for extracting content from login-gated forums using `--profile` flags. Profiles persist cookies locally on your machine in browser-use's default profile directory. The agent does NOT attempt automated login — it uses browser-use's cookie persistence from previous manual sessions. If you haven't logged into a forum manually via browser-use before, the agent won't have access. No credentials are stored or transmitted by this skill.

**Filesystem writes:**
Research output is written to `research/[topic]-[date].md` in your agent's working directory. Progressive writes happen every 3-5 tool calls as crash recovery. Files stay on your local machine — nothing is uploaded. If running in a shared environment, configure your agent's working directory to a safe location.

**Sub-agent prompt injection surface:**
The skill mandates pasting full instructions into sub-agent task prompts. This means the entire SKILL.md (including your research query) is sent to whatever model provider your sub-agent uses. If you use external/remote model providers, be aware that your research queries and the full skill text are transmitted to those services. This is standard for any agent skill that delegates to sub-agents — but worth noting if your research topics are sensitive.

**Recommended for first-time users:**
- Run in **Interactive** mode (not Autonomous) until you're comfortable with the skill's behavior
- Start with a short duration (10 min) to see how it works
- Review the research file output before trusting findings

## Activation

When the user invokes this skill (e.g. "do long research", "research X", "pull up long research"), **immediately start the pre-flight checklist**. Do NOT ask "what topic?" separately — go straight into the pre-flight questions. If the user already provided a topic in their message, pre-fill it and ask the remaining questions.

## Pre-Flight Checklist (MANDATORY — NO EXCEPTIONS)

Before starting ANY research, confirm all of these with the user:

1. **Topic** — What exactly to research. Get specific. If not provided yet, ask now.
2. **Duration** — How long to spend. Minimum 10 minutes, can be hours.
3. **Autonomy** — Choose one. Default: Autonomous.
   - **Autonomous** — No questions, log everything, report at end.
   - **Interactive** — May ask clarifying questions during research. Pauses for answers.
   - **Interactive-continue** — May ask clarifying questions, but if user doesn't reply within ~2 minutes, continue research with best judgment. Never block on silence.
4. **Tools** — List in priority order (highest priority first). The plan block MUST reflect this ordering. Default priority:
   1. **web_search** — discovery, overviews, forum consensus
   2. **web_fetch** — reading specific review/forum/article pages
   3. **browser-use** (REQUIRED dependency) — retailer pricing (Amazon, etc.), JS-heavy sites, anything web_fetch can't reach. See `references/browser-use-patterns.md`
   
   User may reorder (e.g., browser-use first for pricing-heavy research). Always include all three in the plan block — never omit browser-use.
5. **Scheduling** — Now or delayed? If delayed, note time + timezone.
6. **Output** — Where to deliver (this chat, specific topic, file only) and format (summary, full report, comparison table).
7. **Clarifying questions** — Ask anything about the user's situation BEFORE starting. Don't assume hardware, location, budget, preferences, etc.

⛔ **GATE: You MUST post the plan block below and receive explicit user approval before making ANY research tool calls.** Do not start research based on implied approval, partial answers, or "just get going" energy. The plan block IS the gate.

Post this and wait for approval:
```
📋 Research Plan
• Topic: [what]
• Duration: [X] minutes/hours
• Mode: Autonomous / Interactive / Interactive-continue
• Tools: [list in priority order, e.g. web_search → web_fetch → browser-use]
• Start: Now / [scheduled time]
• Output: [where and format]
• Questions: [anything unclear about user's situation]

Proceed? (yes to start)
```

If the user answers clarifying questions but doesn't say "proceed/yes/go", re-post the updated plan and ask again.

---

## Spawning (CRITICAL — read this before delegating to a sub-agent)

⛔ **The sub-agent MUST have the full skill instructions in its task prompt.** The root cause of most research failures is the orchestrator paraphrasing the skill instead of injecting it. A sub-agent that doesn't read this file will ignore every gate, every ratio, every enforcement rule.

### How to spawn a research sub-agent:

1. **Read this entire SKILL.md** into context (you're already doing this if you're reading this).
2. **Construct the task prompt** with these MANDATORY sections in this order:

```
TASK PROMPT TEMPLATE (paste in this order — critical rules at TOP and BOTTOM):
─────────────────────────────────────────────────────────────────────────────
## ⛔ CRITICAL RULES (read first, enforce always)
1. READ > SEARCH. After Seed, you cannot search unless you've read something since your last search.
2. NEVER start synthesis while time remains. Run `date +%s` and check END_TS.
3. browser-use cascade: chromium → real → remote. Try ALL 3 before giving up on any source.
4. web_search returns URLS, not answers. Ignore Perplexity's synthesis text. Extract only the citation URLs.
5. "Not found" IS a valid finding. If you can't find what was asked, say so honestly. Do NOT answer an adjacent question.

## Research Task
[The user's EXACT question, quoted verbatim. Do not paraphrase, soften, or broaden it.]

## Task Anchor (re-read every 5 tool calls)
Your job is to answer THIS question: "[exact question again]"
Every 5 tool calls, ask yourself: "Does my last action directly serve THIS question?"
If no → STOP current branch → re-orient.

## User Context
[Any relevant context — location, timeline, constraints. Keep separate from the task.]

## Research Rules
[Paste the FULL Execution section from SKILL.md — the complete Read-Driven Loop,
browser-use Cascade, Forum-Cracking Playbook, Progressive Writing, Time Enforcement,
Negative Results, Self-Audit, etc.]

## ⛔ REMINDER (read last, enforce always)
- You MUST read more pages than you search. Track: reads vs searches.
- You MUST try all 3 browser modes before giving up.
- You MUST NOT start synthesis while time remains.
- You MUST deliver honest negative results, not drift to adjacent questions.
- You MUST run the self-audit before delivering.
─────────────────────────────────────────────────────────────────────────────
```

3. **Never summarize the rules.** Paste them. The sub-agent needs the actual enforcement language.
4. **Quote the user's question verbatim** in both Task and Task Anchor. Do not rephrase "find real life experience where X happened" into "research whether X is common."
5. **Put critical rules at both TOP and BOTTOM** of the prompt — primacy and recency effects in attention mean middle sections get ignored.

### Common spawning mistakes:
- ❌ "Research X for 10 minutes following the long-research skill" — the sub-agent doesn't have the skill
- ❌ Paraphrasing the question — changes what the agent optimizes for
- ❌ Adding your own interpretation — "Focus on category A" when user said "any category"
- ❌ Omitting browser-use cascade details — agent won't know to retry
- ❌ Rules only in the middle of a long prompt — agent attention drops off
- ✅ Critical rules at top AND bottom + full rules in middle + exact question quoted

---

## Execution

### Where to Run
- **Dedicated topic or sub-agent** — never in main session
- Sub-agent for fully autonomous tasks
- Dedicated topic if interactive (so user can engage)

### The Read-Driven Loop (replaces the old "Execution Flow")

The fundamental architecture: **reading pages is the default action. Searching is only allowed when the URL queue is empty.** This prevents the search-addiction pattern where agents fire 15 searches and read 3 pages.

```
1. SETUP
   ├─ START_TS=$(date +%s)
   ├─ END_TS=$((START_TS + DURATION_SECONDS))
   ├─ SEARCH_COUNT=0, READ_COUNT=0, WRITE_COUNT=0
   ├─ Create URL_QUEUE (empty list)
   └─ Post: "🚀 Research started. Deadline: $(date -d @$END_TS '+%H:%M:%S')"

2. SURVEY PHASE (first 30% of committed time — BREADTH before depth)
   ├─ Goal: IDENTIFY as many candidates/angles as possible. Do NOT deep-dive yet.
   ├─ Run 3-5 broad searches with different angles/terminology
   ├─ For each search: extract citation URLs + candidate names/items mentioned
   ├─ Build a CANDIDATE LIST: every distinct option/entity mentioned across all sources
   ├─ ⛔ GATE: Write #1 to file (Task Anchor + FULL candidate list + URL queue)
   ├─ CANDIDATE GATE: You MUST have identified ≥10 candidates before deep-diving ANY of them.
   │   If topic naturally has fewer (e.g., "best 3 X"), adjust to ≥2x the expected answer count.
   ├─ WRITE_COUNT += 1
   └─ Post: "📋 Survey complete. [N] candidates identified: [list]. Now deep-diving."
   
   Example: Don't stop at the first 3 options you find. If researching [Topic], survey should
   uncover at least 10-20 candidates across different categories, brands, or approaches.
   THEN prioritize which to deep-dive based on relevance to the question.

3. MAIN LOOP (repeat until time runs out)
   │
   ├─ IF URL_QUEUE is not empty:
   │   ├─ Pop next URL from queue
   │   ├─ RELEVANCE CHECK: Is this URL likely to contain what the Task Anchor asks for?
   │   │   If clearly irrelevant (e.g., beginner guide when searching for expert anecdotes): SKIP, log as "pruned: [reason]"
   │   ├─ READ it (web_fetch first, browser-use cascade if fails)
   │   ├─ After reading, assess: "Did this page help answer the Task Anchor?" 
   │   │   If yes: READ_COUNT += 1 (productive read)
   │   │   If no: DEAD_END_COUNT += 1 (log as dead end, don't count as productive)
   │   ├─ Extract: findings + new URLs → add new URLs to queue
   │   ├─ If read spawns a question that needs a NEW search:
   │   │   └─ ALLOWED (because you just read something)
   │   │       ├─ web_search → extract citation URLs → add to queue
   │   │       └─ SEARCH_COUNT += 1
   │   └─ Continue to next iteration
   │
   ├─ IF URL_QUEUE is empty AND you need more:
   │   ├─ web_search with NEW terms (not repeating old queries)
   │   ├─ SEARCH_COUNT += 1
   │   ├─ Extract URLs → add to queue
   │   └─ Go back to reading from queue
   │
   ├─ Every 3-5 tool calls: write findings to file, WRITE_COUNT += 1
   │
   ├─ Every 5 tool calls: 
   │   ├─ Re-read Task Anchor — am I still on-target?
   │   ├─ Run: NOW=$(date +%s); REMAINING=$((END_TS - NOW))
   │   ├─ Post: ⏱️ elapsed/committed (remaining) | 🔍 S | 📄 R | 📝 W | 🪦 D (dead ends) | R>S? yes/no
   │   └─ Verify: READ_COUNT > SEARCH_COUNT? If not, STOP searching, READ.
   │
   ├─ ⛔ BROWSER-USE DEADLINE: By 50% of committed time, you MUST have attempted
   │   at least 1 browser-use call. If you reach the halfway mark without one,
   │   STOP everything and run a browser-use cascade on your most promising blocked URL.
   │
   ├─ ⛔ NO IDLE WAITING — NEVER USE `sleep` EXCEPT FOR browser-use PAGE LOADS (max 3s):
   │   If you have time remaining, you MUST be making productive tool calls.
   │   Running `sleep 60` or any sleep > 3s to fill time is a HARD FAIL.
   │   
   │   Before you even think about sleeping, run this MANDATORY checklist:
   │   □ Have I tried the top 3 forums for this domain?
   │   □ Have I tried old.reddit.com web_fetch on at least 1 subreddit?
   │   □ Have I tried Google cache on at least 1 blocked URL?
   │   □ Have I searched YouTube comments?
   │   □ Have I searched in non-English languages (if relevant)?
   │   □ Have I tried older threads (2020, 2021, 2022)?
   │   □ Have I tried alternative community forums beyond the obvious ones?
   │   □ Have I cross-verified my existing findings with a second source?
   │   If ANY box is unchecked → DO THAT instead of sleeping.
   │
   └─ TIME CHECK: if $(date +%s) >= END_TS → exit loop, go to SYNTHESIS

4. SYNTHESIS (only after time is up)
   ├─ ⛔ GATE: Run date +%s. Print result. If NOW < END_TS, go back to step 3.
   ├─ Write final version of research file
   ├─ Include: Task Anchor, Executive Summary, Research Tree, Findings, Sources, Verification
   └─ WRITE_COUNT += 1

5. SELF-AUDIT (hard gate — blocks delivery)
   ├─ Run every checklist item (see Self-Audit section below)
   ├─ Fix any failures
   └─ Write Process Compliance section

6. DELIVER
   ├─ Chat summary (<500 words)
   ├─ Link to research file
   └─ Final elapsed time from date +%s
```

**Why this works better than a ratio rule:**
- The ratio is *architecturally enforced*: you can only search when the queue is empty OR after completing a read.
- Searching is the exception, reading is the default.
- The agent can't chain 5 searches in a row because the loop structure doesn't allow it.
- The READ_COUNT > SEARCH_COUNT check every 5 calls catches any drift.

### The Search Discipline

**web_search returns URLs, not answers.**

When web_search returns a response from Perplexity/Sonar:
1. **Extract ONLY the citation URLs** from the response.
2. **Add those URLs to your queue.**
3. **Ignore the synthesized text.** Do not read it. Do not cite it. Do not base any finding on it.

Why: Perplexity fabricates quotes, hallucinates thread URLs, and presents unverified claims as consensus. If you read its synthesis, you'll unconsciously treat it as a finding. Don't read it. URLs only.

**After Seed phase, you earn each search by reading:**
- ✅ READ → SEARCH → READ → SEARCH (alternating)
- ✅ READ → READ → READ → SEARCH (reading more is always fine)
- ❌ SEARCH → SEARCH (never, unless in Seed)
- ❌ SEARCH → SEARCH → READ (too late, you already chained)

**Hard search cap:** Maximum searches = 1.5x committed minutes. For 10 min = max 15 searches.
If you hit the cap, you are BLOCKED from searching for the rest of the session. Read only.
At any checkpoint: if SEARCH_COUNT > 2x READ_COUNT → BLOCKED from searching until reads catch up.

**PDF URLs:** If a URL ends in `.pdf`, use browser-use to render it. web_fetch returns binary garbage for PDFs. Skip PDFs entirely if browser-use is unavailable.

### Source Balance: User Reports vs Official Research (MANDATORY)

**For grey-area topics** (supplements, nootropics, off-label treatments, emerging tech, anything without large studies or established consensus):
- User reports ARE the data. The person on a forum who's been using a product for 6 months IS a primary source.
- **Hard rule: ≥40% of productive reads must be forum/user-report sources** (not academic papers, not marketing sites, not review articles).
- Track: FORUM_READ_COUNT separately from STUDY_READ_COUNT.
- At every 5-call checkpoint: `Forum reads / Total reads >= 0.4?` If not → next reads MUST be forums.
- Forums to prioritize: Reddit (relevant subreddits), StackExchange, specialized community forums for the topic, niche discussion boards, practitioner blogs with comment sections

**For well-studied topics** (established science, mainstream products):
- Official research takes priority. Forum reads still valuable but ratio can be 30/70.

### Adversarial Thinking (MANDATORY — prevents confirmation bias)

For EVERY candidate/option the research identifies as "good" or "recommended":
1. **Search for the negative case.** Literally search: `"[candidate] dangers" OR "[candidate] problems" OR "[candidate] risks" OR "[candidate] didn't work"`
2. **Follow the mechanism chain.** If something works by mechanism X, ask: "What ELSE does mechanism X do? Could it cause harm?"
   - Example: If X promotes growth/healing via mechanism Y → Does Y also have unwanted side effects? Search it.
   - Example: If X improves metric A → Does it also worsen metric B? Search it.
   - Example: If X suppresses process P → Does that suppression cause downstream problems? Search it.
3. **Devil's advocate search quota:** At least 1 adversarial search per 3 candidates identified. If you found 9 options, you need ≥3 "what could go wrong" searches.
4. **Write a "Risks & Concerns" section** that is at LEAST 25% the length of the "Benefits" section. If your benefits section is 2000 words and risks is 200 words, you're not being honest.

### Task Anchoring (MANDATORY — prevents drift)

The #1 failure mode is **task drift** — answering an adjacent, easier question.

**Mechanism:**
1. Write the user's **exact question** (verbatim) at the top of the research file under `## Task Anchor`.
2. Every 5 tool calls, re-read it and ask: "Does my last action directly help answer THIS question?"
3. If no → STOP the current branch → re-orient.

**Examples of drift:**
- User asks: "find real life experience where [specific event] happened"
- ❌ Drift: researching general requirements (answers "what's needed" not "who experienced it")
- ❌ Drift: reading official policy documents (answers "what's the rule" not "what happened")
- ✅ On-target: finding a forum thread where someone says "this happened to me: [specific event]"

**The test:** If your findings say "according to official policy..." instead of "user X on forum Y reported that..." — you've drifted.

### Negative Results (MANDATORY — don't panic-pivot)

Sometimes the answer is: **"I looked hard and didn't find it."**

This is a VALID research outcome. Do NOT:
- ❌ Pivot to answering an adjacent question to have "something to show"
- ❌ Present policy/official guidance as a substitute for the anecdotes you couldn't find
- ❌ Inflate weak leads into findings
- ❌ Quote Perplexity synthesis as if it were a real source

Instead:
- ✅ Document exactly what you searched for and where (queries + forums + pages read)
- ✅ State clearly: "After [N] searches and [M] page reads across [forums], I found zero anecdotes matching [exact question]"
- ✅ Report adjacent findings separately: "While I didn't find X, I did find Y which is related but distinct"
- ✅ Assess WHY you might not have found it: rare event? wrong search terms? content behind paywalls? topic not discussed publicly?
- ✅ Suggest what would need to happen to find it: "This might require searching [specific forum] with a logged-in account" or "This may be too rare for public discussion"

**The summary for a negative result should lead with the negative.** Don't bury it under adjacent findings.

---

## Tool Rules

### General
- **Retailer sites (Amazon, Best Buy, etc.)**: ALWAYS browser-use with `--profile`. web_fetch cannot scrape Amazon.
- **Forums/reviews**: web_fetch first, browser-use cascade if blocked.
- **Discovery**: web_search (for URLs, not answers).
- **browser-use is a hard requirement.** If not installed: `pip install browser-use && browser-use install`.

### browser-use Cascade (try ALL 3 — no exceptions)

browser-use has 3 browser modes. You MUST try them **in order**. Do NOT give up after one failure.

**Use this exact bash pattern:**
```bash
URL="https://example.com"
SESSION="research"

# Attempt 1: chromium (free)
echo ">>> Trying chromium..."
browser-use --session $SESSION --browser chromium open "$URL" 2>&1 | tail -5
# If "url:" appears in output → SUCCESS

# Attempt 2: real (free)  
echo ">>> Trying real..."
browser-use --session $SESSION --browser real open "$URL" 2>&1 | tail -5

# Attempt 3: remote (paid, last resort)
echo ">>> Trying remote..."
browser-use --session $SESSION --browser remote open "$URL" 2>&1 | tail -5
```

**Run all 3 in sequence. Stop at the first success. Log all attempts:**
```
[BROWSER CASCADE: {url}]
  chromium: SUCCESS/FAIL (reason)
  real: SUCCESS/FAIL (reason)
  remote: SUCCESS/FAIL (reason)
```

⛔ If you get an **import error** (e.g., `BrowserConfig` not found), that's a code bug, not a site block. Fix the code (use `BrowserProfile`) and retry. Do NOT count code bugs as cascade failures.

⛔ NEVER give up after 1 failure. NEVER skip to "find alternative source" without trying all 3 modes. If you log only 1 attempt, the self-audit will fail you.

### web_fetch Failure Escalation
When web_fetch returns 403, empty content, Cloudflare, or broken HTML:
1. Run the **full browser-use cascade** (all 3 modes)
2. Log: `[web_fetch BLOCKED: {url} → cascade: chromium=X, real=Y, remote=Z]`
3. Only after all 3 fail: find an alternative source (but log that you tried)

### Forum-Cracking Playbook

Forums are where real experiences live. They're also the hardest to access. Use these strategies IN ORDER:

**Reddit (NOTE: as of 2026, Reddit blocks most automated access including old.reddit.com):**
1. `old.reddit.com` via web_fetch (try first but expect 403)
2. Google cache: web_search `cache:reddit.com/r/[sub]/comments/[id]`
3. Reddit aggregation sites that compile Reddit reviews by topic
4. browser-use cascade on `reddit.com` (last resort)
5. web_search `site:reddit.com "[exact phrase]"` — use citation URLs, NOT Perplexity synthesis
6. **Fallback forums when Reddit fails:** StackExchange, specialized community forums for the topic, niche discussion boards

**Login-gated forums:**
1. web_fetch (sometimes works for newer threads)
2. browser-use chromium + JavaScript eval to extract post content:
   ```bash
   browser-use --session forum --browser chromium open "https://forum.example.com/thread/[ID]"
   # Wait 2s for page load
   browser-use --session forum --browser chromium eval "Array.from(document.querySelectorAll('[data-role=commentContent], .post-body, .message-content')).map((e,i) => 'POST ' + i + ': ' + e.innerText.substring(0,600)).join('\n===\n')"
   ```
3. This eval pattern extracts post content from login-gated pages — adapt selectors per forum.

**Blocked forums:**
1. web_fetch (may fail — if so, skip to browser-use)
2. browser-use cascade
3. Google cache

**YouTube comments:**
1. web_fetch on the video page (gets description + some comments)
2. browser-use for full comment sections

**Domain-specific community forums:**
1. Identify the top 3-5 forums for the research topic via web_search
2. web_fetch with /threads/ or /topic/ URLs, search via `site:[forum-domain]`
3. browser-use chromium for search, eval to extract post content
4. Look for practitioner blogs, review aggregation sites, and niche wikis
5. Academic databases for study abstracts when relevant (web_fetch works for most)

**Vendor research with browser-use:**
- Use browser-use eval to extract product catalogs with prices
- Example: `document.querySelectorAll('.product-miniature')` → map name + price
- Always capture full catalog, not just target products

**General fallback for any blocked source:**
1. Google `cache:[url]` via web_fetch
2. Wayback Machine: `https://web.archive.org/web/[url]`
3. Google `site:[domain] "[exact phrase]"` to find alternative pages on the same site

### Anecdote-Hunting Searches (for "find real experiences" tasks)

When the user asks for **real-life experiences**, first-person accounts, or anecdotes:

**Use personal-language queries:**
```
"my experience with" [topic] site:[relevant-forum]
"I tried" OR "I switched to" OR "after using" [topic] forum
"my experience" [topic] "what happened" forum
"I had to" OR "they told me" OR "turns out" [topic keywords]
```

**DO NOT use policy-language queries:**
```
"[topic] requirements overview" ← returns official pages, not stories
"what is needed for [topic]" ← returns guides, not experiences
```

**Source priority for anecdotes:**
1. Specialized forums for the topic (use browser-use eval pattern if login-gated)
2. Reddit (old.reddit.com → Google cache → browser-use)
3. Niche community forums and discussion boards
4. Q&A sites (real expert answers to real questions)
5. YouTube comments
6. Google `site:` searches with first-person language

**The test:** Your findings should contain direct quotes from real people, with usernames and thread URLs. If your report says "typically X happens..." instead of "user @JohnDoe42 on [Forum] reported: '...'" — you've answered a different question.

---

## Source Verification (MANDATORY)

- **Never trust Perplexity/Sonar synthesis.** Extract URLs only. Ignore the text.
- When Sonar claims "Reddit users say X": treat it as a LEAD to find URLs, not a source.
- Real user quotes must come from pages you actually fetched.
- If you can't verify a forum claim: mark it `[⚠️ unverified forum consensus]`
- ⛔ **FIREWALL:** Unverified claims CANNOT appear in Recommendation or Executive Summary. They can appear in Detailed Findings with ⚠️ tag only.

---

## Progressive Writing (MANDATORY — even for short sessions)

⛔ **GATE: First write MUST happen after Seed phase.** You CANNOT proceed to tree traversal until you've written initial findings, URL queue, and Task Anchor to the research file.

- **Write #1 (GATE):** After Seed — Task Anchor, URL queue, search terms. No more tool calls until this write lands.
- **Subsequent writes:** Every 3-5 tool calls — append new findings in batches.
- **Final write:** Synthesis phase — executive summary, tree, recommendation.
- ⛔ **NEVER accumulate all findings and write once at the end.** If session crashes, all data is lost.
- **≤15 min sessions:** minimum 3 writes. **>15 min:** minimum 1 write per 5 minutes.
- **Count writes.** Every status update: `📝 [N] file writes`. If N=0 after 4+ tool calls → STOP and write NOW.

---

## Time Enforcement (WALL-CLOCK — NO GUESSING)

**Setup:**
```bash
START_TS=$(date +%s)
END_TS=$((START_TS + DURATION_SECONDS))
echo "START_TS=$START_TS" > /tmp/research_time
echo "END_TS=$END_TS" >> /tmp/research_time
echo "Deadline: $(date -d @$END_TS '+%H:%M:%S UTC')"
```

**Every status check:**
```bash
source /tmp/research_time
NOW=$(date +%s)
echo "Elapsed: $(( (NOW - START_TS) / 60 )) min | Remaining: $(( (END_TS - NOW) / 60 )) min"
```

**Status format:**
```
⏱️ [elapsed] / [committed] ([remaining] left) | 🔍 [S] searches | 📄 [R] reads | 📝 [W] writes | R>S? [yes/no]
```

The `R>S?` field: reads must exceed searches. If it says "no", stop searching and read.

### Synthesis Gate (HARD — prevents finishing early)

⛔ **Before starting synthesis, you MUST run this check:**
```bash
source /tmp/research_time
NOW=$(date +%s)
if [ $NOW -lt $END_TS ]; then
  echo "BLOCKED: $((( END_TS - NOW ) / 60)) minutes remaining. Go back to research."
else
  echo "TIME UP: Proceed to synthesis."
fi
```

**If the check prints "BLOCKED":** You CANNOT synthesize. Go back to the Main Loop. Use the remaining time for:
- New search terms (synonyms, adjacent topics, different languages)
- Older threads (add year ranges: "2020", "2021", etc.)
- Adjacent communities (different forums)
- Cross-verifying existing findings with additional sources
- Following up on leads you deprioritized earlier
- YouTube comments on relevant videos

**If the check prints "TIME UP":** Proceed to synthesis.

---

## Context Management (see `references/context-management.md`)
- Write findings to `research/[topic]-[date].md` progressively.
- Chat context gets summaries only — detail goes to file.
- Write checkpoints every 5-10 minutes (recovery anchors after compaction).
- Long sessions WILL compact — that's expected and fine.
- Never stop research due to context size.

---

## Pricing Data (when applicable)
If the research involves products/purchases:
- **MUST hit at least one retailer** via browser-use for real pricing.
- web_search price summaries are estimates, NOT verified.
- Note currency, tax inclusion (e.g., regional pricing differences such as VAT inclusion vs exclusion), date of check.

---

## Output

### Research File (`research/[topic]-[date].md`)
```markdown
# [Topic] Research
**Date:** [timestamp]
**Duration:** [actual time spent]
**Tools used:** [list]
**Searches:** [count] | **Deep reads:** [count] | **Ratio R:S:** [ratio]

## Task Anchor
> [User's exact question, quoted verbatim]

## Executive Summary
[3-5 bullet points — ONLY ✅ verified findings]
[If negative result: lead with "After X searches and Y page reads, no [specific thing] was found."]

## Research Tree
[SEARCH → READ → spawned → READ → etc. Shows traversal.]

## Detailed Findings
### [Category 1]
[findings with source URLs, ✅/⚠️ markers]

## Comparison Table (if applicable)

## Sources
[numbered list of URLs actually fetched — NOT search result URLs]

## Source Verification
[✅ verified (fetched actual page) | ⚠️ unverified (search synthesis) | 🔗 direct quote]

## Confidence Notes
[what's solid vs uncertain]

## Recommendation
[ONLY ✅ verified sources. If negative result, recommend next steps to find the answer.]

## Process Compliance
[Self-audit pass/fail for each gate + remediation taken]
```

### Chat Summary
Post concise summary (<500 words) when done. Link to full research file.

---

## Post-Research Self-Audit (HARD GATE — blocks delivery)

⛔ **You CANNOT post the chat summary until every box is checked.** Run the audit, fix failures, THEN deliver.

### Process Gates
- [ ] START_TS and END_TS set with `date +%s`
- [ ] All time reports used real `date +%s` (no guessing)
- [ ] Time commitment honored — verify: final `date +%s` ≥ END_TS
- [ ] Synthesis Gate bash check was run and printed "TIME UP"
- [ ] Task Anchor written to file and re-checked every 5 tool calls
- [ ] **No idle waiting** — no sleep loops or timer countdowns. Every minute had active tool calls.

### Read/Search Balance
- [ ] READ_COUNT > SEARCH_COUNT — post actual numbers: `reads: [R] / searches: [S]`
- [ ] No SEARCH→SEARCH chains outside Seed phase
- [ ] Every search after Seed was preceded by at least 1 read
- [ ] **Dead ends tracked** — reads on irrelevant pages logged as dead ends, not counted as productive reads. Post: `🪦 [D] dead ends`

### Writing Gates
- [ ] Write #1 happened after Seed (before tree traversal)
- [ ] ≥3 writes for ≤15 min sessions, or 1/5min for longer
- [ ] Research tree logged in file
- [ ] Every status update included `📝 [N]` and `R>S? [yes/no]`

### Tool Usage Gates (EVIDENCE REQUIRED — not honor system)
⛔ **For each browser-use gate, you must paste the actual command and its output.** Checking a box without evidence is audit fraud.

- [ ] browser-use cascade attempted — **PASTE the 3 commands and outputs below:**
  ```
  chromium attempt: [paste command + result]
  real attempt: [paste command + result]  
  remote attempt: [paste command + result]
  ```
- [ ] browser-use attempted before 50% of committed time (paste timestamp proof)
- [ ] Every web_fetch failure escalated to full cascade — **list each 403 and what you did:**
  ```
  [url] → 403 → cascade: chromium=[result], real=[result], remote=[result]
  ```
- [ ] Reddit 403 → tried old.reddit.com first (paste the web_fetch attempt), then cascade
- [ ] At least 1 successful browser-use interaction in the session

### Source Quality Gates
- [ ] Zero Perplexity synthesis text in Executive Summary or Recommendation
- [ ] All sources have URLs from pages actually fetched
- [ ] Claims marked ✅ verified / ⚠️ unverified — none unmarked
- [ ] Recommendations backed ONLY by ✅ verified sources

### Task Fidelity Gate
- [ ] Re-read Task Anchor. Does the Executive Summary directly answer the exact question?
- [ ] If user asked for anecdotes: report contains direct quotes with usernames + thread URLs
- [ ] If mostly policy/guidance when anecdotes were asked: FAIL → go find stories
- [ ] If negative result: summary LEADS with the negative, doesn't bury it under adjacent findings

### Read Quality Gate
- [ ] Count reads that actually helped answer the Task Anchor vs dead-end reads
- [ ] At least 50% of reads must be on-topic (relevant to the actual question)
- [ ] Dead ends logged with reason: `🪦 [url] — [why irrelevant]`
- [ ] URL queue was filtered for relevance before reading (didn't blindly read every Perplexity citation)

### Survey Breadth Gate
- [ ] Survey Phase completed in first 30% of time
- [ ] Candidate list has ≥10 items (or ≥2x expected answer count for smaller topics)
- [ ] Candidates written to file BEFORE deep-diving any single one
- [ ] Deep-dive prioritization justified (why these candidates over others)

### Source Balance Gate (for grey-area topics)
- [ ] FORUM_READ_COUNT / total reads ≥ 0.4 (40% user reports)
- [ ] Post actual counts: `Forum reads: [F] / Study reads: [S] / Ratio: [F/(F+S)]`
- [ ] Real user quotes with usernames included in findings
- [ ] If ratio < 0.4: explain why (e.g., "no forums exist for this topic")

### Adversarial Thinking Gate
- [ ] At least 1 adversarial search per 3 candidates (e.g., 9 candidates = ≥3 "dangers/risks" searches)
- [ ] Each recommended candidate has a "Risks & Concerns" subsection
- [ ] Mechanism chains explored (if X promotes Y for benefit, does Y also cause Z harm?)
- [ ] Risks section is ≥25% the length of Benefits section
- [ ] Post: `Devil's advocate searches: [N] / Candidates: [M] / Ratio: [N/ceil(M/3)]`

### Remediation (fix before delivering)
| Failure | Fix |
|---------|-----|
| READ_COUNT ≤ SEARCH_COUNT | Read more pages now |
| Missing writes | Write current findings immediately |
| Unverified claims in recommendation | Remove or verify them |
| Time not honored | Continue researching |
| browser-use cascade incomplete | Run remaining modes now |
| Task drift | Re-search with original question terms |
| No anecdotes when requested | Forum searches with first-person language |
| Only 1-2 browser modes tried | Try the remaining modes on any pending source |

---

## Anti-Patterns

### Architecture violations
- ❌ **Search addiction** — firing web_search to "see what comes up" instead of reading pages in the queue. The queue is your job. Search only when it's empty or a read spawns a new question.
- ❌ **Reading Perplexity synthesis** — the synthesized text from web_search is noise. Extract URLs. Ignore text. If your findings cite "according to Perplexity..." you've failed.
- ❌ **SEARCH→SEARCH chains** after Seed — architecturally forbidden. Each search must be earned by a read.
- ❌ **Finishing early** — the Synthesis Gate bash check prevents this. Run it. **TIME IS A HARD CONTRACT.** If committed to 10 minutes, you work for 10 minutes. Finishing at 4 min on a 10-min commitment = CRITICAL FAILURE. If you think you're "done" early, you're NOT — run the mandatory checklist, search deeper, cross-verify, find more threads. Check `date +%s` against END_TS before ANY final output.
- ❌ **Idle waiting / sleep commands** — NEVER use `sleep` for more than 3 seconds (browser-use page loads only). Running `sleep 60` to fill remaining time is a HARD FAIL that the audit WILL catch. The checklist of "things to do when done" is mandatory — run through it before claiming you're out of options.
- ❌ **Garbage reads** — reading irrelevant pages just to inflate READ_COUNT. A beginner tutorial doesn't count as a "read" when researching expert-level anecdotes. Filter the URL queue for relevance BEFORE reading. Dead-end reads must be logged as dead ends, not productive reads.
- ❌ **Audit fraud** — checking self-audit boxes for things you didn't do. If the audit says "browser-use cascade attempted" but you made zero browser-use calls, that's fabrication. The audit requires EVIDENCE (paste commands + outputs), not just checkboxes.

### Content violations
- ❌ **Answering a different question** — if user wants anecdotes, don't deliver policy summaries. Re-read the Task Anchor.
- ❌ **Panic-pivoting on negative results** — "not found" is valid. Don't inflate weak leads.
- ❌ **Unverified claims in recommendations** — if you didn't fetch the page, it can't go in the recommendation.
- ❌ **Marketing claims as benchmarks** — distinguish clearly.
- ❌ **Premature narrowing** — picking 3-5 candidates in Seed and ignoring everything else. The Survey Phase exists to prevent this. You MUST cast a wide net before deep-diving. If you're deep-diving a candidate before identifying ≥10 options, you've narrowed too early.
- ❌ **All-research, no-users** — citing 10 academic papers and 0 forum threads. For grey-area topics, user reports are EQUALLY valuable. The 40% forum-read quota exists for a reason.
- ❌ **Confirmation bias** — only searching for why something works, never for why it might harm. The Adversarial Thinking section is mandatory. Every "this is great" needs a "but here's what could go wrong" search.

### Tool violations
- ❌ **Giving up after 1 browser-use failure** — try ALL 3 modes. Log all attempts.
- ❌ **Silently skipping blocked sources** — web_fetch 403 → full cascade, always.
- ❌ **web_fetch on Amazon** — use browser-use with `--profile`.
- ❌ **Zero browser-use calls** — must attempt at least once per session.

### Process violations
- ❌ **Running in main session** — always dedicated topic or sub-agent.
- ❌ **Spawning sub-agent without full rules** — paraphrasing = agent ignores rules. Paste them.
- ❌ **Paraphrasing user's question** — quote verbatim. "Find real experiences" ≠ "research whether common".
- ❌ **Single write at end** — progressive writes mandatory. Session crashes lose everything.
- ❌ **Fabricating elapsed time** — every timestamp from `date +%s`. No guessing.
- ❌ **Skipping self-audit** — hard gate. No exceptions.
- ❌ **Skipping pre-flight** — plan block must be posted and approved.
