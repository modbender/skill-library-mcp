# 123pan-upload

123云盘文件上传工具 - 支持直链短链接、大文件分片上传

## 功能特性

- ✅ **直链短链接**（推荐）：`https://xxx.v.123pan.cn/{userID}/{fileID}`，隐私友好、URL 简洁
- ✅ **大文件分片上传**：支持超过 1GB 的文件
- ✅ **三种链接格式**：直链短链接 / 分享链接 / 直链长链接
- ✅ **自动续期 Token**：支持从 JWT Token 提取用户 ID

## 安装

### 1. 安装 Skill

```bash
# 方法一：使用 OpenClaw CLI
openclaw skill install ./123pan-upload.skill

# 方法二：手动复制
mkdir -p ~/.openclaw/skills/123pan-upload
cp -r 123pan-upload/* ~/.openclaw/skills/123pan-upload/
```

### 2. 配置环境变量

编辑 `~/.openclaw/.env`：

```bash
# 123云盘 OpenAPI 配置
export PAN123_ACCESS_TOKEN="your_access_token_here"
export PAN123_DIRECT_FOLDER_ID="your_folder_id_here"
```

**获取方式：**
- `access_token`：从 [123云盘开放平台](https://www.123pan.com/dashboard/dev) 获取
- `folder_id`：在 123云盘网页版中，打开已启用直链的文件夹，从 URL 获取文件夹 ID

### 3. 安装依赖

```bash
pip install requests
```

## 使用方法

### 基本使用

```bash
python scripts/upload.py --file /path/to/file
```

默认返回**直链短链接**。

### 指定链接类型

```bash
# 直链短链接（默认）
python scripts/upload.py --file /path/to/file --link-type short_direct

# 分享链接（需要跳转页面）
python scripts/upload.py --file /path/to/file --link-type share

# 直链长链接（包含完整路径）
python scripts/upload.py --file /path/to/file --link-type direct
```

### 指定目标文件夹

```bash
python scripts/upload.py --file /path/to/file --folder 30767843
```

### 输出示例

```json
{
  "success": true,
  "file_id": 30769728,
  "filename": "example.zip",
  "size": 6010,
  "link": "https://1817804024.v.123pan.cn/1817804024/30769728",
  "link_type": "short_direct_link"
}
```

## 链接类型对比

| 类型 | 格式 | 特点 |
|------|------|------|
| `short_direct` | `https://xxx.v.123pan.cn/{userID}/{fileID}` | 直接下载，URL 短，隐私好（默认） |
| `share` | `https://www.123pan.com/s/xxxxx` | 分享页面，需点击下载 |
| `direct` | `https://xxx.v.123pan.cn/{userID}/folder/file` | 直接下载，URL 长，暴露文件名 |

## 文件结构

```
123pan-upload/
├── SKILL.md              # Skill 使用说明
├── manifest.json         # 元数据
├── scripts/
│   └── upload.py         # 主程序
└── references/
    └── api-reference.md  # API 文档
```

## API 说明

### 上传流程

1. **小文件（<1GB）**：单步上传 `POST /upload/v2/file/single/create`
2. **大文件（≥1GB）**：分片上传
   - 创建文件 `POST /upload/v2/file/create`
   - 获取上传 URL `POST /upload/v1/file/get_upload_url`
   - 上传分片 `PUT {presigned_url}`
   - 完成上传 `POST /upload/v2/file/upload_complete`

### 直链短链接格式

```
https://{userID}.v.123pan.cn/{userID}/{fileID}
```

用户 ID 从 JWT Token 自动提取，无需手动配置。

## 注意事项

- 单文件大小限制：10GB（开发者账号）
- Token 有效期：检查 `exp` 字段，过期后需重新获取
- 文件夹需**启用直链空间**，否则无法获取直链

## 许可证

MIT
