import { pathToFileURL } from 'node:url';
import { readFile, realpath, stat } from 'node:fs/promises';
import { isAbsolute, relative, resolve } from 'node:path';
import { isAddress } from 'ethers';

import { help, rebalance_now, verify_deployment_config } from '../index.js';
import type { TargetEntryInput } from '../index.js';

function readFlagValue(args: string[], flag: string): string | undefined {
  const index = args.indexOf(flag);
  if (index < 0 || index + 1 >= args.length) {
    return undefined;
  }
  return args[index + 1];
}

function usage(): string {
  return [
    'Usage:',
    '  npm run cli -- help',
    '  npm run cli -- rebalance-now',
    '  npm run cli -- rebalance-now --target-entries \'[{"tokenAddress":"0x...","allocation":0.5},{"tokenAddress":"0x...","allocation":0.5}]\'',
    '  npm run cli -- verify-deployment --troubleshooting-file ./summary.txt',
    '  npm run cli -- verify-deployment --troubleshooting-summary "Safe=0x..."'
  ].join('\n');
}

function validateTargetEntry(entry: unknown, index: number): TargetEntryInput {
  if (typeof entry !== 'object' || entry === null || Array.isArray(entry) || Object.getPrototypeOf(entry) !== Object.prototype) {
    throw new Error(`Invalid --target-entries[${index}]: expected object with tokenAddress/allocation.`);
  }

  const keys = Object.keys(entry as Record<string, unknown>);
  for (const key of keys) {
    if (key !== 'tokenAddress' && key !== 'allocation') {
      throw new Error(`Invalid --target-entries[${index}]: unexpected key ${key}.`);
    }
  }

  const tokenAddress = (entry as Record<string, unknown>).tokenAddress;
  const allocation = (entry as Record<string, unknown>).allocation;

  if (typeof tokenAddress !== 'string' || !isAddress(tokenAddress)) {
    throw new Error(`Invalid --target-entries[${index}].tokenAddress: expected valid EVM address.`);
  }
  if (typeof allocation !== 'number' || !Number.isFinite(allocation) || allocation <= 0 || allocation > 1) {
    throw new Error(`Invalid --target-entries[${index}].allocation: expected number in (0, 1].`);
  }

  return { tokenAddress, allocation };
}

function parseTargetEntries(raw: string): TargetEntryInput[] {
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    throw new Error('Invalid --target-entries: must be valid JSON.');
  }

  if (!Array.isArray(parsed)) {
    throw new Error('Invalid --target-entries: expected JSON array.');
  }

  return parsed.map((entry, index) => validateTargetEntry(entry, index));
}

function isWithinBase(basePath: string, targetPath: string): boolean {
  const rel = relative(basePath, targetPath);
  return rel !== '..' && !rel.startsWith(`..${process.platform === 'win32' ? '\\' : '/'}`) && !isAbsolute(rel);
}

async function readTroubleshootingFile(inputPath: string): Promise<string> {
  const basePath = await realpath(process.cwd());
  const candidatePath = resolve(basePath, inputPath);
  const resolvedPath = await realpath(candidatePath);

  if (!isWithinBase(basePath, resolvedPath)) {
    throw new Error('Invalid --troubleshooting-file: path must stay within the current working directory.');
  }

  const fileStats = await stat(resolvedPath);
  if (!fileStats.isFile()) {
    throw new Error('Invalid --troubleshooting-file: expected a regular file.');
  }
  if (fileStats.size > 128 * 1024) {
    throw new Error('Invalid --troubleshooting-file: file too large (max 128KB).');
  }

  return readFile(resolvedPath, 'utf8');
}

export async function runCli(args: string[], io: Pick<Console, 'log' | 'error'> = console): Promise<number> {
  const command = args[0];

  if (!command || command === 'help') {
    io.log(JSON.stringify(help(), null, 2));
    io.log(usage());
    return 0;
  }

  if (command !== 'rebalance-now' && command !== 'verify-deployment') {
    io.error(`Unknown command: ${command}`);
    io.error(usage());
    return 1;
  }

  try {
    if (command === 'verify-deployment') {
      const troubleshootingSummaryArg = readFlagValue(args, '--troubleshooting-summary');
      const troubleshootingFile = readFlagValue(args, '--troubleshooting-file');
      const executorModuleAddress = readFlagValue(args, '--executor-module-address');
      const rpcUrl = readFlagValue(args, '--rpc-url');

      const troubleshootingSummary = troubleshootingSummaryArg
        ?? (troubleshootingFile ? await readTroubleshootingFile(troubleshootingFile) : undefined);

      if (!troubleshootingSummary) {
        throw new Error('Missing troubleshooting summary. Use --troubleshooting-summary or --troubleshooting-file.');
      }

      const result = await verify_deployment_config({
        troubleshootingSummary,
        executorModuleAddress,
        rpcUrl
      });
      io.log(JSON.stringify(result, null, 2));
      return 0;
    }

    const targetEntriesRaw = readFlagValue(args, '--target-entries');
    const targetEntries = targetEntriesRaw ? parseTargetEntries(targetEntriesRaw) : undefined;
    const result = await rebalance_now({ targetEntries });
    io.log(JSON.stringify(result, null, 2));
    return 0;
  } catch (error) {
    io.error(error instanceof Error ? error.message : String(error));
    return 1;
  }
}

async function main(): Promise<void> {
  process.exitCode = await runCli(process.argv.slice(2));
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  void main();
}
