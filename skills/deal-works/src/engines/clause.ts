/**
 * Clause Engine - 1 tool
 * Contract clause rendering and templating
 */

import { z } from "zod";
import type { Tool } from "@modelcontextprotocol/sdk/types.js";
import { getEngineClient } from "../client.js";

// Input schemas
const ClauseRenderInputSchema = z.object({
  templateId: z.string().min(1),
  variables: z.record(z.union([z.string(), z.number(), z.boolean()])),
  format: z.enum(["HTML", "MARKDOWN", "PLAIN"]).default("MARKDOWN"),
});

// Tool definitions
export const clauseTools: Tool[] = [
  {
    name: "clause_render",
    description: "Render a contract clause template with provided variables. Returns formatted text.",
    inputSchema: {
      type: "object",
      properties: {
        templateId: {
          type: "string",
          description: "Clause template ID",
        },
        variables: {
          type: "object",
          description: "Variables to substitute in the template",
          additionalProperties: {
            oneOf: [
              { type: "string" },
              { type: "number" },
              { type: "boolean" },
            ],
          },
        },
        format: {
          type: "string",
          enum: ["HTML", "MARKDOWN", "PLAIN"],
          description: "Output format",
          default: "MARKDOWN",
        },
      },
      required: ["templateId", "variables"],
    },
  },
];

// Tool handlers
export async function handleClauseTool(
  name: string,
  args: Record<string, unknown>
): Promise<unknown> {
  const client = getEngineClient();

  switch (name) {
    case "clause_render": {
      const input = ClauseRenderInputSchema.parse(args);
      return client.fetch("clause", "/render", {
        method: "POST",
        body: input,
      });
    }

    default:
      throw new Error(`Unknown clause tool: ${name}`);
  }
}
