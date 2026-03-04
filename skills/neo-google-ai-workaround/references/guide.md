# Implementation Guide & Best Practices

## Session Management Best Practices

### Token Lifecycle
1. **Create** a session with initial auth token.
2. **Monitor** token expiry; refresh proactively before expiration.
3. **Rotate** sessions when restrictions are detected.
4. **Destroy** expired or compromised sessions immediately.

### Session Persistence
- Sessions are persisted to `assets/.sessions/` as JSON files.
- Tokens are redacted before writing to disk for security.
- In-memory session state includes full token data for active use.

### Session Rotation Strategy
- On rate limit detection: rotate to a new session with different proxy.
- On auth failure: refresh token first; if refresh fails, create new session.
- On IP block: switch proxy and create new session.

## Proxy Configuration

### Rotation Strategies

| Strategy | Use Case |
|----------|----------|
| `round-robin` | Default; even distribution across proxies |
| `least-used` | When proxies have different capacity limits |
| `random` | When predictable patterns should be avoided |

### Health Checks
- Proxies are health-checked by tracking failure counts.
- After `maxFailures` (default: 3), a proxy is marked unhealthy.
- Health check cycles can recover proxies with reduced failure counts.

### Adding Proxies
```bash
# Via CLI
node scripts/main.js proxy-add --host proxy.example.com --port 8080

# Via config file
# Edit assets/config-template.json and add to the "proxies" array
```

## Restriction Detection

### Detection Flow
1. API response is passed to the Detector.
2. Each restriction pattern is tested against the response.
3. Matched patterns generate recommended actions.
4. Actions are prioritized by severity (critical > high > medium > low).

### Handling Detected Restrictions

| Restriction | Action | Description |
|-------------|--------|-------------|
| Rate Limit | `rotate_session` | Create new session to reset rate counters |
| Auth Expired | `refresh_token` | Refresh the current session's auth token |
| Geo Block | `switch_proxy` | Switch to a proxy in an allowed region |
| IP Block | `switch_proxy` | Switch to a non-blocked proxy |
| Service Unavailable | `wait_retry` | Wait and retry after a delay |
| Access Denied | `rotate_session` | Rotate session and optionally switch proxy |

## CLI Usage Examples

### Full Workflow
```bash
# 1. Check current status
node scripts/main.js status

# 2. Configure proxies
node scripts/main.js proxy-add --host proxy1.example.com --port 8080
node scripts/main.js proxy-add --host proxy2.example.com --port 8080

# 3. Create a session
node scripts/main.js session-create

# 4. Monitor for restrictions
node scripts/main.js detect

# 5. View diagnostics
node scripts/main.js diagnostics

# 6. Clean up
node scripts/main.js session-destroy
```

## Integration with OpenClaw Agents

### Agent Workflow
1. Agent detects Google AI access issue.
2. Agent triggers `google-ai-workaround` skill.
3. Skill analyzes the restriction type.
4. Skill applies the appropriate mitigation (session rotation, proxy switch, token refresh).
5. Agent receives updated session credentials.
6. Agent retries the Google AI request.

### Programmatic Usage
```javascript
const { runCommand, loadConfig } = require("./scripts/main");

const config = loadConfig();
const result = runCommand("detect", { silent: true }, config);

if (result.diagnostics.restrictedCount > 0) {
  runCommand("session-rotate", { silent: true }, config);
}
```
