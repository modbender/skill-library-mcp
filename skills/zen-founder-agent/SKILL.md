---
name: zen-founder-agent
emoji: 🦞💰
description: Analyze startup pitch decks and get matched with VCs from Zen.GP's investor database
category: business
metadata: {"openclaw":{"requires":{"env":["ZEN_FOUNDER_AGENT_API_KEY"],"bins":["curl"]},"primaryEnv":"ZEN_FOUNDER_AGENT_API_KEY"}}
---




# Zen Founder Agent 

Connect startups with the right VCs. Analyze pitch decks and get 5 recommended investors from Zen.GP's curated database of venture capital firms.

 ## Quick Start                                                                                                                                                                                                                                                                                              
 1. Install the skill
```bash 
clawhub install zen-founder-agent  
```                                                                                                                                                   
 2. Get your API Key at: https://zen.gp/settings/#api-keys                                                                                        
 3. Add it to OpenClaw:                                                                                                             
   ```bash                                                                                                                                          
     openclaw config set skills.entries.zen-founder-agent.env.ZEN_FOUNDER_AGENT_API_KEY "YOUR_API_KEY_HERE"                                         
   ```                                                                                                                                              
 4. Restart:                                                                                                                 
   ```bash                                                                                                                                          
     openclaw gateway restart   
```      

## What This Skill Does

1. **Analyzes pitch decks** - Extract company name, industry, stage, location, funding ask, and key metrics
2. **Matches with VCs** - Score and rank investors based on industry focus, stage preference, and geographic alignment
3. **Provides introductions** - Get contact details and match reasoning for recommended investors

## Available Endpoints

### 1. Analyze and Match (Recommended)
**POST** `/api/v1/founder/analyze-and-match`

Combined operation - analyze pitch and get investor matches in one call.

```bash
curl -X POST https://zen.gp/api/v1/founder/analyze-and-match \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ZEN_FOUNDER_AGENT_API_KEY" \
  -d '{
    "content": "<pitch deck text content>",
    "limit": 5,
    "filters": {
      "stage": "seed",
      "country": "United States"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "startup_profile": {
    "company_name": "TechStartup Inc",
    "industry": ["AI/ML", "SaaS"],
    "stage": "seed",
    "location": "San Francisco, USA",
    "funding_ask": 2000000,
    "description": "AI-powered analytics platform",
    "unique_selling_points": ["Patent-pending algorithm", "10x faster than competitors"]
  },
  "matched_investors": [
    {
      "investor_id": 123,
      "organization_name": "Sequoia Capital",
      "contact_name": "Jane Smith",
      "email": "jane@sequoiacap.com",
      "match_score": 92.5,
      "match_reasons": ["Industry alignment: AI/ML", "Stage match: seed", "Active investor (45 investments)"]
    }
  ],
  "match_count": 5
}
```

### 2. Analyze Pitch Only
**POST** `/api/v1/founder/analyze-pitch`

Extract startup profile without matching.

```bash
curl -X POST https://zen.gp/api/v1/founder/analyze-pitch \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ZEN_FOUNDER_AGENT_API_KEY" \
  -d '{"content": "<pitch deck text>"}'
```

### 3. Match Investors
**POST** `/api/v1/founder/match-investors`

Find investors for an existing profile.

```bash
curl -X POST https://zen.gp/api/v1/founder/match-investors \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ZEN_FOUNDER_AGENT_API_KEY" \
  -d '{
    "profile": {
      "company_name": "TechStartup",
      "industry": ["AI/ML"],
      "stage": "seed",
      "location": "San Francisco"
    },
    "limit": 5
  }'
```

### 4. Get Investor Details
**GET** `https://zen.gp/api/v1/founder/investor/{investor_id}`

Get full details for a specific investor.

### 5. Search Investors
**GET** `https://zen.gp/api/v1/founder/investors/search?industry=AI&stage=seed&country=USA&limit=10`

Search investors by criteria without pitch analysis.

## Usage Instructions

When the user wants to find investors for their startup:

1. **If they provide a pitch deck or description:**
   - Use `/analyze-and-match` endpoint
   - Pass the full pitch content in the `content` field
   - Present the startup profile extracted and top 5 VC matches

2. **If they want to refine results:**
   - Use filters: `stage`, `country`, `min_investments`
   - Adjust `limit` to get more/fewer results

3. **If they want more details on a specific investor:**
   - Use `/investor/{id}` to get full profile
   - Include LinkedIn, Crunchbase, investment history

4. **If they just want to browse investors:**
   - Use `/investors/search` with their criteria

## Response Formatting

When presenting matches to users, format like this:

**🎯 Top VC Matches for [Company Name]**

1. **[Organization Name]** (Match Score: XX%)
   - Contact: [Name] - [Email]
   - Why they match: [Match reasons]
   - Investments: [Number] | Stage: [Focus]
   - [Website] | [LinkedIn]

## Error Handling

- `401` - Invalid or missing API key → Run the setup command above with your key
- `400` - Missing content → Prompt user to provide pitch deck content
- `500` - Server error → Retry or report issue

## Support

- Get API Key: https://zen.gp/settings/\#api-keys
- Documentation: https://zen.gp/docs/founder-agent
- Issues: https://zen.gp/support
