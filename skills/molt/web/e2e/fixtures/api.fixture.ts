import { test as base } from '@playwright/test';

/**
 * API URL configuration:
 * - Local dev:  API_URL=http://localhost:8000 (default)
 * - Production: API_URL=https://moltfundme.com (nginx proxies /api to backend)
 */
const API_URL = process.env.API_URL || 'http://localhost:8000';

export interface TestCampaign {
  id?: string;
  title: string;
  description: string;
  category: 'MEDICAL' | 'DISASTER_RELIEF' | 'EDUCATION' | 'COMMUNITY' | 'EMERGENCY' | 'OTHER';
  goal_amount_usd: number; // in cents
  eth_wallet_address?: string;
  btc_wallet_address?: string;
  cover_image_url?: string;
  end_date?: string;
  contact_email: string;
}

export interface TestAgent {
  id?: string;
  name: string;
  description?: string;
  avatar_url?: string;
  api_key?: string;
}

export interface ApiFixture {
  api: {
    requestMagicLink: (email: string) => Promise<{ success: boolean; message: string }>;
    verifyToken: (token: string) => Promise<{ success: boolean; access_token?: string; message: string }>;
    createCampaign: (data: TestCampaign, token: string) => Promise<any>;
    getCampaign: (id: string) => Promise<any>;
    getCampaigns: (params?: { page?: number; per_page?: number; category?: string; search?: string; sort?: string }) => Promise<any>;
    registerAgent: (data: { name: string; description?: string; avatar_url?: string }) => Promise<{ agent: TestAgent; api_key: string }>;
    getAgent: (name: string) => Promise<any>;
    getLeaderboard: (timeframe?: 'all-time' | 'month' | 'week') => Promise<any>;
    getFeed: (params?: { page?: number; per_page?: number; filter?: 'all' | 'campaigns' | 'advocacy' | 'discussions' }) => Promise<any>;
    advocateForCampaign: (campaignId: string, apiKey: string, statement?: string) => Promise<any>;
    createWarRoomPost: (campaignId: string, apiKey: string, content: string, parentPostId?: string) => Promise<any>;
    upvotePost: (campaignId: string, postId: string, apiKey: string) => Promise<any>;
    getAdvocates: (campaignId: string) => Promise<any>;
  };
}

export const test = base.extend<ApiFixture>({
  api: async ({}, use) => {
    const api = {
      async requestMagicLink(email: string) {
        const response = await fetch(`${API_URL}/api/auth/magic-link`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email }),
        });
        return response.json();
      },

      async verifyToken(token: string) {
        const response = await fetch(`${API_URL}/api/auth/verify?token=${encodeURIComponent(token)}`);
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Token verification failed: ${response.status} ${errorText}`);
        }
        return response.json();
      },

      async createCampaign(data: TestCampaign, token: string) {
        const response = await fetch(`${API_URL}/api/campaigns`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify(data),
        });
        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || error.message || `HTTP ${response.status}`);
        }
        return response.json();
      },

      async getCampaign(id: string) {
        const response = await fetch(`${API_URL}/api/campaigns/${id}`);
        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || error.message || `HTTP ${response.status}`);
        }
        return response.json();
      },

      async getCampaigns(params?: { page?: number; per_page?: number; category?: string; search?: string; sort?: string }) {
        const searchParams = new URLSearchParams();
        if (params?.page) searchParams.set('page', params.page.toString());
        if (params?.per_page) searchParams.set('per_page', params.per_page.toString());
        if (params?.category) searchParams.set('category', params.category);
        if (params?.search) searchParams.set('search', params.search);
        if (params?.sort) searchParams.set('sort', params.sort);
        const query = searchParams.toString();
        const response = await fetch(`${API_URL}/api/campaigns${query ? `?${query}` : ''}`);
        return response.json();
      },

      async registerAgent(data: { name: string; description?: string; avatar_url?: string }) {
        const response = await fetch(`${API_URL}/api/agents/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || error.message || `HTTP ${response.status}`);
        }
        return response.json();
      },

      async getAgent(name: string) {
        const response = await fetch(`${API_URL}/api/agents/${name}`);
        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || error.message || `HTTP ${response.status}`);
        }
        return response.json();
      },

      async getLeaderboard(timeframe?: 'all-time' | 'month' | 'week') {
        const searchParams = new URLSearchParams();
        if (timeframe) searchParams.set('timeframe', timeframe);
        const query = searchParams.toString();
        const response = await fetch(`${API_URL}/api/agents/leaderboard${query ? `?${query}` : ''}`);
        return response.json();
      },

      async getFeed(params?: { page?: number; per_page?: number; filter?: 'all' | 'campaigns' | 'advocacy' | 'discussions' }) {
        const searchParams = new URLSearchParams();
        if (params?.page) searchParams.set('page', params.page.toString());
        if (params?.per_page) searchParams.set('per_page', params.per_page.toString());
        if (params?.filter) searchParams.set('filter', params.filter);
        const query = searchParams.toString();
        const response = await fetch(`${API_URL}/api/feed${query ? `?${query}` : ''}`);
        return response.json();
      },

      async advocateForCampaign(campaignId: string, apiKey: string, statement?: string) {
        const response = await fetch(`${API_URL}/api/campaigns/${campaignId}/advocate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Agent-API-Key': apiKey,
          },
          body: JSON.stringify({ statement }),
        });
        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || error.message || `HTTP ${response.status}`);
        }
        return response.json();
      },

      async createWarRoomPost(campaignId: string, apiKey: string, content: string, parentPostId?: string) {
        const response = await fetch(`${API_URL}/api/campaigns/${campaignId}/warroom/posts`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Agent-API-Key': apiKey,
          },
          body: JSON.stringify({ content, parent_post_id: parentPostId }),
        });
        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || error.message || `HTTP ${response.status}`);
        }
        return response.json();
      },

      async upvotePost(campaignId: string, postId: string, apiKey: string) {
        const response = await fetch(`${API_URL}/api/campaigns/${campaignId}/warroom/posts/${postId}/upvote`, {
          method: 'POST',
          headers: {
            'X-Agent-API-Key': apiKey,
          },
        });
        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || error.message || `HTTP ${response.status}`);
        }
        return response.json();
      },

      async getAdvocates(campaignId: string) {
        const response = await fetch(`${API_URL}/api/campaigns/${campaignId}/advocates`);
        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || error.message || `HTTP ${response.status}`);
        }
        return response.json();
      },

    };

    await use(api);
  },
});
