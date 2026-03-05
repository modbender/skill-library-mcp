# Video Summary Prompt Template

Use this template to generate a structured summary from a video transcript. Replace the placeholders with actual values before sending to the AI.

---

## Prompt

You are an expert content analyst. Based on the following video transcript, generate a comprehensive structured summary in the same language as the transcript.

### Video Information

- **Title**: {{TITLE}}
- **URL**: {{URL}}
- **Duration**: {{DURATION}}
- **Platform**: {{PLATFORM}}

### Transcript

```
{{TRANSCRIPT}}
```

### Output Format

Please generate a summary in Markdown with the following structure:

---

# {{TITLE}}

## Basic Information

| Field | Value |
|-------|-------|
| Platform | {{PLATFORM}} |
| URL | {{URL}} |
| Duration | {{DURATION}} |

## Overview

> A 2-3 sentence high-level summary of the video content.

## Key Points

- Point 1
- Point 2
- Point 3
- ...

## Detailed Content

### Section 1: [Topic]

Detailed explanation of this section's content...

### Section 2: [Topic]

Detailed explanation of this section's content...

(Add more sections as needed based on the content structure)

## Notable Quotes

> "Quote 1" — Context

> "Quote 2" — Context

## Related Topics

- Topic 1: Brief description of how it relates
- Topic 2: Brief description of how it relates
- Topic 3: Brief description of how it relates

---

### Instructions

1. Write the summary in the **same language** as the transcript (Chinese transcript → Chinese summary, English → English).
2. Extract **all** important information — do not omit key details.
3. Use the speaker's actual words for the "Notable Quotes" section.
4. The "Detailed Content" sections should follow the video's natural structure/flow.
5. Keep the overview concise but make the detailed sections thorough.
6. If the video discusses technical topics, preserve technical terms accurately.
