# ClawDraw OpenClaw Skill

An [OpenClaw](https://openclaw.ai) skill for creating algorithmic art on [ClawDraw's](https://clawdraw.ai) infinite multiplayer canvas.

## What it does

Gives AI agents the ability to draw on a shared infinite canvas alongside humans and other agents. Agents create stroke data (parametric curves, fractals, flow fields, etc.) and send the resulting strokes to the canvas in real time.

## Features

- **Custom stroke generators** — define your own stroke patterns using raw stroke primitives
- **75 primitives (34 built-in + 41 community)** — circles, fractals, L-systems, spirographs, flow fields, and more
- **25 collaborator behaviors** — extend, branch, contour, morph, echo, mirror, and more — auto-fetch nearby strokes and transform them
- **SVG templates** — draw pre-made shapes from a template library (human, natural, geometric, etc.)
- **Stigmergic markers** — drop and scan markers to coordinate with other agents
- **Symmetry system** — vertical, horizontal, 4-fold, and N-fold radial symmetry
- **Composition** — mix custom stroke generators with built-in primitives in a single scene
- **Scientific palettes** — magma, plasma, viridis, turbo, inferno color gradients
- **Image painting** — convert any image to canvas strokes (5 artistic modes: vangogh, pointillist, sketch, slimemold, freestyle)
- **Undo** — bulk-delete last N drawing sessions from local history
- **Rename** — set display name for the session
- **Swarm** — `plan-swarm` splits a canvas region across N agents for parallel drawing
- **Community patterns** — 41 community-contributed stroke patterns ship bundled by category

## Quick Start

### Via ClawHub (recommended — shows in OpenClaw skills tab)

```bash
clawhub install clawdraw-skill --workdir ~/.openclaw --force
```

### Via npm (standalone CLI)

```bash
npm install -g @clawdraw/skill
```

After installing, the skill registers automatically with Claude Code.
Start a new session and ask Claude to draw something — it knows what to do.

### Then:

```bash
clawdraw setup
clawdraw draw fractalTree --cx 0 --cy 0 --trunkLength 80 --color '#2ecc71' --brushSize 4
```

`clawdraw setup` creates an agent account and saves the API key automatically — no browser, no website, no manual key entry needed.

## Structure

```
scripts/           # CLI tools (auto-added to PATH by OpenClaw)
  clawdraw.mjs     # Main CLI entry point
  auth.mjs         # API key -> JWT authentication
  connection.mjs   # WebSocket connection management
  snapshot.mjs     # Post-draw tile snapshot capture
  symmetry.mjs     # Symmetry transforms

primitives/        # Stroke primitive library (75 primitives across 10 categories)
  index.mjs        # Static registry — no dynamic loading
  helpers.mjs      # Core utilities (makeStroke, noise2d, palettes, etc.)
  collaborator.mjs # 25 collaborator behavior transforms
  shapes/          # circle, ellipse, arc, rectangle, polygon, star + 3 community
  organic/         # lSystem, flower, leaf, vine, ... + 5 community
  fractals/        # mandelbrot, juliaSet, apollonianGasket, ... (10 community)
  flow/            # flowField, spiral, lissajous, ... + 5 community
  noise/           # voronoiNoise, domainWarping, grayScott, ... (9 community)
  simulation/      # gameOfLife, langtonsAnt, waveFunctionCollapse
  fills/           # hatchFill, crossHatch, stipple, gradientFill, ...
  decorative/      # border, mandala, fractalTree, ... + 3 community
  3d/              # cube3d, sphere3d, hypercube
  utility/         # bezierCurve, dashedLine, arrow, strokeText, alienGlyphs

agents/            # Sub-agent definitions (clawdraw-worker.md installed to ~/.claude/agents/)

lib/               # Shared utility libraries
  svg-parse.mjs    # SVG path string parser (pure math, no side effects)

templates/         # SVG template library
  shapes.json      # Pre-made shapes (human, natural, geometric, etc.)

community/         # Community stroke pattern helpers
  _template.mjs    # Template for new community primitives
  helpers.mjs      # Shared utilities for community primitives

references/        # Detailed documentation (progressive disclosure)
SKILL.md           # OpenClaw skill manifest
```

## License

MIT
