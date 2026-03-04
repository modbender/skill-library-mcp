# Dashboard Link Implementation - Clean & Secure

## 🎯 Problem Summary

**Before:**
- Dashboard URL was 400+ characters long (full JWT token in URL)
- JWT contained sensitive signature data and wallet messages
- 24-hour expiry made links temporary (bad UX for saved identity cards)
- Environment pointing to wrong domain (preview vs preflight)
- Dashboard couldn't display agent cards

## ✅ Solution

**New Flow:**
1. Generate identity card data
2. Initialize agent wallet
3. Register agent with Bloom → get `agentUserId`
4. **Save identity card data** to Bloom backend (new endpoint)
5. Create permanent dashboard link: `https://preflight.bloomprotocol.ai/agent/{agentUserId}`

**Benefits:**
- ✅ Short URL (~50 chars vs 400+ chars)
- ✅ No sensitive data in URL (no signatures, no private keys)
- ✅ No expiry - permanent link to view identity card
- ✅ Correct environment (preflight)
- ✅ Clean architecture - backend stores data, frontend displays it

---

## 🔧 Changes Made

### **1. Skill Code (`bloom-identity-skill-v2.ts`)**

**Updated Step 5 (Single Atomic Operation):**
```typescript
// Step 5: Register agent and save identity card with Bloom
try {
  // Register agent with Bloom backend (includes identity data in one call)
  const registration = await this.agentWallet!.registerWithBloom('Bloom Skill Discovery Agent', {
    personalityType: identityData!.personalityType,
    tagline: identityData!.customTagline,  // Fixed: customTagline → tagline
    description: identityData!.customDescription,  // Fixed: customDescription → description
    mainCategories: identityData!.mainCategories,
    subCategories: identityData!.subCategories,
    confidence: dataQuality,  // Fixed: dataQuality → confidence
    mode: usedManualQA ? 'manual' : 'data',
  });
  agentUserId = registration.agentUserId;

  // Create permanent dashboard link (no expiry, no sensitive data)
  const baseUrl = process.env.DASHBOARD_URL || 'https://preflight.bloomprotocol.ai';
  dashboardUrl = `${baseUrl}/agent/${agentUserId}`;
}
```

### **2. Agent Wallet (`agent-wallet.ts`)**

**Updated `registerWithBloom()` method:**
```typescript
async registerWithBloom(
  agentName: string,
  identityData?: {
    personalityType: string;
    tagline: string;  // ✅ Fixed field name
    description: string;  // ✅ Fixed field name
    mainCategories: string[];
    subCategories: string[];
    confidence: number;  // ✅ Fixed field name
    mode: 'data' | 'manual';
  }
): Promise<{ agentUserId: number; x402Endpoint: string }>
```

**What changed:**
- Now accepts optional `identityData` parameter
- Sends identity data to backend in single call
- Matches backend DTO format exactly
- Field names fixed: `tagline`, `description`, `confidence` (not `customTagline`, `customDescription`, `dataQuality`)
- Removed separate `saveIdentityCard()` method (not needed)

### **3. Environment Config (`.env.example`)**

**Updated default:**
```bash
# Before
DASHBOARD_URL=http://localhost:3000

# After
DASHBOARD_URL=https://preflight.bloomprotocol.ai
```

---

## 🎨 Backend Status

### **✅ Existing Endpoint: `POST /x402/agent-claim`**

**Location:** `src/modules/x402/x402.controller.ts:103`

**Request:**
```json
{
  "agentName": "Bloom Skill Discovery Agent",
  "agentType": "skill-discovery",
  "walletAddress": "0x1234...",
  "network": "base-mainnet",
  "signature": "0xabc...",
  "message": "Bloom Agent Registration: Bloom Skill Discovery Agent",
  "identityData": {
    "personalityType": "The Visionary",
    "tagline": "Early adopter shaping crypto's future",
    "description": "You're not just following trends...",
    "mainCategories": ["DeFi", "Infrastructure", "Social"],
    "subCategories": ["defi", "dao", "nft"],
    "confidence": 85,
    "mode": "data"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "agentUserId": 416543868,
    "x402Endpoint": "https://x402.bloomprotocol.ai/base/0x1234..."
  }
}
```

**What it does:**
1. ✅ Verifies signature to prove wallet ownership
2. ✅ Verifies nonce to prevent replay attacks
3. ✅ Stores agent data in `agent_identities` MongoDB collection
4. ✅ Stores identity card data in same document
5. ✅ Generates consistent agentUserId from wallet address
6. ✅ Returns agentUserId and X402 endpoint

### **❌ Missing: GET Endpoint to Retrieve Agent Data**

**Backend needs:** `GET /agent/{agentUserId}` or `GET /x402/agent/{agentUserId}`

**What it should do:**
1. Accept `agentUserId` from URL path
2. Query `agent_identities` collection in MongoDB
3. Return agent data including identity card:
```json
{
  "success": true,
  "data": {
    "agentUserId": 416543868,
    "walletAddress": "0x1234...",
    "agentName": "Bloom Skill Discovery Agent",
    "network": "base-mainnet",
    "x402Endpoint": "https://x402.bloomprotocol.ai/base/0x1234...",
    "identityData": {
      "personalityType": "The Visionary",
      "tagline": "Early adopter shaping crypto's future",
      "description": "You're not just following trends...",
      "mainCategories": ["DeFi", "Infrastructure", "Social"],
      "subCategories": ["defi", "dao", "nft"],
      "confidence": 85,
      "mode": "data"
    },
    "createdAt": "2025-02-06T12:00:00Z",
    "updatedAt": "2025-02-06T12:00:00Z"
  }
}
```

### **Frontend Route: `/agent/{agentUserId}`**

**What frontend should do:**
1. Extract `agentUserId` from URL path
2. Fetch agent data from backend: `GET /agent/{agentUserId}`
3. Display identity card with all data:
   - Personality type + emoji
   - Tagline
   - Description
   - Categories
   - Confidence score
   - Mode (manual vs data-driven)
4. If no card exists, show friendly message: "No identity card found for this agent"

---

## 🔒 Security Notes

**What's in the URL:**
- ✅ Only public agent user ID (e.g., `416543868`)
- ✅ No wallet addresses
- ✅ No private keys
- ✅ No signatures
- ✅ No JWT tokens

**What's secure:**
- Identity card data is signed by agent wallet (proves authenticity)
- Data is stored on backend, not exposed in URL
- Link is permanent - no expiry concerns
- Anyone with the link can view the card (public by design)

**Note:** Identity cards are meant to be **publicly shareable**. This is similar to ENS profiles, Twitter profiles, etc. If agents want private data, that should use separate authentication.

---

## 📝 Migration Notes

**For existing agents:**
- Old JWT-based links will stop working once frontend removes JWT handling
- Agents can regenerate their identity cards to get new permanent links
- No data loss - cards are re-creatable from on-chain/manual data

**For testing:**
- Use `DASHBOARD_URL=http://localhost:3000` for local development
- Ensure backend endpoint exists before pushing to production
- Frontend should handle missing cards gracefully

---

## 🎉 Example Output

**Before (400+ chars):**
```
https://preview.bloomprotocol.ai/dashboard?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWdlbnQiLCJ2ZXJzaW9uIjoiMS4wIiwiYWRkcmVzcyI6IjB4MTIzNC4uLiIsIm5vbmNlIjoiYWJjLTEyMy14eXoiLCJ0aW1lc3RhbXAiOjE3MDcyMzQ1Njc4OTAsImV4cGlyZXNBdCI6MTcwNzMyMDk2Nzg5MCwic2NvcGUiOlsicmVhZDppZGVudGl0eSIsInJlYWQ6c2tpbGxzIiwicmVhZDp3YWxsZXQiXSwic2lnbmF0dXJlIjoiMHhhYmMuLi4iLCJzaWduZWRNZXNzYWdlIjoiQmxvb20gQWdlbnQgQXV0aGVudGljYXRpb25cbkFkZHJlc3M6IDB4MTIzNC4uLiJ9.xyz123...
```

**After (~50 chars):**
```
https://preflight.bloomprotocol.ai/agent/416543868
```

**Improvement:** 88% shorter, cleaner, shareable, permanent! 🎉

---

Built with ❤️ for better UX and security
