import { theme } from 'antd';

export type ThemeMode = 'light' | 'dark';

export function getAntdTheme(mode: ThemeMode) {
  const isDark = mode === 'dark';

  return {
    algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
    token: {
      // === brand tokens (start here) ===
      colorPrimary: '#1677ff',
      borderRadius: 10,
      fontSize: 14,
      // Optional:
      // fontFamily: 'Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif',
    },
    components: {
      Button: { controlHeight: 40 },
      Layout: { headerBg: '#ffffff' },
      Table: { headerBg: '#fafafa' },
    },
  } as const;
}
