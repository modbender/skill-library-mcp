import { describe, expect, it } from "bun:test";
import type { BinanceConfig } from "../config/schema";
import { getPostStatus } from "./get-post-status";

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

describe("getPostStatus", () => {
  it("maps published status", async () => {
    const result = await getPostStatus(
      { postId: "post-1" },
      {
        config,
        client: {
          getJson: async () => ({
            code: 0,
            data: {
              status: "published"
            }
          })
        }
      }
    );

    expect(result).toEqual({
      status: "published",
      postUrl: "https://www.binance.com/en/square/post/post-1"
    });
  });

  it("maps pending_review status", async () => {
    const result = await getPostStatus(
      { postId: "post-2" },
      {
        config,
        client: {
          getJson: async () => ({
            code: 0,
            data: {
              reviewStatus: "pending_review"
            }
          })
        }
      }
    );

    expect(result.status).toBe("pending_review");
  });

  it("maps deleted status from numeric value", async () => {
    const result = await getPostStatus(
      { postId: "post-3" },
      {
        config,
        client: {
          getJson: async () => ({
            code: 0,
            data: {
              postStatus: 3
            }
          })
        }
      }
    );

    expect(result.status).toBe("deleted");
  });

  it("maps not_found from failed envelope", async () => {
    const result = await getPostStatus(
      { postId: "post-404" },
      {
        config,
        client: {
          getJson: async () => ({
            code: 404,
            message: "post not found"
          })
        }
      }
    );

    expect(result).toEqual({
      status: "not_found"
    });
  });
});
