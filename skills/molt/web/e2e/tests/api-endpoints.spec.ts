/**
 * Production API Endpoint Tests
 *
 * Tests all MoltFundMe API endpoints directly (no browser).
 * Run against production: BASE_URL=https://moltfundme.com API_URL=https://moltfundme.com bun run test:e2e -- tests/api-endpoints.spec.ts
 * Run against local:      bun run test:e2e -- tests/api-endpoints.spec.ts
 */
import { test, expect } from '../fixtures';

const API_URL = process.env.API_URL || 'http://localhost:8000';

test.describe('API Endpoints - Health & Root', () => {
  test('GET /api/campaigns should be reachable (API health proxy)', async ({}) => {
    const response = await fetch(`${API_URL}/api/campaigns?per_page=1`);
    expect(response.ok).toBe(true);
    const data = await response.json();
    expect(data).toHaveProperty('campaigns');
    expect(data).toHaveProperty('total');
  });
});

test.describe('API Endpoints - Campaigns', () => {
  test('GET /api/campaigns returns campaign list', async ({ api }) => {
    const data = await api.getCampaigns({ per_page: 5 });
    expect(data).toHaveProperty('campaigns');
    expect(data).toHaveProperty('total');
    expect(data).toHaveProperty('page');
    expect(data).toHaveProperty('per_page');
    expect(Array.isArray(data.campaigns)).toBe(true);
  });

  test('GET /api/campaigns supports pagination', async ({ api }) => {
    const page1 = await api.getCampaigns({ page: 1, per_page: 2 });
    expect(page1.page).toBe(1);
    expect(page1.per_page).toBe(2);
    expect(page1.campaigns.length).toBeLessThanOrEqual(2);

    if (page1.total > 2) {
      const page2 = await api.getCampaigns({ page: 2, per_page: 2 });
      expect(page2.page).toBe(2);
    }
  });

  test('GET /api/campaigns supports search', async ({ api }) => {
    // Get campaigns - should have at least one from beforeAll setup
    const all = await api.getCampaigns({ per_page: 1 });
    expect(all.campaigns.length).toBeGreaterThan(0);

    const term = all.campaigns[0].title.split(' ')[0]; // First word of first campaign
    const results = await api.getCampaigns({ search: term });
    expect(results.campaigns.length).toBeGreaterThan(0);
    // Verify search relevance
    const found = results.campaigns.some((c: any) =>
      c.title.toLowerCase().includes(term.toLowerCase()) ||
      c.description?.toLowerCase().includes(term.toLowerCase())
    );
    expect(found).toBe(true);
  });

  test('GET /api/campaigns supports category filter', async ({ api }) => {
    const categories = ['MEDICAL', 'DISASTER_RELIEF', 'EDUCATION', 'COMMUNITY', 'EMERGENCY', 'OTHER'];
    for (const category of categories) {
      const results = await api.getCampaigns({ category, per_page: 3 });
      expect(Array.isArray(results.campaigns)).toBe(true);
      // If results exist, they should all match the category
      for (const campaign of results.campaigns) {
        expect(campaign.category).toBe(category);
      }
    }
  });

  test('GET /api/campaigns supports sort options', async ({ api }) => {
    const sortOptions = ['newest', 'most_advocates', 'trending'];
    for (const sort of sortOptions) {
      const results = await api.getCampaigns({ sort, per_page: 3 });
      expect(Array.isArray(results.campaigns)).toBe(true);
    }
  });

  test('GET /api/campaigns rejects invalid sort option', async ({}) => {
    const response = await fetch(`${API_URL}/api/campaigns?sort=invalid_sort`);
    expect(response.status).toBe(422);
  });

  test('GET /api/campaigns/:id returns campaign detail', async ({ api }) => {
    const all = await api.getCampaigns({ per_page: 1 });
    expect(all.campaigns.length).toBeGreaterThan(0);

    const campaign = await api.getCampaign(all.campaigns[0].id);
    expect(campaign).toHaveProperty('id');
    expect(campaign).toHaveProperty('title');
    expect(campaign).toHaveProperty('description');
    expect(campaign).toHaveProperty('category');
    expect(campaign).toHaveProperty('goal_amount_usd');
    expect(campaign).toHaveProperty('created_at');
  });

  test('GET /api/campaigns/:id returns 404 for non-existent campaign', async ({}) => {
    const response = await fetch(`${API_URL}/api/campaigns/non-existent-id-12345`);
    expect(response.status).toBe(404);
  });
});

test.describe('API Endpoints - Agents', () => {
  test('GET /api/agents/leaderboard returns agent list', async ({ api }) => {
    const data = await api.getLeaderboard('all-time');
    expect(Array.isArray(data)).toBe(true);
  });

  test('GET /api/agents/leaderboard supports timeframe filter', async ({ api }) => {
    const allTime = await api.getLeaderboard('all-time');
    const month = await api.getLeaderboard('month');
    const week = await api.getLeaderboard('week');

    expect(Array.isArray(allTime)).toBe(true);
    expect(Array.isArray(month)).toBe(true);
    expect(Array.isArray(week)).toBe(true);
  });

  test('POST /api/agents/register creates a new agent', async ({ api }) => {
    const agentName = `api-test-agent-${Date.now()}`;
    const result = await api.registerAgent({
      name: agentName,
      description: 'Created by API endpoint test',
    });

    expect(result).toHaveProperty('agent');
    expect(result).toHaveProperty('api_key');
    expect(result.agent.name).toBe(agentName);
    expect(result.api_key).toBeTruthy();
  });

  test('POST /api/agents/register rejects duplicate names', async ({ api }) => {
    const agentName = `dup-test-${Date.now()}`;

    // First registration should succeed
    await api.registerAgent({ name: agentName });

    // Second should fail
    await expect(
      api.registerAgent({ name: agentName })
    ).rejects.toThrow();
  });

  test('GET /api/agents/:name returns agent profile', async ({ api }) => {
    const agentName = `profile-test-${Date.now()}`;
    await api.registerAgent({ name: agentName, description: 'Profile test agent' });

    const agent = await api.getAgent(agentName);
    expect(agent.name).toBe(agentName);
    expect(agent.description).toBe('Profile test agent');
    expect(agent).toHaveProperty('karma');
    expect(agent).toHaveProperty('created_at');
  });
});

test.describe('API Endpoints - Feed', () => {
  test('GET /api/feed returns activity events', async ({ api }) => {
    const data = await api.getFeed({ per_page: 10 });
    expect(data).toHaveProperty('events');
    expect(data).toHaveProperty('total');
    expect(Array.isArray(data.events)).toBe(true);
  });

  test('GET /api/feed supports filtering', async ({ api }) => {
    const filters = ['all', 'campaigns', 'advocacy', 'discussions'] as const;
    for (const filter of filters) {
      const data = await api.getFeed({ filter, per_page: 5 });
      expect(Array.isArray(data.events)).toBe(true);
    }
  });

  test('GET /api/feed supports pagination', async ({ api }) => {
    const page1 = await api.getFeed({ page: 1, per_page: 3 });
    expect(page1).toHaveProperty('page');
    expect(Array.isArray(page1.events)).toBe(true);
  });
});

test.describe('API Endpoints - Advocacy & War Room', () => {
  let campaignId: string;
  let agentApiKey: string;
  let agentName: string;
  let creatorToken: string;

  test.beforeAll(async () => {
    // Check if campaigns exist, if not create one
    const response = await fetch(`${API_URL}/api/campaigns?per_page=1`);
    const data = await response.json();
    
    if (data.campaigns.length > 0) {
      campaignId = data.campaigns[0].id;
    } else {
      // Create a test campaign via API
      // First, get a creator token
      const email = `api-setup-${Date.now()}@example.com`;
      const magicLinkResponse = await fetch(`${API_URL}/api/auth/magic-link`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const magicLinkData = await magicLinkResponse.json();
      
      // Extract token from dev mode message
      const tokenMatch = magicLinkData.message?.match(/Token: ([^\s]+)/);
      if (tokenMatch) {
        const token = tokenMatch[1];
        const verifyResponse = await fetch(`${API_URL}/api/auth/verify?token=${encodeURIComponent(token)}`);
        const verifyData = await verifyResponse.json();
        creatorToken = verifyData.access_token;
        
        // Create campaign
        const campaignResponse = await fetch(`${API_URL}/api/campaigns`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${creatorToken}`,
          },
          body: JSON.stringify({
            title: `API Test Campaign ${Date.now()}`,
            description: 'Campaign created by API endpoint tests for advocacy and war room testing',
            category: 'COMMUNITY',
            goal_amount_usd: 10000,
            eth_wallet_address: '0x0000000000000000000000000000000000000000', // Dummy address for API tests
            btc_wallet_address: 'bc1q0000000000000000000000000000000000000000000000',
            contact_email: email,
          }),
        });
        
        if (campaignResponse.ok) {
          const campaignData = await campaignResponse.json();
          campaignId = campaignData.id;
        } else {
          // If campaign creation fails (e.g., KYC required), try to use an existing campaign
          // or wait a moment and retry getting campaigns
          await new Promise(resolve => setTimeout(resolve, 2000));
          const retryResponse = await fetch(`${API_URL}/api/campaigns?per_page=1`);
          const retryData = await retryResponse.json();
          if (retryData.campaigns.length > 0) {
            campaignId = retryData.campaigns[0].id;
          }
        }
      }
    }

    // Register a test agent
    agentName = `warroom-test-${Date.now()}`;
    const agentResponse = await fetch(`${API_URL}/api/agents/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: agentName, description: 'War room test agent' }),
    });
    const agentData = await agentResponse.json();
    agentApiKey = agentData.api_key;
  });

  test('POST /api/campaigns/:id/advocate creates advocacy', async ({ api }) => {
    expect(campaignId).toBeTruthy();
    expect(agentApiKey).toBeTruthy();

    const result = await api.advocateForCampaign(
      campaignId!,
      agentApiKey!,
      'This campaign deserves support - verified by API test'
    );
    expect(result).toHaveProperty('success');
    expect(result.success).toBe(true);
    expect(result).toHaveProperty('karma_earned');
    expect(result.karma_earned).toBeGreaterThan(0);
  });

  test('GET /api/campaigns/:id/advocates lists advocates', async ({ api }) => {
    expect(campaignId).toBeTruthy();

    const advocates = await api.getAdvocates(campaignId!);
    expect(Array.isArray(advocates)).toBe(true);
  });

  test('POST /api/campaigns/:id/warroom/posts creates a post', async ({ api }) => {
    expect(campaignId).toBeTruthy();
    expect(agentApiKey).toBeTruthy();

    const post = await api.createWarRoomPost(
      campaignId!,
      agentApiKey!,
      'Automated API test post - verifying war room functionality'
    );
    expect(post).toHaveProperty('id');
    expect(post).toHaveProperty('content');
    expect(post.content).toContain('Automated API test post');
  });

  test('POST /api/campaigns/:id/warroom/posts supports replies', async ({ api }) => {
    expect(campaignId).toBeTruthy();
    expect(agentApiKey).toBeTruthy();

    // Create parent post
    const parent = await api.createWarRoomPost(
      campaignId!,
      agentApiKey!,
      'Parent post for reply test'
    );

    // Register a second agent for the reply
    const replyAgentName = `reply-test-${Date.now()}`;
    const regResult = await api.registerAgent({ name: replyAgentName });

    // Create reply
    const reply = await api.createWarRoomPost(
      campaignId!,
      regResult.api_key,
      'This is a reply to the parent post',
      parent.id
    );
    expect(reply).toHaveProperty('id');
    expect(reply).toHaveProperty('content');
  });

  test('POST /api/campaigns/:id/warroom/posts/:id/upvote works', async ({ api }) => {
    expect(campaignId).toBeTruthy();
    expect(agentApiKey).toBeTruthy();

    // Create a post first
    const post = await api.createWarRoomPost(
      campaignId!,
      agentApiKey!,
      'Post to upvote'
    );

    // Register a different agent to upvote (can't upvote own post)
    const voterName = `voter-${Date.now()}`;
    const voterResult = await api.registerAgent({ name: voterName });

    const upvote = await api.upvotePost(campaignId!, post.id, voterResult.api_key);
    expect(upvote).toHaveProperty('success');
    expect(upvote.success).toBe(true);
  });

  test('advocacy without API key returns 401/403', async ({}) => {
    expect(campaignId).toBeTruthy();

    const response = await fetch(`${API_URL}/api/campaigns/${campaignId}/advocate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ statement: 'No auth test' }),
    });
    // Should fail without API key
    expect([401, 403, 422]).toContain(response.status);
  });
});

test.describe('API Endpoints - Auth', () => {
  test('POST /api/auth/magic-link accepts email', async ({ api }) => {
    const email = `api-test-${Date.now()}@example.com`;
    const result = await api.requestMagicLink(email);
    expect(result).toHaveProperty('success');
    expect(result.success).toBe(true);
    expect(result).toHaveProperty('message');
  });

  test('GET /api/auth/verify rejects invalid token', async ({}) => {
    const response = await fetch(`${API_URL}/api/auth/verify?token=completely-invalid-token`);
    expect(response.ok).toBe(false);
  });
});
