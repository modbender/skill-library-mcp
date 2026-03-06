import { useState, useCallback } from 'react';
import { api } from '../api/client';
import type { Report } from '../api/types';

export function useReports(brainId?: string) {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetch = useCallback(
    async (id: string, limit = 10) => {
      try {
        setLoading(true);
        const data = await api.getReports(id, limit);
        setReports(data.reports || []);
        setError(null);
      } catch (e) {
        setError(e as Error);
        console.error('Failed to fetch reports:', e);
        setReports([]);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  // Auto-fetch if brainId provided
  useState(() => {
    if (brainId) {
      fetch(brainId);
    }
  });

  return {
    reports,
    loading,
    error,
    fetchReports: fetch,
  };
}
