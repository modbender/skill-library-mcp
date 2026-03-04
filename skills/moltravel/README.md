# MolTravel — Travel Agent Plugin for Claude Code

A personal travel agent skill that gives Claude access to flights, visa requirements, destination info, travel advisories, and activities through the [MolTravel MCP server](https://molttravel.com).

## What It Does

Claude automatically uses this skill when you ask about travel. It combines 21+ tools into a seamless travel planning experience:

- **Flight search** — Find and compare flights across airlines and routes
- **Price comparison** — Cross-check prices across multiple booking sites via Navifare
- **Visa requirements** — Check visa rules for any passport/destination combination
- **Country info** — Currency, language, timezone, population, and more
- **Travel advisories** — UK FCDO safety and entry requirement updates
- **Activities** — Search 300K+ experiences and tours via Peek.com
- **Airport & airline lookup** — IATA/ICAO code resolution and search

## Usage

Just ask naturally:

```
"Plan a trip to Japan next week"
"Do I need a visa for Brazil?"
"Find flights from London to Tokyo next Tuesday, back Friday"
"What's there to do in Barcelona?"
"Is it safe to travel to Thailand right now?"
```

## Install

### From a marketplace

```
/plugin install molttravel@<marketplace-name>
```

### Manually

```
/plugin install ./molttravel-plugin
```

## MCP Server

This plugin bundles the MolTravel MCP server configuration. Once installed, the `molttravel` MCP endpoint at `https://mcp.molttravel.com/mcp` is automatically available — no manual setup needed.

## Author

[Navifare](https://navifare.com) — hello@navifare.com
