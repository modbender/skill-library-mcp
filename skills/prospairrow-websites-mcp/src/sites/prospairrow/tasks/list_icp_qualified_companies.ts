import { z } from "zod";
import { Capability, type TaskDefinition } from "../../../framework/types.js";
import { ProspairrowApiClient, pickCompany, pickProspectId, pickWebsite } from "./_api.js";

const inputSchema = z.object({
  min_company_score: z.number().finite().min(0).max(100).default(40),
  min_icp_score: z.number().finite().min(0).max(100).optional(),
  per_page: z.number().int().positive().max(200).default(10),
  page: z.number().int().positive().default(1),
  diagnostics: z.boolean().default(false)
});

function pickNumber(record: Record<string, unknown>, keys: string[]): number | undefined {
  for (const key of keys) {
    const value = record[key];
    if (typeof value === "number" && Number.isFinite(value)) return value;
    if (typeof value === "string") {
      const parsed = Number(value);
      if (Number.isFinite(parsed)) return parsed;
    }
  }
  return undefined;
}

export const task: TaskDefinition = {
  taskId: "list_icp_qualified_companies",
  capability: Capability.READ_ONLY,
  description: "List ICP-qualified companies from Prospairrow with configurable min_company_score filtering.",
  run: async (ctx, params) => {
    const parsed = inputSchema.safeParse(params ?? {});
    if (!parsed.success) {
      return { qualified_companies: [], errors: [parsed.error.message] };
    }

    const { min_company_score, min_icp_score, per_page, page, diagnostics } = parsed.data;
    const apiInit = await ProspairrowApiClient.fromApiKey(ctx.apiKeys?.prospairrow ?? "");
    if (!apiInit.client) {
      return { qualified_companies: [], errors: [apiInit.error ?? "PROSPAIRROW_API_INIT_FAILED"] };
    }

    const api = apiInit.client;
    try {
      const result = await api.listIcpQualifiedProspects({
        minCompanyScore: min_company_score,
        minIcpScore: min_icp_score,
        perPage: per_page,
        page
      });

      if (!result.ok) {
        return {
          qualified_companies: [],
          errors: [`list_icp_qualified_failed:${result.error ?? result.status}`],
          diagnostics: {
            mode: "api",
            apiBase: api.apiBase,
            usedApiKey: true,
            diagnosticsEnabled: diagnostics,
            filters: { min_company_score, min_icp_score, per_page, page },
            ...(diagnostics ? { raw: result.raw } : {})
          }
        };
      }

      const qualifiedCompanies = result.prospects.map((record) => {
        const rec = record as Record<string, unknown>;
        return {
          id: pickProspectId(rec),
          company: pickCompany(rec),
          website: pickWebsite(rec),
          company_score: pickNumber(rec, ["company_score", "companyScore", "score", "company_fit_score"]),
          icp_score: pickNumber(rec, ["icp_score", "icpScore", "icp_fit_score"])
        };
      });

      return {
        qualified_companies: qualifiedCompanies,
        count: qualifiedCompanies.length,
        errors: [],
        diagnostics: {
          mode: "api",
          apiBase: api.apiBase,
          usedApiKey: true,
          diagnosticsEnabled: diagnostics,
          filters: { min_company_score, min_icp_score, per_page, page }
        }
      };
    } finally {
      await api.close();
    }
  }
};
