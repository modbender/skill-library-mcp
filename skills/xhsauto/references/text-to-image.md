---
name: xhs-image
description: 小红书图片生成工具文生图 / 图编辑工具，封装 Google Gemini "nano banana" 与字节跳动 Seed 的 OpenAI 兼容接口，用于生成小红书内容配图。
metadata: {"openclaw": {"emoji": "🖼️"}}
---

# 文生图和图编辑

面向小红书自媒体运营的文生图和图编辑工具，提供两个能力：
1. **文生图**：根据 Prompt 生成图片，支持常见比例（默认 1:1）。
2. **图编辑 / 优化**：基于已有底图与 Prompt 生成优化后的图片。

基于 OpenAI 兼容的图片生成接口，支持以下提供方：
- `google`：Google Gemini "nano banana"（需配置 Google API 网关）
- `seed`：字节跳动 Seed（需配置 Seed API 网关）

## 实现版本

提供两个版本的实现：

### Python 版本（推荐）✅
- **脚本路径**：`{baseDir}/scripts/xhs-image.py`
- **优势**：跨平台兼容（Windows/macOS/Linux），依赖简单，易于维护
- **依赖**：`pip install requests`
- **推荐场景**：所有场景，特别是 Windows 用户

### Bash 版本
- **脚本路径**：`{baseDir}/scripts/xhs-image.sh`
- **优势**：Unix 系统原生支持，无需 Python 环境
- **依赖**：`curl`、`jq`、`base64`
- **推荐场景**：纯 Unix/Linux 环境，或不希望安装 Python 依赖的场景

## 环境变量

### Google Gemini（nano banana）
| 变量名 | 说明 | 默认值 |
| --- | --- | --- |
| `GOOGLE_API_KEY` / `GEMINI_API_KEY` | ✅ 必填，Google/Gemini API Key（任意其一） | 无 |
| `GOOGLE_API_BASE` / `GEMINI_API_BASE` | 接口 Base URL | `https://generativelanguage.googleapis.com/openai` |
| `GOOGLE_IMAGE_MODEL` / `GEMINI_IMAGE_MODEL` | 图片模型名称 | `gemini-3.1-flash-image-preview` |

### ByteDance Seed
| 变量名 | 说明 | 默认值 |
| --- | --- | --- |
| `SEED_API_KEY` | ✅ 必填，Seed API Key | 无 |
| `SEED_API_BASE` | 接口 Base URL | `https://seed.bytedanceapi.com` |
| `SEED_IMAGE_MODEL` | 图片模型名称 | `bytedance/seed-v1` |

## 命令行参数

两个版本的参数完全一致：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `--mode` | 枚举 | ✅ | `generate`（文生图）或 `edit`（图编辑） |
| `--prompt` | 字符串 | ✅ | 提示词；用于生成或编辑指导 |
| `--base-image` | 路径 | ⚠️ | 仅在 `--mode edit` 下必填，作为底图输入 |
| `--provider` | 枚举 | ❌ | `google`（默认）或 `seed`，决定使用哪套环境变量 |
| `--seed` | 整数 | ❌ | 随机种子 |
| `--ratio` | 枚举 | ❌ | 输出比例，可选 `1:1`（默认）、`3:4`、`4:3`、`9:16`、`16:9` |
| `--output` | 路径 | ✅ | 指定输出文件路径 |

> **返回值**：
> 1. 标准错误输出（stderr）：日志信息
> 2. 标准输出（stdout）：JSON 结果，包含 `success`、`output`、`mode`、`provider` 等字段，方便 Agent 解析

## 依赖

### Python 版本（推荐）
```bash
pip install requests
```

### Bash 版本
- `curl`：向 OpenAI 兼容接口发起 HTTP 请求
- `jq`：解析接口返回的 JSON，提取 b64 数据
- `base64`：将返回的 Base64 图片内容解码为 PNG

安装示例：
- **macOS**：`brew install curl jq coreutils`
- **Ubuntu / Debian**：`sudo apt-get install curl jq coreutils`
- **CentOS / Rocky / Alma**：`sudo yum install curl jq coreutils`
- **Windows**：需要 Git Bash 或 WSL 环境

## 使用方式

### Python 版本（推荐）

#### 文生图
```bash
# 设置环境变量
export GOOGLE_API_KEY=xxx
export GOOGLE_API_BASE=https://...

# 生成图片
python {baseDir}/scripts/xhs-image.py \
  --mode generate \
  --prompt "小红书风格的下午茶摆拍" \
  --ratio 1:1 \
  --provider google \
  --output /path/to/output.png
```

#### 图编辑（基于已有底图）
```bash
python {baseDir}/scripts/xhs-image.py \
  --mode edit \
  --base-image /path/to/base.png \
  --prompt "添加温暖的光线和生活气息" \
  --ratio 1:1 \
  --output /path/to/output.png
```

**输出示例：**
```json
{
  "success": true,
  "output": "/path/to/output.png",
  "mode": "generate",
  "provider": "google",
  "size": "1024x1024"
}
```

> 如果 `--output` 指定的目录不存在，脚本会自动创建。

### Bash 版本

#### 文生图
```bash
# 赋予执行权限（首次使用）
chmod +x {baseDir}/scripts/xhs-image.sh

# 生成图片
GOOGLE_API_KEY=xxx GOOGLE_API_BASE=https://... {baseDir}/scripts/xhs-image.sh \
  --mode generate \
  --prompt "小红书风格的下午茶摆拍" \
  --ratio 1:1 \
  --provider google \
  --output /path/to/output.png
```

#### 图编辑
```bash
{baseDir}/scripts/xhs-image.sh \
  --mode edit \
  --base-image /path/to/base.png \
  --prompt "添加温暖的光线和生活气息" \
  --ratio 1:1 \
  --output /path/to/output.png
```

## 输出
- 控制台日志（stderr）：流程与错误信息
- 控制台结果（stdout）：图片文件路径
- JSON（stdout 尾部）：
```json
{
  "success": true,
  "mode": "generate",
  "provider": "google",
  "prompt": "...",
  "base_image": null,
  "ratio": "1:1",
  "output_path": "/tmp/xhs-image-XXXX.png"
}
```

## 常见问题

### Python 版本
1. **ModuleNotFoundError: No module named 'requests'**  
   安装依赖：`pip install requests`

2. **返回 401 Unauthorized**  
   确认 API Key 是否正确且写入对应环境变量（`GOOGLE_API_KEY` 或 `GEMINI_API_KEY`）

3. **FileNotFoundError: Base image not found**  
   确认 `--base-image` 路径正确且文件存在

4. **国内网络不可达 / 连接超时**  
   国内直连国际模型常被阻断，建议购买具备 OpenAI 兼容出口的国内中转站或代理网关，再将 `GOOGLE_API_BASE` / `GEMINI_API_BASE` 指向该中转服务

5. **Windows 上路径问题**  
   使用正斜杠 `/` 或双反斜杠 `\\`，例如：`C:/path/to/image.png` 或 `C:\\path\\to\\image.png`

### Bash 版本
1. **提示缺少必要依赖项（curl/jq/base64）**  
   请先安装依赖，参考上方"依赖"部分

2. **Windows 上无法运行**  
   Bash 脚本需要 Unix 环境，建议在 Windows 上使用 Python 版本，或安装 WSL/Git Bash

3. **返回 empty data**  
   检查 API Base URL 是否指向 OpenAI 兼容的网关
