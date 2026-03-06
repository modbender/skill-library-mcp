# Git Sentinel 🛡️

**Your AI-powered Senior Code Reviewer.**

Stop pushing bugs. Git Sentinel is an OpenClaw skill that acts as a merciless Senior Software Engineer & Security Auditor. It reviews your staged changes before you commit, catching security flaws, performance issues, and bad practices.

## Features

- **🛡️ Security First:** Detects hardcoded secrets, injection risks (SQLi, XSS, RCE), and weak crypto.
- **🚀 Performance:** Flags N+1 queries, expensive loops, and memory leaks.
- **🧹 Clean Code:** Enforces architecture standards and readability.
- **🤖 Zero Config:** Works with any language (JS, Python, Go, Rust, etc.) immediately.

## Installation

```bash
clawhub install git-sentinel
```

## Usage

Inside any Git repository:

```bash
# Review staged changes (ready to commit)
sentinel review

# Review a specific file
sentinel review src/server.js
```

## Example Output

> **🔴 CRITICAL**
> *   `auth.js:42` - **Hardcoded Secret:** Found AWS Key in plain text.
>
> **🟡 WARNING**
> *   `user.js:15` - **Performance:** Nested loop O(n^2) on potentially large dataset.
>
> **Verdict:** ❌ REJECT

## License

MIT © Corezip & Kiri
