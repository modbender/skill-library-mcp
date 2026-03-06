---
name: polymarket-bot
description: Automate Polymarket bot operations including fetching market data, placing trades, and implementing strategies like arbitrage. Use when users need to build or run bots for prediction markets, monitor prices, or execute trades on the Polygon blockchain.
---

# Polymarket Bot Skill

## Overview
This skill enables the creation and operation of a Polymarket bot for tasks such as fetching active markets, monitoring prices, placing orders, and running strategies. It's designed for users involved in cryptocurrency prediction markets, helping automate interactions via the Polymarket APIs while minimizing risks.

## Quick Start
To get started, use the scripts in this skill to initialize and run a basic bot. For example, execute `scripts/fetch_markets.py` to retrieve active markets, then use `scripts/bot_strategy.py` for arbitrage checks.

## Task-Based Structure
This skill is organized by tasks from the SOP, providing modular components for bot development.

### Step 1: Research and Setup Prerequisites
- Review Polymarket APIs (Gamma, CLOB, Data) as outlined in the SOP.
- Ensure tools like Python and Web3.py are installed.
- Reference `references/api_guide.md` for detailed API usage.

### Step 2: Define Bot Functionality and Strategy
- Implement core features like data fetching and trade execution.
- Use prompts in `references/prompts.md` to generate code for strategies.
- Example: Run `scripts/strategy_logic.py` for arbitrage detection.

### Step 3: Development Phases
- **Data Fetching Module**: Use `scripts/fetch_markets.py` to query markets.
- **Authentication and Trading Setup**: Handle in `scripts/auth_setup.py`.
- **Testing and Deployment**: Test with `scripts/test_bot.py` and deploy via references.

### Step 4: Potential Challenges and Mitigations
- Reference `references/challenges.md` for rate limits, fees, and security tips.

### Step 5: Resources
- See below for scripts and references based on the SOP.

## Resources

### scripts/
- `fetch_markets.py`: Script to fetch and parse market data from Polymarket APIs.
- `auth_setup.py`: Handles authentication and deriving API keys.
- `strategy_logic.py`: Implements bot strategies like arbitrage.
- `bot_integration.py`: Combines phases into a full bot script.

### references/
- `api_guide.md`: Documentation on Polymarket APIs and setup.
- `strategy_examples.md`: Examples of prompts for code generation.
- `challenges.md`: Common issues and mitigations for bot development.

### assets/
- (No assets needed for this skill at the moment.)

