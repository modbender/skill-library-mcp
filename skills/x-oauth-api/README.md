# x-oauth-api

Post to X (Twitter) using the official X API with OAuth 1.0a authentication.

## Installation

```bash
clawhub install x-oauth-api
```

Or manually:
```bash
npm install twitter-api-v2 commander dotenv
```

## Quick Start

### 1. Get X API Credentials

1. Go to https://developer.twitter.com/
2. Create a new app or use existing one
3. Generate OAuth 1.0a keys:
   - Consumer Key (API Key)
   - Consumer Secret (API Secret)
   - Access Token
   - Access Token Secret

### 2. Set Environment Variables

```bash
export X_API_KEY="your_consumer_key"
export X_API_SECRET="your_consumer_secret"
export X_ACCESS_TOKEN="your_access_token"
export X_ACCESS_TOKEN_SECRET="your_access_token_secret"
```

Or create a `.env` file:
```
X_API_KEY=your_consumer_key
X_API_SECRET=your_consumer_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_token_secret
X_USER_ID=your_numeric_user_id  # Optional: speeds up mentions
```

### 3. Use It

```bash
# Post a tweet
x post "Hello from X API! 🚀"

# Create a thread
x thread "First tweet" "Second tweet" "Third tweet"

# Check mentions
x mentions --limit 5

# Search tweets
x search "AI agents" --limit 10
```

## Commands

### Post a Tweet
```bash
x post "Your message here"

# With options
x post "Check this out" --media image.jpg
x post "Great point!" --reply-to 1234567890
x post "Agreed" --quote 1234567890
```

### Create a Thread
```bash
x thread "Tweet 1" "Tweet 2" "Tweet 3"
```

### Check Mentions
```bash
x mentions
x mentions --limit 20
x mentions --format json
```

### Search Tweets
```bash
x search "keyword"
x search "from:someone" --limit 50
x search "#hashtag"
```

### Delete a Tweet
```bash
x delete 1234567890
```

### Account Info
```bash
x me
```

## Features

- ✅ Post tweets with OAuth 1.0a (Free tier ✓)
- ✅ Create tweet threads (Free tier ✓)
- ✅ Delete tweets (Free tier ✓)
- ✅ Account info lookup (Free tier ✓)
- 🔒 Monitor mentions (Basic+ tier)
- 🔒 Search tweets (Basic+ tier)
- ✅ JSON output support

## Documentation

Full details in [SKILL.md](./SKILL.md)

## Rate Limits

X API enforces these limits:
- **POST /2/tweets**: 300 per 15 minutes
- **GET mentions**: 180 per 15 minutes  
- **GET search**: 450 per 15 minutes

The skill handles queuing automatically.

## Troubleshooting

**"Missing X API credentials"**
- Set environment variables X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET

**"Unauthorized"**
- Verify credentials are correct
- Check app has write permissions in X Developer Portal

**"Rate limit exceeded"**
- Wait 15 minutes for limit to reset
- Or reduce posting frequency

## Support

For X API documentation: https://developer.twitter.com/en/docs/twitter-api

## License

MIT
