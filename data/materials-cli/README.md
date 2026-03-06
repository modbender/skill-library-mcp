# Materials CLI

A command-line tool for rendering JSON schemas to images (PNG/JPG) using declare-render. Generate schemas with AI or use your own.

## Installation

```bash
cd materials-cli
npm install
```

### Prerequisites

This tool uses `node-canvas` for rendering. If you encounter installation issues, please refer to the [node-canvas installation guide](https://github.com/Automattic/node-canvas#installation).

#### macOS

```bash
brew install pkg-config cairo pango jpeg giflib librsvg pixman
```

#### Ubuntu/Debian

```bash
sudo apt-get install libcairo2-dev libjpeg-dev libpango1.0-dev libgif-dev librsvg2-dev
```

#### Windows

```bash
npm install --global --production windows-build-tools
```

## Usage

### Render a Schema File

```bash
materials render schema.json -o output.png
```

### Generate with AI

```bash
export OPENAI_API_KEY=your-api-key
materials generate "A red circle with text Hello World" -o output.png
```

### Validate a Schema

```bash
materials validate schema.json
```

## Commands

| Command | Description |
|---------|-------------|
| `render <schema>` | Render a JSON schema file to an image |
| `generate <prompt>` | Use AI to generate a schema, then render |
| `validate <schema>` | Validate a schema against the render data schema |

## Options

| Option | Description |
|--------|-------------|
| `-o, --output <path>` | Output file path (default: ./output.png) |
| `-f, --format <format>` | Output format: png or jpg (default: png) |
| `-w, --width <width>` | Canvas width (default: 800) |
| `-h, --height <height>` | Canvas height (default: 600) |
| `--output-schema <path>` | Save the generated schema to a file |
| `--model <model>` | OpenAI model to use (default: gpt-4o) |
| `-i, --interactive` | Interactive mode for input |

## Environment Variables

You can set environment variables in a `.env` file or export them. The CLI supports:

- `OPENAI_API_KEY` - Your OpenAI API key (required for generate command)
- `OPENAI_BASE_URL` - Custom OpenAI API endpoint (optional)
- `OPENAI_MODEL` - Default model to use (optional)

### Using .env File

Copy `.env.example` to `.env` and add your API key:

```bash
cp .env.example .env
# Then edit .env and add your OPENAI_API_KEY
```

### Using Environment Variables

```bash
export OPENAI_API_KEY=sk-your-api-key
```

## Examples

### Render a Simple Schema

```bash
materials render examples/simple.json -o output.png
```

### Generate a Banner

```bash
materials generate "A beautiful banner with gradient background and centered text Welcome" -w 1200 -h 400 -o banner.png
```

### Save Generated Schema

```bash
materials generate "A blue rectangle with rounded corners" --output-schema schema.json -o output.png
```

## Troubleshooting

### node-canvas Installation Failed

If you see errors related to `node-canvas` or native modules, please:

1. Install the required system dependencies (see Prerequisites above)
2. Rebuild node-canvas: `npm rebuild canvas`
3. Or reinstall: `npm install`

For more help, visit: https://github.com/Automattic/node-canvas#installation

### OpenAI API Key Error

Make sure to set the `OPENAI_API_KEY` environment variable:

```bash
export OPENAI_API_KEY=sk-your-api-key
```

## License

ISC
