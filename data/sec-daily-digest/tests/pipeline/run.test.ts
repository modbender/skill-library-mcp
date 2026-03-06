import { describe, expect, test } from "bun:test";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { runPipeline } from "../../src/pipeline/run";

describe("runPipeline", () => {
  test("returns output path and summary counters", async () => {
    const tempRoot = await mkdtemp(path.join(os.tmpdir(), "sec-pipeline-"));
    const outputPath = path.join(tempRoot, "digest.md");

    const result = await runPipeline({
      dryRun: true,
      outputPath,
      env: {
        SEC_DAILY_DIGEST_HOME: tempRoot,
      } as NodeJS.ProcessEnv,
      seedArticles: [
        {
          title: "Critical CVE in AI gateway",
          link: "https://example.com/a",
          pubDate: new Date("2026-02-27T10:00:00Z"),
          description: "CVE-2026-11111 affects model serving layer",
          sourceName: "source-a",
          sourceUrl: "https://example.com",
        },
        {
          title: "New agent evaluation benchmark",
          link: "https://example.com/b",
          pubDate: new Date("2026-02-27T09:00:00Z"),
          description: "LLM agent evaluation and reproducibility notes",
          sourceName: "source-b",
          sourceUrl: "https://example.com",
        },
      ],
    });

    expect(result.outputPath).toBe(outputPath);
    expect(result.counters.articles).toBe(2);
    expect(result.counters.selected).toBeGreaterThan(0);

    const report = await readFile(outputPath, "utf8");
    expect(report).toContain("## AI发展");
    expect(report).toContain("## 安全动态");
    expect(report).toContain("## 📝 今日趋势");
    expect(report).toContain("## 漏洞专报");

    await rm(tempRoot, { recursive: true, force: true });
  });
});
