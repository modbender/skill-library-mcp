import { Contract, JsonRpcProvider, isAddress } from 'ethers';

import {
  assetUniversePolicyAbi,
  executorModuleAbi,
  slippagePolicyAbi,
  staticAllocationPolicyAbi
} from './contracts.js';

export type VerificationStatus = 'match' | 'mismatch' | 'missing';

export interface VerificationCheck {
  field: string;
  status: VerificationStatus;
  envValue?: string;
  summaryValue?: string;
  chainValue?: string;
  detail: string;
}

export interface VerifyDeploymentResult {
  ok: boolean;
  executorModuleAddress: string;
  rpcUrl: string;
  checks: VerificationCheck[];
  mismatches: string[];
  warnings: string[];
  message: string;
}

interface ParsedTroubleshootingSummary {
  safeAddress?: string;
  executorModuleAddress?: string;
  scheduler?: string;
  registry?: string;
  batchTrade?: string;
  feedRegistry?: string;
  cooldownSec?: number;
  assetUniversePolicy?: string;
  assetUniverseAssets: string[];
  staticAllocationPolicy?: string;
  staticAllocationDriftThresholdPercent?: number;
  staticAllocationToleranceThresholdPercent?: number;
  staticAllocationTargets: Array<{ tokenAddress: string; allocationPercent: number }>;
  slippagePolicy?: string;
  maxSlippagePercent?: number;
}

interface DeploymentEnvSnapshot {
  safeAddress?: string;
  executorModuleAddress?: string;
}

interface OnChainDeploymentSnapshot {
  safeAddress: string;
  executorModuleAddress: string;
  scheduler: string;
  registry: string;
  batchTrade: string;
  cooldownSec: number;
  assetUniversePolicy?: string;
  assetUniverseAssets: string[];
  staticAllocationPolicy?: string;
  staticAllocationDriftThresholdPercent?: number;
  staticAllocationToleranceThresholdPercent?: number;
  staticAllocationTargets: Array<{ tokenAddress: string; allocationPercent: number }>;
  staticFeedRegistry?: string;
  slippagePolicy?: string;
  maxSlippagePercent?: number;
  slippageFeedRegistry?: string;
}

interface VerifyDeploymentDeps {
  fetchOnChainDeploymentFn?: (executorModuleAddress: string, rpcUrl: string) => Promise<OnChainDeploymentSnapshot>;
}

function readFirstEnv(names: string[]): string | undefined {
  for (const name of names) {
    const value = process.env[name];
    if (value && value.trim()) {
      return value.trim();
    }
  }
  return undefined;
}

function readEnvAddress(names: string[]): string | undefined {
  const value = readFirstEnv(names);
  if (!value) return undefined;
  return isAddress(value) ? value : undefined;
}

function parsePercent(value: string): number | undefined {
  const normalized = value.replace('%', '').trim();
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : undefined;
}

function readDeploymentEnvSnapshot(): DeploymentEnvSnapshot {
  return {
    safeAddress: readEnvAddress(['SAFE_ADDRESS']),
    executorModuleAddress: readEnvAddress(['EXECUTOR_MODULE_ADDRESS'])
  };
}

function firstAddressInText(value: string): string | undefined {
  const match = value.match(/0x[a-fA-F0-9]{40}/);
  if (!match) return undefined;
  return isAddress(match[0]) ? match[0] : undefined;
}

function parseTroubleshootingSummary(input: string): ParsedTroubleshootingSummary {
  const parsed: ParsedTroubleshootingSummary = {
    assetUniverseAssets: [],
    staticAllocationTargets: []
  };

  let section: 'asset-universe-assets' | 'static-allocation-targets' | null = null;
  const lines = input
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  for (const line of lines) {
    if (line === 'AssetUniverseAssets:') {
      section = 'asset-universe-assets';
      continue;
    }
    if (line === 'StaticAllocationTargets:') {
      section = 'static-allocation-targets';
      continue;
    }

    if (line.startsWith('- ')) {
      const item = line.slice(2).trim();
      if (section === 'asset-universe-assets') {
        const address = firstAddressInText(item);
        if (address) {
          parsed.assetUniverseAssets.push(address);
        }
      } else if (section === 'static-allocation-targets') {
        const address = firstAddressInText(item);
        const allocationMatch = item.match(/AllocationPercent\s*=\s*([0-9]*\.?[0-9]+)%/i);
        const allocationPercent = allocationMatch ? Number(allocationMatch[1]) : undefined;
        if (address && typeof allocationPercent === 'number' && Number.isFinite(allocationPercent)) {
          parsed.staticAllocationTargets.push({ tokenAddress: address, allocationPercent });
        }
      }
      continue;
    }

    section = null;
    const separator = line.indexOf('=');
    if (separator <= 0) continue;

    const key = line.slice(0, separator).trim();
    const rawValue = line.slice(separator + 1).trim();
    const address = firstAddressInText(rawValue);

    if (key === 'Safe') parsed.safeAddress = address;
    if (key === 'ExecutorModule') parsed.executorModuleAddress = address;
    if (key === 'Scheduler') parsed.scheduler = address;
    if (key === 'Registry') parsed.registry = address;
    if (key === 'BatchTrade') parsed.batchTrade = address;
    if (key === 'FeedRegistry') parsed.feedRegistry = address;
    if (key === 'AssetUniversePolicy') parsed.assetUniversePolicy = address;
    if (key === 'StaticAllocationPolicy') parsed.staticAllocationPolicy = address;
    if (key === 'SlippagePolicy') parsed.slippagePolicy = address;

    if (key === 'CooldownSec') {
      const n = Number(rawValue.replace(/[^0-9.]/g, ''));
      if (Number.isFinite(n)) parsed.cooldownSec = n;
    }
    if (key === 'StaticAllocationDriftThresholdPercent') {
      const n = parsePercent(rawValue);
      if (typeof n === 'number') parsed.staticAllocationDriftThresholdPercent = n;
    }
    if (key === 'StaticAllocationToleranceThresholdPercent') {
      const n = parsePercent(rawValue);
      if (typeof n === 'number') parsed.staticAllocationToleranceThresholdPercent = n;
    }
    if (key === 'MaxSlippagePercent') {
      const n = parsePercent(rawValue);
      if (typeof n === 'number') parsed.maxSlippagePercent = n;
    }
  }

  return parsed;
}

function normalizePolicyState(entry: any): { policy: string; policyType: string } {
  const policy = entry?.policy ?? (Array.isArray(entry) ? entry[0] : undefined);
  const policyType = entry?.policyType ?? (Array.isArray(entry) ? entry[1] : undefined);
  return {
    policy: typeof policy === 'string' ? policy : '',
    policyType: typeof policyType === 'string' ? policyType : ''
  };
}

function normalizePolicyType(value: string): string {
  return value.toLowerCase().replace(/[^a-z]/g, '');
}

function bpsToPercent(bps: number): number {
  return bps / 100;
}

async function defaultFetchOnChainDeployment(
  executorModuleAddress: string,
  rpcUrl: string
): Promise<OnChainDeploymentSnapshot> {
  const provider = new JsonRpcProvider(rpcUrl);
  const executor = new Contract(executorModuleAddress, executorModuleAbi, provider);

  const [safeAddress, scheduler, registry, batchTrade, cooldownRaw, policiesRaw] = await Promise.all([
    executor.safe() as Promise<string>,
    executor.scheduler() as Promise<string>,
    executor.registry() as Promise<string>,
    executor.batchTrade() as Promise<string>,
    executor.cooldown() as Promise<bigint>,
    executor.getPoliciesWithTypes() as Promise<any[]>
  ]);

  const policies = (policiesRaw as any[]).map(normalizePolicyState);
  const policiesByType = new Map<string, string>();
  for (const policy of policies) {
    const key = normalizePolicyType(policy.policyType);
    if (key && policy.policy && isAddress(policy.policy)) {
      policiesByType.set(key, policy.policy);
    }
  }

  const assetUniversePolicy = policiesByType.get('assetuniverse');
  const staticAllocationPolicy = policiesByType.get('staticallocation');
  const slippagePolicy = policiesByType.get('slippage');

  let assetUniverseAssets: string[] = [];
  if (assetUniversePolicy) {
    const assetUniverse = new Contract(assetUniversePolicy, assetUniversePolicyAbi, provider);
    assetUniverseAssets = await assetUniverse.getTokens() as string[];
  }

  let staticAllocationDriftThresholdPercent: number | undefined;
  let staticAllocationToleranceThresholdPercent: number | undefined;
  let staticAllocationTargets: Array<{ tokenAddress: string; allocationPercent: number }> = [];
  let staticFeedRegistry: string | undefined;
  if (staticAllocationPolicy) {
    const staticAllocation = new Contract(staticAllocationPolicy, staticAllocationPolicyAbi, provider);
    const [driftThresholdBpsRaw, toleranceThresholdBpsRaw, targetsRaw, feedRegistry] = await Promise.all([
      staticAllocation.driftThresholdBps() as Promise<bigint>,
      staticAllocation.toleranceThresholdBps() as Promise<bigint>,
      staticAllocation.getAllTargets() as Promise<any[]>,
      staticAllocation.feedRegistry() as Promise<string>
    ]);

    staticAllocationDriftThresholdPercent = bpsToPercent(Number(driftThresholdBpsRaw));
    staticAllocationToleranceThresholdPercent = bpsToPercent(Number(toleranceThresholdBpsRaw));
    staticFeedRegistry = feedRegistry;
    staticAllocationTargets = targetsRaw.map((target) => {
      const tokenAddress = target?.token ?? (Array.isArray(target) ? target[0] : undefined);
      const bps = target?.bps ?? (Array.isArray(target) ? target[1] : undefined);
      if (typeof tokenAddress !== 'string' || typeof bps === 'undefined') {
        throw new Error('Invalid target entry on StaticAllocation policy.');
      }
      return {
        tokenAddress,
        allocationPercent: bpsToPercent(Number(bps))
      };
    });
  }

  let maxSlippagePercent: number | undefined;
  let slippageFeedRegistry: string | undefined;
  if (slippagePolicy) {
    const slippage = new Contract(slippagePolicy, slippagePolicyAbi, provider);
    const [maxSlippageBpsRaw, feedRegistry] = await Promise.all([
      slippage.maxSlippageBps() as Promise<bigint>,
      slippage.feedRegistry() as Promise<string>
    ]);
    maxSlippagePercent = bpsToPercent(Number(maxSlippageBpsRaw));
    slippageFeedRegistry = feedRegistry;
  }

  return {
    safeAddress,
    executorModuleAddress,
    scheduler,
    registry,
    batchTrade,
    cooldownSec: Number(cooldownRaw),
    assetUniversePolicy,
    assetUniverseAssets,
    staticAllocationPolicy,
    staticAllocationDriftThresholdPercent,
    staticAllocationToleranceThresholdPercent,
    staticAllocationTargets,
    staticFeedRegistry,
    slippagePolicy,
    maxSlippagePercent,
    slippageFeedRegistry
  };
}

function formatPercent(value: number): string {
  return `${value.toFixed(2)}%`;
}

function formatAddressList(value: string[]): string {
  return value.join(', ');
}

function formatTargets(value: Array<{ tokenAddress: string; allocationPercent: number }>): string {
  return value
    .map((entry) => `${entry.tokenAddress}:${formatPercent(entry.allocationPercent)}`)
    .join(', ');
}

function addressesEqual(a: string, b: string): boolean {
  return a.toLowerCase() === b.toLowerCase();
}

function numbersEqual(a: number, b: number): boolean {
  return Math.abs(a - b) < 1e-9;
}

function addressListsEqual(a: string[], b: string[]): boolean {
  if (a.length !== b.length) return false;
  const normalizedA = a.map((x) => x.toLowerCase()).sort();
  const normalizedB = b.map((x) => x.toLowerCase()).sort();
  return normalizedA.every((value, index) => value === normalizedB[index]);
}

function targetsEqual(
  a: Array<{ tokenAddress: string; allocationPercent: number }>,
  b: Array<{ tokenAddress: string; allocationPercent: number }>
): boolean {
  if (a.length !== b.length) return false;
  const mapA = new Map(a.map((entry) => [entry.tokenAddress.toLowerCase(), entry.allocationPercent]));
  const mapB = new Map(b.map((entry) => [entry.tokenAddress.toLowerCase(), entry.allocationPercent]));
  if (mapA.size !== mapB.size) return false;
  for (const [token, allocation] of mapA.entries()) {
    const other = mapB.get(token);
    if (typeof other !== 'number' || !numbersEqual(allocation, other)) {
      return false;
    }
  }
  return true;
}

function buildCheck<T>(params: {
  field: string;
  envValue?: T;
  summaryValue?: T;
  chainValue?: T;
  equals: (a: T, b: T) => boolean;
  format: (value: T) => string;
}): VerificationCheck {
  const values: Array<{ source: 'env' | 'summary' | 'chain'; value: T }> = [];
  if (typeof params.envValue !== 'undefined') values.push({ source: 'env', value: params.envValue });
  if (typeof params.summaryValue !== 'undefined') values.push({ source: 'summary', value: params.summaryValue });
  if (typeof params.chainValue !== 'undefined') values.push({ source: 'chain', value: params.chainValue });

  const check: VerificationCheck = {
    field: params.field,
    status: 'missing',
    detail: ''
  };
  if (typeof params.envValue !== 'undefined') check.envValue = params.format(params.envValue);
  if (typeof params.summaryValue !== 'undefined') check.summaryValue = params.format(params.summaryValue);
  if (typeof params.chainValue !== 'undefined') check.chainValue = params.format(params.chainValue);

  if (values.length < 2) {
    check.status = 'missing';
    check.detail = 'Insufficient data to compare across sources.';
    return check;
  }

  const anchor = values[0].value;
  const mismatch = values.some((entry) => !params.equals(anchor, entry.value));
  if (mismatch) {
    check.status = 'mismatch';
    check.detail = values.map((entry) => `${entry.source}=${params.format(entry.value)}`).join(' | ');
    return check;
  }

  check.status = 'match';
  check.detail = values.map((entry) => `${entry.source} matches`).join(', ');
  return check;
}

export async function verify_deployment_config(params: {
  troubleshootingSummary: string;
  executorModuleAddress?: string;
  rpcUrl?: string;
  deps?: VerifyDeploymentDeps;
}): Promise<VerifyDeploymentResult> {
  const envSnapshot = readDeploymentEnvSnapshot();
  const summary = parseTroubleshootingSummary(params.troubleshootingSummary);
  const executorModuleAddress =
    params.executorModuleAddress ?? envSnapshot.executorModuleAddress ?? summary.executorModuleAddress;

  if (!executorModuleAddress || !isAddress(executorModuleAddress)) {
    throw new Error(
      'Unable to resolve ExecutorModule address. Provide params.executorModuleAddress, set EXECUTOR_MODULE_ADDRESS, or include ExecutorModule in troubleshootingSummary.'
    );
  }

  const rpcUrl = params.rpcUrl ?? process.env.RPC_URL ?? 'https://mainnet.base.org';
  const fetchOnChainDeploymentFn = params.deps?.fetchOnChainDeploymentFn ?? defaultFetchOnChainDeployment;
  const chain = await fetchOnChainDeploymentFn(executorModuleAddress, rpcUrl);

  const chainFeedRegistry = chain.staticFeedRegistry ?? chain.slippageFeedRegistry;
  const checks: VerificationCheck[] = [
    buildCheck({
      field: 'Safe',
      envValue: envSnapshot.safeAddress,
      summaryValue: summary.safeAddress,
      chainValue: chain.safeAddress,
      equals: addressesEqual,
      format: (value) => value
    }),
    buildCheck({
      field: 'ExecutorModule',
      envValue: envSnapshot.executorModuleAddress,
      summaryValue: summary.executorModuleAddress,
      chainValue: chain.executorModuleAddress,
      equals: addressesEqual,
      format: (value) => value
    }),
    buildCheck({
      field: 'Scheduler',
      summaryValue: summary.scheduler,
      chainValue: chain.scheduler,
      equals: addressesEqual,
      format: (value) => value
    }),
    buildCheck({
      field: 'Registry',
      summaryValue: summary.registry,
      chainValue: chain.registry,
      equals: addressesEqual,
      format: (value) => value
    }),
    buildCheck({
      field: 'BatchTrade',
      summaryValue: summary.batchTrade,
      chainValue: chain.batchTrade,
      equals: addressesEqual,
      format: (value) => value
    }),
    buildCheck({
      field: 'FeedRegistry',
      summaryValue: summary.feedRegistry,
      chainValue: chainFeedRegistry,
      equals: addressesEqual,
      format: (value) => value
    }),
    buildCheck({
      field: 'CooldownSec',
      summaryValue: summary.cooldownSec,
      chainValue: chain.cooldownSec,
      equals: numbersEqual,
      format: (value) => String(value)
    }),
    buildCheck({
      field: 'AssetUniversePolicy',
      summaryValue: summary.assetUniversePolicy,
      chainValue: chain.assetUniversePolicy,
      equals: addressesEqual,
      format: (value) => value
    }),
    buildCheck({
      field: 'AssetUniverseAssets',
      summaryValue: summary.assetUniverseAssets.length ? summary.assetUniverseAssets : undefined,
      chainValue: chain.assetUniverseAssets.length ? chain.assetUniverseAssets : undefined,
      equals: addressListsEqual,
      format: formatAddressList
    }),
    buildCheck({
      field: 'StaticAllocationPolicy',
      summaryValue: summary.staticAllocationPolicy,
      chainValue: chain.staticAllocationPolicy,
      equals: addressesEqual,
      format: (value) => value
    }),
    buildCheck({
      field: 'StaticAllocationDriftThresholdPercent',
      summaryValue: summary.staticAllocationDriftThresholdPercent,
      chainValue: chain.staticAllocationDriftThresholdPercent,
      equals: numbersEqual,
      format: formatPercent
    }),
    buildCheck({
      field: 'StaticAllocationToleranceThresholdPercent',
      summaryValue: summary.staticAllocationToleranceThresholdPercent,
      chainValue: chain.staticAllocationToleranceThresholdPercent,
      equals: numbersEqual,
      format: formatPercent
    }),
    buildCheck({
      field: 'StaticAllocationTargets',
      summaryValue: summary.staticAllocationTargets.length ? summary.staticAllocationTargets : undefined,
      chainValue: chain.staticAllocationTargets.length ? chain.staticAllocationTargets : undefined,
      equals: targetsEqual,
      format: formatTargets
    }),
    buildCheck({
      field: 'SlippagePolicy',
      summaryValue: summary.slippagePolicy,
      chainValue: chain.slippagePolicy,
      equals: addressesEqual,
      format: (value) => value
    }),
    buildCheck({
      field: 'MaxSlippagePercent',
      summaryValue: summary.maxSlippagePercent,
      chainValue: chain.maxSlippagePercent,
      equals: numbersEqual,
      format: formatPercent
    })
  ];

  const warnings: string[] = [];
  if (
    chain.staticFeedRegistry &&
    chain.slippageFeedRegistry &&
    !addressesEqual(chain.staticFeedRegistry, chain.slippageFeedRegistry)
  ) {
    warnings.push(
      `On-chain feed registries differ: staticAllocation=${chain.staticFeedRegistry}, slippage=${chain.slippageFeedRegistry}.`
    );
  }

  const mismatches = checks
    .filter((check) => check.status === 'mismatch')
    .map((check) => `${check.field}: ${check.detail}`);
  const ok = mismatches.length === 0;

  return {
    ok,
    executorModuleAddress: chain.executorModuleAddress,
    rpcUrl,
    checks,
    mismatches,
    warnings,
    message: ok
      ? 'Deployment verification passed. Compared troubleshooting summary + env hints against on-chain state.'
      : `Deployment verification found ${mismatches.length} mismatch(es).`
  };
}
