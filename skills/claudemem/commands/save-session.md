---
description: Save a structured summary of the current conversation to persistent memory
argument-hint: Optional title for the session
---

Save this conversation as a structured session summary using claudemem.

## Instructions

1. Review the ENTIRE conversation history from this session
2. Generate a comprehensive session summary with these sections:
   - **Summary**: 1-2 paragraphs of what was accomplished
   - **Key Decisions**: Important choices made with rationale
   - **What Changed**: Files modified with descriptions
   - **Problems & Solutions**: Issues encountered and how they were resolved
   - **Questions Raised**: Open items for future sessions
   - **Next Steps**: Follow-up tasks as a checklist

3. Determine the git branch and project path from the current working directory

4. Save using this command (pipe the markdown content via stdin):
```bash
printf '<your generated markdown>' | claudemem session save \
  --title "<concise title describing the session>" \
  --branch "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')" \
  --project "$(pwd)" \
  --session-id "$(date +%Y%m%d-%H%M%S)" \
  --tags "<relevant,comma,separated,tags>"
```

5. After saving, display:
   - The session title and ID
   - A brief summary of what was captured
   - How many notes were also saved during this session (check with `claudemem stats`)

If the user provided a title argument, use it. Otherwise, generate a descriptive title from the conversation content.
