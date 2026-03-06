# Testing Guide - Agent Identity Card Full Flow

## 🧪 Complete End-to-End Test

This guide walks through testing the entire agent identity card flow from skill execution to viewing on the frontend.

---

## ⚠️ Current Build Status

**Known Issues (Non-Critical):**
- Some deprecated modules have TypeScript errors (recommender/*,  blockchain/contract-client.ts)
- These modules are NOT used in the main identity card generation flow
- The core functionality (skill → backend → frontend) works correctly

**Working Modules:**
- ✅ Core skill execution (`src/bloom-identity-skill-v2.ts`)
- ✅ Agent wallet creation (`src/blockchain/agent-wallet.ts`)
- ✅ Personality analysis (`src/analyzers/personality-analyzer.ts`)
- ✅ Backend API integration
- ✅ Frontend route display

---

## 🚀 Prerequisites

### **1. Environment Setup**

**Skill Repository:**
```bash
cd bloom-identity-skill

# Create .env file
cp .env.example .env

# Configure environment variables
JWT_SECRET=your_secret_here
DASHBOARD_URL=https://preflight.bloomprotocol.ai
NETWORK=base-mainnet
```

**Backend Must Be Running:**
- Local: `http://localhost:3005`
- Staging: `https://bloom-protocol-be.railway.app`
- Production: `https://api.bloomprotocol.ai`

**Frontend Must Be Running:**
- Local: `http://localhost:3000`
- Staging: `https://preflight.bloomprotocol.ai`
- Production: `https://bloomprotocol.ai`

---

## 📝 Test Flow

### **Step 1: Build the Skill**

```bash
cd bloom-identity-skill
npm install
npm run build
```

**Expected Output:**
```
> bloom-identity-skill@2.0.0 build
> tsc

# Some warnings may appear for deprecated modules - this is OK
# As long as dist/ folder is created, build succeeded
```

**Verify:**
```bash
ls dist/
# Should see: bloom-identity-skill-v2.js, index.js, etc.
```

---

### **Step 2: Run the Skill**

```bash
node dist/index.js
```

**Expected Output:**
```
🎴 Generating Bloom Identity for user: default-user
📊 Step 1: Attempting data collection...
📊 Data quality score: 0/100
⚠️  Insufficient data for AI analysis
🔄 Falling back to manual Q&A...
❓ Manual input required from user

Please answer the following questions to generate your identity card:
```

**Follow the prompts:**
1. What categories are you most interested in?
2. Which projects would you support?
3. Your approach to discovering projects?
4. What drives your decisions?

---

### **Step 3: Identity Generation**

**Expected Console Output:**
```
✅ Manual analysis complete: The Visionary
🔍 Step 3: Finding matching OpenClaw Skills...
✅ Found 10 matching skills
🤖 Step 4: Initializing Agent Wallet...
✅ Agent wallet ready: 0x1234...
📝 Step 5: Registering agent with Bloom...
✅ Agent registered! User ID: 416543868
💾 Saving identity card...
✅ Identity card saved!
✅ Dashboard link ready: https://preflight.bloomprotocol.ai/agent/416543868
```

**Key Information to Note:**
- `agentUserId`: e.g., `416543868`
- `Dashboard URL`: e.g., `https://preflight.bloomprotocol.ai/agent/416543868`
- `Wallet Address`: e.g., `0x1234...`

---

### **Step 4: Verify Backend Storage**

**Test Backend API:**
```bash
# Replace 416543868 with your actual agentUserId
curl https://api.bloomprotocol.ai/x402/agent/416543868
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "agentUserId": 416543868,
    "walletAddress": "0x1234567890abcdef1234567890abcdef12345678",
    "agentName": "Bloom Skill Discovery Agent",
    "agentType": "skill-discovery",
    "network": "base-mainnet",
    "x402Endpoint": "https://x402.bloomprotocol.ai/base/0x1234...",
    "identityData": {
      "personalityType": "The Visionary",
      "tagline": "See beyond the hype",
      "description": "You back bold ideas before they're obvious...",
      "mainCategories": ["DeFi", "Infrastructure", "Social"],
      "subCategories": ["defi", "dao", "nft"],
      "confidence": 85,
      "mode": "manual"
    },
    "createdAt": "2026-02-06T12:00:00.000Z",
    "updatedAt": "2026-02-06T12:00:00.000Z"
  },
  "statusCode": 200
}
```

**If 404 Error:**
- Check if backend is running
- Verify agentUserId is correct
- Check backend logs for errors

---

### **Step 5: View on Frontend**

**Open Dashboard URL in Browser:**
```
https://preflight.bloomprotocol.ai/agent/416543868
```

**Expected Visual Elements:**

**✅ Agent Identity Card (Dark Theme):**
- Dark background with gradient
- Hero image at top (personality image)
- Personality name: "The Visionary"
- Tagline: "See beyond the hype"
- Description paragraph

**✅ 2x2 Dimension Scores:**
```
Conviction ←―――●―――→ Curiosity
        0%   85%   100%

Intuition ←―――●―――→ Analysis
       0%   75%   100%
```

**✅ Categories:**
- Main categories as tags (DeFi, Infrastructure, Social)
- Sub-categories displayed below

**✅ OpenClaw Badge:**
- 🦞 via OpenClaw

**✅ Agent Details Section:**
- Agent Name
- Wallet Address (truncated)
- Network (base-mainnet)
- Analysis Confidence (85%)
- Generation Mode (Manual Q&A or On-chain Analysis)
- Interests tags

**✅ Footer CTA:**
- Link to GitHub repository

---

## 🔍 Troubleshooting

### **Issue: Build Fails**

**Symptom:**
```
error TS2307: Cannot find module '../skills/bloom-identity-skill'
```

**Solution:**
These are errors in deprecated modules. They don't affect the main flow.
Check if `dist/` folder was created - if yes, build succeeded.

---

### **Issue: "Agent wallet not initialized"**

**Symptom:**
```
❌ Agent wallet initialization failed: Agent wallet not initialized
```

**Solution:**
1. Check if Coinbase CDP credentials are set (if using real wallet)
2. Verify `NETWORK` env variable is set correctly
3. Check internet connection for CDP API calls

---

### **Issue: "Bloom registration failed"**

**Symptom:**
```
❌ Bloom registration failed: HTTP 500
```

**Solution:**
1. Verify backend is running and accessible
2. Check `BLOOM_API_URL` or use default
3. Check backend logs for error details
4. Verify MongoDB is running (backend dependency)

---

### **Issue: "404 Not Found" on Frontend**

**Symptom:**
Frontend shows "Not Found" page

**Possible Causes:**
1. **Backend GET endpoint not deployed**
   - Check if backend has `/x402/agent/:agentUserId` endpoint
   - Verify backend deployment succeeded

2. **Frontend route not deployed**
   - Check if frontend has `/agent/[agentUserId]/page.tsx`
   - Verify frontend build included new route

3. **Agent doesn't exist**
   - Double-check agentUserId from skill output
   - Try backend API directly to verify data exists

---

### **Issue: Dashboard shows landing page instead of card**

**Symptom:**
URL redirects to homepage

**Solution:**
1. Verify frontend route is deployed
2. Check browser console for errors
3. Verify API_URL env variable on frontend
4. Check if Next.js build included dynamic route

---

## ✅ Success Checklist

- [ ] Skill builds successfully (`dist/` folder created)
- [ ] Skill executes and generates identity
- [ ] Agent wallet created (wallet address shown)
- [ ] Backend registration succeeds (agentUserId returned)
- [ ] Backend API returns agent data (curl test passes)
- [ ] Frontend displays identity card (dark theme visible)
- [ ] 2x2 dimensions displayed correctly (sliders visible)
- [ ] Categories and tags shown
- [ ] OpenClaw badge visible (🦞 via OpenClaw)
- [ ] Agent details section populated
- [ ] URL is short and shareable (~50 chars)

---

## 📊 Performance Expectations

**Skill Execution:**
- Manual Q&A: ~30 seconds (user input time)
- Data-driven: ~10 seconds (API calls)
- Wallet creation: ~3-5 seconds
- Backend registration: ~1-2 seconds

**Total Time:** ~45 seconds (manual) or ~15 seconds (data-driven)

**Frontend Load:**
- First load: ~500ms (API call + render)
- Cached: ~100ms (1-hour cache)

---

## 🎨 Visual Verification

### **Agent Card Should Match:**
- Uses `AgentIdentityCard` component from dashboard
- Dark theme (gray-900 background)
- White text (not black like human cards)
- 2x2 dimension sliders with axis labels
- Height: 659px (full card)
- Width: 372px (max-width)
- OpenClaw badge below categories

### **Not Human Card:**
- ❌ No light theme
- ❌ No black text on light background
- ❌ No project count stats
- ❌ No week number display

---

## 🔗 Quick Test URLs

**Staging (Preflight):**
```
https://preflight.bloomprotocol.ai/agent/416543868
```

**Production:**
```
https://bloomprotocol.ai/agent/416543868
```

**Backend API:**
```
https://api.bloomprotocol.ai/x402/agent/416543868
```

---

## 📝 Notes

**For Development:**
- Use `DASHBOARD_URL=http://localhost:3000` for local frontend testing
- Use `NEXT_PUBLIC_API_URL=http://localhost:3005` for local backend

**For Production:**
- Ensure all services are deployed
- Verify environment variables are set correctly
- Test end-to-end before announcing

---

Built with ❤️ for reliable testing
