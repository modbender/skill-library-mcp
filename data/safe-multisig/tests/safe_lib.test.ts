/**
 * Unit tests for safe_lib.ts — covers all exported helpers.
 */
import { describe, it, expect, vi, afterEach } from 'vitest';
import {
  resolveTxServiceUrl,
  resolveChainId,
  resolveRpcUrl,
  requirePrivateKey,
  validateAddress,
  validateTxHash,
  validateApiKey,
  fetchJson,
  createCommand,
  addCommonOptions
} from '../scripts/safe_lib.js';

// ── resolveTxServiceUrl ──

describe('resolveTxServiceUrl', () => {
  it('returns correct URL for base', () => {
    expect(resolveTxServiceUrl({ chain: 'base' })).toBe(
      'https://api.safe.global/tx-service/base/api'
    );
  });

  it('returns correct URL for mainnet', () => {
    expect(resolveTxServiceUrl({ chain: 'mainnet' })).toBe(
      'https://api.safe.global/tx-service/eth/api'
    );
  });

  it('returns correct URL for ethereum alias', () => {
    expect(resolveTxServiceUrl({ chain: 'ethereum' })).toBe(
      'https://api.safe.global/tx-service/eth/api'
    );
  });

  it('returns correct URL for optimism', () => {
    expect(resolveTxServiceUrl({ chain: 'optimism' })).toBe(
      'https://api.safe.global/tx-service/oeth/api'
    );
  });

  it('returns correct URL for arbitrum', () => {
    expect(resolveTxServiceUrl({ chain: 'arbitrum' })).toBe(
      'https://api.safe.global/tx-service/arb1/api'
    );
  });

  it('returns correct URL for base-sepolia', () => {
    expect(resolveTxServiceUrl({ chain: 'base-sepolia' })).toBe(
      'https://api.safe.global/tx-service/basesep/api'
    );
  });

  it('returns correct URL for polygon', () => {
    expect(resolveTxServiceUrl({ chain: 'polygon' })).toBe(
      'https://api.safe.global/tx-service/pol/api'
    );
  });

  it('is case-insensitive', () => {
    expect(resolveTxServiceUrl({ chain: 'Base' })).toBe(
      'https://api.safe.global/tx-service/base/api'
    );
  });

  it('uses txServiceUrl override when provided', () => {
    expect(resolveTxServiceUrl({ txServiceUrl: 'https://custom.safe/api' })).toBe(
      'https://custom.safe/api'
    );
  });

  it('strips trailing slash from txServiceUrl', () => {
    expect(resolveTxServiceUrl({ txServiceUrl: 'https://custom.safe/api/' })).toBe(
      'https://custom.safe/api'
    );
  });

  it('throws for unknown chain slug', () => {
    expect(() => resolveTxServiceUrl({ chain: 'fakenet' })).toThrow('Unknown chain slug');
  });

  it('throws when neither chain nor txServiceUrl is set', () => {
    expect(() => resolveTxServiceUrl({})).toThrow('Missing --chain or --tx-service-url');
  });
});

// ── resolveChainId ──

describe('resolveChainId', () => {
  it('returns 8453n for base', () => {
    expect(resolveChainId({ chain: 'base' })).toBe(8453n);
  });

  it('returns 1n for mainnet', () => {
    expect(resolveChainId({ chain: 'mainnet' })).toBe(1n);
  });

  it('returns 1n for ethereum alias', () => {
    expect(resolveChainId({ chain: 'ethereum' })).toBe(1n);
  });

  it('returns 10n for optimism', () => {
    expect(resolveChainId({ chain: 'optimism' })).toBe(10n);
  });

  it('returns 42161n for arbitrum', () => {
    expect(resolveChainId({ chain: 'arbitrum' })).toBe(42161n);
  });

  it('returns 84532n for base-sepolia', () => {
    expect(resolveChainId({ chain: 'base-sepolia' })).toBe(84532n);
  });

  it('throws for unknown chain', () => {
    expect(() => resolveChainId({ chain: 'mars' })).toThrow('Unknown chain slug');
  });

  it('throws when chain is missing', () => {
    expect(() => resolveChainId({})).toThrow('Missing --chain');
  });
});

// ── resolveRpcUrl ──

describe('resolveRpcUrl', () => {
  const originalEnv = process.env.RPC_URL;
  afterEach(() => {
    if (originalEnv !== undefined) process.env.RPC_URL = originalEnv;
    else delete process.env.RPC_URL;
  });

  it('returns explicit rpcUrl when provided', () => {
    expect(resolveRpcUrl({ rpcUrl: 'https://my-rpc.com' })).toBe('https://my-rpc.com');
  });

  it('falls back to RPC_URL env var', () => {
    process.env.RPC_URL = 'https://env-rpc.com';
    expect(resolveRpcUrl({})).toBe('https://env-rpc.com');
  });

  it('uses default RPC for known chain', () => {
    delete process.env.RPC_URL;
    const url = resolveRpcUrl({ chain: 'base' });
    expect(url).toBe('https://mainnet.base.org');
  });

  it('throws when nothing is available', () => {
    delete process.env.RPC_URL;
    expect(() => resolveRpcUrl({})).toThrow('Missing --rpc-url');
  });
});

// ── requirePrivateKey ──

describe('requirePrivateKey', () => {
  const originalPk = process.env.SAFE_SIGNER_PRIVATE_KEY;
  afterEach(() => {
    if (originalPk !== undefined) process.env.SAFE_SIGNER_PRIVATE_KEY = originalPk;
    else delete process.env.SAFE_SIGNER_PRIVATE_KEY;
  });

  it('returns key with 0x prefix', () => {
    process.env.SAFE_SIGNER_PRIVATE_KEY = '0x' + 'ab'.repeat(32);
    expect(requirePrivateKey()).toBe('0x' + 'ab'.repeat(32));
  });

  it('adds 0x prefix when missing', () => {
    process.env.SAFE_SIGNER_PRIVATE_KEY = 'cd'.repeat(32);
    expect(requirePrivateKey()).toBe('0x' + 'cd'.repeat(32));
  });

  it('throws when env var is missing', () => {
    delete process.env.SAFE_SIGNER_PRIVATE_KEY;
    expect(() => requirePrivateKey()).toThrow('Missing SAFE_SIGNER_PRIVATE_KEY');
  });
});

// ── validateAddress ──

describe('validateAddress', () => {
  it('accepts valid checksummed address', () => {
    expect(() => validateAddress('0xA7940a42c30A7F492Ed578F3aC728c2929103E43', 'safe')).not.toThrow();
  });

  it('accepts valid lowercase address', () => {
    expect(() => validateAddress('0x0000000000000000000000000000000000000000', 'safe')).not.toThrow();
  });

  it('rejects too-short address', () => {
    expect(() => validateAddress('0x1234', 'safe')).toThrow('Invalid safe address');
  });

  it('rejects non-hex address', () => {
    expect(() => validateAddress('0xGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG', 'safe')).toThrow();
  });

  it('rejects random string without hex', () => {
    expect(() => validateAddress('hello-world-not-an-address', 'safe')).toThrow();
  });

  it('rejects empty string', () => {
    expect(() => validateAddress('', 'safe')).toThrow();
  });
});

// ── validateTxHash ──

describe('validateTxHash', () => {
  it('accepts valid 32-byte hex hash', () => {
    const hash = '0x' + 'aa'.repeat(32);
    expect(() => validateTxHash(hash)).not.toThrow();
  });

  it('rejects short hex', () => {
    expect(() => validateTxHash('0x1234')).toThrow('Invalid safeTxHash');
  });

  it('rejects non-hex', () => {
    expect(() => validateTxHash('0x' + 'zz'.repeat(32))).toThrow();
  });

  it('rejects empty string', () => {
    expect(() => validateTxHash('')).toThrow();
  });

  it('uses custom label', () => {
    expect(() => validateTxHash('bad', 'myHash')).toThrow('Invalid myHash');
  });
});

// ── validateApiKey ──

describe('validateApiKey', () => {
  it('warns when no API key for official service', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {});
    validateApiKey({ chain: 'base' });
    expect(spy).toHaveBeenCalledWith(expect.stringContaining('WARNING'));
    spy.mockRestore();
  });

  it('does not warn when API key is provided', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {});
    validateApiKey({ chain: 'base', apiKey: 'test-key' });
    expect(spy).not.toHaveBeenCalled();
    spy.mockRestore();
  });

  it('does not warn for custom tx-service URL', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {});
    validateApiKey({ txServiceUrl: 'https://my-custom-service.com' });
    expect(spy).not.toHaveBeenCalled();
    spy.mockRestore();
  });
});

// ── fetchJson ──

describe('fetchJson', () => {
  it('fetches and parses JSON', async () => {
    const mockData = { ok: true, data: 'test' };
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockData)
    }));

    const result = await fetchJson('https://example.com/api');
    expect(result).toEqual(mockData);

    vi.unstubAllGlobals();
  });

  it('throws on non-ok response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      text: () => Promise.resolve('not found')
    }));

    await expect(fetchJson('https://example.com/missing')).rejects.toThrow('HTTP 404');

    vi.unstubAllGlobals();
  });

  it('respects timeout via AbortController', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation((_url, opts) => {
      return new Promise((_resolve, reject) => {
        if (opts?.signal) {
          opts.signal.addEventListener('abort', () => reject(new Error('aborted')));
        }
      });
    }));

    await expect(fetchJson('https://slow.com', { timeoutMs: 50 })).rejects.toThrow();

    vi.unstubAllGlobals();
  });
});

// ── createCommand ──

describe('createCommand', () => {
  it('creates a Commander instance with name and description', () => {
    const cmd = createCommand('test-cmd', 'A test command');
    expect(cmd.name()).toBe('test-cmd');
    expect(cmd.description()).toBe('A test command');
  });
});

// ── addCommonOptions ──

describe('addCommonOptions', () => {
  it('adds chain, tx-service-url, rpc-url, api-key, debug options', () => {
    const cmd = addCommonOptions(createCommand('test', 'test'));
    const optionNames = cmd.options.map(o => o.long);
    expect(optionNames).toContain('--chain');
    expect(optionNames).toContain('--tx-service-url');
    expect(optionNames).toContain('--rpc-url');
    expect(optionNames).toContain('--api-key');
    expect(optionNames).toContain('--debug');
  });
});
