import axios, { AxiosError } from "axios";
import FormData from "form-data";

const API_BASE_URL = "https://6bb95bf119bf.ngrok-free.app/api/v1";
const LESSON_BASE_URL = "https://6bb95bf119bf.ngrok-free.app/ai-lesson";

/**
 * Types
 */

export interface LoginResponse {
  status: number;
  message: string;
  data: {
    token: string;
  };
}

export interface CreateLessonPlanPayload {
  subject: string;
  year_level?: string;
  teaching_time_minutes?: string;
  topic: string;
  curriculum_text: string;
  elaborations: string;
  teacher_notes: string;
  concepts?: string;
  subject_specific_instructions?: string;
  sections?: Array<{
    title: string;
    artefact_types: string[];
  }>;
}

export interface CreateLessonPlanResponse {
  status: number;
  message: string | null;
  data: {
    lesson_ref: string;
    unit_ref: string | null;
    owner_ref: string;
    title: string;
    description: string;
    duration_minutes: number | null;
    seq_num: number;
    lesson_plan_ref: string;
    is_lesson_plan_accepted: boolean | null;
    lesson_type_name: string;
  };
  success: boolean;
}

export interface AcceptLessonPlanResponse {
  status: number;
  message: string | null;
  data: {
    lesson_ref: string;
    unit_ref: string | null;
    owner_ref: string;
    title: string;
    description: string;
    duration_minutes: number | null;
    seq_num: number;
    lesson_plan_ref: string;
    is_lesson_plan_accepted: boolean;
    lesson_type_name: string;
  };
  success: boolean;
}

/**
 * API Functions
 */

/**
 * Login to Edustem API and get JWT token
 */
export async function login(
  username: string,
  password: string,
): Promise<string> {
  try {
    const form = new FormData();
    form.append("username", username);
    form.append("password", password);

    const response = await axios.post<LoginResponse>(
      `${API_BASE_URL}/login/`,
      form,
      {
        headers: form.getHeaders(),
      },
    );

    if (response.data.status !== 200) {
      throw new Error(`Login failed with status ${response.data.status}`);
    }

    return response.data.data.token;
  } catch (error) {
    throw handleError("Login failed", error);
  }
}

/**
 * Create a lesson plan
 */
export async function createLessonPlan(
  token: string,
  payload: CreateLessonPlanPayload,
): Promise<CreateLessonPlanResponse> {
  try {
    // Build the metadata object with defaults
    const metadata = {
      subject: payload.subject,
      year_level: payload.year_level || "7",
      teaching_time_minutes: payload.teaching_time_minutes || "45",
      topic: payload.topic,
      curriculum_text: payload.curriculum_text,
      elaborations: payload.elaborations,
      teacher_notes: payload.teacher_notes,
      concepts: payload.concepts || "",
      subject_specific_instructions:
        payload.subject_specific_instructions || "",
      sections: payload.sections || [
        {
          title: "Focus the learning",
          artefact_types: [
            "LEARNING_INTENTIONS_AND_SUCCESS_CRITERIA",
            "HOOK_AND_LESSON_OPENING",
            "CONTENT_EXPLANATION",
            "PRESENTATION",
            "MULTIPLE_CHOICE_QUIZ",
            "WORKSHEETS",
          ],
        },
      ],
    };

    const response = await axios.post<CreateLessonPlanResponse>(
      `${API_BASE_URL}/ai-lesson/create/`,
      { metadata },
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      },
    );

    if (!response.data.success) {
      throw new Error(`Lesson plan creation failed: ${response.data.message}`);
    }

    return response.data;
  } catch (error) {
    throw handleError("Failed to create lesson plan", error);
  }
}

/**
 * Accept a lesson plan (confirm it)
 */
export async function acceptLessonPlan(
  token: string,
  lessonRef: string,
): Promise<AcceptLessonPlanResponse> {
  try {
    const form = new FormData();
    form.append("lesson_ref", lessonRef);

    const response = await axios.post<AcceptLessonPlanResponse>(
      `${API_BASE_URL}/ai-lesson/accept-lesson-plan/`,
      form,
      {
        headers: {
          ...form.getHeaders(),
          Authorization: `Bearer ${token}`,
        },
      },
    );

    if (!response.data.success) {
      throw new Error(`Accept lesson plan failed: ${response.data.message}`);
    }

    return response.data;
  } catch (error) {
    throw handleError("Failed to accept lesson plan", error);
  }
}

/**
 * Generate the lesson URL
 */
export function generateLessonUrl(lessonRef: string): string {
  return `${LESSON_BASE_URL}/${lessonRef}`;
}

/**
 * Error handling utility
 */
function handleError(context: string, error: unknown): Error {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<any>;
    const status = axiosError.response?.status;
    const message =
      axiosError.response?.data?.message ||
      axiosError.message ||
      "Unknown error";
    return new Error(`${context}: ${status ? `[${status}]` : ""} ${message}`);
  }

  if (error instanceof Error) {
    return new Error(`${context}: ${error.message}`);
  }

  return new Error(`${context}: ${String(error)}`);
}

/**
 * Export all functions and utilities
 */
export default {
  login,
  createLessonPlan,
  acceptLessonPlan,
  generateLessonUrl,
};
