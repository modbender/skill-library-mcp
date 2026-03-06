# Security Model: Listing Swarm

## 🔒 TL;DR

- **Zero credentials stored** — This skill ships with NO API keys, passwords, or secrets
- **BYOK architecture** — You provide your own keys at runtime via environment variables
- **No data exfiltration** — Your product info goes to directories you choose, nowhere else
- **Fully auditable** — All source code is readable, no obfuscation

---

## Credential Handling

### What We DON'T Do

| ❌ Never | Explanation |
|----------|-------------|
| Store credentials | No hardcoded keys, no config files with secrets |
| Log sensitive data | API keys and passwords are never written to logs |
| Phone home | No telemetry, no analytics, no callbacks to LinkSwarm |
| Access unrelated data | Only touches directories.json, submissions.json, and your product config |

### What YOU Control

| Service | Your Responsibility | How It's Used |
|---------|---------------------|---------------|
| 2captcha.com | Create account, fund it, get API key | Solves captchas on directory forms |
| IMAP (Gmail, etc.) | Provide app password (optional) | Auto-clicks verification links |

You set these via environment variables. They exist only in your runtime environment.

---

## Data Flow Analysis

### Flow 1: Captcha Solving (User-Initiated)

```
Directory website         Your agent              2captcha.com
       │                      │                        │
       │ ◄─── visits form ────┤                        │
       │ ─── captcha image ──►│                        │
       │                      │ ── image + YOUR key ──►│
       │                      │ ◄── solution ──────────│
       │ ◄─── submits form ───┤                        │
```

**Data transmitted:** Captcha image (from directory) + your API key (from your env)  
**Data received:** Captcha solution text  
**Risk:** None — you control the 2captcha account, you pay for it, you can revoke the key

### Flow 2: Email Verification (Optional, User-Initiated)

```
Directory website         Your agent              Your IMAP server
       │                      │                        │
       │ ─── sends email ─────┼───────────────────────►│
       │                      │ ── YOUR credentials ──►│
       │                      │ ◄── verification link ─│
       │ ◄─── clicks link ────┤                        │
```

**Data transmitted:** Your IMAP credentials (from your env)  
**Data received:** Verification email content  
**Risk:** None — it's YOUR email, YOUR credentials, YOUR server

### Flow 3: Form Submission (Core Function)

```
Your product.json         Your agent              Directory website
       │                      │                        │
       │ ─── product info ───►│                        │
       │                      │ ─── fills form ───────►│
       │                      │ ◄── confirmation ──────│
```

**Data transmitted:** Your product name, URL, description (that you provided)  
**Data received:** Submission confirmation  
**Risk:** None — this is literally the point of the skill

---

## Files Accessed

| File | Access | Contains | Sensitive? |
|------|--------|----------|------------|
| `directories.json` | Read only | Static list of 70+ AI directories | No |
| `submissions.json` | Read/Write | Track what's been submitted | No |
| `captcha.js` | Read only | 2captcha integration code | No |
| `email.js` | Read only | IMAP integration code | No |
| Your product config | Read only | Your product info for forms | Your data |

---

## Network Endpoints

| Endpoint | Purpose | Auth |
|----------|---------|------|
| `2captcha.com/in.php` | Submit captcha | Your API key |
| `2captcha.com/res.php` | Get solution | Your API key |
| Your IMAP server | Check emails | Your credentials |
| 70+ directory websites | Submit listings | None (public forms) |

**No requests to LinkSwarm servers.** We don't collect data.

---

## Source Code Audit

All code is readable:

```
listing-swarm/
├── SKILL.md           # Documentation (this references)
├── SECURITY.md        # This file
├── directories.json   # Static data, fully readable
├── submissions.json   # Your submission history
├── captcha.js         # ~50 lines, 2captcha API calls
└── email.js           # ~80 lines, IMAP connection
```

No minification. No obfuscation. No dynamic code loading. No eval().

---

## Frequently Asked Questions

**Q: Why does the scanner flag "data exfiltration"?**  
A: The skill does transmit data — captcha images to 2captcha, your product info to directories. That's the whole point. But all flows are user-initiated, using your credentials, to services you chose.

**Q: Can LinkSwarm see my API keys?**  
A: No. Keys exist only in your local environment variables. We never see them.

**Q: What if I don't provide IMAP access?**  
A: The agent will say "Check your email for the verification link from [Directory]" and you click it manually.

**Q: What if I don't provide a captcha API key?**  
A: The agent will flag each captcha for you to solve manually in the browser.

---

## Contact

Security concerns? Open an issue or email hello@linkswarm.ai
