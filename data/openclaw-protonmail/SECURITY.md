# Security Policy

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to **jim@rvacyber.com** with the subject line: `[SECURITY] openclaw-protonmail-skill: [brief description]`

We take security seriously and will respond within **48 hours** to acknowledge receipt.

### What to Include

Please include the following in your report:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)
- Your contact information (if you want credit)

### Response Process

1. **Acknowledgment** (within 48 hours)
2. **Investigation** (1-7 days depending on severity)
3. **Fix development** (timeline depends on complexity)
4. **Disclosure** (coordinated with reporter)

### Security Considerations

This skill handles sensitive email data. Key security principles:

#### Authentication
- **Bridge passwords are NOT your ProtonMail password** — Bridge generates separate credentials
- Store credentials in OpenClaw config with restrictive file permissions (`chmod 600`)
- Never log or transmit credentials
- Never commit credentials to version control

#### Network Security
- **All traffic is local** — Bridge runs on 127.0.0.1 (localhost only)
- IMAP: `127.0.0.1:1143` (local, TLS with self-signed cert)
- SMTP: `127.0.0.1:1025` (local, no network exposure)
- No third-party services — direct connection to your ProtonMail via Bridge

#### Data Handling
- **Email content is decrypted locally** by Bridge (end-to-end encryption maintained to Proton servers)
- Attachments are saved to temp directories (cleaned up by OS)
- No persistent storage of email content by the skill
- OpenClaw session logs may contain email text — treat session files as sensitive

#### Dependencies
- Use `npm audit` regularly
- Pin dependency versions in `package-lock.json`
- Review dependency updates before merging

### Known Limitations

- **Bridge must be running** — If Bridge crashes, the skill cannot connect
- **Bridge uses self-signed certificates** — We disable certificate validation for localhost (acceptable risk, no MITM possible on loopback)
- **Session transcripts** — OpenClaw logs tool calls, which may include email content. Protect your workspace directory.

### Security Best Practices for Users

1. **Protect your Bridge password** — Store in Keychain/password manager
2. **File permissions** — `chmod 600 ~/.openclaw/openclaw.json`
3. **Audit access** — Review who has access to your machine and OpenClaw workspace
4. **Update regularly** — Keep Bridge, OpenClaw, and this skill updated
5. **Monitor sessions** — Check `.openclaw/agents/main/sessions/` for unexpected activity

### Credits

Security researchers who responsibly disclose vulnerabilities will be credited (with permission) in release notes.

---

**Last updated:** 2026-02-16  
**Contact:** jim@rvacyber.com
