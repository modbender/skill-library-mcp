# Vapi OpenClaw Skill

This folder is an OpenClaw skill scaffold for integrating with **Vapi (vapi.ai)**.

- See `SKILL.md` for agent instructions.
- `bin/vapi-api.mjs` is a small helper for calling the Vapi REST API.

## Next steps

1. Provide `VAPI_API_KEY` to your OpenClaw/Gateway environment.
   - For local dev: copy `.env.example` → `.env` and set `VAPI_API_KEY`.
   - `.env` is gitignored.
2. Use the helper to list/create assistants.

## References

- Docs: https://docs.vapi.ai/quickstart/introduction
- API: https://api.vapi.ai/api
- CLI: https://github.com/VapiAI/cli
- Example server: https://github.com/VapiAI/example-server-javascript-node
