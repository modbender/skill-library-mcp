# feishu-file - 飞书文件发送技能

通过飞书 API 发送任意类型文件（PDF、图片、文档等）到指定用户或群聊。

## 快速开始

### 1. 配置环境变量

```bash
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
export FEISHU_RECEIVER="ou_xxx"
```

### 2. 发送文件

```bash
# 基本用法
cd /root/.openclaw/workspace/skills/feishu-file
./scripts/feishu-file-api.sh /path/to/file.pdf

# 指定文件名
./scripts/feishu-file-api.sh /path/to/report.pdf "月度报告.pdf"

# 发送给指定用户
./scripts/feishu-file-api.sh /path/to/file.pdf "文件.pdf" "ou_xxx"
```

## 功能特点

- ✅ **支持所有文件类型**: PDF、图片、Word、Excel、文本等
- ✅ **自动 base64 编码**: 无需手动处理文件编码
- ✅ **灵活的接收者**: 支持发送给个人或群聊
- ✅ **完整的错误处理**: 详细的错误提示和调试信息
- ✅ **两种发送方式**:
  - OpenClaw 框架集成（send-file.sh）
  - 直接飞书 API 调用（feishu-file-api.sh）⭐

## 两种脚本的区别

### send-file.sh
- 用途: 准备文件并生成发送命令
- 特点: 与 OpenClaw 框架集成
- 适用: 在 OpenClaw 会话中使用

### feishu-file-api.sh ⭐ 推荐
- 用途: 直接调用飞书 API 发送文件
- 特点: 独立运行，无需 OpenClaw 框架
- 适用: 脚本自动化、定时任务、独立使用

## 使用示例

### 发送 PDF 报告

```bash
./scripts/feishu-file-api.sh /tmp/monthly_report.pdf "2026年2月月度报告.pdf"
```

### 发送图片

```bash
./scripts/feishu-file-api.sh /tmp/screenshot.png "截图.png"
```

### 发送 Word 文档

```bash
./scripts/feishu-file-api.sh ~/docs/report.docx "项目报告.docx"
```

### 批量发送文件

```bash
#!/bin/bash
FILES=(
  "/tmp/report1.pdf"
  "/tmp/report2.pdf"
  "/tmp/report3.pdf"
)

for file in "${FILES[@]}"; do
  filename=$(basename "$file")
  /root/.openclaw/workspace/skills/feishu-file/scripts/feishu-file-api.sh "$file" "$filename"
  sleep 2  # 避免频率限制
done
```

### 定时发送报告

```bash
# 添加到 crontab
# 每天 9:00 发送日报
0 9 * * * /root/.openclaw/workspace/skills/feishu-file/scripts/feishu-file-api.sh /tmp/daily_report.txt "日报_$(date +\%Y\%m\%d).txt"
```

## 文件大小限制

- **默认限制**: 100MB
- **建议大小**: 单个文件不超过 20MB
- **超大文件**: 使用云存储链接分享

### 自定义文件大小限制

```bash
export FILE_SIZE_LIMIT=52428800  # 50MB
./scripts/feishu-file-api.sh /path/to/file.pdf
```

## 支持的文件类型

| 类型 | 扩展名 | MIME Type |
|------|--------|-----------|
| PDF | .pdf | application/pdf |
| PNG 图片 | .png | image/png |
| JPEG 图片 | .jpg, .jpeg | image/jpeg |
| Word 文档 | .docx | application/vnd.openxmlformats-officedocument.wordprocessingml.document |
| Excel 表格 | .xlsx | application/vnd.openxmlformats-officedocument.spreadsheetml.sheet |
| 文本文件 | .txt | text/plain |

## 错误处理

### 常见错误及解决方案

#### 1. 文件不存在
```bash
❌ [ERROR] 文件不存在: /path/to/file.pdf
✅ 检查文件路径是否正确
```

#### 2. 文件过大
```bash
❌ [ERROR] 文件过大: 150MB (限制: 100MB)
✅ 压缩文件或使用云存储链接
```

#### 3. 权限不足
```bash
❌ [ERROR] 获取访问令牌失败
✅ 检查 FEISHU_APP_ID 和 FEISHU_APP_SECRET 是否正确
```

#### 4. 接收者 ID 错误
```bash
❌ [ERROR] 消息发送失败
✅ 确认接收者 ID 格式（ou_xxx 或 oc_xxx）
```

## API 端点

本技能使用以下飞书 API 端点：

1. **获取访问令牌**
   ```
   POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
   ```

2. **上传文件**
   ```
   POST https://open.feishu.cn/open-apis/im/v1/files
   ```

3. **发送消息**
   ```
   POST https://open.feishu.cn/open-apis/im/v1/messages
   ```

## 技术实现

### 工作流程

```
文件 → 检查 → 上传 → 获取 file_key → 发送消息 → 完成
```

### 关键代码

```bash
# 1. 获取访问令牌
TOKEN_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\": \"$FEISHU_APP_ID\", \"app_secret\": \"$FEISHU_APP_SECRET\"}")

# 2. 上传文件
UPLOAD_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $TENANT_ACCESS_TOKEN" \
  -F "file=@$FILE_PATH" \
  -F "file_type=$(file --mime-type -b "$FILE_PATH")")

# 3. 发送消息
SEND_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages" \
  -H "Authorization: Bearer $TENANT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"receive_id\": \"$RECEIVER\",
    \"msg_type\": \"file\",
    \"content\": \"{\\\"file_key\\\":\\\"$FILE_KEY\\\",\\\"file_name\\\":\\\"$FILE_NAME\\\"}\"
  }")
```

## 相关技能

- **feishu-voice**: 飞书语音消息发送
- **feishu-doc**: 飞书文档操作
- **md2pdf**: Markdown 转 PDF（常配合使用）

## 测试

```bash
# 测试发送文本文件
echo "测试文件内容" > /tmp/test.txt
./scripts/feishu-file-api.sh /tmp/test.txt "测试.txt"

# 测试发送 PDF
./scripts/feishu-file-api.sh /tmp/douyin_analysis_report.pdf
```

## 最佳实践

1. **文件命名**: 使用有意义的文件名，包含日期或版本号
   ```bash
   report_20260223.pdf  ✅
   report.pdf           ❌
   ```

2. **文件大小**: 控制在 20MB 以内，确保传输稳定

3. **错误处理**: 发送失败时记录日志并重试
   ```bash
   for i in {1..3}; do
     ./scripts/feishu-file-api.sh "$file" && break
     sleep 5
   done
   ```

4. **批量发送**: 添加延迟避免频率限制
   ```bash
   sleep 2  # 每次发送间隔 2 秒
   ```

## 许可证

MIT License

---

**维护者**: 小美 ⭐  
**最后更新**: 2026-02-23  
**版本**: v1.0
