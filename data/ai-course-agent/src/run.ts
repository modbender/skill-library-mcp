import { processUserMessage, isCourseLessonRequest } from "./integration";

const userInput = "帮我创建一个七年级语文从百草园到三味书屋的课程";

async function main() {
  console.log(`\n[User] ${userInput}\n`);

  if (!isCourseLessonRequest(userInput)) {
    console.log("[Agent] Not a course request");
    return;
  }

  console.log("[Agent] 🎓 Course request detected! Processing...\n");

  const response = await processUserMessage(userInput);
  console.log(`[Agent Response]\n${response}\n`);
}

main().catch(console.error);
