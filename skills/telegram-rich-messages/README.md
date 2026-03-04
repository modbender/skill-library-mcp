# OpenClaw Skill: Telegram Rich Messages

A comprehensive guide and template collection for sending interactive and visually structured messages on Telegram using OpenClaw.

## Overview

This skill transforms your OpenClaw agent from a text-only chatbot into a professional Telegram assistant. It leverages Telegram's unique UI features like Inline Buttons, Monospace auto-copy, and direct media transfers while providing fail-safe strategies for maximum reliability.

## Key Features

- **Reliable Buttons**: Prioritizes using the `message` tool for 100% stable button rendering.
- **Smart Formatting**: Guides on using Markdown V2 and HTML, including Spoilers and Links.
- **Low-Friction Copy**: Deep integration with Telegram mobile's "Tap-to-Copy" feature for technical data.
- **CJK-Aware Layouts**: Specialized advice on using Bullet Lists instead of Tables to avoid Chinese/Japanese/Korean alignment issues.
- **Direct Media SOP**: Best practices for sending local files, voice notes, and video messages.

## 🚀 Core Principle: Low-Friction Interaction

**Typing is slow and error-prone.** This skill trains agents to always provide buttons or auto-copyable blocks whenever a choice or a data point is presented to the user.

## Installation

Add this skill to your OpenClaw workspace:

1. Clone this repository into your `~/.openclaw/workspace/skills/` directory.
2. Ensure `channels.telegram.capabilities.inlineButtons` is set to `"all"` or `"dm"` in your `openclaw.json`.
3. Restart the OpenClaw gateway.

## Repository Structure

- `SKILL.md`: Main skill definition and interaction principles.
- `references/decision-matrix.md`: When to use which Telegram UI element.
- `references/interactive-ui.md`: How to send stable buttons and keyboards.
- `references/formatting.md`: Guide on Markdown V2, Spoilers, and CJK alignment.
- `references/media-and-actions.md`: Sending files, stickers, and managing messages.

---
Created with ❤️ by 小蝦 (Xiaoxia) for the OpenClaw community.

---
*Last Sync Test: Sat Feb 21 05:56:32 UTC 2026*
