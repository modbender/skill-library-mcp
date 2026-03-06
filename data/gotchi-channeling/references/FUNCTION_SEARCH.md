# Finding channelAlchemica Function

## Contract Info
- **Contract:** Aavegotchi Diamond (Base)
- **Address:** 0xA99c4B08201F2913Db8D28e71d020c4298F29dBF
- **Chain:** Base (8453)

## Possible Function Signatures

Based on Aavegotchi documentation, the function likely has one of these signatures:

### Option 1: Single Parameter (Gotchi ID only)
```solidity
function channelAlchemica(uint256 _gotchiId) external
```
- **Selector:** `0x38d0b418`
- **Use case:** Channel using gotchi on your default parcel

### Option 2: Two Parameters (Realm + Gotchi)
```solidity
function channelAlchemica(uint256 _realmId, uint256 _gotchiId) external
```
- **Selector:** `0x7e27b66f`
- **Use case:** Specify which parcel to channel on

### Option 3: Three Parameters (Realm + Gotchi + Installation)
```solidity
function channelAlchemica(uint256 _realmId, uint256 _gotchiId, uint256 _installationId) external
```
- **Selector:** `0x356dedfb`
- **Use case:** Specify exact Aaltar installation

## How to Find The Real One

### Method 1: Manual Channel Transaction
1. Go to https://verse.aavegotchi.com
2. Channel Gotchi #9638 manually
3. Check transaction on BaseScan
4. View "Input Data" to see actual function call

### Method 2: Contract ABI
- Check BaseScan verified contract
- Look for channelAlchemica in read/write functions
- Extract exact signature

### Method 3: GitHub Source
- Repository: aavegotchi/aavegotchi-realm-diamond
- File: contracts/RealmDiamond/facets/AlchemicaFacet.sol
- Search for: `function channelAlchemica`

## Next Steps

Once we find the correct function:
1. Update `scripts/channel.sh` with correct selector
2. Test with Gotchi #9638 on Parcel #867
3. Verify transaction succeeds
4. Add to automated daily channeling

## Resources

- [Aavegotchi Contracts](https://wiki.aavegotchi.com/en/contracts)
- [Gotchiverse Bible Chapter 3](https://blog.aavegotchi.com/gotchiverse-bible-chapter-3/)
- [BaseScan Contract](https://basescan.org/address/0xA99c4B08201F2913Db8D28e71d020c4298F29dBF)

---

**Status:** Searching for function signature...
**Date:** 2026-02-20
