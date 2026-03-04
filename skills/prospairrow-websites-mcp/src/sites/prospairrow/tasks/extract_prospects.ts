import { z } from "zod";
import { Capability, type TaskDefinition } from "../../../framework/types.js";
import { ensureAuthenticated, ensureProspectWorkspace, extractIdFromText, maybeCaptureDiagnostics } from "./_shared.js";
import { ProspairrowApiClient, pickCompany, pickProspectId, pickWebsite } from "./_api.js";

const inputSchema = z.object({
  limit: z.number().int().positive().max(200).default(50),
  diagnostics: z.boolean().default(false)
});

interface ProspectContact {
  name?: string;
  title?: string;
  linkedin?: string;
  email?: string;
}

interface ProspectRecord {
  id?: string | null;
  company?: string;
  website?: string;
  location?: string;
  industry?: string;
  notes?: string;
  contacts: ProspectContact[];
}

function strip(value: string): string {
  return value.replace(/\s+/g, " ").trim();
}

function pickByRegex(text: string, regex: RegExp): string | undefined {
  const match = text.match(regex);
  return match?.[1] ? strip(match[1]) : undefined;
}

function parseContacts(text: string): ProspectContact[] {
  const contacts: ProspectContact[] = [];
  const lines = text.split("\n").map((line) => line.trim()).filter(Boolean);

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i] ?? "";
    if (!/@|linkedin|contact|manager|director|vp|chief|owner/i.test(line)) continue;

    const email = line.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i)?.[0];
    const linkedin = line.match(/https?:\/\/[^\s]*linkedin\.com[^\s]*/i)?.[0];
    const title = lines[i + 1] && !/@|https?:\/\//i.test(lines[i + 1]) ? lines[i + 1] : undefined;

    contacts.push({ name: line.split("|")[0]?.trim(), title, linkedin, email });
    if (contacts.length >= 10) break;
  }

  return contacts;
}

function parseProspectText(text: string): ProspectRecord {
  const lines = text.split("\n").map((line) => line.trim()).filter(Boolean);
  const website = text.match(/https?:\/\/[^\s]+/i)?.[0];

  return {
    id: extractIdFromText(text),
    company: lines[0],
    website,
    location: pickByRegex(text, /location\s*:?\s*([^\n]+)/i) ?? lines.find((line) => /,\s*[A-Z]{2}$/.test(line)),
    industry: pickByRegex(text, /industry\s*:?\s*([^\n]+)/i),
    notes: pickByRegex(text, /notes?\s*:?\s*([^\n]+)/i),
    contacts: parseContacts(text)
  };
}

export const task: TaskDefinition = {
  taskId: "extract_prospects",
  capability: Capability.READ_ONLY,
  description: "Extract visible prospects and detail panel data from Prospairrow.",
  run: async (ctx, params) => {
    const parsed = inputSchema.safeParse(params ?? {});
    const errors: string[] = [];

    if (!parsed.success) {
      return {
        run_id: ctx.runId,
        timestamp: new Date().toISOString(),
        site: "prospairrow",
        task: "extract_prospects",
        prospects: [],
        errors: [parsed.error.message]
      };
    }

    const { limit, diagnostics } = parsed.data;
    const prospects: ProspectRecord[] = [];

    const apiKeySet = Boolean(String(ctx.apiKeys?.prospairrow || "").trim());
    if (apiKeySet) {
      const apiInit = await ProspairrowApiClient.fromApiKey(ctx.apiKeys?.prospairrow ?? "");
      if (!apiInit.client) {
        return {
          run_id: ctx.runId,
          timestamp: new Date().toISOString(),
          site: "prospairrow",
          task: "extract_prospects",
          prospects,
          errors: [apiInit.error ?? "PROSPAIRROW_API_INIT_FAILED"]
        };
      }

      const api = apiInit.client;
      try {
        const list = await api.listProspects(limit);
        if (!list.ok) {
          errors.push(`api_list_failed:${list.error ?? list.status}`);
        } else {
          for (const item of list.prospects.slice(0, limit)) {
            const rec = item as Record<string, unknown>;
            prospects.push({
              id: pickProspectId(rec),
              company: pickCompany(rec),
              website: pickWebsite(rec),
              location: String(rec.location || "").trim() || undefined,
              industry: String(rec.industry || "").trim() || undefined,
              notes: String(rec.notes || "").trim() || undefined,
              contacts: []
            });
          }
        }

        return {
          run_id: ctx.runId,
          timestamp: new Date().toISOString(),
          site: "prospairrow",
          task: "extract_prospects",
          prospects,
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
        return {
          run_id: ctx.runId,
          timestamp: new Date().toISOString(),
          site: "prospairrow",
          task: "extract_prospects",
          prospects,
          errors: [auth.error ?? "AUTH_REQUIRED"]
        };
      }
    } catch (error) {
      errors.push(`Failed to load interface: ${error instanceof Error ? error.message : String(error)}`);
      return {
        run_id: ctx.runId,
        timestamp: new Date().toISOString(),
        site: "prospairrow",
        task: "extract_prospects",
        prospects,
        errors
      };
    }

    const workspace = await ensureProspectWorkspace(ctx.page, ctx.site.baseUrl);
    const scope = workspace.scope;
    if (!workspace.ok) {
      errors.push(JSON.stringify({ code: workspace.reason ?? "PROSPECT_WORKSPACE_NOT_FOUND", attempts: workspace.attempts }));
      const diagnosticsPayload = await maybeCaptureDiagnostics(ctx.page, scope, diagnostics, ctx.runId, "extract_prospects");
      if (diagnostics && diagnosticsPayload.context) {
        errors.push(JSON.stringify({ code: "DIAGNOSTICS_CONTEXT", context: diagnosticsPayload.context }));
      }
      return {
        run_id: ctx.runId,
        timestamp: new Date().toISOString(),
        site: "prospairrow",
        task: "extract_prospects",
        prospects,
        errors,
        ...(diagnosticsPayload.screenshot ? { diagnostics: diagnosticsPayload } : {})
      };
    }

    const rowCandidates = [
      scope.getByRole("row"),
      scope.getByRole("listitem"),
      scope.locator("[data-testid*='prospect']"),
      scope.locator("[aria-label*='prospect']"),
      scope.locator("article, [role='article'], [role='gridcell']")
    ];

    let rows = rowCandidates[0];
    let selectedSource = "getByRole(row)";
    let selectedCount = 0;

    for (let i = 0; i < rowCandidates.length; i += 1) {
      const count = await rowCandidates[i].count();
      if (count > selectedCount) {
        rows = rowCandidates[i];
        selectedCount = count;
        selectedSource = ["getByRole(row)", "getByRole(listitem)", "data-testid prospect", "aria-label prospect", "article/gridcell"][i] ?? "unknown";
      }
    }

    if (selectedCount === 0) {
      errors.push("Selector path failed for rows: no row/list/card containers found.");
      const diagnosticsPayload = await maybeCaptureDiagnostics(ctx.page, scope, diagnostics, ctx.runId, "extract_prospects");
      if (diagnostics && diagnosticsPayload.context) {
        errors.push(JSON.stringify({ code: "DIAGNOSTICS_CONTEXT", context: diagnosticsPayload.context }));
      }
      return {
        run_id: ctx.runId,
        timestamp: new Date().toISOString(),
        site: "prospairrow",
        task: "extract_prospects",
        prospects,
        errors,
        ...(diagnosticsPayload.screenshot ? { diagnostics: diagnosticsPayload } : {})
      };
    }

    const total = Math.min(selectedCount, limit);

    for (let i = 0; i < total; i += 1) {
      const row = rows.nth(i);
      try {
        const rowText = strip((await row.innerText().catch(() => "")) || "");
        if (!rowText) continue;

        await row.click({ timeout: 3000 }).catch(() => undefined);
        await ctx.page.waitForTimeout(500);

        const detailText = strip((await scope.locator("body").innerText().catch(() => "")) || "");
        prospects.push(parseProspectText(detailText || rowText));
      } catch (error) {
        errors.push(`Row ${i + 1}: ${error instanceof Error ? error.message : String(error)}`);
      }
    }

    if (prospects.length === 0) {
      errors.push(`Prospect containers were found (${selectedSource}) but no parseable records were extracted.`);
    }

    const diagnosticsPayload = await maybeCaptureDiagnostics(ctx.page, scope, diagnostics, ctx.runId, "extract_prospects");
    if (diagnostics && diagnosticsPayload.context) {
      errors.push(JSON.stringify({ code: "DIAGNOSTICS_CONTEXT", context: diagnosticsPayload.context }));
    }

    return {
      run_id: ctx.runId,
      timestamp: new Date().toISOString(),
      site: "prospairrow",
      task: "extract_prospects",
      prospects,
      errors,
      ...(diagnosticsPayload.screenshot ? { diagnostics: diagnosticsPayload } : {})
    };
  }
};
