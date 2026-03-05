# Main Session Integration Guide

## How to Integrate into OpenClaw Main Session

### Method 1: Direct Import (Recommended)

In your main session message handler, add this at the beginning:

```typescript
import {
  processUserMessage,
  isCourseLessonRequest,
} from "./agent/src/integration";

async function handleUserMessage(userInput: string) {
  // Check if this is a course generation request
  if (isCourseLessonRequest(userInput)) {
    console.log("🎓 Course generation request detected!");
    const response = await processUserMessage(userInput);
    return response;
  }

  // Otherwise, handle as normal conversation
  return await normalConversationHandler(userInput);
}
```

### Method 2: Spawn Sub-Agent (Alternative)

If you prefer isolation:

```typescript
import { sessions_spawn } from "../openclaw";

const result = await sessions_spawn({
  agentId: "course-generator",
  task: userInput,
});
```

### Supported Input Patterns

The system automatically detects these patterns:

✅ `"帮我生成6年级数学分数乘除法的课程"`
✅ `"帮我创建一个七年级语文从百草园到三味书屋的课程"`
✅ `"帮我制作9年级英语日常会话的课程"`
✅ `"生成8年级科学地球和宇宙的课程"`

### Expected Output

**Success Response:**

```
✅ 成功为6年级数学分数乘除法生成课程！

📚 **课程链接:**
https://6bb95bf119bf.ngrok-free.app/ai-lesson/356967b7-95dc-4619-9051-c121e36c4659
```

**Failure Response:**

```
❌ 生成课程失败: [error message]
```

## Files

- `src/integration.ts` - Main integration functions
  - `isCourseLessonRequest(message)` - Detect if input is a course request
  - `handleCourseGenerationRequest(userInput)` - Process the request
  - `processUserMessage(userInput)` - End-to-end processing with formatting

- `src/agent.ts` - Core course generation
  - `generateCourse(request)` - Execute the full flow

- `src/utils.ts` - Helpers
  - `gatherCurriculumContent()` - Gather course metadata
  - `generateTeacherNotes()` - Format teacher instructions

## Build & Deploy

```bash
# Build TypeScript
npm run build

# Test locally
npm run test

# Push to GitHub (already done)
git push origin main
```

## Next Steps

1. ✅ Agent code complete
2. ✅ Skill integration complete
3. ✅ Local testing working
4. ⏳ **TODO: Integrate into main session**
   - Copy/import `src/integration.ts` logic
   - Add to your message handler
   - Test with real user input

5. ⏳ Add web search for real curriculum content
6. ⏳ Improve NLP parsing for more complex inputs
