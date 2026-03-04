import { chromium, type Browser, type BrowserContext, type Page } from "playwright";
import { enforceRequestAllowlist, validateUrlAgainstAllowlist } from "./policy.js";

export interface RunnerOptions {
  allowedHosts: string[];
  storageStatePath?: string;
  headed: boolean;
}

export interface RunnerSession {
  browser: Browser;
  context: BrowserContext;
  page: Page;
  safeGoto: (url: string) => Promise<void>;
  close: () => Promise<void>;
}

export async function createRunnerSession(options: RunnerOptions): Promise<RunnerSession> {
  const browser = await chromium.launch({ headless: !options.headed });
  const context = await browser.newContext(options.storageStatePath ? { storageState: options.storageStatePath } : {});
  const page = await context.newPage();

  let navigationViolation: string | null = null;

  await page.route("**/*", async (route) => {
    await enforceRequestAllowlist(route, route.request(), options.allowedHosts);
  });

  page.on("framenavigated", (frame) => {
    const verdict = validateUrlAgainstAllowlist(frame.url(), options.allowedHosts);
    if (!verdict.ok) {
      navigationViolation = verdict.reason ?? "Navigation blocked by policy";
      void page.goto("about:blank").catch(() => undefined);
    }
  });

  async function safeGoto(url: string): Promise<void> {
    const verdict = validateUrlAgainstAllowlist(url, options.allowedHosts);
    if (!verdict.ok) {
      throw new Error(verdict.reason ?? "Blocked URL");
    }

    await page.goto(url, { waitUntil: "domcontentloaded" });
    await page.waitForLoadState("networkidle");

    if (navigationViolation) {
      throw new Error(navigationViolation);
    }
  }

  return {
    browser,
    context,
    page,
    safeGoto,
    close: async () => {
      await context.close();
      await browser.close();
    }
  };
}
