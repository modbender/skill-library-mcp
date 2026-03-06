# CourseForge Tool Reference

Complete reference for all CourseForge MCP tools.

## Courses

### `list_courses`

List all courses owned by the authenticated user

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `page` | number |  | Page number (default: 1) |
| `perPage` | number |  | Results per page (default: 20, max: 100) |
| `published` | boolean |  | Filter by published status |

### `create_course`

Create a new course

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `name` | string | ✅ | Course title |
| `description` | string |  | Course description |
| `language` | string |  | Language code (ISO 639-1, default: en) |
| `difficulty` | string |  | Course difficulty |
| `published` | boolean |  | Published status (default: false) |

### `get_course`

Get a specific course by ID

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |

### `update_course`

Update an existing course

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `name` | string |  | Course title |
| `description` | string |  | Course description |
| `difficulty` | string |  |  |
| `published` | boolean |  | Published status |

### `delete_course`

Delete a course

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |

### `get_course_settings`

Get course settings for a specific course. Returns all settings or filtered by category.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID to get settings for |
| `category` | string |  | Settings category to retrieve (default: all) |

### `update_course_settings`

Update course settings for a specific course. Can update individual fields or entire categories.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID to update settings for |
| `category` | string | ✅ | Settings category to update |
| `settings` | object | ✅ | Settings object with fields to update. Only include fields you want to change. |

## Modules

### `create_module`

Create a new module in a course

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Parent course ID |
| `name` | string | ✅ | Module name |
| `description` | string |  | Module description |
| `order` | number |  | Display order |
| `learningObjectives` | array |  | Array of learning objectives for this module |

### `update_module`

Update an existing module

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string | ✅ | Module ID |
| `name` | string |  | Module name |
| `description` | string |  | Module description |
| `order` | number |  | Display order |
| `learningObjectives` | array |  | Array of learning objectives for this module |

### `delete_module`

Delete a module from a course

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string | ✅ | Module ID |

### `reorder_modules`

Reorder modules in a course

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleIds` | array | ✅ | Ordered array of module IDs |

### `get_module`

Get a specific module by ID

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string | ✅ | Module ID |

## Lessons

### `create_lesson`

Create a new lesson in a module

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string | ✅ | Parent module ID |
| `name` | string | ✅ | Lesson name |
| `description` | string |  | Lesson description |
| `order` | number |  | Display order |
| `learningObjectives` | array |  | Array of learning objectives for this lesson |

### `get_lesson`

Get a specific lesson by ID. Returns the lesson with all content blocks.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string | ✅ | Module ID |
| `lessonId` | string | ✅ | Lesson ID |

### `update_lesson`

Update an existing lesson

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string | ✅ | Module ID |
| `lessonId` | string | ✅ | Lesson ID |
| `name` | string |  | Lesson name |
| `description` | string |  | Lesson description |
| `order` | number |  | Display order |
| `learningObjectives` | array |  | Array of learning objectives for this lesson |

### `delete_lesson`

Delete a lesson from a module

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string | ✅ | Module ID |
| `lessonId` | string | ✅ | Lesson ID |

### `reorder_lessons`

Reorder lessons in a module

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string | ✅ | Module ID |
| `lessonIds` | array | ✅ | Ordered array of lesson IDs |

### `move_lesson`

Move a lesson from one module to another within the same course. Updates lesson order in both source and target modules.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `sourceModuleId` | string | ✅ | Current module ID containing the lesson |
| `lessonId` | string | ✅ | Lesson ID to move |
| `targetModuleId` | string | ✅ | Target module ID |
| `targetPosition` | number |  | Position in target module (0-indexed, optional, defaults to end) |

### `duplicate_lesson`

Copy a lesson with all its content blocks to the same module or a different module. Creates a complete copy with new IDs.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID containing the lesson |
| `sourceModuleId` | string | ✅ | Module ID containing the source lesson |
| `sourceLessonId` | string | ✅ | Lesson ID to duplicate |
| `targetModuleId` | string |  | Target module ID (optional, defaults to same module) |
| `newTitle` | string |  | New lesson title (optional, defaults to "Copy of [original]") |

## Content Blocks

### `add_content_block`

Add a content block to a lesson.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string | ✅ | Module ID |
| `lessonId` | string | ✅ | Lesson ID |
| `block` | object | ✅ | Content block data. For flip cards: type "interactive", content.interactionType "flipcard", content.data.cards array. Fo |
| `position` | object |  | Where to insert the block. Omit to append at end. |

### `get_content_block`

Get a specific content block by ID. Returns the full block data including:

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string | ✅ | Module ID |
| `lessonId` | string | ✅ | Lesson ID |
| `blockId` | string | ✅ | Content block ID |

### `update_content_block`

Update an existing content block. Only include fields you want to change.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string | ✅ | Module ID |
| `lessonId` | string | ✅ | Lesson ID |
| `blockId` | string | ✅ | Content block ID |
| `updates` | object | ✅ | Fields to update. For image blocks, include content.size, content.crop, content.filters |

### `delete_content_block`

Delete a content block from a lesson. This permanently removes the block and its content.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string | ✅ | Module ID |
| `lessonId` | string | ✅ | Lesson ID |
| `blockId` | string | ✅ | Content block ID |

### `reorder_content_blocks`

Reorder content blocks in a lesson by providing the complete ordered list of block IDs.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string | ✅ | Module ID |
| `lessonId` | string | ✅ | Lesson ID |
| `blockIds` | array | ✅ | Ordered array of block IDs |

### `move_content_block`

Move a content block to a new position within the same lesson or to a different lesson.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string | ✅ | Source module ID |
| `lessonId` | string | ✅ | Source lesson ID |
| `blockId` | string | ✅ | Content block ID to move |
| `targetModuleId` | string |  | Target module ID (optional, defaults to source module) |
| `targetLessonId` | string |  | Target lesson ID (optional, defaults to source lesson) |
| `position` | object | ✅ | Where to place the block in the target lesson |

## Course Management

### `validate_course`

Validate course readiness for export. Runs comprehensive checks including:

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID to validate |
| `wcagLevel` | string |  | WCAG compliance level to check (default: AA) |
| `checkTypes` | array |  | Specific check types to run (optional, runs all if not specified) |

### `duplicate_module`

Copy a module with all its lessons and content blocks. Creates a complete copy with new IDs for the module and all lessons.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID containing the module |
| `sourceModuleId` | string | ✅ | Module ID to duplicate |
| `newTitle` | string |  | New module title (optional, defaults to "Copy of [original]") |

### `export_course`

Export course to various e-learning formats:

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID to export |
| `format` | string | ✅ | Export format |
| `options` | object |  | Export options |

## Knowledge Library

### `list_collections`

List all knowledge collections owned by the authenticated user. Collections organize documents for use in AI responses.

### `create_collection`

Create a new knowledge collection to organize documents

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `name` | string | ✅ | Collection name (e.g., "Medical Terminology", "Company Policies") |
| `description` | string |  | Collection description (optional) |
| `color` | string |  | Hex color code for visual organization (optional, default: #3B82F6) |

### `list_documents`

List all documents in a specific knowledge collection

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `collectionId` | string | ✅ | Collection ID |

### `delete_document`

Delete a document from the knowledge library

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `documentId` | string | ✅ | Document ID to delete |

### `search_knowledge`

Search the knowledge library for relevant information using semantic search. Returns document chunks most similar to the query.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `query` | string | ✅ | Search query or question |
| `collectionIds` | array |  | Collection IDs to search (optional, searches all if not provided) |
| `topK` | number |  | Number of results to return (default: 5, max: 20) |

## AI & Generation

### `ai_chat_assistant`

Chat with the AI instructional designer assistant for help with course creation, content suggestions, and pedagogical guidance

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `message` | string | ✅ | Your message or question for the AI assistant |
| `context` | object |  | Optional context about the current course, module, or lesson being worked on |
| `conversationHistory` | array |  | Previous messages in the conversation |

### `ai_chat_with_research`

Full conversational AI with optional web research capabilities. Use this for complex content creation, research-backed suggestions, and instructional design guidance.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `message` | string | ✅ | Your message or question |
| `courseContext` | object |  | Optional context about the current course |
| `enableResearch` | boolean |  | Enable web research for current information (default: false) |
| `conversationId` | string |  | Optional conversation ID for context continuity |

### `analyze_image`

Analyze an image using Claude vision for content suggestions, quality checks, or accessibility improvements.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `imageUrl` | string |  | URL of image to analyze |
| `imageBase64` | string |  | Base64 encoded image data (alternative to URL) |
| `prompt` | string | ✅ | What to analyze about the image |

### `auto_fix_quality_issues`

Automatically fix quality issues in a course such as missing alt text, placeholder content, and accessibility problems.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `issues` | array |  | Specific issues to fix (from validate_course) |
| `fixAll` | boolean |  | Fix all detected auto-fixable issues (default: false) |

### `convert_document_to_pdf`

Convert PowerPoint, Word, or Excel documents to PDF for preview or download.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `sourceUrl` | string | ✅ | Firebase Storage URL of the document |

### `delete_storage_file`

Delete a file from Firebase Storage. Use this to clean up generated images or old exports.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `filePath` | string |  | Full storage path to the file (e.g., "courses/abc123/images/image.png") |
| `downloadUrl` | string |  | Download URL of the file (alternative to filePath) |

### `fetch_url_content`

Fetch and extract content from URLs for use in course creation. Supports up to 3 URLs at once.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `urls` | array | ✅ | URLs to fetch (max 3) |

### `generate_course_outline`

Generate a complete course outline including modules, lessons, and learning objectives using AI.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `topic` | string | ✅ | Course topic |
| `targetAudience` | string |  | Target audience description |
| `duration` | string |  | Expected course duration (e.g., "2 hours", "1 week") |
| `learningObjectives` | array |  | High-level learning objectives (optional) |
| `style` | string |  | Course style (default: professional) |

### `generate_image`

Generate custom images using AI (Gemini 2.5) for course content. Images are automatically uploaded to Firebase Storage.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `prompt` | string | ✅ | Detailed description of the image to generate (be specific about style, composition, mood, colors) |
| `courseId` | string | ✅ | Course ID (for organizing uploads) |
| `lessonId` | string | ✅ | Lesson ID (for organizing uploads) |
| `aspectRatio` | string |  | Image aspect ratio (default: 16:9) |
| `numberOfImages` | number |  | Number of images to generate (default: 1, max: 4) |
| `context` | string |  | Additional context for better alt text generation |

### `generate_job_aid_pdf`

Generate a professionally formatted PDF job aid from step-by-step instructions.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `title` | string | ✅ | Job aid title |
| `description` | string |  | Job aid description (optional) |
| `steps` | array | ✅ | Steps for the job aid |
| `courseId` | string |  | Course ID for file organization (optional) |
| `lessonId` | string |  | Lesson ID for file organization (optional) |

### `generate_lesson_content`

Generate content for a lesson using AI based on topic and learning objectives

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string | ✅ | Module ID |
| `lessonId` | string | ✅ | Lesson ID |
| `topic` | string | ✅ | Lesson topic |
| `learningObjectives` | array |  | Learning objectives |

### `generate_quiz_from_content`

Auto-generate quiz questions from existing lesson content.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `lessonId` | string | ✅ | Lesson ID to generate quiz from |
| `questionCount` | number |  | Number of questions (default: 5) |
| `questionTypes` | array |  | Types of questions to generate |

### `get_openapi_spec`

Get the OpenAPI 3.0 specification for the CourseForge REST API

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `format` | string |  | Output format (default: json) |

### `get_storage_usage`

Get storage usage statistics for the user's account.

### `get_youtube_captions`

Extract captions/transcript from a YouTube video for accessibility or content creation.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `videoId` | string | ✅ | YouTube video ID |
| `language` | string |  | Language code (default: en) |

### `get_youtube_metadata`

Get detailed metadata for a YouTube video including duration, captions availability, and channel info.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `videoUrl` | string | ✅ | YouTube video URL or video ID |

### `list_storage_files`

List files stored in the user's Firebase Storage. Use this to see generated images, exports, and other uploaded files.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `category` | string |  | Category of files to list (default: all) |
| `courseId` | string |  | Filter files by course ID (optional) |
| `limit` | number |  | Maximum number of files to return (default: 50, max: 200) |

### `manage_knowledge_files`

Manage files in the Knowledge Library - move between collections or remove from library.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `action` | string | ✅ | Action to perform |
| `documentId` | string | ✅ | Knowledge document ID to manage |
| `targetCollectionId` | string |  | Target collection ID (required for move action) |

### `marketing_support_chat`

Chat with the marketing support assistant for questions about CourseForge features, pricing, documentation, and general support

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `message` | string | ✅ | Your question or support request |
| `page` | string |  | Current page context (e.g., "pricing", "features", "docs", "faq") |
| `conversationHistory` | array |  | Previous messages in the conversation |

### `scrape_web_to_knowledge`

Scrape web page content and add it to a knowledge collection for AI reference.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `url` | string | ✅ | URL to scrape |
| `collectionId` | string | ✅ | Knowledge collection ID to add the content to |

### `search_user_media`

Search the user's existing images by description, prompt, or tags. Use this before generating new images to find and reuse existing relevant images.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `query` | string | ✅ | Search query (description, prompt keywords, or concept) |
| `courseId` | string |  | Filter to specific course (optional) |
| `category` | string |  | Filter by image category (default: all) |
| `limit` | number |  | Maximum results to return (default: 10, max: 50) |

### `suggest_improvements`

Get AI suggestions for improving course content, engagement, accessibility, or assessments.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string |  | Course ID |
| `moduleId` | string |  | Module ID (optional, narrows focus) |
| `lessonId` | string |  | Lesson ID (optional, narrows focus) |
| `focusArea` | string |  | Area to focus suggestions on |

### `summarize_document`

Summarize a knowledge library document into key points.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `documentId` | string | ✅ | Knowledge document ID |
| `summaryLength` | string |  | Length of summary (default: standard) |

### `translate_content`

Translate course content to another language.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `contentId` | string | ✅ | ID of the content to translate |
| `contentType` | string | ✅ | Type of content |
| `targetLanguage` | string | ✅ | Target language code (e.g., "es", "fr", "de") |

### `upload_to_knowledge`

Upload or add a file to a Knowledge Library collection for use in AI-powered course creation.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `collectionId` | string | ✅ | Target Knowledge Library collection ID |
| `fileUrl` | string |  | URL of existing file to add (Firebase Storage URL or external) |
| `base64Data` | string |  | Base64-encoded file content (alternative to fileUrl) |
| `fileName` | string |  | Name for the file (required with base64Data) |
| `contentType` | string |  | MIME type (required with base64Data) |
| `description` | string |  | Optional description of the document content |

### `web_search`

Search the web for current information to include in course content. Useful for research, fact-checking, and finding up-to-date information.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `query` | string | ✅ | Search query |
| `numResults` | number |  | Number of results (default: 5, max: 10) |
| `category` | string |  | Search category filter |

## Search & Media

### `search_stock_media`

Search for stock photos and videos from Pexels and Pixabay. Use this to find relevant, high-quality images and videos for course content. Choose this over AI image generation for real-world photography, generic concepts, and professional imagery.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `query` | string | ✅ | Search query (e.g., "teamwork", "coding laptop", "classroom learning") |
| `mediaType` | string |  | Type of media to search for (default: photo) |
| `provider` | string |  | Specific provider to search or "all" for combined results (default: all) |
| `count` | number |  | Number of results per provider (default: 3, max: 10) |
| `orientation` | string |  | Image/video orientation preference (optional) |

### `search_youtube`

Search YouTube videos for embedding in courses. Returns videos with metadata, thumbnails, and caption availability. Use this to find educational videos, tutorials, and demonstrations to enhance course content.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `query` | string | ✅ | Search query (e.g., "React hooks tutorial", "project management basics") |
| `maxResults` | number |  | Maximum results to return (1-12, default: 5) |
| `order` | string |  | Sort order: relevance (default), date (newest), viewCount (popular), rating (top rated) |
| `videoDuration` | string |  | Filter by duration: any (default), short (<4min), medium (4-20min), long (>20min) |
| `captionedOnly` | boolean |  | Only return videos with captions/subtitles (default: false) |

## Recordings

### `list_recordings`

List user recordings from Chrome Extension Capture. Use these recordings to create walkthrough, simulation, or recording content blocks in courses. Recordings contain step-by-step workflow captures with screenshots and optional video.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `limit` | number |  | Maximum number of recordings to return (default: 20, max: 50) |
| `status` | string |  | Filter by recording status (default: ready) |

## API Keys

### `list_api_keys`

List all API keys for the authenticated user

### `create_api_key`

Create a new API key

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `name` | string | ✅ | API key name/description |

### `revoke_api_key`

Revoke an existing API key

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `keyId` | string | ✅ | API key ID to revoke |

## Skills

### `list_skills`

List all available CourseForge skills. Skills are domain-specific expertise modules that provide guidance for creating training content in specific fields.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `category` | string |  | Filter skills by category (default: all) |

### `get_skill`

Get the full content of a specific CourseForge skill. Returns the complete skill definition including role, capabilities, module structures, best practices, and recommended tools.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `skillId` | string | ✅ | Skill ID (e.g., "course-builder", "salesforce-specialist", "ocm-specialist") |

## Agentic UI Control

### `add_annotation`

Add a temporary visual annotation to a content block.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string | ✅ | Module ID |
| `lessonId` | string | ✅ | Lesson ID |
| `blockId` | string | ✅ | Block ID to annotate |
| `type` | string | ✅ | Annotation type (affects color/style) |
| `note` | string |  | Annotation note/message |

### `close_preview`

Close the course preview modal and return to the editor.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |

### `create_checkpoint`

Create a named checkpoint of the current course state for potential rollback.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `name` | string | ✅ | Checkpoint name (for later reference) |
| `description` | string |  | Optional description of what the checkpoint captures |

### `expand_sidebar_item`

Expand or collapse a module in the sidebar to show/hide its lessons.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string | ✅ | Module ID to expand/collapse |
| `expanded` | boolean | ✅ | true to expand, false to collapse |

### `focus_content_block`

Focus the editor on a specific content block, opening it for editing if applicable.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string | ✅ | Module ID |
| `lessonId` | string | ✅ | Lesson ID |
| `blockId` | string | ✅ | Block ID to focus |
| `openEditor` | boolean |  | Open the block editor if available (default: false) |

### `get_canvas_state`

Get the current state of the course editor canvas.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |

### `highlight_issues`

Highlight multiple quality issues across the course with visual indicators.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `issues` | array | ✅ | Issues to highlight |

### `list_checkpoints`

List all available checkpoints for a course.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |

### `lock_canvas`

Lock the course editor canvas to prevent user edits while MCP is making changes.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID to lock |
| `message` | string |  | Message to display to user (e.g., "Creating modules...", "Adding content...") |

### `notify_user`

Send a toast notification to the user. Use this to communicate progress, completion, warnings, or errors.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID (for routing to correct editor instance) |
| `message` | string | ✅ | Notification message |
| `type` | string |  | Notification type (default: info) |
| `duration` | number |  | Duration in milliseconds (default: 4000, use 0 for persistent) |

### `open_preview`

Open the course preview modal to show the user how the course looks to learners.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `startAt` | object |  | Where to start the preview (optional) |

### `open_settings`

Open the course settings dialog.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `tab` | string |  | Settings tab to open (optional) |

### `refresh_canvas`

Force the course editor to refresh and reload the latest course data from the database.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID to refresh |

### `remove_annotation`

Remove a specific annotation or all annotations from a block/lesson/course.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `blockId` | string |  | Block ID to remove annotation from (optional) |
| `lessonId` | string |  | Remove all annotations from lesson (optional) |
| `clearAll` | boolean |  | Remove all annotations from course (default: false) |

### `request_choice`

Present the user with multiple options to choose from.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `title` | string | ✅ | Dialog title |
| `message` | string | ✅ | Explanation of the choice |
| `options` | array | ✅ | Available options |
| `allowCancel` | boolean |  | Allow user to cancel (default: true) |

### `request_confirmation`

Ask the user for confirmation before performing a destructive or significant operation.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `title` | string | ✅ | Dialog title |
| `message` | string | ✅ | Detailed explanation of what will happen |
| `confirmLabel` | string |  | Confirm button text (default: "Confirm") |
| `cancelLabel` | string |  | Cancel button text (default: "Cancel") |
| `isDestructive` | boolean |  | If true, styles confirm button as destructive (red) |

### `rollback_to_checkpoint`

Restore the course to a previously created checkpoint.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `checkpointName` | string | ✅ | Name of checkpoint to restore |

### `scroll_to_element`

Scroll the editor viewport to a specific element (module, lesson, or content block).

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `elementType` | string | ✅ | Type of element to scroll to |
| `elementId` | string | ✅ | ID of the element |
| `highlight` | boolean |  | Briefly highlight the element after scrolling (default: true) |

### `select_element`

Select a module, lesson, or content block in the editor sidebar/canvas.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `moduleId` | string |  | Module ID (selects module if only this provided) |
| `lessonId` | string |  | Lesson ID (selects lesson, requires moduleId) |
| `blockId` | string |  | Block ID (selects block, requires moduleId and lessonId) |

### `show_progress`

Display a progress indicator for multi-step operations.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `message` | string |  | Current operation description |
| `total` | number |  | Total number of steps |
| `current` | number |  | Current step (0-indexed) |
| `isComplete` | boolean |  | Set true to dismiss the progress indicator |

### `toggle_sidebar`

Show or hide the course structure sidebar.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID |
| `visible` | boolean | ✅ | true to show, false to hide |

### `unlock_canvas`

Unlock the course editor canvas to allow user edits again.

| Param | Type | Req | Description |
|-------|------|-----|-------------|
| `courseId` | string | ✅ | Course ID to unlock |

