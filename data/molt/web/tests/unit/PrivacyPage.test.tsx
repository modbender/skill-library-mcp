import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import PrivacyPage from '../../src/pages/PrivacyPage';

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/privacy']}>
      <Routes>
        <Route path="/privacy" element={<PrivacyPage />} />
      </Routes>
    </MemoryRouter>
  );
}

describe('PrivacyPage', () => {
  it('renders the page', () => {
    renderPage();
    expect(screen.getByRole('heading', { name: /privacy policy/i })).toBeInTheDocument();
  });

  it('contains key phrases: KYC, identity verification', () => {
    renderPage();
    const content = document.body.textContent || '';
    expect(content).toMatch(/KYC|identity verification/i);
  });
});
