import { getEndpointPath, resolvePostUrl } from "../api/endpoints";
import {
  asRecord,
  binanceEnvelopeSchema,
  extractDataRecord,
  extractEnvelopeMessage,
  extractStringCandidate,
  isEnvelopeSuccess,
  type PublishPostInput,
  type PublishPostResult,
  publishPostInputSchema,
  publishPostResultSchema
} from "../api/types";
import type { BinanceConfig } from "../config/schema";
import { SessionExpiredError, toSafeErrorMessage } from "../utils/errors";
import { uploadImageFromUrl } from "../utils/image-upload";

export type PublishPostDependencies = {
  client: {
    postJson: (path: string, body: unknown) => Promise<unknown>;
    postFormData: (path: string, formData: FormData) => Promise<unknown>;
  };
  config: BinanceConfig;
  uploadImage?: (imageUrl: string) => Promise<string>;
};

type PublishPayload = {
  content: string;
  images?: string[];
  poll?: {
    question: string;
    options: string[];
    durationHours: number;
  };
};

const buildPayload = (input: PublishPostInput, uploadedImageUrls: string[]): PublishPayload => ({
  content: input.content,
  ...(uploadedImageUrls.length > 0 ? { images: uploadedImageUrls } : {}),
  ...(input.poll
    ? {
        poll: {
          question: input.poll.question,
          options: input.poll.options,
          durationHours: input.poll.durationHours
        }
      }
    : {})
});

const extractPublishResult = (config: BinanceConfig, rawResponse: unknown): PublishPostResult => {
  const envelopeResult = binanceEnvelopeSchema.safeParse(rawResponse);
  const rootRecord = asRecord(rawResponse) ?? {};

  if (envelopeResult.success) {
    if (!isEnvelopeSuccess(envelopeResult.data)) {
      return publishPostResultSchema.parse({
        success: false,
        error: extractEnvelopeMessage(envelopeResult.data)
      });
    }

    const data = extractDataRecord(envelopeResult.data) ?? {};
    const postData = asRecord(data.post) ?? asRecord(data.article) ?? data;

    const postId =
      extractStringCandidate(postData, ["postId", "id", "articleId", "feedId"]) ??
      extractStringCandidate(data, ["postId", "id", "articleId", "feedId"]);
    const postUrl =
      extractStringCandidate(postData, ["postUrl", "url", "shareUrl"]) ??
      extractStringCandidate(data, ["postUrl", "url", "shareUrl"]) ??
      (postId ? resolvePostUrl(config, postId) : undefined);

    return publishPostResultSchema.parse({
      success: true,
      ...(postId ? { postId } : {}),
      ...(postUrl ? { postUrl } : {})
    });
  }

  const fallbackPostId = extractStringCandidate(rootRecord, ["postId", "id", "articleId", "feedId"]);
  const fallbackPostUrl =
    extractStringCandidate(rootRecord, ["postUrl", "url", "shareUrl"]) ??
    (fallbackPostId ? resolvePostUrl(config, fallbackPostId) : undefined);

  return publishPostResultSchema.parse({
    success: true,
    ...(fallbackPostId ? { postId: fallbackPostId } : {}),
    ...(fallbackPostUrl ? { postUrl: fallbackPostUrl } : {})
  });
};

export const publishPost = async (
  input: PublishPostInput,
  dependencies: PublishPostDependencies
): Promise<PublishPostResult> => {
  try {
    const parsedInput = publishPostInputSchema.parse(input);
    const uploadImage =
      dependencies.uploadImage ??
      ((imageUrl: string) =>
        uploadImageFromUrl(imageUrl, {
          client: dependencies.client,
          config: dependencies.config
        }));

    const imageUrls = parsedInput.imageUrls ?? [];
    const uploadedImageUrls =
      imageUrls.length > 0 ? await Promise.all(imageUrls.map((imageUrl) => uploadImage(imageUrl))) : [];
    const payload = buildPayload(parsedInput, uploadedImageUrls);

    const endpoint = getEndpointPath(dependencies.config, "publishPost");
    const rawResponse = await dependencies.client.postJson(endpoint, payload);
    return extractPublishResult(dependencies.config, rawResponse);
  } catch (error) {
    if (error instanceof SessionExpiredError) {
      return publishPostResultSchema.parse({
        success: false,
        error: "Session expired or unauthorized"
      });
    }

    return publishPostResultSchema.parse({
      success: false,
      error: toSafeErrorMessage(error, "Unable to publish post")
    });
  }
};
