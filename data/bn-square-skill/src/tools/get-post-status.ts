import { buildPostStatusQuery, getEndpointPath, resolvePostUrl } from "../api/endpoints";
import {
  asRecord,
  binanceEnvelopeSchema,
  extractDataRecord,
  extractEnvelopeMessage,
  extractStringCandidate,
  getPostStatusInputSchema,
  getPostStatusResultSchema,
  isEnvelopeSuccess,
  normalizeEnvelopeCode,
  type GetPostStatusInput,
  type GetPostStatusResult
} from "../api/types";
import type { BinanceConfig } from "../config/schema";
import { ApiError } from "../utils/errors";

export type GetPostStatusDependencies = {
  client: {
    getJson: (path: string, options?: { query?: Record<string, string> }) => Promise<unknown>;
  };
  config: BinanceConfig;
};

const isNotFoundSignal = (code: string | undefined, message: string | undefined): boolean => {
  const normalizedCode = code?.toLowerCase();
  const normalizedMessage = message?.toLowerCase();

  return (
    normalizedCode === "404" ||
    normalizedCode === "not_found" ||
    normalizedCode === "post_not_found" ||
    normalizedMessage?.includes("not found") === true
  );
};

const mapStatus = (statusValue: unknown): GetPostStatusResult["status"] => {
  if (typeof statusValue === "number") {
    if (statusValue === 1) {
      return "published";
    }
    if (statusValue === 0 || statusValue === 2) {
      return "pending_review";
    }
    if (statusValue === -1 || statusValue === 3) {
      return "deleted";
    }
  }

  if (typeof statusValue === "string") {
    const normalized = statusValue.trim().toLowerCase();
    if (normalized.includes("publish") || normalized.includes("online") || normalized.includes("success")) {
      return "published";
    }
    if (normalized.includes("pending") || normalized.includes("review") || normalized.includes("audit")) {
      return "pending_review";
    }
    if (normalized.includes("delete") || normalized.includes("remove") || normalized.includes("block")) {
      return "deleted";
    }
    if (normalized.includes("not_found") || normalized.includes("not found") || normalized === "404") {
      return "not_found";
    }
  }

  return "pending_review";
};

export const getPostStatus = async (
  input: GetPostStatusInput,
  dependencies: GetPostStatusDependencies
): Promise<GetPostStatusResult> => {
  const parsedInput = getPostStatusInputSchema.parse(input);
  const endpoint = getEndpointPath(dependencies.config, "getPostStatus");
  const query = buildPostStatusQuery(dependencies.config, parsedInput.postId);
  const rawResponse = await dependencies.client.getJson(endpoint, { query });
  const envelopeResult = binanceEnvelopeSchema.safeParse(rawResponse);

  if (!envelopeResult.success) {
    const fallback = asRecord(rawResponse) ?? {};
    const fallbackStatus = mapStatus(fallback.status);
    const postUrl =
      extractStringCandidate(fallback, ["postUrl", "url", "shareUrl"]) ??
      resolvePostUrl(dependencies.config, parsedInput.postId);

    return getPostStatusResultSchema.parse({
      status: fallbackStatus,
      ...(fallbackStatus === "not_found" ? {} : { postUrl })
    });
  }

  const envelope = envelopeResult.data;
  const envelopeMessage = extractEnvelopeMessage(envelope);
  const envelopeCode = normalizeEnvelopeCode(envelope.code);
  if (!isEnvelopeSuccess(envelope)) {
    if (isNotFoundSignal(envelopeCode, envelopeMessage)) {
      return getPostStatusResultSchema.parse({
        status: "not_found"
      });
    }
    throw new ApiError(envelopeMessage);
  }

  const data = extractDataRecord(envelope) ?? {};
  const postData = asRecord(data.post) ?? asRecord(data.article) ?? data;

  const statusValue = postData.status ?? postData.postStatus ?? postData.reviewStatus;
  const status = mapStatus(statusValue);

  if (status === "not_found") {
    return getPostStatusResultSchema.parse({
      status: "not_found"
    });
  }

  const postUrl =
    extractStringCandidate(postData, ["postUrl", "url", "shareUrl"]) ??
    extractStringCandidate(data, ["postUrl", "url", "shareUrl"]) ??
    resolvePostUrl(dependencies.config, parsedInput.postId);

  return getPostStatusResultSchema.parse({
    status,
    postUrl
  });
};
