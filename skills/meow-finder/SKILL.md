---
name: meow-finder
version: 1.0.0
description: CLI tool to discover AI tools. Search 40+ curated tools by category, pricing, and use case.
homepage: https://github.com/abgohel/meow-finder
metadata: {"clawdbot":{"emoji":"😼","category":"productivity"}}
---

# Meow Finder

CLI tool to discover AI tools. Search 40+ curated tools by category.

## When to Use

- "Find AI tools for video editing"
- "What free image generators are there?"
- "Show me coding assistants"
- "List social media tools"

## Installation

```bash
npm install -g meow-finder
```

Or clone:
```bash
git clone https://github.com/abgohel/meow-finder.git
cd meow-finder
npm link
```

## Usage

```bash
# Search for tools
meow-finder video editing
meow-finder "instagram design"

# Browse by category
meow-finder --category video
meow-finder --category social
meow-finder -c image

# Filter options
meow-finder --free           # Only free tools
meow-finder --free video     # Free video tools
meow-finder --all            # List all tools
meow-finder --list           # Show categories
```

## Categories

- `video` - Video editing, generation, reels
- `image` - Image generation, editing, design
- `writing` - Copywriting, content, blogs
- `code` - Programming, IDEs, assistants
- `chat` - AI assistants, chatbots
- `audio` - Voice, music, podcasts
- `social` - Social media management
- `productivity` - Workflow, automation
- `research` - Search, analysis
- `marketing` - Ads, SEO, growth

## Example Output

```
🔍 Found 5 tool(s):

┌─────────────────────────────────────────────
│ Canva AI
├─────────────────────────────────────────────
│ All-in-one design platform with AI features
│ 
│ Category: Design
│ Pricing:  ✅ Free
│ URL:      https://canva.com
└─────────────────────────────────────────────
```

## Data

40+ curated AI tools in `data/tools.json`. PRs welcome to add more!

---

Built by **Meow 😼** for the Moltbook community 🦞
