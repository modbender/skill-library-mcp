# Gigaverse Onboarding Reference

Before entering dungeons, new players must complete onboarding:

1. ✅ Authenticate (JWT)
2. ✅ Mint a Noob character (onchain)
3. ✅ Set a username (part of mint)
4. ✅ Choose a faction

## Wallet Setup

Generate a standard Ethereum wallet (EOA) for Gigaverse:
- Generate a fresh keypair
- Fund with ETH on Abstract chain
- Call contracts directly from your wallet

## Play Modes & Onboarding

Check `~/.config/gigaverse/config.json` for mode:

### Autonomous Mode
```
Agent handles everything automatically:
- Generates username (e.g., "Agent_7x92k")
- Selects faction (random or from config preference)
- Proceeds without asking
- Just needs funded wallet
```

### Interactive Mode
```
Agent asks at each checkpoint:
- "What username would you like for your Noob?"
- "Here are the factions: [list]. Which do you choose?"
- Waits for human response before proceeding
```

## Gate Check

**Block dungeon actions unless ALL are true:**
- `noob != null`
- `username` exists OR `usernames.length > 0`
- Faction doc exists with `FACTION_CID > 0`

If any fail → route to onboarding instead of dungeon.

---

## 1) Authenticate

```bash
curl -X POST https://gigaverse.io/api/user/auth \
  -H "Content-Type: application/json" \
  -d '{
    "signature": "0x...",
    "address": "0x...",
    "message": "Login to Gigaverse at 1730000000000",
    "timestamp": 1730000000000
  }'
```

---

## 2) Check Account State

```bash
curl https://gigaverse.io/api/game/account/0xYOUR_ADDRESS
# or
curl https://gigaverse.io/api/user/gameaccount/0xYOUR_ADDRESS
```

Check response for:
- `noob`: exists or null
- `username`: present or missing
- `canEnterGame`: boolean

---

## 3) Reserve Username & Get Mint Signature

⚠️ **CRITICAL: Username must be lowercase!**

The API signs `username.toLowerCase().trim()`. You MUST use the same normalized username for both the API call and the contract call.

```bash
# Always lowercase!
USERNAME="myusername"  # not "MyUserName"

curl "https://gigaverse.io/api/indexer/usernameAvailable/$USERNAME" \
  -H "Authorization: Bearer YOUR_JWT"
```

Response:
```json
{
  "available": true,
  "signature": "0x..."
}
```

The `signature` is required for the onchain mint call. **Use the exact same lowercase username in the contract call.**

---

## 4) Mint Noob (Onchain)

Call the **AccountSystem** contract at `0x5f8b7eb615D5FCE81fafFb107450EdE201384C00`.

⚠️ **Use the SAME lowercase username from step 3!**

### Option A: Mint with ETH (0.005 ETH)
```solidity
mintWithEth(string _username, bytes signature)
```

```javascript
// Example with viem
await walletClient.writeContract({
  address: '0x5f8b7eb615D5FCE81fafFb107450EdE201384C00',
  abi: mintAbi,
  functionName: 'mintWithEth',
  args: ['myusername', signature],  // lowercase!
  value: parseEther('0.005')
});
```

Payable — requires 0.005 ETH mint fee.

### Option B: Mint with Referral
```solidity
mintWithEthReferral(string _username, address _referrer, bytes signature)
```
Payable — referrer gets bonus.

**Signature source:** The `signature` from step 3 (`/indexer/usernameAvailable`).

---

## 5) Verify Noob & Username

After mint transaction confirms:

```bash
curl https://gigaverse.io/api/account/0xYOUR_ADDRESS
```

Check:
- `noob`: should now exist
- `usernames[]`: should contain your name

---

## 6) Get Faction Options

```bash
curl https://gigaverse.io/api/factions/summary
```

Response includes `entities[]` with:
- Faction IDs
- Names/descriptions
- Expected input cost arrays

---

## 7) Choose Faction

```bash
curl -X POST https://gigaverse.io/api/factions/choose \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "factionId": 1,
    "expectedInputIds": [],
    "expectedInputAmounts": []
  }'
```

For first-time choice, expected arrays are typically empty.

---

## 8) Verify Faction Selection

```bash
curl https://gigaverse.io/api/factions/player/0xYOUR_ADDRESS
```

Confirm:
- Faction record exists
- `FACTION_CID > 0`

---

## 9) Ready for Dungeons!

Only after all gates pass:

```bash
# Check energy
curl https://gigaverse.io/api/offchain/player/energy/0xYOUR_ADDRESS

# Get dungeon info
curl https://gigaverse.io/api/game/dungeon/today \
  -H "Authorization: Bearer YOUR_JWT"

# Start run
curl -X POST https://gigaverse.io/api/game/dungeon/action \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{"action":"start_run","dungeonId":1,"actionToken":0,"data":{...}}'
```

---

## Quick Gate Check Script

```bash
#!/bin/bash
ADDRESS="0xYOUR_ADDRESS"
JWT="YOUR_JWT"

# Check account
ACCOUNT=$(curl -s "https://gigaverse.io/api/game/account/$ADDRESS")

NOOB=$(echo "$ACCOUNT" | jq -r '.noob // empty')
USERNAME=$(echo "$ACCOUNT" | jq -r '.username // .usernames[0] // empty')

# Check faction
FACTION=$(curl -s "https://gigaverse.io/api/factions/player/$ADDRESS")
FACTION_CID=$(echo "$FACTION" | jq -r '.FACTION_CID // 0')

echo "Noob: ${NOOB:-NOT SET}"
echo "Username: ${USERNAME:-NOT SET}"
echo "Faction CID: $FACTION_CID"

if [ -n "$NOOB" ] && [ -n "$USERNAME" ] && [ "$FACTION_CID" -gt 0 ]; then
    echo "✅ Ready for dungeons!"
else
    echo "❌ Onboarding incomplete"
fi
```

---

## Onboarding Flow Summary

```
┌─────────────────────────────────────────────────────────┐
│  1. Authenticate (JWT)                                  │
│       ↓                                                 │
│  2. Check account state                                 │
│       ↓                                                 │
│  ┌─ No noob? ──────────────────────────────────────┐   │
│  │  3. Reserve username → get signature            │   │
│  │  4. Mint noob onchain (contract call)           │   │
│  │  5. Verify noob exists                          │   │
│  └─────────────────────────────────────────────────┘   │
│       ↓                                                 │
│  ┌─ No faction? ───────────────────────────────────┐   │
│  │  6. Get faction options                         │   │
│  │  7. Choose faction                              │   │
│  │  8. Verify faction selection                    │   │
│  └─────────────────────────────────────────────────┘   │
│       ↓                                                 │
│  9. Ready for dungeons! 🎮                              │
└─────────────────────────────────────────────────────────┘
```
