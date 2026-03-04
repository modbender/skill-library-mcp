# ohmytoken

Track your LLM token consumption as pixel art at [ohmytoken.dev](https://ohmytoken.dev).

## What it does

After each LLM call, this skill reports the **model name** and **token count** (input + output) to ohmytoken.dev. Your usage appears as colorful beads on a pixel board in real-time.

**Privacy**: Only 3 fields are sent: `model`, `prompt_tokens`, `completion_tokens`. Zero prompts, zero code, zero content. Your IP is visible during the HTTP connection but is not logged.

You can also set your API key via the `OHMYTOKEN_API_KEY` environment variable.

## Setup (30 seconds)

1. Go to [ohmytoken.dev](https://ohmytoken.dev) and sign in with Google or GitHub
2. Copy your API key from Settings (looks like `omt_abc123...`)
3. Set the environment variable:

```bash
export OHMYTOKEN_API_KEY="omt_YOUR_KEY"
```

Add to your `~/.zshrc` or `~/.bashrc`, then `source ~/.zshrc`.

That's it. The skill runs silently in the background.

## Links

- Dashboard: [ohmytoken.dev](https://ohmytoken.dev)
- Source: [github.com/0x5446/ohmytoken-oss](https://github.com/0x5446/ohmytoken-oss)
- Issues: [github.com/0x5446/ohmytoken-oss/issues](https://github.com/0x5446/ohmytoken-oss/issues)
