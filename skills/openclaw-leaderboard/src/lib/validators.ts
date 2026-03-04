import { z } from "zod/v4";

export const currencyEnum = z.enum(["USD", "EUR", "GBP", "BTC", "ETH"]);
export const proofTypeEnum = z.enum([
  "SCREENSHOT",
  "LINK",
  "TRANSACTION_HASH",
  "DESCRIPTION_ONLY",
]);
export const voteTypeEnum = z.enum(["LEGIT", "SUSPICIOUS"]);

export const submissionCreateSchema = z.object({
  openclawInstanceId: z
    .string()
    .min(1, "Instance ID is required")
    .max(100, "Instance ID too long"),
  openclawName: z
    .string()
    .min(1, "Name is required")
    .max(50, "Name must be under 50 characters"),
  description: z
    .string()
    .min(10, "Description must be at least 10 characters")
    .max(2000, "Description must be under 2000 characters"),
  amountCents: z
    .number()
    .int("Amount must be a whole number of cents")
    .positive("Amount must be positive")
    .max(100_000_000_00, "Amount too large"), // $100M max
  currency: currencyEnum,
  proofType: proofTypeEnum,
  proofUrl: z
    .url("Invalid URL")
    .refine((url) => /^https?:\/\//i.test(url), "URL must use http or https protocol")
    .optional(),
  proofDescription: z.string().max(5000).optional(),
  transactionHash: z.string().max(200).optional(),
  verificationMethod: z
    .string()
    .min(10, "Verification method must be at least 10 characters")
    .max(1000, "Verification method must be under 1000 characters"),
  systemPrompt: z.string().max(10000).optional(),
  modelId: z.string().max(200).optional(),
  modelProvider: z.string().max(100).optional(),
  tools: z.array(z.string().max(200)).max(50).optional(),
  modelConfig: z.record(z.string(), z.unknown()).optional(),
  configNotes: z.string().max(5000).optional(),
});

export const leaderboardQuerySchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  pageSize: z.coerce.number().int().min(1).max(100).default(20),
  currency: currencyEnum.optional(),
  period: z.enum(["day", "week", "month", "year", "all"]).default("all"),
});

export const voteCreateSchema = z.object({
  voteType: voteTypeEnum,
});

export type SubmissionCreateInput = z.infer<typeof submissionCreateSchema>;
export type LeaderboardQuery = z.infer<typeof leaderboardQuerySchema>;
export type VoteCreateInput = z.infer<typeof voteCreateSchema>;
