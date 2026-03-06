---
name: feishu-mention-bot
description: 飞书群聊中 @机器人并发送消息。当用户需要在飞书群里艾特机器人、通知其他机器人、或让机器人之间互相通信时使用。
---

# 飞书 @机器人 技能

在飞书群聊中 @其他机器人并发送消息，让被艾特的机器人收到通知并响应。

## 前提条件

确保飞书应用有以下权限：
- `im:message` 或 `im:message:send_as_bot` — 发送消息
- `im:message.group_at_msg:readonly` — 接收 @消息

## 核心：@机器人格式

### 文本消息
```
<at user_id="open_id">名字</at> 你的消息内容
```

### 富文本消息（post）
在 markdown 内容中使用：
```
<at user_id="open_id">名字</at>
```

### 卡片消息（interactive）
在 lark_md 内容中使用：
```
<at id=open_id></at>
```

## 如何获取机器人的 open_id

**方法：从消息历史提取**

```bash
# 1. 获取 tenant_access_token
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"YOUR_APP_ID","app_secret":"YOUR_APP_SECRET"}' | jq -r '.tenant_access_token')

# 2. 获取群消息历史，提取 mentions
curl -s "https://open.feishu.cn/open-apis/im/v1/messages?container_id_type=chat&container_id=CHAT_ID&page_size=50" \
  -H "Authorization: Bearer $TOKEN" | \
  jq '[.data.items[]? | select(.mentions != null and .mentions != []) | .mentions[]?] | unique_by(.id)'
```

**关键点：**
- 飞书的群成员 API 不返回机器人信息
- 必须从消息历史的 `mentions` 字段提取
- 机器人在群里被艾特过的消息才会有 mentions

## 使用示例

### 使用 message 工具

```
message action=send channel=feishu target=chat:CHAT_ID message="<at user_id=\"ou_xxx\">机器人名</at> 你好！"
```

### 使用飞书 API 直接调用

```bash
curl -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "receive_id": "CHAT_ID",
    "msg_type": "text",
    "content": "{\"text\":\"<at user_id=\\\"ou_xxx\\\">机器人名</at> 你好！\"}"
  }'
```

## 注意事项

1. **必须使用 open_id**：不能用 app_id，必须是 `ou_` 开头的 open_id
2. **机器人必须在群里**：被艾特的机器人必须是群成员
3. **机器人需要订阅事件**：被艾特的机器人需要订阅 `im.message.group_at_msg` 事件才能收到通知
4. **缓存机器人 open_id**：获取后建议保存到 TOOLS.md 或数据库，避免重复查询

## 当前群机器人列表

> 从 TOOLS.md 或消息历史中查找具体的 open_id

示例：
| 名称 | open_id |
|-----|---------|
| OpenClaw唐 | ou_xxx |
| Lynn | ou_xxx |
