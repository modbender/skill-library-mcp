// wallet.js — Wallet utilities for Base mainnet: auto-swap ETH→USDC, transfers
import { ethers } from 'ethers';

const BASE_RPC = process.env.RPC_URL || 'https://mainnet.base.org';
const USDC_ADDRESS = process.env.USDC_ADDRESS || '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913';
const WETH_ADDRESS = '0x4200000000000000000000000000000000000006';
const SWAP_ROUTER = '0x2626664c2603336E57B271c5C0b26F421741e481'; // Uniswap V3 on Base
const GAS_RESERVE = ethers.parseEther('0.005'); // keep ~0.005 ETH for gas

const USDC_ABI = [
  'function balanceOf(address) view returns (uint256)',
  'function transfer(address to, uint256 amount) returns (bool)',
  'function decimals() view returns (uint8)',
];

const SWAP_ROUTER_ABI = [
  'function exactInputSingle((address tokenIn, address tokenOut, uint24 fee, address recipient, uint256 amountIn, uint256 amountOutMinimum, uint160 sqrtPriceLimitX96)) external payable returns (uint256 amountOut)',
];

/** Create a provider for Base mainnet */
export function getProvider() {
  return new ethers.JsonRpcProvider(BASE_RPC);
}

/** Create a wallet from a private key */
export function loadWallet(privateKey) {
  const provider = getProvider();
  return new ethers.Wallet(privateKey, provider);
}

/** Load wallet from .env WALLET_PRIVATE_KEY */
export function loadWalletFromEnv() {
  const key = process.env.WALLET_PRIVATE_KEY;
  if (!key) throw new Error('WALLET_PRIVATE_KEY not set in environment');
  return loadWallet(key);
}

/** Get ETH balance on Base (returns human-readable string) */
export async function getETHBalance(address) {
  const provider = getProvider();
  const balance = await provider.getBalance(address);
  return ethers.formatEther(balance);
}

/** Get USDC balance for an address (returns human-readable string) */
export async function getUSDCBalance(address) {
  const provider = getProvider();
  const usdc = new ethers.Contract(USDC_ADDRESS, USDC_ABI, provider);
  const [balance, decimals] = await Promise.all([usdc.balanceOf(address), usdc.decimals()]);
  return ethers.formatUnits(balance, decimals);
}

/**
 * Swap ETH → USDC on Base via Uniswap V3.
 * Keeps GAS_RESERVE ETH for future transactions.
 * @param {ethers.Wallet} wallet - funded wallet
 * @param {string|null} amountETH - ETH to swap (human-readable), or null to swap all minus gas reserve
 * @returns {{ txHash: string, usdcReceived: string }}
 */
export async function swapETHtoUSDC(wallet, amountETH = null) {
  const provider = wallet.provider;
  const balance = await provider.getBalance(wallet.address);

  let amountIn;
  if (amountETH) {
    amountIn = ethers.parseEther(amountETH.toString());
  } else {
    // swap everything minus gas reserve
    if (balance <= GAS_RESERVE) {
      throw new Error(`ETH balance too low to swap. Have ${ethers.formatEther(balance)}, need >${ethers.formatEther(GAS_RESERVE)} for gas reserve.`);
    }
    amountIn = balance - GAS_RESERVE;
  }

  const router = new ethers.Contract(SWAP_ROUTER, SWAP_ROUTER_ABI, wallet);
  const usdcBefore = await getUSDCBalance(wallet.address);

  const tx = await router.exactInputSingle({
    tokenIn: WETH_ADDRESS,
    tokenOut: USDC_ADDRESS,
    fee: 500, // 0.05% pool (deepest liquidity for ETH/USDC on Base)
    recipient: wallet.address,
    amountIn,
    amountOutMinimum: 0,
    sqrtPriceLimitX96: 0,
  }, { value: amountIn });

  await tx.wait();
  const usdcAfter = await getUSDCBalance(wallet.address);
  const usdcReceived = (parseFloat(usdcAfter) - parseFloat(usdcBefore)).toFixed(6);

  return { txHash: tx.hash, usdcReceived };
}

/**
 * Ensure the wallet has enough USDC for a payment.
 * If USDC is insufficient, auto-swaps ETH → USDC.
 * @param {ethers.Wallet} wallet
 * @param {string} amountNeeded - USDC amount needed (human-readable)
 * @returns {boolean} true if wallet has enough after potential swap
 */
export async function ensureUSDC(wallet, amountNeeded) {
  const usdcBal = parseFloat(await getUSDCBalance(wallet.address));
  const needed = parseFloat(amountNeeded);

  if (usdcBal >= needed) return true;

  // try to swap ETH to cover the gap
  try {
    const result = await swapETHtoUSDC(wallet);
    const newBal = parseFloat(await getUSDCBalance(wallet.address));
    return newBal >= needed;
  } catch {
    return false;
  }
}

/** Transfer USDC from wallet to recipient. Auto-swaps ETH if needed. Returns tx hash. */
export async function transferUSDC(wallet, to, amountHuman) {
  // auto-swap if USDC balance is insufficient
  const hasFunds = await ensureUSDC(wallet, amountHuman);
  if (!hasFunds) {
    throw new Error(`Insufficient funds. Need ${amountHuman} USDC but wallet cannot cover it even after ETH swap.`);
  }

  const usdc = new ethers.Contract(USDC_ADDRESS, USDC_ABI, wallet);
  const decimals = await usdc.decimals();
  const amount = ethers.parseUnits(amountHuman.toString(), decimals);
  const tx = await usdc.transfer(to, amount);
  await tx.wait();
  return tx.hash;
}
