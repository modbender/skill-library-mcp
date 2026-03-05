import { z } from "zod";
import { Capability, type TaskDefinition } from "../../../framework/types.js";
import { ProspairrowApiClient } from "./_api.js";

const inputSchema = z.object({
  positioning_intensity: z.number().finite().default(6),
  diagnostics: z.boolean().default(false)
});

export const task: TaskDefinition = {
  taskId: "generate_content_marketing",
  capability: Capability.WRITE,
  description: "Generate Prospairrow content marketing output.",
  run: async (ctx, params) => {
    const parsed = inputSchema.safeParse(params ?? {});
    if (!parsed.success) {
      return { content_marketing: null, errors: [parsed.error.message] };
    }

    const { positioning_intensity, diagnostics } = parsed.data;
    const apiInit = await ProspairrowApiClient.fromApiKey(ctx.apiKeys?.prospairrow ?? "");
    if (!apiInit.client) {
      return { content_marketing: null, errors: [apiInit.error ?? "PROSPAIRROW_API_INIT_FAILED"] };
    }

    const api = apiInit.client;
    try {
      const result = await api.generateContentMarketing(positioning_intensity);
      if (!result.ok) {
        return {
          content_marketing: null,
          errors: [`generate_failed:${result.error ?? result.status}`],
          diagnostics: {
            mode: "api",
            apiBase: api.apiBase,
            usedApiKey: true,
            diagnosticsEnabled: diagnostics
          }
        };
      }

      return {
        content_marketing: result.data,
        errors: [],
        diagnostics: {
          mode: "api",
          apiBase: api.apiBase,
          usedApiKey: true,
          diagnosticsEnabled: diagnostics
        }
      };
    } finally {
      await api.close();
    }
  }
};
