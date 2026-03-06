# Security Notes

## Environment Variables

This skill requires `DISCORD_TOKEN` to be set in your environment:

```bash
export DISCORD_TOKEN="your-bot-token"
```

**Never hardcode tokens in scripts or config files.**

## Best Practices

1. **Store secrets securely** — Use env vars, not hardcoded values
2. **Validate inputs** — Thread IDs should be numeric only
3. **Minimize permissions** — Bot should only have access to necessary channels
4. **Audit logs** — Review cron output for anomalies

## Token Setup

To get a Discord bot token:
1. Go to https://discord.com/developers/applications
2. Create or select your application
3. Go to Bot → Reset Token
4. Copy the token and set it as `DISCORD_TOKEN`
