# 1Password UI - Installation Instructions

This skill adds a **1Password** tab to the OpenClaw Control dashboard under **Tools**.

> **Skill URL:** https://clawhub.ai/skills/1password-ui

## Prerequisites

✅ **OpenClaw v2026.1.0+** with source access at `~/clawdbot`

The plugin-architecture skill is **not required** — this skill adds 1Password as a core tab.

---

## Installation Steps

### Step 1: Copy Gateway Handlers

**Copy file to:** `src/gateway/server-methods/1password.ts`

```bash
cp ~/clawd/skills/1password-ui/reference/1password-backend.ts ~/clawdbot/src/gateway/server-methods/1password.ts
```

### Step 2: Register Gateway Handlers

**File:** `src/gateway/server-methods.ts`

Add import near the top:
```typescript
import { onePasswordHandlers } from "./server-methods/1password.js";
```

Add to `coreGatewayHandlers` object:
```typescript
  ...onePasswordHandlers,
```

### Step 3: Add Navigation Tab

**File:** `ui/src/ui/navigation.ts`

1. Add to Tools group in `TAB_GROUPS`:
```typescript
  { label: "Tools", tabs: ["pipedream", "zapier", "1password"] },
```

2. Add to `Tab` type:
```typescript
  | "1password"
```

3. Add to `TAB_PATHS`:
```typescript
  "1password": "/1password",
```

4. Add to `iconForTab` switch:
```typescript
    case "1password":
      return "key";
```

5. Add to `titleForTab` switch:
```typescript
    case "1password":
      return "1Password";
```

6. Add to `subtitleForTab` switch:
```typescript
    case "1password":
      return "Manage secrets and credential mappings with 1Password.";
```

### Step 4: Add App State

**File:** `ui/src/ui/app.ts`

Add these state variables (before `client: GatewayBrowserClient`):

```typescript
  // 1Password state
  @state() onePasswordLoading = false;
  @state() onePasswordMode: "cli" | "connect" | "unknown" = "unknown";
  @state() onePasswordStatus: {
    installed?: boolean;
    signedIn?: boolean;
    connected?: boolean;
    account?: string;
    email?: string;
    host?: string;
    error?: string;
  } = {};
  @state() onePasswordError: string | null = null;
  @state() onePasswordSigningIn = false;
```

### Step 5: Copy View File

**Copy file to:** `ui/src/ui/views/1password.ts`

```bash
cp ~/clawd/skills/1password-ui/reference/1password-views.ts ~/clawdbot/ui/src/ui/views/1password.ts
```

### Step 6: Add View Rendering

**File:** `ui/src/ui/app-render.ts`

1. Add import:
```typescript
import { renderOnePassword, loadOnePasswordStatus } from "./views/1password";
```

2. Add rendering (after the zapier view section, before apikeys):
```typescript
        ${state.tab === "1password"
          ? renderOnePassword({
              onePasswordLoading: state.onePasswordLoading,
              onePasswordMode: state.onePasswordMode,
              onePasswordStatus: state.onePasswordStatus,
              onePasswordError: state.onePasswordError,
              onePasswordSigningIn: state.onePasswordSigningIn,
              gatewayClient: state.client,
            })
          : nothing}
```

### Step 7: Add Tab Loading

**File:** `ui/src/ui/app-settings.ts`

1. Add import:
```typescript
import type { GatewayBrowserClient } from "./gateway";
```

2. Add the loading logic in `refreshActiveTab` function (after zapier section):
```typescript
  if (host.tab === "1password") {
    await load1PasswordStatus(host);
  }
```

3. Add the `load1PasswordStatus` function at the end of the file:
```typescript
// 1Password status loading
type OnePasswordHost = {
  onePasswordLoading: boolean;
  onePasswordMode: "cli" | "connect" | "unknown";
  onePasswordStatus: {
    installed?: boolean;
    signedIn?: boolean;
    connected?: boolean;
    account?: string;
    email?: string;
    host?: string;
    error?: string;
  };
  onePasswordError: string | null;
  client: GatewayBrowserClient | null;
};

export async function load1PasswordStatus(host: OnePasswordHost): Promise<void> {
  if (!host.client) return;

  host.onePasswordLoading = true;
  host.onePasswordError = null;

  try {
    const result = (await host.client.call("1password.status")) as {
      mode: string;
      installed?: boolean;
      signedIn?: boolean;
      connected?: boolean;
      account?: string;
      email?: string;
      host?: string;
      error?: string;
    };

    host.onePasswordMode = result.mode as "cli" | "connect" | "unknown";
    host.onePasswordStatus = {
      installed: result.installed,
      signedIn: result.signedIn,
      connected: result.connected,
      account: result.account,
      email: result.email,
      host: result.host,
      error: result.error,
    };
  } catch (e) {
    host.onePasswordError = e instanceof Error ? e.message : String(e);
  } finally {
    host.onePasswordLoading = false;
  }
}
```

### Step 8: Build and Test

```bash
cd ~/clawdbot

# Build backend
pnpm build

# Build UI
pnpm ui:build

# Restart gateway
clawdbot gateway restart
```

### Step 9: Verify Installation

1. Open the OpenClaw dashboard
2. Look in sidebar under **Tools**
3. Click **1Password** tab
4. Should see connection status (CLI not found / not signed in / connected)

---

## Quick Copy Commands

For agents, here's the full installation in copy-paste commands:

```bash
# Step 1: Copy backend
cp ~/clawd/skills/1password-ui/reference/1password-backend.ts ~/clawdbot/src/gateway/server-methods/1password.ts

# Step 5: Copy view
cp ~/clawd/skills/1password-ui/reference/1password-views.ts ~/clawdbot/ui/src/ui/views/1password.ts

# Step 8: Build
cd ~/clawdbot && pnpm build && pnpm ui:build && clawdbot gateway restart
```

Steps 2-4, 6-7 require code edits as documented above.

---

## Docker Support

For Docker installations using 1Password Connect, set these environment variables:

```yaml
services:
  clawdbot:
    environment:
      - OP_CONNECT_HOST=http://op-connect-api:8080
      - OP_CONNECT_TOKEN=your-connect-token
```

The backend automatically detects Connect mode and uses the API instead of CLI.

---

## Troubleshooting

### Tab doesn't appear
- Check TAB_GROUPS includes "1password"
- Hard refresh browser (Ctrl+Shift+R)
- Check browser console for errors

### "unknown method" error
- Ensure 1password.ts is in server-methods/
- Ensure import and spread added to server-methods.ts
- Rebuild backend: `pnpm build`

### CLI not working
- Install: `brew install 1password-cli`
- Enable CLI integration in 1Password app settings

### Sign-in fails
- Unlock 1Password app first
- Run `op signin` in terminal to authorize
