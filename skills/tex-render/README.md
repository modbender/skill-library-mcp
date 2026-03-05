# TeX Render

Renders LaTeX math to PNG, JPEG, WebP, or AVIF images so formulas can be shown as pictures in chat, docs, or slides. Uses [**MathJax**](https://github.com/mathjax/MathJax) (TeX → SVG) and [**@svg-fns/svg2img**](https://github.com/svg-fns/svg-fns) (SVG → raster) with Sharp.

## What It Does

- **Input**: A LaTeX math expression (e.g. `\frac{F}{m}=a`, or `$$E=mc^2$$`).
- **Output**: An image file (PNG/JPEG/WebP/AVIF) and SVG at known paths, or a Data URL with `--output dataurl`.
- **Use case**: When an agent or tool needs to show an equation to the user, it can render the formula to an image and send it instead of raw LaTeX.

## How It Works

1. **Normalize** the LaTeX string: strip markdown delimiters (`$$...$$`, `$...$`, `\[...\]`, `\(...\)`).
2. **MathJax**: Renders the TeX to **SVG** in Node.js.
3. **@svg-fns/svg2img** (Sharp): Converts SVG to PNG/JPEG/WebP/AVIF.
4. **Paths**: By default, files are written under `~/.openclaw/media/tex-render/`.

```
LaTeX string  →  normalize  →  MathJax  →  SVG  →  @svg-fns/svg2img (Sharp)  →  PNG/JPEG/WebP/AVIF
```

## Install

```bash
npm install
```

- **Dependencies**: `mathjax` (TeX → SVG), `@svg-fns/svg2img`, `sharp` (Node rasterization).
- **Requirements**: Node.js 14+.

## Package Layout

```
tex-render/
├── README.md           # This file
├── SKILL.md            # OpenClaw skill instructions
├── package.json        # Dependencies: mathjax, @svg-fns/svg2img, sharp
└── scripts/
    ├── render.js       # CLI: LaTeX → PNG/JPEG/WebP/AVIF
    └── validate.js     # Validation tests (npm test)
```

## Usage

Run `node scripts/render.js --help` for full options. Summary:

- **Arguments**: LaTeX (required, or from stdin), optional output path  
- **Escaping**: Single quotes for argv; when LaTeX contains apostrophe (e.g. `y'`), use stdin: `printf '%s' "y' = f(t,y)" | node scripts/render.js`
- **Options**: `--format png|jpeg|webp|avif`, `--output file|dataurl`, `--inline`, `--width N`, `--height N`, `--zoom N`, `--quality N`
- **Output**: Writes `.svg` and `.png` (or `.jpeg`, `.webp`, `.avif`), or prints Data URL

Examples:

```bash
node scripts/render.js 'E = mc^2'
node scripts/render.js --format jpeg --quality 80 '\frac{F}{m}=a' ./out/formula
node scripts/render.js --format webp 'x^2 + y^2 = z^2'
node scripts/render.js --format avif 'E = mc^2'
node scripts/render.js --output dataurl 'E = mc^2'
node scripts/render.js --width 800 '\int_0^\infty e^{-x^2} dx'
node scripts/render.js --inline 'x^2 + y^2 = z^2'
```

## How the Skill Uses This

When the OpenClaw agent is about to reply with LaTeX:

1. Extract each LaTeX expression from the draft.
2. Run `render.js` for each to get an image path (or Data URL).
3. Send the image(s) to the user via the message tool.
4. Reply in plain text only.

## Automatic Triggering via TOOLS.md

To make the agent use tex-render **automatically** whenever its reply would contain LaTeX (without the user explicitly saying "use tex-render"), add this to your workspace `TOOLS.md`:

```markdown
## LaTeX in Responses (tex-render)

**Whenever your reply would contain LaTeX** (equations, formulas, scientific notation), **use the tex-render skill** automatically. Do not wait for the user to ask for it. Examples: physics (Lagrangian, Navier-Stokes), math (quadratic formula, integrals), chemistry (reaction equations).

**Workflow:** send plain text → render LaTeX with tex-render → send image via message tool → continue text. Use single quotes around LaTeX when invoking the render script (e.g. `node scripts/render.js '\frac{a}{b}'`).
```

And in the Examples section:

```markdown
### LaTeX / Equations (tex-render)

- When answering scientific or math questions, if your reply would contain LaTeX, use the tex-render skill and send images via the message tool — do not output raw LaTeX. Do this automatically.
```

**Test:** Ask "Explain the Lagrangian formula" (without mentioning tex-render). The agent should render equations as images and send them via the message tool.

## License / Credits

- [**MathJax**](https://github.com/mathjax/MathJax): TeX → SVG.
- [**@svg-fns/svg2img**](https://github.com/svg-fns/svg-fns): SVG → raster (Sharp).
