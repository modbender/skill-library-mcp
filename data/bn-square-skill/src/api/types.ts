import { z } from "zod";

const unknownRecordSchema = z.record(z.unknown());

export const binanceEnvelopeSchema = z
  .object({
    success: z.boolean().optional(),
    code: z.union([z.number(), z.string()]).optional(),
    message: z.string().optional(),
    msg: z.string().optional(),
    data: z.unknown().optional()
  })
  .passthrough();

export type BinanceEnvelope = z.infer<typeof binanceEnvelopeSchema>;

export const normalizeEnvelopeCode = (value: BinanceEnvelope["code"]): string | undefined => {
  if (typeof value === "number") {
    return `${value}`;
  }
  if (typeof value === "string") {
    return value.trim();
  }
  return undefined;
};

export const isEnvelopeSuccess = (envelope: BinanceEnvelope): boolean => {
  if (envelope.success === false) {
    return false;
  }

  const normalizedCode = normalizeEnvelopeCode(envelope.code);
  if (normalizedCode === undefined) {
    return true;
  }

  const normalizedUpperCode = normalizedCode.toUpperCase();
  return normalizedCode === "0" || normalizedUpperCode === "SUCCESS";
};

export const extractEnvelopeMessage = (envelope: BinanceEnvelope): string =>
  envelope.message?.trim() || envelope.msg?.trim() || "Binance API request failed";

export const asRecord = (value: unknown): Record<string, unknown> | undefined => {
  const result = unknownRecordSchema.safeParse(value);
  if (!result.success) {
    return undefined;
  }
  return result.data;
};

export const extractStringCandidate = (source: Record<string, unknown>, keys: string[]): string | undefined => {
  for (const key of keys) {
    const value = source[key];
    if (typeof value === "string" && value.trim().length > 0) {
      return value.trim();
    }
    if (typeof value === "number" && Number.isFinite(value)) {
      return `${value}`;
    }
  }
  return undefined;
};

export const extractDataRecord = (envelope: BinanceEnvelope): Record<string, unknown> | undefined =>
  asRecord(envelope.data);

export const validateSessionResultSchema = z.object({
  valid: z.boolean(),
  userId: z.string().optional(),
  username: z.string().optional(),
  error: z.string().optional()
});

export const pollInputSchema = z.object({
  question: z.string().trim().min(1).max(140),
  options: z.array(z.string().trim().min(1).max(100)).min(2).max(4),
  durationHours: z.number().int().min(1).max(168).default(24)
});

export const publishPostInputSchema = z
  .object({
    content: z.string().trim().min(1).max(10_000),
    imageUrls: z.array(z.string().url()).max(9).optional(),
    poll: pollInputSchema.optional()
  })
  .superRefine((value, ctx) => {
    if (value.poll && value.imageUrls && value.imageUrls.length > 0) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "poll posts cannot include images",
        path: ["imageUrls"]
      });
    }
  });

export const publishPostResultSchema = z.object({
  success: z.boolean(),
  postId: z.string().optional(),
  postUrl: z.string().url().optional(),
  error: z.string().optional()
});

export const getPostStatusInputSchema = z.object({
  postId: z.string().trim().min(1)
});

export const postStatusSchema = z.union([
  z.literal("published"),
  z.literal("pending_review"),
  z.literal("deleted"),
  z.literal("not_found")
]);

export const getPostStatusResultSchema = z.object({
  status: postStatusSchema,
  postUrl: z.string().url().optional()
});

export type ValidateSessionResult = z.infer<typeof validateSessionResultSchema>;
export type PublishPostInput = z.infer<typeof publishPostInputSchema>;
export type PublishPostResult = z.infer<typeof publishPostResultSchema>;
export type GetPostStatusInput = z.infer<typeof getPostStatusInputSchema>;
export type GetPostStatusResult = z.infer<typeof getPostStatusResultSchema>;
