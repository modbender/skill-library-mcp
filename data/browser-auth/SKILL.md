---
name: browser-auth
description: Start a secure remote browser tunnel for manual user authentication (solving Captchas, 2FA, logins) and capture session data. Built for AI Commander.
metadata: {
  "author": "Skippy & Lucas (AI Commander)",
  "homepage": "https://aicommander.dev",
  "env": {
    "AUTH_HOST": { "description": "IP to bind the server to (default: 127.0.0.1). Use 0.0.0.0 only with a secure tunnel.", "default": "127.0.0.1" },
    "AUTH_TOKEN": { "description": "Secret token for accessing the tunnel (default: random hex string)." },
    "BROWSER_PROXY": { "description": "SOCKS5/HTTP proxy for the browser (e.g. socks5://127.0.0.1:40000)." }
  },
  "openclaw": {
    "requires": { "bins": ["node", "chromium-browser"] },
    "install": [
      {
        "id": "npm-deps",
        "kind": "exec",
        "command": "npm install express socket.io playwright-core",
        "label": "Install Node.js dependencies"
      }
    ]
  }
}
---

# Browser Auth

This skill allows the agent to request the user to perform a manual login on a website and then capture the session cookies/localStorage for further automated work.

## 🚨 Security & Risk Mitigation

We take security seriously. Below is how we address common concerns related to remote browser control:

### 1. Remote Code Execution (RCE) Protection
*   **Always Sandboxed**: Chromium runs with the system sandbox **ENABLED**. There is no option to disable it in the code. This prevents a malicious website from escaping the browser and executing code on your host.
*   **Isolation Recommendation**: We recommend running this skill within an isolated container (Docker) or a dedicated VM for an extra layer of protection.

### 2. Token Leakage (Referrer Protection)
*   **Referrer Policy**: The server enforces `Referrer-Policy: no-referrer`. This ensures that even if you navigate to an untrusted site, your secret `AUTH_TOKEN` is NEVER sent in the HTTP Referer header.
*   **URL Cleansing**: The interface automatically clears the `token` parameter from your browser's address bar immediately after the page loads.

### 3. Data Sensitivity
*   **Session Artifacts**: The `session.json` file contains active login cookies. Treat it with the same level of security as a password.
*   **Mandatory Cleanup**: Always delete the session file immediately after the agent finishes its task.
*   **No Persistence**: This skill does not store credentials long-term or exfiltrate them to external servers.

### 4. Network Exposure
*   **Default Local Bind**: By default, the server binds to `127.0.0.1`. 
*   **Secure Access**: If you need remote access, do not bind to `0.0.0.0` directly. Instead, use a secure tunnel like **Tailscale**, **Cloudflare Tunnel (cloudflared)**, or an **SSH tunnel**.

## When to Use

- When a website requires manual interaction to solve Captcha or 2FA.
- When bot detection prevents automated login.
- When you want to authorize an agent without sharing your password.

## Workflow

1.  **Request Auth**: Start the tunnel using `scripts/auth_server.js`.
2.  **Provide Link**: Share the link (including token) with the intended user over a secure channel.
3.  **Wait for Session**: The user logs in and clicks **DONE** in the web UI.
4.  **Verify**: Use `scripts/verify_session.js` to confirm the session is valid.
5.  **Cleanup**: Delete the session file once the task is complete.

## Tools

### Start Auth Server
```bash
AUTH_HOST=127.0.0.1 AUTH_TOKEN=mysecret node scripts/auth_server.js <port> <session_file>
```

### Verify Session
```bash
node scripts/verify_session.js <session_file> <target_url> <expected_text>
```

## Runtime Requirements
Requires: `express`, `socket.io`, `playwright-core`, and a system `chromium-browser`.
