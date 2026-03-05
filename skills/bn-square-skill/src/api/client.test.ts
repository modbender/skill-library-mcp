import { describe, expect, it } from "bun:test";
import { z } from "zod";
import { BinanceHttpClient } from "./client";
import type { BinanceConfig } from "../config/schema";
import { RateLimitError, SessionExpiredError, ValidationError } from "../utils/errors";

const baseConfig: BinanceConfig = {
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

describe("BinanceHttpClient", () => {
  it("sends required headers and query params", async () => {
    let capturedUrl = "";
    let capturedHeaders = new Headers();

    const client = new BinanceHttpClient(baseConfig, async (input, init) => {
      capturedUrl = String(input);
      capturedHeaders = new Headers(init?.headers);
      return new Response(JSON.stringify({ ok: true }), {
        headers: {
          "content-type": "application/json"
        }
      });
    });

    const response = await client.getJson("/validate", {
      query: { id: "123", active: true },
      responseSchema: z.object({ ok: z.boolean() })
    });

    expect(response.ok).toBe(true);
    expect(capturedUrl).toBe("https://www.binance.com/validate?id=123&active=true");
    expect(capturedHeaders.get("Cookie")).toBe("csrftoken=test; session=secure");
    expect(capturedHeaders.get("X-CSRF-Token")).toBe("csrf");
    expect(capturedHeaders.get("User-Agent")).toBe("ua");
  });

  it("maps 401 to SessionExpiredError and sanitizes response", async () => {
    const client = new BinanceHttpClient(baseConfig, async () => {
      return new Response("session=very-sensitive", { status: 401 });
    });

    await expect(client.getJson("/validate")).rejects.toThrow(SessionExpiredError);
    await expect(client.getJson("/validate")).rejects.toThrow("session=<redacted>");
  });

  it("maps 429 to RateLimitError", async () => {
    const client = new BinanceHttpClient(baseConfig, async () => {
      return new Response("too many requests", { status: 429 });
    });

    await expect(client.getJson("/validate")).rejects.toThrow(RateLimitError);
  });

  it("throws ValidationError for invalid response payload", async () => {
    const client = new BinanceHttpClient(baseConfig, async () => {
      return new Response(JSON.stringify({ ok: "true" }), {
        headers: { "content-type": "application/json" }
      });
    });

    await expect(
      client.getJson("/validate", {
        responseSchema: z.object({ ok: z.boolean() })
      })
    ).rejects.toThrow(ValidationError);
  });
});
