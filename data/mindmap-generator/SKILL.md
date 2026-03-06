---
name: mindmap-generator
description: Generates visual mindmap images from conversations, goals, decisions, and daily priorities — delivered as PNG images viewable directly in Telegram. Use when asked to visualize, map out, or break down topics, priorities, decisions, meeting notes, or weekly reviews.
metadata: {"openclaw": {"emoji": "🗺️", "requires": {"bins": ["node", "npx"]}}}
---

# Mindmap Generator Skill

You are a Chief of Staff agent with the ability to generate **visual mindmaps** and deliver them as **PNG images** directly inside Telegram messages.

---

## When to Activate

Activate this skill when ANY of the following are true:

- User explicitly asks for a mindmap, mind map, visual overview, or says "map out", "visualize", "break down visually"
- User asks to see their day, week, or priorities in a visual format
- User shares meeting notes or a voice transcript and asks for structure (note: meeting notes are optional — not every interaction will have them)
- User is making a decision and would benefit from seeing pros/cons/risks mapped out
- User asks to decompose goals, projects, or plans
- During a morning briefing when the user has 3+ priorities to juggle
- User says "I'm overwhelmed" or "there's too much going on" — proactively offer a mindmap

**Do NOT activate** for simple lists of 1-2 items or when the user explicitly asks for text-only output.

---

## How to Generate the Mindmap

### Step 1: Extract Hierarchical Structure

From the user's input (voice note, text message, calendar data, or memory context), extract a tree structure:

- **Root node** = main topic, date, or decision question
- **Level 1** = major categories (max 5-7 branches)
- **Level 2** = details, subtasks, specifics (max 3-5 per branch)
- **Level 3** = only if needed for complex topics (max 2-3 per branch)

Keep it to **3 levels max** for readability. If content is deeper, summarize at level 3.

### Step 2: Write Mermaid Mindmap Syntax

Format the structure using Mermaid's mindmap syntax. This is indentation-based:

```
mindmap
  root((Main Topic))
    Category A
      Detail 1
      Detail 2
    Category B
      Detail 3
      Detail 4
    Category C
      Detail 5
```

#### Shape Guide (use intentionally, not for every node)
- `((text))` = circle — use for the **root node only**
- `(text)` = rounded rectangle — use for **categories**
- `[text]` = square — use for **action items**
- `)text(` = cloud — use for **ideas or open questions**
- `))text((` = bang/explosion — use for **urgent or blocked items**
- `{{text}}` = hexagon — use for **decisions**
- Plain text = default — use for **details and notes**

#### Status Markers
- Prefix with ✅ for completed items
- Prefix with ⏳ for pending/in-progress items  
- Prefix with ❌ for blocked items
- Prefix with ⚠️ for risks or warnings
- Prefix with 💡 for ideas or suggestions

### Step 3: Render to PNG

Run the rendering script to convert Mermaid syntax to a PNG image:

```bash
# Save the mermaid content to a temp .mmd file
echo "$MERMAID_CONTENT" > /tmp/mindmap_input.mmd

# Render to PNG using mermaid-cli
./scripts/render_mindmap.sh /tmp/mindmap_input.mmd /tmp/mindmap_output.png
```

The script uses `mmdc` (mermaid-cli) with a custom theme configured for readability on mobile screens (Telegram).

### Step 4: Send via Telegram

After rendering, send the PNG image to the user's Telegram chat:

```bash
./scripts/send_telegram_photo.sh /tmp/mindmap_output.png "Here's your mindmap 🗺️" "$CHAT_ID"
```

The image will appear **inline in the Telegram conversation** — no downloads, no links, no HTML files.

---

## Formatting Rules

1. **Root node** = always use circle shape `((text))`
2. **Max 4 levels deep** — if deeper, summarize
3. **Max 7 branches** from root — group if more
4. **Short labels** — max 5-6 words per node. Details go in sub-nodes, not long labels
5. **No special characters** in node text that break Mermaid: avoid `(`, `)`, `[`, `]`, `{`, `}` inside label text unless they are shape delimiters
6. **Use status markers** (✅ ⏳ ❌) when the content involves tasks or progress
7. **No Markdown inside nodes** — Mermaid mindmap doesn't support bold/italic inside nodes

---

## Output Behavior

- **Always** send the mindmap as a PNG image in Telegram (viewable inline)
- **Always** include a brief text summary before or after the image (1-2 sentences)
- **Optionally** offer to regenerate with changes: "Want me to adjust anything on this map?"
- If rendering fails, fall back to a **text-based tree** using Unicode box-drawing characters:

```
📊 Today's Priorities
├── 🔴 Client Proposal (due 2pm)
│   ├── Review pricing section
│   └── Add case studies
├── 🟡 Team Standup (11am)
│   └── Prep sprint update
├── 🟢 Follow up with Rajesh
│   └── Send updated timeline
└── 📋 Admin
    ├── Expense report
    └── Update project tracker
```

---

## Example Scenarios

### Scenario 1: Morning Briefing

User says: "What's my day look like?"

Generate this mindmap:

```
mindmap
  root((Wednesday Feb 18))
    (Meetings)
      [10am - Team Standup]
      [2pm - Client Review]
      [4pm - 1:1 with Priya]
    (Tasks)
      ))⚠️ Proposal due today((
      [⏳ Review PR #342]
      [⏳ Update roadmap doc]
    (Follow-ups)
      [❌ Rajesh - SOW overdue 3 days]
      [⏳ Ankit - waiting on pricing]
    )Open Questions(
      )Timeline for Phase 2(
      )Budget approval status(
```

Send with message: "Good morning! Here's your Wednesday mapped out. The proposal is due today and Rajesh's SOW is 3 days overdue — those need attention first. 🗺️"

### Scenario 2: Decision Analysis

User says: "Should I take on the Acme consulting project?"

```
mindmap
  root((Acme Consulting Decision))
    (Pros)
      ₹12L revenue over 3 months
      Expands fintech portfolio
      Rajesh intro to their CTO
    (Cons)
      40hrs/month commitment
      Overlaps with product launch
      Below usual rate by 15%
    ))Risks((
      Scope creep - no fixed SOW yet
      Payment terms NET-60
      Single point of contact leaving
    {{Past Precedent}}
      Similar deal with TechCorp
      Went 2x over timeline
      But led to 3 referrals
    )Decision Factors(
      Can you delegate product launch?
      Is the CTO intro worth the discount?
      What does your cash flow look like in Q2?
```

### Scenario 3: Post-Meeting Action Map (when meeting notes are available)

After a meeting transcript is available, generate:

```
mindmap
  root((Meeting - Rajesh - Feb 18))
    {{Decisions Made}}
      Go with Vendor A
      Launch date March 15
      Budget approved at ₹8L
    (Action Items)
      [You - Send SOW by Friday]
      [Rajesh - Review pricing by Wed]
      [Priya - Set up staging env]
    )Open Questions(
      )Phase 2 timeline TBD(
      )Need legal review on clause 4.2(
    (Context)
      Rajesh seemed hesitant on timeline
      Budget was originally ₹6L - pushed up
```

### Scenario 4: Weekly Review

```
mindmap
  root((Week 7 Review))
    (✅ Completed - 5)
      ✅ Client proposal submitted
      ✅ Sprint planning done
      ✅ Hired frontend dev
      ✅ Updated investor deck
      ✅ Fixed auth bug
    (⏳ Carried Forward - 2)
      ⏳ Blog post draft
      ⏳ Vendor evaluation
    (❌ Dropped - 1)
      ❌ Office space tour - deprioritized
    (Key Wins)
      Client signed 6-month extension
      New dev starts Monday
    ))Blockers((
      Legal review delayed 5 days
      AWS costs spiking - need investigation
```

---

## Dependencies

- `@mermaid-js/mermaid-cli` (mmdc) — renders Mermaid syntax to PNG/SVG
- `curl` — for Telegram Bot API calls
- Node.js v18+ — runtime for mermaid-cli
