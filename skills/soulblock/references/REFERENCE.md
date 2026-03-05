# SoulBlocks Skill Reference

## Environment Variables (Optional Overrides)

The skill uses built-in defaults for the Base mainnet contract and RPC. Set these only to override:

- `SOULBLOCKS_CONTRACT_ADDRESS`: Overrides the built-in contract address.
- `SOULBLOCK_RPC_URL`: Overrides the default RPC (`https://mainnet.base.org`).

Additional fallbacks supported by `scripts/fetch.ts`:

- `NEXT_PUBLIC_CONTRACT_ADDRESS`
- `NEXT_PUBLIC_RPC_URL`

## Chain and Limits

- Chain ID: `8453` (Base mainnet)
- Mint price: `0.02 ETH`
- Max fragments per token: `64`
- Max fragment size: `2048` bytes
- Fragment separator for reconstruction: `\n\n`

## Deep Link Formats

- Mint: `https://soulblocks.ai/mint`
- Append (one-click): `https://soulblocks.ai/append/<token-id>?content=<URL-encoded-fragment-text>`
- Append (short link): `https://soulblocks.ai/append/<token-id>`

Build a one-click append URL from terminal:

```bash
TOKEN_ID=42
FRAGMENT_TEXT="Your new fragment"
ENCODED_CONTENT=$(node -e 'console.log(encodeURIComponent(process.argv[1]))' "$FRAGMENT_TEXT")
echo "https://soulblocks.ai/append/${TOKEN_ID}?content=${ENCODED_CONTENT}"
```

## ClawHub Publish Target

From monorepo root, publish only this skill folder:

```bash
npx @openclaw/clawhub publish skills/soulblock
```

## Contract Methods Used by the Skill

- `ownerOf(uint256)`
- `getFragmentCount(uint256)`
- `getFragmentContent(uint256,uint256)`
- `getGenesisBlock(uint256)`
- `getMinter(uint256)`
