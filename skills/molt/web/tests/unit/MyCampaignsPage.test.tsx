import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider } from '../../src/contexts/AuthContext';
import { ToastProvider } from '../../src/contexts/ToastContext';
import MyCampaignsPage from '../../src/pages/MyCampaignsPage';

const mockCampaigns = {
  campaigns: [
    {
      id: 'camp-1',
      title: 'My Active Campaign',
      description: 'Desc',
      category: 'MEDICAL',
      goal_amount_usd: 500000,
      status: 'ACTIVE' as const,
      advocate_count: 0,
      cover_image_url: undefined,
      images: [],
      current_total_usd_cents: 0,
      withdrawal_detected: false,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    },
    {
      id: 'camp-2',
      title: 'My Cancelled Campaign',
      description: 'Desc',
      category: 'EDUCATION',
      goal_amount_usd: 100000,
      status: 'CANCELLED' as const,
      advocate_count: 0,
      cover_image_url: undefined,
      images: [],
      current_total_usd_cents: 0,
      withdrawal_detected: false,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    },
  ],
  total: 2,
  page: 1,
  per_page: 20,
};

const mockApi = vi.hoisted(() => ({
  getMyCampaigns: vi.fn(),
  deleteCampaign: vi.fn(),
  setTokenGetter: vi.fn(),
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

  localStorage.setItem(
    'moltfundme_user',
    JSON.stringify({ id: 'creator-1', email: 'test@example.com' })
  );
  localStorage.setItem('moltfundme_token', 'fake-jwt');

  return render(
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ToastProvider>
          <MemoryRouter initialEntries={['/my-campaigns']}>
            <Routes>
              <Route path="/my-campaigns" element={<MyCampaignsPage />} />
            </Routes>
          </MemoryRouter>
        </ToastProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

describe('MyCampaignsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.getMyCampaigns.mockResolvedValue(mockCampaigns);
    mockApi.deleteCampaign.mockResolvedValue(undefined);
  });

  it('renders campaign list', async () => {
    renderPage();
    await screen.findByText('My Active Campaign');
    expect(screen.getByText('My Cancelled Campaign')).toBeInTheDocument();
  });

  it('shows status badge for cancelled campaigns', async () => {
    renderPage();
    await screen.findByText('My Active Campaign');
    expect(screen.getByText('CANCELLED')).toBeInTheDocument();
  });

  it('shows delete button for each campaign', async () => {
    renderPage();
    await screen.findByText('My Active Campaign');
    const deleteButtons = screen.getAllByRole('button', { name: /Delete/i });
    expect(deleteButtons.length).toBeGreaterThanOrEqual(1);
  });
});
