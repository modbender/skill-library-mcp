---
name: kim-msg
description: "快手 Kim即时通讯消息发送。支持两种方式：(1) Webhook - 向 Kim 机器人所在的群聊发送消息；(2) 消息号 -
  使用 appKey/secretKey 直接向快手 Kim 用户发送消息。适用于向 Kim 推送通知、告警、日报等场景。官网:
  https://kim.kuaishou.com/"
---


# Kim 消息发送（快手 IM）

## 概述

Kim 是快手的企业即时通讯工具，支持两种发送消息的方式：

1. **Webhook 方式** - 需要 Kim 机器人 Token，向机器人所在的群聊发送消息
2. **消息号方式** - 需要 appKey + secretKey，可以直接发送给指定用户（快手邮箱前缀）

官方网站：https://kim.kuaishou.com/

## 首次配置

首次使用前，需要选择一种方式并配置相应的凭证：

### Webhook 方式
需要从 Kim 机器人获取 Webhook Token，告诉晴晴帮你配置。

### 消息号方式
需要提供：
- **appKey**: Kim 应用 Key
- **secretKey**: Kim 应用 Secret
- **用户名**: 要发送消息的目标用户（必须是快手邮箱前缀，如 `wangyang`，不是完整邮箱 `wangyang@kuaishou.com`）

## 使用方法

### 方式一：Webhook 发送

```bash
# 发送 Markdown 消息到群聊
kim-msg/webhook.sh "**标题**\n\n正文内容"

# 发送纯文本
kim-msg/webhook.sh "Hello World" --text
```

### 方式二：消息号发送

```bash
# 发送消息给指定用户（用户名必须是邮箱前缀，如 wangyang）
kim-msg/message.sh -u <邮箱前缀> -m "消息内容"

# 示例
kim-msg/message.sh -u wangyang -m "**提醒**：今天有会议"
```

> ⚠️ 首次使用如果遇到权限错误，运行：`chmod +x scripts/*.sh`

## API 详情

### Webhook
- **URL:** `https://kim-robot.kwaitalk.com/api/robot/send?key=<key>`
- **Method:** POST
- **Body:**
```json
{
  "msgtype": "markdown",
  "markdown": {"content": "消息内容"}
}
```

### 消息号
- **获取 Token:** `https://is-gateway.corp.kuaishou.com/token/get?appKey=<appKey>&secretKey=<secretKey>`
- **发送消息:** 自动尝试以下两个接口：
  - 单用户: `/openapi/v2/message/send` (`username` 单个用户)
  - 批量: `/openapi/v2/message/batch/send` (`usernames` 数组)
  - **自动重试:** 优先尝试单用户接口，失败则尝试批量接口
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "msgType": "markdown",
  "markdown": {"content": "消息内容"},
  "usernames": ["用户名"]
}
```

## 配置方式

| 凭证 | 环境变量 | 说明 |
|------|----------|------|
| Webhook Token | `KIM_WEBHOOK_TOKEN` | Webhook 方式用 |
| App Key | `KIM_APP_KEY` | 消息号方式用 |
| Secret Key | `KIM_SECRET_KEY` | 消息号方式用 |

## 注意事项

- 不硬编码任何 API Key/Token
- 消息内容需合规
- API 异常时检查凭证和网络

## 源码

GitHub: https://github.com/LeeGoDamn/kim-msg-skill