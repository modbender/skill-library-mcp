# Registration — Account & Credential Setup

Walk the user through Kaggle account registration, generating all three API
credentials (KAGGLE_USERNAME, KAGGLE_KEY, KAGGLE_API_TOKEN), and saving them
securely to a `.env` file. Run the credential checker first to skip steps
that are already complete.

## Credential Check (Always Run First)

Before starting the walkthrough, check what's already configured:

```bash
python3 skills/kaggle/modules/registration/scripts/check_registration.py
```

This checks for all three credentials in env vars, `.env` file, and
`~/.kaggle/kaggle.json`. If all three are found, tell the user they're
already set up and no further action is needed.

## The 3 Credentials

| Variable | Format | Source |
|----------|--------|--------|
| `KAGGLE_USERNAME` | Kaggle handle (e.g., `johndoe`) | Account creation |
| `KAGGLE_KEY` | 32-char hex string | "Create New Token" button |
| `KAGGLE_API_TOKEN` | `KGAT_`-prefixed string | "Create API Token" button |

**Why all three?** The legacy key (`KAGGLE_KEY`) works with kaggle-cli,
kagglehub, and most MCP endpoints. The KGAT token (`KAGGLE_API_TOKEN`) is
required by some MCP endpoints that reject legacy keys (competition search,
notebook search, dataset status). Having both ensures full compatibility.

## Step 1: Create a Kaggle Account

If the user doesn't have a Kaggle account:

1. Direct them to [https://www.kaggle.com/account/login](https://www.kaggle.com/account/login)
2. Click **Register** (or sign in with Google/GitHub)
3. Fill in email, password, and choose a username (this is their `KAGGLE_USERNAME`)
4. Click **Create Account** and verify email

### Phone / Persona Verification (Optional but Recommended)

Required for competition submissions, GPU/TPU access, and restricted datasets:

1. Go to [https://www.kaggle.com/settings](https://www.kaggle.com/settings)
2. Under **Phone Verification**, click **Verify**
3. Enter phone number and SMS code

## Step 2: Generate Legacy API Key

This produces `KAGGLE_USERNAME` + `KAGGLE_KEY`:

1. Go to [https://www.kaggle.com/settings](https://www.kaggle.com/settings)
2. Scroll to the **API** section
3. Click **Create New Token** (not "Create API Token" — that's Step 3)
4. A `kaggle.json` file downloads automatically containing:
   ```json
   {"username": "your_username", "key": "your_32_char_hex_key"}
   ```
5. Ask the user for the `username` and `key` values from this file

**Security:** Tell the user to never share this file or commit it to git.

## Step 3: Generate KGAT Token

This produces `KAGGLE_API_TOKEN`:

1. Go to [https://www.kaggle.com/settings](https://www.kaggle.com/settings)
2. Scroll to the **API** section
3. Click **Create API Token** (the *other* button, not "Create New Token")
4. When prompted for scopes, recommend enabling: **Competitions**, **Datasets**, **Notebooks/Kernels**, **Models**
5. Copy the generated `KGAT_`-prefixed token
6. Ask the user to provide this token

## Step 4: Save Credentials to .env

Once all three values are collected, create or update the `.env` file:

```bash
# Create .env with all 3 credentials
cat > .env << 'ENVEOF'
KAGGLE_USERNAME=<username>
KAGGLE_KEY=<key>
KAGGLE_API_TOKEN=<token>
ENVEOF

# Secure the file
chmod 600 .env
```

Replace `<username>`, `<key>`, and `<token>` with the actual values.

Also ensure `.env` is in `.gitignore`:

```bash
if ! grep -q '^.env$' .gitignore 2>/dev/null; then
  echo '.env' >> .gitignore
fi
```

And set up `~/.kaggle/kaggle.json` for CLI/library compatibility:

```bash
mkdir -p ~/.kaggle
echo '{"username":"<username>","key":"<key>"}' > ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

## Step 5: Verify Setup

Run the checker again to confirm everything works:

```bash
python3 skills/kaggle/modules/registration/scripts/check_registration.py
```

Expected output: all three credentials show `[OK]`.

## Security Best Practices

- **Never** commit `.env` or `kaggle.json` to version control
- **Never** echo or print credential values in terminal output
- **Always** add `.env` and `.kaggle/` to `.gitignore`
- Set file permissions: `chmod 600 .env ~/.kaggle/kaggle.json`

## References

- [kaggle-setup.md](references/kaggle-setup.md) — Full step-by-step guide with troubleshooting table
