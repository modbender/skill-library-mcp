import fs from "node:fs/promises";
import path from "node:path";
import type { Frame, Locator, Page } from "playwright";

type Scope = Page | Frame;

export type SelectorAttempt = {
  strategy: string;
  detail: string;
};

export type DebugContext = {
  pageUrl: string;
  scopeUrl: string;
  frameUrls: string[];
  headings: string[];
  buttons: string[];
  searchboxes: number;
  prospectRows: number;
};

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export function websiteToDomain(website?: string): string | undefined {
  if (!website) return undefined;
  try {
    const host = new URL(website).hostname.toLowerCase();
    return host.replace(/^www\./, "");
  } catch {
    return undefined;
  }
}

export async function ensureAuthenticated(page: Page): Promise<{ ok: boolean; error?: string }> {
  const url = page.url();
  if (/login|signin|auth/i.test(url)) {
    return { ok: false, error: "AUTH_REQUIRED: redirected to login page" };
  }

  const loginHints = [
    page.getByRole("heading", { name: /sign in|login|welcome back/i }),
    page.getByLabel(/password/i),
    page.getByPlaceholder(/password/i)
  ];

  for (const hint of loginHints) {
    if (await hint.count()) {
      return { ok: false, error: "AUTH_REQUIRED: login UI detected" };
    }
  }

  return { ok: true };
}

async function extractor(locator: Locator, limit = 10): Promise<string[]> {
  const total = Math.min(await locator.count(), limit);
  const items: string[] = [];

  for (let i = 0; i < total; i += 1) {
    const text = (await locator.nth(i).innerText().catch(() => "")).trim();
    if (text) items.push(text.replace(/\s+/g, " ").slice(0, 120));
  }

  return items;
}

async function scoreScope(scope: Scope): Promise<number> {
  return (
    (await scope.getByRole("button", { name: /add|new|create|import|enrich/i }).count()) +
    (await scope.getByRole("searchbox").count()) +
    (await scope.getByRole("row").count()) +
    (await scope.getByRole("listitem").count()) +
    (await scope.locator("[data-testid*='prospect']").count())
  );
}

export async function detectMainAppFrame(page: Page): Promise<Scope> {
  const main = page.mainFrame();
  const frames = [main, ...page.frames().filter((frame) => frame !== main)];

  let best: Scope = main;
  let bestScore = -1;

  for (const frame of frames) {
    try {
      const url = frame.url();
      if (url && /^https?:/i.test(url)) {
        const hostname = new URL(url).hostname;
        if (hostname !== "app.prospairrow.com") continue;
      }

      const score = await scoreScope(frame);
      if (score > bestScore) {
        bestScore = score;
        best = frame;
      }
    } catch {
      // Keep scoring other frames.
    }
  }

  return best;
}

async function clickAnyNavLabel(scope: Scope, labels: string[]): Promise<boolean> {
  for (const label of labels) {
    const regex = new RegExp(escapeRegExp(label), "i");
    const candidates = [
      scope.getByRole("link", { name: regex }),
      scope.getByRole("tab", { name: regex }),
      scope.getByRole("button", { name: regex }),
      scope.getByText(regex)
    ];

    for (const candidate of candidates) {
      if (await candidate.count()) {
        const target = candidate.first();
        if (await target.isVisible().catch(() => true)) {
          await target.click({ timeout: 4000 }).catch(() => undefined);
          return true;
        }
      }
    }
  }

  return false;
}

export async function ensureProspectWorkspace(page: Page, baseUrl: string): Promise<{ ok: boolean; scope: Scope; attempts: string[]; reason?: string }> {
  const attempts: string[] = [];

  let scope = await detectMainAppFrame(page);
  let score = await scoreScope(scope);
  if (score > 0) {
    return { ok: true, scope, attempts };
  }

  attempts.push(`initial_scope_score:${score}`);

  const navLabels = ["Interface", "Prospects", "Saved Prospects", "Leads", "Companies"];
  const clicked = await clickAnyNavLabel(page, navLabels);
  attempts.push(`nav_click:${clicked ? "attempted" : "not_found"}`);

  if (clicked) {
    await page.waitForLoadState("networkidle", { timeout: 10000 }).catch(() => undefined);
    scope = await detectMainAppFrame(page);
    score = await scoreScope(scope);
    attempts.push(`post_nav_scope_score:${score}`);
    if (score > 0) {
      return { ok: true, scope, attempts };
    }
  }

  const base = new URL(baseUrl);
  if (page.url() !== base.href) {
    attempts.push(`goto:${base.href}`);
    await page.goto(base.href, { waitUntil: "domcontentloaded", timeout: 15000 }).catch(() => undefined);
    await page.waitForLoadState("networkidle", { timeout: 10000 }).catch(() => undefined);
    scope = await detectMainAppFrame(page);
    score = await scoreScope(scope);
    attempts.push(`post_goto_scope_score:${score}`);
    if (score > 0) {
      return { ok: true, scope, attempts };
    }
  }

  return {
    ok: false,
    scope,
    attempts,
    reason: "PROSPECT_WORKSPACE_NOT_FOUND"
  };
}

export async function collectDebugContext(page: Page, scope: Scope): Promise<DebugContext> {
  const headings = await extractor(scope.getByRole("heading"), 8);
  const buttons = await extractor(scope.getByRole("button"), 16);
  const searchboxes = await scope.getByRole("searchbox").count();
  const prospectRows =
    (await scope.locator("[data-testid*='prospect']").count()) +
    (await scope.getByRole("row").count()) +
    (await scope.getByRole("listitem").count());

  return {
    pageUrl: page.url(),
    scopeUrl: scope.url(),
    frameUrls: page.frames().map((f) => f.url()).filter(Boolean),
    headings,
    buttons,
    searchboxes,
    prospectRows
  };
}

export async function findFirstVisible(candidates: Locator[]): Promise<{ ok: boolean; locator?: Locator; attempts: string[] }> {
  const attempts: string[] = [];

  for (const candidate of candidates) {
    const descriptor = candidate.toString();
    try {
      const count = await candidate.count();
      if (!count) {
        attempts.push(`not found: ${descriptor}`);
        continue;
      }

      for (let i = 0; i < Math.min(count, 3); i += 1) {
        const loc = candidate.nth(i);
        if (await loc.isVisible().catch(() => false)) {
          return { ok: true, locator: loc, attempts };
        }
      }

      return { ok: true, locator: candidate.first(), attempts };
    } catch (error) {
      attempts.push(`failed: ${descriptor} (${error instanceof Error ? error.message : String(error)})`);
    }
  }

  return { ok: false, attempts };
}

export async function clickByRoleOrText(scope: Scope, labels: string[]): Promise<{ ok: boolean; used?: SelectorAttempt; attempts: string[]; error?: string }> {
  const attempts: string[] = [];

  for (const label of labels) {
    const regex = new RegExp(escapeRegExp(label), "i");
    const candidates = [
      scope.getByRole("button", { name: regex }),
      scope.getByRole("menuitem", { name: regex }),
      scope.getByRole("link", { name: regex }),
      scope.locator("[aria-label]", { hasText: regex }),
      scope.getByText(regex)
    ];

    const found = await findFirstVisible(candidates);
    attempts.push(...found.attempts);
    if (!found.ok || !found.locator) {
      attempts.push(`not found: role-or-text:${label}`);
      continue;
    }

    try {
      await found.locator.click({ timeout: 5000 });
      return {
        ok: true,
        used: { strategy: "role-or-text", detail: label },
        attempts
      };
    } catch (error) {
      attempts.push(`failed click: role-or-text:${label} (${error instanceof Error ? error.message : String(error)})`);
    }
  }

  return {
    ok: false,
    attempts,
    error: `Selector path failed: ${attempts.join(" | ")}`
  };
}

export async function fillByLabelOrPlaceholder(scope: Scope, fieldNames: string[], value: string): Promise<{ ok: boolean; selectorTried: string[] }> {
  const selectorTried: string[] = [];

  for (const fieldName of fieldNames) {
    const regex = new RegExp(fieldName, "i");
    const candidates = [
      scope.getByLabel(regex),
      scope.getByPlaceholder(regex),
      scope.getByRole("textbox", { name: regex }),
      scope.locator(`input[name*='${fieldName.toLowerCase()}']`),
      scope.locator(`textarea[name*='${fieldName.toLowerCase()}']`)
    ];

    for (const candidate of candidates) {
      const descriptor = `${fieldName}:${candidate.toString()}`;
      selectorTried.push(descriptor);

      try {
        const count = await candidate.count();
        if (!count) continue;

        const loc = candidate.first();
        await loc.click({ timeout: 1500 }).catch(() => undefined);
        await loc.fill(value, { timeout: 5000 });
        return { ok: true, selectorTried };
      } catch {
        // Continue to next selector.
      }
    }
  }

  return { ok: false, selectorTried };
}

export async function maybeCaptureDiagnostics(page: Page, scope: Scope, enabled: boolean, runId: string, taskId: string): Promise<{ screenshot?: string; context?: DebugContext }> {
  if (!enabled) return {};

  const artifactDir = path.join(process.cwd(), "artifacts");
  await fs.mkdir(artifactDir, { recursive: true });
  const filePath = path.join(artifactDir, `${taskId}-${runId}.png`);
  await page.screenshot({ path: filePath, fullPage: true });
  const context = await collectDebugContext(page, scope).catch(() => undefined);

  return {
    screenshot: filePath,
    context
  };
}

export async function searchProspect(scope: Scope, query: string): Promise<void> {
  const q = query.trim();
  if (!q) return;

  const searchCandidates = [
    scope.getByRole("searchbox"),
    scope.getByPlaceholder(/search/i),
    scope.getByRole("textbox", { name: /search/i }),
    scope.locator("input[type='search']")
  ];

  const found = await findFirstVisible(searchCandidates);
  if (!found.ok || !found.locator) return;

  await found.locator.click({ timeout: 2500 }).catch(() => undefined);
  await found.locator.fill("").catch(() => undefined);
  await found.locator.fill(q);
  await new Promise((resolve) => setTimeout(resolve, 800));
}

export async function findProspectRow(scope: Scope, query: string): Promise<Locator | null> {
  const escaped = escapeRegExp(query);
  const regex = new RegExp(escaped, "i");

  const rowCandidates = [
    scope.getByRole("row", { name: regex }),
    scope.getByRole("listitem", { name: regex }),
    scope.locator("[data-testid*='prospect']", { hasText: regex }),
    scope.locator("[aria-label*='prospect']", { hasText: regex }),
    scope.locator("article, [role='article'], [role='gridcell']", { hasText: regex }),
    scope.getByText(regex)
  ];

  const found = await findFirstVisible(rowCandidates);
  return found.ok && found.locator ? found.locator : null;
}

export function extractIdFromText(text: string): string | null {
  const match = text.match(/\b(?:id[:\s#-]*)?([a-zA-Z0-9_-]{4,})\b/i);
  return match?.[1] ?? null;
}
