---
name: k3-blockchain-agent
description: >
  Build automated blockchain analysis workflows on K3 — from natural language
  requests to deployed, running automations that fetch on-chain data, analyze it
  with AI, and deliver insights via email, Telegram, or Slack. Use this skill
  whenever the user mentions blockchain workflows, on-chain analytics, DeFi
  monitoring, token tracking, wallet alerts, pool analysis, protocol dashboards,
  NFT tracking, automated trading, smart contract monitoring, or wants to automate
  anything involving blockchain data. Also trigger when the user mentions K3,
  workflow builder, or wants scheduled crypto/DeFi reports. Even if they just say
  "monitor this wallet" or "track this token" — this skill applies.
---

# K3 Blockchain Agent

Transform requests like *"Send me daily updates about the WETH/USDC pool on Uniswap"*
into fully deployed workflows that fetch data, run AI analysis, and deliver reports
automatically.

## Setup

This skill requires the **K3 Development MCP** to be connected. The MCP provides
tools like `generateWorkflow`, `executeWorkflow`, `findAgentByFunctionality`, and
others that let you create and manage blockchain workflows programmatically.

If the K3 MCP isn't connected yet, tell the user they need to add it before
proceeding. Once connected, verify by calling `listTeamMcpServerIntegrations()` —
this confirms the connection and shows what data source integrations (TheGraph,
CoinGecko, etc.) the user's team has wired up. Every team's integrations will be
different — discover what's available rather than assuming.

## How Workflow Building Works

The K3 orchestrator is **conversational**. You describe what you want in plain
language, and the orchestrator asks clarifying questions, then builds and deploys
the workflow. Your job is to show up with the right information so the conversation
is productive.

The loop:

```
UNDERSTAND → what does the user actually want?
FIND DATA  → how do we get that information into the workflow?
TEST       → does the data actually come back correctly?
BUILD      → give the orchestrator everything it needs
DEPLOY     → launch it and verify it works
```

Skipping "test" is the most common mistake — you end up with a deployed workflow
that returns empty data.

## Step 1: Understand the Request

When a user asks for a workflow, figure out these parameters. Ask if anything is
unclear — don't guess on addresses or emails.

| Parameter | What to find out | Examples |
|-----------|-----------------|----------|
| **Data target** | What blockchain data do they need? | pool metrics, token price, wallet balance, NFT data |
| **Protocol** | Which DeFi protocol or chain feature? | Uniswap, Aave, SushiSwap, native transfers |
| **Chain** | Which blockchain? | Ethereum, Arbitrum, Polygon, Base, Stellar |
| **Schedule** | How often / what triggers it? | daily, hourly, on-demand, on wallet activity, on contract event, Telegram chatbot |
| **Analysis** | What kind of insights? | performance summary, anomaly alerts, trend report, trade signal |
| **Delivery** | How should results arrive? | email, Telegram, Slack, Google Sheets |
| **Actions** | Should the workflow do anything? | execute a swap, transfer tokens, write to a contract |
| **Specifics** | Any addresses or IDs? | pool address, token contract, wallet address |

If the user is new to DeFi, briefly explain relevant concepts as you go (what TVL
means, what a liquidity pool is, etc.). Don't assume they know the jargon.

## Step 2: Find the Right Data

This is the critical step. K3 has many ways to get data into a workflow, and you
need to figure out which approach works for the user's specific request.

### K3 data functions

These are the built-in functions for getting data into a workflow. Read
`references/node-types.md` for full details on each.

| Function | What it does |
|----------|-------------|
| **Read API** | Call any REST/GraphQL API — the most flexible option |
| **Read Smart Contract** | Query any smart contract directly on-chain |
| **Read Market Data** | Get token prices, volumes, market metrics |
| **Read Wallet** | Wallet balances, transfers, transaction history |
| **Read NFT** | NFT collections, floor prices, traits, holders |
| **Read Graph** | Query TheGraph subgraphs with custom GraphQL |
| **Read Deployment** | Pull output from your own deployed code on K3 |
| **AI Web Scraper** | Extract structured data from any web page |
| **AI Agent with tools** | AI that dynamically decides what to fetch |

### How to find the data you need

The goal is to figure out the best way to get the specific data the user wants.
Think of it as problem-solving — there are multiple valid approaches and you
should explore them:

1. **Check what the team already has** — call `listTeamMcpServerIntegrations()` to
   see what MCP data sources are connected. If they have TheGraph, CoinGecko, or
   other integrations set up, those are the easiest path.

2. **Search for existing templates** — call `findAgentByFunctionality()` with the
   user's intent. If someone already built a similar workflow, use it as a starting
   point.

3. **Think about which K3 function fits**:
   - Need on-chain contract data? → **Read Smart Contract** can query it directly
   - Need token prices or market data? → **Read Market Data** has it built in
   - Need complex DeFi metrics (TVL, volume, fees)? → **Read Graph** with the right
     subgraph, or **Read API** to a protocol's analytics endpoint
   - Need wallet info? → **Read Wallet** for balances and history
   - Need NFT data? → **Read NFT** for collections and metadata
   - Need data from any public API? → **Read API** can call anything
   - Need to scrape a website? → **AI Web Scraper** can extract and structure it

4. **Search the web** for the right endpoint. If you need a specific protocol's data,
   look up `{protocol name} API`, `{protocol name} subgraph`, or `{protocol name}
   GraphQL endpoint`. Many protocols publish public APIs and subgraphs.

5. **Ask the user** — they may know the API endpoint, have an API key, or know
   exactly which smart contract to read from.

The key insight: there's rarely just one way to get the data. A Uniswap pool's TVL
could come from Read Graph (subgraph query), Read API (calling an analytics endpoint),
or even Read Smart Contract (reading the pool contract directly). Pick whichever is
most reliable and gives you the data format you need.

### Test before you build

Before constructing the full workflow, verify the data source actually returns
what you expect:

```
1. Create a minimal test workflow with generateWorkflow()
   — just a trigger + one data fetch step, nothing else
2. Deploy and run it with executeWorkflow()
3. Check the output with getWorkflowRunById() (set includeWorkflowData: true)
4. If the data looks right → proceed to full build
5. If empty or wrong → try a different approach and test again
```

This saves a lot of debugging later. A deployed workflow with bad data is worse
than no workflow.

## Step 3: Build the Workflow

Now give the K3 orchestrator everything it needs. Use `generateWorkflow()` with
a detailed prompt that includes:

- **Trigger type and schedule** (e.g., "runs daily" or "triggers on wallet activity")
- **Data source and how to query it** (e.g., "use Read Graph to query pool X" or
  "use Read Smart Contract to get the pair's reserves")
- **What the AI should analyze** (e.g., "highlight TVL changes over 5%")
- **Any actions to take** (e.g., "execute a swap on Uniswap if condition is met")
- **How to deliver results** (e.g., "send Telegram alert" or "email the report")
- **Any MCP integration IDs** the orchestrator needs (from team integrations)

Set `deployWorkflow: false` on the first call so you can review before deploying.

The orchestrator will likely ask follow-up questions — answer them using
`editGeneratedWorkflow()` with the same `generatedWorkflowId`. This back-and-forth
is normal; expect 2-4 rounds.

Once the configuration looks correct, call `editGeneratedWorkflow()` one final time
with `deployWorkflow: true`.

For the full list of available functions, triggers, AI models, and output options,
read `references/node-types.md`.

## Step 4: Deploy and Verify

After deploying:

1. **Run it manually** with `executeWorkflow()` to trigger an immediate test
2. **Check the run** with `getWorkflowRuns()` or `getWorkflowRunById()`
3. **Verify the full chain**: Did data fetch? Did AI analyze? Did notification send?

If something failed, use `editGeneratedWorkflow()` to fix it — you don't need to
start over. See `references/troubleshooting.md` for common issues.

Tell the user what happened: "Your workflow is live and will run daily. I just ran
a test — here's what the first report looks like: [summary]."

## K3 MCP Tool Reference

| Tool | What it does |
|------|-------------|
| `generateWorkflow` | Start building a workflow from natural language |
| `editGeneratedWorkflow` | Continue the conversation with the orchestrator |
| `executeWorkflow` | Run a workflow manually |
| `getWorkflowById` | Get workflow details and config |
| `getWorkflowRuns` | List execution history |
| `getWorkflowRunById` | Get a specific run's details and output |
| `updateWorkflow` | Pause/unpause a scheduled workflow |
| `findAgentByFunctionality` | Search for existing workflow templates |
| `listAgentTemplates` | Browse all available templates |
| `getAgentTemplateById` | Get details on a specific template |
| `listTeamMcpServerIntegrations` | See what data sources the team has connected |
| `listMcpServerIntegrations` | Browse all available MCP data sources |

## Important Rules

1. **Always test data sources** before building the full workflow. A quick test
   fetch saves a lot of debugging time.
2. **The orchestrator is conversational** — expect multiple rounds of back-and-forth
   via `editGeneratedWorkflow`. That's how it's designed to work.
3. **Ask the user for anything you can't look up** — never guess email addresses,
   Telegram handles, or wallet addresses.
4. **Discover team integrations** — call `listTeamMcpServerIntegrations()` to see
   what's available. Every team is different.
5. **Verify workflows work** before telling the user it's done. Run it, check the
   output, confirm delivery.
6. **Be mindful of context** — don't call many K3 MCP tools at once or dump large
   responses. Fetch what you need, check it, move on.
7. **Use web search** to find API endpoints, subgraph URLs, and smart contract
   addresses when you don't know them. The web is your research tool.

## Going Deeper

- `references/node-types.md` — All trigger types, data functions, AI functions,
  DeFi/trading actions, and notification options
- `references/data-sources.md` — How to discover and evaluate data sources for
  different blockchain data needs
- `references/workflow-patterns.md` — Common workflow architectures and when to
  use each one
- `references/troubleshooting.md` — Diagnosing and fixing common workflow issues
