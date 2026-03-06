# Zen+ Health OpenClaw Skill

Bring your wellness data into OpenClaw. Access notifications, timeline, and task catalogue from any chat platform.

## What This Skill Does

- 📬 **Notifications**: Get your latest wellness notifications and reminders
- 📅 **Timeline**: View your activity history and progress tracking  
- 📚 **Catalogue**: Browse available wellness tasks and activities
- 👤 **Profile**: Access your user profile and preferences

## Quick Start

1. **Get an API key** from [zenplus.health/settings/api-keys](https://zenplus.health/settings/api-keys)
2. **Configure the skill**:
   ```bash
   export ZEN_API_BASE_URL="https://api.zenplus.health"
   export ZEN_API_KEY="zen_ak_your_40_character_key"
   ```
3. **Ask your OpenClaw**:
   - "Show my Zen+ notifications"
   - "What's on my Zen+ timeline?"
   - "Browse the Zen+ Health catalogue"

## Security

✅ **Read-only access** - API keys cannot modify your data  
✅ **Revocable** - Disable keys instantly from your settings  
✅ **Hashed** - Keys are securely hashed server-side  
✅ **Scoped permissions** - Only request what you need

See [SECURITY.md](./SECURITY.md) for full security details.

## Example Conversations

**User**: "Show me my latest Zen+ notifications"  
**OpenClaw**: *Fetches and displays your 10 most recent notifications*

**User**: "What is on my timeline for today Zen+ Health?"  
**OpenClaw**: *Queries your timeline for the day*

**User**: "What wellness exercises are available?"  
**OpenClaw**: *Lists the exercise catalog with categories*

## API Scopes Required

- `user:restricted` - View limited profile information
- `timeline:read` - Access activity timeline
- `notification:read` - Fetch notifications
- `catalog:read` - Browse task catalogue
- `working_hours:read` - View schedule preferences

## Links

- 🏠 [Zen+ Health](https://zenplus.health)
- 🔧 [Install OpenClaw Skill](https://zenplus.health/openclaw)
- 📖 [API Documentation](https://zenplus.health/api/docs)
- 🔐 [Manage API Keys](https://zenplus.health/settings/api-keys)
- 💬 [Support](https://zenplus.health/support)

## Distribution

**ClawHub**: Available on [clawhub.ai](https://clawhub.ai)  
**Marketing**: "Wellness where you work" - bring Zen+ Health into your existing workflow

## License

Proprietary - © Zen+ Health
