import { describe, expect, it } from "bun:test";
import type { BinanceConfig } from "../config/schema";
import { SessionExpiredError } from "../utils/errors";
import { publishPost } from "./publish-post";

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

describe("publishPost", () => {
  it("publishes text post successfully", async () => {
    const result = await publishPost(
      { content: "Hello Binance" },
      {
        config,
        client: {
          postFormData: async () => ({}),
          postJson: async (_path, _payload) => ({
            code: 0,
            data: {
              postId: "abc123"
            }
          })
        }
      }
    );

    expect(result).toEqual({
      success: true,
      postId: "abc123",
      postUrl: "https://www.binance.com/en/square/post/abc123"
    });
  });

  it("uploads images before publish", async () => {
    let capturedPayload: unknown;

    const result = await publishPost(
      { content: "Chart update", imageUrls: ["https://example.com/image.png"] },
      {
        config,
        uploadImage: async () => "https://img.binance.com/img-1.png",
        client: {
          postFormData: async () => ({}),
          postJson: async (_path, payload) => {
            capturedPayload = payload;
            return {
              code: 0,
              data: {
                post: {
                  id: "p-001",
                  postUrl: "https://www.binance.com/en/square/post/p-001"
                }
              }
            };
          }
        }
      }
    );

    expect(capturedPayload).toEqual({
      content: "Chart update",
      images: ["https://img.binance.com/img-1.png"]
    });
    expect(result.success).toBe(true);
    expect(result.postId).toBe("p-001");
  });

  it("rejects poll with images", async () => {
    const result = await publishPost(
      {
        content: "Vote",
        imageUrls: ["https://example.com/image.png"],
        poll: {
          question: "Bull or bear",
          options: ["Bull", "Bear"],
          durationHours: 24
        }
      },
      {
        config,
        client: {
          postFormData: async () => ({}),
          postJson: async () => ({})
        }
      }
    );

    expect(result.success).toBe(false);
    expect(result.error).toContain("poll posts cannot include images");
  });

  it("returns session error on unauthorized call", async () => {
    const result = await publishPost(
      { content: "Hello Binance" },
      {
        config,
        client: {
          postFormData: async () => ({}),
          postJson: async () => {
            throw new SessionExpiredError();
          }
        }
      }
    );

    expect(result).toEqual({
      success: false,
      error: "Session expired or unauthorized"
    });
  });
});
