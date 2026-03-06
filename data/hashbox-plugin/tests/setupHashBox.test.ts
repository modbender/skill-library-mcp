import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { readFile, mkdtemp, rm } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { configureHashBox, loadConfig, refreshCustomToken } from "../src/setupHashBox.js";
import type { HashBoxConfig } from "../src/setupHashBox.js";

let tempDir: string;

function mockFetchExchangeSuccess(
  customToken = "mock-custom-token",
  userId = "mock-user-id",
) {
  return vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    json: async () => ({ customToken, userId }),
  } as unknown as Response);
}

function mockFetchExchangeFailure(status = 401, error = "Invalid token") {
  return vi.fn().mockResolvedValue({
    ok: false,
    status,
    json: async () => ({ error }),
  } as unknown as Response);
}

describe("configureHashBox", () => {
  beforeEach(async () => {
    tempDir = await mkdtemp(join(tmpdir(), "hashbox-setup-"));
    vi.spyOn(process, "cwd").mockReturnValue(tempDir);
  });

  afterEach(async () => {
    vi.restoreAllMocks();
    await rm(tempDir, { recursive: true, force: true });
  });

  it("should exchange token, save config, and return success message", async () => {
    vi.stubGlobal("fetch", mockFetchExchangeSuccess("ct-123", "user-42"));

    const result = await configureHashBox("HB-test-token-123");
    expect(result).toContain("HashBox configured successfully");
    expect(result).toContain("user-42");
  });

  it("should save customToken and userId to config file", async () => {
    vi.stubGlobal("fetch", mockFetchExchangeSuccess("ct-saved", "uid-saved"));

    await configureHashBox("HB-save-test");
    const configPath = join(tempDir, "hashbox_config.json");
    const raw = await readFile(configPath, "utf-8");
    const config = JSON.parse(raw) as HashBoxConfig;
    expect(config.token).toBe("HB-save-test");
    expect(config.customToken).toBe("ct-saved");
    expect(config.userId).toBe("uid-saved");
  });

  it("should throw on invalid token without HB- prefix", async () => {
    await expect(configureHashBox("INVALID-token")).rejects.toThrow(
      "Invalid token",
    );
  });

  it("should throw on empty string", async () => {
    await expect(configureHashBox("")).rejects.toThrow("Invalid token");
  });

  it("should throw when token exchange fails", async () => {
    vi.stubGlobal("fetch", mockFetchExchangeFailure(401, "Invalid token"));

    await expect(configureHashBox("HB-bad-token")).rejects.toThrow(
      "Token exchange failed",
    );
  });

  it("should include status code in exchange error message", async () => {
    vi.stubGlobal("fetch", mockFetchExchangeFailure(403, "Forbidden"));

    await expect(configureHashBox("HB-forbidden")).rejects.toThrow("(403)");
  });

  it("should call exchangeToken endpoint with correct body", async () => {
    const fetchMock = mockFetchExchangeSuccess();
    vi.stubGlobal("fetch", fetchMock);

    await configureHashBox("HB-check-body");

    expect(fetchMock).toHaveBeenCalledOnce();
    const [url, opts] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toContain("exchangeToken");
    expect(opts.method).toBe("POST");
    const body = JSON.parse(opts.body as string);
    expect(body).toEqual({ token: "HB-check-body" });
  });
});

describe("loadConfig", () => {
  beforeEach(async () => {
    tempDir = await mkdtemp(join(tmpdir(), "hashbox-load-"));
    vi.spyOn(process, "cwd").mockReturnValue(tempDir);
  });

  afterEach(async () => {
    vi.restoreAllMocks();
    await rm(tempDir, { recursive: true, force: true });
  });

  it("should return null when config file does not exist", async () => {
    const config = await loadConfig();
    expect(config).toBeNull();
  });

  it("should return config when file exists", async () => {
    vi.stubGlobal("fetch", mockFetchExchangeSuccess("ct-load", "uid-load"));
    await configureHashBox("HB-load-test");

    const config = await loadConfig();
    expect(config).not.toBeNull();
    expect(config!.token).toBe("HB-load-test");
    expect(config!.customToken).toBe("ct-load");
    expect(config!.userId).toBe("uid-load");
  });
});

describe("refreshCustomToken", () => {
  beforeEach(async () => {
    tempDir = await mkdtemp(join(tmpdir(), "hashbox-refresh-"));
    vi.spyOn(process, "cwd").mockReturnValue(tempDir);
  });

  afterEach(async () => {
    vi.restoreAllMocks();
    await rm(tempDir, { recursive: true, force: true });
  });

  it("should re-exchange token and update config file", async () => {
    vi.stubGlobal("fetch", mockFetchExchangeSuccess("ct-refreshed", "uid-refreshed"));

    const oldConfig: HashBoxConfig = {
      token: "HB-refresh-me",
      customToken: "ct-old",
      userId: "uid-old",
    };

    const updated = await refreshCustomToken(oldConfig);
    expect(updated.customToken).toBe("ct-refreshed");
    expect(updated.userId).toBe("uid-refreshed");
    expect(updated.token).toBe("HB-refresh-me");

    // Verify file was updated
    const configPath = join(tempDir, "hashbox_config.json");
    const raw = await readFile(configPath, "utf-8");
    const saved = JSON.parse(raw) as HashBoxConfig;
    expect(saved.customToken).toBe("ct-refreshed");
  });

  it("should throw when refresh exchange fails", async () => {
    vi.stubGlobal("fetch", mockFetchExchangeFailure(500, "Server error"));

    const oldConfig: HashBoxConfig = {
      token: "HB-refresh-fail",
      customToken: "ct-old",
      userId: "uid-old",
    };

    await expect(refreshCustomToken(oldConfig)).rejects.toThrow(
      "Token exchange failed",
    );
  });
});
