# Security Policy

## Reporting a Vulnerability

We take security seriously. If you find a vulnerability, please report it via [GitHub Issues](https://github.com/lraivisto/ResearchVault/issues) or contact the maintainer directly.

## Local-First Design

ResearchVault is designed to run entirely on your local machine. 

*   **SQLite Storage**: Data is stored locally. No cloud synchronization or hidden telemetry.
*   **SSRF Protection**: The `scuttle` tool resolve DNS and blocks access to internal/private network addresses (RFC1918, localhost, link-local) by default.
*   **Opt-in Services**: All background processes (Watchdog, MCP server) require manual invocation.
*   **Restricted Invocation**: The `disable-model-invocation: true` flag is set to prevent AI models from autonomously triggering side-effects without a direct user prompt.

## Network Access

Outbound connections are limited to:
1. User-provided research URLs.
2. The Brave Search API (if an API key is explicitly configured).

No hidden background crawling occurs.
