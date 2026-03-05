import path from "node:path";
import type { FetchLike } from "../api/client";
import { getEndpointPath } from "../api/endpoints";
import {
  asRecord,
  binanceEnvelopeSchema,
  extractDataRecord,
  extractEnvelopeMessage,
  extractStringCandidate,
  isEnvelopeSuccess
} from "../api/types";
import type { BinanceConfig } from "../config/schema";
import { ApiError, ValidationError } from "./errors";

export type ImageUploadDependencies = {
  client: {
    postFormData: (path: string, formData: FormData) => Promise<unknown>;
  };
  config: BinanceConfig;
  fetchImpl?: FetchLike;
};

const normalizeMimeType = (value: string | null): string | undefined => {
  if (!value) {
    return undefined;
  }

  return value.split(";")[0]?.trim().toLowerCase();
};

const inferFileName = (imageUrl: string, mimeType: string | undefined): string => {
  try {
    const parsedUrl = new URL(imageUrl);
    const candidateName = path.basename(parsedUrl.pathname);
    if (candidateName && candidateName !== "/") {
      return candidateName;
    }
  } catch {
    // No-op; caller validates URL separately.
  }

  if (mimeType === "image/png") {
    return "upload.png";
  }
  if (mimeType === "image/webp") {
    return "upload.webp";
  }
  return "upload.jpg";
};

const extractUploadResultUrl = (rawResponse: unknown): string | undefined => {
  const envelopeResult = binanceEnvelopeSchema.safeParse(rawResponse);

  if (envelopeResult.success) {
    if (!isEnvelopeSuccess(envelopeResult.data)) {
      throw new ApiError(extractEnvelopeMessage(envelopeResult.data));
    }

    const data = extractDataRecord(envelopeResult.data) ?? {};
    const nestedImage = asRecord(data.image) ?? asRecord(data.asset) ?? {};

    return (
      extractStringCandidate(data, ["url", "imageUrl", "imageURL", "location"]) ??
      extractStringCandidate(nestedImage, ["url", "imageUrl", "imageURL", "location"]) ??
      extractStringCandidate(asRecord(rawResponse) ?? {}, ["url", "imageUrl", "imageURL", "location"])
    );
  }

  const fallbackRecord = asRecord(rawResponse) ?? {};
  return extractStringCandidate(fallbackRecord, ["url", "imageUrl", "imageURL", "location"]);
};

export const uploadImageFromUrl = async (
  imageUrl: string,
  dependencies: ImageUploadDependencies
): Promise<string> => {
  let parsedUrl: URL;

  try {
    parsedUrl = new URL(imageUrl);
  } catch {
    throw new ValidationError("imageUrl must be a valid URL");
  }

  const fetchImpl = dependencies.fetchImpl ?? fetch;
  const imageResponse = await fetchImpl(parsedUrl.toString(), {
    method: "GET",
    redirect: "follow"
  });

  if (!imageResponse.ok) {
    throw new ApiError(`Unable to download image from URL (status ${imageResponse.status})`, imageResponse.status);
  }

  const mimeType = normalizeMimeType(imageResponse.headers.get("content-type"));
  const allowedMimeTypes = dependencies.config.image.allowedMimeTypes.map((item) => item.toLowerCase());
  if (!mimeType || !allowedMimeTypes.includes(mimeType)) {
    throw new ValidationError(`Unsupported image mime type: ${mimeType ?? "unknown"}`);
  }

  const contentLengthRaw = imageResponse.headers.get("content-length");
  if (contentLengthRaw) {
    const declaredSize = Number(contentLengthRaw);
    if (Number.isFinite(declaredSize) && declaredSize > dependencies.config.image.maxBytes) {
      throw new ValidationError(`Image exceeds size limit (${dependencies.config.image.maxBytes} bytes)`);
    }
  }

  const bytes = new Uint8Array(await imageResponse.arrayBuffer());
  if (bytes.byteLength > dependencies.config.image.maxBytes) {
    throw new ValidationError(`Image exceeds size limit (${dependencies.config.image.maxBytes} bytes)`);
  }

  const fileName = inferFileName(imageUrl, mimeType);
  const fileBlob = new Blob([bytes], { type: mimeType });
  const formData = new FormData();
  formData.append(dependencies.config.image.uploadFieldName, fileBlob, fileName);

  const endpoint = getEndpointPath(dependencies.config, "imageUpload");
  const rawUploadResponse = await dependencies.client.postFormData(endpoint, formData);
  const uploadedImageUrl = extractUploadResultUrl(rawUploadResponse);

  if (!uploadedImageUrl) {
    throw new ValidationError("Image upload response does not include an image URL");
  }

  return uploadedImageUrl;
};
