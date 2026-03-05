import { z } from "zod";
import { Capability, type TaskDefinition } from "../../../framework/types.js";
import { ProspairrowApiClient } from "./_api.js";

const inputSchema = z.object({
  prospect_id: z.union([z.string().min(1), z.number().int().positive()]),
  reveal: z.boolean().default(true),
  reveal_limit: z.number().int().positive().max(100).default(1),
  diagnostics: z.boolean().default(false)
});

export const task: TaskDefinition = {
  taskId: "apollo_enrich",
  capability: Capability.WRITE,
  description: "Run Apollo ICP enrichment for a prospect id with configurable reveal_limit.",
  run: async (ctx, params) => {
    const parsed = inputSchema.safeParse(params ?? {});
    if (!parsed.success) {
      return { apollo_enrich: null, errors: [parsed.error.message] };
    }

    const { prospect_id, reveal, reveal_limit, diagnostics } = parsed.data;
    const apiInit = await ProspairrowApiClient.fromApiKey(ctx.apiKeys?.prospairrow ?? "");
    if (!apiInit.client) {
      return { apollo_enrich: null, errors: [apiInit.error ?? "PROSPAIRROW_API_INIT_FAILED"] };
    }

    const api = apiInit.client;
    try {
      const result = await api.apolloIcpRun(String(prospect_id), {
        reveal,
        revealLimit: reveal_limit
      });

      if (!result.ok) {
        return {
          apollo_enrich: null,
          errors: [`apollo_enrich_failed:${result.error ?? result.status}`],
          diagnostics: {
            mode: "api",
            apiBase: api.apiBase,
            usedApiKey: true,
            diagnosticsEnabled: diagnostics,
            prospect_id: String(prospect_id),
            reveal,
            reveal_limit,
            ...(diagnostics ? { raw: result.data } : {})
          }
        };
      }

      return {
        apollo_enrich: result.data,
        errors: [],
        diagnostics: {
          mode: "api",
          apiBase: api.apiBase,
          usedApiKey: true,
          diagnosticsEnabled: diagnostics,
          prospect_id: String(prospect_id),
          reveal,
          reveal_limit
        }
      };
    } finally {
      await api.close();
    }
  }
};
