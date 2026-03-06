import { createPublicClient, createWalletClient, http } from 'viem';
import { base, baseSepolia } from 'viem/chains';
import { privateKeyToAccount } from 'viem/accounts';

export const SBT_ABI = [
  {
    name: 'safeMint',
    type: 'function',
    stateMutability: 'nonpayable',
    inputs: [
      { name: 'to', type: 'address' },
      { name: 'uri', type: 'string' },
    ],
    outputs: [],
  },
] as const;

export interface MintSbtParams {
  contractAddress: `0x${string}`;
  to: `0x${string}`;
  tokenUri: string;
  network: 'base-mainnet' | 'base-sepolia';
  privateKey: `0x${string}`;
}

export async function mintIdentitySbt(params: MintSbtParams): Promise<string> {
  const chain = params.network === 'base-mainnet' ? base : baseSepolia;
  const account = privateKeyToAccount(params.privateKey);

  const publicClient = createPublicClient({
    chain,
    transport: http(chain.rpcUrls.default.http[0]),
  });

  const walletClient = createWalletClient({
    account,
    chain,
    transport: http(chain.rpcUrls.default.http[0]),
  });

  const hash = await walletClient.writeContract({
    address: params.contractAddress,
    abi: SBT_ABI,
    functionName: 'safeMint',
    args: [params.to, params.tokenUri],
  });

  // wait for inclusion (60s timeout)
  await publicClient.waitForTransactionReceipt({ hash, timeout: 60_000 });

  return hash;
}
