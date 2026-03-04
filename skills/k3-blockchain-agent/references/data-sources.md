# Data Sources — Discovery Guide

This file helps you figure out how to get specific blockchain data into a K3
workflow. Rather than a fixed lookup table, think of this as a problem-solving
guide — there are multiple valid approaches for most data needs, and you should
explore to find what works best.

## Table of Contents

1. [Discovery Process](#discovery-process)
2. [Common Data Needs and Approaches](#common-data-needs-and-approaches)
3. [Finding Endpoints Online](#finding-endpoints-online)
4. [Well-Known Public APIs](#well-known-public-apis)

---

## Discovery Process

Every team's K3 setup is different. Before assuming how to get data:

### 1. Check team MCP integrations

Call `listTeamMcpServerIntegrations()` to see what the team has connected. Common
integrations include TheGraph, CoinGecko, and various protocol-specific MCPs. If
an integration exists for your data need, use it — it's already set up and working.

### 2. Search for existing templates

Call `findAgentByFunctionality()` describing what you need. If someone already
built a workflow for a similar purpose, you can use it directly or learn from its
data source approach.

### 3. Browse available MCP servers

Call `listMcpServerIntegrations()` to see all MCP servers available in the K3
ecosystem. There may be a ready-made integration that the team hasn't connected yet.

### 4. Research online

Search the web for `{protocol name} API` or `{protocol name} subgraph` to find
public endpoints. Most serious DeFi protocols publish APIs and documentation.

### 5. Ask the user

They may know the endpoint, have an API key, or have a specific smart contract
they want to read from.

---

## Common Data Needs and Approaches

These are directional suggestions — not rules. The best approach depends on what
the team has connected and what data format you need.

### Token prices and market data

**Easiest**: Read Market Data (built-in, no configuration needed)
**Also works**: Read API → CoinGecko, CoinMarketCap, or other market data APIs
**Via MCP**: If the team has CoinGecko or Token API MCP connected

### DEX pool metrics (TVL, volume, fees)

**Common approach**: Read Graph → query the protocol's TheGraph subgraph
**Also works**: Read API → protocol's analytics REST endpoint (e.g., Uniswap has
various analytics APIs), Read Smart Contract → read the pool contract directly
**Via MCP**: If the team has TheGraph Subgraph MCP connected

### Wallet balances and holdings

**Easiest**: Read Wallet (built-in, pass wallet address and chain)
**Also works**: Read Smart Contract → call `balanceOf` on individual tokens
**Via MCP**: Various wallet data MCPs may be available

### Smart contract state

**Direct approach**: Read Smart Contract → call any public function on the contract
**Also works**: Read Graph if the data is indexed by a subgraph
**Good for**: Interest rates, reserves, governance parameters, pool configurations

### NFT data (collections, floor prices, traits)

**Easiest**: Read NFT (built-in)
**Also works**: Read API → OpenSea, Reservoir, or other NFT APIs

### Historical on-chain data

**Common approach**: Read Graph → query historical entities (dayData, hourData)
**Also works**: Read API → analytics APIs that serve historical data
**Via AI Agent**: Use Web3 Data Fetcher tool to let AI query historical prices

### Cross-protocol or cross-chain comparisons

**Approach**: Multiple Read nodes → one for each protocol/chain → feed all into
an AI node for comparative analysis
**Also works**: AI Agent with tools enabled → let the AI decide what to fetch

### Data from websites without APIs

**Approach**: AI Web Scraper → point it at the page and describe what to extract

---

## Finding Endpoints Online

When you need a specific protocol's data and don't know the endpoint:

1. **TheGraph Explorer** — search for `{protocol name}` subgraphs. Many protocols
   publish subgraphs even if they're not well-known. Different chains have
   different deployments.

2. **Protocol documentation** — check their docs site for "API", "Developers", or
   "Integration" sections. Most serious protocols publish REST or GraphQL endpoints.

3. **Protocol frontend inspection** — open their analytics/info page, use browser
   DevTools → Network tab, filter by "graphql" or "fetch". The URLs and payloads
   show you exactly what data is available.

4. **DeFiLlama** — `api.llama.fi` provides REST endpoints for TVL, yields, and
   protocol metrics across hundreds of protocols. Good fallback when protocol-specific
   APIs are hard to find.

5. **Block explorers** — Etherscan, Arbiscan, Polygonscan etc. can help you find
   contract addresses and verify which functions are available on a smart contract
   (useful for Read Smart Contract approach).

---

## Well-Known Public APIs

These are commonly used and well-documented. Not exhaustive — search the web for
more options.

| API | What it provides | Endpoint style |
|-----|-----------------|----------------|
| CoinGecko | Token prices, volume, market cap, trending | REST |
| DeFiLlama | TVL, yields, protocol metrics across many protocols | REST |
| TheGraph | DEX data, DeFi metrics via protocol-specific subgraphs | GraphQL |
| Etherscan / chain explorers | Transaction data, contract verification, token transfers | REST |
| OpenSea / Reservoir | NFT sales, floor prices, collection data | REST |
| Alchemy / Infura | Raw blockchain data, token balances, logs | REST / JSON-RPC |

Remember: Read API can call any of these. Read Smart Contract can bypass APIs
entirely and query the blockchain directly. The best approach depends on what data
you need and what format is most useful for the workflow.
