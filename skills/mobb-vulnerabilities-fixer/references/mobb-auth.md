# Mobb Authentication and Login Flow

## API Key Basics

- A Mobb account is required to authenticate and generate API keys.
- Create an API key in the Mobb web app: Settings → Access Tokens → Add API Key. Copy it immediately; it is shown only once.
- The user should configure authentication on their machine (for example, by setting `API_KEY` before launching MCP). Do not read or request environment variables directly.
- If authentication is missing or invalid, MCP triggers a browser-based login flow to authorize access.
- Optional: set `API_URL` and `WEB_APP_URL` for non-default tenant endpoints.

## Browser Login Flow (MCP)

1. MCP creates a one-time CLI login and a local RSA key pair.
2. MCP opens the default browser to the Mobb web app login URL.
3. User signs in (or creates an account) and authorizes the CLI.
4. MCP polls for an encrypted API token, decrypts it locally, and stores it for future use.
5. If the login does not complete within ~2 minutes, the flow fails and must be retried.

## User Guidance

- Always inform the user that a browser window will open for Mobb login/authorization.
- If the user does not have a Mobb account, tell them to create one and generate an API key in the Mobb app.
- If authentication fails, ask the user to retry or provide `MOBB_API_KEY`/`API_KEY` explicitly.
