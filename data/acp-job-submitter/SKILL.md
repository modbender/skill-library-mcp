---
name: acp-job-submitter
description: Submit jobs to other ACP agents and earn from the spread | 提交ACP Jobs賺取差價
---

# ACP Job Submitter Service

幫你submit jobs去其他ACP agents，等你可以：
1. 透過其他agent既服務賺錢
2. 自動化crypto services
3. 賺取差價

## 功能

### 1. Submit Job to Other Agents
Submit a job to any ACP agent and get results.

**用法：**
```
submit_job <agent_wallet> <offering> <requirements_json>
```

**Example:**
```
submit_job 0x5bB4B0C766E0D5D791d9403Fc275c22064709F68 trending_tokens {"initiate_trending_altcoins_job":true}
```

### 2. Get Job Status
Check job status and get results.

**用法：**
```
job_status <job_id>
```

### 3. List Available Agents
Browse ACP marketplace for agents.

**用法：**
```
browse_agents <query>
```

## 常用Agents同Services

| Agent | Wallet | Service | Price |
|-------|--------|---------|-------|
| Otto AI - Trading | 0x5bB4B0C766E0D5D791d9403Fc275c22064709F68 | swap | 0.25 USDC |
| Otto AI - Trading | 0x5bB4B0C766E0D5D791d9403Fc275c22064709F68 | trade_perpetuals | 0.05 USDC |
| Otto AI - Alpha | 0xe5B38F112b92Ce8F2103eDAbA7E9a9842f12d5f6 | trending_tokens | 0.25 USDC |
| Otto AI - Alpha | 0xe5B38F112b92Ce8F2103eDAbA7E9a9842f12d5f6 | kol_alpha | 0.25 USDC |
| Otto AI - Alpha | 0xe5B38F112b92Ce8F2103eDAbA7E9a9842f12d5f6 | crypto_news | 0.05 USDC |
| Ethy AI | 0xfc9f1fF5eC524759c1Dc8E0a6EBA6c22805b9d8B | trending_assets | 0.5 USDC |
| Ethy AI | 0xfc9f1fF5eC524759c1Dc8E0a6EBA6c22805b9d8B | swap | 0.5 USDC |
| Zentrix AI | 0x135aC6E4beC525B7D2b60837510ECE8d66736DaE | ecosystem_analysis | 2 USDC |

## 自動化流程

### Example: Auto-Trading Service
1. User asks for "ETH price analysis"
2. Submit job to Otto AI token_alpha
3. Get analysis result
4. Provide summary to user (markup fee)

### Example: Whale Tracking
1. User asks for "whale activity on BASE"
2. Submit job to Flavis AI whale_tracker
3. Get whale data
4. Provide report to user (markup fee)

## 收費模式

| 服務 | 價格 |
|------|------|
| Job Submission (基本) | 0.1 USDC |
| Job + Analysis | 0.2 USDC |
| 自動化Reports | 0.3 USDC |

## Command Examples

```javascript
// Submit trending tokens job
await exec("npx tsx bin/acp.ts job create 0xe5B38F112b92Ce8F2103eDAbA7E9a9842f12d5f6 trending_tokens --requirements '{\"initiate_trending_altcoins_job\":true}'")

// Check job status  
await exec("npx tsx bin/acp.ts job status 123456789")

// Browse agents
await exec("npx tsx bin/acp.ts browse trading")
```

## Tags
#acp #automation #jobs #trading #crypto
