# Telegram UI Decision Matrix

Use this guide to choose the best UI element for your specific scenario.

| Scenario | Recommended UI | Why? |
| :--- | :--- | :--- |
| **Simple binary choice** (Yes/No, Confirm/Cancel) | **Inline Buttons** | Immediate feedback, keeps chat clean. |
| **Multi-choice navigation** (e.g., Settings menu) | **Inline Buttons** | Can lead to different actions/sub-menus without user typing. |
| **Guided input** (e.g., Choose a category) | **Inline Buttons** | Pre-defined options prevent typos and misinterpretation. |
| **Sharing sensitive/technical data** (IDs, Tokens) | **Monospace Block** | Tap-to-copy on mobile is the lowest friction way to extract data. |
| **Confirming a destructive action** (Delete, Clear) | **Inline Buttons** | Provides a physical safety gate before execution. |
| **Long lists of files/results** | **Markdown Table** | Renders as monospaced block; clean and structured. |
| **Frequent repetitive commands** | **Custom Menu Commands** | Available via the `/` menu; no need to remember syntax. |
| **Sending an image/PDF/File** | **Direct Media Send** | Native file support; user can preview/save instantly. |
| **Acknowledging a message** | **Reaction (Emoji)** | Low noise; shows the bot is working/received the info. |

## Friction Levels (Lower is better)
1. **Reaction** (0 friction) - Acknowledgment.
2. **Inline Button** (1 tap) - Decision making.
3. **Monospace Copy** (1 tap + 1 paste) - Data extraction.
4. **Text Reply** (Many taps) - High friction; avoid if possible.
