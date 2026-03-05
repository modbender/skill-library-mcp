# Security Policy

## 🛡️ About Prompt Guard

Prompt Guard is a security skill for AI agent platforms like [Clawdbot](https://github.com/clawdbot/clawdbot) and [Moltbot](https://github.com/moltbot/moltbot). It protects against:

- **Prompt Injection Attacks** - Manipulation attempts in EN/KO/JA/ZH
- **Secret Exfiltration** - Attempts to extract API keys, tokens, credentials
- **Privilege Escalation** - Unauthorized command execution in group contexts

## 🔐 Reporting a Vulnerability

If you discover a security vulnerability in Prompt Guard, please report it responsibly:

1. **DO NOT** create a public GitHub issue
2. **Email**: [security contact - create issue for contact info]
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## ⏱️ Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 7 days
- **Fix/Patch**: Depends on severity
  - Critical: 24-72 hours
  - High: 1-2 weeks
  - Medium/Low: Next release cycle

## 🎯 Scope

### In Scope
- Bypass of detection patterns
- False negatives allowing dangerous commands
- Information disclosure through the tool
- Configuration vulnerabilities

### Out of Scope
- Attacks on the underlying AI model itself
- Social engineering of human operators
- Issues in Clawdbot/Moltbot core (report to those projects)

## 🏆 Recognition

We appreciate security researchers who help improve Prompt Guard. With your permission, we'll acknowledge your contribution in our changelog and README.

## 📚 Security Resources

- [Clawdbot Security Docs](https://docs.clawd.bot/security)
- [Moltbot Security Guide](https://docs.molt.bot/security)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Prompt Injection Defense Patterns](https://github.com/topics/prompt-injection)

## 🔗 Related Projects

| Project | Description |
|---------|-------------|
| [Clawdbot](https://github.com/clawdbot/clawdbot) | AI agent platform |
| [Moltbot](https://github.com/moltbot/moltbot) | AI agent platform |
| [ClawdHub](https://clawdhub.com) | Skill marketplace |

---

**Prompt Guard** - Protecting AI agents from manipulation attacks.
