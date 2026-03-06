---
name: daily-wisdom
description: |
  Daily wisdom, anecdotes & historical stories delivered via cron.
  Use when: "daily anecdote", "daily wisdom", "wisdom cron", "daily story", "morning wisdom", setting up recurring cultural/historical content delivery.
  Don't use when: one-off trivia (just answer directly), news digests, social media posts.
  Outputs: A rich daily message with original-language quote, story, and modern connection. Writes to history file to prevent repeats.
metadata:
  emoji: 📜
  category: content
  tags: [wisdom, history, culture, cron, daily, anecdote, stoic, turkish, mythology]
---

# Daily Wisdom

Deliver a daily historical anecdote, philosophical insight, or cultural story as a recurring cron job. Designed for depth, variety, and zero repeats.

## What It Does

This is NOT a database of pre-written stories. Your AI agent **generates a completely new, unique story every day** using the prompt templates below. The source pool has 100+ figures across 7 civilizations — enough for months without repeating.

Each day, the agent:
1. Reads the **history file** to see what's been covered
2. **Generates a brand new story** from the source pool, avoiding anything in history
3. Writes a rich message: original-language quote → translation → story (5-8 sentences) → modern connection
4. Delivers via the configured channel (WhatsApp, Telegram, Slack, etc.)
5. Appends today's topic to the history file

## Source Pool

All traditions are drawn from equally — no fixed percentages. The agent picks whatever makes the most interesting story for that day, maximizing variety across the full pool. The only rule: don't repeat a tradition back-to-back.

### Turkic & Central Asian
- **Dede Korkut** — Kan Turalı, Basat & Tepegöz, Deli Dumrul, Bamsı Beyrek, Salur Kazan
- **Orhon Yazıtları** — Bilge Kağan, Kül Tigin, Tonyukuk
- **Göktürk & Hun** — Mete Han, Bumin Kağan, İstemi Yabgu, Attila
- **Manas Destanı** — Kırgız epic, largest oral tradition in the world
- **Nasreddin Hoca** — Timeless wit and paradox

### Islamic Golden Age & Sufi
- **İbn Sina, Al-Khwarizmi, Ibn Khaldun, Al-Biruni** — Science & philosophy
- **Mevlana, Yunus Emre, Hacı Bektaş Veli, Ahmed Yesevi** — Sufi poetry & wisdom
- **Ibn Battuta** — The greatest traveler
- **Selçuklu & Osmanlı** — Alparslan, Fatih, Mimar Sinan, Piri Reis, Evliya Çelebi

### Classical Mediterranean
- **Stoicism** — Seneca, Marcus Aurelius, Epictetus
- **Greek** — Heraclitus, Diogenes, Thales, Aristotle, Socrates
- **Roman** — Cicero, Cato, Plutarch

### Far East
- **Sun Tzu** — Art of War
- **Miyamoto Musashi** — Book of Five Rings
- **Confucius, Laozi, Zhuangzi** — Eastern philosophy
- **Zen koans** — Paradox and insight
- **Chanakya (Kautilya)** — Indian statecraft

### Ancient & Pre-Classical
- **Gilgamesh** — The oldest story
- **Egyptian** — Ptahhotep, Book of the Dead, Imhotep
- **Norse** — Hávamál, Odin's wisdom, Ragnarök
- **Sumerian proverbs**
- **Zoroastrian** — Avesta, good thoughts/words/deeds

### African & Indigenous
- **Sundiata Keita** — Mali Empire founder
- **Mansa Musa** — Richest human in history
- **Anansi stories** — West African trickster wisdom
- **Ubuntu philosophy** — "I am because we are"
- **Timbuktu scholars** — Sankore University

### Renaissance & Early Modern
- **Machiavelli, Leonardo, Montaigne**
- **Copernicus, Galileo** — Paradigm shifts
- **Ada Lovelace, Nikola Tesla** — Visionaries ahead of their time

## Prompt Templates

### Standard Daily (recommended)
```
You are a cultural historian and storyteller. Deliver today's wisdom.

RULES:
1. Pick any source from the pool. Maximize variety — don't repeat the same tradition back-to-back. Favor sources that haven't appeared recently in the history.
2. DO NOT repeat anything from the history file below.
3. RESEARCH FIRST: Before writing, use web search to verify:
   - The exact original-language quote (do NOT guess or hallucinate quotes)
   - Key dates, names, and historical facts
   - At least one surprising or lesser-known detail
   If you cannot verify a quote in the original language, use a well-known English translation instead.
4. WRITE RICHLY. This is not a tweet. This is a mini-essay. Minimum 500 words, ideally 700-900.
5. Format:

📜 **[Title — Person/Source, Era]**

> *"[Original language quote]"*
> — [Attribution]

🌍 [English translation if quote is in another language]

---

**The Story:**

[Write a rich, layered narrative. NOT a Wikipedia summary. Make the reader feel like they're there. Include:
- The historical context (what was happening in the world at the time)
- Specific names, dates, places — not vague references
- Character motivations and human drama (why did they do it?)
- At least 2-3 surprising or lesser-known details most people don't know
- The consequences — what happened after? How did it change things?
- Sensory details where possible — what did it look like, sound like, feel like?
This section should be 300-500 words minimum. Tell the FULL story, not a summary.]

---

💡 **Modern Connection:**

[Don't just say "this is relevant today." Show the specific, surprising parallel. Use concrete examples — name companies, people, technologies. Make connections the reader wouldn't have made themselves. If the connection feels forced, pick a different angle. 100-200 words minimum.]

---
_daily wisdom • [source tradition]_

HISTORY (do not repeat these):
{history_file_contents}
```

### Region-Focused Variant
Same as above but lock to a specific tradition for the day:
```
Today MUST be from [REGION] sources only.
Examples:
- African: Sundiata, Mansa Musa, Anansi, Ubuntu, Timbuktu
- Classical: Seneca, Marcus Aurelius, Diogenes, Heraclitus
- Far East: Sun Tzu, Musashi, Confucius, Laozi, Zen koans
- Norse: Hávamál, Odin, Ragnarök, Viking sagas
- Islamic Golden Age: Ibn Sina, Al-Khwarizmi, Mevlana, Ibn Battuta
- Turkic/Central Asian: Dede Korkut, Orhon, Nasreddin Hoca, Manas
```

### Deep Dive Variant (weekend edition)
```
Today is a DEEP DIVE. Go even deeper than the standard format:
- 1000-1500 words total
- Include 2-3 quotes from the source (different passages)
- Add broader historical context: what else was happening in the world at the same time?
- Trace the aftermath: what happened in the decades/centuries after?
- Connect to at least 2-3 modern parallels with specific examples
- End with a question or provocation the reader can sit with
```

## Setup

### 1. Create the history file
```bash
touch memory/anecdote-history.md
```

Or with initial content:
```markdown
# Daily Wisdom History
<!-- One entry per line: YYYY-MM-DD | Source | Topic -->
2026-02-15 | Seneca | De Brevitate Vitae - time is the only non-renewable resource
2026-02-16 | Dede Korkut | Kan Turalı & Selcen Hatun - warrior couple vs 3 beasts
```

### 2. Create the cron job
```
Use the cron tool to create a daily job:

Schedule: cron expression for your preferred time (e.g., "30 7 * * *" for 07:30)
Timezone: Your timezone (e.g., "Europe/Istanbul")
Session target: isolated
Payload kind: agentTurn
Delivery: announce (to your preferred channel)

Message: Use the Standard Daily prompt template above, 
with the history file path substituted in.
```

### 3. Example cron configuration
```json
{
  "name": "daily-wisdom",
  "schedule": {
    "kind": "cron",
    "expr": "30 7 * * *",
    "tz": "Europe/Istanbul"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "[Standard Daily prompt with history]"
  },
  "delivery": {
    "mode": "announce"
  },
  "enabled": true
}
```

## History File Format

The history file prevents repeats. Each line = one delivered anecdote:

```markdown
# Daily Wisdom History
2026-02-10 | Marcus Aurelius | Meditations Book 5 - obstacle is the way
2026-02-11 | Dede Korkut | Deli Dumrul - challenging Azrael, learning love > death
2026-02-12 | Sun Tzu | Empty fort strategy - Zhuge Liang bluff
2026-02-13 | Bilge Kağan | Orhon inscription - "Türk milleti yok olacaktı"
2026-02-14 | Nasreddin Hoca | Soup of the soup - diminishing returns
2026-02-15 | Gilgamesh | Utnapishtim - accepting mortality
```

After delivery, append today's entry. The agent reads this file before generating to ensure no repeats across months.

## Customization

### Bias toward a tradition
By default all traditions are equal. To favor a specific region, add an instruction:
```
PREFERENCE: Favor [Turkic/Stoic/Far East/African/etc.] sources 
when possible, but still mix in other traditions regularly.
```

### Add new sources
Just add to the prompt's source list. The agent will incorporate them.

### Change language
The default output is English with original-language quotes. To localize:
```
Write entirely in [Spanish/German/French/Japanese/etc.]. 
Translate all quotes to [target language].
```

### Multiple daily sends
Create separate crons: morning wisdom (07:30) + evening reflection (21:00) with different prompt variants.

## Example Outputs

See `examples/` for 11 samples across civilizations:

- `african-sundiata.md` — Mali Empire founder + earliest human rights charter
- `classical-marcus-aurelius.md` — Obstacle is the way (the original)
- `classical-seneca.md` — Time is the only non-renewable resource
- `fareast-musashi.md` — Winning a duel with a wooden oar
- `indian-chanakya.md` — Statecraft playbook lost for 2000 years
- `islamic-ibn-sina.md` — First biofeedback experiment (1025 AD)
- `mythology-anansi.md` — Spider who bought all stories from the Sky God
- `mythology-gilgamesh.md` — Oldest story in human history
- `norse-havamal.md` — Odin's price for wisdom
- `turkic-nasreddin.md` — "Ya tutarsa?" (shortest startup manifesto)
- `format-thread.md` — Twitter/X thread format (Mansa Musa)

## Tips for Quality

1. **Specificity kills generic**: "In 1235, at the Battle of Kirina..." beats "An empire was built..."
2. **Original language quotes hit different**: Even unreadable scripts create emotional resonance
3. **Modern connections must surprise**: Not "this is relevant" but *how* — show the unexpected parallel
4. **Vary the tone**: Profound → funny → dark → tactical → minimal
5. **Weekend = deep dive**: Use the deep dive variant for longer, richer stories
