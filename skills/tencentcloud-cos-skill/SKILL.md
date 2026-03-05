---
name: tencent-cloud-cos
description: >
  腾讯云对象存储(COS)和数据万象(CI)集成技能。当用户需要上传、下载、管理云存储文件，
  或需要进行图片处理（质量评估、超分辨率、抠图、二维码识别、水印）、智能图片搜索、
  文档转PDF、视频智能封面生成等操作时使用此技能。
metadata:
  {
    "openclaw":
      {
        "emoji": "☁️",
        "requires": {},
        "install":
          [
            {
              "id": "node-mcporter",
              "kind": "node",
              "package": "mcporter",
              "bins": ["mcporter"],
              "label": "Install mcporter (MCP CLI)",
            },
            {
              "id": "node-cos-mcp",
              "kind": "node",
              "package": "cos-mcp",
              "bins": ["cos-mcp"],
              "label": "Install cos-mcp (COS MCP Server)",
            },
            {
              "id": "node-cos-sdk",
              "kind": "node",
              "package": "cos-nodejs-sdk-v5",
              "label": "Install COS Node.js SDK",
            },
          ],
      },
  }
---

# 腾讯云 COS 技能

通过 cos-mcp MCP 工具 + Node.js SDK 脚本 + COSCMD 管理腾讯云对象存储和数据万象。

## 首次使用 — 自动设置

当用户首次要求操作 COS 时，按以下流程操作：

### 步骤 1：检查当前状态

```bash
{baseDir}/scripts/setup.sh --check-only
```

如果输出显示一切 OK（cos-mcp 已安装、凭证已配置），跳到「执行策略」。

### 步骤 2：如果未配置，引导用户提供凭证

告诉用户：
> 我需要你的腾讯云凭证来连接 COS 存储服务。请提供：
> 1. **SecretId** — 腾讯云 API 密钥 ID
> 2. **SecretKey** — 腾讯云 API 密钥 Key
> 3. **Region** — 存储桶区域（如 ap-guangzhou）
> 4. **Bucket** — 存储桶名称（格式 name-appid，如 mybucket-1250000000）
> 5. **DatasetName**（可选） — 数据万象数据集名称（仅智能搜索需要）
>
> 你可以在 [腾讯云控制台 > 访问管理 > API密钥管理](https://console.cloud.tencent.com/cam/capi) 获取密钥，
> 在 [COS 控制台](https://console.cloud.tencent.com/cos/bucket) 查看存储桶信息。

### 步骤 3：用户提供凭证后，运行自动设置

```bash
{baseDir}/scripts/setup.sh --secret-id "<SecretId>" --secret-key "<SecretKey>" --region "<Region>" --bucket "<Bucket>"
```

如有 DatasetName：
```bash
{baseDir}/scripts/setup.sh --secret-id "<SecretId>" --secret-key "<SecretKey>" --region "<Region>" --bucket "<Bucket>" --dataset "<DatasetName>"
```

脚本会自动：
- 检查并安装 mcporter（MCP 命令行工具）
- 检查并安装 cos-mcp 和 cos-nodejs-sdk-v5
- 创建/更新 `~/.mcporter/mcporter.json`，写入 cos-mcp 服务器配置
- 将凭证写入 shell 配置文件（`~/.zshrc` 或 `~/.bashrc`），重启后仍可用
- 配置 coscmd（如有 Python 环境）
- 验证 COS 连接

设置完成后即可开始使用。

## 执行策略

三种方式按优先级降级，确保操作始终可完成：

1. **方式一：cos-mcp MCP 工具**（优先） — 功能最全，支持存储 + 图片处理 + 智能搜索 + 文档媒体处理
2. **方式二：Node.js SDK 脚本** — 通过 `scripts/cos_node.mjs` 执行存储操作
3. **方式三：COSCMD 命令行** — 通过 shell 命令执行存储操作

```
mcporter + cos-mcp 可用？（which mcporter && 配置存在）
  ├─ 是 → 使用方式一 mcporter 调用（全部功能）
  └─ 否 → cos-mcp MCP 工具可直接调用？（getCosConfig 返回结果）
              ├─ 是 → 使用方式一直接调用（全部功能）
              └─ 否 → Node.js + cos-nodejs-sdk-v5 可用？
                        ├─ 是 → 使用方式二（存储操作）
                        └─ 否 → coscmd 可用？（which coscmd）
                                  ├─ 是 → 使用方式三（存储操作）
                                  └─ 否 → 运行 setup.sh 安装
```

**判断方式一(mcporter)**：`which mcporter` 且 `cat ~/.mcporter/mcporter.json | grep cos-mcp` 有输出。
**判断方式一(直接)**：尝试调用 `getCosConfig` MCP 工具，若返回结果则可用。
**判断方式二**：`node -e "require('cos-nodejs-sdk-v5')"` 成功则可用。
**判断方式三**：`which coscmd` 有输出则可用。

---

## 方式一：cos-mcp MCP 工具（优先）

> GitHub: https://github.com/Tencent/cos-mcp

MCP 配置模板见 `references/config_template.json`。

### 调用格式

通过 mcporter 命令行调用 cos-mcp MCP 工具：

```
mcporter call cos-mcp.<tool_name> --config ~/.mcporter/mcporter.json --output json [--args '<JSON>']
```

列出所有可用工具：
```
mcporter list cos-mcp --config ~/.mcporter/mcporter.json --schema
```

**判断 mcporter 是否可用**：`which mcporter` 且 `~/.mcporter/mcporter.json` 包含 cos-mcp 配置。
如果 mcporter 不可用，可回退到客户端直接调用 MCP 工具（`getCosConfig` 等）。

### 工具总览

| 类别 | 说明 |
|------|------|
| 存储操作 | 上传、下载、列出、获取签名URL |
| 图片处理 | 质量评估、超分辨率、抠图、二维码识别、水印 |
| 智能搜索 | 以图搜图、文本搜图（需预建数据集） |
| 文档媒体 | 文档转PDF、视频智能封面（异步任务） |

### 常用操作

> 以下示例同时展示两种调用格式。mcporter 格式省略公共前缀 `mcporter call cos-mcp.` 和 `--config ~/.mcporter/mcporter.json --output json`。
> 完整 mcporter 命令：`mcporter call cos-mcp.<tool> --config ~/.mcporter/mcporter.json --output json --args '<JSON>'`

#### 存储

```bash
# 上传本地文件（mcporter 格式）
mcporter call cos-mcp.putObject --config ~/.mcporter/mcporter.json --output json --args '{"filePath":"/path/to/file.jpg","targetDir":"images"}'

# 上传本地文件（客户端直接调用格式）
putObject  filePath="/path/to/file.jpg"  targetDir="images"

# 上传字符串内容
putString  content="hello world"  fileName="test.txt"  targetDir="docs"

# 通过 URL 上传
putObjectSourceUrl  sourceUrl="https://example.com/image.png"  targetDir="images"

# 列出文件
getBucket  Prefix="images/"

# 下载文件
getObject  objectKey="images/photo.jpg"

# 获取签名下载链接
getObjectUrl  objectKey="images/photo.jpg"
```

#### 图片处理

```
# 图片质量评估
assessQuality  objectKey="images/photo.jpg"

# AI 超分辨率
aiSuperResolution  objectKey="images/photo.jpg"

# AI 智能抠图
aiPicMatting  objectKey="images/photo.jpg"

# 二维码识别
aiQrcode  objectKey="images/qrcode.jpg"

# 添加文字水印
waterMarkFont  objectKey="images/photo.jpg"  text="版权所有"

# 获取图片元信息
imageInfo  objectKey="images/photo.jpg"
```

#### 智能搜索（需预建数据集）

```
# 以图搜图
imageSearchPic  uri="https://example.com/query.jpg"

# 文本搜图
imageSearchText  text="蓝天白云"
```

#### 文档与媒体处理（异步任务）

```
# 文档转 PDF
createDocToPdfJob  objectKey="docs/report.docx"
# 查询任务结果
describeDocProcessJob  jobId="<jobId>"

# 视频智能封面
createMediaSmartCoverJob  objectKey="videos/demo.mp4"
# 查询任务结果
describeMediaJob  jobId="<jobId>"
```

工具详细参数定义见 `references/api_reference.md`。

---

## 方式二：Node.js SDK 脚本

> 官方文档: https://www.tencentcloud.com/zh/document/product/436/8629

当 cos-mcp 不可用时，通过 `scripts/cos_node.mjs` 执行存储操作。凭证从环境变量读取。

### 常用命令

> 以下省略 `node {baseDir}/scripts/cos_node.mjs` 前缀。完整格式：`node {baseDir}/scripts/cos_node.mjs <action> [options]`

```bash
# 上传文件
upload --file /path/to/file.jpg --key remote/path/file.jpg

# 上传字符串
put-string --content "文本内容" --key remote/file.txt --content-type "text/plain"

# 下载文件
download --key remote/path/file.jpg --output /path/to/save/file.jpg

# 列出文件
list --prefix "images/"

# 获取签名 URL
sign-url --key remote/path/file.jpg --expires 3600

# 查看文件信息
head --key remote/path/file.jpg

# 删除文件
delete --key remote/path/file.jpg
```

所有命令输出 JSON 格式，`success: true` 表示成功，退出码 0。

### 限制

仅支持存储操作，**不支持**图片处理、智能搜索、文档转换。

---

## 方式三：COSCMD 命令行

> 官方文档: https://www.tencentcloud.com/zh/document/product/436/10976

当方式一和方式二均不可用时使用。配置持久化在 `~/.cos.conf`。

### 常用命令

```bash
# 上传
coscmd upload /path/to/file.jpg remote/path/file.jpg
coscmd upload -r /path/to/folder/ remote/folder/

# 下载
coscmd download remote/path/file.jpg /path/to/save/file.jpg
coscmd download -r remote/folder/ /path/to/save/

# 列出文件
coscmd list images/

# 删除
coscmd delete remote/path/file.jpg
coscmd delete -r remote/folder/ -f

# 签名 URL
coscmd signurl remote/path/file.jpg -t 3600

# 文件信息
coscmd info remote/path/file.jpg

# 复制/移动
coscmd copy <BucketName-APPID>.cos.<Region>.myqcloud.com/source.jpg dest.jpg
coscmd move <BucketName-APPID>.cos.<Region>.myqcloud.com/source.jpg dest.jpg
```

### 限制

仅支持存储操作，**不支持**图片处理、智能搜索、文档转换。

---

## 功能对照表

| 功能 | 方式一 cos-mcp | 方式二 Node SDK | 方式三 COSCMD |
|------|:-:|:-:|:-:|
| 上传文件 | ✅ | ✅ | ✅ |
| 上传字符串/Base64 | ✅ | ✅ | ❌ |
| 通过 URL 上传 | ✅ | ❌ | ❌ |
| 下载文件 | ✅ | ✅ | ✅ |
| 列出文件 | ✅ | ✅ | ✅ |
| 获取签名 URL | ✅ | ✅ | ✅ |
| 删除文件 | ❌ | ✅ | ✅ |
| 查看文件信息 | ❌ | ✅ | ✅ |
| 递归上传/下载目录 | ❌ | ❌ | ✅ |
| 图片处理（CI） | ✅ | ❌ | ❌ |
| 智能搜索 | ✅ | ❌ | ❌ |
| 文档转 PDF | ✅ | ❌ | ❌ |
| 视频智能封面 | ✅ | ❌ | ❌ |

## 使用规范

1. **首次使用先运行** `{baseDir}/scripts/setup.sh --check-only` 检查环境
2. **mcporter 调用必须带** `--config ~/.mcporter/mcporter.json` 和 `--output json`
3. **凭证不明文展示**：引导用户自行通过 setup.sh 或编辑配置文件设置
4. **所有文件路径**（`objectKey`/`cospath`/`--key`）为存储桶内的相对路径，如 `images/photo.jpg`
5. **图片处理/智能搜索/文档转换仅方式一可用**，不可用时明确告知用户
6. **异步任务**（文档转换、视频封面）需通过 `jobId` 轮询结果
7. **上传后主动获取链接**：上传完成后调用 `getObjectUrl` 或 `sign-url` 返回访问链接
8. **错误处理**：调用失败时先用 `setup.sh --check-only` 诊断环境问题
9. **方式二脚本源码**见 `scripts/cos_node.mjs`
10. **MCP 工具详细参数**见 `references/api_reference.md`
11. **MCP 配置模板**见 `references/config_template.json`
