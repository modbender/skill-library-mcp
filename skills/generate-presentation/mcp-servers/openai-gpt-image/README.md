# OpenAI GPT Image MCP Server

An MCP (Model Context Protocol) server that provides AI image generation and editing capabilities using OpenAI's GPT Image models.

## Features

- **Image Generation** (`create-image`) — Generate images from text prompts using `gpt-image-1.5`, `gpt-image-1`, or `gpt-image-1-mini`
- **Image Editing** (`edit-image`) — Edit existing images with text instructions and optional masks
- **Multiple Output Formats** — PNG, JPEG, WebP with configurable quality and compression
- **Flexible Output** — Return as base64 or save directly to file (auto-switches for large images)
- **Azure OpenAI Support** — Compatible with Azure OpenAI endpoints
- **Environment File Support** — Load API keys from `.env` files via `--env-file` flag

## Setup

### 1. Install dependencies

```bash
cd mcp-servers/openai-gpt-image
npm install
```

### 2. Build

```bash
npm run build
```

### 3. Configure your API key

Create a `.env` file in your project root:

```
OPENAI_API_KEY=sk-your-api-key-here
```

### 4. Add to Claude Code MCP config

Add to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "openai-gpt-image-mcp": {
      "command": "node",
      "args": [
        "<absolute-path-to>/mcp-servers/openai-gpt-image/dist/index.js",
        "--env-file",
        "<absolute-path-to>/.env"
      ]
    }
  }
}
```

Replace `<absolute-path-to>` with the actual absolute path on your system.

## Tools

### `create-image`

Generate images from text prompts.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | required | Text description of the image (max 32000 chars) |
| `model` | string | `gpt-image-1.5` | Model: `gpt-image-1.5`, `gpt-image-1`, `gpt-image-1-mini` |
| `size` | string | `auto` | `1024x1024`, `1536x1024`, `1024x1536`, `auto` |
| `quality` | string | `auto` | `high`, `medium`, `low`, `auto` |
| `output` | string | `base64` | `base64` or `file_output` |
| `file_output` | string | — | Absolute path to save the image |
| `background` | string | — | `transparent`, `opaque`, `auto` |
| `output_format` | string | — | `png`, `jpeg`, `webp` |
| `n` | number | 1 | Number of images (1-10) |

### `edit-image`

Edit an existing image with text instructions.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image` | string | required | Absolute path or base64 string of the source image |
| `prompt` | string | required | Text description of the desired edit |
| `mask` | string | — | Optional mask image (transparent areas = edit zones) |
| `model` | string | `gpt-image-1.5` | Model to use |
| `size` | string | — | Output size |
| `quality` | string | — | Output quality |
| `output` | string | `base64` | `base64` or `file_output` |
| `file_output` | string | — | Absolute path to save the result |

## License

MIT
