# envoic Troubleshooting

## uvx Not Found

- Install uv, then retry: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Fallback install: `pip install envoic`

## npx Slow or Hanging

- First invocation may download package metadata; wait once and retry.
- Fallback global install: `npm install -g envoic`

## Permission Errors

- Skip inaccessible paths and report what could not be scanned or deleted.

## Large Workspace Scan Time

- Start with a narrower root path.
- Run without `--deep` first, then repeat with `--deep` on target folders.

## Broken Virtual Environment

- If `bin/python` or `Scripts/python.exe` is missing/dangling, delete and recreate the environment.
