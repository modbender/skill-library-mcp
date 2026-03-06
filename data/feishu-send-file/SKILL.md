---
name: feishu-send-file
description: 飞书发送文件技能。当需要通过飞书向用户发送文件附件（HTML、ZIP、PDF、代码文件等非图片/视频的普通文件）时使用。图片和视频用 message tool 的 media 参数即可，普通文件必须用本技能的两步流程：先上传获取 file_key，再发送消息。
---

# 飞书发送文件

飞书机器人发送普通文件（非图片/视频）需要两步：先上传文件获取 file_key，再用 file_key 发消息。

## 快速流程

### 方式一：用脚本（推荐）

```bash
python3 scripts/send_file.py <file_path> <open_id> <app_id> <app_secret> [file_name]
```

app_id 和 app_secret 从 `openclaw.json` 的 `channels.feishu` 字段读取。
open_id 从 inbound_meta 的 chat_id 字段获取（格式为 `user:ou_xxx`，取 `ou_xxx` 部分）。

示例：
```bash
python3 /root/.openclaw/workspace/skills/feishu-send-file/scripts/send_file.py \
  /root/myfiles/report.html \
  ou_22f2eefd5abe63e0cd67f4882cec06d4 \
  cli_xxxxxxxx \
  your_app_secret
```

### 方式二：手动两步

**Step 1 - 上传文件：**
```bash
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"<APP_ID>","app_secret":"<APP_SECRET>"}' | python3 -c "import json,sys; print(json.load(sys.stdin)['tenant_access_token'])")

FILE_KEY=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_type=stream" \
  -F "file_name=<文件名>" \
  -F "file=@<文件路径>" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['file_key'])")
```

**Step 2 - 发送消息：**
```bash
curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"receive_id\":\"<OPEN_ID>\",\"msg_type\":\"file\",\"content\":\"{\\\"file_key\\\":\\\"$FILE_KEY\\\"}\"}"
```

## 注意事项

- **图片/视频**：直接用 `message` tool 的 `media` 参数，不需要本技能
- **普通文件**：必须走本技能的两步流程，直接用 `filePath` 参数只会显示路径
- `receive_id_type=open_id` 对应个人用户；群聊用 `chat_id` 并替换类型
- 飞书 file_type 用 `stream` 适用于所有普通文件类型
