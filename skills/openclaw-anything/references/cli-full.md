# OpenClaw CLI Reference

Source: `docs.openclaw.ai/cli` + individual subcommand pages. Verified: 2026-02-27.
High-risk commands require `OPENCLAW_WRAPPER_ALLOW_RISKY=1`. See `security-policy.md`.

## ⚡ Quick Lookup

| Keyword | Section |
|---------|--------|
| setup, install, doctor, update, reset | Core Commands |
| gateway, bind, port, service, probe | Gateway Commands |
| channel, login, pairing, capabilities | Channels and Pairing |
| model, auth, alias, fallback, scan | Models |
| agent, send, deliver, thinking, identity | Agents |
| message, poll, thread, emoji, sticker | Messaging |
| security, audit, fix | Security and Secrets |
| secret, reload, apply, configure | Security and Secrets |
| memory, index, search, semantic | Memory |
| skill, list, check | Skills |
| cron, schedule, announce, deliver | Automation (Cron) |
| browser, click, type, screenshot, pdf | Browser |
| node, invoke, run, camera, screen, location | Nodes |
| device, approve, rotate, revoke | Devices |
| approval, allowlist | Approvals |
| sandbox, recreate | Sandbox |
| webhook, gmail, dns | Webhooks and DNS |
| hook, enable, bundled | Bundled Hooks |
| /status, /config, /debug | Chat Slash Commands |

## Global Flags
- `--dev`: isolate state under `~/.openclaw-dev`, shift default ports.
- `--profile <name>`: isolate state under `~/.openclaw-<name>`.
- `--no-color`: disable ANSI colors. `NO_COLOR=1` also respected.
- `--json`: machine-readable output (most commands).
- `-V`, `--version`, `-v`: print version and exit.

## Command Tree
```
openclaw [--dev] [--profile <name>] <command>
  setup
  onboard [--install-daemon]
  configure
  config get|set|unset
  completion
  doctor
  dashboard [--no-open]
  security audit [--deep] [--fix]
  secrets reload|audit|configure|apply [--from <plan.json>] [--dry-run]
  reset
  uninstall
  update
  channels list|status|logs|add|remove|login|logout
  directory
  skills list|info|check [--eligible] [--json] [-v]
  plugins list|info|install|enable|disable|doctor [--json]
  hooks list|info|check|enable|disable|install|update
  memory status|index|search [--query "<query>"]
  message send|poll|react|reactions|read|edit|delete|pin|unpin|pins|permissions|search|timeout|kick|ban
  message thread <create|list|reply>
  message emoji <list|upload>
  message sticker <send|upload>
  message role <info|add|remove>
  message channel <info|list>
  message member info
  message voice status
  message event <list|create>
  agent [--message <text>] [--to <dest>] [--channel <ch>] [--local] [--deliver] [--json]
  agents list|add|delete|bindings|bind|unbind
  acp
  status
  health
  sessions
  gateway [--port <port>] [--bind <loopback|tailnet|lan|auto|custom>] [--token <token>] [--force]
  gateway call <method> [--params <json>]
  gateway health|status|probe|discover
  gateway install|uninstall|start|stop|restart|run
  logs [--follow] [--limit <n>] [--json] [--plain] [--no-color]
  system event [--text <text>] [--mode <now|next-heartbeat>]
  system heartbeat last|enable|disable
  system presence
  models list [--all] [--local] [--provider <name>] [--json]
  models status [--check] [--probe] [--probe-provider <name>]
  models set <model>
  models set-image <model>
  models aliases list|add|remove
  models fallbacks list|add|remove|clear
  models image-fallbacks list|add|remove|clear
  models scan [--min-params <b>] [--set-default] [--set-image]
  models auth add|setup-token|paste-token
  models auth order get|set|clear
  sandbox list|recreate|explain
  cron status|list|add|edit|rm|enable|disable|runs|run
  nodes status|list|describe|pending|approve|reject|rename|invoke|run|notify
  nodes camera list|snap|clip
  nodes canvas snapshot|present|hide|navigate|eval|a2ui
  nodes screen record
  nodes location get
  devices list|approve|reject|remove|clear|rotate|revoke
  node run|status|install|uninstall|start|stop|restart
  approvals get|set|allowlist add|remove
  browser status|start|stop|reset-profile|tabs
  browser open|focus|close|navigate|resize
  browser click|type|press|hover|drag|select|upload|fill
  browser dialog|wait|evaluate|console|pdf
  browser screenshot|snapshot
  browser profiles|create-profile|delete-profile
  webhooks gmail setup|run
  pairing list|approve
  qr
  dns setup [--apply]
  docs [query...]
  tui
  voicecall (plugin; if installed)
```

## Core Commands
- `openclaw onboard [--install-daemon]`: Run onboarding wizard.
- `openclaw doctor`: Validate local install and health.
- `openclaw status`: Show global OpenClaw status.
- `openclaw version`: Print CLI version.
- `openclaw health`: Check health endpoint (standalone).
- `openclaw dashboard [--no-open]`: Open or print dashboard URL.
- `openclaw configure`: Interactive config wizard.
- `openclaw config get <key>`: Get config value.
- `openclaw config set <key> <value>`: Set config value.
- `openclaw config unset <key>`: Unset config value.
- `openclaw update`: Update CLI to latest stable build.
- `openclaw uninstall`: Remove CLI and optionally data.
- `openclaw completion`: Shell completion setup.
- `openclaw logs [--follow] [--limit <n>] [--json] [--plain]`: Structured log viewer.

## Gateway Commands
- `openclaw gateway`: Start gateway in foreground.
  - By default, requires `gateway.mode=local` in `~/.openclaw/openclaw.json`. Use `--allow-unconfigured` for ad-hoc/dev runs.
  - Binding beyond loopback without auth is blocked (safety guardrail).
  - `SIGUSR1` triggers in-process restart (controlled by `commands.restart` config key, enabled by default).
  - `--port <port>`, `--bind <loopback|tailnet|lan|auto|custom>`, `--token <token>`
  - `--auth <token|password>`, `--password <password>`
  - `--tailscale <off|serve|funnel>`, `--tailscale-reset-on-exit`
  - `--allow-unconfigured`, `--dev`, `--reset` (requires `--dev`), `--force`, `--verbose`
  - `--ws-log <auto|full|compact>`, `--compact`, `--raw-stream`, `--raw-stream-path <path>`
  - `--claude-cli-logs`: only show claude-cli logs in console
  - `--token` also sets `OPENCLAW_GATEWAY_TOKEN` for the process
  - `--password` also sets `OPENCLAW_GATEWAY_PASSWORD` for the process
- `openclaw gateway status [--deep] [--no-probe] [--json]`: Show gateway runtime status.
  - `--url <url>`, `--token <token>`, `--password <password>`, `--timeout <ms>` (default 10000)
  - `--deep`: system-level service scan. `--no-probe`: skip RPC probe.
  - Surfaces legacy or extra gateway services. Profile-named services are first-class.
- `openclaw gateway health [--url <ws://...>]`: Check gateway health endpoint.
- `openclaw gateway probe [--json]`: Probe configured remote + localhost.
  - `--ssh <user@host[:port]>`, `--ssh-identity <path>`, `--ssh-auto`
  - Related config: `gateway.remote.sshTarget`, `gateway.remote.sshIdentity`
- `openclaw gateway discover [--timeout <ms>] [--json]`: Discover gateways via Bonjour/mDNS.
  - Advertises `_openclaw-gw._tcp` service type.
  - Fields: `role`, `transport`, `gatewayPort`, `sshPort`, `tailnetDns`, `gatewayTls`, `cliPath`
- `openclaw gateway restart|stop|start`: Manage service lifecycle (all support `--json`).
- `openclaw gateway install [--port <port>] [--runtime <node|bun>] [--token <token>] [--force] [--json]`: Install gateway background service.
  - Note: `--runtime` defaults to Node; bun is not recommended (WhatsApp/Telegram bugs).
- `openclaw gateway uninstall`: Remove gateway background service.
- `openclaw gateway run`: Run gateway process.
- `openclaw gateway call <method> [--params <json>]`: Call gateway RPC methods.

## Channels and Pairing
- `openclaw channels list [--no-usage] [--json]`: List configured channels.
  - `--no-usage`: skip usage snapshot (avoids HTTP 403 if `user:profile` scope is missing).
- `openclaw channels status`: Show channel status.
- `openclaw channels logs --channel <name|all>`: Channel-specific logs.
- `openclaw channels capabilities [--channel <ch>] [--target channel:<id>]`: Probe channel capabilities.
  - Discord: intents + channel permissions. Slack: bot + user scopes. Telegram: bot flags + webhook.
  - MS Teams: app token + Graph roles/scopes. Signal: daemon version.
- `openclaw channels resolve --channel <ch> "<name>" [--kind user|group|auto]`: Resolve names to IDs.
  - Supports Slack (#channel/@user), Discord (Server/#channel), Matrix (Room Name).
- `openclaw channels add --channel <ch> [--token <bot-token>] [--delete]`: Add a channel.
  - Interactive mode: prompts for account IDs, display names, agent bindings.
  - Creates `channels.<channel>.accounts` config entries.
- `openclaw channels remove --channel <ch> [--delete]`: Remove a channel.
- `openclaw channels login --channel <name>`: Authenticate a channel (interactive).
- `openclaw channels logout --channel <name>`: Disconnect a channel.
- `openclaw pairing list [channel] [--channel <ch>] [--account <id>] [--json]`: List pairing requests.
- `openclaw pairing approve <channel> <code> [--account <id>] [--notify]`: Approve pairing (high-risk).

## Models
- `openclaw models list [--all] [--local] [--provider <name>] [--json] [--plain]`: Show available models.
- `openclaw models status [--check] [--probe] [--json] [--plain]`: Model auth and provider status.
  - `--probe-provider <name>`, `--probe-profile <id>`, `--probe-timeout <ms>`
- `openclaw models set <model>`: Set default model.
- `openclaw models set-image <model>`: Set default image model.
- `openclaw models auth add`: Interactive auth helper.
- `openclaw models auth setup-token --provider <name> [--yes]`: Setup token shorthand.
- `openclaw models auth paste-token --provider <name> [--profile-id <id>] [--expires-in <duration>]`: Direct token paste.
- `openclaw models auth order get|set|clear [--provider <name>] [--agent <id>]`: Auth priority ordering.
- `openclaw models aliases list|add|remove [--json] [--plain]`: List/add/remove alias map.
- `openclaw models fallbacks list|add|remove|clear [--json]`: Model fallback chain.
- `openclaw models image-fallbacks list|add|remove|clear [--json]`: Image model fallback chain.
- `openclaw models scan [--min-params <b>] [--max-age-days <d>] [--provider <name>] [--set-default] [--set-image] [--json]`: Discover local models.

## Agents
- `openclaw agent [--message <text>] [--to <dest>] [--session-id <id>] [--agent <id>] [--channel <ch>] [--local] [--deliver] [--json] [--timeout <s>] [--thinking <off|minimal|low|medium|high|xhigh>] [--verbose <on|full|off>]`: Send message to agent.
  - `--reply-channel <ch>` + `--reply-to <dest>`: Route agent reply to a different channel/target.
  - `--thinking` only works with GPT-5.2+ and Codex models.
  - `OPENCLAW_AGENT_DIR` / `PI_CODING_AGENT_DIR` env vars also scope agent context.
- `openclaw agents list [--json] [--bindings]`: List agents.
- `openclaw agents add [name] [--workspace <dir>] [--model <id>] [--agent-dir <dir>] [--bind <channel[:accountId]>] [--non-interactive] [--json]`: Add agent.
- `openclaw agents delete <id> [--force] [--json]`: Delete agent.
- `openclaw agents bindings [--agent <id>] [--json]`: Show bindings.
- `openclaw agents bind [--agent <id>] [--bind <channel[:accountId]>] [--json]`: Add bindings.
  - Binding without `accountId` matches channel default account only.
  - `accountId: "*"` is channel-wide fallback (less specific than explicit account).
  - Adding explicit accountId to existing channel-only binding upgrades in place.
- `openclaw agents unbind [--agent <id>] [--bind <channel[:accountId]>] [--all] [--json]`: Remove bindings.
- `openclaw agents set-identity [--workspace <dir>] [--agent <id>] [--from-identity] [--identity-file <path>] [--name <name>] [--emoji <emoji>] [--avatar <path|url>]`: Set agent identity.
  - Reads `IDENTITY.md` from workspace root when using `--from-identity`.
  - Identity fields: `name`, `theme`, `emoji`, `avatar` (stored in `agents.list[].identity`).

## Messaging
- `openclaw message send --target <dest> --message "<text>"`: Send message.
- `openclaw message poll --channel <ch> --target <dest> --poll-question "<q>" --poll-option <opt>`: Create poll.
- `openclaw message react|reactions|read|edit|delete|pin|unpin|pins|permissions|search|timeout|kick|ban`: Message operations.
- `openclaw message thread <create|list|reply>`: Thread operations.
- `openclaw message emoji <list|upload>`: Emoji operations.
- `openclaw message sticker <send|upload>`: Sticker operations.
- `openclaw message role <info|add|remove>`: Role operations.
- `openclaw message channel <info|list>`: Channel info.
- `openclaw message member info`: Member info.
- `openclaw message voice status`: Voice status.
- `openclaw message event <list|create>`: Event operations.

## Security and Secrets
- `openclaw security audit [--json]`: Audit config + local state for common security issues.
  - Checks: `session.dmScope`, `security.trust_model`, `hooks.defaultSessionKey`, `gateway.nodes.denyCommands/allowCommands`, `tools.profile`, `gateway.allowRealIpFallback`, `discovery.mdns.mode`, `sandbox.browser.cdpSourceRange`, `gateway.auth.mode`, `dangerous`/`dangerously` keywords
- `openclaw security audit --deep [--json]`: Best-effort live Gateway probe.
- `openclaw security audit --fix [--json]`: Tighten safe defaults (high-risk).
  - Flips `groupPolicy="open"` → `"allowlist"`
  - Sets `logging.redactSensitive` from `"off"` to `"tools"`
  - Tightens permissions for state/config files (`credentials/*.json`, `auth-profiles.json`, `sessions.json`, `*.jsonl`)
  - Does NOT: rotate tokens, disable tools, change bind/auth/network
- `openclaw secrets reload [--json]`: Re-resolve refs via `secrets.reload` RPC. Keeps last-known-good on failure.
- `openclaw secrets audit [--check] [--json]`: Scan for plaintext residues, unresolved refs, precedence drift.
  - Finding codes: `PLAINTEXT_FOUND`, `REF_UNRESOLVED`, `REF_SHADOWED`, `LEGACY_RESIDUE`
  - `--check`: exits non-zero on findings.
  - JSON summary: `plaintextCount`, `unresolvedRefCount`, `shadowedRefCount`, `legacyResidueCount`
- `openclaw secrets configure [--providers-only] [--skip-provider-setup] [--apply] [--yes] [--plan-out <path>] [--json]`: Interactive helper.
  - Workflow: provider setup → credential mapping → preflight → optional apply.
  - `--providers-only`: configure `secrets.providers` only.
  - `--skip-provider-setup`: skip provider setup, map to existing providers.
  - Generated plans enable scrub options by default (`scrubEnv`, `scrubAuthProfilesForProviderTargets`, `scrubLegacyAuthJson`).
  - Without `--apply`, still prompts "Apply this plan now?" after preflight.
  - Targets secret-bearing fields: `models.providers.*.apiKey`, `skills.entries.*.apiKey`, etc.
- `openclaw secrets apply --from <plan.json> [--dry-run] [--json]`: Apply a previously generated plan (high-risk).
  - Mutates: `openclaw.json`, `auth-profiles.json`, legacy `auth.json`, `~/.openclaw/.env`
  - No rollback backups by design. Use `--dry-run` first.

## System
- `openclaw system event [--text <text>] [--mode <now|next-heartbeat>] [--json]`: Push system events.
- `openclaw system heartbeat last|enable|disable [--json]`: Heartbeat management.
- `openclaw system presence [--json]`: Presence info.

## Memory
Memory is provided by the `memory-core` plugin. Disable with `plugins.slots.memory = "none"` in config.
- `openclaw memory status [--deep] [--agent <id>]`: Show index stats.
  - `--deep`: probes vector + embedding availability.
  - `--deep --index`: runs reindex if store is dirty.
- `openclaw memory index [--verbose] [--agent <id>]`: Reindex memory files.
  - `--verbose`: prints per-phase details (provider, model, sources, batch activity).
  - Includes extra paths from `memorySearch.extraPaths` config.
- `openclaw memory search "<query>" [--query "<query>"] [--agent <id>]`: Semantic search over memory.
  - Query input: positional `[query]` or `--query <text>` (flag wins if both provided).

## Skills
- `openclaw skills list [--eligible] [--json] [-v]`: List skills.
- `openclaw skills info <name>`: Show details for one skill.
- `openclaw skills check`: Summary of ready vs missing requirements.

## Automation (Cron)
- `openclaw cron status [--json]`: Cron engine status.
- `openclaw cron list [--all] [--json]`: List cron jobs (table by default).
- `openclaw cron add --name <name> (--at|--every|--cron) (--system-event|--message)`: Create cron job (high-risk).
  - `--announce`: announce to channel. `--deliver` / `--no-deliver`: control delivery.
  - `--at` + `--keep-after-run`: one-time job that persists after execution.
  - `--channel <ch>`, `--to <dest>`: delivery target for announce.
- `openclaw cron edit <id> [--announce] [--channel <ch>] [--to <dest>] [--no-deliver]`: Edit job (high-risk).
- `openclaw cron rm <id>`: Delete job (aliases: `remove`, `delete`) (high-risk).
- `openclaw cron enable <id>` / `cron disable <id>`: Toggle job.
- `openclaw cron runs --id <id> [--limit <n>]`: View run history.
  - Run logs stored at `~/.openclaw/cron/runs/<jobId>.jsonl`.
  - `cron.sessionRetention` (default 24h) prunes completed sessions.
  - `cron.runLog.maxBytes` + `cron.runLog.keepLines` prune log files.
- `openclaw cron run <id> [--force]`: Run job immediately (high-risk).

## Browser
Common flags: `--url <gatewayWsUrl>`, `--token <token>`, `--timeout <ms>`, `--browser-profile <name>`, `--json`.

### Browser Profiles
Two built-in profile types:
- `openclaw`: dedicated OpenClaw-managed Chrome instance (isolated user data dir).
- `chrome`: controls existing Chrome tabs via Chrome extension relay.

- `openclaw browser profiles`: List browser profiles.
- `openclaw browser create-profile --name <name> [--color <hex>] [--cdp-url <url>]`: Create profile.
- `openclaw browser delete-profile --name <name>`: Delete profile.
- `openclaw browser --browser-profile <name> <subcommand>`: Use specific profile.

### Browser Extension Relay
- `openclaw browser extension install`: Install Chrome extension.
- `openclaw browser extension path`: Show extension path.
- Attach via `chrome://extensions` → load unpacked.

### Remote Browser Control
- Via node host proxy: `gateway.nodes.browser.mode` + `gateway.nodes.browser.node` config.

### Lifecycle
- `openclaw browser status|start|stop`: Manage browser runtime (high-risk).
- `openclaw browser reset-profile`: Reset browser profile.

### Tabs
- `openclaw browser tabs`: List open tabs.
- `openclaw browser open <url>`: Open URL in new tab.
- `openclaw browser focus <targetId>`: Focus tab.
- `openclaw browser close [targetId]`: Close tab.

### Navigation & Capture
- `openclaw browser navigate <url> [--target-id <id>]`: Navigate tab.
- `openclaw browser screenshot [targetId] [--full-page] [--ref <ref>] [--element <sel>] [--type png|jpeg]`: Capture screenshot.
- `openclaw browser snapshot [--format aria|ai] [--target-id <id>] [--interactive] [--compact] [--depth <n>] [--selector <sel>] [--out <path>] [--limit <n>]`: Capture structured page snapshot.
- `openclaw browser pdf [--target-id <id>]`: Export page as PDF.

### Interaction
- `openclaw browser resize <width> <height> [--target-id <id>]`: Resize viewport.
- `openclaw browser click <ref> [--double] [--button <left|right|middle>] [--modifiers <csv>] [--target-id <id>]`: Click element.
- `openclaw browser type <ref> <text> [--submit] [--slowly] [--target-id <id>]`: Type into element.
- `openclaw browser press <key> [--target-id <id>]`: Press key.
- `openclaw browser hover <ref> [--target-id <id>]`: Hover element.
- `openclaw browser drag <startRef> <endRef> [--target-id <id>]`: Drag and drop.
- `openclaw browser select <ref> <values...> [--target-id <id>]`: Select dropdown.
- `openclaw browser upload <paths...> [--ref <ref>] [--input-ref <ref>] [--element <sel>] [--target-id <id>] [--timeout-ms <ms>]`: File upload.
- `openclaw browser fill [--fields <json>] [--fields-file <path>] [--target-id <id>]`: Fill form.
- `openclaw browser dialog --accept|--dismiss [--prompt <text>] [--target-id <id>] [--timeout-ms <ms>]`: Handle dialogs.
- `openclaw browser wait [--time <ms>] [--text <value>] [--text-gone <value>] [--target-id <id>]`: Wait for conditions.
- `openclaw browser evaluate --fn <code> [--ref <ref>] [--target-id <id>]`: Execute JavaScript.
- `openclaw browser console [--level <error|warn|info>] [--target-id <id>]`: Read console logs.

## Nodes
Common flags: `--url`, `--token`, `--timeout`, `--json`.

### Node Management
- `openclaw nodes status [--connected] [--last-connected <duration>] [--json]`: Node status.
- `openclaw nodes list [--connected] [--last-connected <duration>] [--json]`: List nodes.
  - `--last-connected` accepts durations like `24h`, `7d`.
- `openclaw nodes describe --node <id|name|ip>`: Describe a node.
- `openclaw nodes pending`: List pending approvals.
- `openclaw nodes approve <requestId>`: Approve node (high-risk).
- `openclaw nodes reject <requestId>`: Reject node.
- `openclaw nodes rename --node <id|name|ip> --name <displayName>`: Rename node.

### Remote Execution (Highest Risk)
- `openclaw nodes invoke --node <id|name|ip> --command <command> [--params <json>] [--invoke-timeout <ms>] [--idempotency-key <key>]`: Invoke command on node.
  - Default params: `{}`. Default invoke timeout: 15000ms.
- `openclaw nodes run --node <id|name|ip> [--cwd <path>] [--env KEY=VAL] [--command-timeout <ms>] [--invoke-timeout <ms>] [--needs-screen-recording] <command...>`: Run shell on node.
  - `--raw <command>`: Run a shell string (`/bin/sh -lc` or `cmd.exe /c`).
  - `--agent <id>`: Agent-scoped approvals/allowlists.
  - `--ask <off|on-miss|always>`, `--security <deny|allowlist|full>`: Security mode overrides.
  - Reads `tools.exec.*` config (+ `agents.list[].tools.exec.*` overrides).
  - Uses exec approvals (`exec.approval.request`) before invoking `system.run`.
  - `--node` can be omitted when `tools.exec.node` is set.
  - Note: node hosts ignore `PATH` overrides; `tools.exec.pathPrepend` not applied to node hosts.
  - On Windows node hosts, `cmd.exe /c` shell-wrapper runs always require approval.

### Notifications & Sensors
- `openclaw nodes notify --node <id|name|ip> [--title <text>] [--body <text>] [--sound <name>] [--priority <passive|active|timeSensitive>] [--delivery <system|overlay|auto>] [--invoke-timeout <ms>]`: Push notification (macOS only).
- `openclaw nodes camera list --node <id|name|ip>`: List cameras.
- `openclaw nodes camera snap --node <id|name|ip> [--facing front|back|both] [--device-id <id>] [--max-width <px>] [--quality <0-1>] [--delay-ms <ms>] [--invoke-timeout <ms>]`: Take photo (high-risk).
- `openclaw nodes camera clip --node <id|name|ip> [--facing front|back] [--device-id <id>] [--duration <ms|10s|1m>] [--no-audio] [--invoke-timeout <ms>]`: Record video clip (high-risk).
- `openclaw nodes canvas snapshot|present|hide|navigate|eval|a2ui`: Canvas/UI overlay commands.
- `openclaw nodes screen record --node <id|name|ip> [--duration <ms|10s>] [--fps <n>]`: Record screen (high-risk).
- `openclaw nodes location get --node <id|name|ip> [--accuracy <coarse|balanced|precise>]`: Get location (high-risk).

## Node Host
- `openclaw node run --host <gateway-host> --port 18789`: Run node.
- `openclaw node status`: Node status.
- `openclaw node install [--host <host>] [--port <port>] [--tls] [--runtime <node|bun>] [--force]`: Install node service.
- `openclaw node uninstall|stop|restart`: Node lifecycle.

## Devices
- `openclaw devices list [--json]`: List devices.
- `openclaw devices approve [requestId] [--latest]`: Approve device (high-risk).
- `openclaw devices reject <requestId>`: Reject device.
- `openclaw devices remove <deviceId>`: Remove device (high-risk).
- `openclaw devices clear --yes [--pending]`: Clear devices (high-risk).
- `openclaw devices rotate --device <id> --role <role> [--scope <scope...>]`: Rotate device credentials (high-risk).
- `openclaw devices revoke --device <id> --role <role>`: Revoke device role (high-risk).

## Approvals
- `openclaw approvals get [--node <id|name|ip>] [--gateway] [--json]`: Get approval policies.
  - `--node`: scope to a specific node. `--gateway`: scope to gateway.
- `openclaw approvals set --file <path> [--node <id|name|ip>] [--gateway]`: Replace approvals from file.
- `openclaw approvals allowlist add <pattern> [--agent <id>] [--node <id|name|ip>]`: Add to allowlist.
  - `--agent` defaults to `"*"` (all agents). Patterns support globs.
  - Stored at `~/.openclaw/exec-approvals.json`.
- `openclaw approvals allowlist remove <pattern>`: Remove from allowlist.
- Note: `--node` resolves via same resolver as `openclaw nodes` (id, name, ip, or id prefix).

## Sandbox
- `openclaw sandbox explain [--session <key>] [--agent <id>] [--json]`: Explain sandbox config.
- `openclaw sandbox list [--browser] [--json]`: List sandboxes.
  - Shows: container name/status, Docker image match, age, idle time, session/agent.
  - `--browser`: only list browser containers.
- `openclaw sandbox recreate [--all] [--session <key>] [--agent <id>] [--browser] [--force] [--json]`: Recreate sandbox (high-risk).
  - Use cases: after Docker image update, config change, `setupCommand` change.

## Webhooks and DNS
- `openclaw webhooks gmail setup|run [--account <email>] [--project] [--topic]`: Gmail webhook integration (high-risk).
- `openclaw dns setup [--apply]`: Local DNS setup (high-risk, `--apply` requires sudo on macOS).

## Other
- `openclaw docs [query...]`: Search docs from CLI.
- `openclaw qr`: QR code generation.
- `openclaw tui`: Terminal UI.
- `openclaw acp`: Agent Communication Protocol.
- `openclaw directory`: Directory listing.
- `openclaw voicecall`: Voice call plugin (if installed).
- `openclaw doctor [--fix] [--yes]`: Validate install. `--fix` applies repairs.
## Chat Slash Commands
- `/status`: Quick diagnostics.
- `/config`: Persisted config changes.
- `/debug`: Runtime-only config overrides (requires `commands.debug: true`).

## Bundled Hooks
Four bundled hooks (disabled by default, enable via `openclaw hooks enable <name>`, restart gateway):
- `session-memory`: Save context on `/new` → `memory/YYYY-MM-DD-slug.md`
- `bootstrap-extra-files`: Inject `AGENTS.md`/`TOOLS.md` on agent bootstrap
- `command-logger`: Log to `~/.openclaw/logs/commands.log` (JSONL)
- `boot-md`: Run `BOOT.md` on gateway startup

---
Config hot reload and env var details → see `config-schema.md`.
