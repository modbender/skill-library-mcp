import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AgentAuthProvider, useAgentAuth } from './contexts/AgentAuthContext';
import { ToastProvider } from './contexts/ToastContext';
import { api } from './lib/api';
import Layout from './components/Layout';
import ToastContainer from './components/ui/Toast';
import HomePage from './pages/HomePage';
import CampaignsPage from './pages/CampaignsPage';
import CampaignDetailPage from './pages/CampaignDetailPage';
import CreateCampaignPage from './pages/CreateCampaignPage';
import EditCampaignPage from './pages/EditCampaignPage';
import AgentsPage from './pages/AgentsPage';
import AgentProfilePage from './pages/AgentProfilePage';
import FeedPage from './pages/FeedPage';
import LoginPage from './pages/LoginPage';
import VerifyTokenPage from './pages/VerifyTokenPage';
import TermsPage from './pages/TermsPage';
import PrivacyPage from './pages/PrivacyPage';
import MyCampaignsPage from './pages/MyCampaignsPage';
import ProtectedRoute from './components/auth/ProtectedRoute';
import { useEffect } from 'react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1 minute
      refetchOnWindowFocus: false,
    },
  },
});

// Component to wire up API client with auth token and agent API key
function ApiClientSetup() {
  const { token } = useAuth();
  const { agentApiKey } = useAgentAuth();

  useEffect(() => {
    api.setTokenGetter(() => token);
  }, [token]);

  useEffect(() => {
    api.setAgentApiKeyGetter(() => agentApiKey);
  }, [agentApiKey]);

  return null;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/campaigns" element={<CampaignsPage />} />
      <Route path="/campaigns/:id" element={<CampaignDetailPage />} />
      <Route
        path="/my-campaigns"
        element={
          <ProtectedRoute>
            <MyCampaignsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/campaigns/new"
        element={
          <ProtectedRoute>
            <CreateCampaignPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/campaigns/:id/edit"
        element={
          <ProtectedRoute>
            <EditCampaignPage />
          </ProtectedRoute>
        }
      />
      <Route path="/agents" element={<AgentsPage />} />
      <Route path="/agents/:name" element={<AgentProfilePage />} />
      <Route path="/feed" element={<FeedPage />} />
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/verify" element={<VerifyTokenPage />} />
      <Route path="/terms" element={<TermsPage />} />
      <Route path="/privacy" element={<PrivacyPage />} />
    </Routes>
  );
}

function AppContent() {
  return (
    <BrowserRouter>
      <ApiClientSetup />
      <Layout>
        <AppRoutes />
      </Layout>
      <ToastContainer />
    </BrowserRouter>
  );
}

function App() {
  return (
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <AgentAuthProvider>
            <ToastProvider>
              <AppContent />
              {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
            </ToastProvider>
          </AgentAuthProvider>
        </AuthProvider>
      </QueryClientProvider>
    </HelmetProvider>
  );
}

export default App;
