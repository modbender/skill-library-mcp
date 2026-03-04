# config-validator

A utility skill to validate OpenClaw configuration files (`openclaw.json`, `.env`, `package.json`) and ensure critical settings are present and correctly formatted.

## Usage

```bash
node skills/config-validator/index.js [--fix]
```

## Features

- Checks for required environment variables (`.env`).
- Validates `openclaw.json` structure.
- Checks `package.json` dependencies against installed modules.
- Reports missing or malformed configurations.
- Optional `--fix` flag attempts basic repairs (e.g., creating missing files from templates).

## Dependencies

- None (built-in Node.js modules).
