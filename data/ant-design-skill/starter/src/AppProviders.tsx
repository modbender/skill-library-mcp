import React, { useMemo, useState } from 'react';
import { ConfigProvider, Layout, Switch, Typography } from 'antd';
import { getAntdTheme, ThemeMode } from './theme';

export function AppProviders({ children }: { children: React.ReactNode }) {
  const [mode, setMode] = useState<ThemeMode>('light');

  const antdTheme = useMemo(() => getAntdTheme(mode), [mode]);

  return (
    <ConfigProvider theme={antdTheme}>
      <Layout style={{ minHeight: '100vh' }}>
        <Layout.Header
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Typography.Text style={{ color: '#fff', fontWeight: 600 }}>
            AntD Starter
          </Typography.Text>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Typography.Text style={{ color: '#fff' }}>Dark</Typography.Text>
            <Switch checked={mode === 'dark'} onChange={(v) => setMode(v ? 'dark' : 'light')} />
          </div>
        </Layout.Header>
        <Layout.Content>{children}</Layout.Content>
      </Layout>
    </ConfigProvider>
  );
}
