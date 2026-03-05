# YaCy Skill for OpenClaw

Control and manage a local YaCy search engine instance with OpenClaw.

## Quick Start

1. **Install YaCy** (already done if you followed the build steps)
   - Java 11+ and ant required
   - Build: `ant clean all` in the yacy_search_server directory
   - Start: `./startYACY.sh`

2. **Install the skill**
   - Upload to ClawHub or place in OpenClaw skills directory
   - Configure `yacy_dir` if your installation path differs

3. **Use the tools**
   - `openclaw skill yacy yacy_start` - Start the service
   - `openclaw skill yacy yacy_stop` - Stop the service
   - `openclaw skill yacy yacy_status` - Check status
   - `openclaw skill yacy yacy_search "query" [count]` - Search the web using YaCy

## Replace Brave Search with YaCy

To make YaCy your default search instead of Brave:

1. Ensure `BRAVE_API_KEY` is **not** set in your Gateway environment (or remove it)
2. Configure OpenClaw to use the YaCy skill for search queries:
   ```bash
   openclaw configure --set tools.defaultSearch=yacy_search
   ```
   Or edit your OpenClaw config to include:
   ```json
   {
     "tools": {
       "defaultSearch": "yacy_search"
     }
   }
   ```
3. Now when you ask to "search for something", OpenClaw will use YaCy instead of Brave.

> **Note:** YaCy's search quality depends on your local index. It may take time to build a comprehensive index. You can also let YaCy participate in the global P2P network to share indexes with other peers.

## Access

Open **http://localhost:8090** in your browser.

**Default credentials:**
- Username: `admin`
- Password: `yacy`

Change password after first login via *ConfigAccounts_p*.

## What is YaCy?

YaCy is a free, distributed search engine that runs entirely on your own hardware. It indexes the web (or your intranet) and can optionally share index data with other YaCy peers in a P2P network. Perfect for privacy-conscious users who want their own search engine.

## Skill Capabilities

- Start/stop the YaCy daemon
- Check if YaCy is running and responding
- View recent log entries
- Configure installation directory and port

## Building from Source (optional)

```bash
git clone --depth 1 https://github.com/yacy/yacy_search_server.git
cd yacy_search_server
sudo apt-get install openjdk-11-jdk-headless ant  # if not already installed
ant clean all
```

## Notes

- YaCy runs completely locally; no external dependencies once built
- Ports: 8090 (HTTP), 8443 (HTTPS)
- Data stored in `DATA/` directory within installation
- To disable P2P network, adjust settings in admin: http://localhost:8090/ConfigP2P_p.html

## License

GPL 2.0+ (same as YaCy)

---

Skill version: 0.1.0  
Created: 2026-02-11
