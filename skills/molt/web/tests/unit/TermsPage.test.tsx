import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import TermsPage from '../../src/pages/TermsPage';

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/terms']}>
      <Routes>
        <Route path="/terms" element={<TermsPage />} />
      </Routes>
    </MemoryRouter>
  );
}

describe('TermsPage', () => {
  it('renders the page', () => {
    renderPage();
    expect(screen.getByRole('heading', { name: /terms of service/i })).toBeInTheDocument();
  });

  it('contains key legal phrases: information service, non-custodial, peer-to-peer', () => {
    renderPage();
    const content = document.body.textContent || '';
    expect(content).toMatch(/information service/i);
    expect(content).toMatch(/non-custodial|non custodial/i);
    expect(content).toMatch(/peer-to-peer|peer to peer/i);
  });
});
