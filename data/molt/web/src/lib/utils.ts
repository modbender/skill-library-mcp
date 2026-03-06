import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}

export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;
  
  return formatDate(dateString);
}

export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

export function copyToClipboard(text: string): Promise<void> {
  return navigator.clipboard.writeText(text);
}

// Currency conversion utilities
export function dollarsToCents(amount: number): number {
  return Math.round(amount * 100);
}

export function centsToDollars(amount: number): number {
  return amount / 100;
}

// Wallet address validation
export function validateEthAddress(address: string): boolean {
  return /^0x[a-fA-F0-9]{40}$/.test(address);
}

export function validateBtcAddress(address: string): boolean {
  // Basic BTC address validation (can be improved)
  return address.length >= 26 && address.length <= 62 && /^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[a-z0-9]{39,59}$/.test(address);
}

export function validateUsdcBaseAddress(address: string): boolean {
  // USDC on Base uses the same address format as Ethereum (0x...)
  return validateEthAddress(address);
}

export function validateSolAddress(address: string): boolean {
  // Solana addresses are base58 encoded, typically 32-44 characters
  return /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(address);
}

// Crypto conversion utilities (converting from smallest units to display units)
export function satoshiToBtc(satoshi: number): number {
  return satoshi / 100000000;
}

export function weiToEth(wei: number): number {
  return wei / 1000000000000000000;
}

export function lamportsToSol(lamports: number): number {
  return lamports / 1000000000;
}

export function usdcBaseToUsd(usdcBase: number): number {
  // USDC has 6 decimals
  return usdcBase / 1000000;
}

// Fallback function for calculating USD when backend hasn't refreshed yet
// Note: This uses approximate values and should only be used as a fallback.
// The backend provides accurate current_total_usd_cents after balance refresh.
export function cryptoToUsd(
  btcSatoshi: number = 0,
  ethWei: number = 0,
  solLamports: number = 0,
  usdcBase: number = 0
): number {
  // This is a fallback - prices should come from backend
  // Using conservative estimates for display purposes only
  const btcAmount = satoshiToBtc(btcSatoshi);
  const ethAmount = weiToEth(ethWei);
  const solAmount = lamportsToSol(solLamports);
  const usdcAmount = usdcBaseToUsd(usdcBase);
  
  // Rough estimates (will be replaced by backend prices after refresh)
  // These are only used before the first balance refresh
  return (
    btcAmount * 95000 +  // Conservative BTC estimate
    ethAmount * 2700 +   // Conservative ETH estimate
    solAmount * 200 +    // Conservative SOL estimate
    usdcAmount * 1       // USDC is always $1
  );
}

export function formatCryptoAmount(amount: number, chain: 'btc' | 'eth' | 'sol' | 'usdc_base'): string {
  if (chain === 'btc') {
    return `${satoshiToBtc(amount).toFixed(8)} BTC`;
  } else if (chain === 'eth') {
    return `${weiToEth(amount).toFixed(6)} ETH`;
  } else if (chain === 'sol') {
    return `${lamportsToSol(amount).toFixed(4)} SOL`;
  } else if (chain === 'usdc_base') {
    return `${usdcBaseToUsd(amount).toFixed(2)} USDC`;
  }
  return amount.toString();
}

export function getBlockExplorerUrl(txHash: string, chain: 'btc' | 'eth' | 'sol' | 'usdc_base'): string {
  const urls: Record<string, string> = {
    btc: `https://www.blockchain.com/explorer/transactions/btc/${txHash}`,
    eth: `https://etherscan.io/tx/${txHash}`,
    sol: `https://solscan.io/tx/${txHash}`,
    usdc_base: `https://basescan.org/tx/${txHash}`,
  };
  return urls[chain] || '#';
}
