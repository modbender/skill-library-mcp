# x-read

`x-read` is a simple OpenClaw skill that renders public X (Twitter) posts via Puppeteer and extracts a cleaned-up, markdown-friendly summary of the tweet/article. It is intentionally read-only: there are no API keys, no posting, and no account links.

## Features

- Loads the permalink in a headless Chromium instance using Puppeteer.
- Extracts the main tweet/article text, timestamps, links, and media (with `ALT` text).
- Formats the output as Markdown, trimming noise so conversations stay readable in Telegram.
- Handles multi-image posts and includes the article body when available.

## Usage

```bash
openclaw use x-read read_tweet --url "https://x.com/<user>/status/<id>"
```

The skill will print a short thread summary with media references. The same command can also be invoked indirectly via the `OpenClaw` interface (e.g., pressing the generated button or calling the tool in Telegram). The skill does not post, like, DM, or authenticate—just reads what is publicly accessible.

## Development

- `index.js` contains the Puppeteer logic and selectors.
- `SKILL.md` describes the tool for OpenClaw.
- `package.json` pins Puppeteer and exposes the single entry point (`read_tweet`).

Before publishing on ClawHub, make sure you have tested the command locally and confirmed you still want to keep it read-only.
