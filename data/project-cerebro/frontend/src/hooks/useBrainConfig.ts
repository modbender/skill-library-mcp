import { useState, useCallback, useEffect, useRef } from 'react';
import { api } from '../api/client';

export function useBrainConfig(brainId?: string) {
  const [config, setConfig] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const loadConfig = useCallback(async (id: string) => {
    try {
      setLoading(true);
      const data = await api.getBrainConfig(id);
      const parsed = JSON.parse(data.config || '{}');
      setConfig(parsed);
    } catch (e) {
      console.error('Failed to load brain config:', e);
      setConfig({});
    } finally {
      setLoading(false);
    }
  }, []);

  const saveConfig = useCallback(
    async (id: string, configData: Record<string, any>) => {
      try {
        const configText = JSON.stringify(configData, null, 2);
        await api.saveBrainConfig(id, configText);
        setLastSaved(new Date());
      } catch (e) {
        console.error('Failed to save brain config:', e);
      }
    },
    []
  );

  const updateConfig = useCallback(
    (updates: Record<string, any>) => {
      setConfig((prev) => ({ ...prev, ...updates }));
    },
    []
  );

  const getCfg = useCallback(
    (path: string, fallback: any = '') => {
      const parts = path.split('.');
      let cur: any = config;
      for (const p of parts) {
        if (!cur || typeof cur !== 'object' || !(p in cur)) return fallback;
        cur = cur[p];
      }
      return cur ?? fallback;
    },
    [config]
  );

  const setCfg = useCallback(
    (path: string, value: any) => {
      const parts = path.split('.');
      setConfig((prev) => {
        const next = { ...prev };
        let cur: any = next;
        for (let i = 0; i < parts.length - 1; i++) {
          const p = parts[i];
          cur[p] = typeof cur[p] === 'object' && cur[p] !== null ? { ...cur[p] } : {};
          cur = cur[p];
        }
        cur[parts[parts.length - 1]] = value;
        return next;
      });
    },
    []
  );

  // Auto-save with debounce
  useEffect(() => {
    if (!brainId) return;
    
    if (saveTimerRef.current) {
      clearTimeout(saveTimerRef.current);
    }

    saveTimerRef.current = setTimeout(() => {
      saveConfig(brainId, config);
    }, 700);

    return () => {
      if (saveTimerRef.current) {
        clearTimeout(saveTimerRef.current);
      }
    };
  }, [config, brainId, saveConfig]);

  // Load config when brainId changes
  useEffect(() => {
    if (brainId) {
      loadConfig(brainId);
    }
  }, [brainId, loadConfig]);

  return {
    config,
    loading,
    lastSaved,
    getCfg,
    setCfg,
    updateConfig,
    loadConfig,
    saveConfig,
  };
}
