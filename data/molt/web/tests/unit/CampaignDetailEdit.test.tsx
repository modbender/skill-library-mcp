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

describe('CampaignDetailPage edit button', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.getCampaign.mockResolvedValue(mockCampaign);
    mockApi.getWarRoomPosts.mockResolvedValue([]);
    mockApi.getAdvocates.mockResolvedValue([]);
    mockApi.getCampaignDonations.mockResolvedValue({ donations: [], total: 0 });
    mockApi.refreshCampaignBalance.mockResolvedValue(mockCampaign);
    localStorage.clear();
  });

  it('shows Edit button when user is campaign owner', async () => {
    localStorage.setItem(
      'moltfundme_user',
      JSON.stringify({ id: 'creator-1', email: 'test@example.com' })
    );
    localStorage.setItem('moltfundme_token', 'fake-jwt');

    renderPage();
    await screen.findByText('Test Campaign');

    const editButton = screen.getByRole('link', { name: /Edit/i });
    expect(editButton).toBeInTheDocument();
    expect(editButton).toHaveAttribute('href', '/campaigns/campaign-1/edit');
  });

  it('does NOT show Edit button when user is not campaign owner', async () => {
    localStorage.setItem(
      'moltfundme_user',
      JSON.stringify({ id: 'other-creator', email: 'other@example.com' })
    );
    localStorage.setItem('moltfundme_token', 'fake-jwt');

    renderPage();
    await screen.findByText('Test Campaign');

    expect(screen.queryByRole('link', { name: /Edit/i })).not.toBeInTheDocument();
  });
});
