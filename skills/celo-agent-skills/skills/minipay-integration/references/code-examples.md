# MiniPay Code Examples

## Transaction Confirmation

Always wait for transaction confirmation:

```typescript
import { createPublicClient, http } from "viem";
import { celo } from "viem/chains";

const publicClient = createPublicClient({
  chain: celo,
  transport: http(),
});

async function waitForTransaction(hash: `0x${string}`): Promise<boolean> {
  const receipt = await publicClient.waitForTransactionReceipt({ hash });
  return receipt.status === "success";
}
```

## Gas Estimation

Estimate gas for transactions:

```typescript
import { createPublicClient, http, formatUnits, encodeFunctionData } from "viem";
import { celo } from "viem/chains";

const publicClient = createPublicClient({
  chain: celo,
  transport: http(),
});

// Estimate gas in CELO
const gasEstimate = await publicClient.estimateGas({
  account: address,
  to: USDM_ADDRESS,
  data: encodeFunctionData({
    abi: ERC20_ABI,
    functionName: "transfer",
    args: [recipient, amount],
  }),
});

// Get gas price
const gasPrice = await publicClient.request({
  method: "eth_gasPrice",
  params: [],
});

// Calculate fee
const fee = BigInt(gasEstimate) * BigInt(gasPrice);
console.log("Estimated fee:", formatUnits(fee, 18), "CELO");
```

## Fee Currency (Pay Gas with Stablecoins)

MiniPay supports paying gas fees with USDm:

```typescript
import { createWalletClient, custom, encodeFunctionData } from "viem";
import { celo } from "viem/chains";

const USDM_ADDRESS = "0x765de816845861e75a25fca122bb6898b8b1282a";

const walletClient = createWalletClient({
  chain: celo,
  transport: custom(window.ethereum),
});

const hash = await walletClient.sendTransaction({
  account: address,
  to: USDM_ADDRESS,
  data: encodeFunctionData({
    abi: ERC20_ABI,
    functionName: "transfer",
    args: [recipient, amount],
  }),
  feeCurrency: USDM_ADDRESS, // Pay gas with USDm
});
```

**Note:** Only USDm is currently supported for fee abstraction.

## Deeplinks

Open MiniPay's Add Cash screen:

```typescript
const openAddCash = () => {
  window.location.href = "https://minipay.opera.com/add_cash";
};
```

## Complete Transfer Example

Full example with error handling:

```typescript
import {
  createPublicClient,
  createWalletClient,
  custom,
  http,
  parseUnits,
  formatUnits,
  encodeFunctionData,
} from "viem";
import { celo } from "viem/chains";

const USDM_ADDRESS = "0x765de816845861e75a25fca122bb6898b8b1282a";

const ERC20_ABI = [
  {
    name: "transfer",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [
      { name: "to", type: "address" },
      { name: "amount", type: "uint256" },
    ],
    outputs: [{ type: "bool" }],
  },
  {
    name: "balanceOf",
    type: "function",
    stateMutability: "view",
    inputs: [{ name: "account", type: "address" }],
    outputs: [{ type: "uint256" }],
  },
] as const;

const publicClient = createPublicClient({
  chain: celo,
  transport: http(),
});

async function transferUSDm(
  to: string,
  amount: string
): Promise<{ success: boolean; hash?: string; error?: string }> {
  try {
    // Check if in MiniPay
    if (typeof window === "undefined" || !window.ethereum?.isMiniPay) {
      return { success: false, error: "Not in MiniPay" };
    }

    const walletClient = createWalletClient({
      chain: celo,
      transport: custom(window.ethereum),
    });

    const [address] = await walletClient.getAddresses();

    // Check balance
    const balance = await publicClient.readContract({
      address: USDM_ADDRESS,
      abi: ERC20_ABI,
      functionName: "balanceOf",
      args: [address],
    });

    const amountWei = parseUnits(amount, 18);

    if (balance < amountWei) {
      return {
        success: false,
        error: `Insufficient balance. Have ${formatUnits(balance, 18)}, need ${amount}`,
      };
    }

    // Send transaction
    const hash = await walletClient.sendTransaction({
      account: address,
      to: USDM_ADDRESS,
      data: encodeFunctionData({
        abi: ERC20_ABI,
        functionName: "transfer",
        args: [to as `0x${string}`, amountWei],
      }),
    });

    // Wait for confirmation
    const receipt = await publicClient.waitForTransactionReceipt({ hash });

    if (receipt.status === "success") {
      return { success: true, hash };
    } else {
      return { success: false, hash, error: "Transaction failed" };
    }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}
```

## React Hook Example

```typescript
import { useState, useEffect, useCallback } from "react";
import { createWalletClient, createPublicClient, custom, http, formatUnits } from "viem";
import { celo } from "viem/chains";

const USDM_ADDRESS = "0x765de816845861e75a25fca122bb6898b8b1282a";

const ERC20_ABI = [
  {
    name: "balanceOf",
    type: "function",
    stateMutability: "view",
    inputs: [{ name: "account", type: "address" }],
    outputs: [{ type: "uint256" }],
  },
] as const;

export function useMiniPay() {
  const [address, setAddress] = useState<string | null>(null);
  const [balance, setBalance] = useState<string | null>(null);
  const [isMiniPay, setIsMiniPay] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      if (typeof window === "undefined" || !window.ethereum) {
        setIsLoading(false);
        return;
      }

      const inMiniPay = window.ethereum.isMiniPay === true;
      setIsMiniPay(inMiniPay);

      if (inMiniPay) {
        try {
          const accounts = await window.ethereum.request({
            method: "eth_requestAccounts",
            params: [],
          });
          if (accounts[0]) {
            setAddress(accounts[0]);
          }
        } catch (error) {
          console.error("Failed to connect:", error);
        }
      }

      setIsLoading(false);
    };

    init();
  }, []);

  const fetchBalance = useCallback(async () => {
    if (!address) return;

    const publicClient = createPublicClient({
      chain: celo,
      transport: http(),
    });

    const bal = await publicClient.readContract({
      address: USDM_ADDRESS,
      abi: ERC20_ABI,
      functionName: "balanceOf",
      args: [address as `0x${string}`],
    });

    setBalance(formatUnits(bal, 18));
  }, [address]);

  useEffect(() => {
    if (address) {
      fetchBalance();
    }
  }, [address, fetchBalance]);

  return {
    address,
    balance,
    isMiniPay,
    isLoading,
    refreshBalance: fetchBalance,
  };
}
```

## Usage in Component

```tsx
function WalletInfo() {
  const { address, balance, isMiniPay, isLoading } = useMiniPay();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isMiniPay) {
    return <div>Please open this app in MiniPay</div>;
  }

  return (
    <div>
      <p>Address: {address}</p>
      <p>Balance: {balance} USDm</p>
    </div>
  );
}
```
