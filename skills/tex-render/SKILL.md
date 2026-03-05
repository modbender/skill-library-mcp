---
name: tex-render
description: Renders LaTeX math to PNG, JPEG, WebP, or AVIF images using MathJax (TeX→SVG) and @svg-fns/svg2img. Invoke whenever the agent needs to output LaTeX as a viewable image (equations, formulas, notation).
metadata:
  openclaw:
    emoji: 📐
---

# TeX Render 📐

Renders LaTeX math to PNG, JPEG, WebP, or AVIF (and SVG). Use when you need a **viewable image** from LaTeX instead of raw code.

**User notice:** When this skill is active, the agent will **automatically** render any LaTeX in its replies as images and send them in order—without asking for permission. If you prefer to be prompted or to receive raw LaTeX instead, do not enable this skill (or remove it from your workspace).

## Location

The render script lives in the **same skill folder** as this `SKILL.md`:

```
<skill_folder>/
├── SKILL.md
├── package.json
└── scripts/
    ├─── render.js
    └─── validate.js
```

Use the **directory containing this SKILL.md** as the skill path. The script is at `scripts/render.js` relative to that folder. Invoke: `node <skill_folder>/scripts/render.js`. The agent loading this skill has the skill path—use it to run the script.

## Install

One-time setup. After `clawhub install tex-render`, run `npm install` in the skill folder:

```bash
cd <skill_folder>
npm install
```

- **Source:** All dependencies are from the public npm registry only (no ad-hoc downloads, shorteners, or remote archives).
- **Native module:** The `sharp` package may compile during install; ensure Node.js 14+ and a working build toolchain if needed (see [sharp install](https://sharp.pixelplumbing.com/install) for platform notes).

## When to Use

- User or task asks to "render this equation as image" or "show formula as picture"
- Your reply would contain LaTeX — render formulas as images first, then respond with plain text

## Workflow: Response Contains LaTeX

Output your reply **interleaved**: whenever you would output LaTeX, do this instead:

1. **Send the preceding plain text** — call `message` with the text written so far (no LaTeX).
2. **Render** the LaTeX expression with this skill (default PNG; no `--output dataurl`). Parse the JSON for the PNG path.
3. **Send the image** — call `message` with `action: "send"`, `path` set to the rendered PNG, and `message` as short caption.
4. **Continue** outputting the rest of the message. Repeat the cycle (text → render → send image) for each LaTeX block.

Do **not** output raw LaTeX. Do **not** ask the user for permission to render — render and send images immediately when LaTeX would appear in your reply (users are informed of this automatic behavior in the user notice above). Do **not** accumulate everything and send at the end — send text and images in order as you go.

> **Critical:** Output in order: plain text → send → LaTeX → render → send image → plain text → send → LaTeX → render → send image → … The user must receive text and images in the natural reading order.

**Example**: Explaining Lagrangian:  
→ Send "The Lagrangian is defined as " → Render `L = T - V` → Send image with caption "L = T - V" → Send ". The Euler-Lagrange equation is " → Render `d/dt(∂L/∂q̇) - ∂L/∂q = 0` → Send image → Send " — this yields the equations of motion."

## Usage

Run: `node <skill_folder>/scripts/render.js` (or `node scripts/render.js` when already in the skill folder).

**Escaping:** When invoking via shell:
- **Single quotes** for LaTeX without apostrophe: `node scripts/render.js '\frac{d}{dt}'`
- **Stdin** when LaTeX contains apostrophe (e.g. `y'` for derivative): `printf '%s' "y' = f(t, y), \quad y(t_0)=y_0" | node scripts/render.js` — use double quotes so `'` is literal; backslashes like `\quad` stay intact.

```bash
node <skill_folder>/scripts/render.js --help
```

Default output is PNG to `~/.openclaw/media/tex-render/`. The script prints one JSON line with file paths: `{"svg":"...","png":"..."}` or `{"svg":"...","jpeg":"..."}`, etc. Use `--output dataurl` only when the conversation system explicitly supports Data URL images (otherwise it may show raw base64 text).

### Examples (validated by npm test)

Use `<skill_folder>` = the directory containing this SKILL.md.

**Basic (PNG default):**
```bash
node <skill_folder>/scripts/render.js 'E = mc^2'
node <skill_folder>/scripts/render.js '$$\frac{F}{m}=a$$'
```

**LaTeX with apostrophe (e.g. y'):** use stdin to avoid shell quoting issues:
```bash
printf '%s' "y' = f(t, y), \quad y(t_0)=y_0" | node <skill_folder>/scripts/render.js
```

**JPEG / WebP / AVIF:**
```bash
node <skill_folder>/scripts/render.js --format jpeg --quality 80 '\frac{F}{m}=a' ./out/formula
node <skill_folder>/scripts/render.js --format webp 'x^2 + y^2 = z^2'
node <skill_folder>/scripts/render.js --format avif 'E = mc^2'
```

**Data URL (no file):**
```bash
node <skill_folder>/scripts/render.js --output dataurl 'E = mc^2'
```

**Scale by width:**
```bash
node <skill_folder>/scripts/render.js --width 800 '\int_0^\infty e^{-x^2} dx'
```

**Inline math (smaller rendering):**
```bash
node <skill_folder>/scripts/render.js --inline 'a^2 + b^2 = c^2'
```

**Height and zoom:** Use `--height N` or `--zoom N` as documented in `--help`.

## Automatic Triggering (TOOLS.md)

To make the agent use tex-render **without** the user explicitly asking, add to your workspace `TOOLS.md`:

```markdown
## LaTeX in Responses (tex-render)

**Whenever your reply would contain LaTeX** (equations, formulas, scientific notation), **use the tex-render skill** automatically. Examples: physics, math, chemistry questions with formulas.

**Workflow:** send plain text → render LaTeX → send image via message tool → continue text. Use single quotes when invoking (e.g. `'\frac{a}{b}'`).

### LaTeX / Equations (tex-render)

- When answering scientific or math questions, if your reply would contain LaTeX, use tex-render and send images — do this automatically.
```

**Test:** Ask "Explain the Lagrangian formula" without mentioning tex-render. The agent should render and send images.

## Repository

This package is maintained at [https://github.com/TheBigoranger/tex-render](https://github.com/TheBigoranger/tex-render). You can open issues there for bug reports and feature requests.

