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
  id: 'campaign-og-1',
  title: 'Help Save a Life',
  description: 'This is a campaign to raise funds for emergency surgery. Every dollar counts.',
  category: 'MEDICAL',
  goal_amount_usd: 500000,
  status: 'ACTIVE',
  advocate_count: 2,
  cover_image_url: 'https://example.com/cover.jpg',
  images: [{ id: 'img1', image_url: '/api/uploads/campaigns/campaign-og-1/cover.jpg', display_order: 0 }],
  current_total_usd_cents: 50000,
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
              <MemoryRouter initialEntries={['/campaigns/campaign-og-1']}>
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

describe('CampaignDetailPage OG meta tags', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.getCampaign.mockResolvedValue(mockCampaign);
    mockApi.getWarRoomPosts.mockResolvedValue([]);
    mockApi.getAdvocates.mockResolvedValue([]);
    mockApi.getCampaignDonations.mockResolvedValue({ donations: [], total: 0 });
    mockApi.refreshCampaignBalance.mockResolvedValue(mockCampaign);
    document.head.innerHTML = '';
  });

  it('sets og:title to campaign title', async () => {
    renderPage();
    await screen.findByText('Help Save a Life');

    await waitFor(() => {
      const meta = document.querySelector('meta[property="og:title"]');
      expect(meta?.getAttribute('content')).toBe('Help Save a Life');
    });
  });

  it('sets og:description from campaign description (truncated)', async () => {
    renderPage();
    await screen.findByText('Help Save a Life');

    await waitFor(() => {
      const meta = document.querySelector('meta[property="og:description"]');
      expect(meta?.getAttribute('content')).toContain('This is a campaign to raise funds');
      expect(meta?.getAttribute('content')?.length).toBeLessThanOrEqual(200);
    });
  });

  it('sets og:image using cover image or first campaign image', async () => {
    renderPage();
    await screen.findByText('Help Save a Life');

    await waitFor(() => {
      const meta = document.querySelector('meta[property="og:image"]');
      expect(meta?.getAttribute('content')).toBeTruthy();
      expect(meta?.getAttribute('content')).toMatch(/\.(jpg|jpeg|png|webp)/i);
    });
  });

  it('sets Twitter Card meta tags', async () => {
    renderPage();
    await screen.findByText('Help Save a Life');

    await waitFor(() => {
      const card = document.querySelector('meta[name="twitter:card"]');
      const title = document.querySelector('meta[name="twitter:title"]');
      expect(card?.getAttribute('content')).toBe('summary_large_image');
      expect(title?.getAttribute('content')).toBe('Help Save a Life');
    });
  });
});
