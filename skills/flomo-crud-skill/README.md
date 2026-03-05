# flomo-crud-skill

一个面向 Agent Skill 用户的 flomo Web 自动化 Skill。  它通过 Chrome MCP 操作 `https://v.flomoapp.com/mine` 页面，在已登录会话中完成 memo 的 CRUD（查询、创建、编辑、删除）。

## 一键安装

复制这一句话给任意 Agent（Codex / Claude Code / 其他）即可安装：

```text
请从 https://github.com/<your-name>/flomo-web-crud-skill 安装并启用 flomo-web-crud-skill，自动完成所需依赖与配置（包含 hangwin/mcp-chrome 与 chrome-mcp-server），执行最小可用验证（get_windows_and_tabs、chrome_navigate、chrome_read_page），然后把安装路径、配置文件路径和验证结果报告给我。
```

## What

这个 Skill 提供什么：

- 基于网页 UI 的 flomo 自动化（非官方 API）
- 完整 CRUD：`query/search`、`create/insert`、`edit`、`delete`
- 默认安全策略：
  - `edit`（文本检索定位）先列候选再写入
  - `delete` 永远二次确认
  - 不落盘保存 memo 正文
- 搜索支持滚动深扫（默认上限 `50`）

## Why

为什么要用它：

- 不依赖 flomo 官方 API
- 不需要额外 token
- 直接复用浏览器已登录状态，落地快
- 适合在 Codex / Claude Code / 类似环境里，把自然语言任务直接转成可执行的 flomo 操作

## How

如何使用（最短路径）：

1. 准备环境  
   - Chrome 已登录 flomo：`https://v.flomoapp.com/mine`  
   - Agent 会话可用 Chrome MCP（必须）  
   - 当前默认使用的 MCP 实现：[hangwin/mcp-chrome](https://github.com/hangwin/mcp-chrome)

2. 检查能力  
   你的环境至少可调用：  
   - `get_windows_and_tabs`  
   - `chrome_navigate`  
   - `chrome_read_page`  
   - `chrome_click_element`  
   - `chrome_javascript`

3. 做最小验证  
   - `get_windows_and_tabs` 能返回标签页  
   - `chrome_navigate` 能打开 flomo 页面  
   - `chrome_read_page` 能读到页面元素

4. 直接给 Agent 下指令  
   - “查找包含 `周报` 的 flomo memo”  
   - “新增一条 memo：今天把 README 开源化了”  
   - “把这条 memo 改成……（replace）”  
   - “删除这条 memo（确认后执行）”

推荐配置（更稳）：

```toml
[mcp_servers.chrome-mcp-server]
enabled = true
command = "npx"
args = ["-y", "-p", "mcp-chrome-bridge", "mcp-chrome-stdio"]
```

补充：

- 建议优先使用 `stdio` 模式
- 仍需本地安装并启用对应的 Chrome 扩展/桥接组件
- 修改 MCP 配置后通常需要完全重启客户端

---

更多细节见：

- `SKILL.md`
- `references/safety.md`
- `references/ui-locators.md`
- `references/workflows.md`

