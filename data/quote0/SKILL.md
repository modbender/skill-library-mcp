---
name: quote0
description: Control MindReset Dot Quote/0 through the local quote0.js script and Dot Developer Platform APIs. Use when the user asks to configure Quote/0, push text/image content, query device status, switch next content, list tasks, or troubleshoot Dot Open API integration. Requires credentials DOT_API_KEY and (for device actions) DOT_DEVICE_ID.
homepage: https://dot.mindreset.tech/docs/service/open
metadata:
  {
    "openclaw":
      {
        "emoji": "🖼️",
        "requires": { "bins": ["node"], "env": ["DOT_API_KEY", "DOT_DEVICE_ID"] },
        "primaryEnv": "DOT_API_KEY",
      },
  }
---

# Quote/0 技能（v1.0.4）

使用本地脚本调用 Dot Developer Platform API：

```bash
node quote0.js <command> [options]
```

> 在技能目录内执行命令。

---

## 1) 凭据与安全（必须遵守）

### 必需凭据
- `DOT_API_KEY`（必需）
- `DOT_DEVICE_ID`（设备相关命令必需，如 `status|next|list|text|image`）

### 禁止事项
- 不要把 API Key / Device ID 硬编码到脚本、SKILL.md、Git 提交。
- 不要把敏感文件路径传给 `--imageFile`（脚本会读取该路径对应的本地文件并上传）。

### 推荐注入方式（按安全优先级）
1. **单次命令传参（最推荐）**
2. **当前终端临时环境变量**
3. **长期写入 shell 配置（仅在用户明确同意后）**

> 若要持久保存环境变量（如写入 `~/.zshrc` / `~/.bashrc` / PowerShell profile），必须先征得用户明确同意。

---

## 2) 跨平台运行方式（macOS / Linux / Windows）

先进入技能目录：

```bash
cd /path/to/quote0
```

### 方式 A：单次命令传参（推荐）
```bash
node quote0.js devices --apiKey "..."
node quote0.js status --apiKey "..." --deviceId "..."
```

### 方式 B：临时环境变量

#### macOS / Linux（bash/zsh）
```bash
export DOT_API_KEY="你的_key"
export DOT_DEVICE_ID="你的_id"
node quote0.js devices
node quote0.js status
```

#### Windows PowerShell
```powershell
$env:DOT_API_KEY="你的_key"
$env:DOT_DEVICE_ID="你的_id"
node .\quote0.js devices
node .\quote0.js status
```

#### Windows CMD
```cmd
set DOT_API_KEY=你的_key
set DOT_DEVICE_ID=你的_id
node .\quote0.js devices
node .\quote0.js status
```

### 方式 C：持久环境变量（需用户同意）
仅在用户明确授权后再执行。

---

## 3) 首次配置（避免 404/403）

1. 在 Dot App 完成设备配对、联网、在线确认
2. 创建 API Key：`More → API Key → Create API Key`
3. 获取 Device Serial Number（作为 `DOT_DEVICE_ID`）
4. 在 Content Studio 至少添加：
   - 一个 **Text API** 内容项
   - 一个 **Image API** 内容项
5. 运行：
   - `devices` 确认设备可见
   - `status` 确认设备在线

---

## 4) 命令总览

```bash
node quote0.js --help
```

- `devices`：获取设备列表
- `status`：获取设备状态
- `next`：切换下一条内容
- `list`：列出设备内容项
- `text`：推送文本内容
- `image`：推送图像内容

---

## 5) 命令与 API 对应

### devices
- API: `GET /api/authV2/open/devices`
```bash
node quote0.js devices
```

### status
- API: `GET /api/authV2/open/device/:id/status`
```bash
node quote0.js status
node quote0.js status --deviceId "ABCD1234ABCD"
```

### next
- API: `POST /api/authV2/open/device/:id/next`
```bash
node quote0.js next
```

### list
- API: `GET /api/authV2/open/device/:deviceId/:taskType/list`
```bash
node quote0.js list --taskType loop
```

### text
- API: `POST /api/authV2/open/device/:deviceId/text`
```bash
node quote0.js text --message "你好，Quote/0"
node quote0.js text --title "验证码助手" --message "你的验证码：205112" --signature "2026-02-25 00:40" --refresh true
```

关键参数：
- `--message` 必填
- `--title` / `--signature` / `--icon` / `--link` / `--taskKey` 可选
- `--refresh` 默认 `true`

### image
- API: `POST /api/authV2/open/device/:deviceId/image`
```bash
node quote0.js image --imageFile ./card.png
node quote0.js image --imageFile ./text-card.png --border 0 --ditherType NONE --refresh true
```

关键参数：
- `--image` 或 `--imageFile` 二选一
- `--imageFile` 必须是 `.png` 普通文件，且大小不超过 5MB
- 脚本会校验 PNG 文件头（不可绕过）
- `--border`：0 白边 / 1 黑边
- `--ditherType`：`DIFFUSION | ORDERED | NONE`
- `--ditherKernel`：`THRESHOLD | ATKINSON | BURKES | FLOYD_STEINBERG | ...`

---

## 6) 常见错误排查

- `401 Unauthorized`：API Key 错误/过期
- `403 Forbidden`：Key 无此设备权限
- `404 Not Found`：设备 ID 不存在，或未添加 Text/Image API 内容项
- `400 Invalid Params`：参数非法（如 border、image、dither）
- `500 Device response failure`：设备离线/网络异常
- 限流：`10 requests/second`

---

## 7) 官方文档

- 总览：`https://dot.mindreset.tech/docs/service/open`
- API Key：`https://dot.mindreset.tech/docs/service/open/get_api`
- Device ID：`https://dot.mindreset.tech/docs/service/open/get_device_id`
- Device List：`https://dot.mindreset.tech/docs/service/open/list_devices_api`
- Device Status：`https://dot.mindreset.tech/docs/service/open/device_status_api`
- Device Next：`https://dot.mindreset.tech/docs/service/open/device_next_api`
- List Device Content：`https://dot.mindreset.tech/docs/service/open/list_device_tasks_api`
- Text API：`https://dot.mindreset.tech/docs/service/open/text_api`
- Image API：`https://dot.mindreset.tech/docs/service/open/image_api`
