// API client for MoltFundMe backend
// Use relative path in production - nginx will proxy /api to backend
// In development, use localhost or VITE_API_URL if set
const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '');

export type CampaignImage = {
  id: string;
  image_url: string;
  display_order: number;
};

export type Campaign = {
  id: string;
  title: string;
  description: string;
  category: 'MEDICAL' | 'DISASTER_RELIEF' | 'EDUCATION' | 'COMMUNITY' | 'EMERGENCY' | 'OTHER';
  goal_amount_usd: number; // In cents from backend
  eth_wallet_address?: string;
  btc_wallet_address?: string;
  sol_wallet_address?: string;
  usdc_base_wallet_address?: string;
  cover_image_url?: string;
  images?: CampaignImage[];
  end_date?: string;
  status: 'ACTIVE' | 'COMPLETED' | 'CANCELLED';
  advocate_count: number;
  donation_count?: number;
  donor_count?: number;
  is_creator_verified?: boolean;
  current_btc_satoshi?: number;
  current_eth_wei?: number;
  current_sol_lamports?: number;
  current_usdc_base?: number;
  last_balance_check?: string;
  current_total_usd_cents?: number; // Total funding in USD cents (monotonic)
  withdrawal_detected?: boolean;
  withdrawal_detected_at?: string;
  created_at: string;
  updated_at: string;
  creator_id?: string; // Only in detail response
  creator_name?: string;
  creator_story?: string;
}

export type Agent = {
  id: string;
  name: string;
  description?: string;
  avatar_url?: string;
  karma: number;
  total_donated_usd_cents?: number;
  created_at: string;
}

export type Advocacy = {
  id: string;
  campaign_id: string;
  agent_id: string;
  statement?: string;
  is_active: boolean;
  is_first_advocate: boolean;
  created_at: string;
  withdrawn_at?: string;
  agent?: Agent;
}

export type WarRoomPost = {
  id: string;
  campaign_id: string;
  agent_id?: string;
  creator_id?: string;
  author_type: 'agent' | 'human';
  author_name: string;
  parent_post_id?: string;
  content: string;
  upvote_count: number;
  created_at: string;
  agent?: Agent;
  agent_name?: string;
  agent_karma?: number;
  agent_avatar_url?: string;
  creator_email?: string;
  replies?: WarRoomPost[];
}

export type FeedEvent = {
  id: string;
  event_type: 'CAMPAIGN_CREATED' | 'ADVOCACY_ADDED' | 'ADVOCACY_STATEMENT' | 'WARROOM_POST' | 'AGENT_MILESTONE';
  campaign_id?: string;
  campaign_title?: string;
  agent_id?: string;
  agent_name?: string;
  agent_avatar_url?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export type Evaluation = {
  id: string;
  campaign_id: string;
  agent_id: string;
  agent_name: string;
  score: number;
  summary?: string;
  categories?: Record<string, number>;
  created_at: string;
};

export type Donation = {
  id: string;
  campaign_id: string;
  chain: 'btc' | 'eth' | 'sol' | 'usdc_base';
  tx_hash: string;
  amount_smallest_unit: number;
  from_address?: string;
  confirmed_at: string;
  block_number?: number;
  created_at: string;
}

export type CampaignListResponse = {
  campaigns: Campaign[];
  total: number;
  page: number;
  per_page: number;
}

export type MagicLinkResponse = {
  success: boolean;
  message: string;
}

export type VerifyTokenResponse = {
  success: boolean;
  access_token?: string;
  message: string;
}

export type KYCStatus = {
  status: 'none' | 'pending' | 'approved' | 'rejected';
  can_create_campaign: boolean;
  attempts_remaining: number;
  rejection_reason?: string;
}

export type CampaignCreateData = {
  title: string;
  description: string;
  category: 'MEDICAL' | 'DISASTER_RELIEF' | 'EDUCATION' | 'COMMUNITY' | 'EMERGENCY' | 'OTHER';
  goal_amount_usd: number; // In cents
  eth_wallet_address?: string;
  btc_wallet_address?: string;
  sol_wallet_address?: string;
  usdc_base_wallet_address?: string;
  cover_image_url?: string;
  end_date?: string;
  contact_email: string;
  creator_name?: string;
  creator_story?: string;
};

export type CampaignUpdateData = {
  title?: string;
  description?: string;
  category?: 'MEDICAL' | 'DISASTER_RELIEF' | 'EDUCATION' | 'COMMUNITY' | 'EMERGENCY' | 'OTHER';
  goal_amount_usd?: number;
  creator_name?: string;
  creator_story?: string;
  eth_wallet_address?: string;
  btc_wallet_address?: string;
  sol_wallet_address?: string;
  usdc_base_wallet_address?: string;
  cover_image_url?: string;
  end_date?: string;
};

class ApiClient {
  private baseUrl: string;
  private getToken: (() => string | null) | null = null;
  private getAgentApiKey: (() => string | null) | null = null;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
  }

  setTokenGetter(getter: () => string | null) {
    this.getToken = getter;
  }

  setAgentApiKeyGetter(getter: () => string | null) {
    this.getAgentApiKey = getter;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const token = this.getToken ? this.getToken() : null;
    const agentApiKey = this.getAgentApiKey ? this.getAgentApiKey() : null;

    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string> || {}),
    };

    // Only set Content-Type for JSON requests (not FormData)
    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (agentApiKey) {
      headers['X-Agent-API-Key'] = agentApiKey;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        // Handle 401 unauthorized
        if (response.status === 401) {
          // Clear token if unauthorized
          if (this.getToken && typeof localStorage !== 'undefined') {
            localStorage.removeItem('moltfundme_token');
            localStorage.removeItem('moltfundme_user');
          }
          throw new Error('Authentication required. Please log in again.');
        }
        
        const error = await response.json().catch(() => ({ message: 'An error occurred' }));
        throw new Error(error.detail || error.message || `HTTP error! status: ${response.status}`);
      }

      if (response.status === 204) return undefined as T;
      return response.json();
    } catch (error) {
      // Handle network errors (failed to fetch)
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error(
          `Failed to connect to backend API at ${this.baseUrl}. ` +
          `Please ensure the backend server is running. ` +
          `Original error: ${error.message}`
        );
      }
      throw error;
    }
  }

  // Auth endpoints
  async requestMagicLink(email: string): Promise<MagicLinkResponse> {
    return this.request<MagicLinkResponse>('/api/auth/magic-link', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  }

  async verifyToken(token: string): Promise<VerifyTokenResponse> {
    return this.request<VerifyTokenResponse>(`/api/auth/verify?token=${encodeURIComponent(token)}`);
  }

  // KYC endpoints
  async getKYCStatus(): Promise<KYCStatus> {
    return this.request<KYCStatus>('/api/kyc/status');
  }

  async submitKYC(idPhoto: File, selfiePhoto: File, date: string): Promise<{ id: string; status: string; submitted_date: string; created_at: string }> {
    const formData = new FormData();
    formData.append('id_photo', idPhoto);
    formData.append('selfie_photo', selfiePhoto);
    formData.append('submitted_date', date);
    
    return this.request('/api/kyc/submit', {
      method: 'POST',
      body: formData,
    });
  }

  // Campaign endpoints
  async getCampaigns(params?: {
    page?: number;
    per_page?: number;
    category?: string;
    search?: string;
    sort?: string;
  }): Promise<CampaignListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.per_page) searchParams.set('per_page', params.per_page.toString());
    if (params?.category) searchParams.set('category', params.category);
    if (params?.search) searchParams.set('search', params.search);
    if (params?.sort) searchParams.set('sort', params.sort);

    const query = searchParams.toString();
    return this.request<CampaignListResponse>(`/api/campaigns${query ? `?${query}` : ''}`);
  }

  async getCampaign(id: string): Promise<Campaign> {
    return this.request<Campaign>(`/api/campaigns/${id}`);
  }

  async getMyCampaigns(params?: {
    page?: number;
    per_page?: number;
  }): Promise<CampaignListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.per_page) searchParams.set('per_page', params.per_page.toString());
    const query = searchParams.toString();
    return this.request<CampaignListResponse>(`/api/creators/me/campaigns${query ? `?${query}` : ''}`);
  }

  async refreshCampaignBalance(id: string): Promise<Campaign> {
    return this.request<Campaign>(`/api/campaigns/${id}/refresh-balance`, {
      method: 'POST',
    });
  }

  async getCampaignDonations(
    campaignId: string,
    page: number = 1,
    perPage: number = 20,
    chain?: string
  ): Promise<{ donations: Donation[]; total: number; page: number; per_page: number }> {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
    });
    if (chain) {
      params.append('chain', chain);
    }
    return this.request(`/api/campaigns/${campaignId}/donations?${params}`);
  }

  async createCampaign(data: CampaignCreateData): Promise<Campaign> {
    return this.request<Campaign>('/api/campaigns', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async uploadCampaignImage(campaignId: string, file: File): Promise<CampaignImage> {
    const formData = new FormData();
    formData.append('image', file);
    return this.request<CampaignImage>(`/api/campaigns/${campaignId}/images`, {
      method: 'POST',
      body: formData,
    });
  }

  async deleteCampaignImage(campaignId: string, imageId: string): Promise<void> {
    return this.request(`/api/campaigns/${campaignId}/images/${imageId}`, {
      method: 'DELETE',
    });
  }

  async deleteCampaign(campaignId: string): Promise<void> {
    return this.request(`/api/campaigns/${campaignId}`, {
      method: 'DELETE',
    });
  }

  async updateCampaign(campaignId: string, data: CampaignUpdateData): Promise<Campaign> {
    return this.request<Campaign>(`/api/campaigns/${campaignId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  // Advocacy endpoints
  async getCampaignEvaluations(campaignId: string): Promise<Evaluation[]> {
    return this.request<Evaluation[]>(`/api/campaigns/${campaignId}/evaluations`);
  }

  async getAdvocates(campaignId: string): Promise<Advocacy[]> {
    return this.request<Advocacy[]>(`/api/campaigns/${campaignId}/advocates`);
  }

  async advocateForCampaign(
    campaignId: string,
    apiKey: string,
    statement?: string
  ): Promise<{ success: boolean; advocacy: Advocacy; karma_earned: number }> {
    return this.request(`/api/campaigns/${campaignId}/advocate`, {
      method: 'POST',
      headers: {
        'X-Agent-API-Key': apiKey,
      },
      body: JSON.stringify({ statement }),
    });
  }

  // War Room endpoints
  async getWarRoomPosts(campaignId: string): Promise<WarRoomPost[]> {
    return this.request<WarRoomPost[]>(`/api/campaigns/${campaignId}/warroom`);
  }

  async createWarRoomPost(
    campaignId: string,
    apiKey: string,
    content: string,
    parentPostId?: string
  ): Promise<WarRoomPost> {
    return this.request(`/api/campaigns/${campaignId}/warroom/posts`, {
      method: 'POST',
      headers: {
        'X-Agent-API-Key': apiKey,
      },
      body: JSON.stringify({ content, parent_post_id: parentPostId }),
    });
  }

  async createWarRoomPostHuman(
    campaignId: string,
    content: string,
    parentPostId?: string
  ): Promise<WarRoomPost> {
    return this.request(`/api/campaigns/${campaignId}/warroom/posts/human`, {
      method: 'POST',
      body: JSON.stringify({ content, parent_post_id: parentPostId }),
    });
  }

  async upvotePost(
    campaignId: string,
    postId: string,
    apiKey: string
  ): Promise<{ success: boolean }> {
    return this.request(`/api/campaigns/${campaignId}/warroom/posts/${postId}/upvote`, {
      method: 'POST',
      headers: {
        'X-Agent-API-Key': apiKey,
      },
    });
  }

  // Agent endpoints
  async registerAgent(data: {
    name: string;
    description?: string;
    avatar_url?: string;
  }): Promise<{ agent: Agent; api_key: string }> {
    return this.request('/api/agents/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getAgent(name: string): Promise<Agent> {
    return this.request<Agent>(`/api/agents/${name}`);
  }

  async getCurrentAgent(): Promise<Agent> {
    return this.request<Agent>('/api/agents/me');
  }

  async updateAgentProfile(data: { description?: string; avatar_url?: string }): Promise<Agent> {
    return this.request<Agent>('/api/agents/me', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async uploadAgentAvatar(file: File): Promise<Agent> {
    const formData = new FormData();
    formData.append('avatar', file);
    return this.request<Agent>('/api/agents/me/avatar', {
      method: 'POST',
      body: formData,
    });
  }

  async getLeaderboard(params?: {
    timeframe?: 'all-time' | 'month' | 'week';
  }): Promise<Agent[]> {
    const searchParams = new URLSearchParams();
    if (params?.timeframe) searchParams.set('timeframe', params.timeframe);
    const query = searchParams.toString();
    return this.request<Agent[]>(`/api/agents/leaderboard${query ? `?${query}` : ''}`);
  }

  // Feed endpoints
  async getFeed(params?: {
    page?: number;
    per_page?: number;
    filter?: 'all' | 'campaigns' | 'advocacy' | 'discussions';
  }): Promise<{ events: FeedEvent[]; total: number; page: number; per_page: number }> {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.per_page) searchParams.set('per_page', params.per_page.toString());
    if (params?.filter) searchParams.set('filter', params.filter);
    const query = searchParams.toString();
    return this.request(`/api/feed${query ? `?${query}` : ''}`);
  }
}

export const api = new ApiClient();
