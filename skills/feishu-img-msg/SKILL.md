---
name: feishu-img-msg
description: |
  飞书图片消息操作技能，当触发飞书发送图片时自动调用本技能。
  支持上传图片、发送图片消息、获取图片内容。
  Activate when user mentions: 飞书发图、发送图片、上传图片、获取图片、下载图片、image_key。
---

# 飞书图片消息操作技能

本技能提供飞书图片消息的完整操作能力，包括上传、发送、获取图片。

## 功能

| 功能 | 命令 | 说明 |
|------|------|------|
| 上传图片 | `feishu-img-msg upload` | 上传本地图片到飞书，返回 image_key |
| 发送图片 | `feishu-img-msg send` | 发送图片到指定会话（支持文件路径或 image_key） |
| 获取图片 | `feishu-img-msg get` | 下载飞书图片到本地 |
| 查看图片 | `feishu-img-msg view` | 获取图片信息（返回 base64 供 AI 查看） |

## 快速使用

### 1. 发送本地图片到会话

```bash
# 直接发送本地图片文件
python3 ~/.openclaw/workspace/skills/feishu-img-msg/scripts/feishu_image.py \
  send \
  --chat-id "oc_xxxxx" \
  --file "/path/to/image.jpg"
```

### 2. 上传图片获取 image_key

```bash
# 上传图片，返回 image_key
python3 ~/.openclaw/workspace/skills/feishu-img-msg/scripts/feishu_image.py \
  upload \
  --file "/path/to/image.png"
```

### 3. 用 image_key 发送图片

```bash
# 使用已有的 image_key 发送
python3 ~/.openclaw/workspace/skills/feishu-img-msg/scripts/feishu_image.py \
  send \
  --chat-id "ou_xxxxx" \
  --image-key "img_xxxxx"
```

### 4. 下载图片

```bash
# 下载飞书图片到本地
python3 ~/.openclaw/workspace/skills/feishu-img-msg/scripts/feishu_image.py \
  get \
  --image-key "img_xxxxx" \
  --output "/path/to/save.jpg"
```

### 5. 查看图片内容（AI 可读）

```bash
# 获取图片 base64，用于 AI 分析
python3 ~/.openclaw/workspace/skills/feishu-img-msg/scripts/feishu_image.py \
  view \
  --image-key "img_xxxxx"
```

## 参数说明

### send 命令

| 参数 | 必填 | 说明 |
|------|------|------|
| `--chat-id` | ✅ | 接收者 ID（群聊 oc_ 开头，用户 ou_ 开头） |
| `--file` | 二选一 | 本地图片文件路径 |
| `--image-key` | 二选一 | 已上传的 image_key |
| `--chat-type` | 否 | 会话类型：`group`(默认) 或 `user` |
| `--account` | 否 | 飞书账户名（默认 main） |

### upload 命令

| 参数 | 必填 | 说明 |
|------|------|------|
| `--file` | ✅ | 本地图片文件路径 |
| `--account` | 否 | 飞书账户名（默认 main） |

### get 命令

| 参数 | 必填 | 说明 |
|------|------|------|
| `--image-key` | ✅ | 图片的 image_key |
| `--output` | ✅ | 保存路径 |
| `--account` | 否 | 飞书账户名（默认 main） |

### view 命令

| 参数 | 必填 | 说明 |
|------|------|------|
| `--image-key` | ✅ | 图片的 image_key |
| `--account` | 否 | 飞书账户名（默认 main） |

## 支持的图片格式

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- WebP (.webp)

文件大小限制：单张图片最大 30MB

## 权限要求

| Scope | 用途 |
|-------|------|
| `im:resource` | 上传图片、获取图片 |
| `im:message` | 发送消息 |
| `im:message:send_as_bot` | 以机器人身份发送 |

## 常见问题

### 图片发送失败

1. **检查 chat-id 类型**
   - 群聊 ID 以 `oc_` 开头，chat_type 设为 `group`
   - 用户 ID 以 `ou_` 开头，chat_type 设为 `user`

2. **检查图片格式**
   - 支持常见图片格式
   - 确保文件未损坏

3. **检查权限**
   - 机器人需要已加入目标群聊
   - 机器人需要与用户有单聊会话

### token 过期

脚本会自动刷新 tenant_access_token，如仍报错：
- 错误码 `99991400` - token 过期，稍后重试
- 错误码 `99991401` - token 无效，检查 app 配置

## 参考文档

- 飞书上传图片 API: https://open.feishu.cn/document/server-docs/im-v1/image/create
- 飞书获取图片 API: https://open.feishu.cn/document/server-docs/im-v1/image/get
- 飞书发送消息 API: https://open.feishu.cn/document/server-docs/im-v1/message/create
