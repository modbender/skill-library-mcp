import fs from "node:fs";
import { basename } from "node:path";
import { requireEnv } from "./utils.mjs";

export class PostizUploadError extends Error {
  constructor(message, context = {}) {
    super(message);
    this.name = "PostizUploadError";
    this.context = context;
  }
}

function normalizeBaseUrl(rawUrl) {
  return rawUrl.replace(/\/+$/, "");
}

function extractUploadedMediaRef(json) {
  const candidates = [
    json?.url,
    json?.fileUrl,
    json?.data?.url,
    json?.data?.fileUrl,
    json?.result?.url,
    json?.id,
    json?.data?.id,
    json?.result?.id,
  ];
  const value = candidates.find((item) => typeof item === "string" && item.length > 0);
  if (!value) {
    throw new Error("Upload succeeded but response did not include a media URL or ID.");
  }
  return value;
}

async function sleep(ms) {
  await new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

function shouldRetry(status) {
  return [429, 500, 502, 503, 504].includes(status);
}

function backoffMs(attempt) {
  const base = Math.min(400 * 2 ** (attempt - 1), 10_000);
  const jitter = Math.floor(Math.random() * 150);
  return base + jitter;
}

export async function postizUpload({
  filePath,
  mimeType = "image/png",
  timeoutMs = 15000,
  maxAttempts = 3,
}) {
  const baseUrl = normalizeBaseUrl(
    process.env.POSTIZ_BASE_URL || "https://api.postiz.com/public/v1"
  );
  const apiKey = requireEnv("POSTIZ_API_KEY");

  if (!fs.existsSync(filePath)) {
    throw new Error(`Cannot upload missing file: ${filePath}`);
  }

  const fileBuffer = fs.readFileSync(filePath);
  const fileSize = fs.statSync(filePath).size;
  const effectiveTimeout = Math.max(timeoutMs, Math.ceil(fileSize / 1000));
  let lastError;
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    const form = new FormData();
    form.append("file", new Blob([fileBuffer], { type: mimeType }), basename(filePath));
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), effectiveTimeout);
    try {
      const response = await fetch(`${baseUrl}/upload`, {
        method: "POST",
        headers: {
          Authorization: apiKey,
        },
        body: form,
        signal: controller.signal,
      });
      clearTimeout(timer);

      if (!response.ok) {
        const body = await response.text();
        const err = new PostizUploadError(
          `Postiz upload failed (${response.status}): ${body}`,
          { status: response.status, attempt, filePath }
        );
        if (attempt < maxAttempts && shouldRetry(response.status)) {
          await sleep(backoffMs(attempt));
          lastError = err;
          continue;
        }
        throw err;
      }

      const json = await response.json();
      return {
        mediaRef: extractUploadedMediaRef(json),
        raw: json,
        attempt,
      };
    } catch (error) {
      clearTimeout(timer);
      lastError = error;
      if (attempt >= maxAttempts) {
        break;
      }
      await sleep(backoffMs(attempt));
    }
  }
  const message = lastError instanceof Error ? lastError.message : String(lastError);
  throw new PostizUploadError(`Postiz upload failed after ${maxAttempts} attempts: ${message}`, {
    filePath,
    maxAttempts,
  });
}
