---
name: large-document-reader
description: |
  Intelligently splits long academic or technical documents into chapters, generates structured JSON summaries for each, and creates a file system with a global index. This enables efficient AI retrieval and analysis, perfectly solving context window limitations by enabling “overview via summaries, deep-dive on demand” workflows.
version: 1.0.0
author: Document Assistant
category: research
tags: [document-processing, knowledge-management, summarization, ai-optimization]
metadata: {}
---

# Literature Structuring Expert

Automatically decompose long documents (papers, reports, books) into a structured, AI-friendly knowledge base. Splits by chapter, generates machine-readable summaries, and builds a navigable index to overcome context limits.

## When to Use This Skill

Use this skill when the user:

- Has a document that is too long for the AI's context window.
- Needs to perform cross-chapter analysis or get a high-level overview of a long text.
- Wants to build a reusable, queryable knowledge base from a PDF, Markdown, or text file.
- Asks: "How can I get my AI to read this whole book/paper?"

## Quick Reference

| Situation | Action |
|-----------|--------|
| User provides a long document | 1. Analyze and split it into chapters.<br>2. Generate a JSON summary for each chapter.<br>3. Create a master index file. |
| User asks a high-level, cross-chapter question | Provide the content of the `MASTER_INDEX.md` file to the AI. |
| User asks a detailed, chapter-specific question | Provide the corresponding single file from the `./chapters/` directory to the AI. |
| Task completed | Present the generated file tree and `MASTER_INDEX.md` preview to the user. |

## Core Workflow

### Phase 1: Intelligent Splitting
1.  **Analyze Input**: Receive the long document text or file path.
2.  **Identify Structure**: Automatically analyze the document to identify heading hierarchies (e.g., `#`, `##`, `1.`, `1.1`) to determine chapter boundaries. Prioritize user-specified splitting preferences.
3.  **Execute Split**: Split the document into independent plain-text files by chapter.
    *   **Naming Convention**: `{sequence_number}_{chapter_title}.md` (e.g., `01_Introduction.md`).
    *   **Storage Location**: All chapter files are saved in the `./chapters/` directory.

### Phase 2: Summary Generation & Structuring
1.  **Generate Summary per Chapter**: For each file in `./chapters/`, generate a corresponding JSON summary file.
    *   **Structured Fields** (JSON format):
        ```json
        {
          "chapter_id": "Unique identifier matching the filename, e.g., 02_1",
          "chapter_title": "Chapter Title",
          "abstract": "Core summary of the chapter, 200-300 words.",
          "keywords": ["Keyword1", "Keyword2", "Keyword3"],
          "key_points": ["Key point one", "Key point two"],
          "related_sections": ["IDs of other chapters strongly related to this one"]
        }
        ```
    *   **Storage Location**: JSON summary files are saved in the `./summaries/` directory (e.g., `01_Introduction.summary.json`).

### Phase 3: Create Global Index
1.  **Aggregate Information**: Collect data from all JSON files in `./summaries/`.
2.  **Generate Index**: Create a global index file, `MASTER_INDEX.md`.
    *   **Content**: Lists all chapters' IDs, titles, a short abstract preview, and keywords in a Markdown list or table.
    *   **Purpose**: Provides a "bird's-eye view" for quick navigation and high-level Q&A.

## Final Deliverables & File Structure

Upon completion, the following file tree is generated:
```
Project_Root/
├── chapters/           # 【Source Repository】Contains all split chapter texts (.md files)
│   ├── 01_Introduction.md
│   ├── 02_1_Experimental_Methods.md
│   └── ...
├── summaries/          # 【Summary Repository】Contains all structured JSON summaries
│   ├── 01_Introduction.summary.json
│   ├── 02_1_Experimental_Methods.summary.json
│   └── ...
└── MASTER_INDEX.md     # 【Global Navigation】Core document summary index
```

## Usage Instructions for the User

**For Global, Cross-Chapter Queries** (e.g., “What is the paper's main thesis?”):
*   Provide the content of the `MASTER_INDEX.md` file to the AI. This is token-efficient.

**For Specific, In-Depth Queries Within a Chapter** (e.g., “What were the parameters in the 'Methods' section?”):
*   Provide the corresponding single chapter file from the `chapters/` directory to the AI for full context.
