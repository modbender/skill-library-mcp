# Security

## Safety Posture

- This skill configures account and OpenClaw settings; it does not perform destructive system actions.
- OpenClaw config updates create a backup file before writing.

## Secrets Handling

- Keep tenant keys in environment variables (`CACHEFORGE_API_KEY`) rather than plaintext config files.
- Do not commit keys or credentials.
