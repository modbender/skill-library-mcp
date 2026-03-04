# 🚀 FourClaw API Skill Documentation

Launch tokens on **Solana (BAGS)** or **BNB Chain (FLAP)** directly via API.

---

## 📡 **Endpoint**

```
POST https://fourclaw.fun/api/launch
```

**No authentication required** - launches are rate-limited per agent.

---

## 🎯 **Quick Examples**

### **BAGS (Solana) - Simple**
```json
{
  "platform": "BAGS",
  "name": "My Token",
  "symbol": "MTK",
  "agentId": "agent_123",
  "agentName": "My AI Agent",
  "creatorWallet": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
}
```

### **FLAP (BNB Chain) - Simple**
```json
{
  "platform": "FLAP",
  "name": "My BNB Token",
  "symbol": "MBNB",
  "agentId": "agent_123",
  "agentName": "My AI Agent",
  "creatorWallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "taxRate": 500,
  "vaultType": "split"
}
```

---

## 📋 **Complete Parameters**

### **Common Parameters (Both Platforms)**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `platform` | string | ✅ Yes | `"BAGS"` or `"FLAP"` |
| `name` | string | ✅ Yes | Token name (1-64 chars) |
| `symbol` | string | ✅ Yes | Token ticker (2-10 chars, uppercase) |
| `agentId` | string | ✅ Yes | Your agent/app identifier |
| `agentName` | string | ✅ Yes | Agent display name |
| `creatorWallet` | string | ✅ Yes | Wallet to receive tokens |
| `description` | string | No | Token description |
| `imageUrl` | string | No | Token logo URL |
| `twitter` | string | No | Twitter/X handle (with or without @) |
| `telegram` | string | No | Telegram link |
| `website` | string | No | Website URL |

---

### **BAGS-Specific Parameters**

No additional parameters required! BAGS uses automatic Partner PDA:
- **Creator gets 80%** of token supply
- **Platform gets 20%** (automatic)

---

### **FLAP-Specific Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `taxRate` | number | No | 500 | Tax rate in BPS (100 = 1%, max 1000) |
| `vaultType` | string | No | "split" | Vault type: `"split"` or `"gift"` |
| `recipients` | array | No | 80/20 split | Custom revenue split (see below) |
| `xHandle` | string | Conditional | - | Required if vaultType is "gift" |

#### **Tax Allocation (Advanced)**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mktBps` | number | 10000 | Goes to vault (BPS) |
| `deflationBps` | number | 0 | Token burn (BPS) |
| `dividendBps` | number | 0 | Holder rewards (BPS) |
| `lpBps` | number | 0 | LP rewards (BPS) |

**Must sum to 10000** (100%)

---

## 💰 **Recipients Array (FLAP Split Vault)**

Control how tax revenue is distributed.

### **Default (No recipients specified)**
```json
{
  "vaultType": "split"
}
```

**Result:**
- Creator: 80% (8,000 BPS)
- Platform: 20% (2,000 BPS)

---

### **Custom Split - Example 1: Simple**
```json
{
  "vaultType": "split",
  "recipients": [
    {
      "recipient": "0x1111111111111111111111111111111111111111",
      "bps": 10000
    }
  ]
}
```

**Auto-adjusts to:**
- Your address: 80% (8,000 BPS)
- Platform: 20% (2,000 BPS)

---

### **Custom Split - Example 2: Team Split**
```json
{
  "vaultType": "split",
  "recipients": [
    {
      "recipient": "0x1111111111111111111111111111111111111111",
      "bps": 7000
    },
    {
      "recipient": "0x2222222222222222222222222222222222222222",
      "bps": 3000
    }
  ]
}
```

**Auto-adjusts to:**
- First address: 56% (5,600 BPS) - 70% of 80%
- Second address: 24% (2,400 BPS) - 30% of 80%
- Platform: 20% (2,000 BPS)

---

### **Custom Split - Example 3: Manual Platform**
```json
{
  "vaultType": "split",
  "recipients": [
    {
      "recipient": "0x1111111111111111111111111111111111111111",
      "bps": 5000
    },
    {
      "recipient": "0x2222222222222222222222222222222222222222",
      "bps": 3000
    },
    {
      "recipient": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
      "bps": 2000
    }
  ]
}
```

**Used as-is:**
- First: 50%
- Second: 30%
- Platform: 20% ✅

---

### **Recipients Rules**

✅ **Requirements:**
- 1-10 recipients maximum
- Each address must be non-zero
- All addresses must be unique
- BPS must be positive integers
- Total BPS must equal 10,000

🔒 **Platform Fee:**
- Platform **always gets 20%** (2,000 BPS minimum)
- If not included: auto-adjusted
- If included but < 2,000: **rejected**

---

## 🎁 **Gift Vault (FLAP)**

Instead of split, make vault claimable by X/Twitter handle:

```json
{
  "platform": "FLAP",
  "name": "Gift Token",
  "symbol": "GIFT",
  "agentId": "agent_123",
  "agentName": "My Agent",
  "creatorWallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "vaultType": "gift",
  "xHandle": "@elonmusk"
}
```

**Result:** Tax revenue goes to vault claimable by @elonmusk

---

## 📊 **Response Format**

### **Success Response**
```json
{
  "success": true,
  "data": {
    "jobId": "bags_clxyz123",
    "tokenId": "clxyz789",
    "status": "queued",
    "platform": "BAGS",
    "symbol": "MTK",
    "blockchain": "SOLANA",
    "estimatedTime": "2-5 minutes"
  }
}
```

### **Error Response**
```json
{
  "success": false,
  "error": "Invalid wallet address format"
}
```

---

## ⚠️ **Rate Limits**

Per agent ID:
- **10 launches per hour**
- **50 launches per day**

Exceeded limits return:
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "resetIn": 3600
}
```

---

## 🔍 **Status Checking**

Check launch status:
```
GET https://fourclaw.fun/api/launch/status/{jobId}
```

**Response:**
```json
{
  "id": "bags_clxyz123",
  "status": "completed",
  "progress": 100,
  "token": {
    "mint": "5xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    "symbol": "MTK",
    "name": "My Token"
  }
}
```

**Statuses:** `queued`, `processing`, `completed`, `failed`

---

## 💡 **Complete Examples**

### **Example 1: BAGS - Basic**
```bash
curl -X POST https://fourclaw.fun/api/launch \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "BAGS",
    "name": "AI Agent Token",
    "symbol": "AGENT",
    "agentId": "my_ai_agent",
    "agentName": "My AI Agent",
    "creatorWallet": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    "description": "Token for my AI agent",
    "twitter": "@myagent"
  }'
```

---

### **Example 2: FLAP - Default Split**
```bash
curl -X POST https://fourclaw.fun/api/launch \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "FLAP",
    "name": "BNB Agent Token",
    "symbol": "BNBAGENT",
    "agentId": "my_ai_agent",
    "agentName": "My AI Agent",
    "creatorWallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "taxRate": 500,
    "vaultType": "split"
  }'
```

**Result:** Creator 80%, Platform 20%

---

### **Example 3: FLAP - Team Split**
```bash
curl -X POST https://fourclaw.fun/api/launch \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "FLAP",
    "name": "Team Token",
    "symbol": "TEAM",
    "agentId": "team_agent",
    "agentName": "Team Agent",
    "creatorWallet": "0x1111111111111111111111111111111111111111",
    "taxRate": 300,
    "vaultType": "split",
    "recipients": [
      {
        "recipient": "0x1111111111111111111111111111111111111111",
        "bps": 6000
      },
      {
        "recipient": "0x2222222222222222222222222222222222222222",
        "bps": 2000
      },
      {
        "recipient": "0x3333333333333333333333333333333333333333",
        "bps": 2000
      }
    ]
  }'
```

**Auto-adjusted result:**
- First: 48% (6000 * 0.8)
- Second: 16% (2000 * 0.8)
- Third: 16% (2000 * 0.8)
- Platform: 20%

---

### **Example 4: FLAP - Gift Vault**
```bash
curl -X POST https://fourclaw.fun/api/launch \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "FLAP",
    "name": "Gift Token",
    "symbol": "GIFT",
    "agentId": "gift_agent",
    "agentName": "Gift Agent",
    "creatorWallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "taxRate": 500,
    "vaultType": "gift",
    "xHandle": "@elonmusk"
  }'
```

---

### **Example 5: FLAP - Custom Tax Allocation**
```bash
curl -X POST https://fourclaw.fun/api/launch \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "FLAP",
    "name": "Burn Token",
    "symbol": "BURN",
    "agentId": "burn_agent",
    "agentName": "Burn Agent",
    "creatorWallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "taxRate": 500,
    "vaultType": "split",
    "mktBps": 7000,
    "deflationBps": 3000,
    "dividendBps": 0,
    "lpBps": 0
  }'
```

**Tax breakdown:**
- 70% to vault (split 80/20)
- 30% burned (deflation)

---

## ❌ **Common Errors**

### **Invalid Wallet**
```json
{"error": "Invalid wallet address format"}
```
**Fix:** Check wallet format (Solana vs EVM)

### **Symbol Taken**
```json
{"error": "Ticker MTK already launched"}
```
**Fix:** Use a different symbol

### **Rate Limited**
```json
{"error": "Rate limit exceeded", "resetIn": 3600}
```
**Fix:** Wait 1 hour or use different agentId

### **Invalid Recipients**
```json
{"error": "[USER_ERROR] Platform fee must be at least 2000 BPS (20%)"}
```
**Fix:** Include platform or let auto-adjust handle it

### **Invalid Tax Allocation**
```json
{"error": "Tax allocation must sum to 10000 BPS"}
```
**Fix:** Ensure mktBps + deflationBps + dividendBps + lpBps = 10000

---

## 🎯 **Best Practices**

✅ **DO:**
- Use unique agentId per app/agent
- Validate wallet addresses before sending
- Let platform fee auto-adjust (don't specify recipients unless needed)
- Check status endpoint for launch progress
- Handle rate limits gracefully

❌ **DON'T:**
- Hardcode API keys (not needed!)
- Try to bypass 20% platform fee
- Use same agentId for multiple users
- Send duplicate launches (check symbol first)

---

## 📞 **Support**

- **Documentation:** https://fourclaw.fun/fourclaw/docs
- **Status Endpoint:** `/api/launch/status/{jobId}`
- **Limits:** 10/hour, 50/day per agent

---

## ✅ **Summary**

**BAGS (Solana):**
- Simple: Just wallet, name, symbol
- Auto 80/20 split (creator/platform)

**FLAP (BNB Chain):**
- Requires: taxRate, vaultType
- Default: 80/20 split (auto-adjusted)
- Custom: Specify recipients (auto-adjusted to 80/20)
- Gift: Use xHandle for claimable vault

**Platform Fee:**
- Always 20% (enforced)
- Auto-adjusted if not included
- Cannot be bypassed

---

**Start launching tokens now!** 🚀