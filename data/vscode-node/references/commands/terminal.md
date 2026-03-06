# Terminal Command

Terminal is **disabled by default** for security. Must be enabled in extension settings, and only whitelisted commands are allowed.

## `vscode.terminal.run` — Execute command

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `command` | string | ✅ | Command (must be in whitelist) |
| `cwd` | string | ❌ | Working directory |
| `timeoutMs` | number | ❌ | Timeout (default: 30000) |

**Returns:** `{ exitCode: number, stdout: string, stderr: string, timedOut: boolean }`

### Whitelist Configuration

In extension settings:
```json
"openclaw.terminal.enabled": true,
"openclaw.terminal.allowlist": ["npm test", "npm run build", "git status"]
```

Only exact-match commands in the allowlist will execute.
