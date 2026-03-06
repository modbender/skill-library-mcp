/**
 * Local tools (for agents using this skill): balance_aptos, balance_evm, get_wallet_addresses, create_aptos_wallet, create_evm_wallet.
 */

import { tool } from '@langchain/core/tools';
import { z } from 'zod';
import { getAptosBalance } from '../../lib/aptos/balance.js';
import {
  getWalletInfo as getAptosWalletInfo,
  getAllWalletInfos as getAptosAllWalletInfos,
  save as saveAptosWallet,
  exists as aptosWalletExists,
} from '../../lib/aptos/wallet.js';
import {
  getWalletInfo as getEvmWalletInfo,
  getAllWalletInfos as getEvmAllWalletInfos,
  getAddress,
  generate as generateEvmWallet,
  save as saveEvmWallet,
  exists as evmWalletExists,
} from '../../lib/wallet.js';
import { createPublicClientWithRetry } from '../../lib/rpc.js';
import { getChain, getSupportedChains } from '../../lib/chains.js';
import { formatEther } from 'viem';
import { APTOS_FAUCET_TESTNET_PAGE } from '../../lib/aptos/config.js';

export function createLocalTools() {
  const balance_aptos = tool(
    async () => {
      try {
        const info = getAptosWalletInfo();
        if (!info?.address) return JSON.stringify({ error: 'No Aptos wallet. Run setup-aptos.js.' });
        const bal = await getAptosBalance(info.address);
        return JSON.stringify(bal ?? { error: 'Could not fetch balance' });
      } catch (e) {
        return JSON.stringify({ error: e.message });
      }
    },
    {
      name: 'balance_aptos',
      description: 'Get Aptos balance (USDC + APT) for the configured wallet. Returns { address, balances: { usdc, apt } } or { error }. Call before run_prediction, run_backtest, or score tools to confirm sufficient USDC.',
      schema: z.object({}),
    }
  );

  const balance_evm = tool(
    async ({ chain }) => {
      try {
        if (!evmWalletExists()) return JSON.stringify({ error: 'No EVM wallet. Run setup.js.' });
        const addr = getAddress();
        const chainInput = (chain || 'base').toLowerCase();
        const chainName = getSupportedChains().find((c) => c.toLowerCase() === chainInput);
        if (!chainName) {
          return JSON.stringify({ error: `Unsupported chain. Use one of: ${getSupportedChains().join(', ')}` });
        }
        const chainConfig = getChain(chainName);
        const client = createPublicClientWithRetry(chainName);
        const balance = await client.getBalance({ address: addr });
        return JSON.stringify({
          address: addr,
          chain: chainName,
          balance: formatEther(balance),
          symbol: chainConfig.nativeToken?.symbol || 'ETH',
        });
      } catch (e) {
        return JSON.stringify({ error: e.message });
      }
    },
    {
      name: 'balance_evm',
      description: 'Get EVM native token balance. Returns { address, chain, balance, symbol } or { error }. Use chain "baseSepolia" before link_bank_account. Supported: base, baseSepolia, ethereum, polygon, arbitrum, optimism.',
      schema: z.object({
        chain: z.string().default('base').describe('Chain name: base, baseSepolia, ethereum, polygon, arbitrum, optimism (default base)'),
      }),
    }
  );

  const get_wallet_addresses = tool(
    async () => {
      const aptosList = aptosWalletExists() ? getAptosAllWalletInfos() : [];
      const evmList = evmWalletExists() ? getEvmAllWalletInfos() : [];
      return JSON.stringify({
        aptos: aptosList.map((w) => ({ address: w.address, network: w.network || null })),
        evm: evmList.map((w) => ({ address: w.address, network: w.network || null })),
      });
    },
    {
      name: 'get_wallet_addresses',
      description: 'Get all configured wallet addresses. Returns { aptos: [{ address, network }], evm: [{ address, network }] } — arrays may be empty. ALWAYS call this first before any wallet or paid tool action to see what exists.',
      schema: z.object({}),
    }
  );

  const create_aptos_wallet = tool(
    async ({ force, network }) => {
      try {
        const net = (network || '').toLowerCase() === 'mainnet' ? 'mainnet' : 'testnet';
        if (aptosWalletExists() && !force) {
          const infos = getAptosAllWalletInfos();
          return JSON.stringify({
            success: false,
            message: 'Aptos wallet(s) already exist. Use force: true to add another or overwrite. You can have multiple Aptos wallets (testnet and mainnet).',
            addresses: infos.map((w) => ({ address: w.address, network: w.network || null })),
          });
        }
        const { Account } = await import('@aptos-labs/ts-sdk');
        const account = Account.generate();
        const wallet = {
          address: account.accountAddress.toString(),
          privateKey: account.privateKey.toString(),
          network: net,
          createdAt: new Date().toISOString(),
        };
        saveAptosWallet(wallet);
        return JSON.stringify({
          success: true,
          message: `Aptos wallet created (${net}). Whitelist this address at https://arnstein.ch/flow.html and fund with ${net} APT/USDC for run_prediction and run_backtest.`,
          address: wallet.address,
          network: net,
        });
      } catch (e) {
        if (e.code === 'ERR_MODULE_NOT_FOUND' || (e?.message?.includes?.('@aptos-labs/ts-sdk'))) {
          return JSON.stringify({ success: false, error: 'Aptos SDK not installed. Run: npm install @aptos-labs/ts-sdk' });
        }
        return JSON.stringify({ success: false, error: e.message });
      }
    },
    {
      name: 'create_aptos_wallet',
      description: 'Create a new Aptos wallet. Returns { success, address, network }. If wallet exists and force=false, returns existing addresses instead. After creating, call credit_aptos_wallet to fund, then tell the user to whitelist the address at https://arnstein.ch/flow.html.',
      schema: z.object({
        force: z.boolean().default(false).describe('If true, add another wallet even when one exists; otherwise only one allowed per run without force.'),
        network: z.enum(['testnet', 'mainnet']).nullable().default(null).describe('Optional: testnet (default) or mainnet.'),
      }),
    }
  );

  const create_evm_wallet = tool(
    async ({ force, network }) => {
      try {
        const net = (network || '').toLowerCase() === 'mainnet' ? 'mainnet' : 'testnet';
        if (evmWalletExists() && !force) {
          const infos = getEvmAllWalletInfos();
          return JSON.stringify({
            success: false,
            message: 'EVM wallet(s) already exist. Use force: true to add another. You can have multiple EVM wallets (testnet and mainnet).',
            addresses: infos.map((w) => ({ address: w.address, network: w.network || null })),
          });
        }
        const wallet = generateEvmWallet();
        wallet.network = net;
        saveEvmWallet(wallet);
        return JSON.stringify({
          success: true,
          message: `EVM wallet created (${net}). Whitelist this address at https://arnstein.ch/flow.html and fund with ETH on Base Sepolia (testnet) or Base (mainnet) for link_bank_account.`,
          address: wallet.address,
          network: net,
        });
      } catch (e) {
        return JSON.stringify({ success: false, error: e.message });
      }
    },
    {
      name: 'create_evm_wallet',
      description: 'Create a new EVM wallet. Returns { success, address, network }. If wallet exists and force=false, returns existing addresses instead. After creating, call fund_evm_wallet for funding instructions, then tell the user to whitelist at https://arnstein.ch/flow.html.',
      schema: z.object({
        force: z.boolean().default(false).describe('If true, add another wallet even when one exists.'),
        network: z.enum(['testnet', 'mainnet']).optional().describe('Optional: testnet (default) or mainnet.'),
      }),
    }
  );

  const credit_aptos_wallet = tool(
    async ({ amount_octas }) => {
      try {
        if (!aptosWalletExists()) {
          return JSON.stringify({
            success: false,
            error: 'No Aptos wallet. Use create_aptos_wallet first.',
          });
        }
        const info = getAptosWalletInfo();
        const address = info?.address;
        if (!address) {
          return JSON.stringify({ success: false, error: 'Could not read Aptos address.' });
        }
        const network = (process.env.APTOS_FAUCET_NETWORK || 'testnet').toLowerCase();
        const octas = amount_octas ?? 100_000_000; // 1 APT default
        if (network === 'devnet') {
          const { Aptos, AptosConfig, Network } = await import('@aptos-labs/ts-sdk');
          const aptosConfig = new AptosConfig({ network: Network.DEVNET });
          const aptos = new Aptos(aptosConfig);
          await aptos.fundAccount({ accountAddress: address, amount: octas });
          return JSON.stringify({
            success: true,
            message: `Funded Aptos wallet on devnet with ${octas} octas (${octas / 100_000_000} APT). Demo MCP uses testnet by default.`,
            address,
          });
        }
        return JSON.stringify({
          success: true,
          message: 'Aptos testnet has no programmatic faucet. Fund manually: open ' + APTOS_FAUCET_TESTNET_PAGE + ', sign in, enter address below, request APT. Also fund USDC for x402 payments if needed.',
          address,
          faucet_url: APTOS_FAUCET_TESTNET_PAGE,
        });
      } catch (e) {
        return JSON.stringify({ success: false, error: e.message });
      }
    },
    {
      name: 'credit_aptos_wallet',
      description: 'Fund the Aptos wallet. Devnet: programmatic faucet (funds directly). Testnet: returns { faucet_url, address } with manual instructions. Prerequisite: Aptos wallet must exist (call create_aptos_wallet first).',
      schema: z.object({
        amount_octas: z.number().nullable().default(100_000_000).describe('Amount in octas (1 APT = 100_000_000). Default 1 APT.'),
      }),
    }
  );

  const BASE_SEPOLIA_FAUCET = 'https://www.alchemy.com/faucets/base-sepolia';
  const fund_evm_wallet = tool(
    async () => {
      try {
        if (!evmWalletExists()) {
          return JSON.stringify({
            success: false,
            error: 'No EVM wallet. Use create_evm_wallet first.',
          });
        }
        const info = getEvmWalletInfo();
        const address = info?.address;
        if (!address) {
          return JSON.stringify({ success: false, error: 'Could not read EVM address.' });
        }
        return JSON.stringify({
          success: true,
          message: 'EVM (Base Sepolia) has no programmatic faucet here. Fund manually: open a Base Sepolia faucet, enter the address below, request test ETH. Needed for link_bank_account (~$3.65). Whitelist this address at https://arnstein.ch/flow.html.',
          address,
          faucet_url: BASE_SEPOLIA_FAUCET,
        });
      } catch (e) {
        return JSON.stringify({ success: false, error: e.message });
      }
    },
    {
      name: 'fund_evm_wallet',
      description: 'Get funding instructions for the EVM wallet (Base Sepolia). Returns { faucet_url, address, message }. No programmatic faucet — user must fund manually. Prerequisite: EVM wallet must exist (call create_evm_wallet first).',
      schema: z.object({}),
    }
  );

  return [
    balance_aptos,
    balance_evm,
    get_wallet_addresses,
    create_aptos_wallet,
    create_evm_wallet,
    credit_aptos_wallet,
    fund_evm_wallet,
  ];
}
