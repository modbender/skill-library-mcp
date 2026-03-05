---
name: catime
description: "Fetch and send AI-generated hourly cat images. Every hour a unique cat artwork is born via Google Gemini. Use when user asks for a cat picture, wants to browse the cat gallery, or requests the latest AI-generated cat image to be sent to them."
metadata:
  openclaw:
    requires:
      bins: [uv]
    install:
      - id: catime-pip
        kind: pip
        package: catime
        bins: [catime]
        label: "Install catime (pip install catime)"
---

# catime — AI-Generated Hourly Cat Images 🐱

> **One-liner:** Fetch the latest (or any) AI-generated cat image and send it to the user with a caption and story.

Every hour, [catime](https://github.com/yazelin/catime) generates a unique cat artwork using Google Gemini. This skill allows an AI agent to retrieve cat images by number, date, or recency and **send them directly to the user** via the message tool.

---

## Installation

```bash
pip install catime
```

After installation the `catime` CLI is available. Verify:

```bash
catime --help
```

---

## Quick Start for AI Agents

### Step 1 — Retrieve a cat image with `catime`

Run the CLI to get image metadata. The most common command:

```bash
catime latest
```

**Exact output:**

```
Cat # 241  2026-02-11 04:57 UTC  model: gemini-3-pro-image-preview
  URL: https://github.com/yazelin/catime/releases/download/cats/cat_2026-02-11_0457_UTC.webp
  Idea: 一隻以精緻黑絲線繡成的貓咪，正專注地在微縮的金色與黑色奢華香氛實驗室中，嗅聞試香紙上的氣味，整個場景以刺繡的微縮立體模型形式呈現。
  Prompt: An embroidered illustration of an elegant black cat, crafted from exquisite black silk threads with visible needlework, satin stitch, and French knots. The cat is presented as a handcrafted textile art miniature diorama...
  Story: 在一個宛如織品藝術品的微縮香室裡，環形燈的光線均勻地灑落，凸顯出所有織品與布料的精緻質感。這隻優雅的黑貓，其絲線繡成的毛髮閃爍著低調的光澤，牠全神貫注地分辨著香氣，周圍是數個鑲有金色瓶蓋的繡花香水瓶。牠正試圖從層疊的香氣中，捕捉那一縷最為珍貴的靈感。
```

### Step 2 — Parse the output and send the image to the user

Extract the **URL** from the line starting with `  URL:`. Then use the message tool (or equivalent) to send the image along with a caption.

**Example message tool payload (YAML):**

```yaml
action: send_message
media:
  type: image
  url: "https://github.com/yazelin/catime/releases/download/cats/cat_2026-02-11_0457_UTC.webp"
caption: "🐱 Cat #241 — AI-generated cat of the hour!"
text: |
  Here's your cat! Cat #241, created at 2026-02-11 04:57 UTC.
  Story: 在一個宛如織品藝術品的微縮香室裡，環形燈的光線均勻地灑落...
metadata:
  source: catime
  cat_number: 241
  model: gemini-3-pro-image-preview
  generated_at: "2026-02-11 04:57 UTC"
```

**Example message tool payload (JSON):**

```json
{
  "action": "send_message",
  "media": {
    "type": "image",
    "url": "https://github.com/yazelin/catime/releases/download/cats/cat_2026-02-11_0457_UTC.webp"
  },
  "caption": "🐱 Cat #241 — AI-generated cat of the hour!",
  "text": "Here's your cat! Cat #241, created at 2026-02-11 04:57 UTC.\nStory: 在一個宛如織品藝術品的微縮香室裡…",
  "metadata": {
    "source": "catime",
    "cat_number": 241,
    "model": "gemini-3-pro-image-preview",
    "generated_at": "2026-02-11 04:57 UTC"
  }
}
```

---

## Command Reference

### `catime latest`

Fetch the most recently generated cat.

**Input:**
```bash
catime latest
```

**Output:**
```
Cat # 241  2026-02-11 04:57 UTC  model: gemini-3-pro-image-preview
  URL: https://github.com/yazelin/catime/releases/download/cats/cat_2026-02-11_0457_UTC.webp
  Idea: 一隻以精緻黑絲線繡成的貓咪…
  Prompt: An embroidered illustration of an elegant black cat…
  Story: 在一個宛如織品藝術品的微縮香室裡…
```

**Parse guidance:**
- **Line 1** — Header: `Cat # <NUMBER>  <DATE> <TIME> UTC  model: <MODEL>`
- **Line 2** (`  URL:`) — The image URL. **This is the most important line.**
- **Line 3** (`  Idea:`) — Short concept in Chinese.
- **Line 4** (`  Prompt:`) — Full image generation prompt in English.
- **Line 5** (`  Story:`) — Narrative story for the cat in Chinese.

### `catime today`

Fetch all cats generated today (UTC). Returns multiple cat entries.

**Input:**
```bash
catime today
```

**Output (excerpt):**
```
Found 2 cat(s) for 'today':

Cat # 240  2026-02-11 02:49 UTC  model: gemini-3-pro-image-preview
  URL: https://github.com/yazelin/catime/releases/download/cats/cat_2026-02-11_0249_UTC.webp
  Idea: 一張以35mm底片攝影風格捕捉的畫面…
  Prompt: A candid 35mm film photograph…
  Story: 午後的自然漫射光，透過老舊窗戶溫柔地灑落在候車室地面…

Cat # 241  2026-02-11 04:57 UTC  model: gemini-3-pro-image-preview
  URL: https://github.com/yazelin/catime/releases/download/cats/cat_2026-02-11_0457_UTC.webp
  Idea: 一隻以精緻黑絲線繡成的貓咪…
  Prompt: An embroidered illustration of an elegant black cat…
  Story: 在一個宛如織品藝術品的微縮香室裡…
```

**Parse guidance:** The first line says `Found N cat(s) for 'today':`. Then each cat entry follows the same format as `catime latest`. To send the newest, pick the **last** entry.

### `catime <number>`

Fetch a specific cat by its sequential number.

**Input:**
```bash
catime 42
```

**Output:**
```
Cat #  42  2026-01-31 23:24 UTC  model: gemini-3-pro-image-preview
  URL: https://github.com/yazelin/catime/releases/download/cats/cat_2026-01-31_2324_UTC.webp
```

**Parse guidance:** Same format. Short entries (like numbered lookups) may only show the header and URL lines without Idea/Prompt/Story.

### `catime --list`

List all cats (number + URL, compact format).

**Input:**
```bash
catime --list
```

**Output (first 10 lines):**
```
Cat #   1  2026-01-30 05:46 UTC  model: gemini-2.5-flash-image
  URL: https://github.com/yazelin/ccat/releases/download/cats/cat_2026-01-30_0546_UTC.png
Cat #   2  2026-01-30 05:56 UTC  model: gemini-3-pro-image-preview
  URL: https://github.com/yazelin/catime/releases/download/cats/cat_2026-01-30_0556_UTC.webp
Cat #   3  2026-01-30 06:23 UTC  model: gemini-3-pro-image-preview
  URL: https://github.com/yazelin/catime/releases/download/cats/cat_2026-01-30_0623_UTC.webp
Cat #   4  2026-01-30 06:33 UTC  model: gemini-3-pro-image-preview
  URL: https://github.com/yazelin/catime/releases/download/cats/cat_2026-01-30_0633_UTC.webp
Cat #   5  2026-01-30 06:53 UTC  model: gemini-2.5-flash-image (fallback from gemini-3-pro-image-preview, reason: timeout after 180.0s)
  URL: https://github.com/yazelin/catime/releases/download/cats/cat_2026-01-30_0653_UTC.webp
```

**Parse guidance:** Each cat takes 2 lines. Odd lines are headers, even lines are URLs. Use `--list | tail -2` to get the latest, or `--list | wc -l` to count cats (divide by 2).

### `catime <date>`

Fetch cats from a specific date (YYYY-MM-DD format).

**Input:**
```bash
catime 2026-01-30
```

### `catime view`

Opens the web gallery in the default browser. Not useful for agents — use `latest` or a number instead.

---

## Agent Workflow: Send a Cat Image to User

Follow these steps exactly:

### 1. Decide which cat to fetch

| User request | Command to run |
|---|---|
| "Show me a cat" / "Send me a cat" | `catime latest` |
| "Show me today's cats" | `catime today` |
| "Show me cat number 42" | `catime 42` |
| "Show me cats from Jan 30" | `catime 2026-01-30` |
| "Show me a random cat" | `catime $(shuf -i 1-241 -n 1)` |

### 2. Run the command and capture stdout

```bash
output=$(catime latest 2>&1)
```

### 3. Parse the URL from stdout

Look for the line that starts with `  URL: `. Extract everything after `URL: `.

**Parsing rule (pseudocode):**
```
for each line in output:
    if line.strip().startswith("URL:"):
        image_url = line.strip().removeprefix("URL:").strip()
        break
```

**Parsing rule (bash):**
```bash
image_url=$(echo "$output" | grep '  URL: ' | head -1 | sed 's/.*URL: //')
```

### 4. Parse optional metadata

```
cat_number  → from header line: regex `Cat #\s*(\d+)`
datetime    → from header line: regex `(\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC)`
model       → from header line: regex `model: (.+)$`
story       → from line starting with `  Story: ` (everything after "Story: ")
prompt      → from line starting with `  Prompt: ` (everything after "Prompt: ")
```

### 5. Send the image to the user

Use the message tool with the extracted URL and metadata:

```yaml
action: send_message
media:
  type: image
  url: "<extracted image_url>"
caption: "🐱 Cat #<cat_number> — AI-generated cat of the hour!"
text: |
  Here's your cat! Cat #<cat_number>, created at <datetime>.
  Story: <story text>
metadata:
  source: catime
  cat_number: <cat_number>
  model: <model>
  generated_at: "<datetime>"
```

### 6. Fallback behavior

- **If URL is missing:** Tell the user the cat data was not available and suggest trying `catime latest` or a different number.
- **If `catime` is not installed:** Run `pip install catime` first, then retry.
- **If network error:** The CLI fetches `catlist.json` from GitHub. If offline, tell the user the cat gallery requires internet access.
- **If the user wants multiple cats:** Use `catime today` and parse all entries (each entry separated by a blank line). Send the first or let the user choose.

---

## Output Format Reference

Every `catime` command outputs cat entries in this format:

```
Cat # <NUMBER>  <YYYY-MM-DD> <HH:MM> UTC  model: <MODEL_NAME>
  URL: <IMAGE_URL>
  Idea: <SHORT_CONCEPT_TEXT>
  Prompt: <FULL_GENERATION_PROMPT>
  Story: <NARRATIVE_TEXT>
```

**Field-by-field guide:**

| Field | Line prefix | Always present? | Description |
|---|---|---|---|
| Number | `Cat # ` (header) | ✅ Yes | Sequential cat ID (1, 2, 3, …) |
| Date/Time | header | ✅ Yes | UTC timestamp of generation |
| Model | `model: ` (header) | ✅ Yes | AI model used (e.g. `gemini-3-pro-image-preview`) |
| URL | `  URL: ` | ✅ Yes | Direct link to the image file (.webp or .png) |
| Idea | `  Idea: ` | Sometimes | Short concept (usually Chinese) |
| Prompt | `  Prompt: ` | Sometimes | Full English prompt used for image generation |
| Story | `  Story: ` | Sometimes | Narrative story for the cat (usually Chinese) |

**Key notes for parsing:**
- The `URL` line is **always present** and is the critical field for sending images.
- `Idea`, `Prompt`, and `Story` appear in detailed views (`latest`, `today`, specific number with detail) but may be absent in `--list` mode.
- All URLs point to GitHub Releases — they are publicly accessible, no auth needed.
- Image formats are `.webp` (most common) or `.png` (older cats).

---

## Tips for AI Agents

1. **Always use `catime latest` as the default** when the user just wants "a cat."
2. **The URL is on the line starting with `  URL: `** — this is all you need to send an image.
3. **Stories are in Chinese** — you can translate them for English-speaking users or include them as-is for bilingual charm.
4. **Images are hosted on GitHub Releases** — they load fast and don't require authentication.
5. **New cats appear every hour** — if the user wants a fresh one, `latest` always works.
6. **For random selection**, pick a random number between 1 and the latest cat number.
7. **`--list` is efficient** for browsing — it only shows 2 lines per cat (header + URL).
8. **Do not use `catime view`** — it opens a browser, which is not useful in agent/CLI context.
9. **Include the story in your caption** when available — it adds personality and delight.
10. **The Prompt field** is useful if the user is curious about how the image was generated.

---

## About catime

- 🎨 AI-generated cat images every hour using Google Gemini
- 📚 103+ art styles in the style library
- 🐱 Each cat has a unique story and personality
- 🌐 Gallery: [yazelin.github.io/catime](https://yazelin.github.io/catime/)
- 📦 PyPI: `pip install catime`
- ⭐ GitHub: [github.com/yazelin/catime](https://github.com/yazelin/catime)

---

*Note: A helper script for automated cat-sending workflows can be written if needed, but the CLI commands above are sufficient for all agent operations.*
