import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider } from '../../src/contexts/AuthContext';
import { ToastProvider } from '../../src/contexts/ToastContext';
import CreateCampaignPage from '../../src/pages/CreateCampaignPage';

const mockApi = vi.hoisted(() => ({
  createCampaign: vi.fn(),
  getKYCStatus: vi.fn(),
  getCampaigns: vi.fn().mockResolvedValue({ campaigns: [], total: 0 }),
  setTokenGetter: vi.fn(),
}));

vi.mock('../../src/lib/api', () => ({
  api: mockApi,
}));

vi.mock('../../src/components/WalletGeneratorModal', () => ({
  default: ({
    isOpen,
    onConfirm,
  }: {
    isOpen: boolean;
    onConfirm: (w: Record<string, string>) => void;
  }) =>
    isOpen ? (
      <div data-testid="wallet-modal-mock">
        <button
          type="button"
          onClick={() => onConfirm({ btc: 'bc1qtest', eth: '0x1234567890123456789012345678901234567890' })}
        >
          Confirm Wallets
        </button>
      </div>
    ) : null,
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
          <MemoryRouter initialEntries={['/campaigns/new']}>
            <Routes>
              <Route path="/campaigns/new" element={<CreateCampaignPage />} />
            </Routes>
          </MemoryRouter>
        </ToastProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

describe('CreateCampaignPage creator info fields', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.getKYCStatus.mockResolvedValue({ can_create_campaign: true });
    mockApi.createCampaign.mockResolvedValue({
      id: 'new-campaign-id',
      title: 'Test',
      creator_name: 'Jane Doe',
      creator_story: 'My story',
    });
  });

  it('renders creator name and story form fields', async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Help Maria/i)).toBeInTheDocument();
    });

    expect(screen.getByPlaceholderText(/Jane Doe/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Tell donors/i)).toBeInTheDocument();
  });

  it('includes creator_name and creator_story in submit payload', async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Help Maria/i)).toBeInTheDocument();
    });

    await user.type(screen.getByPlaceholderText(/Help Maria/i), 'Test Campaign');
    await user.type(screen.getByPlaceholderText(/Tell your story/i), 'Campaign description');
    await user.type(screen.getByPlaceholderText(/Jane Doe/i), 'Jane Doe');
    await user.type(screen.getByPlaceholderText(/Tell donors/i), 'I am raising funds for medical expenses.');
    await user.selectOptions(screen.getByRole('combobox'), 'MEDICAL');
    await user.type(screen.getByPlaceholderText(/1000\.00/), '1000');

    await user.click(screen.getByRole('checkbox', { name: /Bitcoin/i }));
    await user.click(screen.getByRole('button', { name: /Generate Wallets/i }));
    const confirmBtn = await screen.findByRole('button', { name: /Confirm Wallets/i });
    await user.click(confirmBtn);

    await waitFor(() => {
      expect(screen.queryByTestId('wallet-modal-mock')).not.toBeInTheDocument();
    });

    await user.click(screen.getByRole('button', { name: /Create Campaign/i }));

    await waitFor(() => {
      expect(mockApi.createCampaign).toHaveBeenCalled();
      const call = mockApi.createCampaign.mock.calls[0][0];
      expect(call.creator_name).toBe('Jane Doe');
      expect(call.creator_story).toContain('medical expenses');
    });
  });
});
