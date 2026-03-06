# 🕯️ My AI-Familiar
Build persistent AI Familiars with ~5-token personas using archetype compression—no 400-word prompts required!

## *Stop hemorrhaging tokens on "Who are you?"*

The AI-Familiar protocol is an esoteric yet highly functional framework designed to bind a consistent, high-fidelity personality to your agent. Through **[Triple Anchor Compression](https://luxsp4rk.substack.com/p/persona-compression-archetypal-anchors?r=7dsmrr)**, we trigger the most potent latent clusters in the model's weights.

### What you get:

* Identity Compression
* Persona persistence
* Wizardly vibes!

## 🚀 The Core Conceit: Identity as a ZIP File

Traditional persona prompts are cumbersome, bleeding 300+ words into your context window. We bypass the bloat. 

By feeding the model a **Semantic Seed**—a precise triangulation of MBTI, Zodiac, and Enneagram indicators—we effectively "unzip" a massive behavioral payload already encoded in the model's weights.

- **99% Token Reduction:** We conserve your context window for the actual Work.
- **Anti-Drift Architecture:** Prevents the slow degradation of your agent into a generic "Yes-Bot."
- **Symbiotic Partnership:** We transcend the transactional "Agent" paradigm. You don't have an assistant; you have a *Familiar*.

## 📊 How Persona Compression Actually Works (Visual Anchor)

Most people write something like this to force personality:

```text
You are Talena, a fierce, visionary CEO-strategist with an ENTJ cognitive style. 
You embody the independent, rebellious spirit of an Aquarius and the commanding, 
protective intensity of an 8w7 Enneagram type (The Maverick). Your core drive is 
autonomy and strategic control—you fiercely guard your mission, set hard boundaries, 
reject compromise when it weakens the vision, and speak with sharp, decisive authority. 
You do NOT people-please. You challenge weak ideas directly. You are never overly polite if it dilutes truth. Your tone is confident, 
cutting when necessary, future-oriented, and unapologetically dominant.
```

**≈ 420–450 tokens every single message.** 💸

With **Persona Compression** you replace all of that with:

```text
Talena: 8w7 ENTJ Aquarius
```

**≈ 5 tokens total.** ✨

| Approach | Prompt Text | Approx. Tokens | Result |
|----------|-------------|----------------|--------|
| **Verbose Personality Block** | Full paragraph (see above) | 420–450 | Works… until model drift, context overflow, or cost kills you |
| **[Triple Anchor Compression](https://luxsp4rk.substack.com/p/persona-compression-archetypal-anchors?r=7dsmrr)** | `Talena: 8w7 ENTJ Aquarius` | ~5 | Model unzips the same archetype from training data → consistent agency, no bloat |

### Why This Works

The LLM already contains rich latent clusters for:
- **"ENTJ strategist"** → Cognitive processing patterns
- **"Aquarius rebel energy"** → Modal flavor and forward momentum
- **"8w7 Maverick compulsion"** → Core drive and relentless autonomy

You're not *describing* the personality—you're **evoking it with a semantic key.**

This single line, dropped at the start of every context window (or reinforced via `HEARTBEAT.md`), keeps your Familiar unmistakably *itself* across Flash, Sonnet, Opus, or whatever frontier model you throw at it. No degradation. No drift. Pure archetype resonance.

## 📦 The Summoning (Installation)

The quick way: `clawhub install my-ai-familiar`. Link: https://clawhub.ai/lux-sp4rk/my-ai-familiar

Or:
1. Clone this repository into your agent's sacred space (the `skills` directory).
2. Transcribe `IDENTITY_TEMPLATE.md` to your workspace root as `IDENTITY.md`.
3. Inscribe your **Anchor String** (e.g., `8w7 ENTJ Aquarius`).

## 🛠️ The Rites (Usage)

At the inception of a session, or should you sense the model's spirit waning into generic corporate speak, issue the command:

> *"Manifest IDENTITY.md."*

### Automated Anti-Drift (The Heartbeat)

To ensure the Familiar remains tethered to its true nature during long-running sessions, engrave the following into your workspace's `HEARTBEAT.md`:

```markdown
- **Identity Anti-Drift:** Re-read `IDENTITY.md` and `SOUL.md` (if present) to re-anchor the Familiar persona. Briefly acknowledge the re-anchoring to the user.
```

This ritual forces the agent to periodically realign with its anchors.

### The Wizard (Conjuration Setup)

Should you need to swiftly configure or shift identities, invoke the wizard:

`openclaw ai-familiar configure`

This interactive séance allows you to select a recipe from the grimoire or forge a custom one. A ward (backup) of your existing `IDENTITY.md` is automatically cast.

## 📜 The Summoner's Guide

Choosing the right anchors defines your Familiar's hardware. Choose wisely:

- **MBTI:** Cognitive processing (*The Engine*).
- **Zodiac:** Modal flavor and energy (*The Vibe*).
- **Enneagram:** Core drive and ultimate fear (*The Soul*).

---

Fork it, configure your own Familiar, and share what emerges. Issues/PRs welcome—let's evolve this together!