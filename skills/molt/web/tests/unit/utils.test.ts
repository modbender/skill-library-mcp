import { describe, it, expect, vi } from 'vitest';
import {
  formatCurrency,
  formatDate,
  formatRelativeTime,
  truncate,
  copyToClipboard,
  dollarsToCents,
  centsToDollars,
  validateEthAddress,
  validateBtcAddress,
  validateSolAddress,
} from '../../src/lib/utils';

describe('formatCurrency', () => {
  it('should format positive amounts correctly', () => {
    expect(formatCurrency(1000)).toBe('$1,000.00');
    expect(formatCurrency(100.5)).toBe('$100.50');
    expect(formatCurrency(0)).toBe('$0.00');
  });

  it('should format negative amounts correctly', () => {
    expect(formatCurrency(-1000)).toBe('-$1,000.00');
  });

  it('should handle decimal amounts', () => {
    expect(formatCurrency(10.99)).toBe('$10.99');
    expect(formatCurrency(0.01)).toBe('$0.01');
  });
});

describe('formatDate', () => {
  it('should format valid date strings', () => {
    const date = new Date('2024-01-15T10:30:00Z');
    const formatted = formatDate(date.toISOString());
    expect(formatted).toContain('January');
    expect(formatted).toContain('2024');
  });

  it('should handle invalid date strings gracefully', () => {
    expect(() => formatDate('invalid-date')).not.toThrow();
  });
});

describe('formatRelativeTime', () => {
  it('should return "just now" for recent times', () => {
    const now = new Date();
    const recent = new Date(now.getTime() - 30 * 1000); // 30 seconds ago
    expect(formatRelativeTime(recent.toISOString())).toBe('just now');
  });

  it('should format minutes ago', () => {
    const now = new Date();
    const fiveMinutesAgo = new Date(now.getTime() - 5 * 60 * 1000);
    expect(formatRelativeTime(fiveMinutesAgo.toISOString())).toBe('5 minutes ago');
  });

  it('should format hours ago', () => {
    const now = new Date();
    const twoHoursAgo = new Date(now.getTime() - 2 * 60 * 60 * 1000);
    expect(formatRelativeTime(twoHoursAgo.toISOString())).toBe('2 hours ago');
  });

  it('should format days ago', () => {
    const now = new Date();
    const threeDaysAgo = new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000);
    expect(formatRelativeTime(threeDaysAgo.toISOString())).toBe('3 days ago');
  });

  it('should fall back to formatDate for older dates', () => {
    const now = new Date();
    const oldDate = new Date(now.getTime() - 10 * 24 * 60 * 60 * 1000); // 10 days ago
    const result = formatRelativeTime(oldDate.toISOString());
    expect(result).not.toContain('days ago');
    // Should use formatDate which includes the year
    expect(result).toMatch(/\d{4}/); // Contains a 4-digit year
  });
});

describe('truncate', () => {
  it('should return text unchanged if shorter than maxLength', () => {
    expect(truncate('short', 10)).toBe('short');
  });

  it('should truncate text longer than maxLength', () => {
    expect(truncate('this is a long text', 10)).toBe('this is a ...');
  });

  it('should add ellipsis when truncating', () => {
    const result = truncate('very long text here', 5);
    expect(result).toContain('...');
    expect(result.length).toBe(8); // 5 chars + '...'
  });
});

describe('copyToClipboard', () => {
  it('should call navigator.clipboard.writeText', async () => {
    const text = 'test text';
    // Ensure clipboard is mocked
    const writeTextMock = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, 'clipboard', {
      writable: true,
      configurable: true,
      value: {
        writeText: writeTextMock,
      },
    });
    
    await copyToClipboard(text);
    expect(writeTextMock).toHaveBeenCalledWith(text);
  });
});

describe('dollarsToCents', () => {
  it('should convert dollars to cents', () => {
    expect(dollarsToCents(10)).toBe(1000);
    expect(dollarsToCents(10.50)).toBe(1050);
    expect(dollarsToCents(0.01)).toBe(1);
  });

  it('should round to nearest cent', () => {
    expect(dollarsToCents(10.999)).toBe(1100);
    expect(dollarsToCents(10.001)).toBe(1000);
  });
});

describe('centsToDollars', () => {
  it('should convert cents to dollars', () => {
    expect(centsToDollars(1000)).toBe(10);
    expect(centsToDollars(1050)).toBe(10.5);
    expect(centsToDollars(1)).toBe(0.01);
  });
});

describe('validateEthAddress', () => {
  it('should validate correct Ethereum addresses', () => {
    // Valid 42-character addresses (0x + 40 hex chars)
    expect(validateEthAddress('0x742d35Cc6634C0532925a3b844Bc9e7595f0bEbb')).toBe(true); // Valid 42-char address
    expect(validateEthAddress('0x' + 'a'.repeat(40))).toBe(true);
    expect(validateEthAddress('0x' + 'A'.repeat(40))).toBe(true);
    expect(validateEthAddress('0x' + '1'.repeat(40))).toBe(true);
    expect(validateEthAddress('0x' + 'f'.repeat(40))).toBe(true);
    expect(validateEthAddress('0x' + '0'.repeat(40))).toBe(true);
  });

  it('should reject invalid Ethereum addresses', () => {
    expect(validateEthAddress('0x742d35Cc6634C0532925a3b844Bc9e7595f0bE')).toBe(false); // Too short (41 chars total, 39 hex)
    expect(validateEthAddress('742d35Cc6634C0532925a3b844Bc9e7595f0bEb')).toBe(false); // Missing 0x
    expect(validateEthAddress('0x742d35Cc6634C0532925a3b844Bc9e7595f0bEbbb')).toBe(false); // Too long (43 chars)
    expect(validateEthAddress('0x742d35Cc6634C0532925a3b844Bc9e7595f0bGz')).toBe(false); // Invalid chars G and z (also wrong length)
    expect(validateEthAddress('0x742d35Cc6634C0532925a3b844Bc9e7595f0bG')).toBe(false); // Invalid char G, also too short
    expect(validateEthAddress('')).toBe(false);
  });
});

describe('validateBtcAddress', () => {
  it('should validate correct Bitcoin addresses', () => {
    // Legacy address
    expect(validateBtcAddress('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')).toBe(true);
    // Bech32 address
    expect(validateBtcAddress('bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4')).toBe(true);
  });

  it('should reject invalid Bitcoin addresses', () => {
    expect(validateBtcAddress('')).toBe(false);
    expect(validateBtcAddress('too-short')).toBe(false);
    expect(validateBtcAddress('a'.repeat(100))).toBe(false); // Too long
    expect(validateBtcAddress('invalid-address')).toBe(false);
  });
});

describe('validateSolAddress', () => {
  it('should validate correct Solana addresses', () => {
    expect(validateSolAddress('7EcDhSYGxXyscszYEp35KHN8vvw3svAuLKTzXwCFLtV')).toBe(true);
    expect(validateSolAddress('So11111111111111111111111111111111111111112')).toBe(true); // SOL token
  });

  it('should reject invalid Solana addresses', () => {
    expect(validateSolAddress('')).toBe(false);
    expect(validateSolAddress('0x742d35Cc6634C0532925a3b844Bc9e7595f0bEbb')).toBe(false); // ETH address
    expect(validateSolAddress('invalid')).toBe(false);
  });
});
