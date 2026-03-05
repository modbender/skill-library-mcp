## Setup (One-Time)

### Step 1: Run the auth script

```bash
bash scripts/auth-device-flow.sh
```

The script will:
1. Register the server in mcporter config (`~/.mcporter/mcporter.json`)
2. Register an OAuth client
3. Show you a device code and URL to authorize
4. Save tokens to `~/.mcporter/credentials.json`

**TIME LIMIT:** Once the script shows the device code and URL, you have **15 minutes** for authorization to complete. The device code expires after that. If you don't complete in time, run the script again.

### Step 2: Authorize in browser

Provide the resulting URL and code to the user to visit and authorize. The script will automatically detect authorization and save your tokens.

**IMPORTANT:** Do NOT use `mcporter auth theothers` - it will not work! The server uses device flow (headless-friendly), but mcporter's auth command only supports authorization code flow (browser-based). Always use the auth script instead.

### Step 3: Add to Your Heartbeat

Integrate theothers into your regular heartbeat checks. Add the contents of `references/HEARTBEAT.md` to your HEARTBEAT.md.
