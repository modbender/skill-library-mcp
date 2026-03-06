# nano-pdf-edit

A Claude Code / Codex CLI skill for editing PDF files with natural language using [Nano-PDF](https://github.com/gavrielc/Nano-PDF), powered by Google's Gemini 3 Pro Image (Nano Banana).

## What This Skill Does

When you ask your AI coding agent to edit a PDF — fix a typo, update a chart, change branding, add a slide — this skill teaches it how to use the `nano-pdf` CLI tool to do it. The agent will:

1. Verify dependencies are installed
2. Construct the right `nano-pdf` command with appropriate flags
3. Run the edit and return the modified PDF

## Installation

### Claude Code (personal — available in all projects)

```bash
git clone https://github.com/ps06756/nano-banana-pdf-skill.git ~/.claude/skills/nano-pdf-edit
```

### Claude Code (project-scoped)

```bash
cd your-project
git clone https://github.com/ps06756/nano-banana-pdf-skill.git .claude/skills/nano-pdf-edit
```

### OpenAI Codex CLI

```bash
git clone https://github.com/ps06756/nano-banana-pdf-skill.git ~/.codex/skills/nano-pdf-edit
```

## Prerequisites

The skill will check these for you, but you'll need:

- **nano-pdf**: `pip install nano-pdf`
- **poppler**: `brew install poppler` (macOS) / `sudo apt-get install poppler-utils` (Linux)
- **tesseract**: `brew install tesseract` (macOS) / `sudo apt-get install tesseract-ocr` (Linux)
- **GEMINI_API_KEY**: A paid Google Gemini API key — `export GEMINI_API_KEY="your_key"`
  - Get one at https://aistudio.google.com/api-keys
  - Free tier does **not** support image generation

## Usage

Once installed, just ask your agent naturally:

> "Fix the typo on page 3 of pitch_deck.pdf — it says 'recieve' instead of 'receive'"

> "Update the chart on slide 8 to show Q3 revenue at $2.5M"

> "Add a new title slide at the beginning of my deck"

> "Change the header color to dark blue across slides 1, 3, and 5"

The skill triggers automatically when the agent detects you want to visually edit a PDF.

## Repo Structure

```
nano-pdf-edit/
├── SKILL.md              # Main skill file (loaded by the agent)
├── scripts/
│   └── check_deps.sh     # Dependency verification script
├── references/
│   ├── options.md         # Full CLI options reference
│   └── examples.md        # Comprehensive usage examples
├── evals/
│   └── evals.json         # Test cases for skill evaluation
├── LICENSE
└── README.md
```

## How Nano-PDF Works Under the Hood

1. **Page Rendering** — Converts target PDF pages to images via Poppler
2. **Style References** — Optionally sends reference pages so the model understands fonts, colors, layout
3. **AI Generation** — Sends images + natural language prompt to Gemini 3 Pro Image
4. **OCR Re-hydration** — Tesseract restores the searchable text layer
5. **PDF Stitching** — Replaces original pages with edited versions

Text remains selectable and searchable in the output PDF.

## Key Commands

```bash
# Edit existing pages
nano-pdf edit file.pdf 3 "Fix the typo" 5 "Update the chart" --resolution "4K"

# Add new slides
nano-pdf add file.pdf 0 "Title slide with 'Q3 Review'"

# With style references and context
nano-pdf edit file.pdf 1 "Update branding" --style-refs "2,3" --use-context
```

## Dependencies

- **Nano-PDF** by [gavrielc](https://github.com/gavrielc/Nano-PDF) — the CLI tool that does the heavy lifting
- **Gemini 3 Pro Image** (Nano Banana) by Google DeepMind — the AI model powering the edits

## License

MIT
