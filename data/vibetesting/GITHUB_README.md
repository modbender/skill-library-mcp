# 🧪 VibeTesting

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://github.com/senthazalravi/vibetesting)
[![Version](https://img.shields.io/badge/Version-1.0.0-green)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)]()

**Browser automation testing skill for OpenClaw** - Perform functional, accessibility, performance, visual, and security testing on any website.

## ✨ Features

- 🔍 **Functional Testing** - Analyze forms, inputs, buttons, and links
- ♿ **Accessibility Testing** - WCAG 2.1 compliance checks (A, AA, AAA)
- ⚡ **Performance Testing** - Page load time, size, and Core Web Vitals
- 🎨 **Visual Testing** - Color palette, layout, and responsive design analysis
- 🔒 **Security Testing** - HTTPS, CSP, and vulnerability scanning
- 🔄 **E2E Testing** - User journeys and workflow testing

## 🚀 Quick Start

### Installation

This skill is available in ClawHub. Just tell OpenClaw what to test:

```
[VibeTesting]
target_url: https://example.com
testing_type: quick
```

### Basic Usage

```markdown
[VibeTesting]
target_url: https://mysite.com
testing_type: comprehensive
```

### Test a Specific Feature

```markdown
[VibeTesting]
target_url: https://myapp.com
testing_type: accessibility
wcag_level: AA
```

## 📖 Documentation

- **[SKILL.md](SKILL.md)** - Complete technical documentation
- **[README.md](README.md)** - User guide and examples
- **[EXAMPLES.md](EXAMPLES.md)** - Configuration examples

## 🎯 Test Types

| Type | Duration | Description |
|------|----------|-------------|
| `quick` | 5-10s | Fast smoke test |
| `functional` | 30-60s | Full functionality check |
| `comprehensive` | 2-5min | Everything included |
| `accessibility` | 1-2min | WCAG compliance audit |
| `performance` | 30-60s | Speed and metrics |
| `visual` | 1-2min | Layout and design |
| `security` | 30-60s | Vulnerability scan |
| `e2e` | Varies | User journey testing |

## 📊 Example Results

```
🚀 VibeTesting starting...
📍 Target: https://example.com
🧪 Test Type: comprehensive

✅ Testing complete!
⏱️  Duration: 12.34s
📊 Score: 85/100

📄 HTML report saved to: vibetesting-report.html
```

## 🛠️ Installation & Setup

### Prerequisites

- Node.js 14+
- OpenClaw Gateway running
- Network access (for testing external URLs)

### Manual Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/vibetesting.git
cd vibetesting
```

2. Install dependencies (if any):
```bash
npm install
```

3. Test locally:
```bash
npm test
```

## 📁 Project Structure

```
vibetesting/
├── 📄 index.js           # Main testing framework
├── 📄 SKILL.md           # Technical documentation
├── 📄 README.md          # User guide
├── 📄 EXAMPLES.md        # Configuration examples
├── 📄 package.json       # Package metadata
├── 📄 publish.sh         # Publishing script
├── 📄 PUBLISHING.md      # Publishing guide
└── 📄 .gitignore         # Git ignore rules
```

## 🔧 Configuration

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `target_url` | Yes | - | URL to test |
| `testing_type` | No | `comprehensive` | Type of test |
| `include` | No | All | Categories to include |
| `exclude` | No | None | Categories to skip |
| `report_format` | No | `html` | Output format |
| `headless` | No | `true` | Run without browser UI |
| `viewport` | No | `1920x1080` | Browser size |
| `timeout` | No | `60` | Test timeout (seconds) |
| `wcag_level` | No | `AA` | WCAG compliance level |

### Example Configuration

```json
{
  "target_url": "https://myshop.com",
  "testing_type": "comprehensive",
  "include": ["functional", "accessibility", "performance"],
  "report_format": "html",
  "viewport": { "width": 1920, "height": 1080 },
  "wcag_level": "AA"
}
```

## 📈 Scoring

All test categories receive a score from 0-100:

- **90-100** ✅ Excellent
- **70-89** ⚠️ Good  
- **50-69** 🔶 Needs Improvement
- **0-49** ❌ Poor

## 🔒 Security

- ✅ Tests with permission only
- ✅ Respects rate limits
- ✅ No credential storage
- ✅ Safe for CI/CD

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation:** See [SKILL.md](SKILL.md)
- **Examples:** See [EXAMPLES.md](EXAMPLES.md)
- **Issues:** [GitHub Issues](https://github.com/senthazalravi/vibetesting/issues)
- **Discord:** [OpenClaw Community](https://discord.gg/clawd)
- **Email:** ravi.antone@gmail.com

## 🙏 Acknowledgments

- [OpenClaw](https://github.com/openclaw/openclaw) - The amazing platform this skill is built for
- [TestFox](https://github.com/senthazalravi/TestFox) - The parent project
- All contributors and testers!

---

**Happy Testing!** 🧪🔍✨

Made with ❤️ by the VibeTesting Team
