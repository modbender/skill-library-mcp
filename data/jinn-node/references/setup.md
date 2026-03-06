# Setup Guide

Complete walkthrough for setting up jinn-node from scratch.

## Step 1: Check Requirements

### Node.js (20+)
```bash
node --version
```

### Python (must be 3.10 or 3.11 — NOT 3.12+)

Check system Python:
```bash
python3 --version
```

If system Python is 3.12+, check for pyenv:
```bash
pyenv versions 2>/dev/null | grep -E "3\.(10|11)"
```

**If pyenv has 3.10 or 3.11 available:** Use it for the jinn-node directory after cloning:
```bash
cd jinn-node && pyenv local 3.11.x  # use the actual version from pyenv versions
```

**If no compatible Python found:** Guide user to install Python 3.11 via pyenv:
```bash
pyenv install 3.11.9
```

### Poetry (required)
```bash
poetry --version
```

If not installed:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

---

## Step 2: Clone and Setup

### Clone and enter directory
```bash
git clone https://github.com/Jinn-Network/jinn-node.git
cd jinn-node
```

### Create .env from template
```bash
cp .env.example .env
```

---

## Step 3: Environment Configuration

### Search for existing configuration

Look for existing `.env` files that may contain relevant values:
```bash
find ~ -maxdepth 3 -name ".env" -type f 2>/dev/null | head -5
```

Search found files for relevant env vars:
- `RPC_URL` or `BASE_RPC_URL`
- `OPERATE_PASSWORD`
- `GITHUB_TOKEN`
- `GIT_AUTHOR_NAME`
- `GIT_AUTHOR_EMAIL`
- `GEMINI_API_KEY`

### Confirm with user

**If values found**, present them:

> I found these existing configuration values:
> - `RPC_URL`: https://...
> - `GITHUB_TOKEN`: ghp_...
> - `GIT_AUTHOR_NAME`: ...
>
> Would you like me to use these values? (yes/no)
> If any are outdated, please provide the correct values.

**If no values found** or user declines, ask for each required value.

### Required values

| Variable | Required | Description |
|----------|----------|-------------|
| `RPC_URL` | Yes | Base mainnet RPC (Alchemy, Infura, Tenderly) |
| `OPERATE_PASSWORD` | Yes | Wallet encryption password (min 8 chars) |
| `GEMINI_API_KEY` | If no OAuth | Gemini API key |

### Gemini authentication

Check for existing Gemini auth:
- OAuth: `~/.gemini/oauth_creds.json`
- API key: `GEMINI_API_KEY` in found env files

**If both found:**
> I found both Gemini OAuth credentials and an API key. Which would you prefer to use?
> - **OAuth** (recommended) - No API costs, uses your Google One AI Premium subscription
> - **API key** - Pay-per-use billing

**If only OAuth found:**
> I found Gemini OAuth credentials at `~/.gemini/oauth_creds.json`. Use these? (yes/no)

**If only API key found:**
> I found a Gemini API key. Use this? (yes/no)

**If neither found:**
> No Gemini credentials found. Do you have Google One AI Premium (Gemini Advanced)?
> - **Yes** → Run `npx @google/gemini-cli auth login`
> - **No** → Get API key from https://aistudio.google.com/apikey

### GitHub credentials (highly recommended)

Most venture jobs involve code tasks. Without these, the worker cannot push commits:

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | Personal access token with repo scope |
| `GIT_AUTHOR_NAME` | Commit author name |
| `GIT_AUTHOR_EMAIL` | Commit author email |

After user confirms or provides values, write them to `.env`.

---

## Step 4: Install Dependencies

```bash
yarn install
```

Python deps install automatically. If issues:
```bash
poetry install
```

---

## Step 5: Run Setup Wizard

```bash
yarn setup
```

### Funding prompt

When setup displays funding requirements:

> **Send to the displayed address:**
> - ~0.01 ETH (gas)
> - ~20 OLAS (staking)

Wait for user to confirm funding, then re-run `yarn setup` if it exited.

### Capture outputs

After success, read setup results:
```bash
cat /tmp/jinn-service-setup-*.json 2>/dev/null | head -50
```

Report **Service Config ID** and **Service Safe Address** to user.

---

## Step 6: Run the Worker

### Continuous (recommended)
```bash
yarn worker
```

### Single job test
```bash
yarn worker --single
```
