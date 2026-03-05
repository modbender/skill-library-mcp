# channelAlchemica Function Signature

## ✅ FOUND!

**Contract:** Aavegotchi REALM Diamond  
**Source:** https://github.com/aavegotchi/aavegotchi-realm-diamond  
**File:** contracts/RealmDiamond/facets/AlchemicaFacet.sol

## Function Signature

```solidity
function channelAlchemica(
    uint256 _realmId, 
    uint256 _gotchiId,
    uint256 _lastChanneled,
    bytes memory _signature
) external diamondPaused gameActive
```

**Function Selector:** `cast sig "channelAlchemica(uint256,uint256,uint256,bytes)"`

## Parameters

1. **_realmId** (uint256) - Your REALM parcel token ID
   - Example: 867 (your parcel)

2. **_gotchiId** (uint256) - Your Aavegotchi token ID  
   - Example: 9638

3. **_lastChanneled** (uint256) - Timestamp of last channeling for this gotchi
   - Get from: `s.gotchiChannelings[_gotchiId]`
   - First time: 0

4. **_signature** (bytes) - Backend signature for anti-bot protection
   - **⚠️ CRITICAL:** Requires backend API call to get signature
   - Signature validates: keccak256(abi.encodePacked(_realmId, _gotchiId, _lastChanneled))

## Key Requirements

### 1. **24-Hour Cooldown**
```solidity
if (s.lastChanneledDay[_gotchiId] == block.timestamp / (60 * 60 * 24)) 
    revert("AlchemicaFacet: Gotchi can't channel yet");
```

### 2. **Aaltar Must Be Equipped**
```solidity
require(altarLevel > 0, "AlchemicaFacet: Must equip Altar");
```

### 3. **Parcel Cooldown (Aaltar Level Dependent)**
```solidity
require(
    block.timestamp >= s.parcelChannelings[_realmId] + s.channelingLimits[altarLevel], 
    "AlchemicaFacet: Parcel can't channel yet"
);
```

### 4. **Backend Signature Validation**
```solidity
require(
    LibSignature.isValid(
        keccak256(abi.encodePacked(_realmId, _gotchiId, _lastChanneled)), 
        _signature, 
        s.backendPubKey
    ),
    "AlchemicaFacet: Invalid signature"
);
```

## ⚠️ BLOCKER: Backend Signature Required

**The function REQUIRES a signature from Aavegotchi's backend server.**

This signature:
- Prevents botting/automation
- Validates the channeling request
- Cannot be generated without access to backend private key

## Solutions

### Option 1: Use Gotchiverse UI (Manual)
- Visit https://verse.aavegotchi.com
- Gotchiverse frontend calls backend API to get signature
- Click "Channel" button - signature included automatically

### Option 2: Reverse Engineer Backend API (Advanced)
- Monitor network traffic in Gotchiverse
- Find the backend API endpoint for signatures
- Call it programmatically before channeling
- **Risk:** API may have rate limits or require auth

### Option 3: Browser Automation (Hybrid)
- Use Selenium/Puppeteer to automate Gotchiverse UI
- Let frontend handle signature fetching
- Programmatically click "Channel" button

### Option 4: Contact Aavegotchi Team
- Request official API access for channeling
- Explain automation use case
- Get authorized signature endpoint

## Recommended Path Forward

**For now:** The skill **cannot** do fully autonomous channeling due to the signature requirement.

**Alternative:** Build a **channeling reminder** skill instead:
- Check if channeling is available (read-only)
- Notify you when ready to channel
- Provide direct link to Gotchiverse
- Track your channeling history

## Updated Skill Scope

Instead of autonomous channeling, we can build:

1. **Channeling Status Checker**
   - Check 24h cooldown
   - Verify Aaltar equipped
   - Calculate next available time

2. **Channeling Reminder System**
   - Daily notifications
   - "Ready to channel!" alerts
   - One-click link to Gotchiverse

3. **Channeling History Tracker**
   - Log when you channel
   - Track rewards earned
   - Calculate total Alchemica farmed

Would you like me to pivot the skill to this approach?

---

**Date:** 2026-02-20  
**Status:** Function found, signature blocker identified  
**Next:** Redesign skill as reminder/tracker system
