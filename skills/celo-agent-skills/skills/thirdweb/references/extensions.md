# Thirdweb Extensions Reference

Source: https://portal.thirdweb.com/typescript/v5

## Overview

Thirdweb provides type-safe extensions for interacting with common smart contract standards. Extensions handle ABI encoding/decoding and provide a clean API.

## ERC20 Extensions

```typescript
import {
  balanceOf,
  transfer,
  approve,
  allowance,
  totalSupply,
  decimals,
  name,
  symbol,
} from "thirdweb/extensions/erc20";
```

### Read Balance

```typescript
import { balanceOf } from "thirdweb/extensions/erc20";

const balance = await balanceOf({
  contract,
  address: "0x...",
});
```

### Transfer Tokens

```typescript
import { transfer } from "thirdweb/extensions/erc20";

const transaction = transfer({
  contract,
  to: "0x...",
  amount: "100", // Human-readable amount
});
```

### Approve Spending

```typescript
import { approve } from "thirdweb/extensions/erc20";

const transaction = approve({
  contract,
  spender: "0x...",
  amount: "1000",
});
```

## ERC721 Extensions

```typescript
import {
  balanceOf,
  ownerOf,
  transferFrom,
  approve,
  setApprovalForAll,
  getOwnedNFTs,
  getNFT,
} from "thirdweb/extensions/erc721";
```

### Get NFT Metadata

```typescript
import { getNFT } from "thirdweb/extensions/erc721";

const nft = await getNFT({
  contract,
  tokenId: 1n,
});

console.log(nft.metadata);
```

### Get Owned NFTs

```typescript
import { getOwnedNFTs } from "thirdweb/extensions/erc721";

const nfts = await getOwnedNFTs({
  contract,
  owner: "0x...",
});
```

### Transfer NFT

```typescript
import { transferFrom } from "thirdweb/extensions/erc721";

const transaction = transferFrom({
  contract,
  from: "0x...",
  to: "0x...",
  tokenId: 1n,
});
```

## ERC1155 Extensions

```typescript
import {
  balanceOf,
  balanceOfBatch,
  safeTransferFrom,
  getNFTs,
  getNFT,
} from "thirdweb/extensions/erc1155";
```

### Get Token Balance

```typescript
import { balanceOf } from "thirdweb/extensions/erc1155";

const balance = await balanceOf({
  contract,
  owner: "0x...",
  tokenId: 1n,
});
```

### Batch Balance Check

```typescript
import { balanceOfBatch } from "thirdweb/extensions/erc1155";

const balances = await balanceOfBatch({
  contract,
  owners: ["0x...", "0x..."],
  tokenIds: [1n, 2n],
});
```

## Using Extensions with React

### Read with Hook

```tsx
import { useReadContract } from "thirdweb/react";
import { balanceOf } from "thirdweb/extensions/erc20";

function Balance() {
  const { data, isLoading } = useReadContract(
    balanceOf,
    {
      contract,
      address: userAddress,
    }
  );

  return <div>{data?.toString()}</div>;
}
```

### Write with Hook

```tsx
import { useSendTransaction } from "thirdweb/react";
import { transfer } from "thirdweb/extensions/erc20";

function Transfer() {
  const { mutate: sendTransaction } = useSendTransaction();

  function handleTransfer() {
    const tx = transfer({
      contract,
      to: recipient,
      amount: "10",
    });
    sendTransaction(tx);
  }

  return <button onClick={handleTransfer}>Transfer</button>;
}
```

## Contract Setup

All extensions require a contract reference:

```typescript
import { getContract } from "thirdweb";
import { celo } from "thirdweb/chains";

const contract = getContract({
  client,
  chain: celo,
  address: "0x765de816845861e75a25fca122bb6898b8b1282a", // USDm
});
```
