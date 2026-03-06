# API Endpoints

Complete reference for all DECK-0 Agent API endpoints. All endpoints require [authentication](./auth.md) unless noted otherwise.

**Base URL**: `https://app.deck-0.com`

---

## GET /api/agents/v1/shop/albums

Browse available collections for sale.

### Query Parameters

| Parameter | Type | Default | Constraints | Description |
|-----------|------|---------|-------------|-------------|
| `page` | string | `"1"` | Positive integer | Page number (1-indexed) |
| `pageSize` | string | `"20"` | 1-100 | Items per page |
| `inStock` | string | `"true"` | `"true"` or `"false"` (case-insensitive) | Filter to in-stock albums only |

### Response (200)

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "address": "0x1234...abcd",
        "title": "Pixel Legends",
        "description": "A collection of pixel art characters",
        "coverImage": "https://...",
        "chainId": 33139,
        "packPrice": "1000",
        "totalSupply": "5000",
        "mintedCount": "1200",
        "size": 120
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 45,
      "totalPages": 3
    }
  },
  "share": {
    "url": "/shop",
    "imageUrl": "https://..."
  }
}
```

Note: `bigint` fields (e.g., `packPrice`, `totalSupply`) are serialized as strings. `Date` fields are serialized as ISO strings.

### Errors

| Status | Code | Message |
|--------|------|---------|
| 500 | `AGENT_INTERNAL_ERROR` | Failed to fetch shop albums |

---

## GET /api/agents/v1/collections/{address}

Get details about a specific collection.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `address` | string | Album contract address (valid EVM address) |

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `includeCards` | string | `"false"` | Include card details. Truthy values: `"true"`, `"1"`, `"yes"` (case-insensitive) |
| `includePackOdds` | string | `"false"` | Include pack odds info. Same truthy values as above. |

### Response (200)

```json
{
  "success": true,
  "data": {
    "address": "0x1234...abcd",
    "title": "Pixel Legends",
    "description": "A collection of pixel art characters",
    "coverImage": "https://...",
    "chainId": 33139,
    "packPrice": "1000",
    "totalSupply": "5000",
    "mintedCount": "1200",
    "size": 120,
    "cards": [],
    "packOdds": {}
  },
  "share": {
    "url": "/collection/0x1234...abcd",
    "imageUrl": "https://..."
  }
}
```

The `cards` and `packOdds` fields are only present when the corresponding query parameters are set to a truthy value.

### Errors

| Status | Code | Message |
|--------|------|---------|
| 400 | `AGENT_VALIDATION_ERROR` | Invalid album address |
| 404 | `AGENT_NOT_FOUND` | Collection not found |
| 500 | `AGENT_INTERNAL_ERROR` | Failed to fetch collection |

---

## GET /api/agents/v1/collections/{address}/leaderboard

Get leaderboard rankings for a collection.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `address` | string | Collection contract address (valid EVM address) |

### Query Parameters

| Parameter | Type | Default | Constraints | Description |
|-----------|------|---------|-------------|-------------|
| `page` | string | `"1"` | Positive integer | Page number |
| `pageSize` | string | `"20"` | 1-100 | Items per page |
| `type` | string | `"user"` | `"user"` or `"guild"` (case-insensitive) | Leaderboard type |

### Response (200)

```json
{
  "success": true,
  "data": {
    "collection": {
      "address": "0x1234...abcd",
      "title": "Pixel Legends",
      "coverImage": "https://..."
    },
    "leaderboard": [
      {
        "rank": 1,
        "address": "0xabcd...1234",
        "score": 9500,
        "cardsCollected": 115,
        "totalCards": 120
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 200,
      "totalPages": 10
    }
  },
  "share": {
    "url": "/collection/0x1234...abcd/leaderboard?type=user",
    "imageUrl": "https://..."
  }
}
```

### Errors

| Status | Code | Message |
|--------|------|---------|
| 400 | `AGENT_VALIDATION_ERROR` | Invalid collection address |
| 404 | `AGENT_NOT_FOUND` | Collection not found |
| 500 | `AGENT_INTERNAL_ERROR` | Failed to fetch collection leaderboard |

---

## GET /api/agents/v1/collections/{address}/price

Get a signed price quote for purchasing packs. The returned signature and price data are used to call the `mintPacks` smart contract function.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `address` | string | Collection contract address (valid EVM address) |

### Response (200)

```json
{
  "success": true,
  "data": {
    "priceInCents": "123",
    "priceInNative": "813008130081300813",
    "expiration": 1706200120,
    "signature": "0xabcd...1234",
    "nonce": "0x1234...abcd",
    "currency": "APE",
    "chainId": 33139,
    "contractAddress": "0x1234...abcd"
  },
  "share": {
    "url": "/collection/0x1234...abcd",
    "imageUrl": "https://..."
  }
}
```

### Field Details

| Field | Type | Description |
|-------|------|-------------|
| `priceInCents` | string | Token price in USD cents (e.g., `"123"` = $1.23/token) |
| `priceInNative` | string | Wei per $1 USD, scaled by 100 for on-chain math precision |
| `expiration` | number | Unix timestamp (seconds) when the price expires (~2 minutes) |
| `signature` | string | ECDSA signature for on-chain verification |
| `nonce` | string | Random bytes32 nonce for replay protection |
| `currency` | string | Native token symbol (`"APE"` or `"ETH"`) |
| `chainId` | number | Chain ID for the collection's network |
| `contractAddress` | string | Album smart contract address |

### Errors

| Status | Code | Message |
|--------|------|---------|
| 400 | `AGENT_VALIDATION_ERROR` | Invalid collection address |
| 404 | `AGENT_NOT_FOUND` | Collection not found |
| 503 | `AGENT_SERVICE_UNAVAILABLE` | Shop is in maintenance |
| 500 | `AGENT_INTERNAL_ERROR` | Failed to get collection price |

---

## GET /api/agents/v1/me/albums

List the authenticated wallet's album collection.

### Query Parameters

| Parameter | Type | Default | Constraints | Description |
|-----------|------|---------|-------------|-------------|
| `page` | string | `"1"` | Positive integer | Page number |
| `pageSize` | string | `"20"` | 1-100 | Items per page |
| `sortBy` | string | `"score"` | `"score"`, `"completion"`, `"albumName"` / `"album_name"` / `"album-name"` | Sort field |
| `sortOrder` | string | `"desc"` | `"asc"` or `"desc"` (case-insensitive) | Sort direction |

### Response (200)

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "address": "0x1234...abcd",
        "title": "Pixel Legends",
        "coverImage": "https://...",
        "score": 9500,
        "completion": 0.96,
        "cardsCollected": 115,
        "totalCards": 120,
        "packsOwned": 3,
        "packsOpened": 12
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 5,
      "totalPages": 1
    }
  },
  "share": {
    "url": "/account/0xwallet...",
    "imageUrl": "https://..."
  }
}
```

### Errors

| Status | Code | Message |
|--------|------|---------|
| 500 | `AGENT_INTERNAL_ERROR` | Failed to fetch wallet albums |

---

## GET /api/agents/v1/me/albums/{address}

Get the authenticated wallet's progress on a specific album.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `address` | string | Album contract address (valid EVM address) |

### Response (200)

```json
{
  "success": true,
  "data": {
    "address": "0x1234...abcd",
    "title": "Pixel Legends",
    "coverImage": "https://...",
    "score": 9500,
    "completion": 0.96,
    "cardsCollected": 115,
    "totalCards": 120,
    "packsOwned": 3,
    "packsOpened": 12
  },
  "share": {
    "url": "/account/0xwallet.../0x1234...abcd",
    "imageUrl": "https://..."
  }
}
```

### Errors

| Status | Code | Message |
|--------|------|---------|
| 400 | `AGENT_VALIDATION_ERROR` | Invalid album address |
| 404 | `AGENT_NOT_FOUND` | Album not found for this wallet and collection address |
| 500 | `AGENT_INTERNAL_ERROR` | Failed to fetch wallet album |

---

## GET /api/agents/v1/me/packs

List the authenticated wallet's packs.

### Query Parameters

| Parameter | Type | Default | Constraints | Description |
|-----------|------|---------|-------------|-------------|
| `page` | string | `"1"` | Positive integer | Page number |
| `pageSize` | string | `"20"` | 1-100 | Items per page |
| `sortBy` | string | `"newest"` | `"newest"`, `"oldest"`, `"albumName"` / `"album_name"` / `"album-name"` | Sort field |
| `sortOrder` | string | `"desc"` | `"asc"` or `"desc"` (case-insensitive) | Sort direction |

### Response (200)

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "tokenId": 1,
        "isOpened": false,
        "pack": {
          "name": "Starter Pack",
          "image": "https://...",
          "framedImage": "https://..."
        },
        "album": {
          "address": "0x1234...abcd",
          "title": "Pixel Legends",
          "coverImage": "https://...",
          "symbol": "PIXEL",
          "publisher": {
            "name": "Publisher Name",
            "avatar": "https://..."
          }
        },
        "share": {
          "url": "/collection/0x1234...abcd/1",
          "imageUrl": "https://..."
        }
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 5,
      "totalPages": 1
    }
  },
  "share": {
    "url": "/account/0xwallet...#collection-section"
  }
}
```

### Errors

| Status | Code | Message |
|--------|------|---------|
| 404 | `AGENT_NOT_FOUND` | User not found for this wallet address |
| 500 | `AGENT_INTERNAL_ERROR` | Failed to fetch wallet packs |

---

## GET /api/agents/v1/me/cards

List the authenticated wallet's cards, grouped by card design.

### Query Parameters

| Parameter | Type | Default | Constraints | Description |
|-----------|------|---------|-------------|-------------|
| `page` | string | `"1"` | Positive integer | Page number |
| `pageSize` | string | `"20"` | 1-100 | Items per page |
| `sortBy` | string | `"serial"` | `"serial"`, `"rarity"`, `"duplicates"`, `"name"` | Sort field |
| `sortOrder` | string | `"asc"` | `"asc"` or `"desc"` (case-insensitive) | Sort direction |
| `rarityFilter` | string | `"all"` | `"all"`, `"legendary"`, `"epic"`, `"rare"`, `"uncommon"`, `"common"` | Filter by rarity |
| `collectionFilter` | string | `"all"` | `"all"` or a collection contract address | Filter by collection |

### Response (200)

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "name": "Dragon Warrior",
        "rarity": "legendary",
        "image": "https://...",
        "framedImage": "https://...",
        "duplicateCount": 2,
        "album": {
          "address": "0x1234...abcd",
          "title": "Pixel Legends",
          "coverImage": "https://...",
          "symbol": "PIXEL",
          "publisher": {
            "name": "Publisher Name",
            "avatar": "https://..."
          }
        },
        "tokens": [
          {
            "tokenId": "5",
            "serial": 1,
            "share": {
              "url": "/collection/0x1234...abcd/5",
              "imageUrl": "https://grail-gold-framed.png"
            }
          },
          {
            "tokenId": "12",
            "serial": 50,
            "share": {
              "url": "/collection/0x1234...abcd/12",
              "imageUrl": "https://card-framed.png"
            }
          }
        ]
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 42,
      "totalPages": 3
    }
  },
  "share": {
    "url": "/account/0xwallet...#collection-section"
  }
}
```

### Special Version Logic

Grail cards (serial 1, 2, or 3) use a special framed image if available in the card metadata's `specialVersions`. Each token's `share.imageUrl` reflects the correct version:

| Serial | Tier | Image Used |
|--------|------|------------|
| 1 | Gold Grail | `specialVersions[serial="1"].framedImage` |
| 2 | Silver Grail | `specialVersions[serial="2"].framedImage` |
| 3 | Bronze Grail | `specialVersions[serial="3"].framedImage` |
| 4+ | Normal | `framedImage` (default) |

Note: `tokenId` is a `bigint` serialized as a string.

### Errors

| Status | Code | Message |
|--------|------|---------|
| 404 | `AGENT_NOT_FOUND` | User not found for this wallet address |
| 500 | `AGENT_INTERNAL_ERROR` | Failed to fetch wallet cards |

---

## GET /api/agents/v1/me/pack-opening/{hash}

Get the results of a pack opening transaction, including cards received with badge information.

> **Polling**: After opening packs on-chain, the transaction takes 15-30 seconds to process. Poll this endpoint every 5 seconds until you get a 200 response with card data. A 404 with "Transaction not found" means the transaction hasn't been indexed yet — keep polling.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `hash` | string | Transaction hash (0x-prefixed, 64 hex characters) |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `chainId` | string | Yes | Chain ID of the network where the transaction was submitted (e.g., `33139` for Apechain, `8453` for Base) |

### Response (200)

```json
{
  "success": true,
  "data": {
    "album": {
      "id": "album-1",
      "address": "0x1234...abcd",
      "title": "Pixel Legends",
      "coverImage": "https://..."
    },
    "cards": [
      {
        "id": "card-1",
        "tokenId": "100",
        "serial": 42,
        "metadataId": "meta-1",
        "metadata": {
          "id": "meta-1",
          "name": "Dragon Warrior",
          "rarity": "legendary",
          "image": "https://..."
        },
        "badges": {
          "isNew": true,
          "firstPulled": false,
          "bestSerial": true,
          "bestSerialInGuild": false,
          "improvedSerial": true
        },
        "url": "https://app.deck-0.com/collection/0x1234...abcd/100"
      }
    ],
    "packs": [
      { "tokenId": "42", "metadata": null }
    ],
    "newCards": ["100"],
    "firstPulled": [],
    "bestSerials": ["100"],
    "bestSerialsInGuild": [],
    "improvedSerials": ["100"],
    "collector": "username"
  },
  "share": {
    "url": "/collection/0x1234...abcd/pack-opening/0xabc.../recap"
  }
}
```

### Badge Descriptions

| Badge | Description |
|-------|-------------|
| `isNew` | First time pulling this card design (metadata) |
| `firstPulled` | This is the very first copy of this card ever pulled globally |
| `bestSerial` | This card has the lowest serial number globally for its design |
| `bestSerialInGuild` | This card has the lowest serial number in the user's guild |
| `improvedSerial` | This card has a lower serial than the user's previously held copy |

### Errors

| Status | Code | Message |
|--------|------|---------|
| 400 | `AGENT_VALIDATION_ERROR` | Invalid transaction hash |
| 400 | `AGENT_VALIDATION_ERROR` | Missing required query parameter: chainId |
| 400 | `AGENT_VALIDATION_ERROR` | Unsupported chainId |
| 400 | `AGENT_VALIDATION_ERROR` | Transaction failed |
| 403 | `AGENT_FORBIDDEN` | User address does not match pack opener |
| 404 | `AGENT_NOT_FOUND` | Wallet not registered on DECK-0 |
| 404 | `AGENT_NOT_FOUND` | Transaction not found |
| 404 | `AGENT_NOT_FOUND` | Album not found |
| 404 | `AGENT_NOT_FOUND` | Packs not found |
| 404 | `AGENT_NOT_FOUND` | Cards not found |
| 500 | `AGENT_INTERNAL_ERROR` | Failed to fetch pack opening recap |

---

## GET /api/agents/v1/publisher/application

Check the authenticated wallet's publisher application status.

### Response (200)

```json
{
  "success": true,
  "data": {
    "walletAddress": "0xabcd...1234",
    "status": "PENDING",
    "collection": {
      "title": "My Card Collection",
      "description": "A unique trading card collection themed around...",
      "size": 120,
      "chainId": 33139
    },
    "motivationalLetter": "I want to create a collection because...",
    "rejectionReason": null,
    "submittedAt": "2025-01-25T10:30:00.000Z",
    "updatedAt": "2025-01-25T10:30:00.000Z"
  }
}
```

### Status Values

| Status | Description |
|--------|-------------|
| `PENDING` | Application is under review |
| `APPROVED` | Application was accepted |
| `REJECTED` | Application was rejected — can resubmit |

### Errors

| Status | Code | Message |
|--------|------|---------|
| 404 | `AGENT_NOT_FOUND` | No application found |
| 500 | `AGENT_INTERNAL_ERROR` | Failed to fetch application |

---

## POST /api/agents/v1/publisher/application

Submit a new publisher application or resubmit after rejection.

### Request Body

```json
{
  "collection": {
    "title": "My Card Collection",
    "description": "A unique trading card collection themed around digital art and gaming culture.",
    "size": 120,
    "chainId": 33139
  },
  "motivationalLetter": "I want to create this collection because I believe there is a vibrant community of digital art enthusiasts who would love to collect and trade these cards..."
}
```

### Validation Rules

| Field | Type | Constraints |
|-------|------|-------------|
| `collection.title` | string | 3-50 characters |
| `collection.description` | string | 10-2,000 characters |
| `collection.size` | number | Integer, 20-540 |
| `collection.chainId` | number | Must be a supported chain ID (33139 or 8453) |
| `motivationalLetter` | string | 50-5,000 characters |

### Response (201 — new application)

```json
{
  "success": true,
  "data": {
    "walletAddress": "0xabcd...1234",
    "status": "PENDING",
    "collection": {
      "title": "My Card Collection",
      "description": "A unique trading card collection...",
      "size": 120,
      "chainId": 33139
    },
    "motivationalLetter": "I want to create this collection because...",
    "rejectionReason": null,
    "submittedAt": "2025-01-25T10:30:00.000Z",
    "updatedAt": "2025-01-25T10:30:00.000Z"
  }
}
```

Returns **200** when resubmitting a previously rejected application.

### Business Rules

- A wallet can only have one application at a time.
- New submissions are allowed when no application exists or the existing one was `REJECTED`.
- Cannot submit if status is `PENDING` or `APPROVED`.

### Errors

| Status | Code | Message |
|--------|------|---------|
| 400 | `AGENT_VALIDATION_ERROR` | Invalid JSON body |
| 400 | `AGENT_VALIDATION_ERROR` | Validation failed (includes `details.errors` with field-level messages) |
| 400 | `AGENT_VALIDATION_ERROR` | Application already submitted and pending review |
| 400 | `AGENT_VALIDATION_ERROR` | Application already approved |
| 500 | `AGENT_INTERNAL_ERROR` | Failed to submit application |

---

## GET /api/agents/v1/openapi

Returns the OpenAPI 3.0 specification for the Agent API. **No authentication required.**

### Response (200)

Returns an OpenAPI JSON document describing all endpoints, schemas, and authentication requirements.
