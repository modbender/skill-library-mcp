# LegiScan Bill Tracker

A skill to monitor state legislative activity using the LegiScan API. It filters for active bills based on custom keywords and state selection.

## Setup

1.  **API Key**: Obtain a free API key from [LegiScan](https://legiscan.com/legiscan).
2.  **Environment Variable**: Set `LEGISCAN_API_KEY` in your environment.
3.  **Dependencies**: Requires `requests`.

## Usage

Run the script directly or via a scheduled task (cron).

```bash
# Default (TX, cryptocurrency keywords)
python3 search.py

# Custom State and Keywords
python3 search.py --state TX --keywords "crypto, bitcoin, blockchain"

# Include passed/completed bills
python3 search.py --state TX --keywords "crypto, bitcoin, blockchain" --all
```

## Configuration Options

-   `--state`: Two-letter state abbreviation (Default: `TX` or `LEGISCAN_STATE` env var).
-   `--keywords`: Comma-separated list of terms to search for.
-   `--all`: If flag is present, includes bills that have passed or are completed.

## Best Practices
- The script uses environment variables for sensitive credentials.
- It provides CLI arguments for flexibility without modifying code.
- It includes error handling for API failures and missing configuration.