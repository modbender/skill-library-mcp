# Security notes (Docker MCP Toolkit)

- Bind ports to **127.0.0.1** by default.
- Do **not** expose the MCP endpoint publicly.
- If remote access is required, prefer **SSH tunnel** or **WireGuard** over opening ports.
- Use a dedicated database user with least privilege.
- Rotate credentials immediately if pasted into chat.
