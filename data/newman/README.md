# Newman Skill 🧪

> Production-ready Newman (Postman CLI) skill for automated API testing with gold-standard security practices

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/1999AZZAR/newman-skill/releases)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-orange.svg)](https://openclaw.ai)

## 🎯 What is This?

A comprehensive OpenClaw skill for running automated API tests using [Newman](https://github.com/postmanlabs/newman), the command-line Collection Runner for Postman. This skill includes production-ready scripts, security scanning, and CI/CD integration templates.

## ✨ Features

### 🔒 Security-First Design
- **Hardcoded secret detection** - Prevents API key leaks
- **SSL/TLS enforcement** - No insecure connections in production
- **Environment variable validation** - Ensures proper variable usage
- **PII exposure scanner** - Detects SSN, credit cards, etc.
- **Comprehensive security audit** - 8 critical security checks

### 🚀 Production-Ready Scripts
1. **`install-newman.sh`** - Automated Newman installation (global/local)
2. **`run-tests.sh`** - Test runner with security checks & multi-reporter support
3. **`security-audit.sh`** - Collection security scanner with detailed reports

### 📊 Multi-Reporter Support
- CLI (console output)
- HTML (beautiful reports via htmlextra)
- JSON (machine-readable)
- JUnit (CI/CD integration)
- Custom (build your own)

### 🔄 CI/CD Integration
Ready-to-use templates for:
- GitHub Actions
- GitLab CI
- Jenkins (Declarative & Scripted)
- CircleCI
- Bitbucket Pipelines
- Docker / Docker Compose

## 📦 Installation

### Install the Skill

```bash
# Clone this repository
git clone https://github.com/1999AZZAR/newman-skill.git ~/.openclaw/workspace/skills/newman

# Or download and extract
curl -L https://github.com/1999AZZAR/newman-skill/archive/main.tar.gz | tar -xz -C ~/.openclaw/workspace/skills/
```

### Install Newman CLI

```bash
# Run the installation script
~/.openclaw/workspace/skills/newman/scripts/install-newman.sh --global

# Or install manually
npm install -g newman newman-reporter-htmlextra
```

## 🚀 Quick Start

### 1. Export from Postman

**Collection:**
- Open Postman → Collections
- Click "..." → Export
- Choose "Collection v2.1"
- Save as `api-tests.json`

**Environment:**
- Environments → Click "..." → Export
- Save as `staging.json`

### 2. Run Tests

**Basic:**
```bash
newman run api-tests.json -e staging.json
```

**With reports:**
```bash
~/.openclaw/workspace/skills/newman/scripts/run-tests.sh \
  api-tests.json \
  staging.json \
  --output ./reports \
  --reporters cli,htmlextra,junit \
  --bail
```

### 3. Security Audit

```bash
~/.openclaw/workspace/skills/newman/scripts/security-audit.sh \
  api-tests.json \
  staging.json
```

**Example output:**
```
🔒 Newman Security Audit
=======================

[1/8] Checking for hardcoded secrets...
[OK] No hardcoded secrets found

[2/8] Checking for Basic Auth credentials...
[WARNING] Basic Auth credentials found (ensure they use variables)

[3/8] Checking for insecure HTTP URLs...
[OK] All URLs use HTTPS

...

✅ Security audit passed!
```

## 📚 Documentation

- **[SKILL.md](SKILL.md)** - Main guide (quick start, workflows, best practices)
- **[INSTALLATION.md](INSTALLATION.md)** - Detailed setup instructions
- **[CI/CD Examples](references/ci-cd-examples.md)** - Integration templates
- **[Advanced Patterns](references/advanced-patterns.md)** - Custom reporters, validation, performance testing

## 🔐 Security Best Practices

### ❌ NEVER Do This
```json
{
  "key": "API_KEY",
  "value": "sk_live_abc123xyz",  ❌ Hardcoded!
  "enabled": true
}
```

### ✅ ALWAYS Do This
```json
{
  "key": "API_KEY",
  "value": "{{$processEnvironment.API_KEY}}",  ✅ Environment variable!
  "enabled": true
}
```

```bash
export API_KEY="sk_live_abc123xyz"
newman run collection.json -e environment.json
```

## 🎓 Use Cases

- **Regression Testing** - Automated API tests on every commit
- **Load Testing** - Performance validation with high iteration counts
- **Smoke Tests** - Scheduled health checks for production APIs
- **CI/CD Integration** - Run in GitHub Actions, GitLab CI, Jenkins
- **Multi-Environment** - Test dev/staging/prod with different configs
- **Security Compliance** - Validate API security before deployment

## 🛠️ Scripts Reference

### install-newman.sh
```bash
# Global install (recommended)
./scripts/install-newman.sh --global

# Local install (project-specific)
./scripts/install-newman.sh --local
```

### run-tests.sh
```bash
./scripts/run-tests.sh <collection> <environment> [options]

Options:
  -o, --output DIR        Output directory (default: ./test-results)
  -r, --reporters LIST    Reporters (default: cli,htmlextra)
  -b, --bail              Stop on first failure
  -v, --verbose           Verbose output
  -n, --iterations NUM    Iteration count
  -t, --timeout MS        Request timeout
```

### security-audit.sh
```bash
./scripts/security-audit.sh <collection.json> [environment.json]
```

**Checks:**
- Hardcoded secrets/API keys
- Basic Auth credentials
- Insecure HTTP URLs
- SSL verification disabled
- PII exposure
- Variable usage best practices
- Timeout configurations
- Authentication patterns

## 🔄 CI/CD Example (GitHub Actions)

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Newman
        run: npm install -g newman newman-reporter-htmlextra
      
      - name: Run API Tests
        env:
          API_KEY: ${{ secrets.API_KEY }}
        run: |
          newman run collections/api-tests.json \
            -e environments/staging.json \
            --reporters cli,htmlextra,junit \
            --reporter-htmlextra-export ./reports/newman.html \
            --reporter-junit-export ./reports/newman.xml \
            --bail
      
      - name: Upload Reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: reports/
```

## 📊 Package Contents

```
newman/
├── SKILL.md                    (7.5KB)  - Main guide
├── INSTALLATION.md             (4.4KB)  - Setup instructions
├── README.md                            - This file
├── references/
│   ├── ci-cd-examples.md       (9.5KB)  - CI/CD templates
│   └── advanced-patterns.md    (12.9KB) - Advanced usage
└── scripts/
    ├── install-newman.sh       (1.4KB)  - Auto-installer
    ├── run-tests.sh            (5.5KB)  - Test runner
    └── security-audit.sh       (4.8KB)  - Security scanner

Total: ~46KB uncompressed
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🔗 Links

- **Newman Documentation**: https://learning.postman.com/docs/running-collections/using-newman-cli/
- **Postman Documentation**: https://learning.postman.com/
- **OpenClaw**: https://openclaw.ai
- **Issues**: https://github.com/1999AZZAR/newman-skill/issues

## 🙏 Acknowledgments

- [Postman Labs](https://www.postman.com/) for Newman
- [OpenClaw](https://openclaw.ai) for the skill framework
- Community contributors

---

**Version**: 1.0.0  
**Created**: 2026-02-10  
**Maintainer**: [@1999AZZAR](https://github.com/1999AZZAR)  
**Status**: Production-Ready ✅
