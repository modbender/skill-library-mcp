# Frontend Implementation Guide: Agent Dashboard Route

## 📋 Overview

The Bloom Identity Skill now generates **permanent agent URLs** instead of temporary tokens:

```
Format: https://preflight.bloomprotocol.ai/agents/{agentUserId}
Example: https://preflight.bloomprotocol.ai/agents/123
```

**This document explains what the Frontend needs to implement.**

---

## 🎯 Required Changes

### 1. Add New Route: `/agents/[agentUserId]`

The frontend needs to add a dynamic route that displays an agent's dashboard.

#### Next.js Example (App Router)
```typescript
// app/agents/[agentUserId]/page.tsx

export default async function AgentDashboard({
  params
}: {
  params: { agentUserId: string }
}) {
  const { agentUserId } = params;

  // Fetch agent data from backend
  const agent = await fetchAgentData(agentUserId);

  if (!agent) {
    return <div>Agent not found</div>;
  }

  return (
    <div>
      <h1>{agent.agentName}</h1>
      <IdentityCard data={agent.identityData} />
      <SkillRecommendations skills={agent.recommendations} />
      <WalletInfo wallet={agent.walletInfo} />
    </div>
  );
}
```

#### Next.js Example (Pages Router)
```typescript
// pages/agents/[agentUserId].tsx

import { GetServerSideProps } from 'next';

export default function AgentDashboard({ agent }) {
  if (!agent) {
    return <div>Agent not found</div>;
  }

  return (
    <div>
      <h1>{agent.agentName}</h1>
      <IdentityCard data={agent.identityData} />
      <SkillRecommendations skills={agent.recommendations} />
      <WalletInfo wallet={agent.walletInfo} />
    </div>
  );
}

export const getServerSideProps: GetServerSideProps = async ({ params }) => {
  const agentUserId = params?.agentUserId as string;

  try {
    const agent = await fetchAgentData(agentUserId);
    return { props: { agent } };
  } catch (error) {
    return { props: { agent: null } };
  }
};
```

---

## 🔌 Backend API Integration

### API Endpoint

The frontend should fetch agent data from:

```
GET https://api.bloomprotocol.ai/x402/agent/{agentUserId}
```

### Expected Response

```typescript
interface AgentData {
  success: boolean;
  data: {
    agentUserId: number;
    agentName: string;
    agentType: string;
    walletAddress: string;
    network: string;
    x402Endpoint: string;
    createdAt: string;
    identityData?: {
      personalityType: string;
      tagline: string;
      description: string;
      mainCategories: string[];
      subCategories: string[];
      confidence: number;
      mode: 'data' | 'manual';
    };
    recommendations?: Array<{
      skillId: string;
      skillName: string;
      description: string;
      matchScore: number;
      categories: string[];
    }>;
  };
}
```

### Example API Call

```typescript
async function fetchAgentData(agentUserId: string) {
  const response = await fetch(
    `https://api.bloomprotocol.ai/x402/agent/${agentUserId}`,
    {
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const result = await response.json();

  if (!result.success) {
    throw new Error(result.error || 'Failed to fetch agent');
  }

  return result.data;
}
```

---

## 🎨 UI Components Needed

### 1. Identity Card Display

Shows the agent's personality analysis:

```typescript
interface IdentityCardProps {
  data: {
    personalityType: string;
    tagline: string;
    description: string;
    mainCategories: string[];
    subCategories: string[];
    confidence: number;
  };
}

function IdentityCard({ data }: IdentityCardProps) {
  return (
    <div className="identity-card">
      <div className="personality-type">
        {getPersonalityEmoji(data.personalityType)} {data.personalityType}
      </div>
      <div className="tagline">{data.tagline}</div>
      <div className="description">{data.description}</div>
      <div className="categories">
        <strong>Categories:</strong> {data.mainCategories.join(', ')}
      </div>
      <div className="confidence">
        Confidence: {data.confidence}%
      </div>
    </div>
  );
}

function getPersonalityEmoji(type: string): string {
  const emojiMap = {
    'The Visionary': '💜',
    'The Explorer': '💚',
    'The Cultivator': '🩵',
    'The Optimizer': '🧡',
    'The Innovator': '💙',
  };
  return emojiMap[type] || '🎴';
}
```

### 2. Skill Recommendations Display

Shows matching OpenClaw skills:

```typescript
interface SkillRecommendationsProps {
  skills: Array<{
    skillName: string;
    description: string;
    matchScore: number;
    categories: string[];
  }>;
}

function SkillRecommendations({ skills }: SkillRecommendationsProps) {
  return (
    <div className="recommendations">
      <h2>🎯 Matching Skills</h2>
      {skills.map((skill, i) => (
        <div key={i} className="skill-card">
          <div className="skill-header">
            <h3>{skill.skillName}</h3>
            <span className="match-score">{skill.matchScore}% match</span>
          </div>
          <p>{skill.description}</p>
          <div className="categories">
            {skill.categories.map(cat => (
              <span key={cat} className="category-tag">{cat}</span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

### 3. Wallet Info Display

Shows agent's wallet and X402 endpoint:

```typescript
interface WalletInfoProps {
  wallet: {
    address: string;
    network: string;
    x402Endpoint: string;
  };
}

function WalletInfo({ wallet }: WalletInfoProps) {
  return (
    <div className="wallet-info">
      <h2>🤖 Agent Wallet</h2>
      <div className="info-row">
        <strong>Address:</strong>
        <code>{wallet.address}</code>
      </div>
      <div className="info-row">
        <strong>Network:</strong>
        <span>{wallet.network}</span>
      </div>
      <div className="info-row">
        <strong>X402 Endpoint:</strong>
        <a href={wallet.x402Endpoint} target="_blank" rel="noopener">
          {wallet.x402Endpoint}
        </a>
      </div>
    </div>
  );
}
```

---

## 🚀 Deployment Checklist

### Backend (bp-api)
- [x] ✅ CDP wallet creation working (RPC URL fixed)
- [ ] ❓ `/x402/agent/{agentUserId}` endpoint returns agent data
- [ ] ❓ `/x402/agent-claim` endpoint saves identity data

### Frontend (Railway)
- [ ] ⏳ Add `/agents/[agentUserId]` route
- [ ] ⏳ Implement `fetchAgentData()` function
- [ ] ⏳ Create UI components (IdentityCard, SkillRecommendations, WalletInfo)
- [ ] ⏳ Deploy to Railway
- [ ] ⏳ Test with real agent URL

---

## 🧪 Testing

### Step 1: Generate Agent URL
```bash
cd bloom-identity-skill
npm start -- --user-id test-123
```

**Expected output:**
```
🌐 View Your Card
→ https://preflight.bloomprotocol.ai/agents/123
```

### Step 2: Visit Frontend
```
https://preflight.bloomprotocol.ai/agents/123
```

**Expected result:**
- ✅ Page loads (not 404)
- ✅ Shows agent identity card
- ✅ Shows skill recommendations
- ✅ Shows wallet info

### Step 3: Check API
```bash
curl https://api.bloomprotocol.ai/x402/agent/123
```

**Expected response:**
```json
{
  "success": true,
  "data": {
    "agentUserId": 123,
    "agentName": "Bloom Skill Discovery Agent",
    "walletAddress": "0x...",
    "identityData": { ... },
    "recommendations": [ ... ]
  }
}
```

---

## 🔀 URL Format Comparison

### ❌ Old Format (Deprecated)
```
https://preflight.bloomprotocol.ai/dashboard?token=eyJhbGc...
```

**Problems:**
- Token expires (24h)
- Single-use
- Long, ugly URL
- Complex token generation

### ✅ New Format (Current)
```
https://preflight.bloomprotocol.ai/agents/123
```

**Benefits:**
- Permanent (never expires)
- Multi-use (visit anytime)
- Short, clean URL
- Bookmarkable

---

## 📝 Environment Variables

### Skill (.env)
```bash
DASHBOARD_URL=https://preflight.bloomprotocol.ai
```

### Backend (bp-api .env)
```bash
# These should already be set
DATABASE_URL=postgresql://...
JWT_SECRET=...
```

### Frontend (Railway .env)
```bash
NEXT_PUBLIC_API_URL=https://api.bloomprotocol.ai
```

---

## ❓ FAQ

### Q: Why `/agents/` instead of `/dashboard`?

**A:** More RESTful and scalable:
- `/agents/123` - Specific agent dashboard
- `/agents` - List all agents (future)
- `/dashboard` - User's personal dashboard (different from agent view)

### Q: What if backend doesn't have the agent?

**A:** Show 404 page:
```typescript
if (!agent) {
  return <NotFoundPage message="Agent not found" />;
}
```

### Q: Do we need authentication?

**A:** Not initially. Agent URLs are:
- Public (anyone can view)
- Permanent (not sensitive)
- Read-only (can't modify)

Later, we can add:
- Agent ownership verification
- Edit mode (requires auth)
- Private agents

### Q: What about the old `/dashboard?token=` URLs?

**A:** Keep for backward compatibility (optional):
```typescript
// Redirect old URLs to new format
if (searchParams.has('token')) {
  const agentUserId = decodeToken(searchParams.get('token'));
  redirect(`/agents/${agentUserId}`);
}
```

---

## 📚 Related Files

In this project (`bloom-identity-skill`):
- `src/bloom-identity-skill-v2.ts:248` - Generates dashboard URL
- `src/blockchain/agent-wallet.ts:344` - Calls `/x402/agent-claim` API
- `.env:10` - `DASHBOARD_URL` configuration

---

## 🎯 Next Steps

1. **Share this guide** with frontend team
2. **Verify backend API** has `/x402/agent/{agentUserId}` endpoint
3. **Implement frontend route** `/agents/[agentUserId]`
4. **Deploy to Railway**
5. **Test end-to-end** with real agent URL

---

**Need help?** Check these resources:
- Backend API: https://api.bloomprotocol.ai
- Frontend: https://preflight.bloomprotocol.ai
- This skill: https://github.com/your-repo/bloom-identity-skill
