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

const targetSchema = z.object({
  company: z.string().min(1),
  website: z.string().url().optional()
});

const inputSchema = z
  .object({
    prospectIds: z.array(z.string().min(1)).optional(),
    prospects: z.array(targetSchema).optional(),
    mode: z.enum(["standard", "deep"]).default("standard"),
    diagnostics: z.boolean().default(false)
  })
  .superRefine((val, ctx) => {
    if ((!val.prospectIds || val.prospectIds.length === 0) && (!val.prospects || val.prospects.length === 0)) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Provide prospectIds or prospects." });
    }
  });

function resolveStatus(pageText: string): "started" | "complete" | "failed" {
  if (/failed|error|unable/i.test(pageText)) return "failed";
  if (/complete|done|enriched|ready|success/i.test(pageText)) return "complete";
  return "started";
}

async function pollEnrichmentStatus(pageTextProvider: () => Promise<string>, timeoutMs = 90000): Promise<"started" | "complete" | "failed"> {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    const text = await pageTextProvider();
    const status = resolveStatus(text);
    if (status === "complete" || status === "failed") return status;
    await new Promise((r) => setTimeout(r, 3000));
  }
  return "started";
}

export const task: TaskDefinition = {
  taskId: "enrich_prospects",
  capability: Capability.WRITE,
  description: "Trigger enrichment for prospects by id or company/website.",
  run: async (ctx, params) => {
    const parsed = inputSchema.safeParse(params ?? {});
    const errors: string[] = [];

    if (!parsed.success) {
      return { enrichment: [], errors: [parsed.error.message] };
    }

    const { prospectIds, prospects, mode, diagnostics } = parsed.data;
    const targets: Array<{ id: string | null; company: string; website?: string }> = [
      ...(prospectIds ?? []).map((id) => ({ id, company: id, website: undefined })),
      ...((prospects ?? []).map((p) => ({ id: null, company: p.company, website: p.website })))
    ];

    const apiKeySet = Boolean(String(ctx.apiKeys?.prospairrow || "").trim());
    if (apiKeySet) {
      const apiInit = await ProspairrowApiClient.fromApiKey(ctx.apiKeys?.prospairrow ?? "");
      if (!apiInit.client) {
        return { enrichment: [], errors: [apiInit.error ?? "PROSPAIRROW_API_INIT_FAILED"] };
      }

      const api = apiInit.client;
      const enrichment: Array<{ id: string | null; company: string; status: "started" | "complete" | "failed"; message?: string }> = [];
      try {
        for (const target of targets) {
          let targetId = target.id;

          if (!targetId) {
            const search = await api.searchProspects(target.company, 5);
            if (!search.ok) {
              enrichment.push({ id: null, company: target.company, status: "failed", message: `search_failed:${search.error ?? search.status}` });
              continue;
            }

            const domain = websiteToDomain(target.website);
            const match = search.prospects.find((record) => {
              const company = pickCompany(record).toLowerCase();
              const website = pickWebsite(record).toLowerCase();
              return company === target.company.toLowerCase() || (!!domain && website.includes(domain));
            }) ?? search.prospects[0];

            targetId = match ? pickProspectId(match) : null;
          }

          if (!targetId) {
            enrichment.push({ id: null, company: target.company, status: "failed", message: "Target not found via API search" });
            continue;
          }

          const enrich = await api.enrichProspect(targetId);
          if (!enrich.ok) {
            enrichment.push({ id: targetId, company: target.company, status: "failed", message: `enrich_failed:${enrich.error ?? enrich.status}` });
            continue;
          }

          const statusText = JSON.stringify(enrich.data).toLowerCase();
          const status = resolveStatus(statusText);
          enrichment.push({
            id: targetId,
            company: target.company,
            status: status === "complete" ? "complete" : "started",
            message: status === "complete" ? undefined : "Enrichment started; re-run detail extraction if async."
          });
        }

        return {
          enrichment,
          errors,
          diagnostics: {
            mode: "api",
            apiBase: api.apiBase,
            usedApiKey: true,
            diagnosticsEnabled: diagnostics,
            requestedMode: mode
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
        return { enrichment: [], errors: [auth.error ?? "AUTH_REQUIRED"] };
      }
    } catch (error) {
      return {
        enrichment: [],
        errors: [`Failed to load site: ${error instanceof Error ? error.message : String(error)}`]
      };
    }

    const workspace = await ensureProspectWorkspace(ctx.page, ctx.site.baseUrl);
    const scope = workspace.scope;
    const enrichment: Array<{ id: string | null; company: string; status: "started" | "complete" | "failed"; message?: string }> = [];

    if (!workspace.ok) {
      errors.push(JSON.stringify({ code: workspace.reason ?? "PROSPECT_WORKSPACE_NOT_FOUND", attempts: workspace.attempts }));
      const diagnosticsPayload = await maybeCaptureDiagnostics(ctx.page, scope, diagnostics, ctx.runId, "enrich_prospects");
      if (diagnostics && diagnosticsPayload.context) {
        errors.push(JSON.stringify({ code: "DIAGNOSTICS_CONTEXT", context: diagnosticsPayload.context }));
      }
      return { enrichment, errors, ...(diagnosticsPayload.screenshot ? { diagnostics: diagnosticsPayload } : {}) };
    }

    for (const target of targets) {
      const domain = websiteToDomain(target.website);
      const lookups = [target.id, domain, target.website, target.company].filter((item): item is string => Boolean(item && item.trim()));

      try {
        let row = null;
        let matchedBy: string | null = null;

        for (const lookup of lookups) {
          await searchProspect(scope, lookup);
          row = await findProspectRow(scope, lookup);
          if (row) {
            matchedBy = lookup;
            break;
          }
        }

        if (!row) {
          enrichment.push({ id: target.id, company: target.company, status: "failed", message: `Target not found in visible list: ${lookups.join(" | ")}` });
          continue;
        }

        const rowText = (await row.innerText().catch(() => "")).trim();
        const rowId = extractIdFromText(rowText) ?? target.id;

        await row.click({ timeout: 5000 });
        await ctx.page.waitForTimeout(700);

        if (mode === "deep") {
          const deepModeClick = await clickByRoleOrText(scope, ["Deep", "Deep Enrichment", "Advanced"]);
          if (!deepModeClick.ok) errors.push(JSON.stringify({ code: "DEEP_MODE_NOT_FOUND", company: target.company, attempts: deepModeClick.attempts }));
        }

        const enrichClick = await clickByRoleOrText(scope, ["Run Enrichment", "Enrich", "Refresh Data", "Refresh", "Update", "Find Contacts"]);
        if (!enrichClick.ok) {
          enrichment.push({ id: rowId, company: target.company, status: "failed", message: `Selector path failed (${matchedBy ?? "unknown match"}): ${enrichClick.error}` });
          errors.push(JSON.stringify({ code: "ENRICH_ACTION_NOT_FOUND", company: target.company, attempts: enrichClick.attempts }));
          continue;
        }

        const status = await pollEnrichmentStatus(async () => scope.locator("body").innerText());
        enrichment.push({ id: rowId, company: target.company, status, message: status === "started" ? "Enrichment started; status appears async/pending." : undefined });
      } catch (error) {
        enrichment.push({ id: target.id, company: target.company, status: "failed", message: error instanceof Error ? error.message : String(error) });
      }
    }

    const diagnosticsPayload = await maybeCaptureDiagnostics(ctx.page, scope, diagnostics, ctx.runId, "enrich_prospects");
    if (diagnostics && diagnosticsPayload.context) {
      errors.push(JSON.stringify({ code: "DIAGNOSTICS_CONTEXT", context: diagnosticsPayload.context }));
    }

    return { enrichment, errors, ...(diagnosticsPayload.screenshot ? { diagnostics: diagnosticsPayload } : {}) };
  }
};
