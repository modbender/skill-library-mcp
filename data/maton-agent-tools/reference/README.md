# Maton Reference Implementation

This folder contains reference implementations for integrating Maton into Clawdbot Gateway and UI.

## Files

| File | Purpose |
|------|---------|
| `maton-backend.ts` | Gateway RPC handlers for Maton API |
| `maton-controller.ts` | UI state management and async operations |
| `maton-views.ts` | Lit HTML templates for the Maton UI page |

## Installation

### 1. Backend Integration

Copy `maton-backend.ts` to `src/gateway/server-methods/maton.ts`.

Add to `src/gateway/server-methods.ts`:

```typescript
import { matonHandlers } from "./server-methods/maton.js";

export const coreGatewayHandlers: GatewayRequestHandlers = {
  // ...existing handlers...
  ...matonHandlers,
};
```

### 2. UI Integration

Copy files to the UI:

```bash
cp maton-views.ts      /path/to/clawdbot/ui/src/ui/views/maton.ts
cp maton-controller.ts /path/to/clawdbot/ui/src/ui/controllers/maton.ts
```

### 3. Navigation

Update `ui/src/ui/navigation.ts`:

```typescript
// Add to TAB_GROUPS (Tools section):
{ label: "Tools", tabs: ["pipedream", "zapier", "maton", "1password"] },

// Add to Tab type:
| "maton"

// Add to TAB_PATHS:
maton: "/maton",

// Add to iconForTab:
case "maton":
  return "link";

// Add to titleForTab:
case "maton":
  return "Maton";

// Add to subtitleForTab:
case "maton":
  return "Connect to SaaS tools via Maton AI.";
```

### 4. View State

Add to `ui/src/ui/app-view-state.ts`:

```typescript
// Maton state
matonLoading?: boolean;
matonConfigured?: boolean;
matonApiKey?: string;
matonShowForm?: boolean;
matonConnectionCount?: number;
matonError?: string | null;
matonSuccess?: string | null;
matonTesting?: boolean;
matonConnections?: Array<{
  connection_id: string;
  status: "ACTIVE" | "PENDING" | "FAILED";
  creation_time: string;
  last_updated_time: string;
  url: string | null;
  app: string;
  metadata: Record<string, unknown>;
}>;
matonApps?: Array<{ id: string; name: string }>;
matonConnectingApp?: string | null;
matonDeletingConnection?: string | null;
matonShowAppPicker?: boolean;
```

### 5. App Render

Add imports to `ui/src/ui/app-render.ts`:

```typescript
import { renderMaton } from "./views/maton";
import {
  loadMatonState,
  saveMatonApiKey,
  testMaton,
  disconnectMaton,
  loadMatonConnections,
  connectMatonApp,
  deleteMatonConnection,
  loadMatonApps,
} from "./controllers/maton";
```

Add helper functions:

```typescript
function getMatonState(state: AppViewState) {
  return {
    loading: state.matonLoading ?? false,
    configured: state.matonConfigured ?? false,
    apiKey: state.matonApiKey ?? "",
    showForm: state.matonShowForm ?? false,
    connectionCount: state.matonConnectionCount ?? 0,
    error: state.matonError ?? null,
    success: state.matonSuccess ?? null,
    testing: state.matonTesting ?? false,
    connections: state.matonConnections ?? [],
    apps: state.matonApps ?? [],
    connectingApp: state.matonConnectingApp ?? null,
    deletingConnection: state.matonDeletingConnection ?? null,
    showAppPicker: state.matonShowAppPicker ?? false,
  };
}

function applyMatonResult(state: AppViewState, result: ReturnType<typeof getMatonState>) {
  Object.assign(state, {
    matonLoading: result.loading,
    matonConfigured: result.configured,
    matonApiKey: result.apiKey,
    matonShowForm: result.showForm,
    matonConnectionCount: result.connectionCount,
    matonError: result.error,
    matonSuccess: result.success,
    matonTesting: result.testing,
    matonConnections: result.connections,
    matonApps: result.apps,
    matonConnectingApp: result.connectingApp,
    matonDeletingConnection: result.deletingConnection,
    matonShowAppPicker: result.showAppPicker,
  });
}
```

Add tab rendering in `renderApp()` (between zapier and 1password). Include handler for `onShowAppPicker` that loads apps:

```typescript
onShowAppPicker: () => {
  state.matonShowAppPicker = true;
  // Load apps if not already loaded
  if (!state.matonApps || state.matonApps.length === 0) {
    loadMatonApps(state.client!, (fn) => {
      const result = fn(getMatonState(state));
      applyMatonResult(state, result);
    });
  }
},
```

### 6. App Settings (Tab Loading) — IMPORTANT

Update `ui/src/ui/app-settings.ts` to load Maton state when the tab is visited:

```typescript
// Add import at top of file
import { loadMatonState } from "./controllers/maton";

// Add after the zapier loading block (around line 233):
if (host.tab === "maton") await loadMatonState(host.client, (fn) => {
  const result = fn({
    loading: host.matonLoading ?? false,
    configured: host.matonConfigured ?? false,
    apiKey: host.matonApiKey ?? "",
    showForm: host.matonShowForm ?? false,
    connectionCount: host.matonConnectionCount ?? 0,
    error: host.matonError ?? null,
    success: host.matonSuccess ?? null,
    testing: host.matonTesting ?? false,
    connections: host.matonConnections ?? [],
    apps: host.matonApps ?? [],
    connectingApp: host.matonConnectingApp ?? null,
    deletingConnection: host.matonDeletingConnection ?? null,
    showAppPicker: host.matonShowAppPicker ?? false,
  });
  Object.assign(host, {
    matonLoading: result.loading,
    matonConfigured: result.configured,
    matonApiKey: result.apiKey,
    matonShowForm: result.showForm,
    matonConnectionCount: result.connectionCount,
    matonError: result.error,
    matonSuccess: result.success,
    matonTesting: result.testing,
    matonConnections: result.connections,
    matonApps: result.apps,
    matonConnectingApp: result.connectingApp,
    matonDeletingConnection: result.deletingConnection,
    matonShowAppPicker: result.showAppPicker,
  });
});
```

**Note:** This step is critical! Without it, the Maton state (including the apps list) won't load when navigating to the tab.

### 7. API Keys Integration

Update `ui/src/ui/controllers/apikeys.ts`:

```typescript
// Add to KNOWN_PROVIDERS:
"MATON_API_KEY": { 
  name: "Maton", 
  description: "SaaS tools integration", 
  docsUrl: "https://maton.ai" 
},

// Add to commonEnvKeys array:
"MATON_API_KEY",
```

## Build & Test

```bash
# Build gateway
cd /path/to/clawdbot
pnpm build

# Build UI
cd ui
pnpm build

# Restart gateway
clawdbot gateway restart
```

Access the Maton page at `/maton` in the dashboard.

## Troubleshooting

### App picker is empty
- Ensure `loadMatonState` is called in `app-settings.ts` (step 6)
- The apps list is loaded when the tab first opens

### API key not saving
- Check that the config file is writable
- Gateway restarts after saving to pick up new config

### Connection status stuck on PENDING
- User needs to complete OAuth flow via the provided URL
- Click "Authorize" button or the OAuth link
