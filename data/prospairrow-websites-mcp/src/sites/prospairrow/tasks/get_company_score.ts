import { z } from "zod";
import { Capability, type TaskDefinition } from "../../../framework/types.js";
import { ProspairrowApiClient } from "./_api.js";

const inputSchema = z.object({
  prospect_id: z.union([z.string().min(1), z.number().int().positive()]),
  diagnostics: z.boolean().default(false)
});

export const task: TaskDefinition = {
  taskId: "get_company_score",
  capability: Capability.READ_ONLY,
  description: "Retrieve company score for a prospect id.",
  run: async (ctx, params) => {
    const parsed = inputSchema.safeParse(params ?? {});
    if (!parsed.success) {
      return { company_score: null, errors: [parsed.error.message] };
    }

    const { prospect_id, diagnostics } = parsed.data;
    const apiInit = await ProspairrowApiClient.fromApiKey(ctx.apiKeys?.prospairrow ?? "");
    if (!apiInit.client) {
      return { company_score: null, errors: [apiInit.error ?? "PROSPAIRROW_API_INIT_FAILED"] };
    }

    const api = apiInit.client;
    try {
      const result = await api.getCompanyScore(String(prospect_id));
      if (!result.ok) {
        return {
          company_score: null,
          errors: [`get_company_score_failed:${result.error ?? result.status}`],
          diagnostics: {
            mode: "api",
            apiBase: api.apiBase,
            usedApiKey: true,
            diagnosticsEnabled: diagnostics,
            prospect_id: String(prospect_id),
            ...(diagnostics ? { raw: result.data } : {})
          }
        };
      }

      return {
        company_score: result.data,
        errors: [],
        diagnostics: {
          mode: "api",
          apiBase: api.apiBase,
          usedApiKey: true,
          diagnosticsEnabled: diagnostics,
          prospect_id: String(prospect_id)
        }
      };
    } finally {
      await api.close();
    }
  }
};
