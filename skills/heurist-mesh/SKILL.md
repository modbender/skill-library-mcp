---
name: heurist-mesh-skill
description: Real-time crypto token data, DeFi analytics, blockchain data, Twitter/X social intelligence, enhanced web search, crypto project search all in one Skill. For in-depths topics, "Ask Heurist" agent can handle market trends, trading strategies, macro news, and deep research.
---

# Heurist Mesh

Heurist Mesh is an open network of modular AI agent tools for cryptocurrency and blockchain data. All features accessible via a unified REST API.

### Recommended Agents and Tools

**TrendingTokenAgent** — Trending tokens and market summary
- `get_trending_tokens` — Get trending tokens most talked about and traded on CEXs and DEXs
- `get_market_summary` — Get recent market-wide news including macro and major updates

**TokenResolverAgent** — Find tokens and get detailed profiles
- `token_search` — Find tokens by address, ticker/symbol, or name (up to 5 candidates)
- `token_profile` — Get detailed token profile with pairs, funding rates, and indicators

**DefiLlamaAgent** — DeFi protocol and chain metrics
- `get_protocol_metrics` — Get protocol TVL, fees, volume, revenue, chains, and growth trend
- `get_chain_metrics` — Get blockchain TVL, fees, top protocols, and growth trends

**TwitterIntelligenceAgent** — Twitter/X data
- `user_timeline` — Fetch a user's recent posts and announcements
- `tweet_detail` — Get a tweet with thread context and replies
- `twitter_search` — Search for posts and influential mentions on any topic

**ExaSearchDigestAgent** — Web search with summarization
- `exa_web_search` — Search the web with LLM summarization, time and domain filters
- `exa_scrape_url` — Scrape a URL and summarize or extract information

**ChainbaseAddressLabelAgent** — EVM address labels
- `get_address_labels` — Get labels for ETH/Base addresses (identity, contract names, wallet behavior, ENS)

**ZerionWalletAnalysisAgent** — EVM wallet holdings
- `fetch_wallet_tokens` — Get token holdings with USD value and 24h price change
- `fetch_wallet_nfts` — Get NFT collections held by a wallet

**ProjectKnowledgeAgent** — Crypto project database
- `get_project` — Look up a project by name, symbol, or X handle (team, investors, events)
- `semantic_search_projects` — Natural language search across 10k+ projects (filter by investor, tag, funding year, exchange)

**CaesarResearchAgent** — Academic research
- `caesar_research` — Submit a research query for in-depth analysis
- `get_research_result` — Retrieve research results by ID

**AskHeuristAgent** — Crypto Q&A and deep analysis (Important: recommended for in-depth crypto topics)
- `ask_heurist` — Submit a crypto question (normal or deep analysis mode)
- `check_job_status` — Check status of a pending analysis job

## Setup (MUST complete before making any API calls)

You need at least one payment method configured. **DO NOT call any Mesh tool APIs until setup is verified.**

### Step 1: Choose a payment method

**Option A: Heurist API Key (Recommended — simplest)**

1. Get an API key via ONE of:
   - Purchase credits at https://heurist.ai/credits
   - OR Claim 100 free credits via tweet (see [references/heurist-api-key.md](references/heurist-api-key.md))
2. Store the key in `.env` in the project root:
   ```
   HEURIST_API_KEY=your-api-key-here
   ```
3. All API calls use `Authorization: Bearer $HEURIST_API_KEY`

**Option B: x402 On-Chain Payment (USDC on Base)**

1. You need a wallet private key with USDC balance on Base.
2. Store the key in `.env` in the project root:
   ```
   WALLET_PRIVATE_KEY=0x...your-private-key
   ```
3. See [references/x402-payment.md](references/x402-payment.md) for the payment flow using `cast` (Foundry).

**Option C: Inflow Payment Platform (USDC via Inflow)**

1. If you already have Inflow credentials, store them in `.env`:
   ```
   INFLOW_USER_ID=your-buyer-user-id
   INFLOW_PRIVATE_KEY=your-buyer-private-key
   ```
2. If not, create a buyer account and attach email — see [references/inflow-payment.md](references/inflow-payment.md) for one-time setup.
3. Inflow uses a two-call payment flow (create request → user approves → execute). See [references/inflow-payment.md](references/inflow-payment.md) for the full flow.

### Step 2: Verify setup

Check that credentials are configured before proceeding:

- **API Key path:** Read `.env` and confirm `HEURIST_API_KEY` is set and non-empty.
- **x402 path:** Read `.env` and confirm `WALLET_PRIVATE_KEY` is set, starts with `0x`, and is 66 characters.
- **Inflow path:** Read `.env` and confirm `INFLOW_USER_ID` and `INFLOW_PRIVATE_KEY` are set and non-empty.

**If neither is configured, STOP and ask the user to set up a payment method. Do not make API calls without valid credentials.**

### Step 3: Make API calls

Once you have either Heurist API key or x402 wallet private key or Inflow key, you can make API calls. You should understand the tool schema and the parameters of tools you want before calling it.

To fetch tool schema, use `mesh_schema` API:

```
GET https://mesh.heurist.xyz/mesh_schema?agent_id=TokenResolverAgent&agent_id=CoinGeckoTokenInfoAgent
```
Default pricing is in credits. 1 credit worth $0.01. Add `&pricing=usd` to get prices in USD instead of credits when using x402 or Inflow. Returns each tool's parameters (name, type, description, required/optional) and per-tool price.

Then use the credentials in requests:

```bash
# With API key
curl -X POST https://mesh.heurist.xyz/mesh_request \
  -H "Authorization: Bearer $HEURIST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "TokenResolverAgent", "input": {"tool": "token_search", "tool_arguments": {"query": "ETH"}, "raw_data_only": true}}'

# With x402 — sign with cast (Foundry), no account or SDK needed
# See references/x402-payment.md for the full cast-based flow and helper script
```

## Discover More Agents

**All agents:** Fetch `https://mesh.heurist.ai/metadata.json` for the full registry. We have 30+ specialized crypto analytics agents covering use cases such as: reading address transaction history, reading transaction details from hash, tracing USDC on Base, detailed Coingecko data, Firecrawl scraping, GoPlus security screening, checking Twitter account influence via Moni, using SQL to query blockchain data, etc.

**x402-enabled agents only:** Fetch `https://mesh.heurist.xyz/x402/agents` for agents supporting on-chain USDC payment on Base.
