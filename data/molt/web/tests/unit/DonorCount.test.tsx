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

describe('CampaignDetailPage donor count', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders donation count when donation_count > 0', async () => {
    renderPage({
      id: 'campaign-1',
      title: 'Test Campaign',
      description: 'Test',
      category: 'MEDICAL',
      goal_amount_usd: 100000,
      status: 'ACTIVE',
      advocate_count: 0,
      donation_count: 5,
      donor_count: 3,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    });

    await screen.findByText('Test Campaign');
    const section = screen.getByTestId('donation-donor-count');
    expect(section).toHaveTextContent('5');
    expect(section).toHaveTextContent('donations');
  });

  it('renders donor count when donation_count > 0 and donor_count > 1', async () => {
    renderPage({
      id: 'campaign-1',
      title: 'Test Campaign',
      description: 'Test',
      category: 'MEDICAL',
      goal_amount_usd: 100000,
      status: 'ACTIVE',
      advocate_count: 0,
      donation_count: 5,
      donor_count: 3,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    });

    await screen.findByText('Test Campaign');
    const section = screen.getByTestId('donation-donor-count');
    expect(section).toHaveTextContent('3');
    expect(section).toHaveTextContent('donors');
  });

  it('does NOT render donation/donor meta section when donation_count is 0', async () => {
    renderPage({
      id: 'campaign-1',
      title: 'Test Campaign',
      description: 'Test',
      category: 'MEDICAL',
      goal_amount_usd: 100000,
      status: 'ACTIVE',
      advocate_count: 0,
      donation_count: 0,
      donor_count: 0,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    });

    await screen.findByText('Test Campaign');
    expect(screen.queryByTestId('donation-donor-count')).not.toBeInTheDocument();
  });
});
