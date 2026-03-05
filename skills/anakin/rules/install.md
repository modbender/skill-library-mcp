---
name: anakin-cli-installation
description: |
  Install the Anakin CLI and handle authentication errors.
---

# Anakin CLI Installation

## Quick Install

```bash
pip install anakin-cli
```

## Verify Installation

Check if installed and authenticated:

```bash
anakin status
```

Output will show:
- Authentication status
- API endpoint
- Account information

## Authentication

If not authenticated, run:

```bash
anakin login --api-key "ak-your-key-here"
```

Get your API key from [anakin.io/dashboard](https://anakin.io/dashboard).

## Error Handling

If ANY command returns an authentication error (e.g., "not authenticated", "unauthorized", "HTTP 401", "invalid API key"):

1. **First, check authentication status:**
   ```bash
   anakin status
   ```

2. **If not authenticated, use an ask user question tool if available:**

   **Question:** "How would you like to authenticate with Anakin?"

   **Options:**
   1. **Enter API key** - Get an API key from anakin.io/dashboard
   2. **Already have an API key** - Paste your existing API key

### If user needs to get an API key:

Tell them to:
1. Visit [anakin.io/dashboard](https://anakin.io/dashboard)
2. Sign up or log in
3. Generate an API key (starts with `ak-`)
4. Copy the key

Then run:
```bash
anakin login --api-key "ak-their-key-here"
```

### If user has an API key:

Ask for their API key, then run:

```bash
anakin login --api-key "ak-their-key-here"
```

Or set the environment variable:

```bash
export ANAKIN_API_KEY="ak-their-key-here"
```

Tell them to add this export to `~/.zshrc` or `~/.bashrc` for persistence:

```bash
echo 'export ANAKIN_API_KEY="ak-your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

After authentication, retry the original command.

## Troubleshooting

### Command not found

If `anakin` command is not found after installation:

1. Check if Python bin is in PATH:
   ```bash
   echo $PATH | grep -o "[^:]*bin"
   ```

2. Try with full path:
   ```bash
   python -m anakin --version
   ```

3. Add Python bin to PATH:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   # Add to ~/.zshrc or ~/.bashrc for persistence
   ```

4. Or reinstall:
   ```bash
   pip install --user anakin-cli
   ```

### Permission errors

If you get permission errors during installation:

```bash
# Use --user flag (recommended)
pip install --user anakin-cli

# Or use a virtual environment
python -m venv anakin-env
source anakin-env/bin/activate
pip install anakin-cli
```

### HTTP 429 (Rate Limited)

If commands return HTTP 429 errors:
- Wait before retrying (do not loop immediately)
- The user has hit rate limits
- Check their plan at [anakin.io/dashboard](https://anakin.io/dashboard)

### HTTP 401 (Unauthorized)

If commands return HTTP 401 after authentication:
- API key may be invalid or expired
- Run `anakin login --api-key "new-key"` with a fresh key
- Check [anakin.io/dashboard](https://anakin.io/dashboard) for valid keys

## Best Practices for Agents

1. **Always check status first** before running anakin commands
2. **Always quote URLs** to prevent shell interpretation issues
3. **Always use `-o <file>`** to save output to files
4. **On authentication errors**, use the error handling flow above
5. **On rate limit errors**, wait and inform the user
6. **Default to markdown format** unless user asks for JSON
