---
name: comms-md
description: "Create a COMMS.md — a structured, queryable document expressing someone's communication preferences for humans and agents. Use when: (1) someone wants to articulate how they communicate (style, channels, rhythms, tone), (2) someone wants a document other people's agents can read before reaching out, (3) someone says 'comms.md' or asks about communication preferences documents."
metadata:
  openclaw:
    version: "1.0.0"
    author: "stedman"
    related:
      - comms-md-reader
---

# COMMS.md Creator

Generate a structured communication preferences document through guided conversation.

## What COMMS.md Is

A queryable personal document that expresses how someone communicates: their natural style, channel preferences, availability rhythms, async voice, and interaction protocols. Designed to be read by both humans and agents before initiating contact.

## Workflow

### 1. Orient

Explain the concept briefly:

> "A COMMS.md is a structured doc that captures how you communicate — your style, when you're available, which channels you prefer, how you write in different contexts. Think of it as a user manual for reaching you. Other people (or their agents) can reference it before getting in touch."

### 2. Interview

Walk through these areas conversationally. Don't dump all questions at once — do 2-3 per turn, adapt based on answers, skip what's clearly not relevant.

**Style & strengths** (start here — it's introspective and sets the tone):
- What comes naturally when you communicate? (e.g. brevity, storytelling, humor, directness)
- What requires effort? (e.g. small talk, follow-through, emotional labor, context-switching)
- Where does communication break down for you?

**Collaboration model:**
- What kind of people do you work best with?
- How do you prefer to set up working relationships?

**Weekly rhythm:**
- Walk through their week: energy, availability windows, protected time
- Which days are meeting-heavy? Which are deep work?

**Sync philosophy:**
- What are calls for? What are they NOT for?
- How tactical vs. strategic do calls get?

**Channel preferences:**
- For each situation type (urgent, professional, casual, etc.): what channel, what timing?
- Role of email vs. text vs. voice notes vs. calls?
- How does closeness change channel choice?
- Notification habits, response triage, focus mode patterns

**Async voice** (this section often needs the most drawing out):
- How do they write to close friends vs. professional contacts?
- Capitalization, punctuation, emoji habits?
- What do they never do in writing? (anti-patterns)
- How do they handle outreach to new people? Re-engaging after silence?
- Do they have a gap between how competent they are and how warm they read? How do they bridge it?

**Boundaries:**
- What's the fastest way to annoy them?
- What should people never do?

### 3. Draft

Read `references/comms-template.md` for the output structure. Generate the COMMS.md using the template, filling in sections from the interview. Use the person's own words and phrasing where possible.

For reference on what a completed COMMS.md looks like, see `references/example.md`.

### 4. Review and Iterate

Present the draft and ask what feels off, what's missing, what's too specific or too vague. Expect 1-2 revision rounds. Common adjustments:
- Tone too formal or too casual for how they actually talk
- Missing a channel or context they care about
- Weekly rhythm needs more nuance
- Anti-patterns section needs real examples

### 5. Place the Document

Ask where they want it saved. Common locations:
- Personal website (for public/professional use)
- Notes app or vault (Obsidian, Notion, etc.)
- Workspace docs (for team use)

## Related Skills

- **comms-md-reader** — the companion skill for reading and adapting to someone else's COMMS.md when drafting outreach

## Guidelines

- **Use their voice.** The doc should sound like them, not like a template. Mirror their register.
- **Earn specificity.** Generic preferences ("I prefer email for professional stuff") are less useful than specific ones ("Email for intros beyond close friends and anything they'll need to find later").
- **Skip irrelevant sections.** Not everyone has a weekly rhythm to document or sync philosophy to articulate. Leave out what doesn't apply rather than filling with filler.
- **The Async Voice section is the highest-value section for agent consumption.** Spend extra time here. This is what another agent reads to calibrate tone when drafting a message to this person.
- **Version the output.** Include `Version 0.1` at the bottom so they can track iterations.
