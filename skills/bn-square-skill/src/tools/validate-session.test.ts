import { describe, expect, it } from "bun:test";
import type { BinanceConfig } from "../config/schema";
import { SessionExpiredError } from "../utils/errors";
import { validateSession } from "./validate-session";

const config: BinanceConfig = {
  apiBaseUrl: "https://www.binance.com",
  cookieHeader: "csrftoken=test; session=secure",
  csrfToken: "csrf",
  sessionToken: "session-token",
  userAgent: "ua",
  referer: "https://www.binance.com/en/square",
  requestTimeoutMs: 5000,
  postUrlTemplate: "https://www.binance.com/en/square/post/{postId}",
  endpoints: {
    validateSessionPath: "/validate",
    publishPostPath: "/publish",
    getPostStatusPath: "/status",
    imageUploadPath: "/upload",
    statusQueryParam: "postId"
  },
  image: {
    uploadFieldName: "file",
    maxBytes: 5_242_880,
    allowedMimeTypes: ["image/png"]
  }
};

describe("validateSession", () => {
  it("returns valid=true for successful response", async () => {
    const result = await validateSession({
      config,
      client: {
        getJson: async () => ({
          code: 0,
          data: {
            userId: "123",
            username: "trader"
          }
        })
      }
    });

    expect(result).toEqual({
      valid: true,
      userId: "123",
      username: "trader"
    });
  });

  it("returns valid=false when envelope indicates failure", async () => {
    const result = await validateSession({
      config,
      client: {
        getJson: async () => ({
          code: "401",
          message: "invalid session"
        })
      }
    });

    expect(result.valid).toBe(false);
    expect(result.error).toBe("invalid session");
  });

  it("returns expired message on SessionExpiredError", async () => {
    const result = await validateSession({
      config,
      client: {
        getJson: async () => {
          throw new SessionExpiredError("unauthorized");
        }
      }
    });

    expect(result).toEqual({
      valid: false,
      error: "Session expired or unauthorized"
    });
  });
});
