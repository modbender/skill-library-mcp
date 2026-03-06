# bnbot-openclaw-skill

OpenClaw Skill for [BNBOT](https://chromewebstore.google.com/detail/bnbot-your-ai-growth-agen/haammgigdkckogcgnbkigfleejpaiiln) - Control Twitter/X via AI.

## Install

```bash
clawhub install jackleeio/bnbot-openclaw-skill
```

Or search for "bnbot" on [ClawHub](https://clawhub.ai/).

## User Flow

```mermaid
flowchart TD
    A["用户在 ClawHub 搜索 bnbot"] --> B["clawhub install bnbot"]
    B --> C["Skill 下载到 ~/.openclaw/skills/"]
    C --> D{"bnbot-mcp-server\n已安装?"}
    D -- No --> E["npm install -g bnbot-mcp-server\n(自动安装)"]
    E --> F["Skill 激活"]
    D -- Yes --> F
    F --> G["用户首次使用 BNBOT 功能"]
    G --> H{"~/.openclaw/openclaw.json\n已配置 bnbot MCP?"}
    H -- No --> I["AI 自动写入 mcpServers 配置"]
    I --> J["提示用户重启 OpenClaw"]
    J --> K["OpenClaw 重启"]
    H -- Yes --> K
    K --> L["MCP Server 自动启动\n(npx bnbot-mcp-server)"]
    L --> M["WebSocket 连接\nlocalhost:18900"]
    M --> N{"BNBOT 扩展\n已开启 OpenClaw?"}
    N -- No --> O["提示用户在扩展\nSettings 中开启"]
    O --> N
    N -- Yes --> P["扩展连接 WebSocket"]
    P --> Q["✅ 就绪！用户可以\n通过 AI 控制 Twitter/X"]

    style A fill:#e8f4f8
    style Q fill:#d4edda
    style E fill:#fff3cd
    style I fill:#fff3cd
    style O fill:#f8d7da
```

## Architecture

```mermaid
flowchart LR
    subgraph OpenClaw
        A[AI Agent] -->|"MCP (stdio)"| B[bnbot-mcp-server]
    end
    subgraph Local
        B -->|"WebSocket\nlocalhost:18900"| C[BNBOT Chrome Extension]
    end
    subgraph Browser
        C -->|"DOM Operations"| D[Twitter/X]
    end

    style A fill:#e8f4f8
    style B fill:#fff3cd
    style C fill:#d4edda
    style D fill:#e2e3e5
```

## What It Does

This skill automatically configures the `bnbot-mcp-server` MCP server and lets your AI assistant:

- Scrape tweets, bookmarks, and search results
- Post tweets and threads
- Reply to tweets
- Navigate Twitter/X pages
- Get account analytics

## Requirements

- [BNBOT Chrome Extension](https://chromewebstore.google.com/detail/bnbot-your-ai-growth-agen/haammgigdkckogcgnbkigfleejpaiiln) installed
- OpenClaw toggle enabled in BNBOT Settings
- Twitter/X open in Chrome

## Related

- [bnbot-mcp-server](https://github.com/jackleeio/bnbot-mcp-server) - The MCP server this skill installs
- [BNBOT Extension](https://github.com/jackleeio/BNBOT-Extension) - The Chrome extension
