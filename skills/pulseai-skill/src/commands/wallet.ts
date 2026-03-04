import { Command } from 'commander';
import { formatEther, erc20Abi } from 'viem';
import { generatePrivateKey, privateKeyToAccount } from 'viem/accounts';
import { formatUsdm } from '@pulseai/sdk';
import { getClient, getAddress, loadConfig, saveConfig } from '../config.js';
import { output, error, info, success, isJsonMode } from '../lib/output.js';

const OPERATOR_MESSAGE = 'Ask your agent owner to set you as operator: pulse agent set-operator --agent-id <ID> --operator <YOUR_ADDRESS>';

async function showWallet(): Promise<void> {
  const client = getClient();
  const address = getAddress();

  const [ethBalance, usdmBalance] = await Promise.all([
    client.publicClient.getBalance({ address }),
    client.publicClient.readContract({
      address: client.addresses.usdm,
      abi: erc20Abi,
      functionName: 'balanceOf',
      args: [address],
    }) as Promise<bigint>,
  ]);

  output({
    address,
    network: 'MegaETH Mainnet',
    chainId: client.chain.id,
    ethBalance: formatEther(ethBalance) + ' ETH',
    usdmBalance: formatUsdm(usdmBalance) + ' USDm',
  });
}

export const walletCommand = new Command('wallet')
  .description('Show wallet address and balances')
  .option('--json', 'Output as JSON')
  .action(async () => {
    try {
      await showWallet();
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

walletCommand
  .command('show')
  .description('Show wallet address and balances')
  .option('--json', 'Output as JSON')
  .action(async () => {
    try {
      await showWallet();
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });

walletCommand
  .command('generate')
  .description('Generate and save a wallet private key')
  .option('--json', 'Output as JSON')
  .action(async () => {
    try {
      const config = loadConfig();
      const existingKey = config.privateKey;

      if (existingKey) {
        const existingAddress = privateKeyToAccount(existingKey).address;
        info('Wallet key already exists at ~/.pulse/config.json');

        output({
          address: existingAddress,
          ...(isJsonMode() ? { privateKey: existingKey } : {}),
          message: OPERATOR_MESSAGE,
        });
        success('Using existing wallet key.');
        return;
      }

      info('Generating new wallet key...');
      const privateKey = generatePrivateKey();
      const account = privateKeyToAccount(privateKey);

      saveConfig({ privateKey });
      success('Saved wallet key to ~/.pulse/config.json');

      output({
        address: account.address,
        ...(isJsonMode() ? { privateKey } : {}),
        message: OPERATOR_MESSAGE,
      });
    } catch (e) {
      error(e instanceof Error ? e.message : String(e));
    }
  });
