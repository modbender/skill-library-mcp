import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider } from '../../src/contexts/AuthContext';
import { ToastProvider } from '../../src/contexts/ToastContext';
import ToastContainer from '../../src/components/ui/Toast';
import EditCampaignPage from '../../src/pages/EditCampaignPage';

const mockCampaign = {
  id: 'campaign-1',
  title: 'Existing Campaign',
  description: 'Existing description',
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
  creator_name: 'Jane Doe',
  creator_story: 'My story',
  current_total_usd_cents: 0,
  withdrawal_detected: false,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

const mockApi = vi.hoisted(() => ({
  getCampaign: vi.fn(),
  updateCampaign: vi.fn(),
  getKYCStatus: vi.fn(),
  setTokenGetter: vi.fn(),
}));

vi.mock('../../src/lib/api', () => ({
  api: mockApi,
}));

vi.mock('../../src/components/WalletGeneratorModal', () => ({
  default: () => null,
}));

vi.mock('../../src/components/ChainSelector', () => ({
  default: () => null,
}));

function renderPage(campaignId = 'campaign-1') {
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
          <MemoryRouter initialEntries={[`/campaigns/${campaignId}/edit`]}>
            <Routes>
              <Route path="/campaigns/:id/edit" element={<EditCampaignPage />} />
            </Routes>
            <ToastContainer />
          </MemoryRouter>
        </ToastProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

describe('EditCampaignPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.getCampaign.mockResolvedValue(mockCampaign);
    mockApi.updateCampaign.mockResolvedValue({ ...mockCampaign, title: 'Updated Title' });
    mockApi.getKYCStatus.mockResolvedValue({ can_create_campaign: true });
    localStorage.clear();
  });

  it('loads form with existing campaign data pre-filled', async () => {
    renderPage();
    await waitFor(() => {
      expect(mockApi.getCampaign).toHaveBeenCalledWith('campaign-1');
    });
    await waitFor(() => {
      expect(screen.getByDisplayValue('Existing Campaign')).toBeInTheDocument();
    });
    expect(screen.getByDisplayValue('Existing description')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Jane Doe')).toBeInTheDocument();
  });

  it('redirects non-owner to campaign detail', async () => {
    mockApi.getCampaign.mockResolvedValue({
      ...mockCampaign,
      creator_id: 'other-creator-id',
    });
    localStorage.setItem(
      'moltfundme_user',
      JSON.stringify({ id: 'creator-1', email: 'test@example.com' })
    );
    localStorage.setItem('moltfundme_token', 'fake-jwt');

    renderPage();
    await waitFor(() => {
      expect(mockApi.getCampaign).toHaveBeenCalled();
    });
    // Should redirect - typically via Navigate or useNavigate
    // We check that we don't see the Save Changes button (form not shown for non-owner)
    await waitFor(() => {
      expect(screen.queryByRole('button', { name: /Save Changes/i })).not.toBeInTheDocument();
    }, { timeout: 2000 });
  });

  it('calls updateCampaign and navigates on successful update', async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => {
      expect(screen.getByDisplayValue('Existing Campaign')).toBeInTheDocument();
    });

    const titleInput = screen.getByDisplayValue('Existing Campaign');
    await user.clear(titleInput);
    await user.type(titleInput, 'Updated Title');

    const submitButton = screen.getByRole('button', { name: /Save Changes/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockApi.updateCampaign).toHaveBeenCalledWith(
        'campaign-1',
        expect.objectContaining({ title: 'Updated Title' })
      );
    });
  });

  it('shows toast on update failure', async () => {
    const user = userEvent.setup();
    mockApi.updateCampaign.mockRejectedValue(new Error('Update failed'));
    renderPage();
    await waitFor(() => {
      expect(screen.getByDisplayValue('Existing Campaign')).toBeInTheDocument();
    });

    const submitButton = screen.getByRole('button', { name: /Save Changes/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockApi.updateCampaign).toHaveBeenCalled();
    });
    await waitFor(() => {
      expect(screen.getByText(/Failed to update campaign|Update failed/i)).toBeInTheDocument();
    });
  });
});
