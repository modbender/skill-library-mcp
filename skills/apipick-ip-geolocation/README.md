# apipick-ip-geolocation

A skill that looks up geographic and network information for any IP address using the [apipick](https://www.apipick.com) IP Geolocation API — returning country, city, timezone, currency, ISP, and ASN.

## Compatible Platforms

This skill works with any AI coding agent that supports skill packages or can execute shell commands:

<table>
  <tr>
    <td align="center" width="160">
      <a href="https://docs.anthropic.com/en/docs/claude-code">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Claude_AI_symbol.svg/1280px-Claude_AI_symbol.svg.png" width="48" height="48" alt="Claude Code" /><br />
        <b>Claude Code</b>
      </a>
    </td>
    <td align="center" width="160">
      <a href="https://cursor.com">
        <img src="https://cdn.simpleicons.org/cursor/F54E00" width="48" height="48" alt="Cursor" /><br />
        <b>Cursor</b>
      </a>
    </td>
    <td align="center" width="160">
      <a href="https://openai.com/codex/">
        <img src="https://cdn.simpleicons.org/openai/412991" width="48" height="48" alt="OpenAI Codex" /><br />
        <b>OpenAI Codex</b>
      </a>
    </td>
    <td align="center" width="160">
      <a href="https://manus.im">
        <img src="https://cdn.simpleicons.org/meta/0081FB" width="48" height="48" alt="Manus" /><br />
        <b>Manus</b>
      </a>
    </td>
    <td align="center" width="160">
      <a href="https://antigravity.google">
        <img src="https://brandlogos.net/wp-content/uploads/2025/12/google_antigravity-logo_brandlogos.net_qu4jc-512x472.png" width="48" height="48" alt="Google Antigravity" /><br />
        <b>Google Antigravity</b>
      </a>
    </td>
    <td align="center" width="160">
      <a href="https://openclaw.ai">
        <img src="https://pub-9d9ac8d48a724b8eb296cf20dfd3c940.r2.dev/OpenClaw/ClawBot.png" width="48" height="48" alt="OpenClaw" /><br />
        <b>OpenClaw</b>
      </a>
    </td>
  </tr>
  <tr>
    <td align="center"><sub>Anthropic's agentic<br/>CLI for Claude</sub></td>
    <td align="center"><sub>AI-powered<br/>code editor</sub></td>
    <td align="center"><sub>OpenAI's terminal<br/>coding agent</sub></td>
    <td align="center"><sub>Autonomous AI<br/>agent by Meta</sub></td>
    <td align="center"><sub>Google's agent-first<br/>IDE with Gemini</sub></td>
    <td align="center"><sub>Open-source personal<br/>AI assistant</sub></td>
  </tr>
</table>

## What it does

Given a public IPv4 or IPv6 address (or no address to look up your own IP), this skill returns:

- **Location** — country, continent, city, latitude/longitude
- **Timezone** — IANA timezone identifier
- **Currency** — ISO 4217 currency code for the country
- **Network** — ISP name and ASN number

## Requirements

An apipick API key is required. Get 100 free credits at [apipick.com](https://www.apipick.com).

## Usage

Once installed, just ask your AI agent naturally:

- *"Where is the IP address 8.8.8.8 located?"*
- *"What country does 185.220.101.1 belong to?"*
- *"What's the ISP for IP 1.1.1.1?"*
- *"Look up my current IP location"*

## API Reference

| Field | Value |
|-------|-------|
| Endpoint | `GET https://www.apipick.com/api/ip-geolocation` |
| Auth | `x-api-key` header |
| Cost | 1 credit per request |

See [`references/api_reference.md`](references/api_reference.md) for full documentation.

## Links

- [apipick.com](https://www.apipick.com) — API platform
- [IP Geolocation](https://www.apipick.com/ip-geolocation) — product page
- [Get API Key](https://www.apipick.com/dashboard/api-keys)
