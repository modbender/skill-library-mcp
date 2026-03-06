import { afterEach, beforeEach, describe, expect, test } from "bun:test";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { loadConfig } from "../../src/config/load";

describe("loadConfig", () => {
  let tempRoot = "";

  beforeEach(async () => {
    tempRoot = await mkdtemp(path.join(os.tmpdir(), "sec-dd-"));
  });

  afterEach(async () => {
    await rm(tempRoot, { recursive: true, force: true });
  });

  test("uses defaults when config file is missing", async () => {
    const cfg = await loadConfig({}, { SEC_DAILY_DIGEST_HOME: tempRoot } as NodeJS.ProcessEnv);
    expect(cfg.provider).toBe("openai");
    expect(cfg.opml_profile).toBe("tiny");
    expect(cfg.time_range_hours).toBe(48);
  });

  test("CLI provider overrides YAML provider", async () => {
    await writeFile(
      path.join(tempRoot, "config.yaml"),
      "provider: gemini\nopml_profile: full\ntime_range_hours: 24\ntop_n: 10\n",
      "utf8",
    );

    const cfg = await loadConfig(
      { provider: "claude" },
      { SEC_DAILY_DIGEST_HOME: tempRoot } as NodeJS.ProcessEnv,
    );
    expect(cfg.provider).toBe("claude");
    expect(cfg.opml_profile).toBe("full");
  });

  test("persists merged config to config.yaml", async () => {
    const cfg = await loadConfig({ top_n: 42 }, { SEC_DAILY_DIGEST_HOME: tempRoot } as NodeJS.ProcessEnv);
    expect(cfg.top_n).toBe(42);

    const cfgAgain = await loadConfig({}, { SEC_DAILY_DIGEST_HOME: tempRoot } as NodeJS.ProcessEnv);
    expect(cfgAgain.top_n).toBe(42);
  });
});
