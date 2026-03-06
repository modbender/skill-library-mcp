import { describe, expect, test } from "bun:test";
import { getStateRoot } from "../../src/config/paths";

describe("getStateRoot", () => {
  test("uses ~/.sec-daily-digest by default", () => {
    const root = getStateRoot({});
    expect(root.endsWith("/.sec-daily-digest")).toBe(true);
  });

  test("supports SEC_DAILY_DIGEST_HOME override", () => {
    const root = getStateRoot({
      SEC_DAILY_DIGEST_HOME: "/tmp/sec-home",
    } as NodeJS.ProcessEnv);
    expect(root).toBe("/tmp/sec-home");
  });
});
