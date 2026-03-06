# Installation Guide

## Quick Install

### Option 1: OpenClaw Install (Recommended)

```bash
openclaw skills install pmp-agentclaw
```

### Option 2: Manual Install

```bash
# Clone or copy to skills directory
cd ~/.npm-global/lib/node_modules/openclaw/skills/
git clone https://github.com/CyberneticsPlus-Services/pmp-agentclaw.git

# Or copy local folder
cp -r ~/Desktop/PMP-Agentclaw pmp-agentclaw

# Build
cd pmp-agentclaw
npm install
npm run build
```

### Option 3: Direct Usage (No Install)

```bash
cd ~/Desktop/PMP-Agentclaw
npm install
npm run build

# Use directly
node dist/cli/calc-evm.js 10000 5000 4500 4800
```

## Verification

```bash
# Check installation
clawhub validate ~/.npm-global/lib/node_modules/openclaw/skills/pmp-agentclaw

# Test CLI
npx pmp-agentclaw calc-evm 10000 5000 4500 4800
```

## Requirements

- Node.js >= 18
- TypeScript compiler (for build)
- OpenClaw (for full integration)
