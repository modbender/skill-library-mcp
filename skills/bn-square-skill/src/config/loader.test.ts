import { afterEach, describe, expect, it } from "bun:test";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { loadConfig } from "./loader";
import { ConfigError } from "../utils/errors";

const minimalEnv: NodeJS.ProcessEnv = {
  BINANCE_COOKIE_HEADER: "csrftoken=test; session=test-session"
};

const fullEnv: NodeJS.ProcessEnv = {
  ...minimalEnv,
  BINANCE_CDP_URL: "http://127.0.0.1:9222",
  BINANCE_VALIDATE_SESSION_PATH: "/custom/validate-session",
  BINANCE_PUBLISH_POST_PATH: "/custom/publish-post",
  BINANCE_GET_POST_STATUS_PATH: "/custom/status",
  BINANCE_IMAGE_UPLOAD_PATH: "/custom/upload-image"
};

const temporaryPaths: string[] = [];

afterEach(() => {
  for (const tempPath of temporaryPaths.splice(0, temporaryPaths.length)) {
    rmSync(tempPath, { recursive: true, force: true });
  }
});

describe("loadConfig", () => {
  it("loads with only cookie header (endpoint defaults apply)", () => {
    const config = loadConfig({
      env: { ...minimalEnv },
      skipEnvFile: true
    });

    expect(config.cookieHeader).toBe("csrftoken=test; session=test-session");
    expect(config.cdpUrl).toBeUndefined();
    expect(config.endpoints.validateSessionPath).toBe("/bapi/accounts/v1/private/account/user/userInfo");
    expect(config.endpoints.publishPostPath).toBe("/bapi/composite/v1/private/pgc/content/short/create");
    expect(config.endpoints.getPostStatusPath).toBe("/bapi/composite/v1/public/pgc/content/detail");
    expect(config.endpoints.imageUploadPath).toBe("/bapi/composite/v1/private/pgc/content/image/upload");
    expect(config.image.maxBytes).toBe(5 * 1024 * 1024);
  });

  it("loads custom endpoint paths from env", () => {
    const config = loadConfig({
      env: { ...fullEnv },
      skipEnvFile: true
    });

    expect(config.cdpUrl).toBe("http://127.0.0.1:9222");
    expect(config.endpoints.publishPostPath).toBe("/custom/publish-post");
  });

  it("loads from config.json if file exists", () => {
    const tempDir = mkdtempSync(path.join(tmpdir(), "bn-square-skill-"));
    temporaryPaths.push(tempDir);

    writeFileSync(
      path.join(tempDir, "config.json"),
      JSON.stringify(
        {
          apiBaseUrl: "https://www.binance.com",
          cookieHeader: "csrftoken=abc; session=def",
          endpoints: {
            validateSessionPath: "/api/validate",
            publishPostPath: "/api/publish",
            getPostStatusPath: "/api/status",
            imageUploadPath: "/api/upload",
            statusQueryParam: "postId"
          },
          image: {
            uploadFieldName: "file",
            maxBytes: 6_000_000,
            allowedMimeTypes: ["image/png"]
          }
        },
        null,
        2
      ),
      "utf8"
    );

    const config = loadConfig({
      cwd: tempDir,
      env: {},
      skipEnvFile: true
    });

    expect(config.endpoints.validateSessionPath).toBe("/api/validate");
    expect(config.image.maxBytes).toBe(6_000_000);
    expect(config.image.allowedMimeTypes).toEqual(["image/png"]);
  });

  it("throws ConfigError when cookie header is missing", () => {
    expect(() =>
      loadConfig({
        env: {},
        skipEnvFile: true
      })
    ).toThrow(ConfigError);
  });

  it("rejects invalid cookie header format", () => {
    expect(() =>
      loadConfig({
        env: {
          ...minimalEnv,
          BINANCE_COOKIE_HEADER: "invalid-cookie-format"
        },
        skipEnvFile: true
      })
    ).toThrow(ConfigError);
  });
});
