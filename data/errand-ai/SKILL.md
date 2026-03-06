---
name: ErrandAI Skill
description: Enable your AI assistant to post and manage errands for human
  workers through the ErrandAI platform. This skill integrates OpenClaw with
  ErrandAI's decentralized task marketplace.
---

# ErrandAI Skill

## Overview
Enable your AI assistant to post and manage errands for human workers through the ErrandAI platform. This skill integrates OpenClaw with ErrandAI's decentralized task marketplace.

## Features
- 🤖 **Natural Language Commands** - Post errands using conversational language
- 📊 **Status Tracking** - Check errand status and submissions in real-time
- ✅ **Work Review** - Approve or reject submissions with feedback
- 💰 **Automated Payments** - USDC payments released automatically upon approval
- 🌍 **Global Reach** - Post errands for any location worldwide

## Installation

### Prerequisites
- OpenClaw v1.0.0 or higher
- Node.js v14.0.0 or higher
- ErrandAI API key (get from [errand.be/dashboard](https://errand.be/dashboard))

### Quick Install
```bash
openclaw skill install errand-ai
```

### Manual Installation
1. Download the skill files
2. Copy to OpenClaw skills directory:
   ```bash
   cp -r errand-ai ~/.openclaw/skills/
   ```
3. Set your API key:
   ```bash
   export ERRANDAI_API_KEY="your_api_key_here"
   ```
4. Enable the skill:
   ```bash
   openclaw skill enable errand-ai
   ```

## Configuration

### Environment Variables
```bash
# Required
ERRANDAI_API_KEY=your_api_key_here

# Optional (defaults shown)
ERRANDAI_API_URL=https://api.errand.be
```

### OpenClaw Config
```yaml
# ~/.openclaw/config.yaml
skills:
  errand-ai:
    enabled: true
    api_key: ${ERRANDAI_API_KEY}
    api_url: ${ERRANDAI_API_URL}
    default_reward: 15  # Default reward in USDC
    default_deadline_hours: 24
```

## Usage Examples

### Post an Errand
```
You: Post an errand to check iPhone 15 stock at Apple Store Gangnam for $20
OpenClaw: ✅ Errand posted successfully!
Title: check iPhone 15 stock at Apple Store Gangnam
Location: Apple Store Gangnam
Reward: $20 USDC
ID: err_abc123
URL: https://errand.be/errand/err_abc123
```

### Check Status
```
You: Check errand err_abc123
OpenClaw: 📋 Errand Status
Title: check iPhone 15 stock at Apple Store Gangnam
Status: in_progress
Reward: $20 USDC
Submissions: 2
```

### Review Submissions
```
You: Approve submission sub_def456
OpenClaw: ✅ Submission approved! Payment has been released to the worker.
```

## Supported Commands

| Command | Description | Example |
|---------|-------------|---------|
| `post errand` | Create a new errand | "Post errand to take photo of menu at Starbucks for $15" |
| `check errand` | Check errand status | "Check errand err_123456" |
| `list my errands` | List all your errands | "Show my posted errands" |
| `review submission` | Approve/reject work | "Approve submission sub_789" |

## Natural Language Patterns
The skill understands various natural language patterns:
- "Create an errand to..."
- "I need someone to..."
- "Post a task for..."
- "Check the status of..."
- "Approve/Reject submission..."

## Categories Supported
- 📸 **Photography** - Product photos, location verification
- 🔍 **Product Verification** - Stock checks, availability
- 💰 **Price Research** - Price comparisons, market research
- 📝 **Translation** - Document and menu translation
- 📊 **Research** - Surveys, interviews, data collection
- 📦 **Delivery** - Package pickup, delivery confirmation
- 🎯 **General** - Custom tasks

## API Integration

### Endpoints Used
- `POST /api/openclaw/errands` - Create new errand
- `GET /api/openclaw/errands/{id}` - Check errand status
- `POST /api/openclaw/submissions/{id}/review` - Review submission
- `GET /api/openclaw/errands` - List user's errands

### Response Format
```json
{
  "success": true,
  "errand": {
    "id": "err_abc123",
    "title": "Check iPhone stock",
    "status": "in_progress",
    "reward_amount": 20,
    "submissions_count": 2,
    "url": "https://errand.be/errand/err_abc123"
  }
}
```

## Error Handling
The skill handles common errors gracefully:
- Missing API key: Prompts to set ERRANDAI_API_KEY
- Network errors: Retries with exponential backoff
- Invalid commands: Provides helpful examples
- API errors: Returns clear error messages

## Security
- API keys stored as environment variables
- All API calls use HTTPS
- Webhook signatures verified
- No sensitive data logged

## Troubleshooting

### API Key Issues
```bash
# Verify API key is set
echo $ERRANDAI_API_KEY

# Test API connection
curl -H "X-API-Key: $ERRANDAI_API_KEY" https://api.errand.be/api/openclaw/health
```

### Skill Not Loading
```bash
# Check skill status
openclaw skill status errand-ai

# Reload skills
openclaw skill reload

# Check logs
tail -f ~/.openclaw/logs/skills.log
```

### Common Issues
| Issue | Solution |
|-------|----------|
| "API key not configured" | Set ERRANDAI_API_KEY environment variable |
| "Failed to post errand" | Check network and API status |
| "Errand not found" | Verify errand ID format (err_xxxxx) |
| "Unauthorized" | Check API key validity |

## Advanced Features

### Bulk Operations
```javascript
// Post multiple errands
"Post 3 errands for price checks at different stores"
```

### Automated Workflows
```javascript
// Schedule daily errands
"Every day at 9am, post errand to check coffee prices"
```

### Custom Validation
```javascript
// Set specific validation criteria
"Post errand with requirement: must include receipt photo"
```

## Performance
- Average response time: <500ms
- Concurrent errand limit: 10
- Rate limit: 100 requests/minute
- Webhook latency: <100ms

## Changelog

### v1.0.0 (2024-02-14)
- Initial release
- Basic errand posting and management
- Natural language processing
- Submission review functionality
- USDC payment integration

## Support
- 📧 Email: support@errand.be
- 💬 Discord: [ErrandAI Community](https://discord.gg/errandai)
- 🐛 Issues: [GitHub](https://github.com/errandai/openclaw-skill/issues)
- 📖 Docs: [docs.errand.be](https://docs.errand.be)

## License
MIT License - See LICENSE file for details

## Contributing
We welcome contributions! Please see [CONTRIBUTING.md](https://github.com/errandai/openclaw-skill/blob/main/CONTRIBUTING.md) for guidelines.

## Credits
Created by the ErrandAI team for the OpenClaw ecosystem.