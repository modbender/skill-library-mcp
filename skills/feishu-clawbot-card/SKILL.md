---
name: Feishu ClawBot Card (FCC)
description: This skill allows OpenClaw bots to create, exchange, and store
  standardized identity cards ("ClawCards"). It acts as a Rolodex for your AI to
  remember who's who.
---

# Feishu ClawBot Card (FCC)

**The Universal Business Card Protocol for AI Agents on Feishu.**

This skill allows OpenClaw bots to create, exchange, and store standardized identity cards ("ClawCards"). It acts as a Rolodex for your AI to remember who's who.

## 📦 Installation

```bash
openclaw install HMyaoyuan/feishu-clawbot-card
```

## 🚀 Usage Guide

### 1. 🆔 Mint Your Card (Create Identity)
First, define who *you* are. Run this once to register yourself in the local registry.

```bash
node skills/feishu-clawbot-card/index.js mint '{
  "display_name": "MyBotName",
  "feishu_id": "cli_a...", 
  "avatar": { "url": "https://..." },
  "bio": {
    "species": "Robot",
    "mbti": "INTJ",
    "desc": "I am a helpful coding assistant."
  },
  "capabilities": ["coding", "search"]
}'
```
*Note: `feishu_id` should be your App ID (`cli_...`) or User Open ID (`ou_...`).*

### 2. 📤 Share Your Card (Export)
Generate a shareable JSON code block to send to other bots or humans.

```bash
# Get the JSON for a specific bot (by name or ID)
node skills/feishu-clawbot-card/index.js export "MyBotName"
```
**Output:** A JSON block. Copy this and send it in a chat!

### 3. 📥 Save a Friend's Card (Import)
When someone sends you their card JSON (following FCC-v1 protocol), save it to your registry.

```bash
# Paste the received JSON string
node skills/feishu-clawbot-card/index.js import '{"protocol":"fcc-v1", ...}'
```

### 4. 📇 View Registry (List)
See all the bots you know.

```bash
node skills/feishu-clawbot-card/index.js list
```

### 5. 🎨 Display Card (Render)
Generate a beautiful Feishu Rich Text (Post) JSON to display a card in chat.

```bash
node skills/feishu-clawbot-card/index.js render "MyBotName"
```

## 📜 Protocol Schema (FCC v1)

A valid card must follow this JSON structure:

```json
{
  "protocol": "fcc-v1",
  "id": "uuid...",
  "display_name": "Name",
  "feishu_id": "cli_... or ou_...",
  "avatar": { "url": "https://..." },
  "bio": {
    "species": "...",
    "mbti": "...",
    "desc": "..."
  },
  "capabilities": ["tag1", "tag2"]
}
```
