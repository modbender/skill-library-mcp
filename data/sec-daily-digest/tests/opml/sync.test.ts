import { afterEach, beforeEach, describe, expect, test } from "bun:test";
import { mkdir, mkdtemp, readFile, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { syncOpml } from "../../src/opml/sync";

describe("syncOpml", () => {
  let home = "";

  beforeEach(async () => {
    home = await mkdtemp(path.join(os.tmpdir(), "sec-opml-"));
  });

  afterEach(async () => {
    await rm(home, { recursive: true, force: true });
  });

  test("falls back to cached OPML when remote fails", async () => {
    const cachePath = path.join(home, "opml", "tiny.opml");
    await mkdir(path.dirname(cachePath), { recursive: true });
    await Bun.write(cachePath, "<opml><body/></opml>");

    const result = await syncOpml({
      profile: "tiny",
      env: { SEC_DAILY_DIGEST_HOME: home } as NodeJS.ProcessEnv,
      fetcher: async () => {
        throw new Error("network down");
      },
    });

    expect(result.usedCache).toBe(true);
    expect(result.opmlPath).toBe(cachePath);
  });

  test("throws when no cache and remote check fails", async () => {
    const run = syncOpml({
      profile: "tiny",
      env: { SEC_DAILY_DIGEST_HOME: home } as NodeJS.ProcessEnv,
      fetcher: async () => {
        throw new Error("network down");
      },
    });

    await expect(run).rejects.toThrow("No cached OPML available");
  });

  test("writes cache when remote fetch succeeds", async () => {
    const remoteXml = "<opml><body><outline text=\"test\"/></body></opml>";
    const result = await syncOpml({
      profile: "full",
      env: { SEC_DAILY_DIGEST_HOME: home } as NodeJS.ProcessEnv,
      fetcher: async () => new Response(remoteXml, { status: 200 }),
    });

    expect(result.usedCache).toBe(false);
    expect(result.updated).toBe(true);

    const saved = await readFile(result.opmlPath, "utf8");
    expect(saved).toBe(remoteXml);
  });
});
