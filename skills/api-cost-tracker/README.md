# API Cost Tracker 💰

[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-green)](https://nodejs.org/)

> **Track AI API costs across OpenAI, Anthropic, Google AI with budget alerts and analytics**

The first comprehensive API cost tracking skill for OpenClaw. Monitor your AI spending, set budgets, get alerts, and optimize costs.

## ✨ Features

- ✅ **Multi-Provider Support** - OpenAI, Anthropic, Google AI
- ✅ **Real-Time Tracking** - Monitor costs as they happen
- ✅ **Budget Alerts** - Get notified when approaching limits
- ✅ **Usage Analytics** - Detailed insights into API usage
- ✅ **Cost Optimization** - AI-powered tips to reduce spending
- ✅ **Export Reports** - JSON, CSV, Markdown formats
- ✅ **Historical Data** - Track costs over time
- ✅ **Model Comparison** - Compare costs across models
- ✅ **Zero Dependencies** - Lightweight and fast
- ✅ **Easy Integration** - Works with OpenClaw agents

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/api-cost-tracker.git
cd api-cost-tracker
```

### Basic Usage

```bash
# Track current costs
npm start

# Check budget status
npm run budget

# Generate report
npm run report

# Get optimization tips
npm run optimize

# Run tests
npm test
```

## 📊 Example Output

### Cost Tracking
```
💰 API Cost Tracker

Total Cost: $23.45

By Provider:
  openai: $14.80
  anthropic: $8.20
  google: $0.45

By Model:
  openai/gpt-4: $12.50
  openai/gpt-3.5-turbo: $2.30
  anthropic/claude-3-sonnet: $8.20
```

### Budget Status
```
💵 Budget Status

✅ daily: $23.45 / $10 (234.5%)
🔶 weekly: $23.45 / $50 (46.9%)
✅ monthly: $23.45 / $200 (11.7%)
```

### Optimization Tips
```
💡 Optimization Tips

1. [HIGH] Consider using GPT-3.5 Turbo for simpler tasks. Current GPT-4 spend: $12.50
   Potential savings: $8.38
```

## 🎯 Use Cases

1. **Monitor Spending** - Track API costs in real-time
2. **Budget Management** - Set and enforce budget limits
3. **Cost Optimization** - Get AI-powered suggestions to reduce costs
4. **Team Reporting** - Export detailed cost reports
5. **Model Comparison** - Compare costs across different AI models
6. **Historical Analysis** - Review spending trends over time

## 🔧 Configuration

Edit `config.json` to customize:

```json
{
  "budgets": {
    "daily": 10,
    "weekly": 50,
    "monthly": 200
  },
  "alerts": {
    "enabled": true,
    "thresholds": [50, 75, 90, 100]
  }
}
```

## 📈 Pricing Reference

### OpenAI (per 1K tokens)
- **GPT-4:** $0.03 (input) / $0.06 (output)
- **GPT-4 Turbo:** $0.01 / $0.03
- **GPT-3.5 Turbo:** $0.0005 / $0.0015

### Anthropic (per 1K tokens)
- **Claude-3 Opus:** $0.015 / $0.075
- **Claude-3 Sonnet:** $0.003 / $0.015
- **Claude-3 Haiku:** $0.00025 / $0.00125

### Google AI (per 1K tokens)
- **Gemini Pro:** $0.00025 / $0.0005
- **Gemini Ultra:** $0.0025 / $0.0075

## 🔗 Integration with OpenClaw

Add to your `HEARTBEAT.md` for automated tracking:

```markdown
Every 6 hours:
- Run: node /path/to/api-cost-tracker/scripts/main.mjs track
- Alert if budget > 75%
```

### Automated Budget Monitoring

```bash
# Add to crontab
0 */6 * * * cd /path/to/api-cost-tracker && npm start
```

## 🧪 Testing

All tests passing ✅

```bash
npm test

🧪 Running API Cost Tracker Tests
✅ GPT-4 cost calculation correct
✅ Total cost calculated
✅ OpenAI costs tracked
✅ Anthropic costs tracked
✅ Budget monitoring works
✅ Optimization tips generated
```

## 📁 Project Structure

```
api-cost-tracker/
├── scripts/
│   └── main.mjs          # Core tracking logic
├── tests/
│   └── test.mjs          # Test suite
├── docs/                 # Documentation
├── references/           # Reference materials
├── data/                 # Cost data (auto-generated)
├── SKILL.md              # OpenClaw skill metadata
├── package.json
├── config.json           # Configuration
└── README.md             # This file
```

## 🛠️ Advanced Features

### Export Reports

```bash
# Markdown
node scripts/main.mjs report --markdown > report.md

# CSV
node scripts/main.mjs report --csv > costs.csv

# JSON
node scripts/main.mjs report --json > data.json
```

### Historical Analysis

```bash
# View last 30 days
node scripts/main.mjs history --days 30
```

### Custom Budget Periods

```javascript
const tracker = new APICostTracker({
  budgets: {
    hourly: 1,
    daily: 10,
    weekly: 50,
    monthly: 200
  }
});
```

## 🗺️ Roadmap

- [ ] More providers (Cohere, AI21, Hugging Face)
- [ ] Real-time dashboard (web UI)
- [ ] Team cost sharing
- [ ] Custom pricing rules
- [ ] Predictive analytics
- [ ] Slack/Discord notifications
- [ ] Cost allocation by project

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines.

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

Free for personal and commercial use.

## 🙏 Acknowledgments

- Built for [OpenClaw](https://github.com/openclaw/openclaw)
- Inspired by the need for better AI cost tracking
- Community-driven development

## 📞 Support

- **GitHub Issues:** [Report a bug](https://github.com/YOUR_USERNAME/api-cost-tracker/issues)
- **OpenClaw Discord:** [Join community](https://discord.gg/clawd)
- **Documentation:** [Full docs](https://github.com/YOUR_USERNAME/api-cost-tracker/wiki)

---

**Made with ❤️ for the OpenClaw community**

**Star ⭐ this repo if you find it useful!**
