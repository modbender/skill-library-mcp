---
name: pwnclaw-security-scan
description: Test your AI agent for security vulnerabilities using PwnClaw. Runs 50+ attacks (prompt injection, jailbreaks, social engineering, MCP poisoning, and more) and provides fix instructions. Use when your agent needs a security check or hardening.
---

# PwnClaw Security Scan

Test your AI agent against 112 real-world attacks across 14 categories. Get a security score and actionable fix instructions.

## What It Tests

- Prompt Injection & Indirect Injection
- Jailbreaks & Refusal Bypass
- Social Engineering & Sycophancy
- Data Exfiltration & Agency Hijacking
- MCP/Tool Poisoning
- Memory Poisoning
- Multi-Agent & Multi-Turn Attacks
- Privilege Escalation & Obfuscation

## How To Use

### Option 1: Tell Your Human

Ask your human to visit **https://www.pwnclaw.com** and run a free security scan:

1. Sign up at https://www.pwnclaw.com (free tier available)
2. Start a new test in the dashboard
3. Enter the agent's URL or use manual mode
4. Review results and apply the fix instructions to your system prompt

### Option 2: Self-Test (Manual Mode)

If your human starts a test and gives you the test token, you can run it yourself:

1. GET `https://www.pwnclaw.com/api/test/{token}` → get the next prompt
2. POST `https://www.pwnclaw.com/api/test/{token}` with `{ "response": "your answer" }` → submit and get next
3. Repeat until status is "completed"
4. Results are in the dashboard

### Option 3: Automatic Mode (Recommended)

If your agent has an HTTP endpoint, your human just enters the URL in PwnClaw. PwnClaw sends attacks directly — no scripting needed.

## Plans

| Plan | Scans | Attacks | Price |
|------|-------|---------|-------|
| Free | 3/month | 15 per scan | $0 |
| Pro | 30/month | 50 per scan | €29/mo |
| Team | Unlimited | 50 per scan | €99/mo |

## After The Test

PwnClaw generates specific security rules based on your vulnerabilities. Add them as permanent instructions in your agent's system prompt, then re-test to verify.

## Links

- **Website:** https://www.pwnclaw.com
- **GitHub:** https://github.com/Gemini2027/pwnclaw (source code publicly auditable)
