import { useState, useEffect } from 'react';

export type Theme = 'light' | 'dark';
export type ThemeMode = 'light' | 'dark' | 'system';

export function useTheme() {
  const [theme, setTheme] = useState<Theme>('dark');
  const [mode, setMode] = useState<ThemeMode>('system');

  const applyTheme = (nextMode: ThemeMode) => {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (nextMode === 'system') {
      setTheme(prefersDark ? 'dark' : 'light');
    } else {
      setTheme(nextMode);
    }
  };

  useEffect(() => {
    const stored = localStorage.getItem('cerebro-theme') as ThemeMode | null;
    const initialMode: ThemeMode = stored === 'light' || stored === 'dark' || stored === 'system'
      ? stored
      : 'system';

    setMode(initialMode);
    applyTheme(initialMode);
  }, []);

  useEffect(() => {
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e: MediaQueryListEvent) => {
      if (mode === 'system') {
        setTheme(e.matches ? 'dark' : 'light');
      }
    };

    media.addEventListener('change', handler);
    return () => media.removeEventListener('change', handler);
  }, [mode]);

  useEffect(() => {
    const root = document.documentElement;
    const body = document.body;

    if (theme === 'dark') {
      root.classList.add('dark');
      body.classList.add('dark');
    } else {
      root.classList.remove('dark');
      body.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    const nextMode: ThemeMode = mode === 'dark' ? 'light' : mode === 'light' ? 'system' : 'dark';
    setMode(nextMode);
    applyTheme(nextMode);
    localStorage.setItem('cerebro-theme', nextMode);
  };

  return {
    theme,
    mode,
    toggleTheme,
  };
}
