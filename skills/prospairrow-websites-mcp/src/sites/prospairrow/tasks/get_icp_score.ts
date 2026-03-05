import { z } from "zod";
import { Capability, type TaskDefinition } from "../../../framework/types.js";
import { ProspairrowApiClient } from "./_api.js";

const inputSchema = z.object({
  prospect_id: z.union([z.string().min(1), z.number().int().positive()]),
  force_rescore: z.boolean().default(false),
  diagnostics: z.boolean().default(false)
});

export const task: TaskDefinition = {
  taskId: "get_icp_score",
  capability: Capability.READ_ONLY,
  description: "Retrieve ICP score for a prospect id with optional force_rescore flag.",
  run: async (ctx, params) => {
    const parsed = inputSchema.safeParse(params ?? {});
    if (!parsed.success) {
      return { icp_score: null, errors: [parsed.error.message] };
    }

    const { prospect_id, force_rescore, diagnostics } = parsed.data;
    const apiInit = await ProspairrowApiClient.fromApiKey(ctx.apiKeys?.prospairrow ?? "");
    if (!apiInit.client) {
      return { icp_score: null, errors: [apiInit.error ?? "PROSPAIRROW_API_INIT_FAILED"] };
    }

    const api = apiInit.client;
    try {
      const result = await api.getIcpScore(String(prospect_id), { forceRescore: force_rescore });
      if (!result.ok) {
        return {
          icp_score: null,
          errors: [`get_icp_score_failed:${result.error ?? result.status}`],
          diagnostics: {
            mode: "api",
            apiBase: api.apiBase,
            usedApiKey: true,
            diagnosticsEnabled: diagnostics,
            prospect_id: String(prospect_id),
            force_rescore,
            ...(diagnostics ? { raw: result.data } : {})
          }
        };
      }

      return {
        icp_score: result.data,
        errors: [],
        diagnostics: {
          mode: "api",
          apiBase: api.apiBase,
          usedApiKey: true,
          diagnosticsEnabled: diagnostics,
          prospect_id: String(prospect_id),
          force_rescore
        }
      };
    } finally {
      await api.close();
    }
  }
};
