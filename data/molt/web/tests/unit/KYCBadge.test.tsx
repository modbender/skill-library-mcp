import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider } from '../../src/contexts/AuthContext';
import { AgentAuthProvider } from '../../src/contexts/AgentAuthContext';
import { ToastProvider } from '../../src/contexts/ToastContext';
import CampaignDetailPage from '../../src/pages/CampaignDetailPage';

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

function renderPage(campaign: Record<string, unknown>) {
  mockApi.getCampaign.mockResolvedValue(campaign);
  mockApi.getWarRoomPosts.mockResolvedValue([]);
  mockApi.getAdvocates.mockResolvedValue([]);
  mockApi.getCampaignDonations.mockResolvedValue({ donations: [], total: 0 });
  mockApi.refreshCampaignBalance.mockResolvedValue(campaign);

  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
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

describe('CampaignDetailPage KYC badge', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders Verified Creator badge when is_creator_verified is true', async () => {
    renderPage({
      id: 'campaign-1',
      title: 'Test Campaign',
      description: 'Test',
      category: 'MEDICAL',
      goal_amount_usd: 100000,
      status: 'ACTIVE',
      advocate_count: 0,
      is_creator_verified: true,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    });

    await screen.findByText('Test Campaign');
    expect(screen.getByText('Verified Creator')).toBeInTheDocument();
  });

  it('does NOT render Verified Creator badge when is_creator_verified is false', async () => {
    renderPage({
      id: 'campaign-1',
      title: 'Test Campaign',
      description: 'Test',
      category: 'MEDICAL',
      goal_amount_usd: 100000,
      status: 'ACTIVE',
      advocate_count: 0,
      is_creator_verified: false,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    });

    await screen.findByText('Test Campaign');
    expect(screen.queryByText('Verified Creator')).not.toBeInTheDocument();
  });

  it('does NOT render Verified Creator badge when is_creator_verified is undefined', async () => {
    renderPage({
      id: 'campaign-1',
      title: 'Test Campaign',
      description: 'Test',
      category: 'MEDICAL',
      goal_amount_usd: 100000,
      status: 'ACTIVE',
      advocate_count: 0,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    });

    await screen.findByText('Test Campaign');
    expect(screen.queryByText('Verified Creator')).not.toBeInTheDocument();
  });
});
