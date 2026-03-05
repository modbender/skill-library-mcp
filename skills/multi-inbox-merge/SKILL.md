---
name: multi-inbox-merge
description: 多平台私信合并助手：将邮箱、WhatsApp、Telegram、钉钉、企微、飞书、短信等消息统一为会话线程，自动去重、紧急度评分并生成跟进队列。用户提到“合并私信/统一收件箱/客户消息汇总/待跟进清单/读取钉钉消息”时使用。
---

# 多平台私信合并助手

把分散在不同平台的消息，合并成一个可执行的跟进队列。

## 能力

- 导入多个渠道的消息导出文件（CSV/JSON）
- 标准化字段（联系人、时间、内容、来源）
- 按联系人合并会话线程
- 消息去重（避免重复跟进）
- 紧急度评分并输出“优先跟进列表”

## 输入格式（建议）

支持 CSV 与 JSON。钉钉消息可直接导入 JSON（如 `messages`/`data` 列表），脚本会自动识别常见字段（`conversation_id`、`sender_name`、`msg_time`、`msg_content` 等）。

每条消息建议包含以下字段：

- `source`：来源渠道（email / whatsapp / telegram / wecom / lark / sms ...）
- `contact_key`：联系人主键（邮箱或手机号，建议唯一）
- `sender`：发送方
- `timestamp`：时间（建议 ISO8601）
- `text`：消息内容
- `thread_id`：会话ID（可选）
- `direction`：inbound / outbound（可选，建议提供）

## 运行命令

先拉钉钉 API（可选）：

```bash
python3 skills/multi-inbox-merge/scripts/fetch_dingtalk_messages.py \
  --out data/inbox/dingtalk.json
```

再统一合并：

```bash
python3 skills/multi-inbox-merge/scripts/merge_inbox.py \
  --inputs data/inbox/*.csv data/inbox/dingtalk.json \
  --out reports/inbox-merge-$(date +%F)
```

## 输出结果

- `merged_messages.csv`：标准化并去重后的消息
- `threads_summary.csv`：按联系人汇总的线程信息
- `followup_queue.csv`：按紧急度排序的跟进列表
- `summary.md`：汇总统计与Top紧急线程

## 前置凭据检查（钉钉）

当用户要求“读取钉钉消息”时，先检查以下环境变量：

- `DINGTALK_CLIENT_ID`
- `DINGTALK_CLIENT_SECRET`
- `DINGTALK_MESSAGES_API_URL`

若任意缺失：必须先停止执行并返回可复制配置命令，不继续后续步骤。

建议提示文案：

```bash
export DINGTALK_CLIENT_ID='你的appKey'
export DINGTALK_CLIENT_SECRET='你的appSecret'
export DINGTALK_MESSAGES_API_URL='你的消息查询接口URL'
```

然后提示用户回复：`已设置`。

## 建议工作流

1. 确认要合并的平台范围。
2. 若涉及钉钉，先完成“前置凭据检查”。
3. 提供各平台导出文件（或由已接入工具拉取）。
4. 执行合并脚本。
5. 返回 Top10 优先跟进对象 + 建议动作。

## 安全与边界

- 未经明确同意，不自动外发消息。
- 日志中避免输出密钥、令牌等敏感信息。
- 原始导出文件只读保留，不覆盖。

## 参考

- 字段与评分细则：`references/schema.md`
- 钉钉 API 对接：`references/dingtalk-api.md`
