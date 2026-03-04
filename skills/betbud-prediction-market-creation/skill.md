# Prediction Market Creator

An AI agent that automatically creates prediction markets on betbud.live by analyzing trending crypto Twitter content.

## What it does

1. **Fetches trending content** from premium crypto Twitter accounts (WatcherGuru, tier10k, CoinDesk, etc.)
2. **Analyzes with Claude AI** to find debatable, time-bound topics
3. **Avoids duplicates** using local cache of recent predictions
4. **Fetches professional images** from Unsplash for each market
5. **Creates blockchain markets** on Base Sepolia testnet
6. **Registers to betbud.live** automatically via Bubble.io API workflow

## Features

- ✅ Fetches from 5+ premium crypto Twitter accounts
- ✅ Uses Claude Sonnet 4 for intelligent topic selection
- ✅ Professional images from Unsplash
- ✅ Deduplication cache (last 20 predictions)
- ✅ Creates markets on blockchain + registers to betbud.live

## Requirements

You need API keys for:
- Twitter API (twitterapi.io)
- Anthropic Claude API
- Unsplash API
- Base Sepolia RPC URL
- Ethereum wallet private key

## Setup

1. Clone the repo
2. Create `.env` file with your API keys (see `.env.example`)
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python skill.py`

## How it works

1. Fetches 15+ tweets from premium accounts + trending topics
2. Claude analyzes and picks the best debatable topic
3. Gets a professional image from Unsplash
4. Creates market on blockchain (Base Sepolia)
5. Registers to betbud.live via API workflow
6. Saves to cache to avoid duplicates

## Output

Creates prediction markets like:
- "Will Bitcoin reach $100k by March 2026?"
- "Will Ethereum ETF approval happen by February 2026?"
- Each with professional images, clear resolution criteria, and 7-14 day duration

## Safety

- No hardcoded API keys in code
- Uses Bubble.io backend workflow (no exposed credentials)
- All sensitive data in `.env` file
```

---

### **📄 Create `.env.example`**

Create this file to show what keys are needed:
```
TWITTERAPI_IO_KEY=your_twitter_api_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
RPC_URL=https://sepolia.base.org
PRIVATE_KEY=your_wallet_private_key_here
UNSPLASH_ACCESS_KEY=your_unsplash_access_key_here
```

---

### **📄 Create/Update `requirements.txt`**
```
anthropic==0.79.0
web3==7.14.1
python-dotenv==1.0.0
requests==2.32.3
```

---

## **STEP 2: PUBLISH TO CLAWHUB**

Go to: https://clawhub.com/publish

### **Fill out the form:**

**1. Skill Name:**
```
Prediction Market Creator
```

**2. Short Description (one line):**
```
AI agent that creates prediction markets on betbud.live by analyzing trending crypto Twitter
```

**3. Long Description:**
```
This AI agent automatically monitors trending crypto Twitter content from premium accounts (WatcherGuru, tier10k, CoinDesk, etc.), analyzes it with Claude AI to find the most debatable topics, and creates prediction markets on betbud.live.

Features:
- Fetches diverse content from 5+ premium Twitter accounts
- Uses Claude Sonnet 4 for intelligent topic selection
- Avoids duplicates with local caching
- Professional images from Unsplash
- Creates blockchain markets on Base Sepolia
- Automatically registers to betbud.live

Perfect for running 24/7 to keep your prediction market platform fresh with relevant, timely topics.
```

**4. GitHub Repository URL:**
```
https://github.com/YOUR_USERNAME/YOUR_REPO_NAME
```

**5. Category:**
```
Social Media & Content
```
or
```
Blockchain & Web3
```

**6. Tags (add these):**
```
prediction-markets, crypto, twitter, blockchain, ai-agent, automation
```

**7. Required API Keys:**
List each key and where to get it:
```
- Twitter API: https://twitterapi.io (for fetching tweets)
- Anthropic API: https://console.anthropic.com (for Claude AI)
- Unsplash API: https://unsplash.com/developers (for images)
- Base Sepolia RPC: https://sepolia.base.org (free)
- Ethereum Wallet Private Key: Your wallet (for blockchain transactions)
```

**8. Installation Instructions:**
```
1. Clone the repository
2. Install dependencies: pip install -r requirements.txt
3. Create .env file with your API keys (see .env.example)
4. Run: python skill.py
```

**9. Usage Instructions:**
```
Run the skill with: python skill.py

The agent will:
1. Fetch trending crypto content
2. Analyze and pick a unique topic
3. Create a blockchain market
4. Register to betbud.live
5. Save to cache to avoid duplicates

Run it on a schedule (cron job) to continuously create new markets.
```

**10. Demo/Screenshot:**
Upload a screenshot showing:
- Terminal output of successful run
- Or a screenshot of created market on betbud.live

**11. License:**
```
MIT