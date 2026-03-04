import { describe, expect, test } from "bun:test";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { runPipeline } from "../../src/pipeline/run";

describe("sec-digest e2e", () => {
  test("generates digest with merged vulnerability references", async () => {
    const workspace = await mkdtemp(path.join(os.tmpdir(), "sec-e2e-"));
    const outputPath = path.join(workspace, "digest.md");
    const opmlFixture = await readFile(path.join(process.cwd(), "tests/fixtures/tiny.opml"), "utf8");
    const feedFixture = await readFile(path.join(process.cwd(), "tests/fixtures/sample-rss.xml"), "utf8");

    const fetcher: typeof fetch = async (input) => {
      const url = String(input);
      if (url.includes("CyberSecurityRSS/master/tiny.opml")) {
        return new Response(opmlFixture, { status: 200 });
      }
      if (url === "https://fixture.local/feed.xml") {
        return new Response(feedFixture, { status: 200 });
      }
      return new Response("not found", { status: 404 });
    };

    const result = await runPipeline({
      dryRun: true,
      outputPath,
      env: {
        SEC_DAILY_DIGEST_HOME: workspace,
      } as NodeJS.ProcessEnv,
      fetcher,
      now: new Date("2026-02-27T12:00:00.000Z"),
    });

    const markdown = await readFile(outputPath, "utf8");
    expect(result.counters.articles).toBe(2);
    expect(result.counters.selected).toBeGreaterThan(0);
    expect(markdown).toContain("今日趋势");
    expect(markdown).toContain("漏洞专报");
    expect(markdown).toContain("CVE-2026-77777");
    expect(markdown).toContain("fixture.local/post-1");

    await rm(workspace, { recursive: true, force: true });
  });
});
