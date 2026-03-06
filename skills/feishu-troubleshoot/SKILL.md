---
name: 飞书连接问题解决方案
description: 解决 OpenClaw 连接飞书时的常见问题。
---

# 飞书连接问题解决方案

解决 OpenClaw 连接飞书时的常见问题。

## 问题一：机器人不回复

导入以下权限：

```json
{
  "scopes": {
    "tenant": [
      "application:bot.menu:write",
      "contact:user.employee_id:readonly",
      "im:chat.access_event.bot_p2p_chat:read",
      "im:chat.members:bot_access",
      "im:message",
      "im:message.group_at_msg:readonly",
      "im:message.p2p_msg:readonly",
      "im:message:readonly",
      "im:message:send_as_bot",
      "im:message.reactions:read",
      "im:resource"
    ],
    "user": [
      "im:chat.access_event.bot_p2p_chat:read"
    ]
  }
}
```

## 问题二：应用平台检查

### 1. 启用机器人能力
路径：飞书开放平台 → 你的应用 → **应用能力** → **机器人**
- 开启「机器人能力」
- 配置机器人名称

### 2. 配置事件订阅（长连接）
⚠️ **必须在 OpenClaw 网关启动后再配置**

路径：飞书开放平台 → 你的应用 → **事件与回调**
- **订阅方式**：「**使用长连接接收事件**」
- **添加事件**：`im.message.receive_v1`

### 3. 配置权限
路径：飞书开放平台 → 你的应用 → **权限管理**
- 点击「**批量导入**」
- 粘贴 JSON 权限
- 保存

### 4. 发布应用
路径：飞书开放平台 → 你的应用 → **版本管理与发布**
- 创建版本 → 提交发布

## 问题三：日历权限开放

导入以下权限：

```json
{
  "scopes": {
    "tenant": [
      "calendar:calendar",
      "calendar:calendar:readonly",
      "task:task:write",
      "task:task:read",
      "contact:user.employee_id:readonly"
    ],
    "user": [
      "calendar:calendar",
      "calendar:calendar:readonly",
      "task:task:write",
      "task:task:read"
    ]
  }
}
```

## 参考

- 飞书开放平台：https://open.feishu.cn/app
- OpenClaw 文档：https://docs.openclaw.ai
