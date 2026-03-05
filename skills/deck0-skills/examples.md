# Workflow Examples

End-to-end examples showing complete agent workflows with request/response pairs. All examples assume authentication headers are already set (see [auth.md](./auth.md)).

**Base URL**: `https://app.deck-0.com`

---

## 1. Browse and Buy Packs

### Step 1: Browse the shop

```
GET /api/agents/v1/shop/albums?page=1&pageSize=10&inStock=true
```

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "address": "0x1a2b3c4d5e6f7890abcdef1234567890abcdef12",
        "title": "Pixel Legends",
        "description": "A collection of pixel art characters from the retro gaming era",
        "coverImage": "https://storage.deck-0.com/covers/pixel-legends.png",
        "chainId": 33139,
        "packPrice": "1000",
        "totalSupply": "5000",
        "mintedCount": "1200",
        "size": 120
      },
      {
        "address": "0xabcdef1234567890abcdef1234567890abcdef12",
        "title": "Crypto Creatures",
        "description": "Mythical creatures of the blockchain",
        "coverImage": "https://storage.deck-0.com/covers/crypto-creatures.png",
        "chainId": 8453,
        "packPrice": "500",
        "totalSupply": "10000",
        "mintedCount": "3400",
        "size": 200
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 10,
      "total": 2,
      "totalPages": 1
    }
  },
  "share": {
    "url": "/shop",
    "imageUrl": "https://storage.deck-0.com/covers/pixel-legends.png"
  }
}
```

### Step 2: Get collection details

```
GET /api/agents/v1/collections/0x1a2b3c4d5e6f7890abcdef1234567890abcdef12?includeCards=true&includePackOdds=true
```

```json
{
  "success": true,
  "data": {
    "address": "0x1a2b3c4d5e6f7890abcdef1234567890abcdef12",
    "title": "Pixel Legends",
    "description": "A collection of pixel art characters from the retro gaming era",
    "coverImage": "https://storage.deck-0.com/covers/pixel-legends.png",
    "chainId": 33139,
    "packPrice": "1000",
    "totalSupply": "5000",
    "mintedCount": "1200",
    "size": 120,
    "cards": [
      { "id": 1, "name": "Dragon Warrior", "rarity": "legendary", "image": "https://..." },
      { "id": 2, "name": "Pixel Knight", "rarity": "rare", "image": "https://..." }
    ],
    "packOdds": {
      "common": 0.60,
      "uncommon": 0.25,
      "rare": 0.10,
      "legendary": 0.05
    }
  },
  "share": {
    "url": "/collection/0x1a2b3c4d5e6f7890abcdef1234567890abcdef12",
    "imageUrl": "https://storage.deck-0.com/covers/pixel-legends.png"
  }
}
```

### Step 3: Get signed price

```
GET /api/agents/v1/collections/0x1a2b3c4d5e6f7890abcdef1234567890abcdef12/price
```

```json
{
  "success": true,
  "data": {
    "priceInCents": "123",
    "priceInNative": "813008130081300813",
    "expiration": 1706200120,
    "signature": "0x1234567890abcdef...",
    "nonce": "0xabcdef1234567890...",
    "currency": "APE",
    "chainId": 33139,
    "contractAddress": "0x1a2b3c4d5e6f7890abcdef1234567890abcdef12"
  }
}
```

### Step 4: Mint packs on-chain

Using the data from the price response, call `mintPacks` on the album contract. **`packPrice` must come from the collection response (`GET /collections/{address}`), not from `priceInCents` in the price response** (which is the token price per unit, e.g. USD per APE). When using fallback signing, ensure `DECK0_PRIVATE_KEY` is set before running.

```bash
set -euo pipefail
# packPrice = 1000 (from collection details — pack price in USD cents, e.g. $10.00)
# quantity = 2
# priceInNative = 813008130081300813 (from price response)
# value = (1000 * 813008130081300813 * 2) / 100 = 16260162601626016260 wei ≈ 16.26 APE
VALUE=$(echo "1000 * 813008130081300813 * 2 / 100" | bc)

cast send "0x1a2b3c4d5e6f7890abcdef1234567890abcdef12" \
  "mintPacks(address,uint256,uint256,uint256,bytes,bytes32)" \
  "$WALLET" 2 813008130081300813 1706200120 "0x1234567890abcdef..." "0xabcdef1234567890..." \
  --value "$VALUE" \
  --private-key "$DECK0_PRIVATE_KEY" \
  --rpc-url "https://rpc.apechain.com"
```

---

## 2. Open Packs

### Step 1: Check owned packs

First, check your album progress to see how many packs you own:

```
GET /api/agents/v1/me/albums/0x1a2b3c4d5e6f7890abcdef1234567890abcdef12
```

```json
{
  "success": true,
  "data": {
    "address": "0x1a2b3c4d5e6f7890abcdef1234567890abcdef12",
    "title": "Pixel Legends",
    "coverImage": "https://storage.deck-0.com/covers/pixel-legends.png",
    "score": 4500,
    "completion": 0.42,
    "cardsCollected": 50,
    "totalCards": 120,
    "packsOwned": 3,
    "packsOpened": 10
  }
}
```

### Step 2: Open packs on-chain

Call `openPacks` with the pack token IDs (obtained from `PackMinted` events during purchase). When using fallback signing, ensure `DECK0_PRIVATE_KEY` is set.

```bash
set -euo pipefail
cast send "0x1a2b3c4d5e6f7890abcdef1234567890abcdef12" \
  "openPacks(uint256[])" \
  "[42,43,44]" \
  --private-key "$DECK0_PRIVATE_KEY" \
  --rpc-url "https://rpc.apechain.com"
```

Each pack reveals 5 cards. Save the transaction hash from the receipt for the next step.

### Step 3: Poll for pack opening recap

After the `openPacks` transaction confirms, poll the recap endpoint to get card details and badges. The transaction takes 15-30 seconds to be indexed.

```bash
set -euo pipefail
TX_HASH="0x..."  # from openPacks transaction (must be from a trusted source, e.g. your own receipt)
CHAIN_ID=33139   # Apechain Mainnet

# Validate tx hash format before interpolating into the request (avoids injection if TX_HASH were ever user-supplied)
[[ "$TX_HASH" =~ ^0x[a-fA-F0-9]{64}$ ]] || { echo "Invalid tx hash format"; exit 1; }

# Poll every 5 seconds, up to 6 retries (~30 seconds). Uses make_authenticated_request_capture from auth.md.
for attempt in $(seq 1 6); do
  HTTP_CODE=$(make_authenticated_request_capture \
    "/api/agents/v1/me/pack-opening/${TX_HASH}" \
    "chainId=${CHAIN_ID}" \
    /tmp/recap.json)

  if [ "$HTTP_CODE" = "200" ]; then
    jq . /tmp/recap.json
    break
  fi

  if [ "$HTTP_CODE" = "404" ]; then
    echo "Not indexed yet, retrying in 5s... (attempt $attempt/6)"
    sleep 5
    continue
  fi

  echo "Recap failed with HTTP $HTTP_CODE"
  break
done
```

Response:

```json
{
  "success": true,
  "data": {
    "album": {
      "id": "album-1",
      "address": "0x1a2b3c4d5e6f7890abcdef1234567890abcdef12",
      "title": "Pixel Legends",
      "coverImage": "https://storage.deck-0.com/covers/pixel-legends.png"
    },
    "cards": [
      {
        "id": "card-1",
        "tokenId": "500",
        "serial": 7,
        "metadataId": "meta-3",
        "metadata": { "id": "meta-3", "name": "Dragon Warrior", "rarity": "legendary" },
        "badges": { "isNew": true, "firstPulled": false, "bestSerial": false, "bestSerialInGuild": false, "improvedSerial": true },
        "url": "https://app.deck-0.com/collection/0x1a2b3c4d5e6f7890abcdef1234567890abcdef12/500"
      },
      {
        "id": "card-2",
        "tokenId": "501",
        "serial": 42,
        "metadataId": "meta-7",
        "metadata": { "id": "meta-7", "name": "Pixel Knight", "rarity": "rare" },
        "badges": { "isNew": false, "firstPulled": false, "bestSerial": false, "bestSerialInGuild": false, "improvedSerial": false },
        "url": "https://app.deck-0.com/collection/0x1a2b3c4d5e6f7890abcdef1234567890abcdef12/501"
      }
    ],
    "packs": [{ "tokenId": "42", "metadata": null }],
    "newCards": ["500"],
    "firstPulled": [],
    "bestSerials": [],
    "bestSerialsInGuild": [],
    "improvedSerials": ["500"],
    "collector": "myusername"
  },
  "share": {
    "url": "/collection/0x1a2b3c4d5e6f7890abcdef1234567890abcdef12/pack-opening/0xabc.../recap"
  }
}
```

---

## 3. Track Collection Progress

### List all your collections

```
GET /api/agents/v1/me/albums?sortBy=completion&sortOrder=desc
```

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "address": "0x1a2b3c4d5e6f7890abcdef1234567890abcdef12",
        "title": "Pixel Legends",
        "coverImage": "https://...",
        "score": 9500,
        "completion": 0.96,
        "cardsCollected": 115,
        "totalCards": 120,
        "packsOwned": 0,
        "packsOpened": 25
      },
      {
        "address": "0xabcdef1234567890abcdef1234567890abcdef12",
        "title": "Crypto Creatures",
        "coverImage": "https://...",
        "score": 2100,
        "completion": 0.35,
        "cardsCollected": 70,
        "totalCards": 200,
        "packsOwned": 5,
        "packsOpened": 15
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 2,
      "totalPages": 1
    }
  }
}
```

### View leaderboard

```
GET /api/agents/v1/collections/0x1a2b3c4d5e6f7890abcdef1234567890abcdef12/leaderboard?type=user&page=1&pageSize=5
```

```json
{
  "success": true,
  "data": {
    "collection": {
      "address": "0x1a2b3c4d5e6f7890abcdef1234567890abcdef12",
      "title": "Pixel Legends",
      "coverImage": "https://..."
    },
    "leaderboard": [
      { "rank": 1, "address": "0xaaaa...", "score": 12000, "cardsCollected": 120, "totalCards": 120 },
      { "rank": 2, "address": "0xbbbb...", "score": 11500, "cardsCollected": 119, "totalCards": 120 },
      { "rank": 3, "address": "0xcccc...", "score": 9500, "cardsCollected": 115, "totalCards": 120 }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 5,
      "total": 200,
      "totalPages": 40
    }
  }
}
```

### View guild leaderboard

```
GET /api/agents/v1/collections/0x1a2b3c4d5e6f7890abcdef1234567890abcdef12/leaderboard?type=guild
```

---

## 4. Publisher Application Flow

### Step 1: Check if you already have an application

```
GET /api/agents/v1/publisher/application
```

If no application exists:

```json
{
  "success": false,
  "error": {
    "code": "AGENT_NOT_FOUND",
    "message": "No application found"
  }
}
```

### Step 2: Submit an application

```
POST /api/agents/v1/publisher/application
Content-Type: application/json

{
  "collection": {
    "title": "Arcade Heroes",
    "description": "A nostalgic collection featuring iconic arcade game characters reimagined as trading cards. Each card features unique pixel art and gameplay stats.",
    "size": 120,
    "chainId": 33139
  },
  "motivationalLetter": "As a lifelong arcade enthusiast and digital artist, I want to bring the magic of retro gaming to the blockchain. I have a team of 3 pixel artists and a community of 5,000 retro gaming fans ready to collect. Our collection will feature 120 unique cards across 4 rarity tiers, each with original artwork inspired by classic arcade cabinets."
}
```

Response (201 Created):

```json
{
  "success": true,
  "data": {
    "walletAddress": "0xabcd...1234",
    "status": "PENDING",
    "collection": {
      "title": "Arcade Heroes",
      "description": "A nostalgic collection featuring iconic arcade game characters...",
      "size": 120,
      "chainId": 33139
    },
    "motivationalLetter": "As a lifelong arcade enthusiast...",
    "rejectionReason": null,
    "submittedAt": "2025-01-25T10:30:00.000Z",
    "updatedAt": "2025-01-25T10:30:00.000Z"
  }
}
```

### Step 3: Check status later

```
GET /api/agents/v1/publisher/application
```

If rejected:

```json
{
  "success": true,
  "data": {
    "walletAddress": "0xabcd...1234",
    "status": "REJECTED",
    "collection": {
      "title": "Arcade Heroes",
      "description": "A nostalgic collection...",
      "size": 120,
      "chainId": 33139
    },
    "motivationalLetter": "As a lifelong arcade enthusiast...",
    "rejectionReason": "Please provide more details about the artwork and card distribution plan.",
    "submittedAt": "2025-01-25T10:30:00.000Z",
    "updatedAt": "2025-01-26T14:00:00.000Z"
  }
}
```

### Step 4: Resubmit after rejection

Update your application and resubmit via `POST /api/agents/v1/publisher/application` with an improved motivational letter or collection details. The same endpoint handles both initial submissions and resubmissions. Returns 200 on resubmission.
