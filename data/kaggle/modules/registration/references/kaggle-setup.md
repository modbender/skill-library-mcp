# Kaggle Account & API Setup Guide

Step-by-step instructions for creating a Kaggle account, generating API credentials, and configuring them for use with any OpenClaw-compatible agent (Claude Code, gemini-cli, Cursor, etc.).

## 1. Create a Kaggle Account

1. Go to [https://www.kaggle.com/account/login](https://www.kaggle.com/account/login)
2. Click **Register** (or sign in with Google/GitHub if you prefer)
3. Fill in:
   - **Email**: your email address
   - **Password**: choose a strong password
   - **Username**: choose a username (this becomes your Kaggle handle, e.g., `yourname`)
4. Click **Create Account**
5. Verify your email by clicking the link Kaggle sends you

### Persona Verification (Required for Some Features)

Kaggle requires phone verification to:
- Submit to competitions
- Use GPU/TPU accelerators
- Download some restricted datasets

To verify:
1. Go to [https://www.kaggle.com/settings](https://www.kaggle.com/settings)
2. Under **Phone Verification**, click **Verify**
3. Enter your phone number and the SMS code

## 2. Generate Your API Credentials

You need **three** credential values for full compatibility with all Kaggle tools:

| Credential | Variable | Format | How to Get |
|-----------|----------|--------|------------|
| Username | `KAGGLE_USERNAME` | Your Kaggle handle | From account creation |
| Legacy API Key | `KAGGLE_KEY` | 32-char hex string | "Create New Token" button |
| KGAT Token | `KAGGLE_API_TOKEN` | `KGAT_`-prefixed string | "Create API Token" button |

### Step A: Legacy API Key (Create New Token)

1. Go to [https://www.kaggle.com/settings](https://www.kaggle.com/settings)
2. Scroll to the **API** section
3. Click **Create New Token**
4. A file called `kaggle.json` will download automatically
5. The file contains:
   ```json
   {"username":"your_username","key":"your_32_char_hex_key"}
   ```

This legacy key works with **all tools**: kaggle-cli, kagglehub, and most MCP Server endpoints.

### Step B: KGAT Scoped Token (Create API Token)

1. Go to [https://www.kaggle.com/settings](https://www.kaggle.com/settings)
2. Scroll to the **API** section
3. Click **Create API Token** (note: this is a *different* button from "Create New Token")
4. When prompted for scopes, enable: **Competitions**, **Datasets**, **Notebooks/Kernels**, **Models**
5. Copy the generated `KGAT_`-prefixed token

**Why both?** Some MCP Server endpoints reject legacy keys and require a KGAT token. These include competition search, notebook search, and dataset status endpoints. Having both token types ensures full compatibility.

**Warning**: KGAT tokens have scoped permissions. If you get 403/401 errors, regenerate the token with broader scopes at [https://www.kaggle.com/settings](https://www.kaggle.com/settings).

## 3. Install Your Credentials

### Method 1: .env File (Recommended for Projects)

Create a `.env` file in your project root:

```
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_32_char_hex_key
KAGGLE_API_TOKEN=KGAT_your_scoped_token
```

**Important**: Add `.env` to your `.gitignore`:
```bash
echo ".env" >> .gitignore
```

Secure the file:
```bash
chmod 600 .env
```

### Method 2: kaggle.json File

Place the downloaded `kaggle.json` in the Kaggle config directory:

```bash
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

Note: `kaggle.json` only stores username + legacy key. For the KGAT token, also set it as an environment variable or in `.env`.

### Method 3: Shell Environment Variables

Add to your shell profile (`~/.zshrc`, `~/.bashrc`):

```bash
export KAGGLE_USERNAME="your_username"
export KAGGLE_KEY="your_32_char_hex_key"
export KAGGLE_API_TOKEN="KGAT_your_scoped_token"
```

Then reload:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

## 4. Verify Your Setup

### Using the Registration Checker

```bash
python3 skills/kaggle/modules/registration/scripts/check_registration.py
```

Expected output when all credentials are configured:
```
[OK] KAGGLE_USERNAME: your_username (from env)
[OK] KAGGLE_KEY: ****abcd (from env)
[OK] KAGGLE_API_TOKEN: KGAT_****wxyz (from env)

All 3 Kaggle credentials found. You're ready to go!
```

### Manual Verification

```bash
# Test legacy key with kaggle CLI
kaggle datasets list --search "titanic" --page-size 1

# Test with kagglehub
python3 -c "import kagglehub; print(kagglehub.whoami())"
```

## 5. Credential Priority Order

When multiple credential sources exist, they are checked in this order:

| Priority | Source | Used By |
|----------|--------|----------|
| 1 | `KAGGLE_API_TOKEN` env var | CLI, kagglehub |
| 2 | `~/.kaggle/access_token` file | CLI, kagglehub |
| 3 | `KAGGLE_USERNAME` + `KAGGLE_KEY` env vars | CLI, kagglehub |
| 4 | `~/.kaggle/kaggle.json` file | CLI, kagglehub, MCP |

## 6. Common Misconfigurations

| Variable Set | Problem | Fix |
|-------------|---------|-----|
| `KAGGLE_TOKEN` instead of `KAGGLE_KEY` | kaggle-cli won't find credentials | Rename to `KAGGLE_KEY` |
| Only `KAGGLE_API_TOKEN` (KGAT) | Some CLI operations fail due to scopes | Also set `KAGGLE_KEY` with legacy key |
| Only `KAGGLE_KEY` (legacy) | Some MCP endpoints return "Unauthenticated" | Also set `KAGGLE_API_TOKEN` with KGAT |
| Credentials in env but no `kaggle.json` | Some tools only read `kaggle.json` | Run `setup_env.sh` to auto-create |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `kaggle: command not found` | Run `pip install kaggle` or check install location with `pip show kaggle` |
| `401 Unauthenticated` | Check that credentials exist and are correct |
| `403 Forbidden` on competition | Accept competition rules at kaggle.com |
| `403 Forbidden` on model | Accept model license at kaggle.com |
| `kaggle.json permissions warning` | Run `chmod 600 ~/.kaggle/kaggle.json` |
| KGAT token doesn't work for CLI | KGAT tokens have scoped permissions; use legacy key for CLI |
| MCP "Unauthenticated" on some endpoints | Use KGAT token for those endpoints |
| `dataset_load()` returns 404 | Known bug in kagglehub v0.4.3; use `dataset_download()` + `pd.read_csv()` |
| `competitions download` no `--unzip` | kaggle CLI v1.8+ removed `--unzip` for competitions; unzip manually |
