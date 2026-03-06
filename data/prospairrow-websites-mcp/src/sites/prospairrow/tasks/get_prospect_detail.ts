import { z } from "zod";
import { Capability, type TaskDefinition } from "../../../framework/types.js";
import {
  clickByRoleOrText,
  ensureProspectWorkspace,
  ensureAuthenticated,
  extractIdFromText,
  findProspectRow,
  maybeCaptureDiagnostics,
  searchProspect,
  websiteToDomain
} from "./_shared.js";
import { ProspairrowApiClient, pickCompany, pickProspectId, pickWebsite } from "./_api.js";

const inputSchema = z
  .object({
    id: z.string().optional(),
    company: z.string().optional(),
    website: z.string().url().optional(),
    diagnostics: z.boolean().default(false)
  })
  .superRefine((val, ctx) => {
    if (!val.id && !val.company && !val.website) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Provide id, company, or website." });
    }
  });

function pickText(pageText: string, regex: RegExp): string | undefined {
  return pageText.match(regex)?.[1]?.trim();
}

export const task: TaskDefinition = {
  taskId: "get_prospect_detail",
  capability: Capability.READ_ONLY,
  description: "Retrieve detailed fields for a single prospect.",
  run: async (ctx, params) => {
    const parsed = inputSchema.safeParse(params ?? {});
    const errors: string[] = [];

    if (!parsed.success) {
      return { prospect: null, errors: [parsed.error.message] };
    }

    const { id, company, website, diagnostics } = parsed.data;
    const domain = websiteToDomain(website);
    const queries = [id, domain, website, company].filter((item): item is string => Boolean(item && item.trim()));

    const apiKeySet = Boolean(String(ctx.apiKeys?.prospairrow || "").trim());
    if (apiKeySet) {
      const apiInit = await ProspairrowApiClient.fromApiKey(ctx.apiKeys?.prospairrow ?? "");
      if (!apiInit.client) {
        return { prospect: null, errors: [apiInit.error ?? "PROSPAIRROW_API_INIT_FAILED"] };
      }

      const api = apiInit.client;
      try {
        let targetId = id ?? null;

        if (!targetId && company) {
          const search = await api.searchProspects(company, 5);
          if (!search.ok) {
            return { prospect: null, errors: [`search_failed:${search.error ?? search.status}`] };
          }

          const match = search.prospects.find((record) => {
            const c = pickCompany(record).toLowerCase();
            const w = pickWebsite(record).toLowerCase();
            return (!!company && c === company.toLowerCase()) || (!!domain && w.includes(domain));
          }) ?? search.prospects[0];

          targetId = match ? pickProspectId(match) : null;
        }

        if (!targetId) {
          return { prospect: null, errors: [`Prospect not found via API search: ${queries.join(" | ")}`] };
        }

        const detail = await api.getProspect(targetId);
        if (!detail.ok) {
          return { prospect: null, errors: [`detail_failed:${detail.error ?? detail.status}`] };
        }

        const [intel, strategy] = await Promise.all([
          api.getBusinessIntelligence(targetId),
          api.getSalesStrategy(targetId)
        ]);

        const d = detail.data;
        const prospect = {
          id: targetId,
          company: String(d.company || d.company_name || company || "").trim() || undefined,
          website: String(d.website || d.company_website || website || "").trim() || undefined,
          location: String(d.location || "").trim() || undefined,
          industry: String(d.industry || "").trim() || undefined,
          size: String(d.size || d.company_size || "").trim() || undefined,
          notes: String(d.notes || "").trim() || undefined,
          enrichment_status: d.enrichment_status,
          enrichment_summary: d.enrichment_summary,
          business_intelligence: intel.ok ? intel.data : null,
          sales_strategy: strategy.ok ? strategy.data : null
        };

        return {
          prospect,
          errors,
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

    try {
      await ctx.safeGoto(ctx.site.baseUrl);
      await ctx.page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => undefined);
      const auth = await ensureAuthenticated(ctx.page);
      if (!auth.ok) {
        return { prospect: null, errors: [auth.error ?? "AUTH_REQUIRED"] };
      }

      const workspace = await ensureProspectWorkspace(ctx.page, ctx.site.baseUrl);
      const scope = workspace.scope;

      if (!workspace.ok) {
        errors.push(JSON.stringify({ code: workspace.reason ?? "PROSPECT_WORKSPACE_NOT_FOUND", attempts: workspace.attempts }));
        const diagnosticsPayload = await maybeCaptureDiagnostics(ctx.page, scope, diagnostics, ctx.runId, "get_prospect_detail");
        if (diagnostics && diagnosticsPayload.context) {
          errors.push(JSON.stringify({ code: "DIAGNOSTICS_CONTEXT", context: diagnosticsPayload.context }));
        }

        return {
          prospect: null,
          errors,
          ...(diagnosticsPayload.screenshot ? { diagnostics: diagnosticsPayload } : {})
        };
      }

      let row = null;
      for (const query of queries) {
        await searchProspect(scope, query);
        row = await findProspectRow(scope, query);
        if (row) break;
      }

      if (!row) {
        const diagnosticsPayload = await maybeCaptureDiagnostics(ctx.page, scope, diagnostics, ctx.runId, "get_prospect_detail");
        if (diagnostics && diagnosticsPayload.context) {
          errors.push(JSON.stringify({ code: "DIAGNOSTICS_CONTEXT", context: diagnosticsPayload.context }));
        }

        return {
          prospect: null,
          errors: [`Prospect not found in visible list: ${queries.join(" | ")}`],
          ...(diagnosticsPayload.screenshot ? { diagnostics: diagnosticsPayload } : {})
        };
      }

      await row.click({ timeout: 5000 });
      await ctx.page.waitForTimeout(700);

      const panelOpen = await clickByRoleOrText(scope, ["Details", "View", "Open", "Profile"]);
      if (!panelOpen.ok) {
        errors.push(JSON.stringify({ code: "DETAIL_PANEL_FALLBACK", attempts: panelOpen.attempts }));
      }

      const pageText = await scope.locator("body").innerText();
      const sizeMatch = pageText.match(/(?:headcount|size|employees?)\s*:?\s*([^\n]+)/i);
      const techStack = pageText.match(/(?:tech stack|technology|tools?)\s*:?\s*([^\n]+)/i)?.[1]?.trim();
      const contacts = (pageText.match(/linkedin|@/gi) ?? []).length;

      const prospect = {
        id: extractIdFromText(pageText) ?? id ?? null,
        company: company ?? pickText(pageText, /company\s*:?\s*([^\n]+)/i) ?? undefined,
        website: website ?? pickText(pageText, /(https?:\/\/[^\s]+)/i) ?? undefined,
        location: pickText(pageText, /location\s*:?\s*([^\n]+)/i),
        industry: pickText(pageText, /industry\s*:?\s*([^\n]+)/i),
        size: sizeMatch?.[1]?.trim(),
        notes: pickText(pageText, /notes?\s*:?\s*([^\n]+)/i),
        techStack,
        contactsFound: contacts
      };

      const diagnosticsPayload = await maybeCaptureDiagnostics(ctx.page, scope, diagnostics, ctx.runId, "get_prospect_detail");
      if (diagnostics && diagnosticsPayload.context) {
        errors.push(JSON.stringify({ code: "DIAGNOSTICS_CONTEXT", context: diagnosticsPayload.context }));
      }

      return {
        prospect,
        errors,
        ...(diagnosticsPayload.screenshot ? { diagnostics: diagnosticsPayload } : {})
      };
    } catch (error) {
      return { prospect: null, errors: [error instanceof Error ? error.message : String(error)] };
    }
  }
};
