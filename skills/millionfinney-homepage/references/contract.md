# Million Finney Homepage Contract Reference

**Network:** Ethereum mainnet  
**Contract address:** `0x0CCBBBAb176EbE9E4b9846C5555f5e89762A31d7` (`millionfinneyhomepage.eth`)  
**Grid:** 1,000 × 1,000 pixels (IDs `0–999,999`)  
**Price:** `0.001 ETH` per pixel (1 finney)  
**Batch limit:** 100 pixels/tx  
**Token ID formula:** `tokenId = y * 1000 + x` (0-indexed coordinates)

## Core Lifecycle

1. **Availability check** → `isPixelOwned(tokenId)` or `getPixelColors(startId, count)`.
2. **Purchase** (step 1) → `purchasePixel` or `purchasePixelBatch` with titles + packed `bytes3` colors. Send `PIXEL_PRICE × count`.
3. **Attach media** (step 2) → `setPixelMedia(tokenId, mediaURI)` once per pixel, immutable.
4. **After sell-out** → owners can `createAuction` → buyers call `buyFromAuction`; `cancelAuction` rolls back.

Media (IPFS URI) can be uploaded _before_ or _after_ purchase, but calling `setPixelMedia` finalizes it forever.

## Key Write Functions

| Function | When to Use | Notes |
| --- | --- | --- |
| `purchasePixel(uint256 tokenId, string title, bytes3 color)` | Buy a single pixel | Send `0.001 ETH`; reverts if already owned or empty title. |
| `purchasePixelBatch(uint256[] tokenIds, string[] titles, bytes3[] colors)` | Buy up to 100 pixels | Arrays must match in length ≤ 100; send `price × count`. |
| `setPixelMedia(uint256 tokenId, string mediaURI)` | Pin IPFS art | Owner-only, one-time, immutable. Use `ipfs://` URIs. |
| `createAuction(uint256 tokenId, uint256 startPrice, uint256 endPrice, uint256 duration)` | List Dutch auction | Allowed only when `allPixelsSold() == true`. Duration 3600–2592000 s. |
| `buyFromAuction(uint256 tokenId)` | Purchase from auction | Pay ≥ `getCurrentAuctionPrice(tokenId)`. 2.5% fee withheld. |
| `cancelAuction(uint256 tokenId)` | Abort auction | Owner-only. |

## Key Read Functions

| Function | Output |
| --- | --- |
| `isPixelOwned(tokenId)` | `bool` availability check. |
| `getPixelData(tokenId)` | `(title, mediaURI, color, purchaseTimestamp, originalBuyer)`.
| `getPixelColors(startId, count)` | `(bytes3[] colors, bool[] owned)` windowed scan (ideal for free-slot detection). |
| `getPixelCoordinates(tokenId)` / `getTokenId(x, y)` | Convert between ID and coordinates. |
| `pixelsSold()` / `allPixelsSold()` | Supply stats + auction unlock flag. |
| `tokenURI(tokenId)` | On-chain Base64 JSON with attributes + IPFS image pointer. |
| `getAuction(tokenId)` / `getCurrentAuctionPrice(tokenId)` | Dutch auction state + live price. |

## Events

- `PixelPurchased(uint256 indexed tokenId, address indexed buyer, string title, bytes3 color, uint256 timestamp)`
- `PixelMediaSet(uint256 indexed tokenId, address indexed owner, string mediaURI)`
- `AuctionCreated(uint256 indexed tokenId, address indexed seller, uint256 startPrice, uint256 endPrice, uint256 duration)`
- `AuctionSettled(uint256 indexed tokenId, address seller, address buyer, uint256 price)`
- `AuctionCancelled(uint256 indexed tokenId, address indexed seller)`

Use `watchContractEvent`/`getContractEvents` (viem) or `contract.on(...)` (ethers v6) for automations.

## IPFS Upload API Quick Reference

```
POST https://millionfinneyhomepage.com/api/ipfs/upload
Content-Type: multipart/form-data
```

| Field | Description |
| --- | --- |
| `file` | Binary media (PNG/JPEG/GIF/WebP/MP3/MP4/etc., ≤ 5 MB). |
| `address` | Wallet address that will own the pixel. |
| `signature` | EIP-191 signature of `Upload media for Million Finney Homepage pixel #<tokenId>`. |
| `tokenId` | Target pixel ID (string or number). |

Response: `{ "cid": "Qm...", "uri": "ipfs://Qm...", "key": "s3-object-key" }`.

Delete unused uploads (if tx failed) via `DELETE /api/ipfs/upload?key=...&address=...&signature=...&tokenId=...`, signing `Delete media for Million Finney Homepage pixel #<tokenId>`.

## Example Snippets

<details>
<summary>Ethers.js (v6) — buy + set media</summary>

```ts
import { ethers } from "ethers";
const provider = new ethers.JsonRpcProvider(process.env.RPC_URL!);
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY!, provider);
const contract = new ethers.Contract(
  "0x0CCBBBAb176EbE9E4b9846C5555f5e89762A31d7",
  ABI,
  wallet,
);

const x = 500;
const y = 250;
const tokenId = y * 1000 + x;

if (!(await contract.isPixelOwned(tokenId))) {
  const buyTx = await contract.purchasePixel(tokenId, "Finney Bot", "0xFF5733", {
    value: ethers.parseEther("0.001"),
  });
  await buyTx.wait();
}

const mediaTx = await contract.setPixelMedia(tokenId, "ipfs://QmYourHash");
await mediaTx.wait();
```

</details>

<details>
<summary>Viem — scan availability window</summary>

```ts
const startId = 200 * 1000 + 100;
const count = 50;
const [colors, owned] = await publicClient.readContract({
  address: CONTRACT,
  abi,
  functionName: "getPixelColors",
  args: [startId, count],
});

const free = [];
for (let i = 0; i < count; i++) {
  if (!owned[i]) {
    const tokenId = startId + i;
    free.push({
      tokenId,
      x: tokenId % 1000,
      y: Math.floor(tokenId / 1000),
      suggestedColor: colors[i] ?? "0x000000",
    });
  }
}
```

</details>

## Auction Checklist

1. Confirm `await contract.allPixelsSold()`.
2. Decide `startPrice`, `endPrice`, `duration` (in seconds).
3. `await contract.createAuction(tokenId, startPrice, endPrice, duration)`.
4. Monitor `AuctionSettled` or `getAuction(tokenId)` to know when it sells.
5. Buyers call `buyFromAuction` with `value >= currentPrice`.

## Troubleshooting

- **`AlreadyOwned` revert:** Pixel taken between availability check and purchase → retry after re-checking `isPixelOwned`.
- **`BatchTooLarge` or `ArrayLengthMismatch`:** Keep ≤ 100 entries; ensure all arrays same length.
- **`MediaAlreadySet`:** Each pixel’s media URI is immutable; ensure you only call `setPixelMedia` once.
- **Upload auth failures:** Make sure the signature message exactly matches the expected string and includes the decimal `tokenId`.
