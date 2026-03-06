# Local Portfolio Auditor Skill for ClawBot

## Overview

The **Local Portfolio Auditor** is a privacy-focused ClawBot skill designed to help users monitor their cryptocurrency and stock holdings. It operates by reading a local configuration file (`portfolio.json`) and querying public, read-only APIs to fetch current market data. This approach ensures that sensitive private keys or personal financial data are never exposed to the bot or external services beyond the public API calls.

## Features

*   **Privacy-Focused:** All configuration is stored locally. No private keys are ever requested or stored.
*   **Read-Only Access:** Interacts only with public APIs to retrieve market data.
*   **Cryptocurrency Tracking:** Supports tracking Ethereum balances via address and other cryptocurrencies by amount and CoinGecko ID.
*   **Stock Tracking:** Monitors stock values based on symbols and share counts.
*   **Customizable:** Easily configure your assets in a local `portfolio.json` file.

## Installation

1.  **Create Skill Directory:** Create a new folder named `local-portfolio-auditor` in your ClawBot skills directory (e.g., `~/.openclaw/skills/` or `<project>/skills/`).
2.  **Download Files:** Place the `SKILL.md`, `main.py`, `requirements.txt`, and `portfolio.json` files into this new directory.
3.  **Install Dependencies:** Navigate to the `local-portfolio-auditor` directory in your terminal and install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure `portfolio.json`:** Edit the `portfolio.json` file to include your cryptocurrency addresses and stock symbols. See the example below.

## Usage

Once installed and configured, you can trigger the skill via your ClawBot interface using phrases like:

*   "audit my portfolio"
*   "check my crypto holdings"
*   "what's my stock value"

### Example `portfolio.json` Configuration

```json
{
    "crypto": [
        {"type": "ETH", "address": "0xYourEthereumAddressHere", "coin_id": "ethereum"},
        {"type": "BTC", "coin_id": "bitcoin", "amount": 0.05},
        {"type": "ADA", "coin_id": "cardano", "amount": 100.0}
    ],
    "stocks": [
        {"symbol": "AAPL", "shares": 10},
        {"symbol": "GOOGL", "shares": 5},
        {"symbol": "MSFT", "shares": 20}
    ]
}
```

**Note on `coin_id`:** For cryptocurrencies, use the `id` from CoinGecko (e.g., `ethereum` for ETH, `bitcoin` for BTC, `cardano` for ADA). You can find these IDs on the CoinGecko website or their API documentation.

**Note on API Keys:** For stock data, a free and reliable API often requires an API key and may have rate limits. For production use, consider obtaining an API key for services like Alpha Vantage and setting it as an environment variable (e.g., `ALPHAVANTAGE_API_KEY`). The `main.py` script is designed to read `ETHERSCAN_API_KEY` as an environment variable for Ethereum balance lookups. If not set, it will use dummy values.

## Security Considerations

*   **API Keys:** Never hardcode API keys directly into `main.py`. Always use environment variables.
*   **Read-Only:** This skill is designed to be read-only. It does not support transactions or access to private keys.
*   **Public APIs:** Relies on public APIs. Be aware of their terms of service and rate limits.

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests on the GitHub repository for this skill.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
