# Plutio Skill Setup Guide

Complete instructions for setting up and configuring the Plutio skill for the first time.

## Step 1: Get Your Plutio API Credentials

1. Log in to your Plutio workspace (e.g., `https://yourname.plutio.com/`)
2. Go to **Settings** (click your profile icon)
3. Navigate to **API** (left sidebar)
4. Click **Create New Application**
5. Give it a name (e.g., "OpenClaw Integration")
6. Copy and save:
   - **Client ID** (also called App Key)
   - **Client Secret** (also called Secret Code)

**⚠️ Security**: Store these securely. Never commit them to version control.

---

## Step 2: Configure in OpenClaw (Recommended)

The easiest way to configure the Plutio skill is through OpenClaw chat.

### Via Matrix Chat

Send a message to your OpenClaw assistant:

```
Setup Plutio skill with:
- Subdomain: grewing
- Client ID: YOUR_CLIENT_ID_HERE
- Client Secret: YOUR_CLIENT_SECRET_HERE
```

The assistant will:
1. Store credentials securely in Bitwarden or local storage
2. Test the connection
3. Cache the access token for future use

---

## Step 3: Command-Line Setup (Alternative)

If you prefer to configure via command line, follow the instructions for your platform.

### macOS & Linux

**Option A: Environment Variables (Session-only)**

```bash
export PLUTIO_SUBDOMAIN="your-subdomain"
export PLUTIO_APP_KEY="your-client-id"
export PLUTIO_SECRET="your-client-secret"

# Verify
echo $PLUTIO_APP_KEY
```

**Option B: Persistent Configuration (Recommended)**

Add to your shell profile (`~/.zshrc`, `~/.bashrc`, or `~/.bash_profile`):

```bash
# Plutio API Credentials
export PLUTIO_SUBDOMAIN="your-subdomain"
export PLUTIO_APP_KEY="your-client-id"
export PLUTIO_SECRET="your-client-secret"
```

Then reload:
```bash
source ~/.zshrc  # or ~/.bashrc depending on your shell
```

**Option C: Bitwarden (Most Secure)**

Store in Bitwarden and retrieve:

```bash
# Install Bitwarden CLI if not already installed
# (On macOS with Homebrew: brew install bitwarden-cli)

# Unlock your vault
export BW_SESSION=$(bw unlock --raw)

# Retrieve credentials
export PLUTIO_APP_KEY=$(bw get password "Plutio API Key")
export PLUTIO_SECRET=$(bw get password "Plutio API Secret")
export PLUTIO_SUBDOMAIN="your-subdomain"
```

---

### Windows (PowerShell 7)

**Option A: Environment Variables (Session-only)**

```powershell
$env:PLUTIO_SUBDOMAIN = "your-subdomain"
$env:PLUTIO_APP_KEY = "your-client-id"
$env:PLUTIO_SECRET = "your-client-secret"

# Verify
Write-Host $env:PLUTIO_APP_KEY
```

**Option B: Persistent Configuration (User Profile)**

Add to your PowerShell profile:

```powershell
# Open your profile
notepad $PROFILE
```

Add these lines:

```powershell
# Plutio API Credentials
$env:PLUTIO_SUBDOMAIN = "your-subdomain"
$env:PLUTIO_APP_KEY = "your-client-id"
$env:PLUTIO_SECRET = "your-client-secret"
```

Save and reload:
```powershell
. $PROFILE
```

If you get an "ExecutionPolicy" error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Option C: Bitwarden (Most Secure)**

```powershell
# Install Bitwarden CLI via Chocolatey or download from bitwarden.com/download
choco install bitwarden-cli

# Unlock vault
$env:BW_SESSION = & bw unlock --raw

# Retrieve credentials
$env:PLUTIO_APP_KEY = & bw get password "Plutio API Key"
$env:PLUTIO_SECRET = & bw get password "Plutio API Secret"
$env:PLUTIO_SUBDOMAIN = "your-subdomain"

# Verify
Write-Host $env:PLUTIO_APP_KEY
```

**Option D: Windows Credential Manager (Windows-native)**

```powershell
# Store credential
$cred = Get-Credential -UserName "PlutioCLI" -Message "Enter your Plutio App Key"
cmdkey /generic:"Plutio" /user:"PlutioCLI" /pass:$cred.GetNetworkCredential().Password

# Retrieve later
$stored = cmdkey /list | Select-String "Plutio"
```

---

## Step 4: Test the Connection

Once configured, test with a simple command:

### macOS/Linux
```bash
python3 ~/.openclaw/workspace/skills/plutio/scripts/plutio-cli.py list-projects \
  --subdomain $PLUTIO_SUBDOMAIN \
  --app-key $PLUTIO_APP_KEY \
  --secret $PLUTIO_SECRET
```

### Windows (PowerShell 7)
```powershell
python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py list-projects `
  --subdomain $env:PLUTIO_SUBDOMAIN `
  --app-key $env:PLUTIO_APP_KEY `
  --secret $env:PLUTIO_SECRET
```

**Expected output**: List of your Plutio projects

---

## Step 5: Create an Alias (Optional, Saves Typing)

### macOS/Linux

Add to `~/.zshrc` or `~/.bashrc`:

```bash
alias plutio='python3 ~/.openclaw/workspace/skills/plutio/scripts/plutio-cli.py'
```

Then reload and use:
```bash
plutio list-projects --subdomain grewing --app-key $PLUTIO_APP_KEY --secret $PLUTIO_SECRET
```

### Windows (PowerShell 7)

Add to your profile:

```powershell
function Invoke-Plutio {
  param([Parameter(ValueFromRemainingArguments=$true)]$Args)
  python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py @Args
}
Set-Alias -Name plutio -Value Invoke-Plutio
```

Then use:
```powershell
plutio list-projects --subdomain grewing --app-key $env:PLUTIO_APP_KEY --secret $env:PLUTIO_SECRET
```

---

## Troubleshooting

### "Unauthorized" Error
- ✅ Check that Client ID and Client Secret are correct
- ✅ Verify credentials are from the **same Plutio workspace**
- ✅ Make sure credentials were copied completely (no extra spaces)

### "Module not found" or Python Error
- ✅ Ensure Python 3 is installed: `python3 --version`
- ✅ Verify the path to plutio-cli.py is correct
- ✅ On Windows, use `python3` not `python`

### Token Cache Issues
Token is cached locally for ~1 hour. To force a refresh:
- Delete the token file and retry:
  - **macOS/Linux**: `rm ~/.config/plutio/token.json`
  - **Windows**: `Remove-Item $env:USERPROFILE\.config\plutio\token.json`

### "Rate Limited" (429 Error)
- Plutio allows 1000 API calls per hour
- Wait before retrying
- Batch operations when possible

---

## Security Best Practices

### Do NOT:
- ❌ Hardcode credentials in scripts
- ❌ Commit credentials to version control
- ❌ Share credentials via email or chat (unencrypted)
- ❌ Store in plain text files

### Do:
- ✅ Use environment variables
- ✅ Store in Bitwarden or OS credential manager
- ✅ Use shell profiles for persistent setup
- ✅ Rotate credentials periodically
- ✅ Use different credentials for development vs. production (if possible)

### Credential Rotation

If you suspect your credentials were compromised:

1. Log in to Plutio
2. Go to **Settings** > **API**
3. Delete the compromised application
4. Create a new application with new Client ID/Secret
5. Update your environment variables
6. Delete old token cache

---

## OpenClaw Auto-Configuration

If you're using the Plutio skill through OpenClaw, you can ask your assistant to:

```
Configure Plutio skill with my credentials
```

The assistant will:
1. Prompt for Client ID and Client Secret (securely)
2. Store them in Bitwarden if available
3. Test the connection
4. Save configuration for future use

This is the **recommended approach** for most users.

---

## Next Steps

Once configured, you're ready to:
- List projects and tasks
- Create new tasks
- Update task status, priority, assignees, due dates
- Batch operations
- Integrate with workflows (calendars, reminders, etc.)

See [powershell-workflows.md](powershell-workflows.md) (PowerShell) or [examples.md](examples.md) (bash) for common workflows.

---

*Last updated: 2026-03-01*
