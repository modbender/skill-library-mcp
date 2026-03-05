---
name: xmind
description: Generate and read XMind (.xmind) files via the published xmind-generator-mcp MCP server (npm), with a chat-first UX.
metadata:
  openclaw:
    emoji: "🧠"
    requires:
      bins: ["mcporter", "npx"]
    install:
      - id: npm
        kind: note
        label: "Uses npx xmind-generator-mcp@0.1.2 (no separate install needed)"
---

# xmind 🧠

Generate and read **XMind** `.xmind` files using the published MCP server `xmind-generator-mcp` (npm).

This skill is chat-first:
- “Generate an XMind for this (optionally: save to …)” → generates a `.xmind` and sends it back.
- “Read this XMind and tell me what it’s about” → explains the map first, then offers a Markdown export.

## When to use
- User wants: “generate an XMind file from this outline / plan / PRD / test plan”.
- Output should be a real `.xmind` file that opens in XMind.

## Input format (for generation)
The MCP tool `generate-mind-map` accepts **Schema A** JSON:
```json
{
  "title": "Root topic",
  "filename": "mindmap-name-no-date",
  "topics": [
    {
      "title": "Topic title (keep core info in the title)",
      "note": "Optional: use sparingly; only when the title would be too long",
      "labels": ["optional"],
      "markers": ["Arrow.refresh"],
      "children": [{"title": "Child topic"}]
    }
  ]
}
```

## How the assistant should call the MCP (stdio via mcporter)
### Generate XMind
Use `npx xmind-generator-mcp@0.1.2` as the MCP server command:
```bash
mcporter call --stdio "npx -y xmind-generator-mcp@0.1.2" generate-mind-map --args '{...}'
```

### Read XMind (Markdown export)
```bash
mcporter call --stdio "npx -y xmind-generator-mcp@0.1.2" read-mind-map --args '{"inputPath":"/path/to/file.xmind","style":"A"}'
```

## Read behavior in chat (UX requirement)
When a user sends an `.xmind` file and asks to “read/understand” it:
1) First, explain in detail what the mind map is about (summary + structure + key points + actionable items + gaps).
2) Only after that, ask whether the user wants an export.
3) If the user wants an export, default to **Markdown**.

- `generate --output` can be a directory (recommended) or a full `.xmind` path.
- If outputPath is omitted, the MCP server defaults to its configured `outputPath` environment variable (see below).

## Chat-first workflow (what the assistant should do)
Trigger phrases:
- “Generate an XMind for this” / “Make an XMind from this”
- “Read this XMind” / “Summarize this XMind”

Language rule (important):
- If the user does **not** explicitly specify the language of the generated mind map, **match the language of the user’s request**.
  - Example: user asks in Chinese → generate Chinese topic titles.
  - Example: user asks in English → generate English topic titles.
- Only switch languages if the user explicitly asks (e.g. “generate in English”).

Filename rule (important):
- If the user provides a filename/path, use it.
- If the user does **not** provide a filename:
  - Default filename should follow the user’s request language.
  - For Chinese: use short hyphen style, **no date** (e.g. `one-day-trip-detailed` in Chinese characters, but keep it short).
  - For English: use a short slug, no date (e.g. `hong-kong-1-day-itinerary`).
- Always sanitize invalid filename characters: `\\ / : * ? \" < > |` → replace with `-`.

Steps:
1) Parse whether the user specified a save location/path.
   - If specified, use that.
   - If not specified, default to `~/Desktop`.
2) Determine output language:
   - If user specified language → follow it.
   - Else → match the user’s message language.
3) Convert the user’s content into Schema A JSON (in the chosen language).
   - Keep it reasonably sized (avoid thousands of nodes in one go).
   - Use XMind enrichment elements when helpful (but keep titles informative):
     - `note`: **use sparingly**. Only put content in `note` when it would make the topic title too long or noisy. If the content is core to the plan, keep it in the title instead of hiding it in `note`.
     - `labels`: add lightweight categorization (e.g. must-do/optional/rainy-day/budget/family-friendly).
     - `relationships`: **sparingly** (mode A) — only for truly cross-branch links that add clarity.
4) Write the JSON to a temp file, e.g. `/tmp/xmind-<ts>.json`.
5) Call the MCP tool `generate-mind-map` via mcporter stdio (`npx xmind-generator-mcp@0.1.2`).
   Capture/compute the output file path.
6) **Send the generated `.xmind` back in chat as an attachment**.
7) Optionally also tell the user where it was saved on disk.
