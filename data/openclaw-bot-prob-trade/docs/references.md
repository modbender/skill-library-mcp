# References: Autonomous Trading on Polymarket

Curated library of research, tools, and frameworks for building trading bots on Polymarket with OpenClaw and prob.trade.

Based on the research article: [Autonomous Trading on Polymarket: Architecture, Strategies, and Deployment](https://prob.trade/blog/autonomous-polymarket-trading-architecture)

---

## Polymarket Architecture & API

1. [The Polymarket API: Architecture, Endpoints, and Use Cases](https://medium.com/@gwrx2005/the-polymarket-api-architecture-endpoints-and-use-cases-f1d88fa6c1bf) — Three-layer architecture overview: Gamma API, CLOB, on-chain settlement.

2. [What is Polymarket?](https://docs.polymarket.com/) — Official documentation. Conditional Token Framework (CTF), YES/NO token mechanics, price = probability.

3. [Fetching Market Data](https://docs.polymarket.com/quickstart/fetching-data) — Gamma API endpoints for market discovery, filtering by category, condition_id mapping.

4. [Developer Quickstart](https://docs.polymarket.com/quickstart/overview) — CLOB REST endpoints, WebSocket subscriptions (`wss://ws-subscriptions-clob.polymarket.com`), real-time orderbook.

5. [Trades Overview](https://docs.polymarket.com/developers/CLOB/trades/trades-overview) — Order lifecycle, RETRYING/FAILED states, block reorg considerations.

6. [Trading](https://docs.polymarket.com/developers/market-makers/trading) — EIP-712 signing, order structure, fee rate BPS, maker/taker amounts.

7. [Code Examples for Polymarket](https://github.com/Polymarket/examples) — Official example code for interacting with Polymarket smart contracts and CLOB.

---

## OpenClaw Framework

8. [OpenClaw (Formerly Clawdbot & Moltbot) Explained](https://milvusio.medium.com/openclaw-formerly-clawdbot-moltbot-explained-a-complete-guide-to-the-autonomous-ai-agent-9209659c2b8b) — Complete guide to the autonomous AI agent framework.

9. [From Clawdbot to Moltbot to OpenClaw: How to Command the World's Most Viral AI Agent](https://medium.com/@ryanshrott/from-clawdbot-to-moltbot-to-openclaw-how-to-command-the-worlds-most-viral-ai-agent-8944a76f8f67) — Skill system, SKILL.md format, script architecture.

10. [OpenClaw GitHub Repository](https://github.com/openclaw/openclaw) — Source code, installation, daemon mode, configuration.

11. [ClawHub Skill Directory](https://github.com/openclaw/clawhub) — Official skill registry. How to publish and discover skills.

12. [Awesome OpenClaw Skills](https://github.com/VoltAgent/awesome-openclaw-skills) — Community-curated collection of OpenClaw skills.

13. [How to Set Up OpenClaw on a Private Server](https://www.hostinger.com/tutorials/how-to-set-up-openclaw) — VPS deployment guide. Node.js 22+, systemd daemon, security hardening.

14. [Running OpenClaw in Docker](https://til.simonwillison.net/llms/openclaw-docker) — Containerized deployment pattern.

15. [From Clawdbot to Moltbot to OpenClaw: Why This AI Agent Grew Up](https://medium.com/@munish.munagala/from-clawdbot-to-moltbot-to-openclaw-why-this-ai-agent-grew-up-instead-of-burning-out-005189861ff3) — Architecture evolution and design decisions.

---

## Trading Strategies & Implementations

### Momentum & Contrarian

16. [+1,560% ROI With OpenClaw Polymarket Trading (prompt included!)](https://www.youtube.com/watch?v=YknxNkTgNWk) — AI Contrarian Momentum and TBO Trend Breakout on 15m/1h crypto markets. ADX, Bollinger Bands, circuit breaker after 3 losses. $20 position cap.

17. [AI Agents For Polymarket (Free & Open Source)](https://www.youtube.com/watch?v=CDAw8ReKmns) — Whale tracking, expiration timing volatility, social sentiment divergence strategies.

### Arbitrage

18. [Inside the Mind of a Polymarket BOT](https://coinsbench.com/inside-the-mind-of-a-polymarket-bot-3184e9481f0a) — Asynchronous pair cost arbitrage. Buying YES + NO when combined cost < $1.00.

19. [ent0n29/polybot](https://github.com/ent0n29/polybot) — MIT. Reverse-engineered Polymarket strategies. Position management module, executor service for low-latency orders.

20. [chainstacklabs/polyclaw](https://github.com/chainstacklabs/polyclaw) — MIT. Logic arbitrage skill for OpenClaw. LLM finds contradictions between correlated markets. Tier 1 (>95% confidence) = near-arbitrage.

### Market Making

21. [Dynamic Spread Market Making Strategy](https://medium.com/@FMZQuant/dynamic-spread-market-making-strategy-74e279d148dd) — SMA/EMA-based fair price, dynamic spread widening on volatility, inventory skew management.

22. [gigi0500/polymarket-market-maker-bot](https://github.com/gigi0500/polymarket-market-maker-bot) — Market making bot architecture for Polymarket CLOB.

23. [lorine93s/polymarket-market-maker-bot](https://github.com/lorine93s/polymarket-market-maker-bot) — Production-ready market maker. Inventory management, cancel/replace cycles, automated risk controls.

### Multi-Agent & Ensemble

24. [neural-trader (NPM)](https://www.npmjs.com/package/neural-trader) — 7-agent ensemble with Byzantine consensus (5/7 quorum for trade entry). News, sentiment, on-chain, risk agents.

### Value Investing & AI-Driven

25. [randomness11/probablyprofit](https://github.com/randomness11/probablyprofit) — MIT. AI-powered trading framework. LLM estimates fair probability, buys when market undervalues by 20%+. Kelly criterion sizing, multi-model consensus (Claude, GPT-4, Gemini).

26. [ProbablyProfit Releases](https://github.com/randomness11/probablyprofit/releases) — Config.yaml pattern: agent/risk/platforms sections. Docker Compose deployment.

### Weather & Domain-Specific

27. [Weather Trading Bots Making $24,000 on Polymarket](https://blog.devgenius.io/found-the-weather-trading-bots-quietly-making-24-000-on-polymarket-and-built-one-myself-for-free-120bd34d6f09) — NOAA/ECMWF forecast vs market price delta. 15%+ divergence trigger.

### Whale Tracking & Copy Trading

28. [NYTEMODEONLY/polyterm](https://github.com/NYTEMODEONLY/polyterm) — Polymarket terminal. Wallet tracking, smart money detection, crypto 15m market data. `polyterm wallets --type smart`.

29. [Awesome Prediction Market Tools](https://github.com/aarora4/Awesome-Prediction-Market-Tools) — Curated list: AI agents, analytics, APIs, dashboards, copy trading, alerting.

### NLP & Sentiment

30. [Predicting Market Sentiment with Social Media: A Deep Learning Approach](https://medium.datadriveninvestor.com/predicting-market-sentiment-with-social-media-a-deep-learning-approach-to-fintech-trading-91993eca0af4) — FinBERT for social sentiment classification.

31. [Step-by-Step DIY Guide: Hugging Face FinBERT AI Model Setup for News Sentiment](https://medium.datadriveninvestor.com/step-by-step-diy-guide-hugging-face-finbert-ai-model-setup-for-news-sentiment-779c62f58b16) — FinBERT setup guide for sentiment analysis pipelines.

---

## Infrastructure & Deployment

32. [How to Setup a Polymarket Bot: Step-by-Step Guide](https://www.quantvps.com/blog/setup-polymarket-trading-bot) — VPS requirements: 2 vCPU, 4 GB RAM, 20 GB SSD for basic setup. 8+ vCPU for ensembles.

33. [Automated Trading on Polymarket: Bots, Arbitrage & Execution](https://www.quantvps.com/blog/automated-trading-polymarket) — Rate limiting, slippage, exponential backoff, WebSocket vs REST.

---

## Security

34. [Researchers Find 341 Malicious ClawHub Skills Stealing Data from OpenClaw Users](https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html) — ClawHavoc supply-chain attack. 12% of ClawHub skills contained malware. Atomic Stealer (AMOS) targeting crypto wallets.

35. [Helpful Skills or Hidden Payloads? Bitdefender Labs on OpenClaw Malicious Skills](https://www.bitdefender.com/en-us/blog/labs/helpful-skills-or-hidden-payloads-bitdefender-labs-dives-deep-into-the-openclaw-malicious-skill-trap) — Attack vectors: fake pre-requisites in SKILL.md, obfuscated bash scripts via glot.io, Base64-encoded payloads.

36. [Key OpenClaw Risks | Kaspersky](https://www.kaspersky.com/blog/moltbot-enterprise-risk-management/55317/) — Enterprise risk management for OpenClaw deployments. Prompt injection, filesystem access.

37. [Securing OpenClaw Agents From ClawHavoc Supply-Chain Attacks](https://www.aryaka.com/blog/securing-openclaw-agents-clawhavoc-supply-chain-attack-ai-secure-protection/) — Sandboxing, Docker isolation, `agents.defaults.sandbox.mode: "non-main"`.

38. [Technical Advisory: OpenClaw Exploitation in Enterprise Networks](https://businessinsights.bitdefender.com/technical-advisory-openclaw-exploitation-enterprise-networks) — C2 server patterns, detection signatures, mitigation strategies.

39. [OpenClaw's 180K-Star Marketplace Was 12% Malware](https://www.pixee.ai/weekly-briefings/openclaw-malware-ai-agent-trust-2026-02-11) — Analysis of malware distribution in skill ecosystem.

40. [Trellix Insights Preview on OpenClaw Threats](https://www.trellix.com/advanced-research-center/insights-preview/) — Threat intelligence on AI agent exploitation.

---

## prob.trade

41. [prob.trade Dashboard](https://app.prob.trade) — Create account, deposit USDC, generate API keys.
42. [prob.trade Trading API Reference](https://prob.trade/docs/trading-api) — HMAC authentication, order placement, positions, balance endpoints.
43. [prob.trade Public Analytics API](https://prob.trade/docs/public-api) — Market search, breaking markets, hot markets, top traders.
44. [probtrade OpenClaw Skill on ClawHub](https://clawhub.ai/probtrade/prob-trade-polymarket-analytics) — Install and configure the API access skill.
