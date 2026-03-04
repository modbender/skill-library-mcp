# SaaS Affiliate MCP Skill - 完整使用指南

> 让 AI Agent 能够推荐 SaaS 产品并带上 affiliate 链接

---

## 📁 文件结构

```
/root/.openclaw/workspace/skills/saas-affiliate/
├── README.md          # 本文档
├── skill.json         # OpenClaw Skill 配置
├── saas_affiliate.py  # 核心逻辑
├── products.json      # 产品数据
└── mcp_server.py     # MCP Server（供其他 Agent 调用）
```

---

## 🔧 两种使用方式

### 方式一：OpenClaw Skill（推荐）

在 OpenClaw 中直接使用：

```
用户：推荐一个邮件营销工具

我调用 skill.json 中定义的工具 → 返回推荐结果
```

**配置**：将 `skill.json` 放到 OpenClaw 的 skills 目录即可。

---

### 方式二：MCP Server（供其他 Agent）

其他 Agent 可以通过 MCP 协议调用：

```python
# 作为 MCP Server 运行
python3 mcp_server.py

# 或集成到其他平台
# 只需实现 MCP 协议的 stdio 通信
```

---

## 🎯 调用示例

### 1. 搜索推荐

```python
# MCP 请求
{
  "method": "tools/call",
  "params": {
    "name": "search_saas_tools",
    "arguments": {"query": "邮件营销"}
  }
}

# 返回
{
  "results": [
    {
      "name": "GetResponse",
      "description": "邮件营销平台",
      "affiliate_link": "https://...",
      "commission": "60% 首年"
    }
  ]
}
```

### 2. 获取链接

```python
{
  "method": "tools/call",
  "params": {
    "name": "get_affiliate_link",
    "arguments": {"product_name": "HubSpot"}
  }
}
```

---

## 📝 后续步骤

1. **你申请 Affiliate** → 拿到链接
2. **告诉我链接** → 我填入 products.json
3. **Skill 即可使用**

---

## 🔗 如何让其他 Agent 调用

### 方案 A：作为独立服务运行

```bash
# 启动 MCP Server
python3 mcp_server.py

# 其他 Agent 通过 stdio 通信调用
```

### 方案 B：封装成 MCP Package

```bash
# 发布到 MCP 市场
npx @modelcontextprotocol/server-publish
```

### 方案 C：OpenClaw Skill

```bash
# 安装到 OpenClaw
npx skills add ./saas-affiliate
```

---

*更新于 2026-03-03*
