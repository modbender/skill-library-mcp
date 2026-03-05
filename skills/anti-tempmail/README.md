# AntiTempMail OpenClaw Skill

[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Validate email addresses against temporary/disposable email providers using the [AntiTempMail](https://antitempmail.com) API.

## 🚀 Quick Start

### 1. Install the Skill

```bash
# Clone to your OpenClaw skills directory
cd ~/.openclaw/skills
git clone https://github.com/EricMymj/antitempmail-skill.git antitempmail
```

### 2. Set Your API Key

Get your API key from [AntiTempMail Dashboard](https://antitempmail.com/dashboard), then:

```bash
export ANTITEMPMAIL_API_KEY="your_api_key_here"
```

Or add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
echo 'export ANTITEMPMAIL_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Use with OpenClaw

Just ask your OpenClaw assistant:

> "Check if test@tempmail.com is a temporary email"

> "Validate these emails: user1@gmail.com, user2@10minutemail.com"

> "Is this email address legitimate: john@example.com?"

## 📖 Features

- ✅ Single email validation
- ✅ Bulk email checking (up to 100 emails)
- ✅ Risk scoring (low/medium/high)
- ✅ Provider detection
- ✅ Confidence scoring
- ✅ Rate limit handling

## 🔧 Manual Usage

See [SKILL.md](SKILL.md) for detailed API documentation and curl examples.

## 📊 API Limits

| Tier | Requests/Day | Price |
|------|--------------|-------|
| Free | 100 | $0 |
| Pro | 10,000 | $9/mo |
| Enterprise | Custom | Contact |

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Links

- [AntiTempMail Website](https://antitempmail.com)
- [API Documentation](https://antitempmail.com/docs)
- [OpenClaw Documentation](https://docs.openclaw.ai)
- [Report Issues](https://github.com/EricMymj/antitempmail-skill/issues)
