# 🎬 Self-Evolving Agent v4.0 — Demo Video Plan

> **Created:** 2026-02-18  
> **Purpose:** Complete production plan for 3 demo formats targeting different audiences  
> **Product:** Self-Evolving Agent v4.0 — 5-stage multi-agent pipeline that reads AI logs, proposes AGENTS.md improvements, and measures whether those improvements actually worked.

---

## 🎯 Core Narrative (The Hook)

> *"Your AI makes the same mistake every week. You correct it. It forgets. Self-Evolving Agent closes that loop — and tells you whether the fix actually worked."*

**The emotional arc across all videos:**
1. **Pain** → "The AI keeps repeating mistakes"
2. **Discovery** → "There's a 5-stage pipeline running every Sunday"
3. **Proof** → "119 consecutive exec retries — caught automatically"
4. **Measurement** → "The fix worked: −45% ✅"
5. **Safety** → "You approve everything. Always."

---

## 🛠️ Recommended Recording Tools

### Terminal Recording (Free — Preferred)
| Tool | Use Case | Install |
|------|----------|---------|
| **asciinema** | Live terminal recording (`.cast` files) | `brew install asciinema` |
| **agg** (asciinema gif generator) | Convert `.cast` → high-quality GIF | `brew install agg` |
| **svg-term-cli** | Convert `.cast` → SVG (crisp, scalable) | `npm i -g svg-term-cli` |
| **vhs** (by charmbracelet) | Script-driven terminal GIFs | `brew install vhs` |

### Screen Recording (Free)
| Tool | Platform | Best For |
|------|----------|----------|
| **OBS Studio** | macOS/Win/Linux | Long-form YouTube (Deep Dive video) |
| **QuickTime Player** | macOS | Quick screen capture, no install |
| **ScreenToGif** | Windows | GIF recording directly |
| **Kap** | macOS (free) | Quick GIF screen capture |

### Diagram Creation (Free)
| Tool | Use Case |
|------|----------|
| **Mermaid.js** | Pipeline flow diagrams (in-browser, free) |
| **Excalidraw** | Hand-drawn style architecture diagrams |
| **Carbon.now.sh** | Beautiful code/terminal screenshots |
| **Slides.com** | Free presentation slides for architecture walkthroughs |

### Editing
| Tool | Cost | Notes |
|------|------|-------|
| **DaVinci Resolve** | Free | Professional-grade, macOS/Win/Linux |
| **iMovie** | Free (macOS) | Quick edits, easy captions |
| **Kdenlive** | Free (all platforms) | Open source, full-featured |
| **CapCut Desktop** | Free | Easy auto-captions |

---

## 📐 Technical Specs

| Spec | Quick Demo (GitHub) | Deep Dive (YouTube) | GIF (Twitter) |
|------|---------------------|---------------------|---------------|
| **Resolution** | 1920×1080 (1080p) | 3840×2160 (4K) or 1080p | 800×450 max |
| **Frame Rate** | 30fps | 30fps | 15fps (GIF) |
| **Format** | MP4 (H.264) | MP4 (H.265/HEVC) | GIF or WebP |
| **Terminal Size** | 120×30 cols/rows | 140×35 cols/rows | 80×24 cols/rows |
| **Font** | JetBrains Mono 14px | JetBrains Mono 16px | JetBrains Mono 12px |
| **Theme** | Dracula / Tokyo Night | Dracula / Tokyo Night | Dracula |
| **Duration** | 2–3 min | 8–10 min | 25–35 sec |

### asciinema Recording Config (`~/.config/asciinema/config`)
```ini
[record]
command = /bin/zsh
cols = 120
rows = 30
idle_time_limit = 2

[play]
speed = 1.5
```

---

## 🎬 VIDEO 1: Quick Demo (2–3 min)
**Platform:** GitHub README, Reddit (r/selfhosted, r/MachineLearning, r/devops), HackerNews  
**Goal:** "Make the viewer understand what this does in 90 seconds, then want to try it"

### Pre-Production Checklist
- [ ] Clean terminal (no personal paths visible, no auth tokens)
- [ ] Fake/demo log data ready in `/tmp/sea-demo/` 
- [ ] Discord webhook screenshot pre-captured
- [ ] Terminal theme: Dracula, font: JetBrains Mono 14px
- [ ] `PS1` simplified: `$ ` only (no hostname, no git branch clutter)

---

### Storyboard — Video 1

#### **[0:00–0:15] HOOK — The Problem** *(15 sec)*
**Visual:** Split screen — left: repeating Discord conversation, right: frustrated dev
```
[Screen: Two-panel layout]
Left panel: Discord chat showing same error three weeks in a row
Right panel: Terminal with "AI made same mistake again"
```
**Narration/Text overlay:**  
> *"Your AI assistant makes the same mistake every week. You fix it. It forgets."*

**Annotation:** `⟵ Same error. Week 3.`

---

#### **[0:15–0:30] SOLUTION REVEAL** *(15 sec)*
**Visual:** Mermaid pipeline diagram animating left-to-right
```
┌─────────┐  ┌─────────┐  ┌───────────┐  ┌──────────┐  ┌───────────┐
│ Collect │→│ Analyze │→│ Benchmark │→│ Measure  │→│Synthesize │
│  Logs   │  │Patterns │  │ Compare  │  │ Effects  │  │ Proposal  │
└─────────┘  └─────────┘  └───────────┘  └──────────┘  └───────────┘
```
**Text overlay:** `"5 specialized agents. Every Sunday. Automatic."`

**Annotation boxes (appear one by one):**
- `Reads 7 days of chat logs`
- `Finds patterns YOU missed`
- `Measures whether past fixes worked`
- `< $0.05/week`

---

#### **[0:30–1:00] LIVE INSTALL** *(30 sec)*
**Visual:** asciinema recording of install + cron registration

**Terminal commands to record:**
```bash
# Step 1: Clone
git clone https://github.com/ramsbaby/openclaw-skills.git /tmp/sea-install

# Step 2: Install
cp -r /tmp/sea-install/skills/self-evolving-agent ~/openclaw/skills/
rm -rf /tmp/sea-install

# Step 3: Register cron
bash ~/openclaw/skills/self-evolving-agent/scripts/register-cron.sh

# Expected output to capture:
# ✅ Cron registered: "🧠 Self-Evolving Agent v4.0 주간 파이프라인"
# ⏰ Schedule: Every Sunday at 22:00 KST
# 📡 Delivery: #your-channel (Discord)
# 🟢 Status: enabled
```

**Annotation:** `← 2 commands. Done.`  
**Speed:** Play at 1.5× with `asciinema play --speed 1.5`

---

#### **[1:00–1:45] THE PIPELINE RUNNING** *(45 sec)*
**Visual:** asciinema recording of orchestrator running with real-looking output

**Terminal commands to record:**
```bash
# Trigger manual run (for demo)
bash ~/openclaw/skills/self-evolving-agent/scripts/v4/orchestrator.sh

# Expected output to capture (use demo data):
# ═══════════════════════════════════════════
# 🧠 Self-Evolving Agent v4.0 — Pipeline Start
# ═══════════════════════════════════════════
# 
# [Stage 1/5] 📥 Collecting logs...
#   → Scanning 7 days of session transcripts
#   → Found: 964 sessions total
#   → Sampled: 30 sessions (weighted by error density)
#   → exec retry events: 405 detected
#   ✅ collect-YYYYMMDD.json written
# 
# [Stage 2/5] 🔍 Analyzing patterns...
#   → Role filter: ON (user messages only)
#   → Context window: 3 lines
#   → Dedup: per-session
#   → Complaint signals found: 23 (after dedup: 11)
#   → AGENTS.md rule violations: 4 detected
#   ✅ analysis-YYYYMMDD.json written
# 
# [Stage 3/5] 📊 Benchmarking previous proposals...
#   → Proposal #2 (exec retry limit): EFFECTIVE ✅ (−45%)
#   → Proposal #3 (log check rule):  NEUTRAL ⏳ (+2%)
#   ✅ benchmark-YYYYMMDD.json written
# 
# [Stage 4/5] 📈 Measuring effects...
#   → Pattern frequency: before vs after
#   → "다시" pattern: 22× → 12× (−45%)
#   ✅ effects.json written
# 
# [Stage 5/5] ✍️  Synthesizing proposal...
#   → Claude Sonnet 4.5 (1 API call)
#   → Tokens used: ~1,847
#   → Cost: $0.003
#   ✅ Proposal written: data/proposals/proposal-YYYYMMDD.json
# 
# ═══════════════════════════════════════════
# ✅ Pipeline complete in 2m 41s
# 📡 Sending to Discord...
# ═══════════════════════════════════════════
```

**Annotation callouts:**
- At Stage 1: `← Reads your actual chat logs`
- At Stage 3: `← Did last week's fix work? ✅`
- At Stage 5: `← Only 1 API call. <$0.05/week`
- At Complete: `← 2m 41s total`

---

#### **[1:45–2:15] DISCORD OUTPUT** *(30 sec)*
**Visual:** Screen recording of Discord showing the actual proposal message

**What to show:**
1. Discord channel notification appearing
2. Scroll through the proposal message showing:
   - Benchmark result: `#2 Effective (−45%) ✅`
   - New proposal with before/after diff
   - The approval commands at the bottom
3. Zoom into: `✅ Apply: "apply proposal #1"` and `❌ Reject: "reject: [reason]"`

**Annotation:** `← Real diff. Real numbers. Your decision.`

---

#### **[2:15–2:30] SAFETY CLOSE** *(15 sec)*
**Visual:** Animated checklist appearing one-by-one

```
✅ Reads your logs — locally
✅ Proposes changes — never applies them automatically
✅ Measures whether fixes actually worked
✅ < $0.05 per week
✅ 400 lines of shell scripts you can read in 15 minutes
```

**Text overlay:** `"AI proposes. You decide. Always."`

---

#### **[2:30–2:50] OUTRO + CTA** *(20 sec)*
**Visual:** GitHub repo URL, star button animation, README screenshot

```
github.com/ramsbaby/openclaw-skills
⭐ Star if you want AI that learns from its own mistakes
```

---

### Production Notes — Video 1

**Recording workflow:**
```bash
# 1. Record pipeline run
asciinema rec /tmp/sea-demo-pipeline.cast --cols 120 --rows 30

# 2. Record install sequence  
asciinema rec /tmp/sea-demo-install.cast --cols 120 --rows 30

# 3. Convert to MP4 (via OBS or screen record the player)
asciinema play /tmp/sea-demo-pipeline.cast --speed 1.5

# 4. For GIF version of terminal sections
agg /tmp/sea-demo-pipeline.cast pipeline-demo.gif \
  --theme dracula \
  --font-family "JetBrains Mono" \
  --font-size 14 \
  --cols 120 \
  --rows 30
```

**Where to add annotations:**
- Use DaVinci Resolve or iMovie text overlays
- Font: Inter or Space Grotesk (professional, readable)
- Color: `#50fa7b` (green) for positive metrics, `#ff5555` (red) for the problem, `#f1fa8c` (yellow) for callouts
- Position: Bottom-left for command explanations, top-right for metric callouts

---

## 🎬 VIDEO 2: Deep Dive (8–10 min)
**Platform:** YouTube, Dev.to, Hacker News "Show HN"  
**Goal:** "Give a developer everything they need to understand the architecture and trust the system"

### Structure Overview

| Segment | Duration | Content |
|---------|----------|---------|
| Hook + Problem | 0:00–0:45 | The frustration loop — same mistakes every week |
| Version History | 0:45–2:00 | v1→v4 journey (earn credibility) |
| Architecture Walkthrough | 2:00–4:30 | 5-stage pipeline with live file inspection |
| Live Pipeline Execution | 4:30–6:30 | Full orchestrator run, every stage explained |
| Before/After Comparison | 6:30–7:30 | Real numbers from v3.0 → v4.0 improvement |
| Discord Output + Safety | 7:30–8:30 | Real notification + approval gate |
| Limits + FAQ | 8:30–9:30 | Honest. What it doesn't do. |
| Outro + CTA | 9:30–10:00 | Links, star, contribute |

---

### Detailed Script — Video 2

#### **[0:00–0:45] HOOK — The Repeating Mistake Problem**
**Visual:** Screen recording of actual Discord chat (sanitized)

**Script (narration):**
> *"Here's a real conversation with my AI assistant. Monday — I tell it to stop splitting messages. Tuesday — it splits messages again. Next Monday — same correction. I was manually updating a file called AGENTS.md — basically a rulebook for the AI — but I could only add rules I noticed. And I had no way to know if those rules were actually working."*
> 
> *"That's the problem this tool solves."*

**Terminal:** Show the AGENTS.md file briefly
```bash
cat ~/openclaw/AGENTS.md | head -30
# → Shows: "🚫 메시지 단편화 금지 (Discord 필수 규칙)"
```

---

#### **[0:45–2:00] VERSION HISTORY — Credibility Building**
**Visual:** Timeline graphic (Excalidraw export or simple animated slide)

**Script:**
> *"Version 1 was a grep script. It keyword-searched chat logs for frustration signals like 'again' and 'you forgot'. It worked — but 40% false positive rate. The AI itself says 'again' all the time. No way to tell who's frustrated."*

> *"Version 2 added exec retry detection. That's when I found 119 consecutive retries in one session. The AI had looped itself trying the same command 119 times. Nobody noticed."*

> *"Version 3 added session health metrics and cleaned up the output. But the fundamental problem remained: I'd apply a proposal, and have no idea if it helped."*

> *"Version 4 closes that loop."*

**Show:** Simple before/after table on screen
```
v3.0: Propose → Apply → ???
v4.0: Propose → Apply → Measure → Report → Propose again
```

---

#### **[2:00–4:30] ARCHITECTURE WALKTHROUGH**
**Visual:** Mix of Excalidraw diagram + live file tree + script reading

**Step 1: Show file structure**
```bash
tree ~/openclaw/skills/self-evolving-agent/scripts/v4/
# Output:
# scripts/v4/
# ├── orchestrator.sh         ← Entry point
# ├── collect-logs.sh         ← Stage 1
# ├── semantic-analyze.sh     ← Stage 2
# ├── benchmark.sh            ← Stage 3
# ├── measure-effects.sh      ← Stage 4
# └── synthesize-proposal.sh  ← Stage 5 (only one with API call)
```

**Step 2: Show data flow — read Stage 1 output**
```bash
# Show what Stage 1 produces
cat ~/openclaw/skills/self-evolving-agent/data/collect-sample.json | jq '.'
# → Show: session count, retry events, error patterns
```

**Step 3: Show role filter in action — the key v4.0 improvement**
```bash
# Open semantic-analyze.sh and show role_filter code
grep -A 10 "role_filter" ~/openclaw/skills/self-evolving-agent/scripts/v4/semantic-analyze.sh
```
**Narration:**
> *"This is the role filter — the change that cut false positives from 40% to 15%. The AI says 'again' and 'retry' constantly. By filtering to user messages only, we only catch the human expressing frustration."*

**Step 4: Show benchmark.sh — the closed feedback loop**
```bash
cat ~/openclaw/skills/self-evolving-agent/data/benchmarks/benchmark-sample.json | jq '.proposals'
# → Shows: proposal #2 effective (-45%), proposal #3 neutral
```

---

#### **[4:30–6:30] LIVE PIPELINE EXECUTION**
**Visual:** Full asciinema recording of the orchestrator running — no cuts, real time (or 1.5× speed)

```bash
# Start the full pipeline
bash ~/openclaw/skills/self-evolving-agent/scripts/v4/orchestrator.sh

# Pause narration at each stage to explain what's happening
```

**Stage-by-stage narration (as pipeline runs):**

- **Stage 1 (Collect):** *"The collector scans 7 days of session transcripts. It finds 964 total sessions, samples 30 by error density — so the heaviest sessions get more attention."*
- **Stage 2 (Analyze):** *"The analyzer runs both keyword matching and structural heuristics. It checks the context window — 3 lines before and after each keyword — to reduce false positives."*
- **Stage 3 (Benchmark):** *"This is the new part. It loads last week's proposals and checks whether the target patterns decreased. Proposal #2 dropped 45%. That's the feedback loop."*
- **Stage 4 (Measure Effects):** *"Deep frequency analysis — not just count, but trajectory. Is the problem getting better week-over-week, or bouncing back?"*
- **Stage 5 (Synthesize):** *"One Claude API call. It gets structured JSON from the first four stages and writes a markdown proposal with before/after diffs. Total cost: about half a cent."*

---

#### **[6:30–7:30] BEFORE / AFTER COMPARISON**
**Visual:** Side-by-side comparison table on screen

**v3.0 vs v4.0 Real Numbers Table:**
```
┌────────────────────────┬──────────────┬──────────────┐
│ Metric                 │ v3.0         │ v4.0         │
├────────────────────────┼──────────────┼──────────────┤
│ False positive rate    │ ~40%         │ ~15% ✅      │
│ Pipeline stages        │ 1 (monolith) │ 5 specialized│
│ Feedback loop          │ None         │ Closed ✅    │
│ Role filtering         │ Partial      │ Full ✅      │
│ Runtime                │ ~5 min       │ <3 min ✅    │
│ Cost per run           │ $0.05–$0.15  │ <$0.05 ✅    │
│ API calls              │ 1 (mixed)    │ 1 (synthesis)│
│ Effect measurement     │ Manual       │ Automatic ✅ │
└────────────────────────┴──────────────┴──────────────┘
```

**Real case study:**
> *"Here's a real number. After applying proposal #2 — the exec retry limit rule — the 'repeat command' pattern dropped from 22 occurrences to 12. That's a 45% reduction, measured automatically by the benchmark agent one week later."*

**Show:** Screenshot of the actual benchmark JSON result

---

#### **[7:30–8:30] DISCORD OUTPUT + APPROVAL GATE**
**Visual:** Real Discord notification screenshot + scroll through proposal

**What to show:**
1. Discord DM/channel notification appearing
2. Full proposal message (scrolled slowly)
3. Zoom into approval commands
4. Type: `apply proposal #1` → show what happens
5. Show: `rejected-proposals.json` — rejection memory

**Narration:**
> *"The AI doesn't decide what changes to your rules. You do. Every proposal requires an explicit approval. Rejections are logged — the system won't re-propose the same change. After 3 similar rejections, it marks that pattern as a user preference and stops suggesting it."*

---

#### **[8:30–9:30] HONEST LIMITS**
**Visual:** Simple text list on dark background

**Script:**
> *"What doesn't it do? It's not true semantic understanding — it's structured heuristics. Not embeddings. There's still a ~15% false positive rate. If the complaint pattern isn't in your config.yaml, it won't find it. The benchmark is frequency-based correlation, not causation. And the first 2-4 weeks have almost no data — cold start problem."*

> *"I'm telling you this because I'd rather you know before you try it than after."*

**Show:** The limitations table from README.md rendered cleanly

---

#### **[9:30–10:00] OUTRO + CTA**
**Visual:** Terminal typing the star command, then GitHub page

**Script:**
> *"Two commands to install. Less than 5 cents a week. Full source code — 400 lines of shell scripts you can read in 15 minutes. If your AI keeps making the same mistakes, this is worth trying."*

```
github.com/ramsbaby/openclaw-skills
⭐ Leave a star if this was useful
🐛 Open an issue if something's broken
💡 PR if you have English/multilingual patterns
```

---

### Production Notes — Video 2

**OBS Setup:**
```
Scene 1: Terminal only (asciinema playback)
Scene 2: Terminal + PiP diagram (top-right corner)
Scene 3: Browser/Discord full screen
Scene 4: Split screen (code left / diagram right)

Audio: USB microphone, cardioid mode, -20dB noise gate
```

**Recommended sections for PiP (picture-in-picture):**
- Architecture diagram visible in corner during Stage walkthroughs
- Code file + terminal side-by-side during script inspection

**B-roll to capture separately:**
1. Excalidraw diagram animation (export as video)
2. Mermaid pipeline diagram (render via mermaid.live, screen record)
3. Discord notification screenshot (real, sanitized)
4. GitHub repo page (with stars/issues visible)

---

## 🎬 VIDEO 3: 30-Second GIF
**Platform:** Twitter/X, Reddit post thumbnail, GitHub README header, Discord embeds  
**Goal:** "Instant visual proof that the pipeline does something real"

### Storyboard — 30-sec GIF

**Tool:** `vhs` (by charmbracelet) for scripted, reproducible GIFs

**VHS Script (`demo.tape`):**
```
Output pipeline-demo.gif

Set Shell "bash"
Set FontSize 13
Set FontFamily "JetBrains Mono"
Set Width 900
Set Height 450
Set Theme "Dracula"
Set TypingSpeed 60ms
Set PlaybackSpeed 1.2

# Short pause to let viewer orient
Sleep 1s

# Show the command
Type "bash ~/openclaw/skills/self-evolving-agent/scripts/v4/orchestrator.sh"
Sleep 500ms
Enter

# Stage outputs (pre-scripted with echo for consistency)
Sleep 800ms

# Stage 1
Type ""
Sleep 200ms

# The output appears (pre-recorded or typed)
Sleep 2s

# Pipeline complete message
Sleep 1s

# Discord message sent
Sleep 1s
```

**What the 30-sec GIF shows (exact sequence):**
```
[0:00–0:03]  $ bash orchestrator.sh                     ← Command typed
[0:03–0:07]  ╔══════════════════════════════╗
             ║  🧠 Self-Evolving Agent v4.0  ║            ← Banner
             ╚══════════════════════════════╝
[0:07–0:12]  [Stage 1/5] 📥 Collecting logs...
               → 964 sessions scanned, 405 exec retries found
               ✅ Done
[0:12–0:17]  [Stage 2/5] 🔍 Analyzing patterns...
               → role_filter=ON | fp rate: ~15%
               ✅ Done
[0:17–0:22]  [Stage 3/5] 📊 Benchmarking...
               → Proposal #2: EFFECTIVE ✅ (−45%)
               ✅ Done
[0:22–0:27]  [Stage 5/5] ✍️  Synthesizing...
               → 1 API call | cost: $0.003
               ✅ Pipeline complete in 2m 41s
[0:27–0:30]  📡 Sent to Discord → awaiting your approval
```

**GIF Production Commands:**
```bash
# Option A: vhs (scripted, clean, reproducible)
vhs demo.tape

# Option B: asciinema → agg
asciinema rec /tmp/demo-30s.cast --cols 100 --rows 25 --idle-time-limit 1
# (manually run the demo, or use 'expect' to automate it)
agg /tmp/demo-30s.cast pipeline-30s.gif \
  --theme dracula \
  --font-family "JetBrains Mono" \
  --font-size 13 \
  --speed 1.5

# Option C: Kap (macOS) — screen-record the asciinema player at gifsicle quality
# Compress final GIF (important for GitHub README loading speed)
gifsicle -O3 --lossy=80 pipeline-30s.gif -o pipeline-30s-optimized.gif

# Target: < 3MB for Twitter, < 10MB for GitHub
```

---

## 🎨 Thumbnail Design Concept

### YouTube Thumbnail (1280×720px)

**Layout:**
```
┌──────────────────────────────────────────────────┐
│                                                   │
│  [Dark background: #282a36 Dracula]               │
│                                                   │
│  LEFT HALF:                                       │
│  Terminal screenshot showing pipeline output      │
│  with green ✅ EFFECTIVE markers                  │
│                                                   │
│  RIGHT HALF:                                      │
│  Large text (white/green):                        │
│                                                   │
│    "119 exec retries.                             │
│     Never noticed.                               │
│     Until now."                                   │
│                                                   │
│  Small text below:                               │
│    "Self-Evolving Agent v4.0"                    │
│                                                   │
│  Bottom bar: [gradient green-to-purple]           │
│    "5 agents • <$0.05/week • Human approval"     │
│                                                   │
└──────────────────────────────────────────────────┘
```

**Design tools:**
- Figma (free tier) or Canva for layout
- Font: Space Grotesk Bold (free, Google Fonts) for headlines
- Color palette: Dracula theme (`#282a36` bg, `#50fa7b` green, `#bd93f9` purple, `#f8f8f2` white)

**Thumbnail variants to A/B test:**
1. **Pain variant:** "Why does my AI keep making the same mistake?" (question hook)
2. **Number variant:** "119 Exec Retries. 1 Tool. Found Automatically." (specificity hook)
3. **Before/After variant:** Side-by-side diff graphic (visual proof)

---

## 🎵 Background Music (Royalty-Free)

### Recommended Tracks

| Track | Source | Style | Best For |
|-------|--------|-------|----------|
| "Chill Lo-Fi Study Beats" | YouTube Audio Library | Lo-fi, calm | Deep dive walkthrough |
| "Future Technology" | Pixabay | Electronic, focus | Quick demo hook |
| "Code and Coffee" | Free Music Archive | Ambient, minimal | Architecture section |
| "Synthwave Drive" | Artlist (free tier) | Synthwave | GIF / trailer |

**Sources (100% royalty-free, YouTube-safe):**
- **YouTube Audio Library** (studio.youtube.com → Audio Library) — best free option
- **Pixabay Music** (pixabay.com/music) — license-free, no attribution needed
- **Free Music Archive** (freemusicarchive.org) — CC licensed
- **Bensound.com** — free tier with attribution

**Volume guidelines:**
- Background music: -18dB to -20dB (barely perceptible)
- Fade in: 0:00–0:03 (3 second fade)
- Duck music during narration / cut by 50%
- GIF: No audio (GIFs are mute), so no music needed

---

## 📤 Upload Strategy

### YouTube — Deep Dive Video

**Title (A/B test these):**
```
Option A: "Self-Evolving Agent v4.0: AI That Fixes Its Own Mistakes (With Proof)"
Option B: "I Built a 5-Stage Pipeline to Find 119 Hidden AI Bugs. Here's What It Found."
Option C: "How I Automated My AI's Rulebook (And Measure Whether It's Working)"
```

**Description template:**
```
Self-Evolving Agent v4.0 — a 5-stage multi-agent pipeline that reads your AI 
assistant's logs, finds patterns of repeated mistakes, and proposes evidence-based 
rule changes to your AGENTS.md. Most importantly: it measures whether those changes 
actually worked.

⏱️ Timestamps:
0:00  The problem — same mistakes every week
0:45  Version history (v1 → v4)
2:00  Architecture walkthrough
4:30  Live pipeline execution
6:30  Before/after comparison
7:30  Discord output + approval gate
8:30  Honest limitations
9:30  Install (2 commands)

🔗 Links:
GitHub: https://github.com/ramsbaby/openclaw-skills
OpenClaw: https://openclaw.ai
Docs: [link]

📊 Real numbers from this video:
• 964 sessions analyzed in one week
• 405 exec retry events detected
• 119 max consecutive retries (one session!)
• False positives: ~40% (v3.0) → ~15% (v4.0)
• Cost: < $0.05/week with Claude Sonnet

#AIAssistant #OpenSource #DevTools #Python #MachineLearning #automation
```

**Tags:**
```
AI assistant, self-improving AI, AGENTS.md, OpenClaw, Claude, automation, 
developer tools, open source, multi-agent, pipeline, log analysis, 
self-evolving agent, AI safety, terminal recording, shell scripts
```

**Upload schedule:**
- Publish: Tuesday or Wednesday, 9–11 AM (your target audience's peak time)
- First 24h: Share on Reddit (r/selfhosted, r/MachineLearning, r/devops, r/programming)
- Pin comment with timestamps + GitHub link
- Cross-post to Dev.to with embedded video

---

### GitHub README Embed

**For Quick Demo (Video 1) — as GIF in README:**
```markdown
[![Demo](docs/pipeline-demo-optimized.gif)](https://youtu.be/YOUR_VIDEO_ID)
```

**For asciinema embed (interactive, pause/copy):**
```html
<a href="https://asciinema.org/a/YOUR_ID">
  <img src="https://asciinema.org/a/YOUR_ID.svg" />
</a>
```

**README placement:**
```
1. Hero banner / logo
2. One-line description
3. → [asciinema recording here] or [GIF here]  ← Video goes here
4. Install instructions
5. ...rest of README
```

---

### Reddit Post Strategy

**r/selfhosted post template:**
```
Title: I built a weekly pipeline that reads my AI's logs and tells me what's broken 
       (with before/after measurement). Open source.

[GIF of pipeline running]

The problem: my AI assistant kept repeating the same mistakes week after week.
I'd correct it manually — but had no way to know if the fix actually worked.

So I built Self-Evolving Agent v4.0: 5 specialized agents that run every Sunday,
analyze 7 days of logs, and propose evidence-based rule changes. Most importantly:
the next week it tells you whether your fix was EFFECTIVE (-45%) or NEUTRAL (+2%).

Real numbers from my instance:
- 405 exec retry events found in one week
- 119 max consecutive retries (the AI looped itself, nobody noticed)
- False positives: down from 40% → 15% with role filtering

It proposes. You decide. Always.

GitHub: [link]
```

**Subreddits to target:**
1. r/selfhosted — "runs on your own machine, analyzes your own logs"
2. r/MachineLearning — "closed feedback loop for AI improvement"
3. r/devops — "5-stage pipeline, shell scripts, cron-based"
4. r/programming — "technical architecture deep dive"
5. r/LocalLLM — "local-first, only 1 API call"
6. r/ChatGPT / r/ClaudeAI — "makes AI assistants better"

---

## 📋 Master Production Checklist

### Pre-Production
- [ ] Create `/tmp/sea-demo/` with sanitized demo data (no real usernames, tokens)
- [ ] Prepare simplified PS1: `export PS1="$ "`
- [ ] Set terminal theme to Dracula + JetBrains Mono
- [ ] Test full pipeline run with demo data (must complete cleanly)
- [ ] Capture Discord screenshot (real but sanitized)
- [ ] Install tools: `brew install asciinema agg vhs gifsicle`
- [ ] Export Excalidraw/Mermaid diagrams as PNG/SVG

### Recording
- [ ] **GIF (Video 3)** — record first (shortest, easiest to iterate)
  - [ ] Install: `asciinema rec /tmp/install.cast`
  - [ ] Pipeline run: `asciinema rec /tmp/pipeline.cast`
- [ ] **Quick Demo (Video 1)** — record second
  - [ ] Hook screen recording (split screen problem/solution)
  - [ ] Pipeline asciinema recording
  - [ ] Discord screenshot screen recording
- [ ] **Deep Dive (Video 2)** — record last (most complex)
  - [ ] OBS setup and test
  - [ ] Architecture walkthrough (slides + terminal)
  - [ ] Live pipeline execution (full, uncut or 1.5×)
  - [ ] Discord approval demo

### Post-Production
- [ ] Edit in DaVinci Resolve or iMovie
- [ ] Add text overlays/annotations
- [ ] Add background music (-18dB)
- [ ] Export: 1080p MP4 for Videos 1&2, optimized GIF for Video 3
- [ ] Compress GIF: `gifsicle -O3 --lossy=80 input.gif -o output.gif`
- [ ] Create YouTube thumbnail (3 variants for A/B)
- [ ] Upload Video 2 to YouTube (unlisted first for review)
- [ ] Embed GIF in GitHub README
- [ ] Upload Video 1 to GitHub (as release asset) or YouTube
- [ ] Draft Reddit posts (use templates above)
- [ ] Schedule: Tuesday/Wednesday 9–11 AM KST

### Post-Upload (48h)
- [ ] Pin YouTube comment with timestamps + GitHub link
- [ ] Reply to comments within first 12 hours (YouTube algorithm boost)
- [ ] Cross-post to Dev.to article with embedded video
- [ ] Post to r/selfhosted, r/MachineLearning, r/devops
- [ ] Tweet/X: GIF + one-liner hook + GitHub link
- [ ] HackerNews "Show HN" post if you want technical audience

---

## 🗂️ Asset File Naming Convention

```
self-evolving-agent/docs/
├── demo-video-plan.md              ← This file
├── assets/
│   ├── pipeline-demo.cast          ← Raw asciinema recording
│   ├── pipeline-demo.gif           ← Converted GIF
│   ├── pipeline-demo-optimized.gif ← Compressed for README
│   ├── install-demo.cast           ← Install sequence recording
│   ├── thumbnail-v1.png            ← YouTube thumbnail (pain variant)
│   ├── thumbnail-v2.png            ← YouTube thumbnail (number variant)
│   ├── architecture-diagram.png    ← Excalidraw export
│   └── discord-screenshot.png      ← Sanitized Discord notification
```

---

*Last updated: 2026-02-18 | Plan version: 1.0*  
*Created for: Self-Evolving Agent v4.0 launch*
