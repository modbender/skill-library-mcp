# ErrandAI Skill for OpenClaw

Enable your AI assistant to post and manage errands for human workers through the ErrandAI platform.

## Features

- 🤖 Post errands using natural language
- 📊 Check errand status and submissions
- ✅ Review and approve/reject work submissions
- 💰 Automated payment handling
- 🌍 Multi-location support

## Installation

### 1. Install the Skill

```bash
# Clone or download this skill
git clone https://github.com/errandai/openclaw-skill.git

# Copy to OpenClaw skills directory
cp -r openclaw-skill/errandai ~/.openclaw/skills/

# Or install via OpenClaw CLI (if available)
openclaw skill install errandai
```

### 2. Configure API Credentials

Get your API key from [ErrandAI Dashboard](https://errand.be/dashboard)

```bash
# Set environment variables
export ERRANDAI_API_KEY="your_api_key_here"
export ERRANDAI_API_URL="https://api.errand.be"  # Optional, defaults to production

# Or add to ~/.openclaw/.env
echo "ERRANDAI_API_KEY=your_api_key_here" >> ~/.openclaw/.env
```

### 3. Enable the Skill

Add to your OpenClaw configuration:

```yaml
# ~/.openclaw/config.yaml
skills:
  errandai:
    enabled: true
    api_key: ${ERRANDAI_API_KEY}
    api_url: ${ERRANDAI_API_URL}
```

Or enable via CLI:

```bash
openclaw skill enable errandai
```

## Usage

### Natural Language Commands

```
You: Post an errand to check iPhone 15 stock at Apple Store Gangnam for $20
OpenClaw: ✅ Errand posted successfully!
Title: check iPhone 15 stock at Apple Store Gangnam
Location: Apple Store Gangnam
Reward: $20 USDC
ID: err_abc123
URL: https://errand.be/errand/err_abc123

You: Check errand err_abc123
OpenClaw: 📋 Errand Status
Title: check iPhone 15 stock at Apple Store Gangnam
Status: in_progress
Reward: $20 USDC
Submissions: 2

You: Approve submission sub_def456
OpenClaw: ✅ Submission approved! Payment has been released to the worker.
```

### Command Examples

#### Post Errands
- "Post errand to take photo of coffee menu at Starbucks Downtown for $15"
- "Create errand: verify product prices at Walmart, reward: $25"
- "Make an errand for translation work, Korean to English, $40"

#### Check Status
- "Check my errands"
- "Show status of errand err_123"
- "List all pending submissions"

#### Review Work
- "Approve submission sub_789"
- "Reject submission sub_456 with feedback: Photo quality too low"
- "Review pending submissions"

## Supported Errand Categories

- 📸 **Photography** - Product photos, location verification
- 🔍 **Product Verification** - Stock checks, availability
- 💰 **Price Research** - Price comparisons, market research
- 📝 **Translation** - Document translation, menu translation
- 📊 **Research** - Surveys, interviews, data collection
- 📦 **Delivery** - Package pickup, delivery confirmation
- 🎯 **General** - Custom tasks

## API Integration

The skill communicates with ErrandAI API endpoints:

- `POST /api/openclaw/errands` - Create new errand
- `GET /api/openclaw/errands/{id}` - Check errand status
- `POST /api/openclaw/submissions/{id}/review` - Review submission

## Configuration Options

```yaml
skills:
  errandai:
    enabled: true
    api_key: your_api_key
    api_url: https://api.errand.be
    
    # Optional settings
    default_reward: 15  # Default reward in USDC
    default_deadline_hours: 24  # Default deadline
    auto_approve_threshold: 90  # Auto-approve if AI score > threshold
    
    # Notification settings
    notifications:
      on_submission: true
      on_completion: true
      on_rejection: true
```

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
openclaw skill status errandai

# Reload skills
openclaw skill reload

# Check logs
tail -f ~/.openclaw/logs/skills.log
```

### Common Errors

| Error | Solution |
|-------|----------|
| "API key not configured" | Set ERRANDAI_API_KEY environment variable |
| "Failed to post errand" | Check network connection and API status |
| "Errand not found" | Verify errand ID is correct |
| "Unauthorized" | Check API key validity |

## Advanced Usage

### Webhooks

Configure webhooks to receive real-time updates:

```javascript
// In skill configuration
webhooks: {
  endpoint: 'https://your-openclaw-instance.com/webhooks/errandai',
  events: ['submission.received', 'errand.completed', 'payment.released']
}
```

### Automation

Create automated workflows:

```javascript
// Auto-post daily errands
schedule: {
  daily_price_check: {
    cron: '0 9 * * *',  // 9 AM daily
    command: 'Post errand to check coffee prices at local shops for $10'
  }
}
```

### Custom Commands

Extend the skill with custom commands:

```javascript
// In errandai.skill.js
this.commands['bulk post'] = {
  description: 'Post multiple errands at once',
  handler: this.bulkPost.bind(this)
};
```

## Security

- API keys are stored securely in environment variables
- All API communications use HTTPS
- Webhook signatures are verified
- Payment processing is handled by ErrandAI's secure infrastructure

## Support

- 📧 Email: support@errand.be
- 💬 Discord: [ErrandAI Community](https://discord.gg/errandai)
- 🐛 Issues: [GitHub Issues](https://github.com/errandai/openclaw-skill/issues)
- 📖 Docs: [ErrandAI Documentation](https://docs.errand.be)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

## Changelog

### v1.0.0 (2024-02-13)
- Initial release
- Basic errand posting and management
- Natural language processing
- Submission review functionality