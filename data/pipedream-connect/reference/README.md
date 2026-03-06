# Reference Implementation

These files are the actual OpenClaw source code for the Pipedream integration. They are included for reference when:

- Debugging issues with the integration
- Building custom integrations
- Understanding the OAuth flow
- Extending functionality

## Files

### pipedream-backend.ts

Gateway RPC handlers that run server-side. Key functions:

- `pipedream.status` — Returns connection status and configured apps
- `pipedream.saveCredentials` — Validates and stores OAuth credentials
- `pipedream.getToken` — Gets fresh access token from stored credentials
- `pipedream.getConnectUrl` — Creates Pipedream Connect token for OAuth flow
- `pipedream.connectApp` — Saves app config to mcporter.json
- `pipedream.disconnectApp` — Removes app from mcporter.json
- `pipedream.refreshToken` — Updates stored access token

**Important:** All Pipedream API calls are made server-side to avoid CORS issues.

### pipedream-controller.ts

UI controller logic that handles user interactions:

- `loadPipedreamState` — Fetches current state from backend
- `savePipedreamCredentials` — Validates and saves credentials via backend
- `connectPipedreamApp` — Handles the full OAuth flow:
  1. Check if app already has tools (OAuth done)
  2. If not, get connect URL and open popup
  3. After OAuth, save config
- `disconnectPipedreamApp` — Removes app connection
- `testPipedreamApp` — Tests if app tools are accessible
- `refreshPipedreamAppToken` — Manually refresh token

### pipedream-views.ts

Lit templates for the UI. Includes:

- Credentials form
- Connected apps list
- Available apps grid
- App browser modal with search
- Manual slug entry
- Setup guide

## Key Implementation Details

### App Slug Format

- **UI uses hyphens:** `google-calendar`
- **MCP uses underscores:** `google_calendar`
- Backend converts automatically

### SSE Response Handling

The MCP endpoint may return Server-Sent Events:

```
event: message
data: {"result":{...},"jsonrpc":"2.0","id":1}
```

Parse by finding lines starting with `data: ` and extracting JSON.

### OAuth Flow

1. User clicks Connect
2. Check `tools/list` — if empty, OAuth needed
3. Call `pipedream.getConnectUrl` to get OAuth URL
4. Open popup with URL including `&app=<slug>`
5. User completes OAuth in popup
6. User clicks Connect again
7. `tools/list` now returns tools
8. Save config to mcporter.json

### Token Refresh

Tokens expire after 1 hour. The refresh script:

1. Reads credentials from `pipedream-credentials.json` or mcporter.json
2. Calls Pipedream OAuth endpoint for new token
3. Updates all `pipedream-*` servers in mcporter.json

## Modifying

If you need to modify this integration:

1. The actual source is in `~/openclaw/src/` and `~/openclaw/ui/src/`
2. After changes, run `npm run build` and `npm run ui:build`
3. Restart gateway: `openclaw gateway restart`

These reference files are snapshots and won't affect the running system.
