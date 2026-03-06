# 📕 OpenClaw 小红书技能

> [OpenClaw](https://openclaw.ai) 小红书自动化技能 — 通过 Telegram / Discord 控制：爬取热点、AI 生成图文、一键发布。

[English](README.md) | 中文

## 功能

- **热点爬取** — 自动抓取小红书发现页热门话题
- **AI 生成内容** — 文案（Claude）+ 配图（任意 OpenAI 兼容的图片生成 API）一站式生成
- **自动发布** — 上传图片、填写标题/正文/话题、点击发布，全程自动
- **全自动流水线** — 热点 → 选题 → 生成 → 预览 → 发布，一条命令搞定

## 前置条件

- macOS 或 Linux
- 已安装并配置 [OpenClaw](https://openclaw.ai)
- [uv](https://docs.astral.sh/uv/)（Python 包管理器）
- Google Chrome
- 一个 OpenAI 兼容的图片生成 API（如 OpenRouter、NanoBanana 或其他服务商）

## 安装

```bash
git clone https://github.com/pearl799/openclaw-skill-xhs.git
cd openclaw-skill-xhs
./install.sh
```

安装脚本会：
1. 将技能文件复制到 `~/.openclaw/skills/xhs/`
2. 安装 Python 依赖
3. 配置 `openclaw.json`（会提示你填写 API Key 等信息）

安装完成后，登录小红书（只需扫码一次）：
```bash
cd ~/.openclaw/skills/xhs/xhs-toolkit && \
uv run python ~/.openclaw/skills/xhs/scripts/xhs_login_persistent.py
```

然后重启 gateway：
```bash
openclaw gateway --force
```

## 使用方式（Telegram / Discord）

| 指令 | 功能 |
|------|------|
| 小红书热点 | 爬取当前热门话题 |
| 帮我生成一篇关于AI的小红书 | AI 生成文案 + 配图 |
| 发布 | 发布已生成的内容 |
| 小红书登录状态 | 检查登录状态 |
| 全自动发布 | 全流程：热点 → 生成 → 发布 |

## 配置

所有配置在 `~/.openclaw/openclaw.json` 的 `skills.entries.xhs.env` 下：

| 变量 | 必填 | 说明 |
|------|------|------|
| `IMAGE_API_KEY` | 是 | 图片生成 API Key（任意 OpenAI 兼容的服务商） |
| `IMAGE_BASE_URL` | 是 | 图片生成 API 地址（如 `https://openrouter.ai/api/v1/chat/completions`） |
| `IMAGE_MODEL` | 是 | 图片生成模型名称（如 `google/gemini-3-pro-image-preview`） |
| `XHS_TOOLKIT_DIR` | 自动 | 安装脚本自动设置 |
| `XHS_COOKIES_FILE` | 自动 | 安装脚本自动设置 |
| `OPENCLAW_GATEWAY_TOKEN` | 自动 | 从 gateway 配置中自动检测 |

## 卸载

```bash
cd openclaw-skill-xhs
./uninstall.sh
```

## 常见问题

**每次都要扫码登录**
- 确认 `XHS_CHROME_PROFILE` 指向一个持久化目录
- 杀掉残留的 Chrome 进程：`pkill -f chrome-data`

**发布失败**
- 先检查登录状态：发送「小红书登录状态」
- 如果已过期，重新登录：运行 `xhs_login_persistent.py`

**图片生成失败**
- 检查 `IMAGE_API_KEY`、`IMAGE_BASE_URL`、`IMAGE_MODEL` 是否正确配置在 `openclaw.json` 中
- 脚本会自动重试最多 3 次

**Chrome 无法启动**
- 杀掉残留进程：`pkill -f chrome-data`
- 确认 Chrome 路径：`ls "/Applications/Google Chrome.app/"`（macOS）

## 许可证

MIT
