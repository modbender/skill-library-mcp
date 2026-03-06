import { requireEnv } from "./utils.mjs";

export class PostizDraftError extends Error {
  constructor(message, context = {}) {
    super(message);
    this.name = "PostizDraftError";
    this.context = context;
  }
}

function normalizeBaseUrl(rawUrl) {
  return rawUrl.replace(/\/+$/, "");
}

export async function postizCreateDraft({
  caption,
  mediaRefs,
  timeoutMs = 15000,
  idempotencyKey,
}) {
  const baseUrl = normalizeBaseUrl(
    process.env.POSTIZ_BASE_URL || "https://api.postiz.com/public/v1"
  );
  const apiKey = requireEnv("POSTIZ_API_KEY");
  const integrationId = requireEnv("POSTIZ_TIKTOK_INTEGRATION_ID");

  if (!Array.isArray(mediaRefs) || mediaRefs.length === 0) {
    throw new PostizDraftError("postizCreateDraft requires at least one uploaded media reference.");
  }

  const payload = {
    integrationId,
    caption,
    media: mediaRefs,
    privacy_level: "SELF_ONLY",
    content_posting_method: "UPLOAD",
  };

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  const response = await fetch(`${baseUrl}/posts`, {
    method: "POST",
    headers: {
      Authorization: apiKey,
      "Content-Type": "application/json",
      ...(idempotencyKey
        ? {
            "Idempotency-Key": idempotencyKey,
          }
        : {}),
    },
    body: JSON.stringify(payload),
    signal: controller.signal,
  });
  clearTimeout(timer);

  if (!response.ok) {
    const body = await response.text();
    throw new PostizDraftError(`Postiz draft creation failed (${response.status}): ${body}`, {
      status: response.status,
      integrationId,
    });
  }

  const json = await response.json();
  return {
    request: payload,
    response: json,
    postId: json?.id || json?.data?.id || json?.result?.id || null,
    status: json?.status || json?.data?.status || json?.result?.status || "unknown",
  };
}
