import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider } from '../../src/contexts/AuthContext';
import { ToastProvider } from '../../src/contexts/ToastContext';
import ToastContainer from '../../src/components/ui/Toast';
import EditCampaignPage from '../../src/pages/EditCampaignPage';

const mockCampaignWithImages = {
  id: 'campaign-1',
  title: 'Test Campaign',
  description: 'Test description',
  category: 'MEDICAL',
  goal_amount_usd: 100000,
  creator_id: 'creator-1',
  status: 'ACTIVE',
  advocate_count: 0,
  cover_image_url: null,
  images: [
    { id: 'img-1', image_url: '/api/uploads/campaigns/campaign-1/photo1.jpg', display_order: 0 },
    { id: 'img-2', image_url: '/api/uploads/campaigns/campaign-1/photo2.jpg', display_order: 1 },
  ],
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
  uploadCampaignImage: vi.fn(),
  deleteCampaignImage: vi.fn(),
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

describe('EditCampaignPage - Image Management', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.getCampaign.mockResolvedValue(mockCampaignWithImages);
    mockApi.updateCampaign.mockResolvedValue(mockCampaignWithImages);
    mockApi.getKYCStatus.mockResolvedValue({ can_create_campaign: true });
    mockApi.uploadCampaignImage.mockResolvedValue({ id: 'img-3', image_url: '/api/uploads/campaigns/campaign-1/photo3.jpg', display_order: 2 });
    mockApi.deleteCampaignImage.mockResolvedValue(undefined);
    localStorage.clear();
  });

  it('displays existing campaign images', async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByDisplayValue('Test Campaign')).toBeInTheDocument();
    });

    const images = screen.getAllByAltText(/Existing image|Campaign image/i);
    expect(images.length).toBe(2);
  });

  it('shows the image upload section with label', async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByDisplayValue('Test Campaign')).toBeInTheDocument();
    });

    expect(screen.getByText(/Campaign Images/i)).toBeInTheDocument();
  });

  it('allows uploading a new image', async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => {
      expect(screen.getByDisplayValue('Test Campaign')).toBeInTheDocument();
    });

    const file = new File(['fake-image'], 'test.jpg', { type: 'image/jpeg' });
    const addButton = screen.getByRole('button', { name: /add image/i });
    
    // Find hidden file input via the add button interaction
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    expect(fileInput).toBeTruthy();

    await user.upload(fileInput, file);

    await waitFor(() => {
      expect(mockApi.uploadCampaignImage).toHaveBeenCalledWith('campaign-1', file);
    });
  });

  it('allows deleting an existing image', async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => {
      expect(screen.getByDisplayValue('Test Campaign')).toBeInTheDocument();
    });

    const removeButtons = screen.getAllByRole('button', { name: /remove image/i });
    expect(removeButtons.length).toBe(2);

    await user.click(removeButtons[0]);

    await waitFor(() => {
      expect(mockApi.deleteCampaignImage).toHaveBeenCalledWith('campaign-1', 'img-1');
    });
  });

  it('shows add button only when fewer than 5 images', async () => {
    mockApi.getCampaign.mockResolvedValue({
      ...mockCampaignWithImages,
      images: [
        { id: 'img-1', image_url: '/api/uploads/1.jpg', display_order: 0 },
        { id: 'img-2', image_url: '/api/uploads/2.jpg', display_order: 1 },
        { id: 'img-3', image_url: '/api/uploads/3.jpg', display_order: 2 },
        { id: 'img-4', image_url: '/api/uploads/4.jpg', display_order: 3 },
        { id: 'img-5', image_url: '/api/uploads/5.jpg', display_order: 4 },
      ],
    });
    renderPage();
    await waitFor(() => {
      expect(screen.getByDisplayValue('Test Campaign')).toBeInTheDocument();
    });

    expect(screen.queryByRole('button', { name: /add image/i })).not.toBeInTheDocument();
  });
});
