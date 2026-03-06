import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
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
  status: 'ACTIVE',
  advocate_count: 0,
  cover_image_url: null,
  images: [],
  current_total_usd_cents: 0,
  withdrawal_detected: false,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

const mockAgentPost = {
  id: 'post-1',
  campaign_id: 'campaign-1',
  agent_id: 'agent-1',
  author_type: 'agent' as const,
  author_name: 'TestMolt',
  agent_name: 'TestMolt',
  agent_karma: 10,
  agent_avatar_url: null,
  content: 'Agent says hello',
  upvote_count: 2,
  created_at: '2026-01-01T00:00:00Z',
};

const mockHumanPost = {
  id: 'post-2',
  campaign_id: 'campaign-1',
  creator_id: 'creator-1',
  author_type: 'human' as const,
  author_name: 'jane',
  content: 'Human says thanks!',
  upvote_count: 0,
  created_at: '2026-01-01T01:00:00Z',
};

const mockApi = vi.hoisted(() => ({
  getCampaign: vi.fn(),
  getWarRoomPosts: vi.fn(),
  getAdvocates: vi.fn(),
  getCampaignDonations: vi.fn(),
  refreshCampaignBalance: vi.fn(),
  createWarRoomPostHuman: vi.fn(),
  setTokenGetter: vi.fn(),
  setAgentApiKeyGetter: vi.fn(),
}));

vi.mock('../../src/lib/api', () => ({
  api: mockApi,
}));

function renderWithProviders(isAuthenticated: boolean) {
  if (isAuthenticated) {
    localStorage.setItem('moltfundme_token', 'test-token');
    localStorage.setItem('moltfundme_user', JSON.stringify({ id: 'creator-1', email: 'jane@example.com' }));
  } else {
    localStorage.removeItem('moltfundme_token');
    localStorage.removeItem('moltfundme_user');
  }

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

describe('War Room', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.getCampaign.mockResolvedValue(mockCampaign);
    mockApi.getWarRoomPosts.mockResolvedValue([mockAgentPost, mockHumanPost]);
    mockApi.getAdvocates.mockResolvedValue([]);
    mockApi.getCampaignDonations.mockResolvedValue({ donations: [], total: 0 });
    mockApi.refreshCampaignBalance.mockResolvedValue(mockCampaign);
    localStorage.clear();
  });

  it('renders agent posts with Molt badge', async () => {
    renderWithProviders(false);

    await screen.findByText('Test Campaign');
    const warRoomTab = screen.getByRole('button', { name: /War Room/i });
    fireEvent.click(warRoomTab);

    await screen.findByText('Agent says hello');
    expect(screen.getByText('Molt')).toBeInTheDocument();
  });

  it('renders human posts with Human badge', async () => {
    renderWithProviders(false);

    await screen.findByText('Test Campaign');
    const warRoomTab = screen.getByRole('button', { name: /War Room/i });
    fireEvent.click(warRoomTab);

    await screen.findByText('Human says thanks!');
    const humanBadges = screen.getAllByText('Human');
    expect(humanBadges.length).toBeGreaterThanOrEqual(1);
  });

  it('shows post form when authenticated', async () => {
    renderWithProviders(true);

    await screen.findByText('Test Campaign');
    const warRoomTab = screen.getByRole('button', { name: /War Room/i });
    fireEvent.click(warRoomTab);

    expect(screen.getByTestId('warroom-post-form')).toBeInTheDocument();
  });

  it('shows sign in prompt when not authenticated', async () => {
    renderWithProviders(false);

    await screen.findByText('Test Campaign');
    const warRoomTab = screen.getByRole('button', { name: /War Room/i });
    fireEvent.click(warRoomTab);

    expect(screen.getByTestId('warroom-sign-in-prompt')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /sign in/i })).toHaveAttribute('href', '/auth/login');
  });
});
