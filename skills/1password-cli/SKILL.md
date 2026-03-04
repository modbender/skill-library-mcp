# 1Password CLI for Agents

This skill allows agents to securely access and manage secrets using the 1Password CLI (`op`) and a Service Account. It provides commands for reading, writing, and managing items within a dedicated vault.

## Prerequisites

1.  **Install 1Password CLI:**
    -   macOS: `brew install --cask 1password-cli`
    -   Linux/Windows: See [official docs](https://developer.1password.com/docs/cli/get-started).
2.  **Create a Service Account:**
    -   Go to [1Password Developer Portal](https://developer.1password.com/).
    -   Create a Service Account and grant it access to a specific vault (e.g., "Agent Vault").
    -   Copy the Service Account Token.
3.  **Set Environment Variable:**
    -   Set `OP_SERVICE_ACCOUNT_TOKEN` in your environment (e.g., `.env` file or export in shell).
    -   For OpenClaw, you can add `OP_SERVICE_ACCOUNT_TOKEN=...` to `.env`.

## Usage

All commands require the `OP_SERVICE_ACCOUNT_TOKEN` to be set.

### 1. Check Authentication

Verify the service account is working:

```bash
op whoami
```

### 2. List Vaults

List vaults accessible to the service account:

```bash
op vault list
```

### 3. Read an Item

Get details of an item (JSON format is best for parsing):

```bash
op item get "Item Name" --vault "Vault Name" --format json
```

Or get a specific field (e.g., password):

```bash
op read "op://Vault Name/Item Name/password"
```

### 4. Create an Item

Create a login item:

```bash
op item create --category login --title "My Service" --url "https://example.com" --vault "Vault Name" username="myuser" password="mypassword"
```

Create a secure note:

```bash
op item create --category "Secure Note" --title "API Key" --vault "Vault Name" notes="my-secret-key"
```

### 5. Edit an Item

Update a password:

```bash
op item edit "Item Name" password="newpassword" --vault "Vault Name"
```

### 6. Delete an Item

```bash
op item delete "Item Name" --vault "Vault Name"
```

## Tips for Agents

-   **Always use JSON output:** Add `--format json` to `op` commands for structured data that is easier to parse.
-   **Security:** Never print the `OP_SERVICE_ACCOUNT_TOKEN` or retrieved secrets to the console unless explicitly asked.
-   **Vaults:** If multiple vaults are available, specify the `--vault` flag to avoid ambiguity.
-   **Rate Limits:** Service accounts have rate limits. Cache results if possible or retry with backoff.

## Troubleshooting

-   **"You are not currently signed in":** Ensure `OP_SERVICE_ACCOUNT_TOKEN` is set correctly.
-   **"account is not authorized":** Check that the service account has permission for the specific vault and operation (read/write).
