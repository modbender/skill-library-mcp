# AI Course Agent

An OpenClaw agent for generating AI education course content using the Edustem API.

## Overview

This agent handles course generation requests by:
1. **Parsing** user input to extract grade level, subject, and content
2. **Gathering** curriculum information via placeholder content
3. **Creating** a lesson plan via Edustem API using the `api-edustem-skill` Skill
4. **Accepting** the lesson plan to trigger course generation
5. **Returning** the generated course link

## Request Example

```
User: "帮我生成6年级数学分数乘除法的课程"

Agent:
1. Parses → grade: 6, subject: 数学, content: 分数乘除法
2. Gathers content (curriculum_text, elaborations, teacher_notes)
3. Calls Skill:
   - login(username, password) → token
   - createLessonPlan(token, metadata) → lesson_ref
   - acceptLessonPlan(token, lesson_ref) → confirmed
4. Returns → https://6bb95bf119bf.ngrok-free.app/ai-lesson/{lesson_ref}
```

## Architecture

```
User Request
  ↓
Agent (src/agent.ts)
  ├─ Parse input
  ├─ Gather curriculum
  ├─ Call Skill functions
  └─ Return course link
  ↓
Skill (api-edustem-skill)
  ├─ login()
  ├─ createLessonPlan()
  └─ acceptLessonPlan()
  ↓
Edustem API
```

## Installation

```bash
# Install dependencies
npm install

# Build TypeScript
npm run build

# Test locally
npm run test

# Run dev mode
npm run dev
```

## Usage

### Local Testing

```bash
npm run test
```

This runs local tests with sample course requests.

### In OpenClaw (Production)

```typescript
import { generateCourse, parseCourseRequest } from './agent';

// In your agent code:
const request = parseCourseRequest(userInput);
const result = await generateCourse(request);

if (result.success) {
  // Send result.courseLink to user
}
```

## Key Files

- **src/agent.ts** - Main orchestration logic
  - `generateCourse()` - Full flow from request to course link
  - `parseCourseRequest()` - Extract grade/subject/content from user input

- **src/utils.ts** - Helper functions
  - `gatherCurriculumContent()` - Fetch course metadata
  - `generateTeacherNotes()` - Format teacher instructions (with 12 trailing dots!)
  - `validateMetadata()` - Validate metadata before API call

- **src/test.ts** - Local test cases

## Important Notes

### Teacher Notes Format

The `teacher_notes` parameter has a **strict format requirement**:

```
"我需要你帮我生成这个主题的课程内容，特别是需要讲解{{topic}}。...让学生参与度高。。。。。。。。。。。。"
                                                                         ^12 dots required^
```

The **12 trailing dots (。)** are MANDATORY. The Edustem API uses them as an end-of-instruction marker. Missing them will cause the API to reject the request.

### Supported Subjects

- 数学 (Math)
- 语文 (Chinese)
- 英语 (English)
- 科学 (Science)
- 历史 (History)
- 地理 (Geography)
- 物理 (Physics)
- 化学 (Chemistry)
- 生物 (Biology)

### Input Format

User input should follow this pattern:
```
帮我生成{{grade}}年级{{subject}}{{content}}的课程
```

Example:
```
帮我生成6年级数学分数乘除法的课程
帮我创建一个七年级语文从百草园到三味书屋的课程
```

## Environment Variables

Configure credentials via environment variables (never hardcode!):

```bash
export EDUSTEM_USERNAME="your-email@example.com"
export EDUSTEM_PASSWORD="your-password"
```

Or use a `.env` file (not committed to git):
```
EDUSTEM_USERNAME=your-email@example.com
EDUSTEM_PASSWORD=your-password
```

## Error Handling

The agent handles these error cases:
- Failed to parse user input → Returns null
- Login failure → Returns error message
- Lesson plan creation failure → Returns API error
- Network errors → Returns error message with details

## Future Improvements

- [ ] Add web search for real curriculum content
- [ ] Implement LLM-based content generation
- [ ] Add caching for frequently requested courses
- [ ] Implement retry logic with exponential backoff
- [ ] Support more subjects and locales
- [ ] Add structured logging
- [ ] Move credentials to .env file
- [ ] Add input validation and sanitization

## Tech Stack

- **Language:** TypeScript
- **Runtime:** Node.js
- **HTTP:** axios
- **Skill:** api-edustem-skill

## License

MIT
