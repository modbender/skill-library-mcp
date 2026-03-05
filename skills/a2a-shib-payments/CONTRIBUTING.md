# Contributing to A2A SHIB Payment System

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

---

## 🎯 Ways to Contribute

### 1. 🐛 Report Bugs
- Check [existing issues](https://github.com/marcus20232023/a2a-shib-payments/issues) first
- Use the bug report template
- Include:
  - Steps to reproduce
  - Expected behavior
  - Actual behavior
  - Environment (Node version, OS, network)
  - Error logs/stack traces

### 2. 💡 Suggest Features
- Open an issue with the `enhancement` label
- Describe:
  - Use case (why is this needed?)
  - Proposed solution
  - Alternative approaches considered
  - Impact on existing functionality

### 3. 📝 Improve Documentation
- Fix typos, clarify instructions
- Add examples or use cases
- Update outdated information
- Translate to other languages

### 4. 🔧 Submit Code
- Bug fixes
- New features
- Performance improvements
- Test coverage
- Refactoring

---

## 🚀 Getting Started

### Fork & Clone

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/a2a-shib-payments.git
cd a2a-shib-payments

# Add upstream remote
git remote add upstream https://github.com/marcus20232023/a2a-shib-payments.git
```

### Install Dependencies

```bash
npm install
```

### Configure Environment

```bash
cp .env.example .env.local
# Edit .env.local with your wallet and RPC details
```

### Run Tests

```bash
npm test
# Or run individual test suites:
npm run test:security
npm run test:escrow
npm run test:reputation
```

### Start Development Agent

```bash
npm start
# Agent runs on http://localhost:8003
```

---

## 📋 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/bug-description
```

**Branch naming:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `test/` - Test improvements
- `refactor/` - Code refactoring

### 2. Make Changes

- Follow existing code style
- Add tests for new functionality
- Update documentation
- Keep commits atomic and focused

### 3. Test Thoroughly

```bash
# Run all tests
npm test

# Test specific functionality
node test-escrow-negotiation.js
node test-reputation.js
node test-security.js

# Manual testing
curl http://localhost:8003/.well-known/agent-card.json
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: Add multi-token support for USDC"
```

**Commit message format:**
```
type: Short description (50 chars max)

Longer explanation if needed (72 chars per line)

- Bullet points for details
- Reference issues: Fixes #123
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `perf:` Performance improvement
- `chore:` Maintenance

### 5. Push & Open PR

```bash
git push origin feature/my-feature
```

Then open a pull request on GitHub.

---

## 📝 Pull Request Guidelines

### PR Title Format
```
[Type] Brief description
```

Examples:
- `[Feature] Add USDC token support`
- `[Fix] Resolve escrow timeout race condition`
- `[Docs] Update LangChain integration example`

### PR Description Template

```markdown
## Description
Brief summary of changes.

## Motivation
Why is this change needed? What problem does it solve?

## Changes
- List of specific changes
- Bullet points for each file/module modified

## Testing
- [ ] All existing tests pass
- [ ] Added new tests for new functionality
- [ ] Manually tested on local agent
- [ ] Tested on testnet (if blockchain changes)

## Documentation
- [ ] Updated README if needed
- [ ] Updated API documentation
- [ ] Added code comments
- [ ] Updated CHANGELOG.md

## Breaking Changes
List any breaking changes (or "None")

## Checklist
- [ ] Code follows project style
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No console.log() or debug code
- [ ] Secrets not committed
- [ ] Ready for review
```

### Review Process

1. **Automated checks:** CI/CD runs tests automatically
2. **Code review:** Maintainer reviews code quality, style, tests
3. **Feedback:** Address review comments
4. **Approval:** Once approved, PR is merged
5. **Release:** Changes included in next release

---

## 🧪 Testing Standards

### Required Tests

**For new features:**
- Unit tests for individual functions
- Integration tests for module interaction
- End-to-end tests for full workflows

**For bug fixes:**
- Regression test that fails before fix
- Passes after fix

### Test Structure

```javascript
// test-new-feature.js
console.log('🧪 Testing New Feature...\n');

async function testFeature() {
  try {
    // Arrange
    const input = {...};
    
    // Act
    const result = await newFeature(input);
    
    // Assert
    if (result === expected) {
      console.log('✅ Test passed');
      return true;
    } else {
      console.log('❌ Test failed:', result);
      return false;
    }
  } catch (error) {
    console.error('❌ Error:', error);
    return false;
  }
}

testFeature();
```

### Coverage Goals

- **Critical paths:** 100% (payments, escrow)
- **Overall:** >80%

---

## 📐 Code Style

### JavaScript Style

```javascript
// Use const/let, not var
const config = {...};
let state = 'pending';

// Async/await preferred over .then()
async function sendPayment() {
  const tx = await wallet.sendTransaction({...});
  return tx;
}

// Descriptive variable names
const escrowAmount = 500; // Good
const x = 500;            // Bad

// JSDoc comments for public functions
/**
 * Create a new escrow contract
 * @param {string} payer - Payer agent ID
 * @param {string} payee - Payee agent ID
 * @param {number} amount - Amount in SHIB
 * @param {Object} options - Escrow options
 * @returns {Object} Escrow details
 */
async function createEscrow(payer, payee, amount, options) {
  // ...
}
```

### File Organization

```
├── Core systems (index.js, escrow.js, etc.)
├── Security (auth.js, rate-limiter.js, audit-logger.js)
├── A2A agents (a2a-agent-*.js)
├── Tests (test-*.js)
├── Documentation (*.md)
├── Deployment (deploy-*.sh, *.service)
└── Config (.env.example, package.json)
```

---

## 🔐 Security Guidelines

### Never Commit Secrets

- Private keys
- API keys
- RPC URLs with auth
- .env.local files

Use `.env.example` for templates only.

### Security Review Checklist

- [ ] No SQL injection vectors
- [ ] Input validation on all user data
- [ ] Rate limiting for public endpoints
- [ ] Authentication for sensitive operations
- [ ] Audit logging for financial operations
- [ ] Time-locks for escrows
- [ ] Multi-party approval for high-value transactions

### Reporting Security Issues

**Do not open public issues for security vulnerabilities.**

Email: (add your security contact email)

We'll respond within 48 hours and work with you to fix it.

---

## 📦 Release Process

### Versioning (SemVer)

- `MAJOR.MINOR.PATCH` (e.g., 2.1.3)
- **MAJOR:** Breaking changes
- **MINOR:** New features (backward-compatible)
- **PATCH:** Bug fixes

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in package.json
- [ ] Git tag created (`git tag -a v2.1.0 -m "Release v2.1.0"`)
- [ ] GitHub release created with notes
- [ ] npm published (if applicable)

---

## 🏷️ Issue Labels

| Label | Purpose |
|-------|---------|
| `bug` | Something isn't working |
| `enhancement` | New feature or request |
| `documentation` | Documentation improvements |
| `good first issue` | Easy for newcomers |
| `help wanted` | Extra attention needed |
| `question` | Further information requested |
| `wontfix` | Will not be worked on |
| `duplicate` | Already exists |
| `priority: high` | Critical issue |
| `priority: low` | Nice to have |

---

## 🎓 Resources for Contributors

### Understanding the Codebase

1. **Start with:** [README.md](README.md) - Overview
2. **Then:** [FINAL-SUMMARY.md](FINAL-SUMMARY.md) - Architecture
3. **Deep dive:** [ESCROW-NEGOTIATION-GUIDE.md](ESCROW-NEGOTIATION-GUIDE.md) - APIs
4. **Security:** [PRODUCTION-HARDENING.md](PRODUCTION-HARDENING.md)

### External Resources

- **A2A Protocol:** https://a2a-protocol.org
- **Ethers.js:** https://docs.ethers.org/
- **Polygon:** https://docs.polygon.technology/
- **Express.js:** https://expressjs.com/

### Getting Help

- **Questions:** Open a [Discussion](https://github.com/marcus20232023/a2a-shib-payments/discussions)
- **Bugs:** Open an [Issue](https://github.com/marcus20232023/a2a-shib-payments/issues)
- **Chat:** (Add Discord/Slack if you create one)

---

## 🙏 Recognition

Contributors are recognized in:
- GitHub contributor list
- CHANGELOG.md release notes
- README.md acknowledgments (for significant contributions)

---

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all.

### Our Standards

**Positive behavior:**
- Being respectful and inclusive
- Accepting constructive criticism
- Focusing on what's best for the community
- Showing empathy

**Unacceptable behavior:**
- Harassment, trolling, or insulting comments
- Personal or political attacks
- Publishing others' private information
- Other unethical or unprofessional conduct

### Enforcement

Violations may result in:
1. Warning
2. Temporary ban
3. Permanent ban

Report issues to: (add moderation contact)

---

## 🎯 Roadmap Priorities

Current focus (v2.1):
- Multi-token support (USDC, POL, DAI)
- WebSocket real-time updates
- Agent marketplace integration

Future (v3.0):
- Cross-chain payments
- Decentralized agent registry
- AI-powered fraud detection

See [README.md](README.md#-roadmap) for full roadmap.

---

## ✅ Ready to Contribute?

1. **Pick an issue** from [good first issues](https://github.com/marcus20232023/a2a-shib-payments/labels/good%20first%20issue)
2. **Comment** on the issue to claim it
3. **Fork, code, test, PR**
4. **Celebrate** your contribution! 🎉

Thank you for making agent-to-agent payments better! 🦪💰
