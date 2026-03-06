// Parse command line arguments into key=value pairs and positional args
export function parseArgs(args: string[]): {
  positional: string[];
  flags: Record<string, string | boolean>;
} {
  const positional: string[] = [];
  const flags: Record<string, string | boolean> = {};

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      const nextArg = args[i + 1];

      // Check if next arg is a value or another flag
      if (nextArg && !nextArg.startsWith('-')) {
        flags[key] = nextArg;
        i++;
      } else {
        flags[key] = true;
      }
    } else if (arg.startsWith('-')) {
      const key = arg.slice(1);
      flags[key] = true;
    } else {
      positional.push(arg);
    }
  }

  return { positional, flags };
}

// Format USD amount with proper decimals
export function formatUsd(amount: string | number, decimals = 2): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  return `$${num.toFixed(decimals)}`;
}

// Format crypto amount
export function formatCrypto(amount: string | number, symbol: string, decimals = 6): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  return `${num.toFixed(decimals)} ${symbol}`;
}

// Truncate address for display
export function truncateAddress(address: string): string {
  if (address.length <= 10) return address;
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

// Parse price string like "$0.01" to number
export function parsePriceString(price: string): number {
  const cleaned = price.replace(/[$,]/g, '');
  return parseFloat(cleaned);
}

// Sleep utility
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Log with timestamp (when verbose)
export function log(message: string, verbose = false): void {
  if (verbose || process.env.X402_VERBOSE === '1') {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${message}`);
  }
}

// Error formatting
export function formatError(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
}

// Validate URL
export function isValidUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:';
  } catch {
    return false;
  }
}

// Check if response is 402 Payment Required
export function is402Response(response: Response): boolean {
  return response.status === 402;
}

// Extract payment details from 402 response headers
export interface PaymentRequirement {
  scheme: string;
  price: string;
  network: string;
  payTo: string;
}

export function extractPaymentRequirements(response: Response): PaymentRequirement[] | null {
  const paymentRequired = response.headers.get('PAYMENT-REQUIRED');
  if (!paymentRequired) return null;

  try {
    const decoded = JSON.parse(atob(paymentRequired));
    return decoded.accepts || null;
  } catch {
    return null;
  }
}
