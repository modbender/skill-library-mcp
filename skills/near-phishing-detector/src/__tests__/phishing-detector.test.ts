import { describe, expect, it } from 'vitest';
import {
  near_phishing_check_contract,
  near_phishing_check_url,
  near_phishing_database,
  near_phishing_report
} from '../phishing-detector.js';

describe('near phishing detector', () => {
  it('flags known scam URL as high risk', async () => {
    const out = await near_phishing_check_url('https://wallet-near.support/login');
    expect(out.ok).toBe(true);
    expect(out.risk_level).toBe('high');
    expect(Number(out.risk_score)).toBeGreaterThanOrEqual(70);
  });

  it('flags suspicious contract with bait words', async () => {
    const out = await near_phishing_check_contract('near-airdrop-claim.near');
    expect(out.ok).toBe(true);
    expect(['medium', 'high']).toContain(out.risk_level);
  });

  it('returns scam database records', async () => {
    const out = await near_phishing_database();
    expect(out.length).toBeGreaterThan(0);
    expect(out.some((r) => r.type === 'domain')).toBe(true);
  });

  it('creates phishing report with triage', async () => {
    const out = await near_phishing_report('https://near-airdrop-claim.com', 'Seed phrase requested in popup');
    expect(out.ok).toBe(true);
    expect(typeof out.report_id).toBe('string');
    expect((out as any).triage).toBeDefined();
    expect(Array.isArray((out as any).next_actions)).toBe(true);
  });

  it('rejects malformed URL input', async () => {
    const out = await near_phishing_check_url('http://%%%bad-url%%%');
    expect(out.ok).toBe(false);
    expect(out.error).toBe('url_parse_failed');
  });
});
