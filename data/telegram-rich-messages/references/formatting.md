# Telegram Formatting Guide

OpenClaw automatically converts Markdown-style text into Telegram-compatible HTML. **Avoid using raw HTML tags** (like `<u>` or `<b>`) as they may be auto-escaped and displayed as literal text.

## Core Formatting (Recommended)
Use these Markdown-style markers for the most reliable rendering:

- **Bold**: `**text**`
- **Italic**: `_text_`
- **Strikethrough**: `~~text~~`
- **Spoiler (Hide text)**: `||text||` (Click to reveal)
- **Hyperlinks**: `[text](url)`

### ⚠️ Underline Limitation
Standard Markdown underline (`__text__`) is often rendered as **Bold** in this environment. Raw HTML `<u>` tags are usually escaped.
**Recommendation**: Use **Bold** or **Italic** for emphasis instead of Underline to ensure consistent rendering across all Telegram clients.

## Interactive Emojis
Sending certain single emojis will trigger animations on Telegram:
- **Dice**: `🎲` (Rolls a random number 1-6)
- **Slot Machine**: `🎰`
- **Other**: `🎯`, `🏀`, `⚽`, ` bowling`

## The "Auto-Copy" Trick (Monospace)
Telegram mobile clients have a unique feature: **Tapping a monospace block copies it to the clipboard.**

### Inline Code
Use backticks for short snippets:
`Your ID: ` `Ud3ceadc38...`

### Code Blocks
Use triple backticks for multi-line data or when you want a larger "tap area":
```text
Project: Apollo
Status: Active
Latest ID: ABC-123
```

## Lists and Tables
- **Lists (Recommended for CJK)**: Use standard bullet points (`-` or `*`). This is the most reliable way to display mixed-language content without alignment issues.
- **Tables**: Markdown tables are converted to monospaced text blocks. 
  - ⚠️ **CJK Alignment Issue**: In monospaced fonts, Chinese/Japanese/Korean characters and Emojis are usually "double-width" while Latin characters are "single-width". Standard Markdown tables often fail to align these correctly.
  - **Best Practice**: If your content contains Chinese characters or Emojis, **avoid tables** and use **Bullet Lists** instead for a cleaner look.
