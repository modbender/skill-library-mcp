# 钉钉 API 直连（消息拉取）

## 目标
先通过钉钉开放平台拿 `accessToken`，再调用你企业可用的消息查询接口，把结果转成 `multi-inbox-merge` 可读 JSON。

## 环境变量（推荐）

- `DINGTALK_CLIENT_ID`
- `DINGTALK_CLIENT_SECRET`
- `DINGTALK_MESSAGES_API_URL`（你企业应用可访问的消息接口 URL）

## 拉取命令

```bash
python3 skills/multi-inbox-merge/scripts/fetch_dingtalk_messages.py \
  --out data/inbox/dingtalk.json
```

如需指定会话：

```bash
python3 skills/multi-inbox-merge/scripts/fetch_dingtalk_messages.py \
  --conversation-id cidxxxx \
  --out data/inbox/dingtalk.json
```

## 合并命令

```bash
python3 skills/multi-inbox-merge/scripts/merge_inbox.py \
  --inputs data/inbox/*.csv data/inbox/dingtalk.json \
  --out reports/inbox-merge-$(date +%F)
```

## 说明

- 不同企业可用的“消息查询接口”可能不同，本脚本支持通过 `--messages-url` 注入。
- 只要接口返回 `messages/data/items/result` 任一数组结构，即可自动识别。
