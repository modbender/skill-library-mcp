# IEX Cloud CLI

Local helper for common IEX Cloud REST calls.

## Prerequisites

- `curl` required
- `jq` optional (for pretty JSON)
- token in `IEX_TOKEN` (preferred)
- `IEX_CLOUD_TOKEN` accepted as a compatibility alias

For OpenClaw-managed runs, prefer storing the token at `skills.entries.iex-cloud.apiKey` and resolving it through `openclaw secrets configure`.

## Usage

```bash
chmod +x scripts/iex_cloud_cli.sh
scripts/iex_cloud_cli.sh --help
```

If you set `IEX_BASE_URL` or pass `--base-url`, the CLI validates that the host is a trusted IEX API domain. Non-default trusted overrides emit a warning to stderr so config changes remain visible in logs and reviews.

## Examples

```bash
scripts/iex_cloud_cli.sh quote AAPL
scripts/iex_cloud_cli.sh chart AAPL 3m
scripts/iex_cloud_cli.sh company MSFT
scripts/iex_cloud_cli.sh stats NVDA
scripts/iex_cloud_cli.sh news TSLA 5
scripts/iex_cloud_cli.sh movers mostactive
scripts/iex_cloud_cli.sh batch AAPL,MSFT quote,stats
scripts/iex_cloud_cli.sh raw stock/AAPL/quote
```

Sandbox example:

```bash
scripts/iex_cloud_cli.sh --sandbox quote AAPL
```

Trusted custom base URL example:

```bash
IEX_BASE_URL=https://sandbox.iexapis.com/stable scripts/iex_cloud_cli.sh quote AAPL
```

`raw` requests must use relative API paths, for example `stock/AAPL/quote`. Full URLs are rejected.
