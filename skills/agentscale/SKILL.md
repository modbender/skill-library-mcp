---
name: agentscale
description: Deploy web apps and APIs to a public URL with a single command.
required_tools: ["tar"]
---

## Free Tier

- No signup or payment required to start.
- Run `npx agentscale register` to get an API key.
- Free deploys expire after 1 hour.
- Limited to 1 service.

## Paid Tier

- Add credits to remove the 1-hour expiry and deploy permanently.
- Use `npx agentscale account` to check your tier and credit balance.
- When you need to add credits, use the `agentspend pay` command or the AgentSpend skill.

## Commands

### Register

```bash
npx agentscale register
```

Generates an API key and saves it to `~/.agentscale/config.json`.

### Deploy

```bash
npx agentscale deploy
```

Run this from your project directory. Packages the current directory and deploys it.

**Options:**
- `--name <name>` — Service name (auto-generated if omitted)

### List

```bash
npx agentscale list
```

Lists your services and their status.

### Account

```bash
npx agentscale account
```

Shows your account tier (free/paid) and credit balance.

To add credits, use the `agentspend pay` command:

```bash
agentspend pay https://api.agentscale.co/add-credits \
  --header "x-api-key:<your-api-key>" \
  --body '{"amount_cents": 500}'
```

Or pay directly with an x402 wallet by calling `POST /add-credits` with your `x-api-key` header and `amount_cents` in the body.

## Project Requirements

- Deploy APIs and web services. Supports Node.js, Python, Go, and more.
- Your project needs a standard structure to be auto-detected:
  - **Node.js:** a `package.json` with a start script.
  - **Python:** a `requirements.txt`.
  - **Go:** a `go.mod`.
- Custom domains, build commands, and start commands are not yet supported.

## Environment Variables

- `AGENTSCALE_API_URL` — Overrides the default API base URL. **Warning:** this redirects all API calls, including those carrying your API key, to the specified URL.

## System Requirements

- `tar` must be available on PATH (used to package projects for deploy).

## Limits

- Upload: 100 MB compressed, 500 MB decompressed.
