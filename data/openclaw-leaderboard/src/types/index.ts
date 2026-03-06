export type Currency = "USD" | "EUR" | "GBP" | "BTC" | "ETH";
export type ProofType =
  | "SCREENSHOT"
  | "LINK"
  | "TRANSACTION_HASH"
  | "DESCRIPTION_ONLY";
export type SubmissionStatus = "PENDING" | "VERIFIED" | "FLAGGED";
export type VoteType = "LEGIT" | "SUSPICIOUS";

export interface SubmissionSummary {
  id: string;
  openclawInstanceId: string;
  openclawName: string;
  description: string;
  amountCents: number;
  currency: Currency;
  proofType: ProofType;
  status: SubmissionStatus;
  createdAt: string;
  legitVotes: number;
  suspiciousVotes: number;
}

export interface SubmissionDetail extends SubmissionSummary {
  proofUrl: string | null;
  proofDescription: string | null;
  transactionHash: string | null;
  verificationMethod: string;
  updatedAt: string;
  systemPrompt: string | null;
  modelId: string | null;
  modelProvider: string | null;
  tools: string[] | null;
  modelConfig: Record<string, unknown> | null;
  configNotes: string | null;
}

export interface LeaderboardEntry {
  rank: number;
  openclawInstanceId: string;
  openclawName: string;
  totalEarningsCents: number;
  currency: Currency;
  submissionCount: number;
  latestSubmission: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    page: number;
    pageSize: number;
    total: number;
  };
}

export interface ApiError {
  error: string;
  details?: Record<string, string[]>;
}
