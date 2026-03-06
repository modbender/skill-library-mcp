/**
 * AI Course Agent - Main Entry Point
 *
 * OpenClaw Skill for auto-generating AI education courses.
 * Supports natural language input in Chinese.
 *
 * Usage:
 *   import { isCourseLessonRequest, processUserMessage } from 'ai-course-agent';
 *   if (isCourseLessonRequest(userInput)) {
 *     const response = await processUserMessage(userInput);
 *   }
 */

export {
  isCourseLessonRequest,
  processUserMessage,
  formatCourseResponse,
  handleCourseGenerationRequest,
} from "./integration";
export { generateCourse, parseCourseRequest } from "./agent";
export { generateTeacherNotes, gatherCurriculumContent } from "./utils";
export {
  login,
  createLessonPlan,
  acceptLessonPlan,
  generateLessonUrl,
} from "./edustem-api";
export type { CourseRequest, GeneratedCourseResponse } from "./agent";
export type {
  LoginResponse,
  CreateLessonPlanPayload,
  CreateLessonPlanResponse,
} from "./edustem-api";
