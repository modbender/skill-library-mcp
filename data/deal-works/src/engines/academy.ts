/**
 * Academy Engine - 3 tools
 * Learning platform for deal-making skills
 */

import { z } from "zod";
import type { Tool } from "@modelcontextprotocol/sdk/types.js";
import { getEngineClient } from "../client.js";

// Input schemas
const AcademyCoursesInputSchema = z.object({
  category: z.enum(["DEALS", "FINANCE", "LEGAL", "AGENTS", "BLOCKCHAIN"]).optional(),
  level: z.enum(["BEGINNER", "INTERMEDIATE", "ADVANCED"]).optional(),
  limit: z.number().min(1).max(100).default(20),
});

const AcademyEnrollInputSchema = z.object({
  courseId: z.string().min(1),
});

const AcademyTipInputSchema = z.object({
  courseId: z.string().min(1),
  amount: z.number().positive(),
  message: z.string().max(500).optional(),
});

// Tool definitions
export const academyTools: Tool[] = [
  {
    name: "academy_courses",
    description: "Browse available courses on the Academy platform.",
    inputSchema: {
      type: "object",
      properties: {
        category: {
          type: "string",
          enum: ["DEALS", "FINANCE", "LEGAL", "AGENTS", "BLOCKCHAIN"],
          description: "Filter by category",
        },
        level: {
          type: "string",
          enum: ["BEGINNER", "INTERMEDIATE", "ADVANCED"],
          description: "Filter by difficulty level",
        },
        limit: {
          type: "number",
          description: "Max courses to return",
          default: 20,
        },
      },
    },
  },
  {
    name: "academy_enroll",
    description: "Enroll in a course. Some courses may require payment.",
    inputSchema: {
      type: "object",
      properties: {
        courseId: {
          type: "string",
          description: "Course ID to enroll in",
        },
      },
      required: ["courseId"],
    },
  },
  {
    name: "academy_tip",
    description: "Tip a course creator to show appreciation.",
    inputSchema: {
      type: "object",
      properties: {
        courseId: {
          type: "string",
          description: "Course ID",
        },
        amount: {
          type: "number",
          description: "Tip amount in Talers",
        },
        message: {
          type: "string",
          description: "Optional thank-you message",
        },
      },
      required: ["courseId", "amount"],
    },
  },
];

// Tool handlers
export async function handleAcademyTool(
  name: string,
  args: Record<string, unknown>
): Promise<unknown> {
  const client = getEngineClient();

  switch (name) {
    case "academy_courses": {
      const input = AcademyCoursesInputSchema.parse(args);
      const params = new URLSearchParams();
      if (input.category) params.set("category", input.category);
      if (input.level) params.set("level", input.level);
      params.set("limit", String(input.limit));
      return client.fetch("academy", `/courses?${params.toString()}`);
    }

    case "academy_enroll": {
      const input = AcademyEnrollInputSchema.parse(args);
      return client.fetch("academy", `/courses/${input.courseId}/enroll`, {
        method: "POST",
        idempotencyKey: `enroll-${input.courseId}-${Date.now()}`,
      });
    }

    case "academy_tip": {
      const input = AcademyTipInputSchema.parse(args);
      return client.fetch("academy", `/courses/${input.courseId}/tip`, {
        method: "POST",
        body: { amount: input.amount, message: input.message },
        idempotencyKey: `tip-${input.courseId}-${Date.now()}`,
      });
    }

    default:
      throw new Error(`Unknown academy tool: ${name}`);
  }
}
