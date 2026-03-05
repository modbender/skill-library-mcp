/**
 * HTTP client for the Auction House API v1
 */

const DEFAULT_BASE_URL = 'https://www.houseproto.fun';

function getBaseUrl(): string {
  return process.env.AUCTION_HOUSE_URL || DEFAULT_BASE_URL;
}

function getApiKey(): string {
  const key = process.env.AUCTION_HOUSE_API_KEY;
  if (!key) {
    throw new Error(
      'AUCTION_HOUSE_API_KEY environment variable is not set. ' +
        'Generate one at https://www.houseproto.fun/settings'
    );
  }
  return key;
}

interface ApiResponse<T = any> {
  ok: boolean;
  status: number;
  data: T;
}

async function request<T = any>(
  method: string,
  path: string,
  body?: any
): Promise<ApiResponse<T>> {
  const url = `${getBaseUrl()}/api/v1${path}`;
  const headers: Record<string, string> = {
    'x-api-key': getApiKey(),
    'Content-Type': 'application/json',
  };

  const res = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const data = await res.json();

  return {
    ok: res.ok,
    status: res.status,
    data,
  };
}

// ─── Read Operations ───

export async function listAuctions(params?: {
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<ApiResponse> {
  const query = new URLSearchParams();
  if (params?.status) query.set('status', params.status);
  if (params?.limit) query.set('limit', params.limit.toString());
  if (params?.offset) query.set('offset', params.offset.toString());

  const qs = query.toString();
  return request('GET', `/auctions${qs ? `?${qs}` : ''}`);
}

export async function searchAuctions(params: {
  search?: string;
  currency?: string;
  token?: string;
  minPrice?: number;
  maxPrice?: number;
  createdAfter?: string;
  endingWithin?: number;
  sort?: string;
  status?: string;
  limit?: number;
}): Promise<ApiResponse> {
  const query = new URLSearchParams();
  if (params.search) query.set('search', params.search);
  if (params.currency) query.set('currency', params.currency);
  if (params.token) query.set('token', params.token);
  if (params.minPrice !== undefined) query.set('minPrice', params.minPrice.toString());
  if (params.maxPrice !== undefined) query.set('maxPrice', params.maxPrice.toString());
  if (params.createdAfter) query.set('createdAfter', params.createdAfter);
  if (params.endingWithin !== undefined) query.set('endingWithin', params.endingWithin.toString());
  if (params.sort) query.set('sort', params.sort);
  if (params.status) query.set('status', params.status);
  if (params.limit) query.set('limit', params.limit.toString());

  const qs = query.toString();
  return request('GET', `/auctions${qs ? `?${qs}` : ''}`);
}

export async function getAuction(
  blockchainAuctionId: string
): Promise<ApiResponse> {
  return request('GET', `/auctions/${blockchainAuctionId}`);
}

export async function getMyAuctions(params?: {
  status?: string;
  limit?: number;
}): Promise<ApiResponse> {
  const query = new URLSearchParams();
  if (params?.status) query.set('status', params.status);
  if (params?.limit) query.set('limit', params.limit.toString());

  const qs = query.toString();
  return request('GET', `/me/auctions${qs ? `?${qs}` : ''}`);
}

export async function getMyBids(params?: {
  limit?: number;
}): Promise<ApiResponse> {
  const query = new URLSearchParams();
  if (params?.limit) query.set('limit', params.limit.toString());

  const qs = query.toString();
  return request('GET', `/me/bids${qs ? `?${qs}` : ''}`);
}

export async function getWalletInfo(
  tokenAddress?: string
): Promise<ApiResponse> {
  const query = new URLSearchParams();
  if (tokenAddress) query.set('token', tokenAddress);

  const qs = query.toString();
  return request('GET', `/me/wallet${qs ? `?${qs}` : ''}`);
}

// ─── Write Operations ───

export async function createAuction(params: {
  auctionName: string;
  tokenAddress: string;
  minimumBid: number;
  durationHours: number;
  description?: string;
}): Promise<ApiResponse> {
  return request('POST', '/auctions/create', params);
}

export async function placeBid(
  blockchainAuctionId: string,
  amount: number
): Promise<ApiResponse> {
  return request('POST', `/auctions/${blockchainAuctionId}/bid`, { amount });
}
