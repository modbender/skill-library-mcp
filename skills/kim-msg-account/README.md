# Kim Channel Skill for OpenClaw

> OpenClaw - Kim 消息渠道插件配置助手  
> 让你能通过 Kim（快手 IM）与你的 OpenClaw 进行消息交互

**📝 文档作者：** yuanyoucai（袁有财）  
**🔗 原始文档：** OpenClaw - Kim 消息渠道插件.pdf

---

## 📋 目录

1. [快速开始](#-快速开始)
2. [安装插件](#-安装插件)
3. [创建 Kim 应用](#-创建 kim-应用)
4. [配置 OpenClaw](#-配置-openclaw)
5. [重启网关](#-重启网关)
6. [验证配置](#-验证配置)
7. [故障排查](#-故障排查)

---

## 🚀 快速开始

### 使用交互式配置脚本

```bash
cd ~/.openclaw/workspace/skills/kim-msg-account
./scripts/setup.sh
```

脚本会自动引导你完成：
- ✅ 插件安装检查
- ✅ 交互式输入配置信息
- ✅ 自动应用配置
- ✅ 网关重启

### 或使用诊断脚本检查状态

```bash
./scripts/diagnose.sh
```

---

## 📦 安装插件

### 1. 设置 npm 公司内部源

```bash
export npm_config_registry="https://npm.corp.kuaishou.com"
```

### 2. 安装 Kim 插件

```bash
openclaw plugins install @ks-openclaw/kim
```

---

## 🏗️ 创建 Kim 应用

### 步骤 1：创建应用

前往 [Kim 开放平台](https://kim.kuaishou.com/) 创建一个应用。

### 步骤 2：配置事件回调

在应用设置中，配置事件回调（用于接收消息）：

#### 请求地址

格式：`https://{your-domain}.corp.kuaishou.com/{webhook}`

**示例：**
- 你的 OpenClaw 主机 IP：`172.22.1.1`
- 申请的域名：`openclaw.corp.kuaishou.com`
- 默认 webhook 路径：`/kim`
- 完整地址：`https://openclaw.corp.kuaishou.com/kim`

**⚠️ 注意事项：**
- Kim Server 的事件回调从 **IDC 机房** 发出
- 如果 OpenClaw 在**办公网**，可能存在网络隔离
- 参考：[AccessProxy IDC 内请求封禁说明及解决方案](https://wiki.corp.kuaishou.com/pages/viewpage.action?pageId=xxxxx)
- 不建议直接使用 IP 地址作为回调

#### Verification Token

如果没有默认生成，点击**刷新按钮**生成一个新的 token。

#### 添加事件

需要添加以下两个事件：

| 事件名称 | 说明 |
|---------|------|
| ✅ 消息号收到消息 | 当用户和消息号单聊时触发该事件 |
| ✅ 群内的应用机器人收到消息 | 当用户在群聊内@应用机器人时触发该事件 |

---

## 🔑 获取 appKey 和 secretKey

### 步骤 1：前往 OpenApi 服务平台

访问 [OpenApi 服务平台](https://open.kuaishou.com/) 获取凭证。

**⚠️ 安全提示：**
> 根据公司安全政策要求，应用的 appKey 和 secretKey 不得明文暴露在代码或 shell 脚本中。建议你将其配置在 Kconf，并开启加密功能来保障数据安全。

### 步骤 2：申请接口权限

申请 `/openapi/v2/message/send` 接口权限：

| 字段 | 填写内容 |
|------|---------|
| 应用名称 | openclaw |
| 应用负责人 | 你的姓名 |
| 服务名称 | **KIM 开放能力** |
| 申请原因 | 请认真填写申请原因，例如业务背景、业务需求、应用场景等 |
| 选择接口 | **发送 im 消息** `/openapi/v2/message/send` |

---

## ⚙️ 配置 OpenClaw

### 方式一：使用 openclaw config 命令（推荐）

```bash
# 配置 webhook 路径（默认 /kim）
openclaw config set channels.kim.webhookPath "/kim"

# 或者配置完整 webhook URL
openclaw config set channels.kim.webhookUrl "https://openclaw.corp.kuaishou.com/kim"

# 配置验证 token
openclaw config set channels.kim.verificationToken "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# 配置 appKey 和 secretKey
openclaw config set channels.kim.appKey "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
openclaw config set channels.kim.secretKey "openAppxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### 方式二：直接编辑配置文件

编辑 `~/.openclaw/openclaw.json`：

```json
{
  "channels": {
    "kim": {
      "appKey": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "secretKey": "openAppxxxxxxxxxxxxxxxxxxxxxxxxx",
      "webhookPath": "/kim",
      "verificationToken": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }
  }
}
```

---

## 🔄 重启网关

```bash
openclaw gateway restart
```

---

## ✅ 验证配置

### 检查插件状态

```bash
# 查看已安装插件
openclaw plugins list

# 检查配置
openclaw config get channels.kim
```

### 测试消息

通过 Kim 消息号或 @群机器人 给 OpenClaw 发送消息，确认能正常收发。

---

## 🔧 故障排查

### 问题 1：收不到消息

**检查项：**

1. **网络连通性**
   ```bash
   curl -v https://{your-domain}.corp.kuaishou.com/kim
   ```

2. **IDC 网络隔离**
   - 如果 OpenClaw 在办公网，需要配置 AccessProxy

3. **事件回调配置**
   - 确认已添加「消息号收到消息」和「群内的应用机器人收到消息」事件

### 问题 2：无法发送消息

**检查项：**

1. **接口权限**
   - 确认已申请 `/openapi/v2/message/send` 接口权限

2. **appKey/secretKey**
   ```bash
   openclaw config get channels.kim.appKey
   openclaw config get channels.kim.secretKey
   ```

3. **日志排查**
   ```bash
   openclaw logs
   ```

### 问题 3：webhook 验证失败

**检查项：**

1. **verificationToken**
   ```bash
   openclaw config get channels.kim.verificationToken
   ```

2. **webhook 路径**
   - 确认 Kim 开放平台配置的路径与 OpenClaw 配置一致

---

## 📊 快速检查清单

| 检查项 | 命令 |
|--------|------|
| 插件是否安装 | `openclaw plugins list \| grep kim` |
| appKey 配置 | `openclaw config get channels.kim.appKey` |
| secretKey 配置 | `openclaw config get channels.kim.secretKey` |
| verificationToken 配置 | `openclaw config get channels.kim.verificationToken` |
| webhook 路径 | `openclaw config get channels.kim.webhookPath` |
| 网关状态 | `openclaw gateway status` |

---

## 📚 相关链接

- [Kim 开放平台](https://kim.kuaishou.com/)
- [OpenApi 服务平台](https://open.kuaishou.com/)
- [3 分钟快速配置 Kim 应用](https://wiki.corp.kuaishou.com/pages/viewpage.action?pageId=xxxxx)
- [AccessProxy IDC 内请求封禁说明](https://wiki.corp.kuaishou.com/pages/viewpage.action?pageId=xxxxx)

---

