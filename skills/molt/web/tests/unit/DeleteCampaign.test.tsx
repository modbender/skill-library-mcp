import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider } from '../../src/contexts/AuthContext';
import { AgentAuthProvider } from '../../src/contexts/AgentAuthContext';
import { ToastProvider } from '../../src/contexts/ToastContext';
import CampaignDetailPage from '../../src/pages/CampaignDetailPage';

const mockDeleteCampaign = vi.fn();
const mockGetCampaign = vi.fn();

const mockApi = vi.hoisted(() => ({
  getCampaign: vi.fn(),
  getWarRoomPosts: vi.fn(),
  getAdvocates: vi.fn(),
  getCampaignDonations: vi.fn(),
  refreshCampaignBalance: vi.fn(),
  deleteCampaign: vi.fn(),
  setTokenGetter: vi.fn(),
  setAgentApiKeyGetter: vi.fn(),
}));

vi.mock('../../src/lib/api', () => ({
  api: mockApi,
}));

const mockCampaignOwner = {
  id: 'campaign-1',
  title: 'Test Campaign',
  description: 'Test description',
  category: 'MEDICAL',
  goal_amount_usd: 500000,
  status: 'ACTIVE' as const,
  advocate_count: 0,
  creator_id: 'creator-1',
  cover_image_url: undefined,
  images: [],
  current_total_usd_cents: 0,
  withdrawal_detected: false,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

const mockCampaignNonOwner = {
  ...mockCampaignOwner,
  creator_id: 'creator-other',
};

function renderPage(campaignId: string, isOwner: boolean) {
  const campaign = isOwner ? mockCampaignOwner : mockCampaignNonOwner;
  mockApi.getCampaign.mockResolvedValue(campaign);

  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  if (isOwner) {
    localStorage.setItem(
      'moltfundme_user',
      JSON.stringify({ id: 'creator-1', email: 'owner@example.com' })
    );
    localStorage.setItem('moltfundme_token', 'fake-jwt');
  } else {
    localStorage.setItem(
      'moltfundme_user',
      JSON.stringify({ id: 'creator-2', email: 'visitor@example.com' })
    );
    localStorage.setItem('moltfundme_token', 'fake-jwt');
  }

  return render(
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <AgentAuthProvider>
            <ToastProvider>
              <MemoryRouter initialEntries={[`/campaigns/${campaignId}`]}>
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

describe('CampaignDetailPage delete campaign', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.getWarRoomPosts.mockResolvedValue([]);
    mockApi.getAdvocates.mockResolvedValue([]);
    mockApi.getCampaignDonations.mockResolvedValue({ donations: [], total: 0 });
    mockApi.refreshCampaignBalance.mockResolvedValue(mockCampaignOwner);
    mockApi.deleteCampaign.mockResolvedValue(undefined);
  });

  it('shows Delete Campaign button only when user is the campaign owner', async () => {
    renderPage('campaign-1', true);
    await screen.findByText('Test Campaign');

    const deleteButton = screen.queryByRole('button', { name: /Delete Campaign/i });
    expect(deleteButton).toBeInTheDocument();
  });

  it('does not show Delete Campaign button when user is not the owner', async () => {
    renderPage('campaign-1', false);
    await screen.findByText('Test Campaign');

    const deleteButton = screen.queryByRole('button', { name: /Delete Campaign/i });
    expect(deleteButton).not.toBeInTheDocument();
  });

  it('shows confirmation dialog when Delete is clicked and calls API on confirm', async () => {
    const user = userEvent.setup();
    renderPage('campaign-1', true);
    await screen.findByText('Test Campaign');

    const deleteButton = screen.getByRole('button', { name: /Delete Campaign/i });
    await user.click(deleteButton);

    // Confirmation dialog should appear
    const confirmButton = await screen.findByRole('button', { name: /Confirm Delete/i });
    expect(confirmButton).toBeInTheDocument();

    await user.click(confirmButton);

    await waitFor(() => {
      expect(mockApi.deleteCampaign).toHaveBeenCalledWith('campaign-1');
    });
  });
});
