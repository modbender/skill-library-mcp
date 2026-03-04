---
name: clawbox-link-to-docs
description: "Turn a user shared web link into two Feishu docs: (1) full original text archive with minimal loss and clear source metadata, and (2) structured analysis summary. Use when the user sends an article/report/blog URL and asks for full text plus analysis, web archive plus brief, or link to knowledge capture."
---

# ClawBox Link to Docs

Execute this workflow when user sends a URL and expects both source doc and analysis doc.

## Workflow

1. Fetch source content
   - Try readable extraction from the URL.
   - If redirected or homepage only content is returned, switch to alternative extraction path (browser or manual source capture) before proceeding.
   - Preserve original language and paragraph order.

2. Create or update two Feishu docs
   - Doc A: [Source] <title>
   - Doc B: [Analysis] <title>

3. Write Source doc (complete first)
   - Include source URL and capture time.
   - Write full original text with paragraph breaks.
   - Do not replace with short summary.
   - If extraction is partial, label clearly: Partial Capture plus missing scope note.

4. Write Analysis doc (structured)
   - Use the template in references/analysis-template.md.
   - Keep concise and decision oriented.

5. Quality gates (required)
   - Read back both docs after write.
   - Source doc fails if it is one line, too short, or clearly summary like.
   - If fail, rewrite once with better segmentation/chunking.

6. Report back to user
   - Return two doc links.
   - State completion status: Full Capture or Partial Capture.

## Non-negotiables

- Default output is always two docs for a link task.
- Source doc priority is fidelity over formatting.
- Never claim full if content is truncated or fallback source is incomplete.
