/**
 * Upload image data (base64 or data URL) to PICUI and return the public URL.
 * Used when the server receives images in chat messages.
 */
import { picui } from "./config.js";

/**
 * Convert a data URL or raw base64 to Buffer and mime type.
 */
function parseImageData(value: string): { buffer: Buffer; mime: string } | null {
  const dataUrlMatch = value.match(/^data:([^;]+);base64,(.+)$/);
  if (dataUrlMatch) {
    return {
      buffer: Buffer.from(dataUrlMatch[2], "base64"),
      mime: dataUrlMatch[1],
    };
  }
  // Raw base64 (legacy)
  if (/^[A-Za-z0-9+/=]+$/.test(value)) {
    return {
      buffer: Buffer.from(value, "base64"),
      mime: "image/png",
    };
  }
  return null;
}

export async function uploadDataUrlToPicui(dataUrl: string): Promise<string> {
  const token = picui.token;
  if (!token) {
    throw new Error("PICUI_TOKEN is not set. Add it to server/.env from https://picui.cn");
  }

  const parsed = parseImageData(dataUrl);
  if (!parsed) {
    throw new Error("Invalid image data: expected data URL (data:mime;base64,...) or base64 string");
  }

  const { buffer, mime } = parsed;
  const formData = new FormData();
  const blob = new Blob([new Uint8Array(buffer)], { type: mime });
  formData.append("file", blob, "image.png");

  const picuiRes = await fetch(`${picui.baseURL}/upload`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/json",
    },
    body: formData,
  });

  const json = (await picuiRes.json()) as {
    status?: boolean;
    message?: string;
    data?: { links?: { url?: string } };
  };

  if (!picuiRes.ok) {
    throw new Error(json.message ?? `PICUI upload failed: ${picuiRes.statusText}`);
  }

  const url = json.data?.links?.url;
  if (!url) {
    throw new Error("PICUI did not return image URL");
  }

  return url;
}

/**
 * Upload a buffer (e.g. rendered PNG) to PICUI and return the public URL.
 */
export async function uploadBufferToPicui(
  buffer: Buffer,
  mime = "image/png",
): Promise<string> {
  const token = picui.token;
  if (!token) {
    throw new Error("PICUI_TOKEN is not set. Add it to server/.env from https://picui.cn");
  }

  const formData = new FormData();
  const blob = new Blob([new Uint8Array(buffer)], { type: mime });
  formData.append("file", blob, "image.png");

  const picuiRes = await fetch(`${picui.baseURL}/upload`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/json",
    },
    body: formData,
  });

  const json = (await picuiRes.json()) as {
    status?: boolean;
    message?: string;
    data?: { links?: { url?: string } };
  };

  if (!picuiRes.ok) {
    throw new Error(json.message ?? `PICUI upload failed: ${picuiRes.statusText}`);
  }

  const url = json.data?.links?.url;
  if (!url) {
    throw new Error("PICUI did not return image URL");
  }

  return url;
}

/**
 * Check if the image value needs upload to PICUI (base64 or data URL).
 * http(s) URLs are already hosted and can be used as-is.
 */
export function needsPicuiUpload(value: string): boolean {
  return (
    !value.startsWith("http://") &&
    !value.startsWith("https://")
  );
}
