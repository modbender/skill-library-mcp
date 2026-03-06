import { describe, expect, it } from "bun:test";
import type { BinanceConfig } from "./config/schema";
import { validateSession } from "./tools/validate-session";
import { publishPost } from "./tools/publish-post";
import { getPostStatus } from "./tools/get-post-status";

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
    validateSessionPath: "/validate-session",
    publishPostPath: "/publish-post",
    getPostStatusPath: "/post-status",
    imageUploadPath: "/upload-image",
    statusQueryParam: "postId"
  },
  image: {
    uploadFieldName: "file",
    maxBytes: 5_242_880,
    allowedMimeTypes: ["image/png"]
  }
};

describe("bn-square-skill integration", () => {
  it("supports validate -> publish -> status flow via DI", async () => {
    // Step 1: validate session
    const session = await validateSession({
      config,
      client: {
        getJson: async () => ({
          code: 0,
          data: { userId: "u-1", username: "trader" }
        })
      }
    });

    expect(session.valid).toBe(true);
    expect(session.userId).toBe("u-1");

    // Step 2: publish post
    const publishResult = await publishPost(
      { content: "Hello from integration test" },
      {
        config,
        client: {
          postJson: async () => ({
            code: 0,
            data: { postId: "p-1" }
          }),
          postFormData: async () => ({})
        }
      }
    );

    expect(publishResult.success).toBe(true);
    expect(publishResult.postId).toBe("p-1");

    // Step 3: get post status
    const status = await getPostStatus(
      { postId: "p-1" },
      {
        config,
        client: {
          getJson: async () => ({
            code: 0,
            data: { status: "published" }
          })
        }
      }
    );

    expect(status).toEqual({
      status: "published",
      postUrl: "https://www.binance.com/en/square/post/p-1"
    });
  });
});
