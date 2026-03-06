import { describe, expect, it } from "bun:test";
import type { BinanceConfig } from "../config/schema";
import { ValidationError } from "./errors";
import { uploadImageFromUrl } from "./image-upload";

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
    maxBytes: 10,
    allowedMimeTypes: ["image/png", "image/jpeg"]
  }
};

describe("uploadImageFromUrl", () => {
  it("uploads downloaded image and returns Binance image URL", async () => {
    let receivedFieldValue: FormDataEntryValue | null = null;

    const uploadedImageUrl = await uploadImageFromUrl("https://example.com/image.png", {
      config,
      fetchImpl: async () =>
        new Response(new Uint8Array([1, 2, 3, 4, 5]), {
          headers: {
            "content-type": "image/png",
            "content-length": "5"
          }
        }),
      client: {
        postFormData: async (_path, formData) => {
          receivedFieldValue = formData.get("file");
          return {
            code: 0,
            data: {
              imageUrl: "https://img.binance.com/abc.png"
            }
          };
        }
      }
    });

    expect(uploadedImageUrl).toBe("https://img.binance.com/abc.png");
    expect(receivedFieldValue).not.toBeNull();
  });

  it("rejects unsupported mime type", async () => {
    await expect(
      uploadImageFromUrl("https://example.com/image.gif", {
        config,
        fetchImpl: async () =>
          new Response(new Uint8Array([1, 2, 3]), {
            headers: {
              "content-type": "image/gif"
            }
          }),
        client: {
          postFormData: async () => ({ code: 0 })
        }
      })
    ).rejects.toThrow(ValidationError);
  });

  it("rejects oversized image", async () => {
    await expect(
      uploadImageFromUrl("https://example.com/big.png", {
        config,
        fetchImpl: async () =>
          new Response(new Uint8Array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]), {
            headers: {
              "content-type": "image/png",
              "content-length": "11"
            }
          }),
        client: {
          postFormData: async () => ({ code: 0 })
        }
      })
    ).rejects.toThrow(ValidationError);
  });

  it("rejects response without image URL", async () => {
    await expect(
      uploadImageFromUrl("https://example.com/image.png", {
        config,
        fetchImpl: async () =>
          new Response(new Uint8Array([1, 2, 3]), {
            headers: {
              "content-type": "image/png"
            }
          }),
        client: {
          postFormData: async () => ({ code: 0, data: {} })
        }
      })
    ).rejects.toThrow(ValidationError);
  });
});
