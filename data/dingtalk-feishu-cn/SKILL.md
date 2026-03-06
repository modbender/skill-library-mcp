---
name: dingtalk-feishu-cn
description: 钉钉/飞书集成 - 企业通讯、机器人、自动化工作流（Slack 中国版）
metadata:
  openclaw:
    emoji: "💼"
    category: "productivity"
    tags: ["dingtalk", "feishu", "lark", "china", "enterprise", "slack"]
---

# 钉钉/飞书集成

企业通讯、机器人、自动化工作流。

## 功能

- 💬 消息发送/接收
- 🤖 机器人集成
- 📅 日程管理
- 📋 审批流程
- 🔄 自动化工作流

## 平台对比

| 功能 | 钉钉 | 飞书/Lark |
|------|------|-----------|
| Webhook | ✅ | ✅ |
| API | ✅ | ✅ |
| 机器人 | ✅ | ✅ |
| 文档 | ✅ | ✅✅ |
| 国际化 | ❌ | ✅ |

## 钉钉集成

### Webhook 机器人

```bash
# 发送消息
curl -X POST "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "msgtype": "text",
    "text": {"content": "这是一条测试消息"}
  }'
```

### API 调用

```python
# 使用 dingtalk-sdk
pip install dingtalk-sdk

from dingtalk import SecretClient
client = SecretClient(APP_KEY, APP_SECRET)
```

## 飞书/Lark 集成

### Webhook 机器人

```bash
# 发送消息
curl -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_HOOK" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "text",
    "content": {"text": "这是一条测试消息"}
  }'
```

### API 调用

```python
# 使用 lark-oapi
pip install lark-oapi

import lark_oapi as lark
client = lark.Client.builder() \
    .app_id(APP_ID) \
    .app_secret(APP_SECRET) \
    .build()
```

## 使用场景

### 1. 告警通知

- 服务器告警
- 业务异常
- 定时报告

### 2. 自动化

- CI/CD 通知
- 任务完成提醒
- 审批流程

### 3. 机器人

- 问答机器人
- 查询工具
- 工作助手

## 快速开始

```bash
# 钉钉机器人
./scripts/dingtalk-notify.sh "告警: CPU 使用率 90%"

# 飞书机器人
./scripts/feishu-notify.sh "任务完成: 数据同步成功"
```

## 注意事项

1. **安全**: Webhook 地址不要泄露
2. **频率**: 避免消息轰炸
3. **格式**: 使用 Markdown/card 提升体验

---

*版本: 1.0.0*
