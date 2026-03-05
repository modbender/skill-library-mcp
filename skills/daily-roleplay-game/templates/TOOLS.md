# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- 生图工具配置（见下方）
- SSH hosts and aliases
- Device nicknames
- Anything environment-specific

---

## 生图工具配置

当前生图后端（填写一项，未配置则跳过所有图片生成）：

- **工具类型**：（comfyui / sd-webui / midjourney / nano-banana-pro / 无）
- **接入地址/API**：

### 各后端接入方式

| 后端 | 类型 | 接入地址示例 | 说明 |
|------|------|-------------|------|
| ComfyUI | 本地 | `http://localhost:8188` | 完整工作流支持，详细配置见 `data/templates/comfyui/README.md` |
| SD WebUI | 本地 | `http://localhost:7860` | 通过 `/sdapi/v1/txt2img` 接口调用，prompt 复用生图关键词体系 |
| Midjourney | 在线 | API 代理地址 + token | 通过 /imagine 命令生图，prompt 需转换为 MJ 格式 |
| Nano Banana Pro | 在线 | API endpoint + API key | REST API 在线生图 |
| 无 | — | — | 跳过所有图片生成，消息中说明暂无图片功能 |

### 脸部参考图片库
**根目录**: `~/.openclaw/media/face_reference/`

（在此添加你的 face reference 图片配置）

---

Add whatever helps you do your job. This is your cheat sheet.
