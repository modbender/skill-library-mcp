# ❓ Frequently Asked Questions

## General

### What is Smart Follow-ups?

A OpenClaw skill that generates contextual follow-up suggestions after AI responses. It analyzes your recent conversation and suggests 3 relevant questions across three categories:

- ⚡ **Quick** — Clarifications, definitions, immediate next steps
- 🧠 **Deep Dive** — Technical depth, advanced concepts, thorough exploration
- 🔗 **Related** — Connected topics, broader context, alternative perspectives

### Why only 3 suggestions?

We originally planned 6 (2 per category), but found 3 provides a cleaner UX:
- Less overwhelming, especially on mobile
- Each category gets one focused, high-quality suggestion
- Faster to scan and decide
- Keeps the interface clean

### How do I use it?

Type `/followups` in any OpenClaw conversation. On Telegram/Discord/Slack, you'll see 3 clickable buttons. On Signal/iMessage, you'll see a numbered list — reply with 1, 2, or 3.

---

## Authentication

### What's the authentication method?

**OpenClaw native** — the skill uses your existing OpenClaw authentication. No additional API keys required!

The handler uses the same model and auth as your current chat session. If you're chatting with Opus, follow-ups use Opus.

### Do I need any API keys?

**No!** The skill works out of the box with OpenClaw-native auth.

### What about OpenRouter/Anthropic?

The standalone CLI tool supports external providers for testing purposes:

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
node cli/followups-cli.js --model anthropic/claude-3-haiku --mode text
```

But the main skill (used in OpenClaw conversations) only uses native auth.

---

## Privacy & Security

### Is my conversation data sent anywhere?

**With OpenClaw native (default):** Same privacy as your normal chat. Your recent exchanges are processed by your configured AI provider (Anthropic) using your existing authentication.

**With OpenRouter:** Your recent exchanges are sent to OpenRouter's API. See [OpenRouter's privacy policy](https://openrouter.ai/privacy).

**With direct Anthropic:** Your recent exchanges are sent to Anthropic's API. See [Anthropic's privacy policy](https://www.anthropic.com/privacy).

### How much context is sent?

Only the last 1-3 message exchanges (user + assistant pairs). We don't send your entire conversation history.

### Are the suggestions logged anywhere?

No. Suggestions are generated on-demand and returned directly to you. Nothing is stored by the skill.

---

## Cost

### How much does it cost to use?

**OpenClaw native:** Part of your normal API usage — no additional cost structure. The skill uses your session's model, so costs are included in your regular usage.

For reference, generating follow-ups typically uses a small amount of tokens (~500-1000) per generation.

---

## Channels

### Which channels support buttons?

- ✅ **Telegram** — Full inline button support
- ✅ **Discord** — Full button support
- ✅ **Slack** — Full button support
- ❌ **Signal** — Text list fallback (reply with number)
- ❌ **iMessage** — Text list fallback
- ❌ **SMS** — Text list fallback

### What happens on channels without buttons?

You get a numbered text list:

```
💡 Smart Follow-up Suggestions

⚡ Quick
1. How do I install Docker?

🧠 Deep Dive
2. Explain Docker's architecture

🔗 Related
3. Compare Docker to Kubernetes

Reply with 1, 2, or 3 to ask that question.
```

Reply with the number to ask that question.

---

## Troubleshooting

### /followups doesn't work

1. **Check skill is installed:** `ls /path/to/openclaw/skills/smart-followups/`
2. **Check skill is enabled:** Look for `smart-followups` in your `openclaw.json`
3. **Restart OpenClaw:** After installing or configuring skills

### "API key required" error

You're using OpenRouter or Anthropic provider but haven't set an API key. Either:
- Switch to `provider: "openclaw"` (uses existing auth)
- Add your API key to the config

### Suggestions aren't relevant

The skill analyzes your last 1-3 exchanges. If your conversation is very short or vague, suggestions may be generic. Try having a more detailed exchange first.

### Buttons don't appear on Telegram

Check that your Telegram channel config has `inlineButtons` capability:

```json
{
  "channels": {
    "telegram": {
      "capabilities": ["inlineButtons"]
    }
  }
}
```

---

## CLI Tool

### Can I use the skill without OpenClaw?

Yes! The CLI tool works standalone:

```bash
export OPENROUTER_API_KEY="sk-or-..."
echo '[{"user":"What is Docker?","assistant":"Docker is..."}]' | followups-cli --mode text
```

### What input formats does the CLI accept?

JSON array of exchanges:
```json
[
  {"user": "What is Docker?", "assistant": "Docker is a containerization platform..."},
  {"user": "How is it different from VMs?", "assistant": "Key differences include..."}
]
```

Or pipe from a file: `cat conversation.json | followups-cli`

### What output formats are available?

- `json` — Raw JSON object
- `telegram` — Telegram inline buttons array
- `text` — Formatted text with categories
- `compact` — Simple numbered list

---

## Development

### How do I contribute?

See [CONTRIBUTING.md](CONTRIBUTING.md). Fork, branch, code, test, PR.

### Where are the development notes?

See [INTERNAL.md](INTERNAL.md) for architecture decisions, design rationale, and development history.

### How do I run tests?

```bash
cd smart-followups
./test.sh
```

---

## Still have questions?

- Open an issue on [GitHub](https://github.com/robbyczgw-cla/smart-followups/issues)
- Ask on [ClawHub Discussions](https://clawhub.ai/skills/smart-followups/discussions)
- Ping [@robbyczgw-cla](https://github.com/robbyczgw-cla)
