# agentspend

AgentSpend CLI for calling x402 endpoints through AgentSpend Cloud.

## Install

```bash
npm install
npm run build
```

## Commands

```bash
agentspend configure
agentspend pay <url> [--method GET|POST|PUT|PATCH|DELETE|...] [--body '{"hello":"world"}'] [--header 'Content-Type:application/json'] [--max-cost 5.000000]
agentspend check <url> [--method GET|POST|PUT|PATCH|DELETE|...] [--body '{"hello":"world"}'] [--header 'Content-Type:application/json']
agentspend status
```

## Credentials

Credentials are stored at `~/.agentspend/credentials.json`.

## Local backend dev CLI

Use the local entrypoint (hardcoded to `http://127.0.0.1:8787`) when testing against a local backend:

```bash
bun run dev:local -- configure
```

Build a non-published local binary:

```bash
bun run build
node dist/dev-index.js configure
```
