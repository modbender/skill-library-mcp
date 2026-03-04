# Connect to Local Device

Deploy a BRICKS application and connect to devices on the local network.

## 1. Discover Devices

Scan the LAN for DevTools-enabled devices:

```bash
bricks devtools scan -j
```

The JSON output includes `deviceId`, `name`, `address`, `port`, `workspaceId`, and `hasPasscode` for each device.

Filter to devices matching the current workspace — compare each device's `workspaceId` against the CLI profile's workspace (shown by `bricks auth status`). Ignore devices from other workspaces.

Options:
- `-t <ms>` — scan timeout (default 3000)
- `--verify` — verify each server via HTTP
- `--udp-only` — skip HTTP subnet probe

## 2. Bind Devices to App

Once you have the target device IDs, bind them to the application:

```bash
# Bind specific devices
bricks app bind <app-id> -b <device-id-1>,<device-id-2>

# Unbind devices
bricks app bind <app-id> -u <device-id>

# Bind and unbind in one call
bricks app bind <app-id> -b <new-device> -u <old-device>
```

After binding, the device will load the application on next refresh. Force an immediate reload:

```bash
bricks device refresh <device-id>
```

## 3. Connect via MCP for Debugging

Use [mcporter](https://mcporter.dev) to bridge the device's MCP endpoint so Claude Code (or other MCP clients) can interact with it directly:

```bash
mcporter call --url http://<device-ip>:19851/mcp --header "Authorization: Bearer <passcode>"
```

Through MCP tools you can check device status, read logs, trigger automations, and debug issues without leaving the agent workflow.
