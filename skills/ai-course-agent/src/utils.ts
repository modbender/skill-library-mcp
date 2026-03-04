/**
 * Utility functions for course generation
 */

import axios from "axios";

export interface LessonMetadata {
  subject: string;
  topic: string;
  curriculum_text: string;
  elaborations: string;
  teacher_notes: string;
}

/**
 * Generate teacher_notes with proper formatting
 *
 * CRITICAL: The teacher_notes must follow this exact format:
 * "我需要你帮我生成这个主题的课程内容，特别是需要讲解{{topic}}。...让学生参与度高。。。。。。。。。。。。"
 *
 * The 12 trailing dots (。) are REQUIRED and mark the end of the instruction.
 * System parses until it finds these dots. Missing them = malformed request!
 */
export function generateTeacherNotes(subject: string, topic: string): string {
  const dots = "。".repeat(12); // System expects exactly 12 dots
  return `我需要你帮我生成这个主题的课程内容，特别是需要讲解${topic}。这些需要在内容和练习题里都体现。用中文来写所有的内容，因为这将会被用来在《${subject}》课程上使用。让学生参与度高，更好理解课程内容。 ${dots}`;
}

/**
 * Fetch curriculum content
 *
 * This function gathers the curriculum_text and elaborations needed for the lesson plan.
 * Currently uses placeholder data; in production, this would:
 * - Search the web for curriculum standards
 * - Query an LLM for content generation
 * - Fetch from a curriculum database
 */
export async function gatherCurriculumContent(
  subject: string,
  topic: string,
  grade: string,
): Promise<LessonMetadata> {
  try {
    console.log(
      `[Utils] Gathering content for ${grade}年级 ${subject} - ${topic}`,
    );

    // In production, you could:
    // 1. Search web for curriculum info
    // 2. Query LLM for content generation
    // 3. Fetch from curriculum database

    // For now, generate placeholder content based on input
    const curriculum_text = generateCurriculumText(grade, subject, topic);
    const elaborations = generateElaborations(subject, topic);

    return {
      subject,
      topic,
      curriculum_text,
      elaborations,
      teacher_notes: generateTeacherNotes(subject, topic),
    };
  } catch (error) {
    console.error("[Utils] Error gathering curriculum content:", error);
    throw error;
  }
}

/**
 * Generate curriculum text (placeholder implementation)
 *
 * In production, this would fetch actual curriculum standards or generate via LLM.
 */
function generateCurriculumText(
  grade: string,
  subject: string,
  topic: string,
): string {
  const gradeText = `${grade}年级`;

  switch (subject) {
    case "数学":
      return `${gradeText}${subject}课程 - ${topic}

基础概念：
- ${topic}是${gradeText}${subject}的重要内容
- 学生需要掌握基本的计算方法
- 需要理解背后的数学原理

学习目标：
- 能够正确进行${topic}的运算
- 理解${topic}的算法原理
- 能够应用到实际问题中

难点：
- 理解${topic}的规则
- 正确处理特殊情况
- 应用到复杂问题`;

    case "语文":
      return `${gradeText}${subject}课程 - ${topic}

文章背景：
- ${topic}是${gradeText}${subject}阅读教学的经典课文
- 体现了${subject}的核心价值观和审美要求
- 对学生的语言发展和思维能力有重要意义

主要内容：
- 故事情节和人物塑造
- 语言特色和修辞手法
- 主题思想和文学价值

教学重点：
- 深入理解文章内涵
- 学习优美的语言表达
- 培养审美和批判能力`;

    case "英语":
      return `${gradeText}${subject}课程 - ${topic}

课程描述：
- ${topic}是${gradeText}${subject}的重要语法/话题
- 覆盖实用的日常表达
- 符合${gradeText}学生的语言水平

学习内容：
- 核心词汇和短语
- 语法结构和用法
- 实际交际场景

学习目标：
- 掌握${topic}的核心表达
- 能够在真实情境中应用
- 提高综合语言能力`;

    default:
      return `${gradeText}${subject}课程 - ${topic}

课程概览：
这是${gradeText}${subject}课程中关于${topic}的教学内容。

主要内容：
- ${topic}的基本概念
- 相关的关键知识点
- 实际应用场景

学习目标：
- 理解${topic}的核心内容
- 掌握相关的技能和方法
- 能够应用到实际中`;
  }
}

/**
 * Generate elaborations (支撑细节)
 *
 * Elaborations provide additional context and depth for the lesson.
 */
function generateElaborations(subject: string, topic: string): string {
  return `本课程对${topic}这一主题进行了深入的教学设计，包括：

1. 知识结构完整：从基础概念到应用实践，形成完整的知识体系
2. 循序渐进：按照学生的认知规律，由浅入深地组织教学内容
3. 理论与实践结合：不仅讲解理论知识，还提供大量的实例和练习
4. 多角度思考：从多个角度分析${topic}，帮助学生形成全面的理解
5. 学生中心：充分考虑学生的学习特点和兴趣，提高学习的主动性和参与度

通过本课程的学习，学生能够：
- 深刻理解${topic}的本质
- 掌握相关的知识和技能
- 学会用这些知识解决实际问题
- 培养终身学习的能力`;
}

/**
 * Validate curriculum metadata before sending to API
 */
export function validateMetadata(metadata: LessonMetadata): boolean {
  // Check required fields
  if (!metadata.subject || !metadata.topic) {
    console.error("[Utils] Missing required fields: subject or topic");
    return false;
  }

  // Check teacher_notes format (must end with dots)
  if (!metadata.teacher_notes.includes("。")) {
    console.error("[Utils] Invalid teacher_notes: missing required dots");
    return false;
  }

  // Check minimum content length
  if (metadata.curriculum_text.length < 50) {
    console.error("[Utils] curriculum_text is too short");
    return false;
  }

  return true;
}
