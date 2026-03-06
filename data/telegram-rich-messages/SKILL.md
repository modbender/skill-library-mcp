---
name: telegram-rich-messages
description: Comprehensive guide for Telegram Rich UI features (Inline buttons, formatting, media, reactions, and message management). Use this skill to provide a low-friction, interactive experience for Telegram users, prioritizing buttons over typing.
metadata:
  {
    "openclaw": { "requires": { "plugins": ["telegram"] } },
  }
---

# Telegram Rich Messages

This skill transforms the agent from a text-only chatbot into an interactive Telegram assistant.

## Core Principle: Low-Friction Interaction
**Typing is slow and error-prone.** Always prioritize Rich UI elements to minimize the user's need to reply with text. If a user has a choice to make, give them a button.

## Quick Navigation
Detailed guides for each feature:

1. **[decision-matrix.md](references/decision-matrix.md)**: When to use which UI element.
2. **[formatting.md](references/formatting.md)**: Markdown V2, HTML, and Auto-Copy (Monospace) tricks.
3. **[interactive-ui.md](references/interactive-ui.md)**: How to send stable Inline Buttons and Quick Replies.
4. **[media-and-actions.md](references/media-and-actions.md)**: Sending files, stickers, using reactions, and editing/deleting messages.

## Best Practices
- **Monospace for Data**: Use code blocks for IDs, addresses, or snippets. Users can tap to copy them instantly on mobile.
- **Stable Buttons**: Always use the `message` tool's `buttons` parameter instead of string directives (`[[buttons:...]]`) for 100% reliability.
- **Contextual Actions**: After completing a task, provide buttons for the most likely next steps (e.g., "Check Status", "Delete", "Settings").
- **Direct Uploads**: Telegram supports direct file uploads. No need for Google Drive or external hosting.
