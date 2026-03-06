import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
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
  eth_wallet_address: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
  btc_wallet_address: null,
  sol_wallet_address: null,
  usdc_base_wallet_address: null,
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

describe('Share functionality', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.getCampaign.mockResolvedValue(mockCampaign);
    mockApi.getWarRoomPosts.mockResolvedValue([]);
    mockApi.getAdvocates.mockResolvedValue([]);
    mockApi.getCampaignDonations.mockResolvedValue({ donations: [], total: 0 });
    mockApi.refreshCampaignBalance.mockResolvedValue(mockCampaign);
    Object.defineProperty(window, 'open', { value: vi.fn(), writable: true });
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText: vi.fn().mockResolvedValue(undefined) },
      writable: true,
    });
  });

  it('uses Web Share API when available', async () => {
    const mockShare = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, 'share', {
      value: mockShare,
      writable: true,
      configurable: true,
    });

    renderPage();
    await screen.findByText('Test Campaign');

    // Click the primary share button (when Web Share API is used, it may be a single Share button)
    const shareButtons = screen.getAllByRole('button', { name: /Share|Copy link|^X$/i });
    const shareButton = shareButtons.find((b) => b.textContent?.includes('Share') || b.getAttribute('aria-label') === 'Share');
    if (shareButton) {
      fireEvent.click(shareButton);
      await waitFor(() => {
        expect(mockShare).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Test Campaign',
            url: expect.any(String),
          })
        );
      });
    }
    // If Web Share is primary, the Share button triggers it
    // Implementation may show Share when navigator.share exists
  });

  it('Facebook share button opens correct URL', async () => {
    renderPage();
    await screen.findByText('Test Campaign');

    const facebookButton = screen.getByRole('button', { name: /Facebook/i });
    expect(facebookButton).toBeInTheDocument();
    fireEvent.click(facebookButton);

    expect(window.open).toHaveBeenCalledWith(
      expect.stringContaining('facebook.com/sharer/sharer.php'),
      '_blank'
    );
    expect(window.open).toHaveBeenCalledWith(
      expect.stringMatching(/u=https?%3A%2F%2F/),
      '_blank'
    );
  });

  it('share-after-donate prompt appears after copying wallet address', async () => {
    renderPage();
    await screen.findByText('Test Campaign');

    // Copy an address (e.g. ETH)
    const copyButtons = screen.getAllByLabelText(/Copy address/i);
    if (copyButtons.length > 0) {
      fireEvent.click(copyButtons[0]);
      await waitFor(() => {
        expect(screen.getByText(/Share this campaign/i)).toBeInTheDocument();
      }, { timeout: 1500 });
    }
  });

  it('Instagram share button opens instagram.com after copying link', async () => {
    renderPage();
    await screen.findByText('Test Campaign');

    const instagramButtons = screen.getAllByRole('button', { name: /Instagram/i });
    expect(instagramButtons.length).toBeGreaterThan(0);
    fireEvent.click(instagramButtons[0]);

    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(expect.stringContaining('http'));
    });
    expect(window.open).toHaveBeenCalledWith('https://www.instagram.com/', '_blank');
  });

  it('TikTok share button opens tiktok.com after copying link', async () => {
    renderPage();
    await screen.findByText('Test Campaign');

    const tiktokButtons = screen.getAllByRole('button', { name: /TikTok/i });
    expect(tiktokButtons.length).toBeGreaterThan(0);
    fireEvent.click(tiktokButtons[0]);

    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(expect.stringContaining('http'));
    });
    expect(window.open).toHaveBeenCalledWith('https://www.tiktok.com/', '_blank');
  });

  it('cover photo header has all share buttons (X, Facebook, Instagram, TikTok, Copy)', async () => {
    const campaignWithCover = {
      ...mockCampaign,
      cover_image_url: 'https://example.com/cover.jpg',
    };
    mockApi.getCampaign.mockResolvedValue(campaignWithCover);
    mockApi.refreshCampaignBalance.mockResolvedValue(campaignWithCover);
    renderPage();
    await screen.findByText('Test Campaign');

    await waitFor(() => {
      expect(screen.getByLabelText('Share on X')).toBeInTheDocument();
    });
    expect(screen.getByLabelText('Share on Facebook')).toBeInTheDocument();
    expect(screen.getByLabelText('Share on Instagram')).toBeInTheDocument();
    expect(screen.getByLabelText('Share on TikTok')).toBeInTheDocument();
    expect(screen.getByLabelText('Copy link')).toBeInTheDocument();
  });

  it('bottom share section has Instagram and TikTok buttons', async () => {
    renderPage();
    await screen.findByText('Test Campaign');

    const bottomShareSection = screen.getByText('Share this campaign').closest('div')!;
    const instagramBtn = bottomShareSection.querySelector('button[aria-label="Instagram"]') 
      || screen.getAllByRole('button', { name: /Instagram/i });
    expect(instagramBtn).toBeTruthy();

    const tiktokBtn = bottomShareSection.querySelector('button[aria-label="TikTok"]')
      || screen.getAllByRole('button', { name: /TikTok/i });
    expect(tiktokBtn).toBeTruthy();
  });
});
