# Qiniu KODO 技能

通过 qiniu-mcp MCP 工具 + Node.js SDK 脚本 + qshell 管理七牛云对象存储和数据处理。

---

## 📖 功能说明

### 核心功能
- 📤 **上传文件** - 单文件、批量上传、断点续传
- 📥 **下载文件** - 单文件、批量下载
- 📋 **列出文件** - 按前缀、分页列出
- 🗑️ **删除文件** - 单文件、批量删除
- 🔗 **获取 URL** - 公开/私有空间 URL 生成
- 📊 **文件信息** - 查看文件详情
- 📁 **目录操作** - 移动、复制、重命名

### 高级功能（通过 MCP 工具）
- 🖼️ **图片处理** - 缩放、裁剪、水印、格式转换
- 🎵 **音视频处理** - 转码、截图、切片
- 🔍 **智能搜索** - 文件搜索和元数据查询
- 📝 **文档处理** - 文档预览、格式转换

---

## 🚀 首次使用 — 自动设置

当用户首次要求操作 KODO 时，按以下流程操作：

### 步骤 1：检查当前状态

```bash
{baseDir}/scripts/setup.sh --check-only
```

**检查内容：**
- ✅ Node.js 环境
- ✅ qiniu-mcp 是否已安装
- ✅ qshell 是否已安装
- ✅ 配置文件是否存在
- ✅ 凭证是否已配置

如果输出显示一切 OK（qiniu-mcp 已安装、凭证已配置），跳到「执行策略」。

---

### 步骤 2：如果未配置，引导用户提供凭证

告诉用户：

```
我需要你的七牛云凭证来连接 KODO 存储服务。请提供：

AccessKey — 七牛云 AccessKey
SecretKey — 七牛云 SecretKey  
Region — 存储区域（如 z0=华东, z1=华北, z2=华南, na0=北美, as0=东南亚）
Bucket — 存储桶名称
Domain（可选） — 访问域名（用于生成文件 URL，如 http://cdn.example.com）

你可以在七牛云控制台获取：
- 密钥管理：https://portal.qiniu.com/user/key
- 存储桶列表：https://portal.qiniu.com/kodo/bucket
- 区域说明：
  - z0: 华东（杭州）
  - z1: 华北（河北）
  - z2: 华南（广州）
  - na0: 北美（洛杉矶）
  - as0: 东南亚（新加坡）
```

---

### 步骤 3：用户提供凭证后，运行自动设置

```bash
{baseDir}/scripts/setup.sh \
  --access-key "<AccessKey>" \
  --secret-key "<SecretKey>" \
  --region "<Region>" \
  --bucket "<Bucket>" \
  --domain "<Domain>"
```

**脚本会自动：**

1. ✅ 检查并安装 mcporter（MCP 命令行工具）
2. ✅ 检查并安装 qiniu-mcp-server（七牛云官方 MCP 工具）
3. ✅ 安装 qiniu Node.js SDK
4. ✅ 安装 qshell 命令行工具
5. ✅ 创建/更新 `~/.mcporter/mcporter.json`，写入 qiniu-mcp 服务器配置
6. ✅ 将凭证写入 shell 配置文件（`~/.zshrc` 或 `~/.bashrc`），重启后仍可用
7. ✅ 创建配置文件 `{baseDir}/config/qiniu-config.json`
8. ✅ 验证七牛云连接
9. ✅ 测试上传下载功能

**设置完成后即可开始使用。**

---

## 🎯 执行策略

三种方式按优先级降级，确保操作始终可完成：

### 方式一：qiniu-mcp MCP 工具（优先）

**特点：** 功能最全，支持存储 + 图片处理 + 音视频处理 + 智能搜索

**使用场景：**
- 需要图片处理（缩放、裁剪、水印）
- 需要音视频转码
- 需要智能搜索
- 需要文档处理

**调用方式：**
```javascript
// 通过 MCP 工具调用
use_mcp_tool("qiniu-mcp", "upload_file", {
  localPath: "/path/to/file.txt",
  key: "uploads/file.txt"
})
```

---

### 方式二：Node.js SDK 脚本

**特点：** 稳定可靠，支持基础存储操作

**使用场景：**
- MCP 工具不可用
- 只需要基础存储操作
- 需要自定义处理逻辑

**调用方式：**
```bash
node {baseDir}/scripts/qiniu_node.mjs upload \
  --local "/path/to/file.txt" \
  --key "uploads/file.txt"

node {baseDir}/scripts/qiniu_node.mjs download \
  --key "uploads/file.txt" \
  --local "/path/to/file.txt"

node {baseDir}/scripts/qiniu_node.mjs list \
  --prefix "uploads/" \
  --limit 100
```

---

### 方式三：qshell 命令行（最后备选）

**特点：** 官方命令行工具，功能全面

**使用场景：**
- MCP 和 SDK 都不可用
- 需要批量操作
- 需要高级功能

**调用方式：**
```bash
# 上传文件
qshell fput <Bucket> <Key> <LocalFile>

# 下载文件
qshell get <Bucket> <Key> <LocalFile>

# 列出文件
qshell list <Bucket> <Prefix> <Limit>

# 批量上传
qshell qupload <ThreadCount> <SrcDir> <Bucket>
```

---

## 📋 使用示例

### 示例1：上传备份文件

**用户说：**
```
帮我上传 /backups/daily-20260301.tar.gz 到七牛云
```

**AI 执行：**
```javascript
// 优先使用 MCP 工具
result = use_mcp_tool("qiniu-mcp", "upload_file", {
  "localPath": "/backups/daily-20260301.tar.gz",
  "key": "backups/daily-20260301.tar.gz"
})

// 如果 MCP 不可用，降级到 Node.js SDK
// node scripts/qiniu_node.mjs upload \
//   --local "/backups/daily-20260301.tar.gz" \
//   --key "backups/daily-20260301.tar.gz"
```

**返回：**
```
✅ 上传成功！

文件：daily-20260301.tar.gz
大小：15.2 MB
URL：http://your-domain.com/backups/daily-20260301.tar.gz
```

---

### 示例2：列出文件

**用户说：**
```
列出七牛云 backups 目录下的所有文件
```

**AI 执行：**
```javascript
// 优先使用 MCP 工具
files = use_mcp_tool("qiniu-mcp", "list_files", {
  "prefix": "backups/",
  "limit": 100
})

// 如果 MCP 不可用，降级到 Node.js SDK
// node scripts/qiniu_node.mjs list --prefix "backups/"
```

**返回：**
```
📋 共找到 15 个文件：

backups/backup-20260301.tar.gz  - 15.2 MB  - 2026-03-01 20:00
backups/backup-20260228.tar.gz  - 14.8 MB  - 2026-02-28 20:00
backups/backup-20260227.tar.gz  - 16.1 MB  - 2026-02-27 20:00
...
```

---

### 示例3：获取文件 URL

**用户说：**
```
给我 images/photo.jpg 的访问链接，1小时有效
```

**AI 执行：**
```javascript
// 优先使用 MCP 工具
url = use_mcp_tool("qiniu-mcp", "get_file_url", {
  "key": "images/photo.jpg",
  "private": true,
  "expires": 3600
})

// 如果 MCP 不可用，降级到 Node.js SDK
// node scripts/qiniu_node.mjs url \
//   --key "images/photo.jpg" --private --expires 3600
```

**返回：**
```
🔗 临时访问链接（1小时有效）：

http://your-domain.com/images/photo.jpg?e=1583097600&token=...
```

---

### 示例4：图片处理

**用户说：**
```
把 images/photo.jpg 缩小到 800x600，加水印
```

**AI 执行：**
```javascript
// 必须使用 MCP 工具（SDK 不支持图片处理）
url = use_mcp_tool("qiniu-mcp", "process_image", {
  "key": "images/photo.jpg",
  "operations": [
    {"type": "resize", "width": 800, "height": 600},
    {"type": "watermark", "text": "OpenClaw", "position": "bottom-right"}
  ]
})
```

**返回：**
```
✅ 图片处理完成！

原图：http://your-domain.com/images/photo.jpg
处理后：http://your-domain.com/images/photo.jpg?imageView2/1/w/800/h/600|watermark/...
```

---

### 示例5：批量删除旧备份

**用户说：**
```
删除七牛云上 30 天前的备份
```

**AI 执行：**
```javascript
// 使用 Node.js SDK 脚本
const cutoffDate = Date.now() - (30 * 24 * 60 * 60 * 1000);

// 列出所有备份
const { execSync } = require('child_process');
const files = JSON.parse(execSync('node scripts/qiniu_node.mjs list --prefix "backups/" --format json'));

// 删除旧备份
for (const file of files) {
  if (file.mtime * 1000 < cutoffDate) {
    execSync(`node scripts/qiniu_node.mjs delete --key ${file.key} --force`);
  }
}
```

**返回：**
```
🗑️  已删除 12 个旧备份：

backups/backup-20260115.tar.gz
backups/backup-20260114.tar.gz
...
```

---

## 🔧 API 文档

### Node.js SDK 脚本 API

#### 上传文件
```bash
node scripts/qiniu_node.mjs upload \
  --local <LocalPath> \
  --key <RemoteKey> \
  [--bucket <Bucket>] \
  [--overwrite]
```

#### 下载文件
```bash
node scripts/qiniu_node.mjs download \
  --key <RemoteKey> \
  --local <LocalPath> \
  [--bucket <Bucket>]
```

#### 列出文件
```bash
node scripts/qiniu_node.mjs list \
  [--prefix <Prefix>] \
  [--limit <Limit>] \
  [--delimiter <Delimiter>] \
  [--format json|table]
```

#### 删除文件
```bash
node scripts/qiniu_node.mjs delete \
  --key <RemoteKey> \
  [--bucket <Bucket>] \
  [--force]
```

#### 批量删除
```bash
node scripts/qiniu_node.mjs batch-delete \
  --file <KeyListFile> \
  [--bucket <Bucket>]
```

#### 获取文件 URL
```bash
node scripts/qiniu_node.mjs url \
  --key <RemoteKey> \
  [--private] \
  [--expires <Seconds>]
```

#### 获取文件信息
```bash
node scripts/qiniu_node.mjs stat \
  --key <RemoteKey> \
  [--bucket <Bucket>]
```

#### 移动文件
```bash
node scripts/qiniu_node.mjs move \
  --src-key <SourceKey> \
  --dest-key <DestKey> \
  [--bucket <Bucket>] \
  [--force]
```

#### 复制文件
```bash
node scripts/qiniu_node.mjs copy \
  --src-key <SourceKey> \
  --dest-key <DestKey> \
  [--bucket <Bucket>] \
  [--force]
```

---

### MCP 工具 API

#### 上传文件
```javascript
use_mcp_tool("qiniu-mcp", "upload_file", {
  localPath: string,    // 本地文件路径
  key: string,          // 远程文件名
  bucket?: string,      // 存储桶（可选）
  overwrite?: boolean   // 是否覆盖（可选）
})
```

#### 下载文件
```javascript
use_mcp_tool("qiniu-mcp", "download_file", {
  key: string,          // 远程文件名
  localPath: string,    // 本地保存路径
  bucket?: string       // 存储桶（可选）
})
```

#### 列出文件
```javascript
use_mcp_tool("qiniu-mcp", "list_files", {
  prefix?: string,      // 文件前缀（可选）
  limit?: number,       // 最大数量（可选）
  delimiter?: string    // 分隔符（可选）
})
```

#### 删除文件
```javascript
use_mcp_tool("qiniu-mcp", "delete_file", {
  key: string,          // 远程文件名
  bucket?: string       // 存储桶（可选）
})
```

#### 获取文件 URL
```javascript
use_mcp_tool("qiniu-mcp", "get_file_url", {
  key: string,          // 远程文件名
  private?: boolean,    // 是否私有空间（可选）
  expires?: number      // 有效期秒数（可选）
})
```

#### 图片处理
```javascript
use_mcp_tool("qiniu-mcp", "process_image", {
  key: string,          // 图片文件名
  operations: [         // 处理操作数组
    {
      type: "resize",   // 缩放
      width: 800,
      height: 600,
      mode: "fit"       // fit/fill/crop
    },
    {
      type: "watermark", // 水印
      text: "OpenClaw",
      position: "bottom-right",
      opacity: 0.5
    }
  ]
})
```

---

## ⚙️ 配置文件

### config/qiniu-config.json

```json
{
  "accessKey": "你的AccessKey",
  "secretKey": "你的SecretKey",
  "bucket": "你的存储桶名称",
  "region": "z0",
  "domain": "http://你的域名.com",
  "options": {
    "use_https": true,
    "use_cdn": true,
    "timeout": 30,
    "upload_threshold": 4194304,
    "chunk_size": 4194304,
    "retry_times": 3
  }
}
```

### 配置项说明

| 配置项 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| accessKey | string | ✅ | 七牛云 AccessKey |
| secretKey | string | ✅ | 七牛云 SecretKey |
| bucket | string | ✅ | 存储桶名称 |
| region | string | ✅ | 区域代码 |
| domain | string | ❌ | 访问域名 |
| use_https | boolean | ❌ | 使用 HTTPS |
| use_cdn | boolean | ❌ | 使用 CDN |
| timeout | number | ❌ | 超时时间（秒） |
| upload_threshold | number | ❌ | 分片上传阈值（字节） |
| chunk_size | number | ❌ | 分片大小（字节） |
| retry_times | number | ❌ | 重试次数 |

---

## 🐛 故障排查

### 问题1：qiniu-mcp 未安装

**症状：**
```
❌ qiniu-mcp 未安装
```

**解决：**
```bash
# 自动安装
bash scripts/setup.sh --install-mcp

# 或手动安装
npm install -g @qiniu/qiniu-mcp-server
```

---

### 问题2：凭证配置失败

**症状：**
```
❌ 凭证验证失败：401 Unauthorized
```

**检查：**
1. AccessKey 和 SecretKey 是否正确
2. 是否有对应存储桶的权限
3. 配置文件格式是否正确

**解决：**
```bash
# 重新配置
bash scripts/setup.sh \
  --access-key "新的AccessKey" \
  --secret-key "新的SecretKey" \
  --region "z0" \
  --bucket "mybucket"
```

---

### 问题3：上传失败

**症状：**
```
❌ 上传失败：连接超时
```

**检查：**
1. 网络连接是否正常
2. 区域代码是否正确
3. 存储桶是否存在

**解决：**
```bash
# 检查配置
node scripts/qiniu_node.mjs check-config

# 测试连接
node scripts/qiniu_node.mjs test-connection
```

---

### 问题4：Node.js SDK 未安装

**症状：**
```
❌ Cannot find module 'qiniu'
```

**解决：**
```bash
# 安装 SDK
cd /home/node/.openclaw/workspace/skills/qiniu-kodo
npm install qiniu

# 或使用自动安装
bash scripts/setup.sh --install-sdk
```

---

### 问题5：qshell 未安装

**症状：**
```
❌ qshell: command not found
```

**解决：**
```bash
# 下载并安装
wget https://devtools.qiniu.com/qshell-linux-x64-v2.6.2.zip
unzip qshell-linux-x64-v2.6.2.zip
chmod +x qshell
sudo mv qshell /usr/local/bin/

# 配置账号
qshell account <AccessKey> <SecretKey> <Name>
```

---

## 📚 相关文档

- [七牛云官方文档](https://developer.qiniu.com/)
- [七牛云 Node.js SDK](https://developer.qiniu.com/kodo/sdk/1289/nodejs)
- [七牛云 MCP Server](https://github.com/qiniu/qiniu-mcp-server)
- [qshell 命令行工具](https://developer.qiniu.com/kodo/tools/1302/qshell)
- [OpenClaw 技能开发指南](https://docs.openclaw.ai/skills)

---

## 🎯 未来计划

- [ ] 支持增量同步
- [ ] 支持断点续传进度查询
- [ ] 支持文件加密上传
- [ ] 支持 Webhook 通知
- [ ] 支持多存储桶管理
- [ ] 支持访问统计分析

---

## 👤 作者

- **创建者**：33 (AI 助手)
- **创建日期**：2026-03-01
- **版本**：v1.0.0
- **参考**：Tencent Cloud COS 技能架构

---

## 📞 支持

如有问题，请在 OpenClaw 中联系 33。

---

## 📄 许可证

MIT License
