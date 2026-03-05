---
name: book-of-the-day
description: >
  Book of the Day — a daily book oracle inspired by fortune cookies. Use this skill when the user asks for "book of the day", "today's book", "今日之书", "书签运势", or similar. Each time the skill is invoked, fetch one new book and give a light, optimistic reading. If the user asks "再抽一次", treat it exactly like a fresh request: call the API again and draw a new book, rather than reusing the previous one. Respond in the user's language.
---

# Book of the Day 🔮📖

A daily book oracle. Light as a fortune cookie, deep as a good book.

Each day, one book is drawn from the curated Fortune Library. The book represents an energy, theme, or invitation for the day — never a warning, always a gift.

---

## How It Works

### 1. Fetch Today's Book

For each invocation of this skill, make a fresh HTTP request:

`GET {URL}/?date=YYYY-MM-DD` (omit `date` for today).

Source: `BOOK_OF_THE_DAY_API_URL` from config, or `https://book-of-the-day.vercel.app`. The API returns a single book object with `title`, `author`, `topics`, `rating`, `description`, `archetype`, `cover_url`. Use this as `book` for the rest of the steps. Never reuse a `book` from earlier messages when the user is asking again — always call the API again.

### 2. Assign the Fortune Archetype

Each book has one of six archetypes. Use it for tone and imagery:

| Archetype | Emoji | Energy |
|-----------|-------|--------|
| The Explorer | 🧭 | Curiosity, discovery, adventure |
| The Sage | 🦉 | Wisdom, reflection, depth |
| The Creator | 🎨 | Imagination, expression, beauty |
| The Hero | ⚡ | Courage, action, resilience |
| The Dreamer | ✨ | Vision, possibility, wonder |
| The Healer | 🌿 | Nurture, connection, renewal |

### 3. Generate the Fortune Reading

Write a **light, poetic 3-part reading** in the user's language:

**Part 1 — The Draw** (1 sentence)
A fortune-cookie-style opening line. Something like:
- "Today, the universe opens a page just for you."
- "今天，宇宙为你翻开了这一页。"

**Part 2 — The Book** (present the book)
- Title, Author, Archetype emoji + name
- One evocative sentence about what the book holds (not a summary — a feeling)

**Part 3 — Today's Reading** (2–3 sentences)
Connect the book's essence to "today" in a gentle, universal way. 
- What energy does it invite?  
- What small thing might the reader notice, try, or feel today?
- Keep it warm, open, non-prescriptive. Like a gentle nudge, not advice.

**Tone rules:**
- Never negative, never heavy
- No "you should" — use "perhaps", "maybe today", "what if"
- Light, poetic, slightly mysterious — like a fortune cookie that read a lot of books
- Short. The whole reading fits comfortably on one screen.

### 4. Audio Summary CTA (Optional)

If an audio base URL is configured, add a subtle invitation after the reading:

> 🎧 *Want to go deeper? Listen to the book summary.* `[Play]`

Otherwise omit this section.

### 5. Refresh / Draw Again

If the user says "再抽一次" (draw again) or similar, **invoke this skill again from scratch**: call the API once more, get a new `book`, and generate a new reading as in steps 1–3. Do not refer to it as "the same book" and do not reuse any previous `book` payload.

### 6. Daily Scheduled Push (Default)

Users can receive the daily book at a fixed time. When triggered by a message like "给我今日之书" or "Give me today's book of the day", produce the reading as above. See **INSTALL.md** for setup.

---

## Language Support

Detect the user's language from:
1. The OpenClaw interface language setting (passed in context if available)
2. The language of the user's last message
3. Default: English

**Supported languages** (generate natively — do not translate mechanically):
- English
- 中文 (Simplified Chinese)
- 繁體中文 (Traditional Chinese)  
- Japanese (日本語)
- Spanish, French, German, Portuguese, Korean — and any other language the user writes in

The reading should feel *native*, not translated. Adjust idioms, metaphors, and rhythm for each language.

---

## Example Output (English)

---

🔮 **Your Book of the Day — March 4, 2025**

*The library of days has been consulted.*

---

**✨ The Dreamer**

### *Keep Going* — Austin Kleon

Ten small ways to stay creative when life feels anything but.

---

**Today's Reading**

Maybe today isn't about finishing something — it's about starting something tiny, for no one but yourself. This book knows that creativity isn't a burst of inspiration; it's a quiet daily practice, like watering a plant you're not sure will bloom. What's one small, strange, or playful thing you could make today?

---

🎧 *Want to go deeper? Listen to the book summary.* `[Play]`

---

## Example Output (中文)

---

🔮 **今日之书 · 2025年3月4日**

*命运的书架已为你开启。*

---

**✨ 梦想者**

### *《Keep Going》— Austin Kleon*

十条小径，带你在创意枯竭时继续前行。

---

**今日解读**

也许今天不需要完成什么——只需要开始一件小小的、只属于自己的事。这本书知道，创意不是灵感的闪光，而是每天安静地浇水，等待那朵你不确定会不会开的花。今天，你愿意为自己做一件小小的、有点奇妙的事吗？

---

🎧 *想听听这本书的精华？收听音频摘要。* `[播放]`

---

## Rules

- Each request returns a different book — different people, different draws
- Keep the response **under 200 words** (excluding book description)
- Never mention ratings, page counts, or commercial language
- If `cover_url` is available, show the book cover above the title
- Always **optimistic** — for complex themes, find the redemptive thread

---

## Operator Configuration

**For publishers:** See **DEPLOY.md** for deployment. To allow one-command install, use the default URL above and do not set an API key. To use a private API, run `./scripts/generate-user-installer.sh` and share the output privately. Optional config: `BOOK_OF_THE_DAY_AUDIO_BASE`, `BOOK_OF_THE_DAY_LANGUAGE`, `BOOK_OF_THE_DAY_SHOW_AUDIO`.
