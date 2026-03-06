# IMA Agent Skill

[中文](#chinese) | [English](#english)

---

<a id="chinese"></a>

# IMA Skill (中文版)

通过 Chrome DevTools Protocol (CDP) 协议，实现对腾讯 **IMA (ima.copilot)** 桌面客户端（AI 知识库助手）的自动化控制。本 Skill 支持全网自动化搜索，并具备独特的**私有知识库注入**功能，无需手动切换即可在查询中自动调用私有知识库。

## ✨ 核心特性

- **🤖 全自动控制**：自动启动、连接并控制 IMA 桌面客户端。
- **🧠 知识库注入**：当查询包含 `@knowledge` 或 `@个人知识库` 标记时，自动注入配置好的 `Knowledge ID`，无需人工干预即可搜索私有数据。
- **🛡️ 零乱码输出**：采用先进的 DOM 提取技术（DOM Extraction），绕过 CDP 网络层的编码缺陷，确保输出完美的 UTF-8 中文结果。
- **🔌 API 拦截**：通过底层 API 拦截技术，强制开启知识库模式。

## 📦 环境要求

- **操作系统**：macOS (已在 macOS 14/15 上验证)
- **IMA 客户端**：需安装在 `/Applications/ima.copilot.app`
- **Python 3**：需安装 `websocket-client` 库

```bash
pip3 install websocket-client
```

## ⚙️ 配置说明

要使用 **私有知识库** 功能，你需要配置你的 Knowledge ID。

1.  **获取 ID**：
    *   打开 IMA 客户端，手动切换到“知识库”模式。
    *   使用网络抓包工具（或 Skill 提供的嗅探脚本）捕获 `/cgi-bin/assistant/qa` 请求。
    *   在请求体（Body）中找到 `"knowledge_ids": ["YOUR_ID_HERE"]` 字段。

2.  **创建配置文件**：
    将 `config.json.sample` 复制为 `config.json`：

    ```bash
    cp config.json.sample config.json
    ```

    编辑 `config.json`：
    ```json
    {
      "knowledge_id": "YOUR_CAPTURED_ID"
    }
    ```

*注意：`config.json` 已被加入 `.gitignore`，以保护你的隐私。*

## 🚀 使用方法

### 命令行调用

**普通全网搜索：**
```bash
python3 scripts/ima.py "DeepSeek V3 分析"
```

**私有知识库搜索：**
(需要先完成配置)
```bash
python3 scripts/ima.py "@knowledge 年度报告分析"
# 或者
python3 scripts/ima.py "@个人知识库 分析新大陆"
```

### 集成到 Clawdbot

本 Skill 专为 [Clawdbot](https://github.com/clawdbot/clawdbot) 设计。安装到 `skills/ima` 后，你可以直接对 Agent 说：

> "用 IMA 搜一下最新的 AI 新闻"
> "去个人知识库查一下关于 Project X 的会议纪要"

## 🛠️ 工作原理

1.  **CDP 连接**：连接到 IMA 的远程调试端口 (8315)。
2.  **请求拦截**：监听 `/qa` API 请求。
3.  **载荷注入**：如果查询被标记为私有，动态修改 JSON 请求体，插入你的 `knowledge_ids`。
4.  **DOM 提取**：等待 React/Vue 页面渲染完成，直接从 DOM 树中提取文本，彻底规避网络层的数据包编码问题。

---

<a id="english"></a>

# IMA Skill (English)

Control the **IMA.copilot** desktop application (AI knowledge base assistant) via Chrome DevTools Protocol (CDP). This skill enables automated searching and, uniquely, **injects private knowledge base context** into queries without manual switching.

## ✨ Features

- **🤖 Automated Control**: Auto-launch and control the IMA desktop app.
- **🧠 Private Knowledge Injection**: Automatically injects your private `Knowledge ID` when the query contains `@knowledge` or `@个人知识库`.
- **🛡️ Zero-Garbled Output**: Uses advanced DOM extraction techniques to bypass CDP encoding issues, ensuring perfect UTF-8 Chinese characters output.
- **🔌 API Interception**: Intercepts network requests to force-enable knowledge base mode programmatically.

## 📦 Requirements

- **macOS** (Tested on macOS 14/15)
- **IMA.copilot App**: Installed in `/Applications/ima.copilot.app`
- **Python 3**: With `websocket-client` installed.

```bash
pip3 install websocket-client
```

## ⚙️ Configuration

To use the **Private Knowledge Base** feature, you need to configure your Knowledge ID.

1.  **Find your ID**:
    *   Open IMA, manually switch to your Knowledge Base.
    *   Use a network sniffer (or check logs) to find the `/cgi-bin/assistant/qa` request.
    *   Look for `"knowledge_ids": ["YOUR_ID_HERE"]` in the request body.

2.  **Create Config File**:
    Copy `config.json.sample` to `config.json`:

    ```bash
    cp config.json.sample config.json
    ```

    Edit `config.json`:
    ```json
    {
      "knowledge_id": "YOUR_CAPTURED_ID"
    }
    ```

*Note: `config.json` is git-ignored to protect your privacy.*

## 🚀 Usage

### Command Line

**Public Search:**
```bash
python3 scripts/ima.py "Analysis of DeepSeek V3"
```

**Private Knowledge Base Search:**
(Requires configuration)
```bash
python3 scripts/ima.py "@knowledge Annual Report Analysis"
# OR
python3 scripts/ima.py "@个人知识库 分析新大陆"
```

### Clawdbot Integration

This skill is designed for [Clawdbot](https://github.com/clawdbot/clawdbot). Once installed in `skills/ima`, you can ask your agent:

> "Use IMA to search for the latest AI news"
> "Check my personal knowledge base for the meeting minutes about Project X"

## 🛠️ How it Works

1.  **CDP Connection**: Connects to IMA's debugging port (8315).
2.  **Request Interception**: Listens for `/qa` API requests.
3.  **Payload Injection**: If the query is marked private, it modifies the JSON payload on-the-fly to include your `knowledge_ids`.
4.  **DOM Extraction**: Waits for the React/Vue app to render, then extracts text directly from the DOM to avoid network-layer encoding bugs.

## License

MIT
