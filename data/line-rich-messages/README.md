# OpenClaw Skill: LINE Rich Messages

A comprehensive guide and template collection for sending interactive and visually rich messages on LINE using OpenClaw.

## Overview

This skill transforms your OpenClaw agent into a professional LINE assistant by enabling native UI capabilities like Flex Messages, buttons, and quick replies. It provides both high-level directives and low-level JSON templates for 100% reliable rendering.

## Key Features

- **Rich Directives**: Use simple tags like `[[buttons: ...]]` or `[[quick_replies: ...]]` to trigger UI elements.
- **Auto-Conversion**: Automatically turns Markdown tables and code blocks into elegant Flex cards.
- **Manual JSON Templates**: Pre-built Raw JSON for mission-critical UI that bypasses system converters.
- **File Delivery SOP**: Integrated workflow for delivering files via Google Drive buttons.
- **Scenario Decision Matrix**: Guidance on choosing the right UI element for the best user experience.

## ⚠️ Crucial UX Note: Copy-Paste Limitation

**Text within LINE Flex Messages (including tables and auto-converted replies) is NOT selectable or copyable on mobile or desktop clients.**

- **The Rule**: If you are sending data meant to be copied (e.g., SSH keys, tokens, long URLs), **send it as plain text**.
- **Avoid**: Do not use Markdown formatting or directives that trigger Flex conversion when the user needs to copy the output.

## Installation

Add this skill to your OpenClaw workspace:

1. Clone this repository into your `~/.openclaw/workspace/skills/` directory.
2. Ensure `channels.line.capabilities.inlineButtons` is set to `"all"` or `"dm"` in your `openclaw.json`.
3. Restart the OpenClaw gateway.

## Repository Structure

- `SKILL.md`: Main skill definition and core principles.
- `references/directives.md`: Detailed syntax for `[[tag]]` commands.
- `references/flex-templates.md`: Raw JSON templates for manual overrides.
- `references/decision-matrix.md`: When to use which UI element.
- `references/markdown-to-flex.md`: Guide on auto-formatting behaviors.
- `references/file-delivery.md`: Google Drive integration guide.

---
Created with ❤️ by 小蝦 (Xiaoxia) for the OpenClaw community.
