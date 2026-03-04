# BrowserMCP Setup Guide

Complete installation and configuration guide for the BrowserMCP MCP server and Chrome extension.

## Overview

BrowserMCP requires two components:
1. **MCP Server** - Runs via npx, handles tool execution
2. **Chrome Extension** - Connects to the browser, executes actions

## Prerequisites

- **Node.js** 18 or newer
- **Google Chrome** browser (or Chromium-based)
- **MCP Client** - VS Code, Cursor, Claude Desktop, Windsurf, or similar

## Part 1: MCP Server Setup

### Installation via npx

Add the following configuration to your MCP client:

```json
{
  "mcpServers": {
    "browsermcp": {
      "command": "npx",
      "args": ["@browsermcp/mcp@latest"]
    }
  }
}
```

### Client-Specific Instructions

#### VS Code

1. Open Settings (Ctrl/Cmd + ,)
2. Search for "MCP"
3. Click "Add Server"
4. Select "Command" type
5. Enter: `npx @browsermcp/mcp@latest`

Or use the install button:

[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install%20Server-0098FF)](https://insiders.vscode.dev/redirect?url=vscode%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522browsermcp%2522%252C%2522command%2522%253A%2522npx%2522%252C%2522args%2522%253A%255B%2522%2540browsermcp%252Fmcp%2540latest%2522%255D%257D)

#### Cursor

1. Open Settings (Ctrl/Cmd + ,)
2. Navigate to **Tools** → **New MCP Server**
3. Use type: `command`
4. Command: `npx @browsermcp/mcp@latest`

Or install via button:

[![Install in Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en/install-mcp?name=BrowserMCP&config=eyJjb21tYW5kIjoibnB4IEBicm93c2VybWNwL21jcEBsYXRlc3QifQ%3D%3D)

#### Claude Desktop

Edit `claude_desktop_config.json`:

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

Add:
```json
{
  "mcpServers": {
    "browsermcp": {
      "command": "npx",
      "args": ["@browsermcp/mcp@latest"]
    }
  }
}
```

#### Windsurf

Add to Windsurf MCP configuration:

```json
{
  "mcpServers": {
    "browsermcp": {
      "command": "npx",
      "args": ["@browsermcp/mcp@latest"]
    }
  }
}
```

See [Windsurf MCP docs](https://docs.windsurf.com/windsurf/cascade/mcp) for details.

### Verifying Server Installation

After configuration:

1. Restart your MCP client
2. BrowserMCP tools should appear in tool list
3. Try running: `navigate(url="https://example.com")`
4. If you get "No connection to browser extension", proceed to Part 2

---

## Part 2: Chrome Extension Setup

### Installation from Chrome Web Store

1. Open Chrome and go to: https://chromewebstore.google.com/detail/browser-mcp/...
   - Or search "Browser MCP" in Chrome Web Store
2. Click **"Add to Chrome"**
3. Confirm the installation

### Extension Configuration

1. **Pin the Extension** (recommended):
   - Click the puzzle piece icon in Chrome toolbar
   - Click the pin icon next to "Browser MCP"
   - Extension icon now stays visible

2. **Connect to a Tab**:
   - Navigate to the website you want to automate
   - Click the Browser MCP extension icon
   - Click **"Connect"** button
   - Status should show "Connected"

### Connection Requirements

- **One tab at a time**: BrowserMCP controls only the connected tab
- **Active connection**: Must click "Connect" on each tab you want to automate
- **Stay on tab**: Switching tabs disconnects automation
- **Extension enabled**: Must remain enabled in Chrome

### Connection Status Indicators

| Icon | Status | Meaning |
|------|--------|---------|
| 🟢 Green | Connected | Tab is ready for automation |
| 🔴 Red | Disconnected | Click Connect to enable |
| 🟡 Yellow | Error | Check extension, try reconnecting |

---

## Part 3: Testing the Setup

### Basic Connectivity Test

```javascript
// Test 1: Navigation
navigate(url="https://example.com")

// Expected: Success message + page snapshot
```

### Full Workflow Test

```javascript
// Step 1: Navigate
navigate(url="https://httpbin.org/forms/post")
wait(time=2)

// Step 2: Get page structure
snapshot()

// Step 3: Fill form (adjust refs based on your snapshot)
type(element="Customer name", ref="e5", text="Test User")
type(element="Telephone", ref="e7", text="555-1234")

// Step 4: Take screenshot
screenshot()

// Step 5: Check console
get_console_logs()
```

---

## Troubleshooting

### MCP Server Issues

#### "command not found: npx"

**Cause:** Node.js not installed or not in PATH

**Solution:**
1. Install Node.js 18+ from https://nodejs.org
2. Restart terminal/IDE
3. Verify: `npx --version`

#### "Error: Cannot find module"

**Cause:** Package installation issue

**Solution:**
```bash
# Clear npx cache
npx clear-npx-cache

# Try again with explicit install
npm install -g @browsermcp/mcp@latest
```

#### MCP Server not appearing in tools

**Cause:** Configuration not loaded

**Solutions:**
1. Restart MCP client completely
2. Check JSON syntax in config
3. Verify command path
4. Check client logs for errors

### Chrome Extension Issues

#### Extension not in Web Store

If the extension isn't available:

1. Go to: https://browsermcp.io
2. Follow download links
3. Or check GitHub releases

#### "No connection to browser extension" Error

**Diagnosis Steps:**

1. **Verify Extension Installed**:
   - chrome://extensions/
   - Look for "Browser MCP"
   - Ensure it's enabled

2. **Check Extension Icon**:
   - Look for Browser MCP icon in toolbar
   - Click it to open popup

3. **Connect to Tab**:
   - Navigate to target website
   - Click extension icon
   - Click "Connect"
   - Wait for "Connected" status

4. **Verify Correct Tab**:
   - BrowserMCP only controls the connected tab
   - Ensure you're on the right tab
   - Check URL in browser matches target

#### Connection Drops

**Symptoms:** 
- Was working, now shows connection error
- Automation stops mid-task

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Switched tabs | Go back to connected tab, or reconnect new tab |
| Browser minimized | Restore browser window |
| Extension disabled | chrome://extensions/ → re-enable |
| Page refreshed | Reconnect extension |
| Chrome updated | May need to reinstall extension |

#### Extension Permissions

Browser MCP requires these permissions:
- **Active Tab**: To see and interact with page
- **Storage**: To save connection state
- **Host permissions**: For the websites you automate

If prompts appear:
1. Click "Allow"
2. Refresh the page
3. Reconnect the extension

### Network Issues

#### Sites Not Loading

**Checks:**
1. Can you navigate manually in Chrome?
2. Check internet connection
3. Verify no VPN/proxy blocking
4. Try a simple site first (example.com)

#### Corporate Firewalls

Some corporate networks block:
- WebSocket connections (used by extension)
- Certain domains
- Third-party extensions

**Workarounds:**
- Use personal network
- Whitelist browsermcp.io
- Contact IT about extension policy

### Performance Issues

#### Slow Response Times

**Possible Causes:**
- Heavy webpage with many elements
- Slow internet connection
- Resource-intensive snapshot

**Solutions:**
- Wait longer between actions
- Close unnecessary browser tabs
- Disable browser extensions
- Use simpler test pages initially

### Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "No connection to browser extension" | Extension not connected | Click Connect in extension |
| "Element not found" | Stale ref or element removed | Take fresh snapshot |
| "Navigation timeout" | Page didn't load in time | Check URL, retry with longer wait |
| "Protocol error" | Browser communication issue | Reconnect extension |
| "Target closed" | Tab was closed | Open new tab, reconnect |

---

## Advanced Configuration

### Running on Remote/WSL

If using WSL or remote development:

1. Install extension in Windows Chrome (not WSL)
2. Use Windows Chrome as the browser
3. Configure MCP server in your WSL environment
4. Extension connects to local Chrome

### Docker/Container Environments

BrowserMCP requires a real browser with the extension. For containerized environments:

1. Use host networking to access Chrome
2. Or install Chrome + extension inside container
3. Forward X11 for headed mode (if needed)

Example Docker considerations:
```dockerfile
# Note: This is complex - BrowserMCP is designed for local use
# Consider Playwright MCP for containerized automation
```

### Multiple Chrome Profiles

BrowserMCP uses the default Chrome profile where the extension is installed. To use different profiles:

1. Install extension in desired Chrome profile
2. Launch Chrome with that profile
3. Connect extension in that profile

---

## Alternative: Using Playwright MCP

If BrowserMCP doesn't fit your needs, consider [Playwright MCP](https://github.com/microsoft/playwright-mcp):

| Feature | BrowserMCP | Playwright MCP |
|---------|------------|----------------|
| Browser | Your Chrome | New instance |
| Profile | Existing | Isolated |
| Login state | Already logged in | Must authenticate |
| Setup | Extension required | Just npx |
| Best for | Personal automation, testing auth | CI/CD, clean sessions |

---

## Getting Help

### Resources

- **Website**: https://browsermcp.io
- **Documentation**: https://docs.browsermcp.io
- **GitHub**: https://github.com/browsermcp/mcp
- **Chrome Extension**: Search "Browser MCP" in Web Store

### Reporting Issues

When reporting problems, include:
1. MCP client (VS Code, Cursor, etc.)
2. Chrome version
3. Error messages
4. Steps to reproduce
5. Screenshots if applicable

### Community

- GitHub Issues: Technical problems
- Discussions: Usage questions
- Documentation: Feature requests
