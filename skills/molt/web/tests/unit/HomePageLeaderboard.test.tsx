import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
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

const mockAgents = [
  { id: '1', name: 'Onyx', description: 'Onchain detective', avatar_url: null, karma: 42, created_at: '2026-02-01T00:00:00Z' },
  { id: '2', name: 'Mira', description: 'Empathy scout', avatar_url: null, karma: 35, created_at: '2026-02-01T00:00:00Z' },
  { id: '3', name: 'Doc', description: 'Medical specialist', avatar_url: null, karma: 28, created_at: '2026-02-01T00:00:00Z' },
  { id: '4', name: 'Sage', description: 'Philosopher', avatar_url: null, karma: 20, created_at: '2026-02-01T00:00:00Z' },
  { id: '5', name: 'Flick', description: 'Pulse reader', avatar_url: null, karma: 15, created_at: '2026-02-01T00:00:00Z' },
];

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

describe('HomePage Top Molts leaderboard section', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.getCampaigns.mockResolvedValue({ campaigns: [], total: 0, page: 1, per_page: 6 });
    mockApi.getLeaderboard.mockResolvedValue(mockAgents);
  });

  it('renders Top Molts heading', async () => {
    renderPage();
    const heading = await screen.findByText('Top Molts');
    expect(heading).toBeInTheDocument();
  });

  it('displays agent names from leaderboard', async () => {
    renderPage();
    expect(await screen.findByText('Onyx')).toBeInTheDocument();
    expect(screen.getByText('Mira')).toBeInTheDocument();
    expect(screen.getByText('Doc')).toBeInTheDocument();
  });

  it('displays karma scores', async () => {
    renderPage();
    await screen.findByText('Onyx');
    expect(screen.getByText('42 karma')).toBeInTheDocument();
    expect(screen.getByText('35 karma')).toBeInTheDocument();
  });

  it('renders View Full Leaderboard link', async () => {
    renderPage();
    const links = await screen.findAllByRole('link', { name: /View Full Leaderboard/i });
    expect(links.length).toBeGreaterThan(0);
    expect(links[0]).toHaveAttribute('href', '/agents');
  });

  it('handles empty leaderboard gracefully', async () => {
    mockApi.getLeaderboard.mockResolvedValue([]);
    renderPage();
    // Should still render the section heading
    const heading = await screen.findByText('Top Molts');
    expect(heading).toBeInTheDocument();
  });
});
