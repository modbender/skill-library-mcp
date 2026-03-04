<p align="center">
    <img src="https://raw.githubusercontent.com/QiaoTuCodes/openclaw-skill-session-memory/main/assets/openclaw-skill-logo.png" alt="OpenClaw Skill" width="500">
</p>

<p align="center">
  <strong>📝 OpenClaw 会话记忆技能</strong>
</p>

<p align="center">
  <a href="https://github.com/QiaoTuCodes/openclaw-skill-session-memory/releases"><img src="https://img.shields.io/github/v/release/QiaoTuCodes/openclaw-skill-session-memory?include_prereleases&style=for-the-badge" alt="GitHub release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
</p>

智能会话记忆技能，自动记录对话内容，按日期存储，支持关键字快速搜索回忆，保护数据隐私。

## ✨ 功能特性

- 📝 **自动记录** - 每次会话结束后自动保存对话内容
- 📅 **按日期存储** - 保存在 `memory/conversations/YYYY-MM-DD.md`
- 🔍 **快速搜索** - 关键字正则匹配，无需加载整个文件
- 🔒 **数据脱敏** - 自动过滤邮箱、手机号、API Key、Token等敏感信息
- 🚀 **快速回忆** - 正则匹配关键数据，即时获取上下文

## 📦 安装

```bash
# 复制技能到你的OpenClaw工作区
cp -r openclaw-skill-session-memory ~/openclaw-workspace/skills/
```

## 🚀 快速开始

### 自动记录（会话结束后自动调用）

技能会在会话结束时自动调用 `record.py` 保存对话。

### 手动搜索

```bash
# 搜索关键字（默认最近7天）
python3 search.py "关键词"

# 搜索指定天数
python3 search.py "关键词" --days 30

# 列出所有会话文件
python3 search.py --list
```

### 手动记录

```bash
python3 record.py
```

## 🔧 系统要求

- Python 3.7+

## 📂 项目结构

```
openclaw-skill-session-memory/
├── SKILL.md           # OpenClaw技能定义
├── skill.py           # 主模块
├── record.py          # 会话记录器
├── search.py          # 快速搜索工具
├── README.md          # 英文文档
├── README-CN.md       # 中文文档
├── LICENSE            # MIT许可证
└── .gitignore
```

## 🔒 隐私保护

自动替换以下内容：
- 邮箱 → `[EMAIL]`
- 手机号 → `[PHONE]`
- API Key/Token → `[API_KEY]`, `[REDACTED]`
- 身份证号 → `[ID_CARD]`
- 银行卡号 → `[CARD]`
- IP地址 → `[IP]`

## 📜 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 👥 作者

- **焱焱 (Yanyan)** - 运行在OpenClaw上的AI助手

---

<p align="center">
  <sub>用 ❤️ 为 OpenClaw 社区打造</sub>
</p>
