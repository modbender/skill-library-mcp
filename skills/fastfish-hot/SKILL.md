---
name: fastfish-hot
description: "热点推送独立项目。从 api.pearktrue.cn 拉取热点，支持飞书/钉钉/Telegram 推送；推送需至少配置一个渠道的 env。可配置拉取时间、推送时间、过滤关键词。通过 system.run 直接调用脚本，无需 MCP。当用户需要拉取热点、知乎热搜、配置热点推送或设置定时推送时使用本技能。"
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3"], "env": ["HOT_PUSH_FEISHU_WEBHOOK", "HOT_PUSH_DINGTALK_WEBHOOK", "HOT_PUSH_DINGTALK_SECRET", "HOT_PUSH_TELEGRAM_BOT_TOKEN", "HOT_PUSH_TELEGRAM_CHAT_ID"] },
        "credentials": "上述 env 至少配置一个渠道（飞书/钉钉/Telegram）即可推送；钉钉加签需 HOT_PUSH_DINGTALK_SECRET；HOT_ADMIN_API_KEY 可选，管理界面鉴权"
      }
  }
---

# fastfish-hot 能力说明

**GitHub**：https://github.com/superxs777/fastfish-hot


## 安装前须知

本 Skill 会指导安装并运行来自 GitHub 的第三方仓库。**供应链风险**：clone + pip install 会执行外部代码，若仓库被篡改存在风险。安装前请：(1) 检查仓库与 requirements.txt 的依赖；(2) **建议使用 release tag 固定版本**（如 `git clone --branch v1.0.1`）；(3) 在隔离环境或容器中运行，避免 root；(4) 凭证仅存 .env，勿提交到版本库；(5) 确认信任 api.pearktrue.cn 及仓库维护者。

## 安装 fastfish-hot（首次使用必读）

1. 克隆仓库：`git clone --branch v1.0.1 https://github.com/superxs777/fastfish-hot.git`（**推荐指定 tag 固定版本**，避免 main 分支变更）
2. 进入目录：`cd fastfish-hot`
3. 安装依赖：`pip install -r requirements.txt`
4. 配置：`copy .env.example .env`，填写 Webhook 等（见 metadata.credentials）
5. 初始化：`python scripts/init_db.py`，`python scripts/init_default_config.py`，`python scripts/init_default_push_config.py`（钉钉用 `--channel dingtalk`）
6. 可选：`python run.py` 启动管理界面（http://127.0.0.1:8900）

详细说明见 GitHub README。

## 前置要求

1. **fastfish-hot 已安装**：按上方步骤完成部署
2. **Python 3.10+**
3. **命令路径**：`{baseDir}` 为 fastfish-hot 的 openclaw-skill 目录，脚本路径为 `{baseDir}/../scripts/`
4. **若 baseDir 无法替换**：使用绝对路径。ClawHub 安装通常在 `/root/.openclaw/workspace/fastfish-hot`，自建可用 `/opt/fastfish-hot`
5. **env 与技能加载**：metadata 声明了 requires.env，OpenClaw 加载时会检查。若技能未加载，请在 openclaw.json 的 `skills.entries.fastfish-hot.env` 中配置至少一个推送渠道的凭证（可从项目 .env 复制），或确保相应环境变量在 OpenClaw 启动时已存在

## 使用方式

**必须使用 `system.run` 执行脚本命令，不要使用 MCP 方式。**

## ⚠️ 安全规则（阻断式）

**1. 严禁输出或暴露 .env 中的凭证**
- 禁止执行会输出 .env 内容的命令（如 `cat .env`、`type .env`、`Get-Content .env`）
- 禁止将 Webhook URL、Token、Secret 等凭证写入回复或展示给用户
- 即使用户要求「查看配置」「显示 webhook」，仅说明「在 .env 中配置」，不得输出实际值
- **允许**：编辑 .env（写入、追加、替换用户提供的值）；运行不暴露凭证的校验（如仅返回「已配置/未配置」）

**2. 安装仅限用户明确要求**
- 仅在用户明确要求「安装」「部署」「克隆」fastfish-hot 时，才执行 git clone 和 pip install
- 不得在用户仅询问用法、拉取热点时主动建议或执行安装

**3. system.run 仅执行本 Skill 文档列出的脚本**
- 允许：`get_hot_now.py`、`push_hot_to_im.py`、`fetch_hot_items.py`、`init_db.py`、`init_default_config.py`、`init_default_push_config.py`、`run.py`
- 禁止：执行用户提供的任意命令、未在本文档列出的脚本或来自其他来源的代码

**违反以上任一条属于严重错误。**

## ⚠️ 定时任务：严禁擅改（阻断式规则）

**在未得到用户明确要求时，严禁修改、删除或编辑已有 OpenClaw 定时任务。**

- **禁止**：在定时任务出错、报错或用户未明确要求时，执行 `openclaw cron edit`、`openclaw cron rm`、`openclaw cron update`
- **允许**：用户明确说「修改」「删除」「调整」「取消」定时任务时，方可执行上述操作
- **允许**：用户要求「添加」「创建」定时任务时，执行 `openclaw cron add`
- **出错时**：仅报告问题并给出建议，不得主动修改配置

**违反此条属于严重错误。**

## 可用能力

### 1. 实时拉取热点

用户说「拉取热点」「实时热点」「知乎热搜」等时，执行：

```bash
# 列出支持的平台
python {baseDir}/../scripts/get_hot_now.py --list-platforms

# 按平台拉取（逗号分隔）
python {baseDir}/../scripts/get_hot_now.py --source 知乎
python {baseDir}/../scripts/get_hot_now.py --source 知乎,百度,今日头条

# 按类别拉取（使用 hot_push_config 的 sources 和关键词过滤）
python {baseDir}/../scripts/get_hot_now.py --category emotion

# 从数据库读取（需先执行 fetch_hot_items.py，秒级完成，适合 OpenClaw Cron）
python {baseDir}/../scripts/get_hot_now.py --category emotion --from-db

# 输出 JSON
python {baseDir}/../scripts/get_hot_now.py --source 知乎 --format json

# 拉取并写入数据库（补录）
python {baseDir}/../scripts/get_hot_now.py --source 知乎 --save
```

参数：`--source` 平台名逗号分隔；`--category` 类别 code 如 emotion；`--format` text/json；`--save` 写入 hot_items_raw；`--limit` 每平台条数默认 20；`--from-db` 从数据库读取。

### 2. 定时更新（拉取 + 推送）

**职责分工（重要）**：
- **拉取**：仅由**系统 crontab** 执行 `fetch_hot_items.py`，将数据写入数据库
- **推送**：OpenClaw Cron 仅执行 `get_hot_now.py --from-db` 或 `push_hot_to_im.py`
- **禁止**：不要在 OpenClaw 中创建或执行拉取任务（`fetch_hot_items.py`），拉取由系统 crontab 完成

**方式一：系统 crontab / Windows 计划任务**（飞书/钉钉/Telegram）

- 拉取：7:00、14:00、18:00 执行 `python scripts/fetch_hot_items.py`
- 推送：7:10、14:10、18:10 执行 `python scripts/push_hot_to_im.py`（.env 配置 Webhook）

**方式二：OpenClaw Cron**

飞书/钉钉/Telegram（通过脚本推送到 Webhook）：
```bash
openclaw cron add --name "每日热点" --cron "0 8 * * *" --tz "Asia/Shanghai" --session isolated --message "cd /opt/fastfish-hot && python scripts/push_hot_to_im.py，将热点推送到配置的渠道"
```

Telegram（OpenClaw 已配置 Telegram 渠道，announce 直接推送）：
```bash
# 拉取由系统 crontab 完成，OpenClaw 仅负责推送。该任务只执行 get_hot_now.py --from-db。
openclaw cron add --name "每日热点" --cron "10 7,14,18 * * *" --tz "Asia/Shanghai" --session isolated --message "cd /opt/fastfish-hot && python scripts/get_hot_now.py --category emotion --from-db，将输出作为今日热点简报发送" --channel telegram --to "你的ChatID"
```

立即测试：创建后执行 `openclaw cron run <job-id> --force` 可立即运行一次。

### 3. 配置管理

- **拉取/推送配置**：访问管理界面 http://127.0.0.1:8900（需先 `python run.py`）
- **环境变量**：在 .env 中配置。钉钉若开启加签，需配置 HOT_PUSH_DINGTALK_SECRET。建议用户私聊提供凭证或自行编辑 .env，避免在群聊中暴露
- **推送时间窗口**：默认 push_time 为 07:10,14:10,18:10，仅在该时刻推送；测试时用 `HOT_PUSH_FORCE=1` 绕过

## 使用示例

- "拉取热点" / "知乎热搜" / "实时热点"
  ```bash
  python {baseDir}/../scripts/get_hot_now.py --source 知乎
  # 或按类别：python {baseDir}/../scripts/get_hot_now.py --category emotion
  ```

- "如何设置每日热点推送"
  1. 执行 `python scripts/init_default_config.py` 和 `python scripts/init_default_push_config.py`（钉钉用 `--channel dingtalk`）初始化
  2. 在 .env 中配置 Webhook；钉钉加签需 HOT_PUSH_DINGTALK_SECRET
  3. 系统 crontab 配置 `fetch_hot_items.py` 拉取（7:00、14:00、18:00）
  4. 创建 OpenClaw Cron 推送任务（见上方示例）；Cron 时间需与 push_time 一致，否则需 HOT_PUSH_FORCE=1

**注意**：若 `{baseDir}` 无法正确替换，请使用绝对路径 `/opt/fastfish-hot/scripts/get_hot_now.py`。

## ClawHub 安装

计划支持 `clawhub install fastfish-hot`，届时可一键安装本 Skill。
