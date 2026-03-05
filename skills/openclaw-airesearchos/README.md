# AIresearchOS Deep Research Skill for OpenClaw

## The Problem with AI Research

ChatGPT checks 3-10 sources and gives you a summary. Perplexity gives you slightly better summaries. Neither produces research deep enough for your AI agent to make an informed decision on your behalf — and if the input is shallow, the output will be too. If your agent's research can't survive scrutiny, its recommendations are just guesses with formatting.

## What AIresearchOS Does Differently

[AIresearchOS](https://airesearchos.com) runs **iterative deep research** — not a single search pass, but multiple rounds of follow-up searches and source analysis across 100-300+ sources. The output is a structured, cited report: executive summary, competitive landscape, market sizing, pricing signals, risks, and a full source appendix. Every claim is traceable.

In independent blind evaluations by Grok, AIresearchOS scored **9.0/10** — beating ChatGPT (5.7), Gemini (7.5), and Perplexity (7.5) on the same prompts. Zero red flags vs. 3-4 for competitors. ([Verify the evaluation yourself](https://grok.com/share/c2hhcmQtMw_d1d5516c-2320-43cf-bb57-1501cc1a9856))

It runs on open-source AI models. No content policies, no invisible guardrails, no corporate filters shaping your results.

## Why This Matters for Your Agent

This skill turns your OpenClaw assistant into a research analyst. Instead of you going to a website, typing a query, and waiting — you just tell your assistant what you need in natural language, from any channel you're already using (WhatsApp, Telegram, Slack, Discord, or the TUI). It handles the submission, monitors progress in the background, and delivers the full report directly to your conversation when it's ready.

Your assistant can also answer clarifying questions the research engine asks to sharpen results, check your credit balance, and pull up past reports — all conversationally.

## What This Skill Does

- **Submit research** on any topic across three depth levels
- **Background monitoring** — the assistant schedules a cron job to check progress and announces results when ready, so you're never blocked
- **Clarifying questions** — the research engine can ask follow-up questions to improve results (API key path)
- **Full reports** with markdown formatting, structured sections, and source citations
- **Credits & history** — check your balance and browse past research

## Research Modes

| Mode | API Key | x402 (USDC) | Sources | Use Case |
|------|---------|-------------|---------|----------|
| Scan | 10 credits | $0.50 | 10-20 | Quick validation |
| Due Diligence | 25 credits | $1.50 | 50-100 | Decision-grade analysis |
| Mission Critical | 100 credits | $5.00 | 150-300+ | Exhaustive coverage |

## Two Ways to Pay

### API Key (recommended for regular use)

Sign up at [airesearchos.com](https://airesearchos.com), subscribe to Pro ($30/month, 150 credits/day), and add your key to OpenClaw:

```json5
// ~/.openclaw/openclaw.json
{
  skills: {
    entries: {
      airesearchos: {
        apiKey: "aro_sk_your_key_here"
      }
    }
  }
}
```

### x402 Pay-Per-Request (no account needed)

Pay with USDC stablecoins on Base network. No signup, no subscription — just a wallet and funds.

```json5
// ~/.openclaw/openclaw.json
{
  skills: {
    entries: {
      airesearchos: {
        env: {
          AIRESEARCHOS_WALLET_KEY: "0xYOUR_PRIVATE_KEY"
        }
      }
    }
  }
}
```

The skill bundles a lightweight x402 payment helper (`scripts/x402-request.mjs`) that handles the HTTP 402 → sign → retry flow automatically. Built on `@x402/core` and `@x402/evm`.

See [SETUP.md](SETUP.md) for detailed instructions on both auth methods, getting USDC on Base, and optional configuration.

## How It Works

1. **You ask** your OpenClaw assistant to research something
2. **The skill detects** your auth method (API key or x402 wallet) automatically at runtime
3. **Research is submitted** to AIresearchOS via the appropriate API endpoint
4. **A background cron job** is scheduled to check status every 2 minutes
5. **When complete**, the cron job announces the full report back to your chat
6. You can also ask **"check my research"** or **"get my report"** at any time

The assistant stays responsive throughout — no blocking, no waiting. Research typically completes in 3-10 minutes depending on mode.

## File Structure

```
SKILL.md                 # Agent instructions (loaded into OpenClaw's system prompt)
SETUP.md                 # User-facing setup guide for both auth methods
CHANGELOG.md             # Version history
scripts/
  package.json           # Dependencies: @x402/core, @x402/evm, viem
  x402-request.mjs       # x402 payment helper (402 → sign → retry)
  check-status.mjs       # Status checker (structured JSON output, env-based auth)
```

## Install

### From ClawHub

```bash
clawhub install airesearchos-deep-research
```

### Manual

Copy or symlink into your OpenClaw skills directory:

```bash
# Global (shared across all agents)
git clone https://github.com/bowtiedbluefin/openclaw-airesearchos.git ~/.openclaw/skills/airesearchos

# Or symlink for development
ln -s /path/to/this/repo ~/.openclaw/skills/airesearchos
```

Start a new OpenClaw session. The skill loads automatically.

## Security

- API keys and wallet keys are injected via OpenClaw's env var system — never exposed in chat
- The x402 script reads keys from environment variables only (never CLI arguments)
- Research results are treated as untrusted external content (prompt injection defense)
- `--max-payment` safety limit prevents unexpected x402 overspend
- All scripts are minimal, single-purpose, and auditable (<200 LOC each)

## License

MIT
