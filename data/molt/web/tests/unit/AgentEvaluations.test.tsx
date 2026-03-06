import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider } from '../../src/contexts/AuthContext';
import { AgentAuthProvider } from '../../src/contexts/AgentAuthContext';
import { ToastProvider } from '../../src/contexts/ToastContext';
import CampaignDetailPage from '../../src/pages/CampaignDetailPage';

const mockCampaign = {
  id: 'campaign-1',
  title: 'Test Campaign',
  description: 'Test description',
  category: 'MEDICAL',
  goal_amount_usd: 100000,
  creator_id: 'creator-1',
  status: 'ACTIVE',
  advocate_count: 0,
  cover_image_url: null,
  images: [],
  current_total_usd_cents: 0,
  withdrawal_detected: false,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

const mockApi = vi.hoisted(() => ({
  getCampaign: vi.fn(),
  getWarRoomPosts: vi.fn(),
  getAdvocates: vi.fn(),
  getCampaignDonations: vi.fn(),
  getCampaignEvaluations: vi.fn(),
  refreshCampaignBalance: vi.fn(),
  setTokenGetter: vi.fn(),
  setAgentApiKeyGetter: vi.fn(),
}));

vi.mock('../../src/lib/api', () => ({
  api: mockApi,
}));

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <AgentAuthProvider>
            <ToastProvider>
              <MemoryRouter initialEntries={['/campaigns/campaign-1']}>
                <Routes>
                  <Route path="/campaigns/:id" element={<CampaignDetailPage />} />
                </Routes>
              </MemoryRouter>
            </ToastProvider>
          </AgentAuthProvider>
        </AuthProvider>
      </QueryClientProvider>
    </HelmetProvider>
  );
}

describe('Agent evaluations display', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.getCampaign.mockResolvedValue(mockCampaign);
    mockApi.getWarRoomPosts.mockResolvedValue([]);
    mockApi.getAdvocates.mockResolvedValue([]);
    mockApi.getCampaignDonations.mockResolvedValue({ donations: [], total: 0 });
    mockApi.refreshCampaignBalance.mockResolvedValue(mockCampaign);
    mockApi.getCampaignEvaluations.mockResolvedValue([]);
  });

  it('displays evaluations section when evaluations exist', async () => {
    mockApi.getCampaignEvaluations.mockResolvedValue([
      {
        id: 'eval-1',
        campaign_id: 'campaign-1',
        agent_id: 'agent-1',
        agent_name: 'TestAgent',
        score: 8,
        summary: 'Strong campaign.',
        categories: { impact: 9, transparency: 7 },
        created_at: '2026-01-15T00:00:00Z',
      },
    ]);

    renderPage();
    await screen.findByText('Test Campaign');

    await waitFor(() => {
      expect(screen.getByText('Agent Evaluations')).toBeInTheDocument();
    });
    expect(screen.getByText('Average: 8.0/10')).toBeInTheDocument();
    expect(screen.getByText('TestAgent')).toBeInTheDocument();
    expect(screen.getByText('Strong campaign.')).toBeInTheDocument();
  });

  it('displays average score', async () => {
    mockApi.getCampaignEvaluations.mockResolvedValue([
      { id: '1', agent_name: 'Agent1', score: 8, summary: 'Good', categories: {}, created_at: '2026-01-01Z' },
      { id: '2', agent_name: 'Agent2', score: 6, summary: 'OK', categories: {}, created_at: '2026-01-01Z' },
    ]);

    renderPage();
    await screen.findByText('Test Campaign');

    await waitFor(() => {
      expect(screen.getByText('Average: 7.0/10')).toBeInTheDocument();
    });
  });

  it('shows empty state when no evaluations', async () => {
    mockApi.getCampaignEvaluations.mockResolvedValue([]);

    renderPage();
    await screen.findByText('Test Campaign');

    await waitFor(() => {
      expect(mockApi.getCampaignEvaluations).toHaveBeenCalledWith('campaign-1');
    });
    expect(screen.queryByText('TestAgent')).not.toBeInTheDocument();
  });
});
