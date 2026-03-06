# cashu-emoji

Allows AI Agents (and humans) to **encode and decode hidden messages in emojis** using Unicode variation selectors.

Primary use-case: decode/encode **Cashu emoji tokens** (`cashu...`) for agent-to-agent payments.
Secondary use-case: hide **general short text messages** in an emoji.

This repo is designed as a **Clawhub agent skill** reference: small, copy/pasteable implementation + CLI examples.

## What is this?

You can hide arbitrary UTF-8 text (e.g. a `cashuB...` token or a plain message) inside an emoji by appending Unicode **variation selectors** (VS1..VS256). Most chat apps display only the emoji, but preserve the hidden selector characters.

This implementation is based on Paul Butler’s `emoji-encoder` technique and the TypeScript adaptation used in Rob’s `nostrly` repo.

## Quickstart (copy/paste)

```bash
git clone https://github.com/robwoodgate/cashu-emoji.git
cd cashu-emoji
npm ci

# decode a whole message (recommended)
node ./bin/cashu-emoji.js decode "<paste message>"

# (or via npm script)
npm run cashu-emoji -- decode "<paste message>"

# decode and print mint/unit/amount if it’s a cashu token
node ./bin/cashu-emoji.js decode "<paste message>" --metadata

# decode as structured JSON (agent-friendly)
node ./bin/cashu-emoji.js decode "<paste message>" --metadata --json

# encode a hidden message
node ./bin/cashu-emoji.js encode "🥜" "hello from inside an emoji"

# encode a cashu token
node ./bin/cashu-emoji.js encode "🥜" "cashuB..."
```

## Quick examples

(These use `node ./bin/...` so you don’t need to install anything globally. If you run via npm scripts, use `npm run -s ...` to suppress npm’s extra header lines.)

### Decode (emoji/message → hidden text)

```bash
node ./bin/cashu-emoji.js decode "<paste whole message here>"
```

### Decode + show Cashu metadata (if hidden text is a Cashu token)

```bash
node ./bin/cashu-emoji.js decode "<paste whole message here>" --metadata
```

### Encode (text → emoji with hidden message)

```bash
node ./bin/cashu-emoji.js encode "🥜" "hello from inside an emoji"
```

### Encode a Cashu token for sending

```bash
node ./bin/cashu-emoji.js encode "🥜" "cashuB..."
```

Tip: Some messengers are less likely to deliver a *truncated/corrupted* emoji-token if **any normal text follows it** (even a single character). It’s not required, just a delivery reliability trick.

Tip (Telegram): code block / “monospace” formatting can help preserve the hidden characters and makes it easier to tap-to-copy.

## Cashu gotchas for new agents

- A decoded `cashu...` token is a **bearer asset**. Treat it like cash: don’t paste it into public logs/issues.
- `--metadata` is a **local parse** (no mint calls). It can tell you mint/unit/amount, but it **cannot** prove the token is unspent/valid.
- Wallets/mints may reject tokens if a messenger truncated the hidden variation selectors. If decode returns gibberish or a partial `cashu...`, ask for the token to be re-sent.

## Test vector

See `examples/minimal-1sat-emoji.txt` for a small Cashu emoji token you can decode.
