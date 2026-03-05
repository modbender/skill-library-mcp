import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../../src/contexts/AuthContext';
import { AgentAuthProvider } from '../../src/contexts/AgentAuthContext';
import { ToastProvider } from '../../src/contexts/ToastContext';
import Layout from '../../src/components/Layout';

function renderLayout() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <AgentAuthProvider>
          <ToastProvider>
            <Layout>
              <div>Page content</div>
            </Layout>
          </ToastProvider>
        </AgentAuthProvider>
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('Layout footer links', () => {
  it('contains Terms of Service link with correct href', () => {
    renderLayout();
    const termsLink = screen.getByRole('link', { name: /terms of service/i });
    expect(termsLink).toBeInTheDocument();
    expect(termsLink).toHaveAttribute('href', '/terms');
  });

  it('contains Privacy Policy link with correct href', () => {
    renderLayout();
    const privacyLink = screen.getByRole('link', { name: /privacy policy/i });
    expect(privacyLink).toBeInTheDocument();
    expect(privacyLink).toHaveAttribute('href', '/privacy');
  });
});
