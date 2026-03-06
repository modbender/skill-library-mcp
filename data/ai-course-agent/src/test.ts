/**
 * Test file for local testing
 *
 * Run with: npm run test
 */

import { generateCourse, parseCourseRequest } from "./agent";

async function runTests() {
  console.log("=".repeat(60));
  console.log("AI Course Agent - Local Test");
  console.log("=".repeat(60));

  // Test cases
  const testCases = [
    "帮我生成6年级数学分数乘除法的课程",
    "帮我创建一个七年级语文从百草园到三味书屋的课程",
    "帮我生成9年级英语日常会话的课程",
  ];

  for (const testCase of testCases) {
    console.log(`\n📝 Input: "${testCase}"`);

    // Parse request
    const request = parseCourseRequest(testCase);
    if (!request) {
      console.log("❌ Failed to parse input");
      continue;
    }

    console.log(`✓ Parsed: ${JSON.stringify(request)}`);

    // Generate course
    console.log("⏳ Generating course...");
    const result = await generateCourse(request);

    if (result.success) {
      console.log(`✅ Success!`);
      console.log(`   Message: ${result.message}`);
      console.log(`   Link: ${result.courseLink}`);
      console.log(`   Lesson Ref: ${result.lessonRef}`);
    } else {
      console.log(`❌ Failed: ${result.message}`);
    }

    console.log("-".repeat(60));
  }

  console.log("\n✨ Test completed!");
}

// Run tests
runTests().catch(console.error);
