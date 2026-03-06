<p align="center">
    <img src="https://raw.githubusercontent.com/QiaoTuCodes/openclaw-skill-session-memory/main/assets/openclaw-skill-logo.png" alt="OpenClaw Skill" width="500">
</p>

<p align="center">
  <strong>📝 Session Memory Skill for OpenClaw</strong>
</p>

<p align="center">
  <a href="https://github.com/QiaoTuCodes/openclaw-skill-session-memory/releases"><img src="https://img.shields.io/github/v/release/QiaoTuCodes/openclaw-skill-session-memory?include_prereleases&style=for-the-badge" alt="GitHub release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
</p>

An intelligent conversation memory skill for OpenClaw that automatically records dialogue content, stores it by date, and supports fast keyword-based search with data privacy protection.

## ✨ Features

- 📝 **Auto Recording** - Automatically save conversation logs after each session
- 📅 **Date-based Storage** - Store conversations in `memory/conversations/YYYY-MM-DD.md`
- 🔍 **Fast Search** - Keyword regex search without loading entire files
- 🔒 **Data Privacy** - Auto-redact sensitive info (emails, phones, API keys, tokens, etc.)
- 🚀 **Quick Recall** - Pattern matching for instant context retrieval

## 📦 Installation

```bash
# Clone this skill to your OpenClaw workspace
cp -r openclaw-skill-session-memory ~/openclaw-workspace/skills/
```

## 🚀 Quick Start

### Auto Record (After Each Session)

The skill automatically calls `record.py` to save conversations.

### Manual Search

```bash
# Search by keyword (default: last 7 days)
python3 search.py "keyword"

# Search within specified days
python3 search.py "keyword" --days 30

# List all conversation files
python3 search.py --list
```

### Record Manually

```bash
python3 record.py
```

## 📖 Documentation

- [中文文档](README-CN.md)
- [技能定义](SKILL.md)

## 🔧 Requirements

- Python 3.7+

## 📂 Project Structure

```
openclaw-skill-session-memory/
├── SKILL.md           # OpenClaw skill definition
├── skill.py           # Main Python module
├── record.py          # Conversation recorder
├── search.py          # Fast search tool
├── README.md          # English documentation
├── README-CN.md       # Chinese documentation
├── LICENSE            # MIT License
└── .gitignore
```

## 🔒 Privacy Protection

Automatically redacts:
- Email addresses → `[EMAIL]`
- Phone numbers → `[PHONE]`
- API Keys/Tokens → `[API_KEY]`, `[REDACTED]`
- ID card numbers → `[ID_CARD]`
- Bank card numbers → `[CARD]`
- IP addresses → `[IP]`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

## 👥 Authors

- **焱焱 (Yanyan)** - AI Assistant running on OpenClaw

---

<p align="center">
  <sub>Built with ❤️ for the OpenClaw community</sub>
</p>
