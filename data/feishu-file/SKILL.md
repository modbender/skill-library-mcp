---
name: feishu-file
description: 飞书文件发送技能。支持发送各类文件到飞书聊天，包括文档、图片、压缩包等，自动识别文件类型并处理上传。
metadata: {
  "openclaw": {
    "requires": {
      "bins": ["curl", "jq", "file"],
      "env": ["FEISHU_APP_ID", "FEISHU_APP_SECRET"]
    }
  }
}
---

# 飞书文件发送技能

将本地文件发送到飞书聊天，支持多种文件类型，自动识别并正确处理。

## 功能特性

- ✅ 支持多种文件类型（文档、图片、压缩包等）
- ✅ 自动识别文件 MIME 类型
- ✅ 文件大小检查
- ✅ 上传到飞书服务器
- ✅ 发送文件消息
- ✅ 错误处理和重试

## 前置要求

### 环境变量

```bash
# 飞书配置
export FEISHU_APP_ID="cli_xxx"              # 飞书应用 ID
export FEISHU_APP_SECRET="your_secret"      # 飞书应用密钥
export FEISHU_RECEIVER="ou_xxx"             # 接收者 Open ID（可选，默认从上下文获取）
```

### 必需工具

- `curl` - HTTP 请求
- `jq` - JSON 处理
- `file` - 文件类型识别

## 使用方法

### 基本用法

```bash
# 发送文件
bash scripts/send_file.sh /path/to/file.pdf

# 发送文件到指定接收者
bash scripts/send_file.sh /path/to/file.pdf ou_xxxxx
```

### 支持的文件类型

| 类型 | 扩展名 | file_type | 最大大小 |
|------|--------|-----------|----------|
| PDF | .pdf | pdf | 30 MB |
| Word | .doc, .docx | doc, docx | 30 MB |
| Excel | .xls, .xlsx | xls, xlsx | 30 MB |
| PowerPoint | .ppt, .pptx | ppt, pptx | 30 MB |
| 图片 | .jpg, .jpeg, .png, .gif, .bmp, .webp | image | 20 MB |
| 音频 | .mp3, .wav, .aac, .ogg, .m4a, .amr, .flac, .wma | audio | 30 MB |
| 视频 | .mp4, .mov, .avi, .mkv, .flv, .wmv, .webm, .m4v | video | 50 MB |
| 压缩包 | .zip, .rar, .7z, .tar, .gz | stream | 30 MB |
| 文本 | .txt, .md, .json, .xml, .csv | stream | 30 MB |
| 其他 | 其他文件类型 | stream | 30 MB |

> **注意**: opus 格式是飞书音频消息专用格式，不作为文件附件处理。如需发送语音消息，请使用 `feishu-voice` 技能。

## 脚本说明

### send_file.sh

主脚本，完整的文件发送流程。

**用法：**
```bash
bash scripts/send_file.sh <文件路径> [接收者ID]
```

**参数：**
- `文件路径` (必需): 要发送的文件路径
- `接收者ID` (可选): 接收者 Open ID（默认使用环境变量 FEISHU_RECEIVER）

**环境变量：**
- `FEISHU_APP_ID`: 飞书应用 ID
- `FEISHU_APP_SECRET`: 飞书应用密钥
- `FEISHU_RECEIVER`: 接收者 Open ID（可选）

### 流程说明

1. **获取 Access Token**: 使用 App ID 和 Secret 获取访问令牌
2. **识别文件类型**: 根据文件扩展名或 MIME 类型确定 file_type
3. **检查文件大小**: 确保不超过飞书限制
4. **上传文件**: 上传到飞书服务器，获取 file_key
5. **发送消息**: 发送文件消息到指定接收者

## 技术细节

### 文件大小限制

| 文件类型 | 大小限制 |
|---------|---------|
| 图片 | 20 MB |
| 音频 | 30 MB |
| 视频 | 50 MB |
| 其他文件（PDF、Office、压缩包等） | 30 MB |

### file_type 参数

上传文件时需要指定 `file_type` 参数：

- `image`: 图片文件
- `audio`: 音频文件
- `video`: 视频文件
- `pdf`: PDF 文件
- `doc`, `docx`: Word 文档
- `xls`, `xlsx`: Excel 文档
- `ppt`, `pptx`: PowerPoint 文档
- `stream`: 其他文件（压缩包、文本等）

### API 端点

| 端点 | 用途 |
|------|------|
| `/auth/v3/tenant_access_token/internal` | 获取访问令牌 |
| `/im/v1/files` | 上传文件 |
| `/im/v1/messages` | 发送消息 |

### 消息格式

发送文件消息的 JSON 格式：

```json
{
  "msg_type": "file",
  "content": "{\"file_key\": \"file_v2_xxx\"}"
}
```

## 故障排查

### 文件上传失败

**问题**: 文件上传返回错误

**可能原因**:
1. 文件大小超限
2. 文件类型不支持
3. 网络问题

**解决**:
```bash
# 检查文件大小
ls -lh /path/to/file

# 检查文件类型
file /path/to/file
```

### 权限错误

**问题**: 上传时返回权限错误

**解决**: 确保飞书应用有以下权限：
- `im:message`
- `im:message:send_as_bot`
- `im:file`

### 接收者不存在

**问题**: 发送消息时返回接收者不存在

**解决**: 确认接收者 ID 正确：
- Open ID: `ou_xxx`
- Chat ID: `oc_xxx`

## 完整示例

```bash
# 设置环境变量
export FEISHU_APP_ID="your_app_id_here"
export FEISHU_APP_SECRET="your_app_secret_here"
export FEISHU_RECEIVER="ou_xxxxx"

# 发送 PDF 文件
bash /root/.openclaw/workspace/skills/feishu-file/scripts/send_file.sh \
  /path/to/document.pdf

# 发送到指定接收者
bash /root/.openclaw/workspace/skills/feishu-file/scripts/send_file.sh \
  /path/to/report.xlsx ou_yyyyy
```

## 注意事项

1. **文件路径**: 支持绝对路径和相对路径
2. **文件名**: 建议使用英文文件名，避免特殊字符
3. **大小限制**: 超过限制的文件会返回错误
4. **网络问题**: 上传大文件时可能需要较长时间
5. **文件清理**: 本地文件不会自动删除

## 相关技能

- `feishu-voice`: 发送语音消息
- `feishu-doc`: 飞书文档操作
- `feishu-drive`: 飞书云盘操作
