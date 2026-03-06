import type {
  BorrowGeneralResponse,
  BorrowTerms,
  BorrowTransactionsResponse,
  DeltaNeutralOpportunityResponse,
  LoansResponse,
  RepayTransactionsResponse
} from './types.js';

export interface TellerApiClientOptions {
  baseUrl?: string;
  timeoutMs?: number;
}

const DEFAULT_BASE_URL = process.env.TELLER_API_BASE_URL?.trim() || 'https://delta-neutral-api.teller.org';
const DEFAULT_TIMEOUT_MS = Number(process.env.TELLER_API_TIMEOUT_MS ?? 15_000);

export class TellerApiClient {
  private readonly baseUrl: string;
  private readonly timeoutMs: number;

  constructor(options: TellerApiClientOptions = {}) {
    this.baseUrl = options.baseUrl ?? DEFAULT_BASE_URL;
    this.timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  }

  async getDeltaNeutralOpportunities(params?: { chainId?: number; coin?: string; limit?: number; minNetAprPct?: number }): Promise<DeltaNeutralOpportunityResponse> {
    const response = await this.request<DeltaNeutralOpportunityResponse>('/perps/delta-neutral');

    const filtered = response.opportunities.filter(opportunity => {
      const matchesChain = params?.chainId ? opportunity.chainId === params.chainId : true;
      const matchesCoin = params?.coin ? opportunity.coin.toLowerCase() === params.coin.toLowerCase() : true;
      const matchesApr = params?.minNetAprPct !== undefined ? opportunity.netAprPct >= params.minNetAprPct : true;
      return matchesChain && matchesCoin && matchesApr;
    });

    const limited = params?.limit ? filtered.slice(0, params.limit) : filtered;

    return {
      ...response,
      count: limited.length,
      opportunities: limited
    };
  }

  getBorrowPools(query?: {
    chainId?: number;
    collateralTokenAddress?: string;
    borrowTokenAddress?: string;
    poolAddress?: string;
    ttl?: number;
  }): Promise<BorrowGeneralResponse> {
    return this.request<BorrowGeneralResponse>('/borrow/general', {
      chainId: query?.chainId,
      collateral_token_address: query?.collateralTokenAddress,
      borrow_token_address: query?.borrowTokenAddress,
      pool_address: query?.poolAddress,
      ttl: query?.ttl
    });
  }

  getBorrowTerms(params: { wallet: string; chainId: number; collateralToken: string; poolAddress: string }): Promise<BorrowTerms> {
    return this.request<BorrowTerms>('/borrow-terms', {
      wallet: params.wallet,
      chainId: params.chainId,
      collateralToken: params.collateralToken,
      poolAddress: params.poolAddress
    });
  }

  getBorrowTransactions(params: {
    walletAddress: string;
    collateralTokenAddress: string;
    chainId: number;
    poolAddress: string;
    collateralAmount: string;
    principalAmount: string;
    loanDuration?: number;
  }): Promise<BorrowTransactionsResponse> {
    return this.request<BorrowTransactionsResponse>('/borrow-tx', {
      walletAddress: params.walletAddress,
      collateralTokenAddress: params.collateralTokenAddress,
      chainId: params.chainId,
      poolAddress: params.poolAddress,
      collateralAmount: params.collateralAmount,
      principalAmount: params.principalAmount,
      loanDuration: params.loanDuration
    });
  }

  getLoans(params: { walletAddress: string; chainId: number }): Promise<LoansResponse> {
    return this.request<LoansResponse>('/loans/get-all', {
      walletAddress: params.walletAddress,
      chainId: params.chainId
    });
  }

  getRepayTransactions(params: { bidId: number; chainId: number; walletAddress: string; amount?: string }): Promise<RepayTransactionsResponse> {
    return this.request<RepayTransactionsResponse>('/loans/repay-tx', {
      bidId: params.bidId,
      chainId: params.chainId,
      walletAddress: params.walletAddress,
      amount: params.amount
    });
  }

  private async request<T>(path: string, query?: Record<string, string | number | boolean | undefined>): Promise<T> {
    const url = new URL(path, this.baseUrl);
    if (query) {
      for (const [key, value] of Object.entries(query)) {
        if (value === undefined || value === null || value === '') continue;
        url.searchParams.set(key, String(value));
      }
    }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.timeoutMs);

    try {
      const response = await fetch(url, {
        signal: controller.signal,
        headers: {
          'accept': 'application/json'
        }
      });

      if (!response.ok) {
        const body = await response.text();
        throw new Error(`Request failed with ${response.status}: ${body}`);
      }

      return (await response.json()) as T;
    } catch (error) {
      if ((error as Error).name === 'AbortError') {
        throw new Error(`Request timed out after ${this.timeoutMs}ms`);
      }
      throw error;
    } finally {
      clearTimeout(timeout);
    }
  }
}
