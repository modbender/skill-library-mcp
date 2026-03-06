
// Configuration for the ResearchVault Portal
const envBackend = import.meta.env.VITE_RESEARCHVAULT_BACKEND_URL as string | undefined;
const localBackend =
  typeof window !== 'undefined'
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : 'http://127.0.0.1:8000';

export const BACKEND_URL = envBackend || localBackend;
export const API_BASE = `${BACKEND_URL}/api`;
