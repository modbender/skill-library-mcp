---
name: courseforge
description: Create and manage online courses via the CourseForge API (caringcourseforge.com). Use when the user wants to create courses, modules, lessons, generate AI content, export to SCORM/xAPI, manage knowledge libraries, or interact with the CourseForge platform. Handles course building, content generation, quizzes, accessibility validation, and course export.
metadata:
  openclaw:
    emoji: "📚"
    requires:
      bins: ["node"]
      env: ["COURSEFORGE_API_KEY"]
    install:
      - id: npm
        kind: npm
        package: courseforge-mcp-client
        global: true
        bins: ["courseforge-mcp"]
        label: "Install CourseForge MCP client (npm)"
---

# CourseForge

Build and manage courses on [Caring CourseForge](https://caringcourseforge.com) via the MCP client.

**Source:** [npm — courseforge-mcp-client](https://www.npmjs.com/package/courseforge-mcp-client)
**Publisher:** Caring Consulting Co ([caringcos.com](https://caringcos.com))

## Setup

1. Install: `npm install -g courseforge-mcp-client`
2. Set `COURSEFORGE_API_KEY` in your environment:
   - Get your key: caringcourseforge.com → Settings → API Keys
   - **Store securely** via your gateway environment config or shell profile (`export COURSEFORGE_API_KEY=cf_prod_...`). Do not store API keys in plaintext workspace files.
3. Verify: `courseforge-mcp` starts without errors

## Calling Tools

Use the wrapper script to call any of the 89 CourseForge tools:

```bash
node scripts/courseforge.mjs <tool_name> '<json_args>'
```

The script requires `COURSEFORGE_API_KEY` in the environment (set via gateway env or shell profile).

```bash
node scripts/courseforge.mjs list_courses '{}'
```

Output is clean JSON (the MCP envelope is stripped automatically).

## Available Tools (89)

- **Courses** (7): `list_courses`, `create_course`, `get_course`, `update_course`, `delete_course`, `get_course_settings`, `update_course_settings`
- **Modules** (5): `create_module`, `update_module`, `delete_module`, `reorder_modules`, `get_module`
- **Lessons** (7): `create_lesson`, `get_lesson`, `update_lesson`, `delete_lesson`, `reorder_lessons`, `move_lesson`, `duplicate_lesson`
- **Content Blocks** (6): `add_content_block`, `get_content_block`, `update_content_block`, `delete_content_block`, `reorder_content_blocks`, `move_content_block`
- **Course Management** (3): `validate_course`, `duplicate_module`, `export_course`
- **Knowledge Library** (5): `list_collections`, `create_collection`, `list_documents`, `delete_document`, `search_knowledge`
- **AI & Generation** (26): `ai_chat_assistant`, `ai_chat_with_research`, `generate_course_outline`, `generate_lesson_content`, `generate_quiz_from_content`, `generate_image`, `generate_job_aid_pdf`, `suggest_improvements`, `auto_fix_quality_issues`, `translate_content`, `summarize_document`, `convert_document_to_pdf`, `analyze_image`, `marketing_support_chat`, `web_search`, `fetch_url_content`, `get_youtube_metadata`, `get_youtube_captions`, `scrape_web_to_knowledge`, `upload_to_knowledge`, `manage_knowledge_files`, `search_user_media`, `list_storage_files`, `delete_storage_file`, `get_storage_usage`, `get_openapi_spec`
- **Search & Media** (2): `search_stock_media`, `search_youtube`
- **Recordings** (1): `list_recordings`
- **API Keys** (3): `list_api_keys`, `create_api_key`, `revoke_api_key`
- **Skills** (2): `list_skills`, `get_skill`
- **Agentic UI Control** (22): `lock_canvas`, `unlock_canvas`, `refresh_canvas`, `notify_user`, `show_progress`, `request_confirmation`, `request_choice`, `scroll_to_element`, `select_element`, `expand_sidebar_item`, `focus_content_block`, `get_canvas_state`, `open_preview`, `close_preview`, `open_settings`, `toggle_sidebar`, `create_checkpoint`, `rollback_to_checkpoint`, `list_checkpoints`, `add_annotation`, `remove_annotation`, `highlight_issues`

For full parameter details on any tool, read `references/tools.md`.

## Common Workflows

### Create a course from scratch

1. `create_course` — title, description, difficulty (beginner/intermediate/advanced)
2. `create_module` — for each section, pass courseId
3. `create_lesson` — for each lesson, pass courseId + moduleId
4. `add_content_block` — add text, images, quizzes to lessons
5. `validate_course` — check quality and accessibility
6. `export_course` — export to SCORM 1.2, SCORM 2004, xAPI, or HTML

### AI-powered course generation

1. `generate_course_outline` — provide topic, audience, difficulty → get full structure
2. `create_course` + `create_module` + `create_lesson` — build the structure from the outline
3. `generate_lesson_content` — auto-generate content for each lesson
4. `generate_quiz_from_content` — create assessments from lesson content
5. `suggest_improvements` — get AI suggestions for quality
6. `auto_fix_quality_issues` — automatically fix issues

### Use domain skills for specialized content

1. `list_skills` — see all 17 available specialist skills
2. `get_skill` — load a skill (e.g., "Instructional Designer", "HR Specialist")
3. Use the skill context when generating content with `ai_chat_assistant`

### Export a course

```bash
node scripts/courseforge.mjs export_course '{"courseId":"xxx","format":"scorm12"}'
```

Formats: `scorm12`, `scorm2004`, `xapi`, `html`

### Content block types

When using `add_content_block`, the `type` field accepts:
- `text` — Rich text/HTML content
- `image` — Image with URL and alt text
- `video` — Embedded video (YouTube, Vimeo, URL)
- `quiz` — Interactive quiz/assessment
- `tabs` — Tabbed content sections
- `accordion` — Collapsible sections
- `callout` — Highlighted callout box
- `divider` — Visual separator
- `code` — Code block with syntax highlighting
- `embed` — External embed (iframe)
- `hotspot` — Interactive image hotspot
- `flashcard` — Flashcard for review
- `sortable` — Drag-and-drop sorting activity
- `timeline` — Timeline visualization
- `process` — Step-by-step process
- `labeled_graphic` — Image with labels
- `knowledge_check` — Quick knowledge check
- `scenario` — Branching scenario

## Notes

- All IDs are Firestore document IDs (alphanumeric strings)
- Courses have a hierarchy: Course → Modules → Lessons → Content Blocks
- The Knowledge Library stores reference documents that AI tools can use for generation
- Agentic UI Control tools require the user to have the course editor open in their browser
- Rate limits apply to AI generation tools based on the user's subscription tier
