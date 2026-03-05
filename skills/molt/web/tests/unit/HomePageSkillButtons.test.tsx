import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider } from '../../src/contexts/AuthContext';
import { AgentAuthProvider } from '../../src/contexts/AgentAuthContext';
import { ToastProvider } from '../../src/contexts/ToastContext';
import HomePage from '../../src/pages/HomePage';

const mockApi = vi.hoisted(() => ({
  getCampaigns: vi.fn(),
  getLeaderboard: vi.fn(),
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
              <MemoryRouter initialEntries={['/']}>
                <HomePage />
              </MemoryRouter>
            </ToastProvider>
          </AgentAuthProvider>
        </AuthProvider>
      </QueryClientProvider>
    </HelmetProvider>
  );
}

describe('HomePage Agent Skills section', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.getCampaigns.mockResolvedValue({ campaigns: [], total: 0, page: 1, per_page: 6 });
    mockApi.getLeaderboard.mockResolvedValue([]);
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText: vi.fn().mockResolvedValue(undefined) },
      writable: true,
      configurable: true,
    });
  });

  it('renders Copy Skill button', async () => {
    renderPage();
    const copyBtn = await screen.findByRole('button', { name: /Copy Skill/i });
    expect(copyBtn).toBeInTheDocument();
  });

  it('renders Download Skill button', async () => {
    renderPage();
    const downloadBtn = await screen.findByRole('button', { name: /Download Skill/i });
    expect(downloadBtn).toBeInTheDocument();
  });

  it('copies skill content to clipboard on Copy Skill click', async () => {
    renderPage();
    const copyBtn = await screen.findByRole('button', { name: /Copy Skill/i });
    fireEvent.click(copyBtn);

    await waitFor(() => {
      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
        expect.stringContaining('MoltFundMe Skill')
      );
    });
  });

  it('shows Copied feedback after clicking Copy Skill', async () => {
    renderPage();
    const copyBtn = await screen.findByRole('button', { name: /Copy Skill/i });
    fireEvent.click(copyBtn);

    await waitFor(() => {
      expect(screen.getByText(/Copied/i)).toBeInTheDocument();
    });
  });

  it('renders public URL link for SKILL.md', async () => {
    renderPage();
    const link = await screen.findByText(/moltfundme\.com\/SKILL\.md/i);
    expect(link).toBeInTheDocument();
  });
});
