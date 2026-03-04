---
name: cashu-emoji
description: Encode and decode Cashu tokens that are hidden inside emojis using Unicode variation selectors.
metadata:
  openclaw:
    emoji: "🥜"
    examples:
      - "Decode an emoji token from a full chat message"
      - "Encode a Cashu token into an emoji for sending"
---

# Cashu Emoji Tokens (Variation Selector encoding)

This skill helps agents **decode** Cashu tokens received as emoji (and **encode** tokens for sending), and it also supports **general hidden messages inside emojis**.

If the decoded text starts with `cashu`, it’s likely a Cashu token. Otherwise treat it as a plain hidden message.

## Why this exists

Some services embed a `cashu...` token into an emoji using Unicode variation selectors (VS1..VS256). Chat apps often display only the emoji, but preserve the hidden selector characters.

Important: many messengers can *truncate or normalize* Unicode. If the variation selectors are lost, the embedded token cannot be recovered.

## Quickstart (copy/paste)

```bash
git clone https://github.com/robwoodgate/cashu-emoji.git
cd cashu-emoji
npm ci

# decode a whole message (recommended)
node ./bin/cashu-emoji.js decode "<paste message>"

# decode and print mint/unit/amount if it’s a cashu token
node ./bin/cashu-emoji.js decode "<paste message>" --metadata

# decode as structured JSON (agent-friendly)
node ./bin/cashu-emoji.js decode "<paste message>" --metadata --json

# encode a hidden message
node ./bin/cashu-emoji.js encode "🥜" "hello from inside an emoji"

# encode a cashu token
node ./bin/cashu-emoji.js encode "🥜" "cashuB..."
```

## What you can do

### 1) Decode

- Input: entire message text (may include other text/emojis)
- Output: the embedded UTF‑8 text, usually a `cashuA...`/`cashuB...` token

```bash
node ./bin/cashu-emoji.js decode "<paste entire message>"
```

Decode semantics (important): the decoder ignores normal characters until it finds the first variation-selector byte, then collects bytes until the first normal character after that payload begins.

### 2) Encode

- Input: a carrier emoji (recommend `🥜`) and a token string
- Output: an emoji string that visually looks like the emoji but contains the hidden token

```bash
node ./bin/cashu-emoji.js encode "🥜" "cashuB..."
```

Tip: some messengers are less likely to deliver a *truncated/corrupted* emoji-token if **any normal text follows it** (even a single character). It’s not required, just a delivery reliability trick.

Tip (Telegram): sending the emoji-token inside a code block / “monospace” formatting can help preserve the hidden characters and makes it easier to tap-to-copy.

## Optional metadata

To sanity-check the decoded token without redeeming it, you can request metadata.

For programmatic/agent use, prefer JSON output:

```bash
node ./bin/cashu-emoji.js decode "<message>" --metadata --json
```

Example JSON response (Cashu token):

```json
{
  "text": "cashuB...",
  "isCashu": true,
  "metadata": {
    "mint": "https://mint.example",
    "unit": "sat",
    "amount": 21
  },
  "metadataError": null
}
```

Example JSON response (plain hidden message):

```json
{
  "text": "hello from inside an emoji",
  "isCashu": false
}
```

```bash
node ./bin/cashu-emoji.js decode "<message>" --metadata
```

This prints mint/unit/amount using `@cashu/cashu-ts` `getTokenMetadata()` (no mint calls).

## Cashu gotchas for new agents

- A decoded `cashu...` token is a **bearer asset**. Treat it like cash.
- `--metadata` is a **local parse**. It can’t prove the token is unspent/valid.
- If decode returns a partial token or nonsense, the messenger likely munged the variation selectors; ask for the token to be re-sent (often with some trailing normal text after the emoji token).

## Files

- `src/emoji-encoder.ts`: core encode/decode
- `bin/cashu-emoji.js`: CLI wrapper
- `examples/`: test vectors

## Safety

This tool only encodes/decodes text. It does not spend funds.
