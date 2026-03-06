# honcho-memory-mux

OpenClaw memory extension + agent skill that:
- stores and retrieves conversational memory via Honcho
- keeps local markdown memory access available as backup via `memory_get`

## Install

```bash
npm install honcho-memory-mux
```

## Configure in OpenClaw

Reference the extension package and provide config:

```json
{
  "memory": {
    "extension": "honcho-memory-mux",
    "config": {
      "apiKey": "YOUR_HONCHO_API_KEY",
      "workspaceId": "openclaw",
      "baseUrl": "https://api.honcho.dev"
    }
  }
}
```

You can also set `HONCHO_API_KEY` as an environment variable.

## Development

```bash
npm install
npm run build
```

Build output is written to `dist/`.
