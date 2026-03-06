---
name: materials-cli
description: Render JSON schemas to images and generate schemas from prompts using declare-render and AI.
version: 1.0.7
metadata:
  clawdbot:
    requires:
      env:
        - OPENAI_API_KEY
      bins:
        - node
    primaryEnv: OPENAI_API_KEY
---
# Materials CLI

Use this skill when the user wants to render JSON schemas to images (PNG/JPG), validate render-data schemas, or generate schemas from natural-language prompts and then render them.

## Commands

- **render** — Render a JSON schema file to an image.
- **generate** — Use AI (OpenAI) to generate a schema from a prompt, then render it.
- **validate** — Validate a JSON schema against the declare-render data schema.

## When to use

- User asks to "render a schema to image", "turn JSON into a picture", or "draw from schema".
- User wants to "generate an image from a description" or "create a schema from a prompt" and render it.
- User wants to "validate" a JSON file against the render data schema.

## Usage

Run via Node (from the project or after `npm install -g materials-cli`):

```bash
materials render <schema-path> [options]
materials generate "<prompt>" [options]
materials validate <schema-path> [options]
```

### Render

- `materials render schema.json -o output.png`
- Options: `-s, --schema <path>`, `-o, --output <path>` (default `./output.png`), `-f, --format <png|jpg>`, `-w, --width`, `-h, --height`, `--output-schema <path>`, `-i, --interactive`

### Generate (AI)

- `materials generate "A red circle with text Hello" -o out.png`
- Options: `-o, --output`, `-f, --format`, `-w, --width`, `-h, --height`, `--output-schema`, `--model`, `--api-key`, `--base-url`, `-i, --interactive`
- Uses `OPENAI_API_KEY` (and optionally `OPENAI_MODEL`, `OPENAI_BASE_URL`) if not passed via flags.

### Validate

- `materials validate schema.json`
- Options: `-s, --schema <path>`, `-i, --interactive`

## CLI help

```
Usage: materials <command> [options]

Commands:
  render <schema>     Render a JSON schema file to an image
  generate <prompt>   Use AI to generate a schema, then render
  validate <schema>   Validate a schema against the render data schema

Examples:
  materials render schema.json -o output.png
  materials generate "A red circle with text Hello"
  materials validate schema.json
```

## Schema format

The JSON schema follows the declare-render format: root has `id`, `width`, `height`, and `layers`. Layer types include text, image, container, shape, etc. Use `materials validate <file>` to check a schema before rendering.
