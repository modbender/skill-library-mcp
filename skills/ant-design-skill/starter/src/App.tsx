import React from 'react';
import { AppProviders } from './AppProviders';
import UsersPage from './pages/UsersPage';

export function App() {
  return (
    <AppProviders>
      <UsersPage />
    </AppProviders>
  );
}
