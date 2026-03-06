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

describe('CreateCampaignPage submit guard', () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    mockApi.getKYCStatus.mockResolvedValue({ can_create_campaign: true });
    mockApi.createCampaign.mockImplementation(
      () => new Promise(() => {}) // Never resolves - simulates pending state
    );

    // Pre-login so user exists
    localStorage.setItem(
      'moltfundme_user',
      JSON.stringify({ id: 'creator-1', email: 'test@example.com' })
    );
    localStorage.setItem('moltfundme_token', 'fake-jwt');
  });

  it('calls createCampaign only once when form is submitted twice quickly', async () => {
    const user = userEvent.setup();
    renderPage();

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Help Maria/i)).toBeInTheDocument();
    });

    // Fill form
    const titleInput = screen.getByPlaceholderText(/Help Maria/i);
    const descInput = screen.getByPlaceholderText(/Tell your story/i);
    const creatorNameInput = screen.getByPlaceholderText(/Jane Doe/i);
    const goalInput = screen.getByPlaceholderText(/1000\.00/);
    await user.type(titleInput, 'Test Campaign');
    await user.type(descInput, 'Test description for the campaign');
    await user.type(creatorNameInput, 'Jane Doe');
    await user.selectOptions(screen.getByRole('combobox'), 'MEDICAL');
    await user.type(goalInput, '1000');

    // Select a chain and generate wallets
    await user.click(screen.getByRole('checkbox', { name: /Bitcoin/i }));
    await user.click(screen.getByRole('button', { name: /Generate Wallets/i }));

    // Confirm wallets in mock modal
    const confirmBtn = await screen.findByRole('button', { name: /Confirm Wallets/i });
    await user.click(confirmBtn);

    // Wait for modal to close (generatedWallets state to be set)
    await waitFor(() => {
      expect(screen.queryByTestId('wallet-modal-mock')).not.toBeInTheDocument();
    });

    // Submit button should now be enabled - click it twice quickly
    const submitButton = screen.getByRole('button', { name: /Create Campaign/i });
    await user.click(submitButton);
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockApi.createCampaign).toHaveBeenCalledTimes(1);
    });
  });
});
