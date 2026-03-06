import { processUserMessage, isCourseLessonRequest } from "./integration";

const userInput = "帮我生成六年级数学分数乘除法的课程";

async function main() {
  console.log(`\n[语音识别] ${userInput}\n`);

  if (!isCourseLessonRequest(userInput)) {
    console.log("[Agent] 不是课程生成请求");
    return;
  }

  console.log("[Agent] 🎓 检测到课程生成请求！处理中...\n");

  const response = await processUserMessage(userInput);
  console.log(`[Agent 响应]\n${response}\n`);
}

main().catch(console.error);
