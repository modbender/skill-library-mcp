# Workflow Patterns

These are common workflow architectures on K3. When a user describes what they want,
match their request to one of these patterns and use it as the blueprint.

---

## Pattern 1: Daily Digest

The most common pattern. Fetches data on a schedule, runs AI analysis, delivers
a report.

```
[Scheduled] → [Read data] → [AI analysis] → [Email / Telegram / Slack]
```

**When to use**: "Send me daily updates about...", "I want a morning report on...",
"Track this pool and email me every day"

**Example prompt to orchestrator**: "Create a workflow that runs daily, uses Read
Graph to query the Uniswap V3 subgraph for pool metrics, then uses AI Service to
summarize performance and highlight notable changes, then sends the report via email."

**Key decisions**: What schedule? What data points? What should the AI highlight?
Where to deliver?

---

## Pattern 2: On-Demand Report

User triggers manually and optionally provides parameters. Good for ad-hoc analysis.

```
[On-Demand] → [Custom Input] → [Read data] → [AI analysis] → [Return / Email]
```

**When to use**: "Let me analyze any token on demand", "Build me a tool I can query",
"I want to check this whenever I want"

**Example**: User enters a token name → Read Market Data gets the price/volume →
AI generates an analysis → result returned or emailed.

**Key decisions**: What parameters does the user provide? How flexible should the
analysis be?

---

## Pattern 3: Wallet Monitor

Reacts to wallet activity in real time. Triggers when a specific address does
something, enriches with context, sends alert.

```
[Wallet Event] → [Read Wallet / Read API] → [AI analysis] → [Telegram / Email]
```

**When to use**: "Notify me when this wallet moves", "Watch this whale", "Alert me
on transfers from address X"

**Example**: Whale wallet triggers activity → Read Wallet gets current portfolio →
AI assesses significance → Telegram alert with summary.

**Key decisions**: Which address(es)? What counts as interesting? How fast does the
alert need to be?

---

## Pattern 4: Smart Contract Event Reactor

Listens for specific events emitted by a smart contract. More targeted than wallet
monitoring — watches a contract, not a wallet.

```
[Smart Contract Event] → [Read data for context] → [AI assess] → [Alert / Action]
```

**When to use**: "Alert me on large swaps", "Notify on Aave liquidations", "Watch
for governance proposals", "Trigger an action when a specific event happens"

**Example**: Pool contract emits Swap event → Read Market Data gets token prices for
USD conversion → AI checks if over threshold → Telegram alert.

**Key decisions**: Which contract and event? What threshold or filter? How much
context enrichment?

---

## Pattern 5: Multi-Source Comparison

Pulls from multiple data sources, feeds into AI for comparative analysis.

```
[Scheduled] → [Read source 1] → [Read source 2] → [AI compare] → [Report]
```

**When to use**: "Compare pools across DEXes", "Best yield across protocols",
"How does this token perform on different chains?"

**Example**: Read Graph → Uniswap V3 pool + Read Graph → SushiSwap pool → AI
compares TVL, volume, fees, makes recommendation.

**Key decisions**: Which sources to compare? What metrics? Should the AI recommend?

---

## Pattern 6: AI-Driven Research

Uses AI Agent with tools to dynamically research a topic. The AI decides what to
fetch based on the question.

```
[On-Demand / Scheduled] → [AI Agent with tools] → [Format / Deliver]
```

**When to use**: "Research this protocol for me", "What's happening in DeFi today?",
"Give me a comprehensive analysis" — where the data needs aren't predefined.

**Example**: AI Agent with Web3 Data Fetcher and MCP tools enabled → user asks a
question → AI decides what data to look up, fetches it, and synthesizes a report.

**Key decisions**: Which tools should the AI have access to? How broad should it go?
What's the output format?

---

## Pattern 7: Automated Trading / Action

Analyzes data and then takes an on-chain action based on the analysis.

```
[Scheduled / Event] → [Read data] → [AI Conditional] → [Uniswap / Token Transfer / Write Smart Contract]
```

**When to use**: "Swap when price hits X", "Rebalance my portfolio weekly",
"Auto-transfer tokens when conditions are met"

**Example**: Scheduled check → Read Market Data for token price → AI Conditional
checks if below target → Uniswap swap executes.

**Key decisions**: What conditions trigger the action? How much should the AI decide
vs. hard rules? What safeguards (spending limits, confirmation)?

**Important**: This pattern involves real money. Make sure the user understands
exactly what actions the workflow will take and under what conditions.

---

## Pattern 8: Data Collection & Storage

Collects data over time and stores it for historical analysis or dashboards.

```
[Scheduled] → [Read data] → [Write API / Google Sheets / S3]
```

**When to use**: "Track this metric over time", "Build a dataset of pool performance",
"Store daily snapshots for analysis later"

**Example**: Daily schedule → Read Graph for pool TVL → Write to Google Sheets with
timestamp → accumulates a historical dataset.

**Key decisions**: What data to collect? Where to store? How to handle schema over
time?

---

## Pattern 9: Web Scraping Pipeline

Extracts data from websites, processes it with AI, delivers insights.

```
[Scheduled] → [AI Web Scraper] → [AI analysis] → [Notification]
```

**When to use**: "Monitor this protocol's blog for updates", "Track governance
forum discussions", "Extract data from a site that doesn't have an API"

**Example**: AI Web Scraper pulls latest posts from a governance forum → AI
summarizes new proposals → Slack notification to the team.

**Key decisions**: Which pages to scrape? How often? What to extract vs. summarize?

---

## Pattern 10: Multi-Step Pipeline with Enrichment

Chains multiple data reads and AI steps for complex analysis.

```
[Trigger] → [Read A] → [AI process A] → [Read B based on A's output] → [AI final] → [Deliver]
```

**When to use**: Complex analyses where later steps depend on earlier results.
"Find the top-performing pools, then deep-dive into each one."

**Example**: Read Graph gets top 10 pools by volume → AI picks the most interesting
3 → Read Smart Contract gets detailed state for each → AI writes a deep analysis →
Email report.

**Key decisions**: How to chain the logic? What does each step pass to the next?
How to handle the case where intermediate data is unexpected?

---

## Pattern 11: Telegram Chatbot Agent

Connects a Telegram bot to an AI-powered workflow so users can interact with
blockchain data conversationally — just send the bot a message and get back
intelligent responses.

```
[Telegram Chatbot trigger] → [AI Agent with tools/MCP] → [Telegram reply]
```

**When to use**: "I want to chat with an AI about crypto on Telegram", "Build me
a Telegram bot that can check wallet balances", "I want on-chain data at my
fingertips in a chat"

**Example 1 — Wallet analyzer bot**: User sends a wallet address to the Telegram
bot → AI Agent receives the message → uses Read Wallet to get balances and
holdings → analyzes the portfolio → replies in Telegram with a summary.

**Example 2 — Market data assistant**: User asks "what's happening with ETH?" →
AI Agent with CoinGecko MCP fetches price, volume, and trends → generates a
concise market update → replies in the chat.

**Example 3 — DeFi research bot**: User sends "analyze the top Uniswap pools" →
AI Agent with Read Graph tool queries the subgraph → picks interesting pools →
replies with key metrics and insights.

**Key decisions**: What tools/MCPs should the AI Agent have access to? How
conversational vs. structured should the responses be? Should the bot support
follow-up questions or treat each message independently?

**Design tip**: The Telegram chatbot trigger passes the user's message as input
to the workflow. An AI Agent node is the natural fit here because it can interpret
the user's intent, decide which tools to call, and compose a natural response —
all in one step. Connect relevant MCP tools (CoinGecko, TheGraph, etc.) to give
the AI Agent access to the data it needs.

---

## Combining Patterns

Real workflows often combine elements from multiple patterns. A daily digest
might include wallet monitoring logic, or an automated trading workflow might
include a notification step. Use these patterns as starting points, then mix and
match based on what the user actually needs.
