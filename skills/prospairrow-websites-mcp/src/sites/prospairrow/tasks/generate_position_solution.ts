import { z } from "zod";
import { Capability, type TaskDefinition } from "../../../framework/types.js";
import { ProspairrowApiClient, pickCompany, pickProspectId, pickWebsite } from "./_api.js";
import { websiteToDomain } from "./_shared.js";

const inputSchema = z
  .object({
    prospect_id: z.string().min(1).optional(),
    company: z.string().min(1).optional(),
    website: z.string().url().optional(),
    diagnostics: z.boolean().default(false)
  })
  .superRefine((val, ctx) => {
    if (!val.prospect_id && !val.company && !val.website) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Provide prospect_id, company, or website." });
    }
  });

export const task: TaskDefinition = {
  taskId: "generate_position_solution",
  capability: Capability.WRITE,
  description: "Generate positioning messages for a Prospairrow prospect.",
  run: async (ctx, params) => {
    const parsed = inputSchema.safeParse(params ?? {});
    if (!parsed.success) {
      return { position_solution: null, errors: [parsed.error.message] };
    }

    const { prospect_id, company, website, diagnostics } = parsed.data;
    const apiInit = await ProspairrowApiClient.fromApiKey(ctx.apiKeys?.prospairrow ?? "");
    if (!apiInit.client) {
      return { position_solution: null, errors: [apiInit.error ?? "PROSPAIRROW_API_INIT_FAILED"] };
    }

    const api = apiInit.client;
    try {
      let targetId = prospect_id ?? null;

      if (!targetId) {
        const query = company ?? website ?? "";
        const search = await api.searchProspects(query, 5);
        if (!search.ok) {
          return {
            position_solution: null,
            errors: [`search_failed:${search.error ?? search.status}`],
            diagnostics: { mode: "api", apiBase: api.apiBase, usedApiKey: true, diagnosticsEnabled: diagnostics }
          };
        }

        const domain = websiteToDomain(website);
        const match =
          search.prospects.find((record) => {
            const c = pickCompany(record).toLowerCase();
            const w = pickWebsite(record).toLowerCase();
            return (
              (!!company && c === company.toLowerCase()) ||
              (!!domain && w.includes(domain))
            );
          }) ?? search.prospects[0];

        targetId = match ? pickProspectId(match) : null;
      }

      if (!targetId) {
        return {
          position_solution: null,
          errors: [`Prospect not found: ${[prospect_id, company, website].filter(Boolean).join(" | ")}`],
          diagnostics: { mode: "api", apiBase: api.apiBase, usedApiKey: true, diagnosticsEnabled: diagnostics }
        };
      }

      const result = await api.generatePositionSolution(targetId);
      if (!result.ok) {
        return {
          position_solution: null,
          errors: [`generate_position_solution_failed:${result.error ?? result.status}`],
          diagnostics: {
            mode: "api",
            apiBase: api.apiBase,
            usedApiKey: true,
            diagnosticsEnabled: diagnostics,
            prospectId: targetId,
            ...(diagnostics ? { raw: result.data } : {})
          }
        };
      }

      return {
        position_solution: result.data,
        errors: [],
        diagnostics: {
          mode: "api",
          apiBase: api.apiBase,
          usedApiKey: true,
          diagnosticsEnabled: diagnostics,
          prospectId: targetId
        }
      };
    } finally {
      await api.close();
    }
  }
};
