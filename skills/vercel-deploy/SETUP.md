# Vercel Deployment Skill - Setup Guide

## ✅ Skill Ready

**Location:** `~/.openclaw/workspace/skills/infra-deploy/`  
**Status:** ✅ Vercel-only, no Azure bloat

## 🔑 Setup (Quick)

**1. Get your Vercel token:**
- Go to: https://vercel.com/account/tokens
- Click "Create"
- Name it "OpenClaw"
- Copy the token (shows only once!)

**2. Set it:**
```bash
export VERCEL_TOKEN="vtk_xxxx..."
```

**To persist across sessions:**
```bash
echo 'export VERCEL_TOKEN="vtk_xxx..."' >> ~/.bashrc
source ~/.bashrc
```

## 🚀 Usage

Once `VERCEL_TOKEN` is set, just tell me:

### Deploy
- **"Deploy BountyLock to Vercel production"**
- **"Deploy to preview"**

### Environment Variables
- **"Set NEXT_PUBLIC_CONTRACT_ADDRESS to 0x... on Vercel"**
- **"List environment variables"**
- **"Update RPC URL to Base Sepolia"**

### Check Status
- **"Check latest deployment"**
- **"Get deployment logs"**

## 📝 Example: First Testnet Deployment

**1. Deploy contracts to Sepolia** (Hardhat)

**2. Tell me:**
```
Set these on Vercel:
- NEXT_PUBLIC_CONTRACT_ADDRESS: 0x...
- NEXT_PUBLIC_RPC_URL: https://sepolia.base.org
- NEXT_PUBLIC_CHAIN_ID: 84532
```

**3. Deploy:**
```
Deploy BountyLock to production
```

## 🎯 What This Does

**YES:**
- ✅ Deploy existing projects
- ✅ Manage env vars
- ✅ Check status/logs

**NO:**
- ❌ "AI will build your app"
- ❌ Code generation
- ❌ Magic deployments

## 🔒 Security

- Production deploys ask for confirmation
- Destructive ops require approval
- Preview deploys are automatic

Ready to set up the token?
