/**
 * CLI integration tests — spawns each script and validates output.
 * Tests --help, input validation errors, and (where safe) live queries.
 */
import { describe, it, expect } from 'vitest';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import path from 'node:path';

const execFileP = promisify(execFile);
const SCRIPTS = path.resolve(import.meta.dirname, '..', 'scripts');
const TSX = path.resolve(import.meta.dirname, '..', 'node_modules', '.bin', 'tsx');

async function run(script: string, args: string[] = []): Promise<{ stdout: string; stderr: string; code: number }> {
  try {
    const { stdout, stderr } = await execFileP(TSX, [path.join(SCRIPTS, script), ...args], {
      timeout: 15000,
      env: { ...process.env, SAFE_SIGNER_PRIVATE_KEY: undefined, SAFE_TX_SERVICE_API_KEY: undefined }
    });
    return { stdout, stderr, code: 0 };
  } catch (err: any) {
    return { stdout: err.stdout ?? '', stderr: err.stderr ?? '', code: err.code === 'ERR_CHILD_PROCESS_STDIO_FINAL_CLOSE' ? 1 : (err.code ?? 1) };
  }
}

// ── safe-info.ts ──

describe('safe-info CLI', () => {
  it('--help exits cleanly', async () => {
    const r = await run('safe-info.ts', ['--help']);
    expect(r.stdout).toContain('safe-info');
  });

  it('errors without --safe', async () => {
    const r = await run('safe-info.ts', ['--chain', 'base']);
    expect(r.code).not.toBe(0);
    expect(r.stderr).toContain('--safe');
  });

  it('errors with invalid address', async () => {
    const r = await run('safe-info.ts', ['--chain', 'base', '--safe', '0xBAD']);
    expect(r.code).not.toBe(0);
    expect(r.stderr).toContain('Invalid');
  });

  it('errors with unknown chain', async () => {
    const r = await run('safe-info.ts', ['--chain', 'fakenet', '--safe', '0x' + '00'.repeat(20)]);
    expect(r.code).not.toBe(0);
    expect(r.stderr).toContain('Unknown chain slug');
  });
});

// ── list-pending.ts ──

describe('list-pending CLI', () => {
  it('--help exits cleanly', async () => {
    const r = await run('list-pending.ts', ['--help']);
    expect(r.stdout).toContain('list-pending');
  });

  it('errors without --safe', async () => {
    const r = await run('list-pending.ts', ['--chain', 'base']);
    expect(r.code).not.toBe(0);
    expect(r.stderr).toContain('--safe');
  });

  it('errors with invalid address', async () => {
    const r = await run('list-pending.ts', ['--chain', 'base', '--safe', 'not-an-addr']);
    expect(r.code).not.toBe(0);
    expect(r.stderr).toContain('Invalid');
  });
});

// ── safe_txs_list.ts ──

describe('safe_txs_list CLI', () => {
  it('--help exits cleanly', async () => {
    const r = await run('safe_txs_list.ts', ['--help']);
    expect(r.stdout).toContain('List multisig');
  });

  it('errors without --safe', async () => {
    const r = await run('safe_txs_list.ts', ['--chain', 'base']);
    expect(r.code).not.toBe(0);
  });
});

// ── propose-tx.ts ──

describe('propose-tx CLI', () => {
  it('--help exits cleanly', async () => {
    const r = await run('propose-tx.ts', ['--help']);
    expect(r.stdout).toContain('propose-tx');
  });

  it('errors without --tx-file', async () => {
    const r = await run('propose-tx.ts', ['--chain', 'base']);
    expect(r.code).not.toBe(0);
    expect(r.stderr).toContain('--tx-file');
  });

  it('errors when private key is missing', async () => {
    const r = await run('propose-tx.ts', ['--chain', 'base', '--tx-file', '/tmp/nonexistent.json']);
    expect(r.code).not.toBe(0);
    expect(r.stderr).toContain('SAFE_SIGNER_PRIVATE_KEY');
  });
});

// ── approve-tx.ts ──

describe('approve-tx CLI', () => {
  it('--help exits cleanly', async () => {
    const r = await run('approve-tx.ts', ['--help']);
    expect(r.stdout).toContain('approve-tx');
  });

  it('errors without --safe', async () => {
    const r = await run('approve-tx.ts', ['--chain', 'base', '--safe-tx-hash', '0x' + 'aa'.repeat(32)]);
    expect(r.code).not.toBe(0);
    expect(r.stderr).toContain('--safe');
  });

  it('errors without --safe-tx-hash', async () => {
    const r = await run('approve-tx.ts', ['--chain', 'base', '--safe', '0x' + '00'.repeat(20)]);
    expect(r.code).not.toBe(0);
    expect(r.stderr).toContain('--safe-tx-hash');
  });
});

// ── execute-tx.ts ──

describe('execute-tx CLI', () => {
  it('--help exits cleanly', async () => {
    const r = await run('execute-tx.ts', ['--help']);
    expect(r.stdout).toContain('execute-tx');
  });

  it('errors without --safe', async () => {
    const r = await run('execute-tx.ts', ['--chain', 'base', '--safe-tx-hash', '0x' + 'bb'.repeat(32)]);
    expect(r.code).not.toBe(0);
    expect(r.stderr).toContain('--safe');
  });

  it('errors without --safe-tx-hash', async () => {
    const r = await run('execute-tx.ts', ['--chain', 'base', '--safe', '0x' + '00'.repeat(20)]);
    expect(r.code).not.toBe(0);
    expect(r.stderr).toContain('--safe-tx-hash');
  });
});

// ── create-safe.ts ──

describe('create-safe CLI', () => {
  it('--help exits cleanly', async () => {
    const r = await run('create-safe.ts', ['--help']);
    expect(r.stdout).toContain('create-safe');
  });

  it('errors without --owners', async () => {
    const r = await run('create-safe.ts', ['--chain', 'base', '--threshold', '1']);
    expect(r.code).not.toBe(0);
    expect(r.stderr).toContain('--owners');
  });

  it('errors without --threshold', async () => {
    const r = await run('create-safe.ts', ['--chain', 'base', '--owners', '0x' + '11'.repeat(20)]);
    expect(r.code).not.toBe(0);
    expect(r.stderr).toContain('--threshold');
  });

  it('errors with invalid owner address', async () => {
    const r = await run('create-safe.ts', ['--chain', 'base', '--owners', '0xBAD', '--threshold', '1']);
    expect(r.code).not.toBe(0);
    expect(r.stderr).toContain('Invalid');
  });

  it('errors when threshold exceeds owner count', async () => {
    const r = await run('create-safe.ts', ['--chain', 'base', '--owners', '0x' + '11'.repeat(20), '--threshold', '3']);
    expect(r.code).not.toBe(0);
    expect(r.stderr).toContain('cannot exceed');
  });

  it('errors with unknown chain', async () => {
    const r = await run('create-safe.ts', ['--chain', 'fakenet', '--owners', '0x' + '11'.repeat(20), '--threshold', '1']);
    expect(r.code).not.toBe(0);
    expect(r.stderr).toContain('Unknown chain slug');
  });
});
