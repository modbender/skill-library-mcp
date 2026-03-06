export interface DeltaNeutralOpportunityResponse {
  ok: boolean;
  asOf: string;
  count: number;
  opportunities: DeltaNeutralOpportunity[];
}

export interface DeltaNeutralOpportunity {
  chainId: number;
  coin: string;
  poolAddress: string;
  platformUrl: string;
  platformLogo?: string | null;
  fundingAprYearlyPct: number;
  fundingAprAbsPct: number;
  borrowAprPct: number;
  borrowFeePct: {
    marketplaceFeePct: number;
    protocolFeePct: number;
    totalBorrowFeePct: number;
  };
  netAprPct: number;
  principalAvailable: string;
  principalAvailableUsd: number;
  allPlatforms: PlatformFundingData[];
  raw?: unknown;
}

export interface PlatformFundingData {
  platformUrl: string;
  platformLogo?: string | null;
  fundingAprYearlyPct: number;
  fundingAprAbsPct: number;
  fundingRate8h?: number | null;
  fundingRateHourly?: number | null;
  oraclePx?: number | null;
  openInterest?: number | null;
}

export interface BorrowGeneralResponse {
  updated_at: number;
  ttl_ms: number;
  count: number;
  filters: Record<string, unknown>;
  results: BorrowPool[];
}

export interface BorrowPool {
  chainId: number;
  pool_address: string;
  collateral_token_address: string;
  collateral_token_symbol: string;
  borrow_token_address: string;
  borrow_token_symbol: string;
  active: boolean;
  isV2?: boolean;
  enrichment?: {
    marketId?: number;
    marketplaceFeePercent?: number | null;
    paymentCycleDuration?: number | null;
    collateralRatioBps?: number;
    collateralRatioPct?: number;
    principalToken?: string;
    principalTokenDecimals?: number;
    minInterestRateBps?: number;
    minInterestRatePct?: number;
    principalAvailableRaw?: string;
    principalAvailable?: number;
    principalAvailableUsd?: number | null;
  };
  enrichmentError?: string;
}

export interface BorrowTerms {
  wallet: string;
  chainId: number;
  collateralToken: string;
  collateralTokenSymbol: string;
  poolAddress: string;
  borrowToken: string;
  borrowTokenSymbol: string;
  collateralWalletBalance?: number;
  collateralWalletBalanceUsd?: number | null;
  collateralSuppliedTokens?: number;
  collateralSuppliedUsd?: number;
  collateralTotalUsd?: number;
  ltvPct?: number;
  collateralRatioPct?: number;
  collateralRatioBps?: number;
  minInterestRatePct?: number;
  minInterestRateBps?: number;
  marketplaceFeePercent?: number;
  paymentCycleDuration?: number;
  paymentCycleDurationYears?: number;
  termInterestPct?: number;
  aprPct?: number;
  principalAvailable?: string;
  principalAvailableUsd?: number;
  maxBorrowByCollateral?: number;
  maxBorrowUsd?: number;
  maxCollateralNeededUsd?: number;
  maxCollateralAmount?: number | null;
  collateralPrice?: number | null;
  marketId?: string;
  principalToken?: string;
  principalTokenDecimals?: number;
  isV2?: boolean;
  poolVersion?: string;
  error?: string;
}

export interface BorrowTransactionsResponse {
  transactions: Array<{
    to: string;
    data: string;
    functionName: string;
    args: Array<string | number>;
    description: string;
    value: string;
  }>;
  summary: {
    totalTransactions: number;
    needsApproval: boolean;
    needsForwarderApproval: boolean;
    needsZeroAllowance: boolean;
    [key: string]: unknown;
  };
}

export interface LoansResponse {
  walletAddress: string;
  chainId: number;
  count: number;
  loans: Loan[];
}

export interface Loan {
  bidId: string;
  borrowerAddress: string;
  lenderAddress: string;
  lendingTokenAddress: string;
  principal: string;
  status: string;
  apr?: string;
  loanDuration?: string;
  paymentCycle?: string;
  paymentCycleAmount?: string;
  acceptedTimestamp?: string;
  nextDueDate?: string;
  collateral?: unknown;
  marketplace?: unknown;
  [key: string]: unknown;
}

export interface RepayTransactionsResponse {
  transactions: Array<{
    to: string;
    data: string;
    functionName: string;
    args: Array<string | number>;
    description: string;
    value: string;
  }>;
  summary: {
    totalTransactions: number;
    loanId: number;
    repaymentAmount: string;
    isFullRepayment: boolean;
    lendingToken?: string;
    [key: string]: unknown;
  };
}
