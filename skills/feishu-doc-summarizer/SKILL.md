---
name: feishu-doc-summarizer
description: Summarize Feishu/Lark cloud documents the user can read. Use when the user sends a Feishu doc link (docx or wiki) and expects an auto summary without extra instructions, or explicitly asks to summarize a Feishu document. Workflow: resolve wiki to docx, read doc content via feishu_doc, summarize using the user’s fixed summary schema from MEMORY.md, and send the summary back to the current chat.
---

# Feishu Doc Summarizer

## Overview

Given a Feishu/Lark document link (docx or wiki), read the document content and reply in-chat with a structured summary following the user’s fixed schema stored in MEMORY.md.

## Workflow

### 0) Input detection

- Trigger when the user message contains a Feishu/Lark **docx** link like:
  - `https://...larkoffice.com/docx/DOC_TOKEN`
- Also trigger when the user message contains a Feishu/Lark **wiki** link like:
  - `https://...larkoffice.com/wiki/WIKI_TOKEN`

The user may provide **no additional instructions**; default to summarizing.

### 1) Resolve link → doc token (if needed)

- If it is a **docx link**: extract `doc_token` directly.
- If it is a **wiki link**:
  - Use `feishu_wiki(action=get, token=wiki_token)` to resolve the underlying object.
  - If the object type is `docx`, extract its doc token.
  - If not docx, tell the user what type it is and what you can support.

### 2) Read document content

- Use `feishu_doc(action=read, doc_token=doc_token)` to retrieve the full document content.
- If permissions fail or content is empty, ask the user to confirm they granted read access.

### 3) Summarize with the fixed schema (from memory)

- Before drafting, retrieve the summary schema from memory (search MEMORY.md for “Feishu 云文档摘要偏好” / “固定模板”).
- Produce the summary strictly following the section order and rules in memory.
- **Citations**: In the “引用原文片段” section, only quote text that appears in the document; do not fabricate.

#### Long documents

If the document is very long:
1) Chunk by headings/paragraph groups, summarize each chunk briefly.
2) Merge chunk summaries into the final schema.
3) Keep “引用原文片段” short and representative.

### 4) Reply back to the user

- Send the final formatted summary back to the current conversation.
- Include the original link in “文档元信息/链接”.

## Output format (must follow memory)

Follow the user’s schema in MEMORY.md exactly; keep missing items as “无/未知” rather than removing sections.
