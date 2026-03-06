# Strategy Examples for Polymarket Bot Skill

## Overview
This reference provides examples of prompts for generating code and strategies for the Polymarket bot, based on the SOP. Use these to build or extend bot functionality in Python.

## Prompt Examples
1. **Data Fetching Module Prompt**:
   "Write a Python script using requests library to fetch active markets from Polymarket's Gamma API. Include functions to list markets with filters for active=true, closed=false, and limit=20. Parse the JSON response to extract market ID, question, outcomes, and current prices. Add error handling for API failures. Output the data in a pandas DataFrame for easy analysis."

2. **Authentication Setup Prompt**:
   "Create a Python function using web3.py to authenticate with Polymarket's CLOB API. Take a private key as input, sign an EIP-712 message to derive API key, secret, and passphrase. Include code to initialize a trading client. Handle proxy wallet if using Gnosis Safe."

3. **Strategy Logic Prompt**:
   "Build a Python class for a Polymarket arbitrage bot. It should poll a specific market every 10 seconds using the CLOB API for prices. If YES price + NO price < 0.98, buy equal amounts of both, then sell the losing side when conditions are met. Include position limits and logging. Use asyncio for concurrency."

4. **Full Bot Integration Prompt**:
   "Combine the above into a complete Python script for a Polymarket trading bot. Load environment variables for private key. Run an infinite loop to monitor markets, execute strategies, and handle notifications. Add backtesting mode using historical data."

5. **Advanced Features Prompt**:
   "Extend the Polymarket bot to include copy trading. Fetch the leaderboard, select top traders, and mirror their trades with a proportional amount. Include filters and risk management."

## How to Use These Prompts
- Feed these into an AI code generator (e.g., via Grok or ChatGPT) to produce code snippets.
- Test and integrate the generated code into the skill's scripts.

This helps in iteratively developing the bot's strategies.