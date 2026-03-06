import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import CampaignCard from '../../src/components/CampaignCard';
import type { Campaign } from '../../src/lib/api';

const baseCampaign: Campaign = {
  id: 'campaign-1',
  title: 'Test Campaign',
  description: 'A test campaign for unit testing',
  category: 'MEDICAL',
  goal_amount_usd: 500000, // $5,000 in cents
  status: 'ACTIVE',
  advocate_count: 2,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

function renderCard(campaign: Campaign) {
  return render(
    <MemoryRouter>
      <CampaignCard campaign={campaign} />
    </MemoryRouter>
  );
}

describe('CampaignCard', () => {
  it('displays $0.00 raised when campaign has no donations', () => {
    renderCard({ ...baseCampaign, current_total_usd_cents: 0 });

    expect(screen.getByText('$0.00')).toBeInTheDocument();
    expect(screen.getByText('of $5,000.00')).toBeInTheDocument();
    expect(screen.getByText('0.0% funded')).toBeInTheDocument();
  });

  it('displays correct raised amount from current_total_usd_cents', () => {
    renderCard({
      ...baseCampaign,
      current_total_usd_cents: 125000, // $1,250.00
    });

    expect(screen.getByText('$1,250.00')).toBeInTheDocument();
    expect(screen.getByText('of $5,000.00')).toBeInTheDocument();
    expect(screen.getByText('25.0% funded')).toBeInTheDocument();
  });

  it('uses crypto fallback when current_total_usd_cents is not set', () => {
    renderCard({
      ...baseCampaign,
      current_total_usd_cents: undefined,
      current_usdc_base: 500000000, // 500 USDC = $500
    });

    // cryptoToUsd with 500 USDC should produce $500.00
    expect(screen.getByText('$500.00')).toBeInTheDocument();
  });

  it('caps progress percentage at 100%', () => {
    renderCard({
      ...baseCampaign,
      goal_amount_usd: 100000, // $1,000
      current_total_usd_cents: 200000, // $2,000 — over goal
    });

    expect(screen.getByText('100.0% funded')).toBeInTheDocument();
  });
});
