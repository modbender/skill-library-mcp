import { z } from "zod";
import { Capability, type TaskDefinition } from "../../../framework/types.js";
import {
  clickByRoleOrText,
  ensureProspectWorkspace,
  ensureAuthenticated,
  extractIdFromText,
  findProspectRow,
  fillByLabelOrPlaceholder,
  maybeCaptureDiagnostics,
  searchProspect,
  websiteToDomain
} from "./_shared.js";
import { ProspairrowApiClient, pickCompany, pickProspectId, pickWebsite } from "./_api.js";

const inputSchema = z.object({
  prospects: z
    .array(
      z.object({
        company: z.string().min(1),
        website: z.string().url(),
        location: z.string().optional(),
        industry: z.string().optional(),
        notes: z.string().optional()
      })
    )
    .min(1)
    .max(50),
  dedupe: z.boolean().default(true),
  diagnostics: z.boolean().default(false)
});

function selectorError(stage: string, attempts: string[]): string {
  return JSON.stringify({ code: "SELECTOR_NOT_FOUND", stage, attempts });
}

export const task: TaskDefinition = {
  taskId: "add_prospects",
  capability: Capability.WRITE,
  description: "Create prospects in Prospairrow with optional dedupe checks.",
  run: async (ctx, params) => {
    const parsed = inputSchema.safeParse(params ?? {});
    const errors: string[] = [];

    if (!parsed.success) {
      return { created: [], errors: [parsed.error.message] };
    }

    const { prospects, dedupe, diagnostics } = parsed.data;
    const created: Array<{ id: string | null; company: string; website: string; status: "created" | "skipped" | "failed"; message?: string }> = [];

    const apiKeySet = Boolean(String(ctx.apiKeys?.prospairrow || "").trim());
    if (apiKeySet) {
      const apiInit = await ProspairrowApiClient.fromApiKey(ctx.apiKeys?.prospairrow ?? "");
      if (!apiInit.client) {
        return { created, errors: [apiInit.error ?? "PROSPAIRROW_API_INIT_FAILED"] };
      }

      const api = apiInit.client;
      try {
        for (const prospect of prospects) {
          const domain = websiteToDomain(prospect.website);

          if (dedupe) {
            const search = await api.searchProspects(prospect.company, 5);
            if (!search.ok) {
              created.push({
                id: null,
                company: prospect.company,
                website: prospect.website,
                status: "failed",
                message: `search_failed:${search.error ?? search.status}`
              });
              continue;
            }

            const existing = search.prospects.find((record) => {
              const company = pickCompany(record).toLowerCase();
              const website = pickWebsite(record).toLowerCase();
              return company === prospect.company.toLowerCase() || (!!domain && website.includes(domain));
            });

            if (existing) {
              created.push({
                id: pickProspectId(existing),
                company: prospect.company,
                website: prospect.website,
                status: "skipped",
                message: "Deduped: matching prospect already exists"
              });
              continue;
            }
          }

          const payload: Record<string, unknown> = {
            company_name: prospect.company,
            website: prospect.website,
            source: "mcp_api"
          };
          if (prospect.location) payload.location = prospect.location;
          if (prospect.industry) payload.industry = prospect.industry;
          if (prospect.notes) payload.notes = prospect.notes;

          const create = await api.createProspect(payload);
          if (!create.ok) {
            created.push({
              id: null,
              company: prospect.company,
              website: prospect.website,
              status: "failed",
              message: `create_failed:${create.error ?? create.status}`
            });
            continue;
          }

          created.push({
            id: pickProspectId(create.data),
            company: prospect.company,
            website: prospect.website,
            status: "created"
          });
        }

        return {
          created,
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
        return { created, errors: [auth.error ?? "AUTH_REQUIRED"] };
      }
    } catch (error) {
      return { created, errors: [`Failed to load site: ${error instanceof Error ? error.message : String(error)}`] };
    }

    const workspace = await ensureProspectWorkspace(ctx.page, ctx.site.baseUrl);
    const scope = workspace.scope;
    if (!workspace.ok) {
      errors.push(JSON.stringify({ code: workspace.reason ?? "PROSPECT_WORKSPACE_NOT_FOUND", attempts: workspace.attempts }));
      const diagnosticsPayload = await maybeCaptureDiagnostics(ctx.page, scope, diagnostics, ctx.runId, "add_prospects");
      if (diagnostics && diagnosticsPayload.context) {
        errors.push(JSON.stringify({ code: "DIAGNOSTICS_CONTEXT", context: diagnosticsPayload.context }));
      }
      return { created, errors, ...(diagnosticsPayload.screenshot ? { diagnostics: diagnosticsPayload } : {}) };
    }

    for (const prospect of prospects) {
      try {
        const domain = websiteToDomain(prospect.website);

        if (dedupe) {
          if (domain) {
            await searchProspect(scope, domain);
            const existingByDomain = await findProspectRow(scope, domain);
            if (existingByDomain) {
              const text = (await existingByDomain.innerText().catch(() => "")).trim();
              created.push({ id: extractIdFromText(text), company: prospect.company, website: prospect.website, status: "skipped", message: "Deduped: matching website/domain already exists" });
              continue;
            }
          }

          await searchProspect(scope, prospect.company);
          const existingByCompany = await findProspectRow(scope, prospect.company);
          if (existingByCompany) {
            const text = (await existingByCompany.innerText().catch(() => "")).trim();
            created.push({ id: extractIdFromText(text), company: prospect.company, website: prospect.website, status: "skipped", message: "Deduped: matching company already exists" });
            continue;
          }
        }

        const addClick = await clickByRoleOrText(scope, ["Add Prospect", "Add", "New Prospect", "New", "Create Prospect", "Create", "Import", "+"]);
        if (!addClick.ok) {
          errors.push(selectorError("open_add_flow", addClick.attempts));
          created.push({ id: null, company: prospect.company, website: prospect.website, status: "failed", message: addClick.error });
          continue;
        }

        const companyFill = await fillByLabelOrPlaceholder(scope, ["company", "organization", "business", "name"], prospect.company);
        if (!companyFill.ok) {
          const message = `Could not fill company field (attempts: ${companyFill.selectorTried.join(" | ")})`;
          errors.push(selectorError("fill_company", companyFill.selectorTried));
          created.push({ id: null, company: prospect.company, website: prospect.website, status: "failed", message });
          continue;
        }

        const websiteFill = await fillByLabelOrPlaceholder(scope, ["website", "domain", "url"], prospect.website);
        if (!websiteFill.ok) errors.push(selectorError("fill_website", websiteFill.selectorTried));
        if (prospect.location) {
          const locationFill = await fillByLabelOrPlaceholder(scope, ["location", "city", "region", "state", "country"], prospect.location);
          if (!locationFill.ok) errors.push(selectorError("fill_location", locationFill.selectorTried));
        }
        if (prospect.industry) {
          const industryFill = await fillByLabelOrPlaceholder(scope, ["industry", "sector", "vertical"], prospect.industry);
          if (!industryFill.ok) errors.push(selectorError("fill_industry", industryFill.selectorTried));
        }
        if (prospect.notes) {
          const notesFill = await fillByLabelOrPlaceholder(scope, ["notes", "description", "memo", "comment"], prospect.notes);
          if (!notesFill.ok) errors.push(selectorError("fill_notes", notesFill.selectorTried));
        }

        const saveClick = await clickByRoleOrText(scope, ["Save", "Create", "Add", "Submit", "Done"]);
        if (!saveClick.ok) {
          errors.push(selectorError("submit_add_form", saveClick.attempts));
          created.push({ id: null, company: prospect.company, website: prospect.website, status: "failed", message: saveClick.error });
          continue;
        }

        await ctx.page.waitForTimeout(1200);
        await searchProspect(scope, domain ?? prospect.company);

        const row = (domain ? await findProspectRow(scope, domain) : null) ?? (await findProspectRow(scope, prospect.company));
        if (!row) {
          created.push({ id: null, company: prospect.company, website: prospect.website, status: "failed", message: "Saved but prospect not found in visible list/search" });
          continue;
        }

        const rowText = (await row.innerText().catch(() => "")).trim();
        created.push({ id: extractIdFromText(rowText), company: prospect.company, website: prospect.website, status: "created" });
      } catch (error) {
        created.push({ id: null, company: prospect.company, website: prospect.website, status: "failed", message: error instanceof Error ? error.message : String(error) });
      }
    }

    const diagnosticsPayload = await maybeCaptureDiagnostics(ctx.page, scope, diagnostics, ctx.runId, "add_prospects");
    if (diagnostics && diagnosticsPayload.context) {
      errors.push(JSON.stringify({ code: "DIAGNOSTICS_CONTEXT", context: diagnosticsPayload.context }));
    }

    return { created, errors, ...(diagnosticsPayload.screenshot ? { diagnostics: diagnosticsPayload } : {}) };
  }
};
