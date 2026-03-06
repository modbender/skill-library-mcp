import { useState, useCallback } from 'react';
import { api } from '../api/client';
import type { BrainStatus } from '../api/types';
import { usePolling } from './usePolling';

export function useBrains() {
  const [brains, setBrains] = useState<BrainStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetch = useCallback(async () => {
    try {
      const data = await api.getStatus();
      setBrains(data.brains || []);
      setError(null);
    } catch (e) {
      setError(e as Error);
      console.error('Failed to fetch brains:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  usePolling(fetch);

  const toggleBrain = useCallback(async (id: string, enabled: boolean) => {
    try {
      await api.toggleBrain(id, enabled);
      await fetch();
    } catch (e) {
      console.error('Failed to toggle brain:', e);
    }
  }, [fetch]);

  const runBrain = useCallback(async (id: string) => {
    try {
      await api.runBrain(id);
      setTimeout(fetch, 500);
    } catch (e) {
      console.error('Failed to run brain:', e);
    }
  }, [fetch]);

  return {
    brains,
    loading,
    error,
    toggleBrain,
    runBrain,
    refetch: fetch,
  };
}
