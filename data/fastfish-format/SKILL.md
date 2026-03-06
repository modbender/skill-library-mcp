---
name: fastfish-format
description: "多渠道格式化与美化：公众号、小红书文章排版，18 套预设样式，配图编排指引。不包含发布。通过 system.run 调用 CLI，无需 MCP。当用户需要公众号格式整理、小红书文案格式化、Markdown 渲染、样式选择或配图流程指引时使用本技能。"
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3"] },
        "credentials": "无必需凭证；配图/生图需对接 baoyu-skills 时，配置 OPENAI_API_KEY 或 GOOGLE_API_KEY 或 DASHSCOPE_API_KEY"
      }
  }
---

# fastfish-format 能力说明

**GitHub**：https://github.com/superxs777/fastfish-format

本 Skill 需配合 fastfish-format 项目使用。请先安装 fastfish-format，再在 OpenClaw 中启用本 Skill。

## 安装前须知

本 Skill 会指导安装并运行来自 GitHub 的第三方仓库。**供应链风险**：clone + pip install 会执行外部代码，若仓库被篡改存在风险。安装前请：(1) 检查仓库与 requirements.txt 的依赖；(2) **建议使用 release tag 固定版本**（如 `git clone --branch v0.1.0`）；(3) 在隔离环境或容器中运行，避免 root；(4) 凭证仅存 .env，勿提交到版本库。

## 安装 fastfish-format（首次使用必读）

1. 克隆仓库：`git clone --branch v0.1.0 https://github.com/superxs777/fastfish-format.git`（**推荐指定 tag 固定版本**）
2. 进入目录：`cd fastfish-format`
3. 安装依赖：`pip install -r requirements.txt` 或 `pip install -e .`
4. 可选：`pip install fastfish-format[api]` 启动 HTTP API 服务（默认 8900 端口）

详细说明见 GitHub README。

## 前置要求

1. **fastfish-format 已安装**：按上方步骤完成部署
2. **Python 3.10+**
3. **命令路径**：`{baseDir}` 为 fastfish-format 的 openclaw-skill 目录，脚本路径为 `{baseDir}/../scripts/`
4. **若 baseDir 无法替换**：使用绝对路径。ClawHub 安装通常在 `/root/.openclaw/workspace/fastfish-format`，自建可用 `/opt/fastfish-format` 或 `C:\fastfish-format`

## 使用方式

**必须使用 `system.run` 执行脚本命令，不要使用 MCP 方式。**

**必须使用 `--json` 参数方式调用**（避免多参数被 shell 拆行）：

```bash
python {baseDir}/../scripts/ffformat_cli.py --json '{"command":"normalize-wechat","content_file":"/tmp/article.txt"}'
```

## ⚠️ 安全规则（阻断式）

**1. 严禁输出或暴露 .env 中的凭证**
- 禁止执行会输出 .env 内容的命令
- 禁止将 API Key 等凭证写入回复或展示给用户
- **允许**：编辑 .env；运行不暴露凭证的校验

**2. 安装仅限用户明确要求**
- 仅在用户明确要求「安装」「部署」「克隆」fastfish-format 时，才执行 git clone 和 pip install
- 不得在用户仅询问用法时主动建议或执行安装

**3. system.run 仅执行本 Skill 文档列出的脚本**
- 允许：`ffformat_cli.py`
- 禁止：执行用户提供的任意命令、未在本文档列出的脚本

**违反以上任一条属于严重错误。**

## 可用能力

### 1. 公众号文本规范化

用户说「公众号格式」「按公众号规范整理」「公众号格式整理」等时，执行：

```bash
python {baseDir}/../scripts/ffformat_cli.py --json '{"command":"normalize-wechat","content_file":"/tmp/article.txt"}'
# 或短文本：python {baseDir}/../scripts/ffformat_cli.py --json '{"command":"normalize-wechat","content":"要点：1. 第一点 2. 第二点"}'
```

返回：`{"ok": true, "content": "整理后的 Markdown", "title": "主标题或 null"}`

### 2. 小红书文本规范化

用户说「小红书格式」「小红书文案整理」等时，执行：

```bash
python {baseDir}/../scripts/ffformat_cli.py --json '{"command":"normalize-xhs","content_file":"/tmp/xhs.txt"}'
```

返回：`{"ok": true, "content": "整理后的 Markdown"}`

### 3. Markdown 渲染为 HTML

用户说「渲染 Markdown」「Markdown 转 HTML」「美化文章」等时，执行：

```bash
python {baseDir}/../scripts/ffformat_cli.py --json '{"command":"render","content_file":"/tmp/article.md","format_style":"minimal"}'
```

format_style 可选：minimal、business、literary、phycat-cherry、phycat-sakura 等（见 styles 命令）。

### 4. 获取可用样式列表

用户说「有哪些样式」「样式列表」「选择样式」等时，执行：

```bash
python {baseDir}/../scripts/ffformat_cli.py --json '{"command":"styles"}'
```

返回样式列表（index、id、label），供用户按序号选择。

### 5. 配图流程指引

用户说「如何配图」「配图流程」「生图指引」等时，执行：

```bash
python {baseDir}/../scripts/ffformat_cli.py --json '{"command":"workflows"}'
```

返回 baoyu-skills 配图流程指引（文章配图、封面图、小红书信息图）。实际生图需安装 baoyu-skills 并配置图像生成 API。

## JSON 参数格式

所有命令通过 `--json` 传入，格式示例：

```json
{"command": "normalize-wechat", "content_file": "/tmp/article.txt"}
{"command": "normalize-wechat", "content": "短文本内容"}
{"command": "normalize-xhs", "content_file": "/tmp/xhs.txt"}
{"command": "render", "content_file": "/tmp/article.md", "format_style": "phycat-sakura"}
{"command": "styles"}
{"command": "workflows"}
```

- `command`：必填，命令名
- `content_file`：内容文件路径（推荐，避免 shell 转义）
- `content`：短文本内容（仅适合无换行、无特殊字符的短文本）
- `format_style`：样式名称，默认 minimal

## 使用示例

- "公众号格式整理" → `normalize-wechat` + content_file
- "小红书文案格式化" → `normalize-xhs` + content_file
- "用樱花粉样式渲染" → `render` + format_style: phycat-sakura
- "有哪些样式" → `styles`
- "配图流程" → `workflows`

**注意**：若 `{baseDir}` 无法正确替换，请使用绝对路径 `/opt/fastfish-format/scripts/ffformat_cli.py`。

## ClawHub 安装

计划支持 `clawhub install fastfish-format`，届时可一键安装本 Skill。
