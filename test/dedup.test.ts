import { describe, it, expect } from "vitest";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { findDuplicates } from "../src/dedup.js";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const skillsDir = join(__dirname, "..", "skills");

describe("dedup: real skills/ directory", () => {
  it("has zero exact duplicates", async () => {
    const report = await findDuplicates(skillsDir);
    if (report.exactDuplicates.length > 0) {
      const details = report.exactDuplicates
        .map((g) => `  "${g[0].name}": ${g.map((s) => s.dirName).join(", ")}`)
        .join("\n");
      expect.fail(`Found exact duplicates:\n${details}`);
    }
  });

  it("reports near-duplicates without failing", async () => {
    const report = await findDuplicates(skillsDir);
    if (report.nearDuplicates.length > 0) {
      console.warn(
        `⚠️  ${report.nearDuplicates.length} near-duplicate pair(s) found:`,
        report.nearDuplicates.map(
          ({ pair, similarity }) => `${pair[0].dirName} ↔ ${pair[1].dirName} (${(similarity * 100).toFixed(0)}%)`,
        ),
      );
    }
    // This is a warning, not a failure
    expect(true).toBe(true);
  });
});
