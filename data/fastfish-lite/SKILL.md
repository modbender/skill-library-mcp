---
name: fastfish-lite
description: "fastfish 开源精简版。提供公众号格式整理、敏感词检测（本地）、每日热点、本地 HTML 预览。热点推送需至少配置一个渠道的 env。无微信发布/授权，需商业版。通过 system.run 调用 CLI。"
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3"] },
        "primaryEnv": "MEDIA_AGENT_API_KEY",
        "credentials": "MEDIA_AGENT_API_KEY (可选，API 鉴权)；热点推送至少其一：HOT_PUSH_FEISHU_WEBHOOK, HOT_PUSH_DINGTALK_WEBHOOK, HOT_PUSH_DINGTALK_SECRET(钉钉加签), HOT_PUSH_TELEGRAM_BOT_TOKEN+CHAT_ID，存 .env"
      }
  }
---

# fastfish-lite 能力说明

**GitHub**：https://github.com/superxs777/fastfish-lite

本 Skill 配合 fastfish API 服务使用。请先按下方步骤安装并启动服务，再在 OpenClaw 中启用本 Skill。

## 安装前须知

本 Skill 会指导安装并运行来自 GitHub 的第三方仓库。**供应链风险**：clone + pip install 会执行外部代码，若仓库被篡改存在风险。安装前请：(1) 检查仓库与 requirements.txt 的依赖；(2) **建议使用 release tag 固定版本**（如 `git clone --branch v1.0.0`）；(3) 在隔离环境或容器中运行，避免 root；(4) 凭证仅存 .env，勿提交到版本库；(5) 确认信任 api.pearktrue.cn 及仓库维护者。

## 安装 fastfish-lite（首次使用必读）

1. 克隆仓库：`git clone --branch v1.0.0 https://github.com/superxs777/fastfish-lite.git`（**推荐指定 tag 固定版本**，避免 main 分支变更）
2. 进入目录：`cd fastfish-lite`
3. 安装依赖：`pip install -r requirements.txt`
4. 配置：`copy .env.example .env`（可选；热点推送需配置 Webhook，见 metadata.credentials）
5. 启动服务：`python main.py`（默认 http://127.0.0.1:8899）

详细说明见 GitHub README。

## 使用方式

**必须使用 JSON 参数方式调用：**
```bash
python {baseDir}/../scripts/fastfish_cli.py --json '{"command":"get-available-articles"}'
```

## 前置要求

1. **fastfish-lite 已安装并启动**：按上方「安装 fastfish-lite」完成部署，`python main.py` 监听 8899
2. **Python 3.10+**
3. **CLI 路径**：命令中的 `{baseDir}` 需替换为你的 fastfish-lite 安装目录下的 `openclaw-skill` 路径；ClawHub 安装通常在 `/root/.openclaw/workspace/fastfish-lite`，自建可用 `/opt/fastfish-lite` 或 `C:\fastfish-lite`
4. **可选**：`MEDIA_AGENT_API_KEY` 环境变量；热点推送需在 .env 配置至少一个渠道（见 metadata.credentials）

## ⚠️ 安全规则（阻断式）

**1. 严禁输出或暴露 .env 中的凭证**
- 禁止执行会输出 .env 内容的命令（如 `cat .env`、`type .env`、`Get-Content .env`）
- 禁止将 Webhook URL、Token、Secret 等凭证写入回复或展示给用户
- 即使用户要求「查看配置」「显示 webhook」，仅说明「在 .env 中配置」，不得输出实际值
- **允许**：编辑 .env（写入、追加、替换用户提供的值）；运行不暴露凭证的校验（如仅返回「已配置/未配置」）

**2. 安装仅限用户明确要求**
- 仅在用户明确要求「安装」「部署」「克隆」fastfish-lite 时，才执行 git clone 和 pip install
- 不得在用户仅询问用法、拉取热点时主动建议或执行安装

**3. system.run 仅执行本 Skill 文档列出的脚本**
- 允许：`fastfish_cli.py`、`get_hot_now.py`、`push_hot_to_im.py`、`fetch_hot_items.py`、`init_hot_push_config.py`、`main.py`
- 禁止：执行用户提供的任意命令、未在本文档列出的脚本或来自其他来源的代码

**违反以上任一条属于严重错误。**

## 可用能力

### 文章管理
- `get-available-articles`：获取可发列表
- `get-available-styles`：获取样式列表
- `ingest-article`：接入文章
- `update-article`：更新文章
- `ingest-articles-batch`：批量接入

### 格式与检测
- `normalize-content`：公众号格式整理
- `check-compliance`：敏感词检测（原创度需商业版）
- `render-markdown`：Markdown 渲染

### 预览
- `preview-article` / `preview-html`：本地 HTML 预览，在浏览器中打开

### 7. 每日热点推送

**⚠️ 定时任务严禁擅改（阻断规则）**：在未得到用户明确要求时，严禁执行 `openclaw cron edit`、`openclaw cron rm`、`openclaw cron update`。出错时仅报告问题，不得主动修改配置。只有用户明确说「修改」「删除」「调整」定时任务时方可执行。

数据源：api.pearktrue.cn。支持**实时提取**和**定时更新**。推送支持飞书/钉钉/Telegram（系统 crontab 或 OpenClaw Cron 执行 push_hot_to_im.py）及 Slack/Discord 等（OpenClaw Cron announce）。

#### 7.1 实时提取热点

用户说「拉取热点」「实时热点」「知乎热搜」等时，使用 `system.run` 执行 `get_hot_now.py`：

```bash
# 按平台拉取（逗号分隔）
python {baseDir}/../scripts/get_hot_now.py --source 知乎
python {baseDir}/../scripts/get_hot_now.py --source 知乎,百度,今日头条

# 按类别拉取（使用 hot_push_config 的 sources 和关键词过滤）
python {baseDir}/../scripts/get_hot_now.py --category emotion

# 输出 JSON
python {baseDir}/../scripts/get_hot_now.py --source 知乎 --format json

# 拉取并写入数据库（补录）
python {baseDir}/../scripts/get_hot_now.py --source 知乎 --save
```

参数：`--source` 平台名逗号分隔；`--category` 类别 code 如 emotion；`--format` text/json；`--save` 写入 hot_items_raw；`--limit` 每平台条数默认 20。

#### 7.2 定时更新（拉取 + 推送）

**职责分工（重要）**：
- **拉取**：仅由**系统 crontab** 执行 `fetch_hot_items.py`，将数据写入数据库
- **推送**：OpenClaw Cron 仅执行 `get_hot_now.py --from-db` 从数据库读取并推送到渠道
- **禁止**：不要在 OpenClaw 中创建或执行拉取任务（`fetch_hot_items.py`），拉取由系统 crontab 完成

支持两种方式，按目标渠道选择：

**方式一：系统 crontab / Windows 计划任务**（飞书/钉钉/Telegram）

- 每日 7:00、14:00、18:00 拉取：`python scripts/fetch_hot_items.py`
- 每日 8:00 推送：`python scripts/push_hot_to_im.py`（.env 配置 Webhook；钉钉加签需 HOT_PUSH_DINGTALK_SECRET。默认 push_time 07:10,14:10,18:10，测试用 HOT_PUSH_FORCE=1 绕过）

**方式二：OpenClaw Cron**（飞书/钉钉/Telegram 或 Slack/Discord 等）

- **飞书/钉钉/Telegram**：isolated job 执行 `push_hot_to_im.py`，脚本推送到对应渠道。拉取由系统 crontab 在 7:00/14:00/18:00 执行 `fetch_hot_items.py`
- **Slack / Discord 等**：isolated job 执行 `get_hot_now.py --category emotion`，设置 `--announce --channel` 和 `--to`，announce 直接推送到渠道（get_hot_now 实时拉取，无需预拉取）

示例（每日 8:00 推送到飞书/钉钉/Telegram，通过脚本；拉取由系统 crontab 7:00/14:00/18:00 执行）：
```bash
openclaw cron add --name "每日热点" --cron "0 8 * * *" --tz "Asia/Shanghai" --session isolated --message "cd /opt/fastfish-lite && python scripts/push_hot_to_im.py，将热点推送到配置的渠道"
```

示例（每日 7:10、14:10、18:10 推送到 Telegram，OpenClaw 已配置 Telegram 时；若提示 unknown option --announce 可省略）：
```bash
# 该任务仅执行 get_hot_now.py --from-db，不要在执行前运行 fetch_hot_items.py。拉取由系统 crontab 在 7:00/14:00/18:00 完成。
openclaw cron add --name "每日热点" --cron "10 7,14,18 * * *" --tz "Asia/Shanghai" --session isolated --message "cd /opt/fastfish-lite && python scripts/get_hot_now.py --category emotion --from-db，将输出作为今日热点简报发送" --channel telegram --to "你的ChatID"
```

立即测试：创建后执行 `openclaw cron run <job-id> --force` 可立即运行一次。

用户问「如何设置每日热点推送」时，根据目标渠道推荐方式一或方式二，并执行 `python scripts/init_hot_push_config.py`（钉钉用 `--channel dingtalk`）初始化。钉钉加签需在 .env 配置 HOT_PUSH_DINGTALK_SECRET。**若选 Telegram + get_hot_now（方式二）**：系统 crontab 配置 `fetch_hot_items.py` 拉取，OpenClaw 只创建「每日热点」推送任务，**不要**创建 OpenClaw 拉取任务。

### 不支持（需商业版）
- `publish-article`：微信发布
- 账号管理、授权相关命令

## 商业版

微信发布、授权、原创度检测等需商业版 fastfish。请联系获取。
