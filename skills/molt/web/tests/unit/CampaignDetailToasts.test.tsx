import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider } from '../../src/contexts/AuthContext';
import { AgentAuthProvider } from '../../src/contexts/AgentAuthContext';
import { ToastProvider } from '../../src/contexts/ToastContext';
import ToastContainer from '../../src/components/ui/Toast';
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
  current_total_usd_cents: 5000,
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
  createWarRoomPostHuman: vi.fn(),
  setTokenGetter: vi.fn(),
  setAgentApiKeyGetter: vi.fn(),
}));

vi.mock('../../src/lib/api', () => ({
  api: mockApi,
}));

function renderPage() {
  localStorage.removeItem('moltfundme_token');
  localStorage.removeItem('moltfundme_user');

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
              <ToastContainer />
            </ToastProvider>
          </AgentAuthProvider>
        </AuthProvider>
      </QueryClientProvider>
    </HelmetProvider>
  );
}

describe('CampaignDetailPage toast behavior', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.getCampaign.mockResolvedValue(mockCampaign);
    mockApi.getWarRoomPosts.mockResolvedValue([]);
    mockApi.getAdvocates.mockResolvedValue([]);
    mockApi.getCampaignDonations.mockResolvedValue({ donations: [], total: 0 });
    localStorage.clear();
  });

  it('does NOT show error toast when auto-refresh balance fails', async () => {
    mockApi.refreshCampaignBalance.mockRejectedValue(
      new Error('Failed to refresh balance: Binance API unavailable')
    );

    renderPage();
    await screen.findByText('Test Campaign');

    // Wait for auto-refresh mutation to fire and fail
    await waitFor(() => {
      expect(mockApi.refreshCampaignBalance).toHaveBeenCalled();
    });

    // The error message should NOT appear as a toast
    expect(screen.queryByText(/Binance API unavailable/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Failed to refresh balance/i)).not.toBeInTheDocument();
  });

  it('does NOT show success toast on auto-refresh', async () => {
    mockApi.refreshCampaignBalance.mockResolvedValue(mockCampaign);

    renderPage();
    await screen.findByText('Test Campaign');

    await waitFor(() => {
      expect(mockApi.refreshCampaignBalance).toHaveBeenCalled();
    });

    // "Balance refreshed successfully" should NOT appear from auto-refresh
    expect(screen.queryByText('Balance refreshed successfully')).not.toBeInTheDocument();
  });

  it('shows success toast when user manually clicks Refresh', async () => {
    mockApi.refreshCampaignBalance.mockResolvedValue(mockCampaign);

    renderPage();
    await screen.findByText('Test Campaign');

    // Wait for auto-refresh to complete first
    await waitFor(() => {
      expect(mockApi.refreshCampaignBalance).toHaveBeenCalledTimes(1);
    });

    // Now manually click Refresh
    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(mockApi.refreshCampaignBalance).toHaveBeenCalledTimes(2);
    });

    // Manual refresh SHOULD show success toast
    await waitFor(() => {
      expect(screen.getByText('Balance refreshed successfully')).toBeInTheDocument();
    });
  });

  it('shows error toast when user manually clicks Refresh and it fails', async () => {
    // First call (auto-refresh) succeeds, second (manual) fails
    mockApi.refreshCampaignBalance
      .mockResolvedValueOnce(mockCampaign)
      .mockRejectedValueOnce(new Error('Failed to refresh balance'));

    renderPage();
    await screen.findByText('Test Campaign');

    await waitFor(() => {
      expect(mockApi.refreshCampaignBalance).toHaveBeenCalledTimes(1);
    });

    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(screen.getByText('Failed to refresh balance')).toBeInTheDocument();
    });
  });

  it('still shows withdrawal toast even on auto-refresh', async () => {
    mockApi.refreshCampaignBalance.mockResolvedValue({
      ...mockCampaign,
      withdrawal_detected: true,
      status: 'CANCELLED',
    });

    renderPage();
    await screen.findByText('Test Campaign');

    await waitFor(() => {
      expect(screen.getByText('Withdrawal detected. Campaign has been cancelled.')).toBeInTheDocument();
    });
  });
});
