---
name: kim-channel
displayName: Kim 消息号 - 快手 IM 配置助手
description: "Kim 消息号配置助手 - 快手（Kuaishou/Kwai）IM 消息渠道集成工具。帮助用户安装和配置 Kim Channel 插件，实现通过 Kim（快手 IM）与 OpenClaw 进行消息交互。支持自动安装插件、交互式配置指引、以及可选的自动配置服务。"
tags: ["kim", "kim 消息号", "快手", "kuaishou", "kwai", "消息号", "im", "即时通讯", "消息渠道", "openclaw"]
metadata:
  {
    "openclaw":
      {
        "emoji": "💬",
        "requires": { "bins": ["openclaw"] },
        "platforms": ["internal"],
        "triggers": ["配置 Kim", "接入 Kim", "Kim 消息号", "kim channel", "安装 kim 插件", "快手消息号", "kwai 消息号"],
      },
  }
---

# Kim Channel 配置助手

> 📝 **文档作者**: yuanyoucai（袁有财）  
> 📚 **完整图文版**: https://docs.corp.kuaishou.com/d/home/fcAA_W4zGstwslCQxlwehh1d2

## 概述

本 skill 帮助你配置 OpenClaw 的 Kim 消息渠道插件，让你能通过 Kim（快手 IM）与 OpenClaw 进行消息交互。

**核心能力：**
1. 🔧 **自动安装** - 一键安装 Kim Channel 插件
2. 📖 **交互指引** - 分步骤引导配置
3. ⚡ **自动配置** - 如用户提供凭证，可直接完成配置

---

## 🚀 快速开始

### 方式 1：运行交互式脚本（推荐）

```bash
cd ~/.openclaw/workspace/skills/kim-msg-account
./scripts/interactive-setup.sh
```

脚本会：
- ✅ 自动检查并安装插件
- ✅ 交互式询问配置方式
- ✅ 可选自动配置或手动指引

### 方式 2：对话式配置

直接告诉我要配置 Kim，我会一步步引导你！

---

## 🎯 交互流程

### 阶段 1：用户表达配置意愿

**触发词：** "配置 Kim"、"接入 Kim"、"Kim 消息号"、"kim channel"等

**响应：**
```
好的！我来帮你配置 Kim 消息渠道 💬

在开始之前，请问你：
1️⃣ 是否已经在 Kim 开放平台创建了应用？
2️⃣ 是否需要我从零开始指导你？

回复"从零开始"或"已有应用"，我来安排下一步～
```

---

### 阶段 2A：用户选择"从零开始"

**步骤 1：创建应用**
```
📱 第一步：创建 Kim 应用

1. 访问 https://kim.kuaishou.com/
2. 点击"应用管理" → "创建应用"
3. 填写应用名称（如：OpenClaw）

完成后告诉我"创建好了"～
```

**等待用户确认** → 发送步骤 2：
```
⚙️ 第二步：配置事件回调

1. 进入"事件和回调"配置页
2. 请求地址填写：`https://你的域名/kim`
3. Verification Token 点击刷新并记录下来
4. 添加两个事件：
   - ✅ 消息号收到消息
   - ✅ 群内的应用机器人收到消息

完成后告诉我"配置好了"～
```

**等待用户确认** → 发送步骤 3：
```
🔑 第三步：获取 appKey 和 secretKey

1. 访问 OpenApi 服务平台
2. 找到你的应用 → 查看密钥
3. 复制 appKey 和 secretKey（预发/正式环境）

拿到后告诉我～
```

**等待用户确认** → 发送步骤 4：
```
📝 第四步：申请接口权限

1. 在 OpenApi 平台点击"接入管理"
2. 创建申请 → 服务名称选择"KIM 开放能力"
3. 勾选接口：**发送 im 消息** `/openapi/v2/message/send`
4. 填写申请原因并提交

审批通过后告诉我"申请好了"～
```

---

### 阶段 2B：用户选择"已有应用"

**响应：**
```
太好了！那我们直接进入配置环节 🔧

请提供以下信息（如果有的话）：
- appKey
- secretKey
- verificationToken
- webhookPath（默认 /kim）

💡 如果你愿意提供这些信息，我可以直接帮你配置到 OpenClaw 中
💡 如果不想提供，我也会一步步指导你自己配置

你希望：
1️⃣ 我帮你自动配置（需要提供凭证）
2️⃣ 你按照指引自己配置
```

---

### 阶段 3A：用户选择"自动配置"并提供凭证

**用户提供信息后，执行：**

```bash
# 1. 先检查插件是否安装
openclaw plugins list | grep kim

# 2. 如果未安装，先安装
openclaw plugins install @ks-openclaw/kim

# 3. 配置凭证
openclaw config set channels.kim.appKey "<用户提供的 appKey>"
openclaw config set channels.kim.secretKey "<用户提供的 secretKey>"
openclaw config set channels.kim.verificationToken "<用户提供的 verificationToken>"
openclaw config set channels.kim.webhookPath "${webhookPath:-/kim}"

# 4. 重启网关
openclaw gateway restart
```

**配置完成后发送：**
```
✅ 配置完成！

已配置项：
- appKey: <appKey 前 8 位>...
- secretKey: 已配置
- verificationToken: 已配置
- webhookPath: <webhookPath>

网关已重启，现在可以测试了！

在 Kim 中搜索你的消息号，发送"你好"试试～
```

---

### 阶段 3B：用户选择"自己配置"

**发送配置命令指引：**
```
好的！按照下面的步骤配置 🔧

### 第 1 步：检查插件是否安装
```bash
openclaw plugins list | grep kim
```

如果没安装，先运行：
```bash
export npm_config_registry="https://npm.corp.kuaishou.com"
openclaw plugins install @ks-openclaw/kim
```

### 第 2 步：配置凭证
```bash
openclaw config set channels.kim.appKey "<你的 appKey>"
openclaw config set channels.kim.secretKey "<你的 secretKey>"
openclaw config set channels.kim.verificationToken "<你的 verificationToken>"
openclaw config set channels.kim.webhookPath "/kim"
```

### 第 3 步：重启网关
```bash
openclaw gateway restart
```

完成后告诉我，我帮你验证配置！
```

---

### 阶段 4：验证配置

**用户说"配置好了"后，执行：**
```bash
# 检查配置
openclaw config get channels.kim.appKey
openclaw config get channels.kim.secretKey
openclaw config get channels.kim.verificationToken
openclaw config get channels.kim.webhookPath

# 检查网关状态
openclaw gateway status
```

**验证通过后发送：**
```
✅ 验证通过！配置正确～

🎉 现在试试给 Kim 发消息吧！

在 Kim 中搜索你的消息号，发送"你好"或"测试"～
```

---

## 🔧 故障排查

### 问题 1：收不到消息

**检查项：**
```bash
# 1. 检查插件
openclaw plugins list | grep kim

# 2. 检查配置
openclaw config get channels.kim

# 3. 检查 webhook 可达性
curl -v https://你的域名/kim

# 4. 查看网关日志
openclaw logs
```

**常见原因：**
- ⚠️ Kim Server 从 IDC 发出，办公网设备需要配置 AccessProxy
- ⚠️ webhook 路径配置错误
- ⚠️ verificationToken 不匹配

### 问题 2：无法发送消息

**检查项：**
```bash
# 检查接口权限
# 确认已在 OpenApi 平台申请 /openapi/v2/message/send 权限

# 检查 appKey/secretKey
openclaw config get channels.kim.appKey
openclaw config get channels.kim.secretKey
```

---

## 🛠️ 执行命令参考

### 安装插件
```bash
export npm_config_registry="https://npm.corp.kuaishou.com"
openclaw plugins install @ks-openclaw/kim
```

### 配置凭证
```bash
openclaw config set channels.kim.appKey "<appKey>"
openclaw config set channels.kim.secretKey "<secretKey>"
openclaw config set channels.kim.verificationToken "<verificationToken>"
openclaw config set channels.kim.webhookPath "/kim"
# 或者使用完整 URL
openclaw config set channels.kim.webhookUrl "https://你的域名/kim"
```

### 验证配置
```bash
# 检查插件
openclaw plugins list | grep kim

# 检查配置
openclaw config get channels.kim

# 检查网关状态
openclaw gateway status
```

### 重启网关
```bash
openclaw gateway restart
```

### 查看日志
```bash
openclaw logs
```

---

## 🛠️ 辅助脚本

### 交互式配置
```bash
./scripts/setup.sh
```

### 诊断配置状态
```bash
./scripts/diagnose.sh
```

---

