# LINE Markdown Auto-Conversion

OpenClaw's LINE plugin automatically transforms standard Markdown structures into beautiful **Flex Messages**. This is the recommended way to display non-interactive data.

## Markdown Tables
Markdown tables are converted into structured "Flex Bubbles".

- **Usage**: Summaries, stats, comparisons, or file lists.
- **Limit**: Avoid extremely wide tables (more than 3 columns) as they may look cramped on mobile.

**Example**:
| Plan | Price | Features |
| :--- | :--- | :--- |
| Basic | Free | 5 calls |
| Pro | $10 | Unlimited |

## Code Blocks
Text inside triple backticks is converted into a styled "Code Card".

- **Usage**: Sharing snippets, log output, or technical identifiers.
- **Benefit**: Improves readability and prevents LINE from stripping indentation.

**Example**:
```bash
openclaw gateway status
```

## Best Practices
1. **Combine with Directives**: You can send a Markdown table followed by a `[[buttons: ...]]` directive to offer actions related to that data.
2. **Alt Text**: Always ensure your primary text explains the card, as some older LINE clients might not render Flex content perfectly.
