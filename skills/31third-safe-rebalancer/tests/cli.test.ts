import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { Address } from 'viem';

vi.mock('../index.js', () => ({
  readConfigFromEnv: vi.fn(() => ({
    safeAddress: '0x1000000000000000000000000000000000000001' as Address,
    chainId: 8453,
    rpcUrl: 'https://mainnet.base.org',
    executorModuleAddress: '0x2000000000000000000000000000000000000002' as Address
  })),
  check_drift: vi.fn(async () => ({ shouldRebalance: false })),
  validate_trade: vi.fn(async () => ({ valid: true })),
  automation: vi.fn(async () => ({ checked: true })),
  execute_rebalance: vi.fn(async () => ({ txHash: '0xabc', why: 'ok' })),
  rebalance_now: vi.fn(async () => ({ executed: true, skipped: false, reason: 'ok', txHash: '0xabc' })),
  plan_rebalance: vi.fn(async () => ({ why: 'planned', response: { ok: true } })),
  help: vi.fn(() => ({ summary: 'help summary' }))
}));

import { runCli, type CliIO } from '../scripts/cli.js';
import { execute_rebalance, help, rebalance_now, validate_trade } from '../index.js';

describe('cli', () => {
  let io: CliIO;
  let logSpy: ReturnType<typeof vi.fn>;
  let errorSpy: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    logSpy = vi.fn();
    errorSpy = vi.fn();
    io = { log: logSpy, error: errorSpy };
    vi.clearAllMocks();
  });

  it('prints help output', async () => {
    const code = await runCli(['help'], io);
    expect(code).toBe(0);
    expect(help).toHaveBeenCalledTimes(1);
    expect(logSpy).toHaveBeenCalledTimes(1);
    expect(String(logSpy.mock.calls[0][0])).toContain('help summary');
  });

  it('parses validate-trade bigints from JSON strings', async () => {
    const code = await runCli([
      'validate-trade',
      '--trade',
      '{"from":"0x3000000000000000000000000000000000000003","to":"0x4000000000000000000000000000000000000004","fromAmount":"1000","minToReceiveBeforeFees":"900"}'
    ], io);

    expect(code).toBe(0);
    expect(validate_trade).toHaveBeenCalledTimes(1);
    const params = (validate_trade as any).mock.calls[0][0];
    expect(params.trade.fromAmount).toBe(1000n);
    expect(params.trade.minToReceiveBeforeFees).toBe(900n);
  });

  it('parses execute-rebalance arrays and bigint fields', async () => {
    const code = await runCli([
      'execute-rebalance',
      '--trades',
      '[{"exchangeName":"x","from":"0x3000000000000000000000000000000000000003","fromAmount":"10","to":"0x4000000000000000000000000000000000000004","minToReceiveBeforeFees":"9","data":"0x12","signature":"0x34"}]',
      '--approvals',
      '[{"token":"0x3000000000000000000000000000000000000003","amount":"10"}]'
    ], io);

    expect(code).toBe(0);
    expect(execute_rebalance).toHaveBeenCalledTimes(1);
    const params = (execute_rebalance as any).mock.calls[0][0];
    expect(params.trades[0].fromAmount).toBe(10n);
    expect(params.approvals[0].amount).toBe(10n);
  });

  it('passes sdk rebalancing payload through execute-rebalance --rebalancing', async () => {
    const code = await runCli([
      'execute-rebalance',
      '--rebalancing',
      '{"txData":"0x1234","requiredAllowances":[{"token":{"address":"0x3000000000000000000000000000000000000003"},"neededAllowance":"10"}]}'
    ], io);

    expect(code).toBe(0);
    expect(execute_rebalance).toHaveBeenCalledTimes(1);
    const params = (execute_rebalance as any).mock.calls[0][0];
    expect(params.rebalancing.txData).toBe('0x1234');
  });

  it('runs rebalance-now one-command flow', async () => {
    const code = await runCli(['rebalance-now', '--force'], io);
    expect(code).toBe(0);
    expect(rebalance_now).toHaveBeenCalledTimes(1);
    const params = (rebalance_now as any).mock.calls[0][0];
    expect(params.force).toBe(true);
  });

  it('returns non-zero and usage for empty args', async () => {
    const code = await runCli([], io);
    expect(code).toBe(1);
    expect(errorSpy).toHaveBeenCalled();
    expect(String(errorSpy.mock.calls[0][0])).toContain('Usage');
  });

  it('returns non-zero for unknown command', async () => {
    const code = await runCli(['unknown-command'], io);
    expect(code).toBe(1);
    expect(errorSpy).toHaveBeenCalled();
    expect(String(errorSpy.mock.calls[0][0])).toContain('Unknown command');
  });
});
