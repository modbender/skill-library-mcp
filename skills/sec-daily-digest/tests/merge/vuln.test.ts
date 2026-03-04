import { describe, expect, test } from "bun:test";
import { mergeVulnerabilityItems } from "../../src/merge/vuln";

describe("mergeVulnerabilityItems", () => {
  test("merges by CVE id first", () => {
    const merged = mergeVulnerabilityItems([
      {
        title: "Advisory for CVE-2026-12345",
        summary: "Critical RCE in product",
        link: "https://a.test/1",
        source: "src-a",
      },
      {
        title: "Patch released",
        summary: "Fixes CVE-2026-12345",
        link: "https://b.test/2",
        source: "src-b",
      },
    ]);

    expect(merged.length).toBe(1);
    expect(merged[0]?.key).toBe("CVE-2026-12345");
    expect(merged[0]?.references.length).toBe(2);
  });

  test("clusters major non-cve incident by semantic key", () => {
    const merged = mergeVulnerabilityItems([
      {
        title: "Critical auth bypass in ACME VPN gateway",
        summary: "Researchers published PoC for auth bypass in ACME gateway",
        link: "https://a.test/3",
        source: "src-a",
      },
      {
        title: "PoC released for ACME VPN authentication bypass",
        summary: "Same product impacted, exploitation details published",
        link: "https://b.test/4",
        source: "src-b",
      },
    ]);

    expect(merged.length).toBe(1);
    expect(merged[0]?.references.length).toBe(2);
  });
});
