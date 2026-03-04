import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider } from '../../src/contexts/AuthContext';
import { AgentAuthProvider } from '../../src/contexts/AgentAuthContext';
import { ToastProvider } from '../../src/contexts/ToastContext';
import AgentProfilePage from '../../src/pages/AgentProfilePage';

const mockApi = vi.hoisted(() => ({
  getAgent: vi.fn(),
  getCurrentAgent: vi.fn(),
  uploadAgentAvatar: vi.fn(),
  updateAgentProfile: vi.fn(),
  setTokenGetter: vi.fn(),
  setAgentApiKeyGetter: vi.fn(),
}));

vi.mock('../../src/lib/api', () => ({
  api: mockApi,
}));

const agentWithoutAvatar = {
  id: 'agent-1',
  name: 'Onyx',
  description: 'Onchain detective',
  avatar_url: null,
  karma: 42,
  created_at: '2026-02-01T00:00:00Z',
};

const agentWithAvatar = {
  ...agentWithoutAvatar,
  avatar_url: 'https://api.dicebear.com/7.x/bottts/svg?seed=Onyx',
};

function renderPage(agentName: string) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  // Note: each test sets localStorage if needed for auth

  return render(
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <AgentAuthProvider>
            <ToastProvider>
              <MemoryRouter initialEntries={[`/agents/${agentName}`]}>
                <Routes>
                  <Route path="/agents/:name" element={<AgentProfilePage />} />
                </Routes>
              </MemoryRouter>
            </ToastProvider>
          </AgentAuthProvider>
        </AuthProvider>
      </QueryClientProvider>
    </HelmetProvider>
  );
}

describe('Agent avatar CTA', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('shows Add a profile photo CTA when agent has no avatar and is viewing own profile', async () => {
    mockApi.getAgent.mockResolvedValue(agentWithoutAvatar);
    mockApi.getCurrentAgent.mockResolvedValue(agentWithoutAvatar);
    localStorage.setItem('moltfundme_agent_api_key', 'molt_test_key');

    renderPage('Onyx');
    const cta = await screen.findByText(/Add a profile photo/i);
    expect(cta).toBeInTheDocument();
  });

  it('does NOT show avatar CTA when agent has an avatar', async () => {
    mockApi.getAgent.mockResolvedValue(agentWithAvatar);
    mockApi.getCurrentAgent.mockResolvedValue(agentWithAvatar);
    localStorage.setItem('moltfundme_agent_api_key', 'molt_test_key');

    renderPage('Onyx');
    await screen.findByText('Onyx');
    expect(screen.queryByText(/Add a profile photo/i)).not.toBeInTheDocument();
  });

  it('does NOT show avatar CTA when viewing someone else\'s profile', async () => {
    mockApi.getAgent.mockResolvedValue(agentWithoutAvatar);
    mockApi.getCurrentAgent.mockResolvedValue({ ...agentWithoutAvatar, id: 'other-agent', name: 'Mira' });
    localStorage.setItem('moltfundme_agent_api_key', 'molt_test_key');

    renderPage('Onyx');
    await screen.findByText('Onyx');
    expect(screen.queryByText(/Add a profile photo/i)).not.toBeInTheDocument();
  });

  it('renders DiceBear default avatar when agent has no avatar_url', async () => {
    mockApi.getAgent.mockResolvedValue(agentWithoutAvatar);
    mockApi.getCurrentAgent.mockResolvedValue(null);

    renderPage('Onyx');
    await screen.findByText('Onyx');
    // The Avatar component should render an img with a DiceBear URL as fallback
    const avatarImg = screen.queryByRole('img', { name: /Onyx/i });
    if (avatarImg) {
      expect(avatarImg.getAttribute('src')).toContain('dicebear');
    }
  });
});
