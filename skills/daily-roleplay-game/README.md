# Daily Roleplay Game — AI 每日职业角色扮演系统

AI 驱动的每日职业角色扮演引擎。每天自动生成新角色（职业+年龄+五维性格+隐藏性癖），通过三级暗示系统引导猜测，支持多种生图后端（ComfyUI / SD WebUI / Midjourney / Nano Banana Pro）实时生成角色图片。

## Features

- **138+ 职业库**：13 大分类（医疗、教育、法律、执法、商务、文化、服务、科技、体育、餐饮、时尚、旅行、特殊幻想）
- **131 个性癖**：6 类（敏感带/行为偏好/穿着癖好/体质反应/特殊嗜好/情境场合），每日 3~5+1 随机抽取
- **五维性格生成**：职业维度/自我/本我/超我/NSFW 性格，每日独特人设
- **三级暗示系统**：6-12 时极隐晦 → 12-18 时中等 → 18-24 时明显
- **主题日/倾向日**：被动日、主动日、身体反应日、职业深度日，日历联动
- **年龄系统**：18-40 岁随机，影响外形/打扮/心态/性经验/台词风格
- **职业+年龄加权**：不同职业和年龄对性癖抽取产生倾向性影响
- **稀有性癖**：15% 概率触发替换，增加惊喜感
- **性癖组合联动**：成对性癖触发组合暗示文案
- **成就系统**：通关次数、连胜加成、职业探索等成就追踪
- **多后端生图**：支持 ComfyUI / SD WebUI / Midjourney / Nano Banana Pro，自动生成角色自拍、脱衣照、惩罚照
- **自动收尾归档**：23:30 自动归档当日所有数据和图片

## Quick Start

### 方式 1：ClawHub 安装（推荐）

```bash
# 安装 skill
clawhub install daily-roleplay-game

# 部署（自动创建 role-play agent + workspace，不影响现有 agent）
./skills/daily-roleplay-game/scripts/setup.sh
```

### 方式 2：Git Clone

```bash
# Clone 仓库
git clone https://github.com/nannyu/openclaw-role-play-skill.git
cd openclaw-role-play-skill

# 部署（自动创建 role-play agent + workspace）
./scripts/setup.sh
```

### 部署后配置

```bash
cd ~/.openclaw/workspace-role-play

# 编辑以下文件：
# IDENTITY.md — 角色名称和时区
# USER.md     — 你的个人信息
# MEMORY.md   — 消息频道（discord/telegram/feishu/last）
# TOOLS.md    — 生图工具（不需要可填「无」）
```

详细部署指南见 [docs/OPENCLAW_SETUP.md](docs/OPENCLAW_SETUP.md)。

## Repository Structure

```
openclaw-role-play-skill/
├── SKILL.md                  # Skill 入口（ClawHub / OpenClaw）
├── README.md                 # 本文件
├── openclaw.example.json5    # OpenClaw 配置参考
│
├── engine/                   # 核心引擎（部署到 workspace 根目录）
│   ├── ENGINE.md             # 运行时规则 + 生成器操作手册
│   ├── AGENTS.md             # Agent 启动顺序与行为规范
│   ├── HEARTBEAT.md          # 心跳规则
│   └── SOUL.md               # 角色人格核心（可自定义）
│
├── data/                     # 游戏数据
│   ├── index.yaml            # 数据索引与生成逻辑
│   ├── age_profiles.yaml     # 年龄档案
│   ├── achievements.yaml     # 成就系统配置
│   ├── holidays_china.json   # 中国节假日
│   ├── professions/          # 职业库（13 类 YAML）
│   ├── kinks/                # 性癖库（A-F 六类 + synergies + overrides）
│   ├── themes/               # 主题日配置
│   ├── personality/          # 五维性格生成数据
│   ├── weights/              # 职业+年龄性癖加权
│   └── templates/            # 早安模板 + 生图配置
│
├── scripts/                  # 可执行脚本
│   ├── setup.sh              # 一键部署（自动创建 agent + workspace）
│   ├── wrapup.sh             # 23:30 收尾归档
│   └── validate-generation.sh # 生成器输出验证
│
├── templates/                # 运行时文件模板（setup.sh 使用）
│   ├── history_tracker.json
│   ├── achievement_tracker.json
│   ├── kink_game_enabled.json
│   ├── USER.md
│   ├── MEMORY.md
│   ├── TOOLS.md
│   └── IDENTITY.md
│
└── docs/                     # 设计文档
    ├── OPENCLAW_SETUP.md     # OpenClaw 部署指南
    ├── CRON_CONFIG.md        # 定时任务配置
    ├── WRAPUP.md             # 收尾流程说明
    ├── daily-roleplay-game.md
    └── kinks-improvement-suggestions.md
```

## Customization Guide

| 文件 | 用途 | 建议 |
|------|------|------|
| `engine/SOUL.md` | 角色人格 | 自定义角色性格、口癖 |
| `templates/IDENTITY.md` | 角色身体数据 | 自定义外貌、体质设定 |
| `templates/USER.md` | 主人信息 | 填写你的称呼和偏好 |
| `data/professions/*.yaml` | 职业库 | 添加新职业 |
| `data/kinks/category_*.yaml` | 性癖库 | 添加新性癖 |
| `data/achievements.yaml` | 成就配置 | 自定义成就和奖励 |
| `data/themes/daily_themes.yaml` | 主题日 | 添加自定义主题 |

## Requirements

- **AI Agent**：支持 OpenClaw 等可读写文件的 AI agent
- **生图工具**（可选）：ComfyUI / SD WebUI / Midjourney / Nano Banana Pro（任选其一，在 TOOLS.md 中配置）
- **消息平台**（可选）：Discord / Telegram / 飞书等 OpenClaw 支持的任意消息平台
- **Python 3**（可选）：wrapup.sh 的成就追踪功能使用

## License

Private use. Do not redistribute without permission.
