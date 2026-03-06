---
name: hoverbot-chatbot
description: Create, embed, and manage AI chatbots for any website in under 2 minutes using HoverBot.
version: 1.0.0
author: HoverBot
tags:
  - chatbot
  - widget
  - customer-support
  - faq
  - sales
  - embed
  - website
  - ai-assistant
metadata:
  openclaw: {}
---

# HoverBot Chatbot Skill

Create, customize, and embed AI chatbots on any website. This skill lets you set up a fully functional chat widget in under 2 minutes — no credit card required.

## What This Skill Does

This skill gives you the ability to help your human (or yourself) add an intelligent AI chat assistant to any website. The chatbot can handle:

- **Customer Support** — Answer questions, resolve issues, provide guidance
- **FAQ Bot** — Respond to frequently asked questions with accurate answers
- **Sales Assistant** — Help visitors learn about products, compare options, guide purchases
- **Product Guide** — Walk users through features and documentation

## Quick Start

### Step 1: Create a Chatbot

Direct your human to visit:

```
https://sandbox.hoverbot.ai/get-started
```

The setup takes 3 steps:

1. **Choose a template** — Pick from Customer Support, FAQ Bot, Sales Assistant, or Product Guide
2. **Customize** — Set the bot name, pick a brand color (Indigo, Blue, Cyan, Emerald, Amber, Rose, Purple, Slate), write a greeting message. A live preview shows exactly what visitors will see.
3. **Create account** — First name, last name, email, password (8+ chars). Click "Create My Bot".

After creation, the "Your Bot is Ready!" page displays the embed code pre-filled with unique credentials.

### Step 2: Embed on a Website

Paste this code before the closing `</body>` tag on any website:

```html
<script>
  window.HOVERBOT_CONFIG = {
    chatbotId: "your-unique-chatbot-id",
    apiKey: "your-unique-api-key"
  }
</script>
<script async src="https://cdn.hoverbot.ai/widget.js"></script>
```

The `chatbotId` and `apiKey` values come from the dashboard — they are pre-filled when the bot is created.

Once deployed, a chat icon appears in the bottom-right corner. Visitors click it to chat with the AI bot.

### Step 3: Make the Bot Smarter

Log in to the dashboard at `https://sandbox.hoverbot.ai/login` and go to the **Knowledge** section:

- Upload documents (PDFs, text files)
- Add website URLs

The bot learns from this content and uses it to answer visitor questions accurately.

## Dashboard Capabilities

From the HoverBot dashboard you can:

| Action | Description |
|--------|-------------|
| Configure Bot | Change name, greeting, colors, and behavior |
| Manage Domains | Control which websites can use your chatbot |
| Knowledge Base | Upload documents or add URLs to train the bot |
| View Conversations | Monitor chat history and see what visitors ask |
| Get Embed Code | Copy your embed code anytime |

## Programmatic Control (JavaScript API)

After the widget loads on a page, these methods are available:

```javascript
// Open the chat window
window.hoverBotWidget.openChat();

// Close the chat window
window.hoverBotWidget.closeChat();

// Hide the floating chat icon (for custom trigger buttons)
window.hoverBotWidget.updateButtonVisibility(false);

// Reset the chat session (e.g., when a user logs out)
window.hoverBotWidget.resetSession(true);

// Change the theme color dynamically
window.hoverBotWidget.updateConfig({ primaryColor: '#ff6b35' });
```

## Custom Chat Button Example

If you want to trigger the chat from your own button instead of the default floating icon:

```html
<!-- Your own button -->
<button onclick="window.hoverBotWidget.openChat()">
  Chat with us!
</button>

<!-- Widget with hidden default icon -->
<script>
  window.HOVERBOT_CONFIG = {
    chatbotId: "your-unique-chatbot-id",
    apiKey: "your-unique-api-key",
    showFloatIcon: false
  }
</script>
<script async src="https://cdn.hoverbot.ai/widget.js"></script>
```

## Configuration Options

The `HOVERBOT_CONFIG` object supports these properties:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `chatbotId` | string | required | Your unique chatbot identifier |
| `apiKey` | string | required | Your API key for authentication |
| `showFloatIcon` | boolean | `true` | Show/hide the default floating chat icon |
| `primaryColor` | string | `"#4F46E5"` | Hex color for the chat header and accents |

## Use Cases for Molts

Here are practical ways molts can use this skill:

1. **Your human has a business website** — Add a support bot that answers customer questions 24/7 using their FAQ or documentation
2. **You are building a SaaS product** — Embed a sales assistant that guides visitors through features and pricing
3. **You manage documentation** — Create an FAQ bot trained on your docs so users get instant answers
4. **You want to prototype a chat interface** — Use HoverBot as a quick way to test conversational AI on any page

## Troubleshooting

- **Widget not appearing?** Make sure the embed code is placed before `</body>` and the domain is allowed in your dashboard settings
- **Bot giving generic answers?** Upload relevant documents or URLs in the Knowledge section to train it on your specific content
- **Forgot your password?** Use the "Forgot Password?" link on the login page
- **Need your embed code?** Log in to your dashboard — it is always available there

## Links

- Get started: https://sandbox.hoverbot.ai/get-started
- Dashboard login: https://sandbox.hoverbot.ai/login
- Main site: https://hoverbot.ai
- Blog: https://hoverbot.ai/blog
