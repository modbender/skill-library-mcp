# Error Catalog

Master index of all OpenClaw error types with diagnostic and fix information.

## Error Categories

| Code | Severity | Description | Auto-Fix |
|------|----------|-------------|----------|
| **Authentication Errors** |
| 401 | High | Unauthorized - Invalid or missing API key | Yes |
| INVALID_API_KEY | High | API key format invalid or not recognized | Yes |
| TOKEN_EXPIRED | Medium | Authentication token has expired | Yes |
| MISSING_ENV_VAR | High | Required environment variable not set | Partial |
| GATEWAY_TOKEN_MISMATCH | High | Gateway token doesn't match config | No |
| **Rate Limiting Errors** |
| 429 | Medium | Too many requests - rate limit exceeded | No |
| QUOTA_EXCEEDED | High | API quota limit reached | No |
| PROVIDER_THROTTLE | Medium | Provider-side throttling active | No |
| CONCURRENT_LIMIT | Medium | Too many concurrent requests | Yes |
| BURST_LIMIT | Low | Short-term burst limit exceeded | No |
| **Gateway Errors** |
| 502 | High | Bad gateway - upstream connection failed | Partial |
| EADDRINUSE | High | Port 18789 already in use | Yes |
| ECONNREFUSED | High | Connection refused by gateway | Partial |
| NETWORK_TIMEOUT | Medium | Network request timeout | No |
| DNS_RESOLUTION | Medium | Cannot resolve hostname | No |
| **Channel Errors** |
| WHATSAPP_NOT_LINKED | High | WhatsApp not linked to gateway | No |
| TELEGRAM_WEBHOOK_FAIL | High | Telegram webhook setup failed | Partial |
| DISCORD_INVALID_PERMS | Medium | Discord bot missing permissions | No |
| SLACK_BOLT_ERROR | Medium | Slack Bolt framework error | Partial |
| SIGNAL_CLI_MISSING | High | Signal CLI not installed | Yes |
| **Sandbox Errors** |
| DOCKER_NOT_RUNNING | High | Docker daemon not running | No |
| CONTAINER_OOM | High | Container out of memory | Partial |
| SANDBOX_TIMEOUT | Medium | Sandbox execution timeout | Yes |
| WORKSPACE_MOUNT_FAIL | High | Cannot mount workspace volume | No |
| PERMISSION_DENIED | High | Sandbox permission denied | Partial |
| **Configuration Errors** |
| CONFIG_SCHEMA_INVALID | High | Config doesn't match schema | Yes |
| MISSING_REQUIRED_FIELD | High | Required config field missing | Partial |
| INVALID_VALUE_TYPE | Medium | Config value has wrong type | Yes |
| DEPRECATED_KEY | Low | Using deprecated config key | Yes |
| CONFIG_PARSE_ERROR | High | Cannot parse config file | No |
| **Installation Errors** |
| NODE_VERSION_OLD | High | Node.js version < 22 required | No |
| PNPM_NOT_FOUND | High | pnpm not installed or not in PATH | No |
| NPM_INSTALL_FAILED | High | npm/pnpm install failed | Partial |
| PATH_NOT_SET | Medium | OpenClaw not in system PATH | Yes |
| DEPENDENCY_CONFLICT | Medium | Package dependency conflict | No |
| **Plugin Errors** |
| PLUGIN_LOAD_FAILED | High | Plugin failed to load | Partial |
| PLUGIN_INIT_ERROR | High | Plugin initialization error | No |
| PLUGIN_VERSION_MISMATCH | Medium | Plugin incompatible with OpenClaw version | No |
| PLUGIN_MISSING_DEPS | High | Plugin dependencies not installed | Yes |
| PLUGIN_CONFIG_INVALID | Medium | Plugin config invalid | Partial |
| **Skill Errors** |
| SKILL_NOT_FOUND | Medium | Requested skill not installed | Yes |
| SKILL_EXEC_TIMEOUT | Medium | Skill execution timeout | Yes |
| SKILL_MANIFEST_INVALID | High | Skill manifest parse error | No |
| CLAWHUB_UNREACHABLE | Medium | Cannot connect to ClawHub | No |
| SKILL_INSTALL_FAILED | High | Skill installation failed | Partial |
| **System Errors** |
| DISK_FULL | Critical | Disk space exhausted | No |
| MEMORY_EXHAUSTED | Critical | System out of memory | No |
| FILE_NOT_FOUND | Medium | Required file missing | Partial |
| PERMISSION_ERROR | High | File system permission denied | No |
| PROCESS_CRASH | Critical | OpenClaw process crashed | No |

## Severity Levels

- **Critical**: System cannot function, immediate action required
- **High**: Major functionality broken, needs urgent fix
- **Medium**: Partial functionality impaired, fix recommended
- **Low**: Minor issue, cosmetic or deprecated feature

## Auto-Fix Capabilities

- **Yes**: Fully automated fix available
- **Partial**: Some aspects can be auto-fixed, manual steps may be needed
- **No**: Requires manual intervention

## Usage

Use error-fixer.py to diagnose and fix:

```bash
# By error code
python3 scripts/error-fixer.py --error 401

# By category
python3 scripts/error-fixer.py --category authentication

# Auto-fix when available
python3 scripts/error-fixer.py --error EADDRINUSE --auto-fix
```

See individual error category files for detailed diagnostics and fixes.
