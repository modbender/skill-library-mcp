# Regex Visualizer

Export Regulex-style railroad diagrams for a regular expression to `SVG` and `PNG`.

This skill renders using the same Regulex web UI export logic (no re-implementation).

## Screenshot

![Example](assets/example.png)

## Usage

```bash
cd ~/.codex/skills/regex-visualizer
npm install
node scripts/render.mjs --re 'hello\\s+world' --flags 'i' --out 'out/hello-world'
```

Outputs:
- `out/hello-world.svg`
- `out/hello-world.png`

## Requirements

- Node.js
- Chrome or Edge installed (the script uses `puppeteer-core` + your local browser)

