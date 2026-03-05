# Grok Twitter Search - 部署与配置指南

本技能采用标准化的环境变量注入，完美兼容 OpenClaw Gateway 架构，并提供友好的纯数字菜单引导脚本。

## 📋 快速初始化 (推荐)

我们提供了一个交互式向导，支持一键配置 API Key、模型偏好并解释 WARP 代理原理。
请使用 `uv` 启动向导（无需全局安装依赖）：

```bash
uv run scripts/setup_interactive.py
```
*注：该向导会在本地生成 `.env` 文件，方便独立测试。如需接入 OpenClaw，请参考下方步骤 2 注入 Gateway。*

---

## 🔧 OpenClaw 生产环境接入步骤

### 步骤 1：确保 WARP 代理运行（防止 403 / 超时）
xAI 的接口对部分地区极其严格，推荐开启 WARP 作为“隐身衣”。
```bash
# 检查 SOCKS5 端口
netstat -tuln | grep 40000
# 预期输出应包含监听状态
```

### 步骤 2：注入 Gateway 环境变量 (核心)
OpenClaw 的技能是无状态的，必须将配置写入宿主环境：

```bash
# 编辑 OpenClaw Gateway 环境变量文件
nano ~/.openclaw/gateway.env
```
追加以下内容：
```env
# Grok Twitter Search Skill Config
GROK_API_KEY=你的_API_KEY
SOCKS5_PROXY=socks5://127.0.0.1:40000
```
保存后，必须重启 Gateway 加载配置：
```bash
openclaw gateway restart
```

### 步骤 3：纯数字交互模式测试
除了自动化调用，你可以随时进入交互菜单测试网络与双模态引擎：

```bash
uv run scripts/search_twitter.py
```
**菜单界面：**
```text
===============================
  Grok 推特检索引擎 (多模态)
===============================
当前代理: socks5://127.0.0.1:40000
1. 极速检索推文 (低成本，grok-4-1-fast)
2. 深度舆情分析 (附带推理，grok-4-1-fast-reasoning)
0. 退出程序
===============================
请输入数字选择功能: 
```

---

## 🧠 Agent 触发话术指南

配置完成后，在 OpenClaw 前端对话框中直接下达指令。Agent 会根据你的意图**自动路由**模型：

* **触发极速模式（省钱省时）**：
  🗣️ *"帮我搜索马斯克最新推文"*
  🗣️ *"看看今天推特上关于 Solana 的最新消息"*
* **触发深度分析模式（启用 Reasoning 推理链）**：
  🗣️ *"深度分析一下推特上关于比特币突破 10 万大关的市场情绪和看涨逻辑"*

---

## 🛠️ 故障排查

| 错误表现 | 排查方向 | 解决方案 |
|----------|----------|----------|
| `Request timeout` | WARP 未启动或代理端口错误 | `sudo systemctl status warp-svc`，检查 `40000` 端口 |
| `401 Unauthorized` | API Key 错误或未加载 | 运行 `openclaw gateway restart` 重载环境 |
| `JSONDecodeError` | LLM 输出了冗余文本 | 确保使用最新的 `search_twitter.py` 原生拦截版代码 |