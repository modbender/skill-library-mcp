# 统一消息结构（Schema）

## 必填字段

- `source`
- `contact_key`
- `sender`
- `timestamp`
- `text`

## 可选字段

- `thread_id`
- `message_id`
- `direction`（inbound / outbound）
- `channel_priority`（渠道优先级，数值）

## 钉钉字段映射（内置支持）

如导入钉钉 JSON，脚本可自动识别：

- 会话ID：`conversation_id` / `chat_id`
- 发送人：`sender_name` / `sender_nick`
- 时间：`msg_time` / `send_time`（支持毫秒时间戳）
- 内容：`msg_content`

## 联系人主键规范

优先级建议：

1. 邮箱（统一小写）
2. 手机号（尽量 E.164）
3. 平台 user id

## 紧急度默认评分规则

- +3：消息包含紧急词（如 urgent/asap/紧急/尽快/今天）
- +2：最新消息为 inbound 且超过 24 小时未回复
- +1：48 小时内 inbound 消息 ≥ 3 条

## 建议动作映射

- 分数 >= 3：优先跟进（建议立即回复并确认下一步）
- 分数 < 3：常规跟进
