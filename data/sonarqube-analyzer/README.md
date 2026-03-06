# OpenClaw SonarQube Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen)](https://nodejs.org/)
[![OpenClaw Plugin](https://img.shields.io/badge/OpenClaw-Plugin-blue)](https://docs.openclaw.ai)

An **OpenClaw Plugin + CLI Skill** for automated SonarQube code quality analysis with intelligent issue detection and suggested solutions.

## 🎯 Dual Mode

This package works in **two modes**:

| Mode | Use Case | Installation |
|------|----------|--------------|
| **OpenClaw Plugin** | AI agents, automation, cron jobs | Add to `openclaw.json` |
| **CLI Tool** | Manual analysis, CI/CD scripts | `npm install -g` or `npx` |

## 🎯 Overview

This skill integrates with SonarQube self-hosted instances to:
- Fetch and analyze code quality issues
- Provide intelligent solutions based on SonarQube rules
- Generate actionable reports in JSON or Markdown
- Check Quality Gate status
- Distinguish between auto-fixable and manual-fix issues

## 🚀 Quick Start

### Mode 1: OpenClaw Plugin (Recommended for AI Agents)

Install as an OpenClaw plugin to use native tools (`sonar_get_issues`, `sonar_analyze_and_suggest`, `sonar_quality_gate`):

```bash
# Clone to your OpenClaw workspace
git clone https://github.com/FelipeOFF/sonarqube-analyzer.git \
  ~/.openclaw/workspace/skills/sonarqube-analyzer

# Install dependencies
cd ~/.openclaw/workspace/skills/sonarqube-analyzer
npm install
```

Add to your `~/.openclaw/openclaw.json`:

```json
{
  "plugins": {
    "load": {
      "paths": [
        "/home/YOUR_USER/.openclaw/workspace/skills/sonarqube-analyzer"
      ]
    },
    "entries": {
      "sonarqube-analyzer": {
        "enabled": true,
        "config": {
          "sonarHostUrl": "http://127.0.0.1:9000",
          "sonarToken": "your-token-here",
          "defaultProject": "my-project"
        }
      }
    }
  }
}
```

Then reload OpenClaw:
```bash
pkill -USR1 -f "openclaw gateway"
```

**Available Tools:**
- `sonar_get_issues(projectKey, pullRequest?)` — Fetch issues from SonarQube
- `sonar_analyze_and_suggest(projectKey, pullRequest?, autoFix?)` — Analyze with solutions
- `sonar_quality_gate(projectKey, pullRequest?)` — Check Quality Gate status

### Mode 2: CLI Tool (For Manual Use & CI/CD)

```bash
# Install globally
npm install -g @felipeoff/sonarqube-analyzer

# Or use with npx (no install)
npx @felipeoff/sonarqube-analyzer --project=my-project
```

Configure environment variables:
```bash
export SONAR_HOST_URL=http://127.0.0.1:9000
export SONAR_TOKEN=your-token-here
```

### Basic Usage

```bash
# Analyze a project
node scripts/analyze.js --project=my-project

# Analyze a specific PR
node scripts/analyze.js --project=my-project --pr=5

# Generate Markdown report
node scripts/analyze.js --project=my-project --pr=5 --format=markdown

# Check Quality Gate status
node scripts/analyze.js --project=my-project --pr=5 --action=quality-gate
```

## 📋 Features

### Issue Analysis
- Fetches all open issues from SonarQube
- Groups by severity (BLOCKER, CRITICAL, MAJOR, MINOR, INFO)
- Provides detailed context (file, line, rule, message)

### Intelligent Solutions
The skill includes a comprehensive rule database with:
- **Problem description**: Clear explanation of the issue
- **Solution**: Step-by-step fix instructions
- **Code examples**: Before/after code snippets
- **Auto-fixable flag**: Indicates if the fix can be automated

### Supported Rules

| Rule ID | Issue | Auto-fixable |
|---------|-------|--------------|
| `typescript:S6606` | Prefer nullish coalescing (`??`) over logical OR (`\|\|`) | ✅ Yes |
| `typescript:S6749` | Redundant fragment with single child | ✅ Yes |
| `typescript:S6759` | Props should be marked as `readonly` | ✅ Yes |
| `typescript:S6571` | Redundant `any` in union types | ✅ Yes |
| `typescript:S3358` | Nested ternary operations | ❌ No (requires refactoring) |
| `typescript:S3776` | High cognitive complexity | ❌ No (requires extraction) |

### Report Generation

**JSON Format** (default):
```json
{
  "totalIssues": 12,
  "autoFixable": {
    "count": 8,
    "issues": [...]
  },
  "manualFix": {
    "count": 4,
    "issues": [...]
  },
  "nextSteps": [
    "Apply auto-fixable issues",
    "Refactor nested ternaries",
    "Run lint and typecheck"
  ]
}
```

**Markdown Format**:
```markdown
# SonarQube Analysis: my-project (PR #5)

**Total Issues:** 12

- 🔧 Auto-fixable: 8
- 📝 Manual fix required: 4

## Next Steps
1. Apply 8 auto-fixable issues
2. Refactor nested ternaries in App.tsx
3. Run lint and typecheck after fixes
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SONAR_HOST_URL` | `http://127.0.0.1:9000` | SonarQube server URL |
| `SONAR_TOKEN` | `admin` | Authentication token |

### CLI Options

```
Options:
  --project=<name>    Project key in SonarQube (required)
  --pr=<number>       Pull request number (optional)
  --action=<type>     Action: analyze | report | quality-gate (default: analyze)
  --format=<type>     Output: json | markdown (default: json)
```

## 🔌 Architecture

```
sonarqube-analyzer/
├── scripts/
│   └── analyze.js          # CLI entry point
├── src/
│   ├── api.js              # SonarQube API client
│   ├── rules.js            # Rule definitions & solutions
│   ├── analyzer.js         # Issue analysis engine
│   └── reporter.js         # Report generators
├── tests/
│   └── *.test.js           # Unit tests
├── openclaw.plugin.json    # OpenClaw plugin manifest
├── SKILL.md                # OpenClaw skill documentation
├── README.md               # This file
└── package.json            # NPM manifest + OpenClaw config
```

**Dual-mode design:** The same codebase powers both the CLI tool and the OpenClaw plugin. The `openclaw.plugin.json` declares the tool schema, while `package.json` handles the CLI binary.

## 🧪 Testing

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test
npm test -- analyze.test.js
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for [OpenClaw](https://github.com/openclaw/openclaw)
- Inspired by SonarQube's code quality philosophy
- Thanks to the OpenClaw community for feedback and support

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/FelipeOFF/sonarqube-analyzer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/FelipeOFF/sonarqube-analyzer/discussions)
- **OpenClaw Docs**: https://docs.openclaw.ai

---

**Made with ❤️ for the OpenClaw community**