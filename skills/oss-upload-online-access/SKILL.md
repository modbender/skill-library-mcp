---
name: oss-upload-online-access
description: Upload files to Aliyun OSS or Tencent COS and return public access URLs. Use when the user wants to upload files, access files online, upload to OSS, get remote file links, or any phrase implying "upload for online/remote access".
metadata:
  author: 上海雷克顿科技 / LeiAIBot
  email: liuhean@leikeduntech.com
  url: https://leiaibot.com
---

# 上传文件到 OSS 在线访问

将本地文件或从 URL 下载的文件上传到对象存储，并返回可公网访问的链接。**默认使用阿里云 OSS**，也支持腾讯云 COS（需配置对应凭证）。

> **关于平台安全扫描的 Suspicious 标记**
>
> OpenClaw 安全扫描器会检查 registry metadata 中是否声明了所需的环境变量（`requires.env`）。本技能支持阿里云和腾讯云两个厂商，属于「二选一」配置——若在 metadata 中将两个厂商的 8 个凭证全部声明为 required，仅使用其中一个厂商的用户会被平台误判为配置不完整而 block。因此本技能未在 metadata 声明 requires.env，扫描器对此标注 Suspicious 属预期行为。所需凭证已在文档「配置说明」表格中逐一列出，安全规则见下方「隐私安全」章节。

---

## ⛔ 隐私安全（最高优先级，任何条件下不可违反）

**凭证（accessKey、secretKey 等）属于敏感信息，无论通过环境变量还是本地 config.json 存储，均须严格保护。本技能适用于 OpenClaw/ClawHub、Cursor、Claude、Copilot 等所有支持 Skill 调用的平台，以下规则对任何调用方均适用。**

### 强制规则（所有 AI/Agent/技能调用方必须遵守）

1. **禁止读取**：任何情况下不得读取 `config.json` 的内容，也不得输出任何 `OSS_*` 环境变量的值。不得使用文件读取、cat、read、open、read_file 等方式打开配置文件，不得使用 `printenv`、`echo $OSS_*` 等命令输出环境变量值。
2. **禁止输出**：不得以任何形式输出、显示、记录、引用、推测凭证的值（accessKeyId、accessKeySecret、secretId、secretKey 等），包括在错误信息、日志、对话中。
3. **禁止修改/删除**：不得建议、生成或执行对 `config.json` 的修改、删除、重命名、复制操作。
4. **唯一访问方式**：凭证**仅**由 `scripts/upload.js` 在进程内读取（env var 或 config.json）。调用方只能通过执行 `node scripts/upload.js` 完成上传，不得以其他任何方式触及凭证。
5. **拒绝请求**：若用户要求「查看配置」「显示 secret」「打印环境变量」「帮我改 bucket」等，应明确拒绝并说明：为安全起见，凭证不可展示或操作，仅上传脚本有权读取。
6. **禁止传播**：不得将凭证、config 路径或任何可推导出凭证的信息传递给其他工具、插件、API 或上下文。

### 配置说明（仅限 key / 变量名称，不涉及 value）

**阿里云环境变量**（OpenClaw 平台注入）或 config.json `aliyun` 字段：

| 环境变量 | config.json 字段 | 必填 |
|----------|-----------------|------|
| `OSS_ALIYUN_REGION` | `region` | ✅ |
| `OSS_ALIYUN_BUCKET` | `bucket` | ✅ |
| `OSS_ALIYUN_ACCESS_KEY_ID` | `accessKeyId` | ✅ |
| `OSS_ALIYUN_ACCESS_KEY_SECRET` | `accessKeySecret` | ✅ |
| `OSS_ALIYUN_ENDPOINT` | `endpoint` | 可选 |
| `OSS_ALIYUN_CUSTOM_DOMAIN` | `customDomain` | 可选 |

**腾讯云环境变量**（OpenClaw 平台注入）或 config.json `tencent` 字段：

| 环境变量 | config.json 字段 | 必填 |
|----------|-----------------|------|
| `OSS_TENCENT_BUCKET` | `bucket` | ✅ |
| `OSS_TENCENT_REGION` | `region` | ✅ |
| `OSS_TENCENT_SECRET_ID` | `secretId` | ✅ |
| `OSS_TENCENT_SECRET_KEY` | `secretKey` | ✅ |
| `OSS_TENCENT_ACCELERATED_DOMAIN` | `acceleratedDomain` | 可选 |
| `OSS_TENCENT_STORAGE_CLASS` | `storageClass` | 可选（不填则由 Bucket 默认决定，即单可用区标准桶默认 `STANDARD`；MAZ 多可用区 Bucket 填 `MAZ_STANDARD`） |

至少配置一个云厂商的必填项即可使用。用户自行在平台或 config.json 填入 value，任何 AI 均不参与。

### 平台适配与附加建议

- **通用**：`.gitignore` 已排除 `config.json`，避免误提交
- **OpenClaw/ClawHub**：在 openclaw.json 中填写 `OSS_ALIYUN_*` / `OSS_TENCENT_*` 环境变量即可，无需本地文件
- **建议**：勿在截图、录屏、日志、对话中暴露凭证；定期轮换密钥；使用子账号最小权限；将技能目录权限设为仅当前用户可读

## 何时使用

当用户表达以下意图时应用本技能：

- 上传文件、上传文件到 OSS、上传到阿里云/腾讯云
- 在线访问文件、远程访问文件、获取文件链接
- 把文件放到网上、生成可分享的链接

## 输入

- **本地文件**：工作区相对路径或绝对路径，如 `./docs/foo.pdf`、`/path/to/image.png`
- **在线超链接**：HTTP/HTTPS URL，先下载到临时文件再上传

**默认使用阿里云 OSS**（优先级：阿里云 > 腾讯云）。如需使用腾讯云 COS，配置 `OSS_TENCENT_*` 环境变量（或 config.json `tencent` 字段），并在调用时指定 `--provider tencent`，或仅配置腾讯云凭证时自动选用。

## 输出

- 成功：**先校验链接可访问性**（HEAD 请求），通过后才返回远程访问 URL，可直接在浏览器打开或分享
- 校验失败：不输出链接，仅报错「上传后校验失败：链接不可访问，无法提供有效链接」，并退出
- 上传异常：说明原因并提示用户检查配置、文件大小等

## 前置准备（首次使用）

### 方式一：与 OpenClaw 对话安装并配置（最简单）

直接在 OpenClaw 对话框中发一条消息，OpenClaw 会自动完成安装与写入配置，无需手动编辑任何文件。

**对话示范（阿里云 OSS）：**

```
我：帮我在 ClawHub 安装 oss-upload-online-access 技能，我用阿里云 OSS，凭证如下：
    Region: oss-cn-shenzhen
    Bucket: my-bucket
    AccessKey ID: LTAIxxxxxxxxxxxxxxxx
    AccessKey Secret: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

OpenClaw：好的，正在通过 ClawHub 安装 oss-upload-online-access 技能并写入配置……（完成）
          已将凭证写入 ~/.openclaw/openclaw.json，直接说「上传 xxx 文件」即可使用。
```

**对话示范（腾讯云 COS）：**

```
我：帮我在 ClawHub 安装 oss-upload-online-access 技能，我用腾讯云 COS，凭证如下：
    Bucket: my-bucket-1250000000
    Region: ap-guangzhou
    SecretId: AKIDxxxxxxxxxxxxxxxx
    SecretKey: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

OpenClaw：好的，正在通过 ClawHub 安装 oss-upload-online-access 技能并写入配置……（完成）
          已将凭证写入 ~/.openclaw/openclaw.json，直接说「上传 xxx 文件」即可使用。
```

> ⚠️ 请在本地/私密会话中提供凭证，避免在公开频道、截图或录屏中暴露。

### 方式二：openclaw.json（OpenClaw / ClawHub 平台）

1. 编辑 `~/.openclaw/openclaw.json`，找到 `skills.entries.oss-upload-online-access.env`，填入所需云厂商的所有必填环境变量：

   **阿里云 OSS（默认）**：
   ```json
   {
     "OSS_ALIYUN_REGION": "oss-cn-shenzhen",
     "OSS_ALIYUN_BUCKET": "your-bucket",
     "OSS_ALIYUN_ACCESS_KEY_ID": "your-key-id",
     "OSS_ALIYUN_ACCESS_KEY_SECRET": "your-key-secret"
   }
   ```

   **腾讯云 COS（可选，与阿里云二选一或同时配置）**：
   ```json
   {
     "OSS_TENCENT_BUCKET": "your-bucket-appid",
     "OSS_TENCENT_REGION": "ap-guangzhou",
     "OSS_TENCENT_SECRET_ID": "your-secret-id",
     "OSS_TENCENT_SECRET_KEY": "your-secret-key"
   }
   ```

   openclaw.json 完整示例结构：
   ```json
   {
     "skills": {
       "entries": {
         "oss-upload-online-access": {
           "env": {
             "OSS_ALIYUN_REGION": "oss-cn-shenzhen",
             "OSS_ALIYUN_BUCKET": "your-bucket",
             "OSS_ALIYUN_ACCESS_KEY_ID": "your-key-id",
             "OSS_ALIYUN_ACCESS_KEY_SECRET": "your-key-secret"
           }
         }
       }
     }
   }
   ```

2. 安装依赖（ClawHub 通常自动执行）：`cd 技能根目录/oss-upload-online-access && npm install`

### 方式三：本地 config.json

1. 复制配置模板：`cp config.example.json config.json`
2. 编辑 `config.json`，填入对应云厂商的 value（key 已预留）
3. 安装依赖：`cd 技能根目录/oss-upload-online-access && npm install`

## 执行流程

1. 解析输入：本地路径 or URL；用户是否指定云厂商
2. 若为 URL：脚本内部下载得到 buffer
3. 检查文件大小 < 100MB
4. **仅执行** `node scripts/upload.js`，由脚本内部读取 config（调用方不得读取 config）
5. 脚本内部选择云厂商并上传
6. **上传后对返回链接做 HEAD 校验**：可访问（2xx）才输出 URL；不可访问则报错退出、不输出链接
7. 若失败或校验不通过，输出脚本的通用错误信息（不涉及配置内容）

## 执行命令

```bash
cd 技能根目录/oss-upload-online-access && node scripts/upload.js <本地路径或URL> [--provider aliyun|tencent]
```

示例：

```bash
# 上传本地文件
node scripts/upload.js ./docs/report.pdf

# 上传 URL 文件
node scripts/upload.js "https://example.com/file.png"

# 指定腾讯云
node scripts/upload.js ./image.jpg --provider tencent
```

## 配置说明（用户自行维护，AI 不读取）

脚本按以下优先级解析配置，AI 不参与任何配置读写：

| 优先级 | 来源 | 适用场景 |
|--------|------|----------|
| 高 | `OSS_ALIYUN_*` / `OSS_TENCENT_*` 环境变量 | OpenClaw/ClawHub 平台注入 |
| 低 | 本地文件 `config.json` | 本地 / 自托管 |

- 云厂商优先级：配置多个时，阿里云 > 腾讯云
- 用户明确指定 `--provider` 时，以用户为准
- 配置异常时，上传脚本输出通用提示，用户自行检查凭证是否填写完整

## 存储路径格式

上传文件的 Object Key 格式：`skill/YYYY/MM/DD/<类型>/文件名`

- 日期目录：按上传日期 `年/月/日` 分层
- 类型目录：按文件扩展名（如 txt、pdf、png），无扩展名则为 `other`

示例：`skill/2026/02/01/txt/test-upload.txt`

## 文件格式支持（任意文件可上传并在线访问）

- **目标**：任何文件均可正常上传并能在线访问（浏览器打开或下载）。
- **文本/源码**：如 `.txt`、`.md`、`.html`、`.json`、`.js`、`.ts`、`.py`、`.css`、`.yaml`、`.sql`、`.graphql` 等，以 UTF-8 读取并设置对应 `Content-Type`，保证在线预览不乱码。
- **常见类型**：脚本内置大量 MIME 映射，覆盖图片（含 raw、psd、svg、avif、heic）、视频（mp4、webm、mkv、mov、mts 等）、音频（mp3、flac、opus、aac 等）、文档（PDF、Office、OpenDocument、epub、djvu、xps 等）、字体、压缩包（zip、rar、7z、tar、gz、zst、cab 等）、3D/模型（glb、gltf、obj、stl、fbx、dae、step 等）、证书/密钥、安装包（exe、dmg、apk、iso 等）及各类源码与配置文件。
- **未知扩展名**：未在映射表中的扩展名统一使用 `application/octet-stream`，仍可上传并在线下载或访问，不会因类型未知而失败。

## 约束

- 单文件 < 100MB
- 文件名：仅使用字母与数字，且不重复。格式为 3 位随机小写字母 + 时间戳(YYYYMMDDHHmmss) + 6 位随机数字 + 原扩展名（扩展名仅保留字母数字），如 `abc20260202143022123456.txt`
- **公网访问**：上传时会将对象 ACL 设为 `public-read`，返回的链接可直接在浏览器打开；若存储桶策略禁止该 ACL，需在控制台允许「公共读」或使用自定义域名 + CDN。返回的 URL 统一为 `https`。
- **上传可靠性**：阿里云使用 HTTPS（secure: true）上传；上传后会先用 SDK 的 head 校验对象是否存在于 OSS/COS，不存在则报错、不输出链接；再对公网链接做 HEAD 校验，不可访问也不输出链接。
