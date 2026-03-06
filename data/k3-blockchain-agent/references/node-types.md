# K3 Node Types Reference

Every K3 workflow is a chain of nodes. This file describes all available node types
so you know what's possible when designing a workflow.

## Table of Contents

1. [Triggers](#triggers)
2. [Read Functions (Data Input)](#read-functions-data-input)
3. [AI Functions](#ai-functions)
4. [Write Functions (Output & Actions)](#write-functions-output--actions)
5. [DeFi & Trading Functions](#defi--trading-functions)
6. [Notification Functions](#notification-functions)
7. [Utility Functions](#utility-functions)

---

## Triggers

Every workflow has exactly one trigger that determines when it starts.

### Scheduled / Manual

Runs on a repeating time interval, or manually on demand.

When to use: Daily digests, hourly monitors, periodic reports, or workflows you
want to trigger manually or via API.

Config: Choose frequency (hourly, daily, etc.) or set a custom interval.

### Smart Contract Event

Triggers when a specific smart contract emits an event on-chain.

When to use: Reacting to swaps, transfers, mints, burns, liquidations, governance
votes, or any on-chain event.

Examples:
- Token contracts: trigger on transfers, approvals, burns
- DEX contracts: trigger on swaps, liquidity additions, pair creation
- NFT contracts: trigger on mints, transfers, sales

Config: Contract address, event name, chain ID.

What you can do with it:
- Send real-time alerts with transaction details (amounts, addresses, event types)
- Initiate follow-up actions (token transfers, trades, contract writes)
- Save event data to a database for analytics and reporting

### Wallet Event (Address Activity)

Triggers when a specific wallet address has on-chain activity.

When to use: Whale watching, portfolio alerts, wallet monitoring, detecting
incoming payments or airdrops.

Config: Wallet address, chain ID.

### Telegram Chatbot

Triggers when a user sends a message to a connected Telegram bot. The user creates
a Telegram bot, connects it to K3, and the workflow runs every time someone sends
the bot a message. The message content is passed into the workflow as input.

When to use: Building conversational AI agents on Telegram — users can chat with
a bot that has access to blockchain data, AI analysis, and any K3 workflow
functions. Think of it as giving users a personal on-chain assistant in their
Telegram chat.

Examples:
- User sends a wallet address → workflow reads the wallet, AI analyzes it, replies
  with a portfolio overview
- User asks "what's the price of ETH?" → AI Agent with CoinGecko MCP fetches the
  data and replies in the chat
- User sends a token name → workflow pulls market data, runs AI analysis, sends
  back a summary

Config: Telegram bot token, connected to K3 platform.

---

## Read Functions (Data Input)

These fetch data that downstream nodes can use.

### Custom Input

Accepts user-provided parameters at runtime. Useful for on-demand workflows where
the user specifies what to analyze each time (e.g., "which token?" or "which
wallet?").

Config: Define input fields with key, name, and default value.

### Read API

Makes an HTTP request to any REST or GraphQL API. This is the most flexible data
input — if a service has a public API, Read API can call it.

When to use: Calling CoinGecko, DeFiLlama, protocol-specific REST APIs, GraphQL
endpoints, or any other web API.

Config: URL, method (GET/POST), headers, body.

### Read Smart Contract

Queries smart contract data directly on any supported blockchain. Reads contract
state without needing an API intermediary.

When to use: Getting on-chain data directly — pool reserves, token balances,
contract parameters, governance state, or any public function on a smart contract.

Examples:
- Read a Uniswap pair contract to get current reserves
- Read an ERC20 token's totalSupply or balanceOf
- Read a lending protocol's interest rates directly from the contract

Config: Contract address, function to call, chain ID, function parameters.

### Read Market Data

Retrieves up-to-date token prices, volumes, and other market metrics. A built-in
convenience function for common market data needs.

When to use: Quick token price lookups, volume data, market cap, or other
standard market metrics without needing to configure a specific API.

### Read Wallet

Accesses wallet data including balances, token holdings, transfers, and transaction
history.

When to use: Portfolio tracking, wallet balance monitoring, transaction history
analysis.

Config: Wallet address(es), chain ID.

### Read NFT

Gets detailed NFT data: collections, floor prices, traits, volumes, account
holders, and more.

When to use: NFT portfolio tracking, collection monitoring, floor price alerts,
trait analysis, holder analytics.

### Read Graph

Fetches data from TheGraph protocol using custom GraphQL queries. Powerful for
complex on-chain analytics and DeFi metrics where a subgraph exists.

When to use: Querying DEX pool data (TVL, volume, fees, swap history), DeFi
protocol metrics, or any data indexed by a TheGraph subgraph.

Config: Subgraph endpoint URL, GraphQL query.

Note: You need to know the subgraph URL and schema. Search the web for
`{protocol name} subgraph` to find endpoints. Different chains have different
subgraph deployments.

### Read Deployment

Pulls output from your own custom-deployed code on K3. If a user has deployed
a custom function via K3's Innovate/Deploy feature, this reads its output.

When to use: Integrating custom code, proprietary data sources, or specialized
computations that aren't available through other read functions.

---

## AI Functions

### AI Service

Integrates AI models to summarize, analyze, or transform data. The basic AI
function — give it a prompt and data, get back analysis.

Supported models: Gemini (free via K3 credits), OpenAI, Claude (Anthropic).

When to use: Summarizing data, generating reports, formatting output, simple
analysis tasks.

### AI Web Scraper

Automatically extracts, structures, and summarizes content from web pages.

When to use: Getting data from websites that don't have APIs, monitoring web
pages for changes, extracting structured data from unstructured web content.

### AI Conditional (AI Routing)

Uses AI to analyze a situation and make a decision about workflow direction.
Enables branching logic based on AI judgment.

When to use: "Only alert me if the change is significant", "Route high-priority
events differently", or any conditional logic that's too complex for simple
if/else rules.

### AI Agent

Autonomous AI agent with advanced reasoning, tool use, and multi-step logic.
The most powerful AI function — it can decide what to do, call tools, and
orchestrate complex sequences.

When to use: Complex lookups where the AI needs to decide what to fetch,
multi-step analysis, or tasks requiring judgment and tool access.

Tool access options:
- **Web3 Data Fetcher (Uniblock)**: Lets the AI fetch on-chain data like
  historical prices, wallet transactions, etc.
- **MCP Server**: Connect to any MCP-compatible service (TheGraph, Google
  Sheets, email, databases, browsers, etc.)

### MCP Server Tool

Connects to any external service that supports Model Context Protocol. This
extends workflows beyond K3's built-in functions.

When to use: Integrating with Google Sheets, Gmail, Stripe, SQL databases,
browsers, cloud servers, or any other MCP-compatible service.

Config: MCP SSE endpoint URL, authentication credentials.

---

## Write Functions (Output & Actions)

### Write API

Sends data to any external or internal API via HTTP POST. The flexible output
function — if a service has an API, Write API can push data to it.

When to use: Sending data to webhooks, posting to external systems, triggering
actions in other platforms.

Config: URL, method, body, credentials.

### Write Smart Contract

Interacts with smart contracts to write or update on-chain data. Executes
transactions on the blockchain.

When to use: Automating on-chain actions like approvals, deposits, withdrawals,
or any smart contract interaction that changes state.

### S3 (Decentralized Storage)

Stores data to cloud storage (like AWS S3).

When to use: Archiving workflow outputs, storing historical data, saving reports
for later retrieval.

---

## DeFi & Trading Functions

These execute actual trades and token operations on-chain.

### Coinbase

Automates trading and asset operations on Coinbase.

When to use: Buying/selling tokens, portfolio rebalancing, or any Coinbase
trading automation.

### Uniswap

Executes trades and swaps on Uniswap automatically.

When to use: DEX trading automation, arbitrage, automated position management.

### Kyberswap

Automates DeFi swaps and liquidity management on Kyberswap.

When to use: Cross-DEX swap optimization, liquidity provision automation.

### Hyperliquid

Trades on Hyperliquid for DeFi automation.

When to use: Perps trading, leveraged position automation.

### Token Transfer

Moves tokens between wallets securely and automatically, triggered by any
workflow logic.

When to use: Automated payments, treasury management, token distribution,
conditional transfers based on alerts or analysis.

---

## Notification Functions

### Email

Sends custom email notifications with dynamic content from the workflow.

When to use: Daily reports, alert emails, formatted analysis deliveries.

Note: Requires an email integration (like Composio) to be connected on the team.

### Telegram

Sends real-time messages or alerts via Telegram.

When to use: Instant alerts, quick notifications, real-time monitoring updates.

Config: Bot token, chat ID.

### Slack

Sends data-driven updates to Slack channels or users.

When to use: Team notifications, shared monitoring alerts, workflow status updates.

---

## Utility Functions

### Notes

Adds comments or explanations directly in the workflow. Non-executable — purely
for documentation and clarity when viewing the workflow in the visual builder.

---

## Custom Deployments

Beyond the built-in functions, users can deploy their own code (Python, JavaScript,
etc.) as workflow steps via K3's Innovate feature. This enables:
- Unique business logic
- Connections to private APIs
- Proprietary data sources or models
- Custom computations

Deployed code becomes available as a workflow node via **Read Deployment**.
