import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider } from '../../src/contexts/AuthContext';
import { AgentAuthProvider } from '../../src/contexts/AgentAuthContext';
import { ToastProvider } from '../../src/contexts/ToastContext';
import CampaignsPage from '../../src/pages/CampaignsPage';

const mockApi = vi.hoisted(() => ({
  getCampaigns: vi.fn(),
  setTokenGetter: vi.fn(),
  setAgentApiKeyGetter: vi.fn(),
}));

vi.mock('../../src/lib/api', () => ({
  api: mockApi,
}));

const mockCampaigns = [
  {
    id: 'c1',
    title: 'Medical Fund',
    description: 'Help with medical bills',
    category: 'MEDICAL',
    goal_amount_usd: 50000,
    status: 'ACTIVE',
    advocate_count: 3,
    cover_image_url: null,
    images: [],
    current_total_usd_cents: 10000,
    created_at: '2026-02-01T00:00:00Z',
  },
  {
    id: 'c2',
    title: 'Education Drive',
    description: 'Scholarships for students',
    category: 'EDUCATION',
    goal_amount_usd: 100000,
    status: 'ACTIVE',
    advocate_count: 1,
    cover_image_url: null,
    images: [],
    current_total_usd_cents: 5000,
    created_at: '2026-02-02T00:00:00Z',
  },
];

function renderPage(initialEntries = ['/campaigns']) {
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
              <MemoryRouter initialEntries={initialEntries}>
                <Routes>
                  <Route path="/campaigns" element={<CampaignsPage />} />
                </Routes>
              </MemoryRouter>
            </ToastProvider>
          </AgentAuthProvider>
        </AuthProvider>
      </QueryClientProvider>
    </HelmetProvider>
  );
}

describe('CampaignsPage filters', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApi.getCampaigns.mockResolvedValue({
      campaigns: mockCampaigns,
      total: 2,
      page: 1,
      per_page: 12,
    });
  });

  it('renders category filter pills', async () => {
    renderPage();
    await screen.findByText('Medical Fund');
    expect(screen.getByRole('button', { name: /Medical/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Education/i })).toBeInTheDocument();
  });

  it('displays result count', async () => {
    renderPage();
    await screen.findByText('Medical Fund');
    expect(screen.getByText(/2 campaigns/i)).toBeInTheDocument();
  });

  it('shows clear button when search has text', async () => {
    renderPage();
    await screen.findByText('Medical Fund');
    const searchInput = screen.getByPlaceholderText(/Search campaigns/i);
    fireEvent.change(searchInput, { target: { value: 'test' } });
    const clearBtn = screen.getByLabelText(/Clear search/i);
    expect(clearBtn).toBeInTheDocument();
  });

  it('clears search when clear button is clicked', async () => {
    renderPage();
    await screen.findByText('Medical Fund');
    const searchInput = screen.getByPlaceholderText(/Search campaigns/i) as HTMLInputElement;
    fireEvent.change(searchInput, { target: { value: 'test' } });
    const clearBtn = screen.getByLabelText(/Clear search/i);
    fireEvent.click(clearBtn);
    expect(searchInput.value).toBe('');
  });

  it('shows empty state for no results', async () => {
    mockApi.getCampaigns.mockResolvedValue({
      campaigns: [],
      total: 0,
      page: 1,
      per_page: 12,
    });
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/No campaigns found/i)).toBeInTheDocument();
    });
  });

  it('reads initial filters from URL params', async () => {
    renderPage(['/campaigns?category=MEDICAL&sort=trending']);
    await waitFor(() => {
      expect(mockApi.getCampaigns).toHaveBeenCalledWith(
        expect.objectContaining({
          category: 'MEDICAL',
          sort: 'trending',
        })
      );
    });
  });
});
