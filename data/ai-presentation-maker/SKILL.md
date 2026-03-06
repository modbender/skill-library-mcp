---
name: ai-presentation-maker
version: 1.0.0
description: "AI Presentation Maker — the interview-driven pitch deck generator for your OpenClaw agent. Tell it what you built, who you're presenting to, and pick an angle — it generates a complete slide deck with speaker notes, factual validation, and real cost breakdowns. No made-up ROI. No speculative projections. Just compelling presentations built from actual work. Exports to Markdown, PPTX, and PDF. Works standalone or alongside AI Persona OS. Built by Jeff J Hunter."
tags: [presentation, slides, pitch-deck, keynote, speaker, deck, export, pptx, pdf, markdown, factual]
author: Jeff J Hunter
homepage: https://jeffjhunter.com
metadata: {"openclaw":{"emoji":"🎤","requires":{"bins":["bash","sed","find","grep","date","wc"],"optionalBins":["openclaw","jq","pandoc","python3"],"env":[],"optionalEnv":[]},"stateDirs":["~/workspace/presentations","~/workspace/presentations/decks","~/workspace/presentations/exports"],"persistence":"Presentation data stored as JSON + Markdown under ~/workspace/presentations/. All file operations routed through assets/presentation-helper.sh which enforces input sanitization, path validation, and JSON validation in code. No network activity required. Export to PPTX requires python3 + python-pptx. Export to PDF requires pandoc.","cliUsage":"The openclaw CLI is OPTIONAL. Core presentation creation works entirely with standard Unix tools and the bundled helper script."}}
---

# 🎤 AI Presentation Maker

**The interview-driven pitch deck generator for your OpenClaw agent.**

Tell it what you built. Tell it who's in the room. Pick an angle. Get a complete slide deck with speaker notes — built from facts, not fantasies.

---

## ⛔ AGENT RULES — READ BEFORE DOING ANYTHING

> 1. **Use EXACT text from this file.** Do not paraphrase menus, slide type names, or instructions. Copy them verbatim.
> 2. **NEVER tell the user to open a terminal or run commands.** You have the exec tool. USE IT. Run every command yourself via exec.
> 3. **One step at a time.** Interview questions go 1-2 at a time. Never dump the full questionnaire.
> 4. **NEVER overwrite existing presentation files without asking.** If the file exists, ask before replacing.
> 5. **FACTUAL VALIDATION IS MANDATORY.** Before generating any slide, check for speculative language. Flag it. The user decides what stays.
> 6. **Scope: ~/workspace/presentations/ only.** All file operations stay under this directory.
> 7. **USE THE HELPER SCRIPT FOR ALL FILE OPERATIONS.** Never construct raw shell commands with user input. Always route through `assets/presentation-helper.sh`.
> 8. **Speaker notes are required.** Every slide gets "What to say" and "What NOT to say" notes. No exceptions.
> 9. **No made-up numbers.** If the user hasn't provided a specific stat, don't invent one. Use "[INSERT ACTUAL NUMBER]" as placeholder and flag it.
> 10. **Respect the user's voice.** If they talk casually, the deck should feel casual. If they're formal, match it. The interview captures this.

---

## 🛡️ Helper Script — Security Layer

All file operations go through `assets/presentation-helper.sh`. This script enforces sanitization in **code**, not in prompt instructions.

**First-run:** Copy the helper to the workspace:
```bash
cp assets/presentation-helper.sh ~/workspace/presentations/helper.sh
chmod +x ~/workspace/presentations/helper.sh
```

**Usage:**
```bash
# Create workspace
~/workspace/presentations/helper.sh init

# Save presentation metadata (JSON from stdin)
~/workspace/presentations/helper.sh save-meta < /tmp/pres_meta.json

# Save slide deck (Markdown from stdin)
~/workspace/presentations/helper.sh save-deck <pres_id>

# List presentations
~/workspace/presentations/helper.sh list

# Get presentation metadata
~/workspace/presentations/helper.sh get-meta <pres_id>

# Get slide deck
~/workspace/presentations/helper.sh get-deck <pres_id>

# Delete presentation
~/workspace/presentations/helper.sh delete <pres_id>

# Sanitize a string
~/workspace/presentations/helper.sh sanitize-string "user input"
```

---

## 🔍 Post-Install Check

> **🚨 AGENT: Run this FIRST before showing any menu.**

```bash
# Check for existing workspace
ls ~/workspace/presentations/config.yaml 2>/dev/null

# Check for AI Persona OS
ls ~/workspace/SOUL.md ~/workspace/AGENTS.md 2>/dev/null | wc -l

# Check export dependencies
which python3 2>/dev/null && echo "HTML export: ✅ (recommended)" || echo "HTML export: ❌ (needs python3)"
echo "Gamma export: ✅ (always available)"
which pandoc 2>/dev/null && echo "PDF export: ✅" || echo "PDF export: ❌ (install pandoc — or use HTML print)"
which python3 2>/dev/null && python3 -c "import pptx; print('PPTX export: ✅')" 2>/dev/null || echo "PPTX export: ❌ (install python3 + python-pptx)"
```

**If config.yaml exists → workspace is set up.** Show:
> "🎤 Presentation Maker is ready. You have X decks saved. Say **create presentation** to start a new one or **list presentations** to see what you've got."

**If config.yaml is missing → fresh install.** Show the welcome message:

> **🚨 AGENT: OUTPUT THE EXACT TEXT BELOW VERBATIM.**

```
🎤 Welcome to AI Presentation Maker!

I build slide decks from your actual work — not templates
stuffed with placeholder text.

Here's how it works:

1. 🎯 I interview you (5 min)
   What you built, who's in the room, what matters

2. 🧭 I suggest angles (pick one)
   3-5 ways to frame your story

3. 📊 I generate your deck
   Slides + speaker notes + factual validation

4. ✏️ You refine
   Add details, change tone, cut slides

5. 📦 Export
   Markdown (default), PPTX, or PDF

Every number in your deck comes from YOU.
No made-up ROI. No fake projections.

Ready? Say "create presentation" to start.
```

Wait for explicit confirmation before proceeding.

---
---

# Setup (First Run Only)

## Create Workspace

> **AGENT: Run on first use.**

```bash
mkdir -p ~/workspace/presentations/{decks,exports,archive}
cp assets/presentation-helper.sh ~/workspace/presentations/helper.sh
chmod +x ~/workspace/presentations/helper.sh
```

## Default Config

Write `~/workspace/presentations/config.yaml`:

```yaml
# AI Presentation Maker — Configuration
# Edit directly or say "edit config" in chat

defaults:
  tone: "conversational"  # professional | conversational | humorous | technical
  max_slides: 20
  include_speaker_notes: true
  factual_validation: true     # Flag speculative language
  include_mistakes_slide: true  # Authenticity builder
  include_costs_slide: true     # Real investment breakdown

export:
  default_format: "html"
  html_theme: "spark"   # terminal | executive | spark | clean
  per_slide_html: false  # true = individual HTML files per slide (keynote quality)
  formats_available:
    markdown: true
    html: true        # Zero dependencies — recommended
    gamma: true       # Zero dependencies — for Gamma.app users
    pptx: false       # Set true after installing python-pptx
    pdf: false        # Set true after installing pandoc (or use HTML print)

speaker:
  name: ""           # Set during first presentation or say "edit config"
  title: ""
  company: ""
  bio: ""

branding:
  cta_links: []
  training_links: []
  coupon_codes: []
```

> **AGENT: If AI Persona OS is detected**, pull speaker info from SOUL.md or AGENTS.md if available. Ask user to confirm.

---
---

# Creating a Presentation

## The Interview

When user says "create presentation", "new deck", "build slides", "make a pitch deck", or similar:

> **AGENT: Follow this interview flow. Ask 1-2 questions per message. Be conversational. Adapt based on their answers — skip redundant questions, dig deeper on thin answers.**

### Phase 1: The Subject (1 message)

> "What's this presentation about? Give me the short version — what did you build, do, or accomplish?"

**Capture:** Core subject. This seeds everything.

**If they give a thin answer** (e.g., "my AI project"), follow up:
> "Tell me more — what specifically did you build? What does it do? How long did it take?"

---

### Phase 2: The Audience (1 message)

> "Who's in the room?
> - How many people?
> - What do they do? (founders, developers, executives, students...)
> - What are they hoping to learn or get from this?"

**Capture:** Audience profile. Drives tone, depth, and angle selection.

---

### Phase 3: The Speaker (1 message)

> "Quick — your name, title, and one sentence of credibility. What makes you the person to give this talk?"
>
> *(If I already have your speaker info from config, I'll use that — just confirm.)*

**Capture:** Speaker identity. Goes on title slide and shapes authority framing.

**If config already has speaker info:** Show it and ask to confirm or update.

---

### Phase 4: The Work (1-2 messages)

This is the most important phase. Get SPECIFICS.

> "Now the meat — what did you actually do? I need real details:
> - What was built or created?
> - How long did it take?
> - What results do you have so far? (actual numbers only)
> - What did it cost? (hardware, software, time)
> - What went wrong? (mistakes are gold for presentations)"

**Capture:** Factual foundation. Every claim in the deck traces back to this.

**If they skip costs:** Ask specifically:
> "What about costs? Hardware, software subscriptions, time invested — even rough numbers make the deck more credible."

**If they skip mistakes:** Ask specifically:
> "Any mistakes or things that didn't work the first time? Audiences love authenticity — it builds trust faster than success stories."

---

### Phase 5: The Angle (1 message)

Based on everything gathered, generate 3-5 presentation angles.

> **AGENT — Angle generation rules:**
> 1. Each angle is a distinct FRAMING of the same content — not different topics
> 2. Each angle implies a different audience takeaway
> 3. Name each angle with a punchy title (3-6 words)
> 4. Add one sentence explaining the angle's focus
> 5. Consider these angle categories:
>    - **Cost/Time Savings** — "We did X for $Y in Z hours"
>    - **Capability Expansion** — "Now we can do things we couldn't before"
>    - **New Business Model** — "This changes how we make money"
>    - **Competitive Advantage** — "While others are still doing X, we're doing Y"
>    - **Personal Transformation** — "How this changed my approach to everything"
>    - **Democratization** — "Anyone can do this now, here's how"
>    - **Behind the Scenes** — "Here's exactly how we built it, warts and all"

**Present like this:**

```
🧭 Here are 5 angles for your deck:

1. [Punchy Title]
   [One sentence explaining the focus]

2. [Punchy Title]
   [One sentence explaining the focus]

3. [Punchy Title]
   [One sentence explaining the focus]

4. [Punchy Title]
   [One sentence explaining the focus]

5. [Punchy Title]
   [One sentence explaining the focus]

Which one resonates? (pick a number or describe your own)
```

**Capture:** Selected angle. This determines the narrative arc of the entire deck.

---

### Phase 6: Resources & CTA (1 message)

> "Last thing — any resources to include?
> - Links to share? (tools, courses, websites)
> - Coupon codes or special offers?
> - What's the ONE thing you want people to do after this talk? (sign up, book a call, visit a URL, join a community)"

**Capture:** CTA and resources. Goes on closing slides.

**If they say "nothing":** That's fine. Not every deck needs a hard CTA.

---

## Interview Complete → Generate Deck

After all 6 phases, confirm the brief:

```
🎤 PRESENTATION BRIEF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 Subject: [subject]
👥 Audience: [size] [roles] — [what they want]
🎙️ Speaker: [name], [title]
🧭 Angle: [selected angle]
💰 Costs: [summary]
📊 Results: [summary]
❌ Mistakes: [summary]
🎯 CTA: [what they should do after]

Generating your deck now...
```

Then proceed to **Deck Generation**.

---
---

# Deck Generation

## Slide Structure

The agent generates slides based on the selected angle and gathered data. Not every deck needs all slide types — the agent selects the relevant ones based on content.

### Core Slides (always included)

**SLIDE 1: Title Slide**
- Presentation title (from the selected angle)
- Speaker name + title
- Event/date (if provided)

**SLIDE 2: The Hook**
- ONE fact-based statement that grabs attention
- Must be verifiable from the interview data
- No speculation. Example: "Yesterday, I built a lead gen system in 5 hours for $40/month. It sent 20 emails and got a reply by midnight."

**SLIDE 3: The Problem**
- The verified pain point the audience has
- Must connect to what was built
- Draw from audience profile (Phase 2)

**SLIDE 4: What We Built**
- Concrete description of the work
- Timeline
- Screenshots/evidence descriptions (agent notes where visuals should go)

**SLIDE 5: What It Does**
- Capabilities as a list or table
- Each capability must be real (no "coming soon" features unless flagged)

**SLIDE 6: Real Results**
- Actual numbers from the interview
- No rounding up. No "approximately." Use exact figures.
- If results are early/limited: "Early results from [timeframe]:" — frame as an experiment, not a case study

### Situational Slides (included when relevant data exists)

**SLIDE: Investment / Real Costs**
- Hardware, software, time — actual numbers
- Include if: user provided cost data
- Format as a simple breakdown table

**SLIDE: Mistakes & What We Learned**
- Real failures from the interview
- What went wrong → what was fixed → what was learned
- Include if: user shared mistakes AND `config.include_mistakes_slide: true`

**SLIDE: Why Now**
- What changed that made this possible/easier
- Historical context — "You could have done this before, but..."
- Include if: the work involves new technology or methodology

**SLIDE: DIY Path**
- How the audience could replicate this themselves
- Tools, steps, approximate time/cost
- Include if: audience profile suggests they want to do it themselves

**SLIDE: What We're Testing**
- Experiments in progress, framed honestly
- "We're currently testing..." not "This will..."
- Include if: user mentioned ongoing experiments

**SLIDE: Potential (WITH CAVEATS)**
- Conservative projections ONLY
- MUST include caveat language: "Based on early results, IF current trends hold..."
- Include if: user explicitly wants projections
- **⚠️ Flag this slide for factual review**

**SLIDE: What You Could Build**
- Framework for the audience to apply to their own context
- Not prescriptive — suggestive. "Here's a framework for thinking about this."
- Include if: audience is builders/doers

### Closing Slides (always included)

**SLIDE: The Offer / CTA**
- Clear single action for the audience
- Include links, codes, URLs from Phase 6
- If no CTA was provided → make this a "Where to Learn More" slide

**SLIDE: Q&A**
- Simple closer
- Include speaker contact info
- Include resource links

---

## Speaker Notes Format

Every slide MUST include speaker notes in this format:

```markdown
### Speaker Notes — [Slide Title]

**What to say:**
[2-4 bullet points of what the speaker should communicate]
[Include specific numbers to reference]
[Include transitions to the next slide]

**What NOT to say:**
[1-2 things to avoid]
[Common traps: overpromising, speculation, competitor bashing]

**Timing:** ~[X] minutes

**Visual aids:** [Screenshots, demos, or props to reference]
```

> **AGENT: "What NOT to say" is critical.** Common entries:
> - "Don't promise specific ROI numbers you haven't verified"
> - "Don't compare to competitors by name"
> - "Don't say 'this will definitely...' — say 'based on what we've seen...'"
> - "Don't skip the costs slide — transparency builds trust"
> - "Don't apologize for early results — frame as experiments"

---

## Factual Validation

> **🚨 MANDATORY: Run this check before showing the generated deck to the user.**

Scan every slide for:

| Flag | Pattern | Action |
|------|---------|--------|
| 🔴 **Speculative** | "could save", "might generate", "potential to", "up to", "estimated" | Flag and suggest rewording to factual language |
| 🔴 **Unverified number** | Any number not from the interview data | Replace with `[INSERT ACTUAL NUMBER]` placeholder |
| 🟡 **Projection** | Future tense claims about results | Add caveat: "Based on early results, IF trends hold..." |
| 🟡 **Superlative** | "best", "fastest", "only", "first" | Flag — user must confirm or remove |
| 🟢 **Hedged OK** | "We're testing", "Early results suggest", "In our experience" | No action — these are honest framings |

After generation, show a validation summary:

```
📋 FACTUAL VALIDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 Speculative claims found: [X]
🟡 Projections needing caveats: [X]
🟢 Factual claims verified: [X]

[List each flag with slide number and the flagged text]

Fix these? (yes / show me / leave as-is)
```

---

## Tone Profiles

The deck's language adapts to the selected tone:

**Professional**
- Formal language, no contractions
- Data-forward, minimal storytelling
- "The system processed 20 outreach emails within the first 6 hours of deployment."

**Conversational (DEFAULT)**
- Contractions, natural language
- Story-driven with data supporting
- "We built this thing yesterday. Sent 20 emails. Got a reply by midnight."

**Humorous**
- Self-deprecating, light
- Mistakes slide is emphasized
- "So naturally, the first thing it did was email the wrong person. We fixed that."

**Technical**
- Jargon-appropriate, architecture-focused
- Include system diagrams, stack details
- "The pipeline uses JSON-based lead storage with cron-triggered sequence management."

---
---

# Asset Planning (Before Generation)

After the interview and outline are complete, but BEFORE generating slides, plan all visual assets.

> **AGENT: Run this checklist before generating any slides:**

## Asset Checklist

1. **Image needs** — Which slides need images? (screenshots, product photos, diagrams)
   - Map each image to a specific slide in the outline
   - If user mentioned a demo → screenshot slide
   - If user mentioned data → plan a big_number or comparison slide
   - If user has a logo → title and closing slides

2. **QR codes** — Does the CTA include a URL?
   - Generate QR codes BEFORE slide generation (not during)
   - Save to `~/workspace/presentations/assets/{pres_id}/`

3. **Data visualization** — Any numbers that need charts or infographics?
   - Plan the visualization type (comparison table, big number, timeline)
   - Match to a slide type from the template gallery

4. **Missing assets** — What's missing?
   - Use `[IMAGE: description of what's needed]` placeholder
   - Tell user: "I need a screenshot of [X] to complete slide [N]. Can you provide one?"

> **AGENT: Never generate slides with broken image paths.** If an image isn't available, use a placeholder description or skip the image slide entirely.

## Custom Style Instruction

If the user wants a custom look beyond the 4 built-in themes, build a `style_instruction` object:

```json
{
  "aesthetic_direction": "A stark, high-contrast design for maximum stage presence.",
  "color_palette": "Background: #1A1A1A, Title: #FFFFFF, Body: #B3B3B3, Accent: #00E676",
  "typography": "Font Family: Roboto. Headline: 64px, Body: 32px, Caption: 18px."
}
```

Pass this to the template engine:

```bash
python3 references/slide-templates.py \
  --style-instruction '{"aesthetic_direction":"...","color_palette":"Background: #1A1A1A, Title: #FFFFFF, Body: #B3B3B3, Accent: #00E676","typography":"Font Family: Roboto. Headline: 64px, Body: 32px."}' \
  --theme custom --type title --title "My Talk" --output slide_01.html
```

> **AGENT: When user asks for custom colors/fonts:**
> 1. Ask for their brand colors (background, text, accent)
> 2. Ask for font preference (or default to Inter)
> 3. Build the style_instruction JSON
> 4. Generate all slides using `--theme custom --style-instruction '{...}'`

---
---

# Quality Checklist (Post-Generation)

After generating all slides, run this QA check BEFORE showing to user.

> **AGENT: Run this checklist after EVERY deck generation. Report any issues found.**

## Automated Checks

| Check | What To Verify | Action If Failed |
|-------|---------------|-----------------|
| **Style consistency** | All slides use same theme colors/fonts | Re-generate with correct theme |
| **Content integrity** | Every interview fact appears in slides | Add missing content |
| **One idea per slide** | No slide has more than 2-3 bullet points | Split into multiple slides |
| **Overflow prevention** | No text exceeds 6 lines per slide body | Split or trim |
| **Image validation** | All `src=` paths exist or are placeholders | Replace with `[IMAGE: description]` |
| **Accessibility** | All `<img>` tags have `alt` attributes | Add descriptive alt text |
| **Link validation** | All URLs in CTA/closing are reachable | Flag broken links |
| **Speaker notes** | Every slide has "What to say" notes | Add notes for bare slides |
| **Factual validation** | No speculative language (already handled) | Run validation engine |

## Text Length Rules

| Element | Maximum | If Exceeded |
|---------|---------|-------------|
| Slide title | 8 words | Shorten or split into title + subtitle |
| Bullet point | 15 words | Rewrite more concisely |
| Bullets per slide | 5 items | Split into 2 slides |
| Body paragraph | 3 sentences | Convert to bullets or split |
| Speaker note | 4 sentences per section | Trim to essentials |

> **AGENT: After QA, report:**
> "✅ Quality check complete: [N] slides, [N] issues found."
> Then list any issues with slide numbers.

---
---

# Edge Case Handling

## Long Text Auto-Split

If a slide's content exceeds the maximum (5 bullets or 3 paragraphs), automatically split:

1. Keep the original title for the first slide
2. Add "(cont'd)" to the title for subsequent slides
3. Split content at natural break points (paragraph breaks, after 3rd bullet)
4. Each resulting slide must pass the text length rules

> **AGENT: When interview data produces too much content for one slide:**
> "That's a lot of great content. I'm splitting it across 2 slides to keep each one clean and readable."

## Missing Sections

If the interview is incomplete (e.g., user skipped the costs question):

- **Do NOT** generate a costs slide with made-up numbers
- **Do NOT** silently skip the slide
- **DO** tell the user: "I notice we didn't cover costs. Want me to add a costs slide? I'll need the real numbers."
- **DO** generate remaining slides normally

## Missing Images

If a slide references an image that doesn't exist:

- For screenshots: Replace with a styled placeholder box saying `[Screenshot: description]`
- For QR codes: Skip the QR element, keep the link text visible
- For logos: Use text-only version of the name
- **Never** leave a broken `<img>` tag in the output

## Unusual Content

- **All numbers**: If interview only provided one or two data points, use `big_number` slides instead of tables
- **No mistakes**: If user says "we didn't make mistakes" → skip mistakes slide entirely, don't force it
- **No CTA**: If user has no links/offers → use a simple closing slide with contact info only
- **Very short talk**: If user wants 3-5 slides, use only: title, one content, closing

---
---

# In-Chat Commands

| Command | What It Does |
|---------|-------------|
| `create presentation` | Start the interview → generate a new deck |
| `list presentations` | Show all saved decks with dates and slide counts |
| `show [name]` | Display a saved deck in chat |
| `edit [name]` | Re-open a deck for changes |
| `add slide [name]` | Add a new slide to an existing deck |
| `remove slide [name] [#]` | Remove a slide by number |
| `reorder [name]` | Show slides and let user drag/reorder |
| `change tone [name] [tone]` | Rewrite deck in a different tone |
| `export [name] [format]` | Export to markdown/html/gamma/pptx/pdf |
| `speaker notes [name]` | Show just the speaker notes |
| `validate [name]` | Re-run factual validation |
| `duplicate [name]` | Copy a deck for a different audience/angle |
| `archive [name]` | Move to archive |
| `delete [name]` | Delete permanently (asks to confirm) |
| `presentation help` | Show all commands |

> **AGENT: Recognize natural language.** "Make me a pitch deck" = `create presentation`. "Show me my slides" = `list presentations`. "Export it as PowerPoint" = `export [last deck] pptx`. Be flexible.

---
---

# Editing & Refinement

When user says "edit [name]" or asks to change a deck:

## Quick Edits

The agent should handle these naturally:

| User Says | Agent Does |
|-----------|-----------|
| "Add real costs" | Asks for cost details, adds/updates Investment slide |
| "Remove projections" | Strips all projection language, removes Potential slide if needed |
| "Add [specific detail]" | Adds to the relevant slide or creates a new one |
| "Make it shorter" | Suggests slides to cut, asks for approval |
| "Make it longer" | Suggests slides to add based on interview data |
| "Change the tone to [X]" | Rewrites all slides in the new tone |
| "Add a mistake" | Asks what went wrong, adds to Mistakes slide |
| "Update the results" | Asks for new numbers, updates Results slide |
| "Change the angle" | Re-generates deck with new angle (keeps all data) |
| "Add speaker notes" | Generates notes for any slides missing them |
| "Move slide X to position Y" | Reorders slides |

## Major Revisions

If the user wants a fundamentally different deck:
> "That's a big change. Want me to keep the same interview data and just re-generate with the new angle? Or start fresh?"

---
---

# Export

## Markdown (Default)

Every presentation is stored as Markdown at `~/workspace/presentations/decks/{pres_id}.md`.

**Markdown format:**

```markdown
# [Presentation Title]
*[Speaker Name] — [Title]*
*[Date]*

---

## Slide 1: [Slide Title]

[Slide content]

> **Speaker Notes:**
> **Say:** [what to say]
> **Don't say:** [what not to say]
> **Timing:** ~X min

---

## Slide 2: [Slide Title]

[Slide content]

...

---

## Resources

- [Link 1]
- [Link 2]

---

*Generated by AI Presentation Maker — Facts, not fantasies.*
```

---
---

# 🎨 Template Gallery

When generating HTML slides, the user picks a **theme** and the agent selects **slide types** from the gallery. The agent can also generate per-slide HTML files for maximum control.

## Choosing a Theme

> **AGENT: Ask the user to pick a theme BEFORE generating HTML slides. Show this menu:**

```
🎨 Pick a visual theme for your slides:

1. 🖥️  Terminal    — Dark + green, terminal window frames. Hacker/tech vibe.
2. 🏢  Executive   — Navy + gold, clean serif headings. Boardroom ready.
3. ⚡  Spark       — Purple/teal gradient, modern sans-serif. Startup energy.
4. ✨  Clean       — White + charcoal, Swiss minimal. Universal and professional.
5. 🎨  Custom      — Tell me your brand colors and I'll build a custom theme.

Which one? (pick a number or describe what you want)
```

**If the user describes something custom** (e.g., "red and black" or "playful"), map to the closest theme and say: "Going with [Theme] — closest match. I can tweak colors after."

## Slide Type Gallery

The agent selects from these **11 premade slide layouts**. Each is a distinct HTML template optimized for stage readability (1280×720, 64-96px headlines).

| Type | Name | What It's For | Key Fields |
|------|------|---------------|------------|
| `title` | Title Slide | Hero opener — name, subtitle, speaker | title, subtitle, speaker |
| `section` | Section Divider | Break between major sections | title, subtitle |
| `text` | Simple Text | Bullet points or paragraphs | title, body |
| `text_and_image` | Text + Image | Split layout — text left, image right | title, body, image_path |
| `big_number` | Big Number | ONE massive stat as hero element | number, label, context |
| `comparison` | Comparison | Side-by-side (before/after, old/new) | title, left/right columns |
| `screenshot` | Screenshot | Full-width image with caption overlay | title, image_path, caption |
| `quote` | Quote | Large pull quote with attribution | quote_text, attribution |
| `timeline` | Timeline | Step-by-step process or chronology | title, steps[] |
| `qr_code` | QR Code | QR hero + CTA link + scan prompt | title, qr_image_path, link_text |
| `closing` | Closing / CTA | Final slide with links and contact | title, cta_text, links[], speaker |

> **AGENT: When generating a deck, select slide types based on the interview data.**
>
> **Mapping guide:**
> - Hook fact → `big_number` or `title`
> - Problem statement → `text`
> - What we built → `text` or `text_and_image` (with screenshot)
> - Results → `big_number` (for hero stat) + `text` (for detail)
> - Costs → `comparison` (old way vs new way)
> - Mistakes → `text` (with bullets)
> - Quote from user or testimonial → `quote`
> - Process/timeline → `timeline`
> - CTA with link/QR → `qr_code`
> - Closing → `closing`

## Generating Per-Slide HTML

For maximum visual control, generate each slide as its own HTML file:

```bash
python3 references/slide-templates.py \
  --theme terminal \
  --type big_number \
  --number "71" \
  --label "Leads Imported" \
  --context "In under 5 minutes" \
  --output ~/workspace/presentations/exports/slide_04.html
```

> **AGENT: When user asks for "beautiful slides" or "stage-ready slides" or "keynote quality":**
> 1. Ask which theme (show the menu above)
> 2. Generate the markdown deck first (for content)
> 3. Then generate per-slide HTML files using `slide-templates.py`
> 4. Each slide gets its own `.html` file in the exports folder
> 5. Tell user: "Your slides are individual HTML files in exports/. Open each in a browser — they're stage-ready at 1280×720."

## Combined Deck vs Per-Slide Files

| Approach | Best For | How |
|----------|----------|-----|
| **Combined deck** (`export-html-slides.py`) | Presenting from one file, quick sharing | Arrow keys navigate between slides |
| **Per-slide files** (`slide-templates.py`) | Maximum visual control, custom layouts per slide | Each slide is a standalone HTML file |
| **Both** | Best of both worlds | Generate per-slide for design, combined for presenting |

> **AGENT: Default to the combined deck for most users.** Only use per-slide when the user specifically wants individual files or asks for "beautiful" / "stage-ready" / "keynote-quality" slides.

---

## 🌐 HTML Slides (Recommended)

> **Zero dependencies** beyond Python 3 standard library. No pip installs.

Beautiful, self-contained HTML presentation you can:
- **Present directly** in any browser (full-screen, arrow key navigation)
- **Print to PDF** with pixel-perfect slide-per-page layout (Ctrl+P)
- **Share as a single file** — no server, no internet required
- **Toggle speaker notes** live during presentation (press N)

**3 built-in themes:**

| Theme | Vibe | Best For |
|-------|------|----------|
| `gradient` | Deep purple/teal, modern | Founder/startup audiences (DEFAULT) |
| `dark` | Navy/red, dramatic | Stage presentations, evening events |
| `light` | Clean white/blue | Corporate, enterprise audiences |

When user says "export as html", "make beautiful slides", "export for presenting", or similar:

```bash
~/workspace/presentations/helper.sh export-html {pres_id} gradient
```

> **AGENT: Ask about theme:**
> "Which vibe? **Gradient** (modern, default), **Dark** (dramatic stage look), or **Light** (clean corporate)?"

**HTML slide features:**
- ⌨️ Arrow keys / space to navigate slides
- 📱 Touch/swipe on mobile
- 🎙️ Press **N** to toggle speaker notes panel
- 🖨️ Print button — each slide = one page, notes hidden
- 📊 Progress bar at bottom
- 📐 Responsive — works on any screen size

> **After export:** "Your slides are at `exports/{name}.html`. Open in any browser to present. Press N for speaker notes. Print (Ctrl+P) for a beautiful PDF."

## 🟣 Gamma.app Export

> **Zero dependencies.** Pure shell script.

Exports clean markdown optimized for [Gamma.app](https://gamma.app) import. Gamma auto-designs your slides — you just provide the content.

**What the Gamma export does:**
- Strips all speaker notes (Gamma doesn't import them)
- Removes note-style blockquotes and metadata lines
- Cleans "Slide N:" prefixes from headings
- Each `##` heading becomes a Gamma "card"
- Pure content — Gamma auto-styles everything

When user says "export for gamma", "gamma export", "I want to use gamma":

```bash
~/workspace/presentations/helper.sh export-gamma {pres_id}
```

> **AGENT: After Gamma export, show these instructions:**
> "Your Gamma-ready file is at `exports/{name}_gamma.md`.
>
> To import into Gamma:
> 1. Go to **gamma.app** → **New** → **Paste text**
> 2. Paste the markdown content or upload the .md file
> 3. Gamma turns each heading into a designed card
> 4. Pick a theme and click **Generate**"

## PPTX Export

> **Requires:** `python3` + `python-pptx` (`pip install python-pptx`)

When user says "export as powerpoint" or "export pptx":

1. Check: `python3 -c "import pptx" 2>/dev/null`
2. If missing → "Install with: `pip install python-pptx`. Want me to try?"
3. If available → run `references/export-pptx.py`
4. Save to `~/workspace/presentations/exports/{pres_id}.pptx`

## PDF Export

> **Requires:** `pandoc` — OR use the HTML Print button (recommended)

When user says "export as pdf":

1. **Recommend HTML route first:** "The HTML slides have a built-in Print button that creates a beautiful PDF. Want to try that instead?"
2. If user wants pandoc: check `which pandoc`, run export
3. Save to `~/workspace/presentations/exports/{pres_id}.pdf`

## Export Comparison

| Format | Dependencies | Visual Quality | Best For |
|--------|-------------|---------------|----------|
| **Markdown** | None | Content only | Editing, version control, sharing |
| **HTML Slides** | Python 3 only | ⭐⭐⭐⭐⭐ | Presenting, printing, sharing as file |
| **Gamma** | None | Gamma designs it | Users who want AI-designed slides |
| **PPTX** | python-pptx | ⭐⭐⭐ | PowerPoint users, corporate |
| **PDF** | pandoc | ⭐⭐ | Static distribution |

---
---

# Data Structure

## Presentation Metadata (JSON)

Stored at `~/workspace/presentations/decks/{pres_id}.json`:

```json
{
  "presentation_id": "[generated 8-char hex]",
  "name": "[user-friendly name]",
  "created": "[ISO timestamp]",
  "updated": "[ISO timestamp]",
  "speaker": {
    "name": "[from interview]",
    "title": "[from interview]",
    "company": "[from interview]"
  },
  "audience": {
    "size": 0,
    "roles": [],
    "interests": [],
    "description": "[from interview]"
  },
  "angle": {
    "title": "[selected angle title]",
    "description": "[angle description]"
  },
  "tone": "conversational",
  "work": {
    "subject": "[what was built/done]",
    "timeline": "[how long it took]",
    "results": {},
    "costs": {},
    "mistakes": []
  },
  "resources": {
    "cta": "[primary call to action]",
    "links": [],
    "coupon_codes": []
  },
  "slides": [
    {
      "slide_number": 1,
      "slide_type": "title",
      "title": "[slide title]"
    }
  ],
  "validation": {
    "speculative_flags": 0,
    "projection_flags": 0,
    "verified_claims": 0,
    "last_validated": "[timestamp]"
  }
}
```

---
---

# Duplicate for Different Audiences

When user says "duplicate [name]" or "I need this for a different audience":

1. Copy the metadata JSON
2. Generate new `presentation_id`
3. Ask: "Same content, different audience? Tell me about the new audience."
4. Re-run Phase 2 (Audience) and Phase 5 (Angle) only
5. Re-generate the deck with new angle/tone
6. Save as a new presentation

This lets users create multiple versions of the same talk for different events.

---
---

# Configuration Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `defaults.tone` | string | conversational | professional / conversational / humorous / technical |
| `defaults.max_slides` | number | 20 | Maximum slides per deck |
| `defaults.include_speaker_notes` | boolean | true | Auto-generate speaker notes |
| `defaults.factual_validation` | boolean | true | Flag speculative language |
| `defaults.include_mistakes_slide` | boolean | true | Include authenticity slide |
| `defaults.include_costs_slide` | boolean | true | Include investment breakdown |
| `export.default_format` | string | html | Default export format |
| `export.html_theme` | string | spark | terminal / executive / spark / clean |
| `export.per_slide_html` | boolean | false | Generate individual HTML files per slide |
| `export.formats_available.*` | boolean | varies | Which export formats are ready |
| `speaker.*` | string | "" | Default speaker info (reused across decks) |
| `branding.cta_links` | array | [] | Default CTA links for all decks |
| `branding.training_links` | array | [] | Default training resource links |
| `branding.coupon_codes` | array | [] | Default coupon codes |

---
---

# Input Sanitization Rules

**⚠️ PRIMARY DEFENSE: The helper script (`~/workspace/presentations/helper.sh`) enforces sanitization in code.**

Secondary rules for edge cases:
1. **Strip shell metacharacters** from all user input before exec
2. **JSON writes** go through the helper's `save-meta` command with validation
3. **Heredocs** use quoted delimiters (`<< 'EOF'`) to prevent expansion
4. **Length limits:** Presentation name ≤ 100 chars, slide content ≤ 5000 chars per slide
5. **Never pass unsanitized user input to exec.** No exceptions.

---
---

# What This Skill Does NOT Do

- **Does NOT use external slide APIs.** References to `slide_initialize`, `slide_edit`, and `slide_present` in some OpenClaw guides are Manus-specific tools not available here. This skill generates HTML/Markdown files directly.
- **Does NOT make up numbers.** Every stat comes from your interview answers. Missing data gets a `[INSERT]` placeholder.
- **Does NOT predict the future.** Projections are conservative, caveated, and flagged for your review.
- **Does NOT replace practice.** A great deck with a bad delivery is still a bad presentation. Use the speaker notes.
- **Does NOT access files outside `~/workspace/presentations/`** without explicit permission.
- **Does NOT require internet for presenting.** HTML slides are self-contained (fonts are loaded from Google Fonts CDN but slides degrade gracefully without them).

---
---

## Why This Exists

Most presentations are built backwards. People open a template, fill in slides, and try to find a story. The result is generic decks with made-up projections and no soul.

AI Presentation Maker works forwards. You tell it what actually happened. It finds the story. Every number is real. Every claim is verified. Every mistake is included because authenticity sells better than perfection.

The interview takes 5 minutes. The deck takes 30 seconds. The refinement takes however long you want. And when you stand up to present, you know every word is true.

---

## Who Built This

**Jeff J Hunter** is the creator of the AI Persona Method and founder of the world's first AI Certified Consultant program.

He runs the largest AI community (3.6M+ members) and has been featured in Entrepreneur, Forbes, ABC, and CBS. As founder of VA Staffer (150+ virtual assistants), Jeff has spent a decade building systems that let humans and AI work together effectively.

AI Presentation Maker is part of the AI Persona ecosystem — the same system Jeff uses to build his own keynotes.

---

## Want to Make Money with AI?

Most people burn API credits with nothing to show for it.

This skill gives you the pitch deck. But if you want to turn AI into actual income, you need the complete playbook.

**→ Join AI Money Group:** https://aimoneygroup.com

Learn how to build AI systems that pay for themselves.

---

## Connect

- **Website:** https://jeffjhunter.com
- **AI Persona Method:** https://aipersonamethod.com
- **AI Money Group:** https://aimoneygroup.com
- **LinkedIn:** /in/jeffjhunter

---

## License

MIT — Use freely, modify, distribute. Attribution appreciated.

---

*AI Presentation Maker — Facts, not fantasies.* 🎤
