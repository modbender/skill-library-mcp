# Composio Composer | X Skill for OpenClaw

A skill for OpenClaw that enables posting tweets to Twitter/X through Composio's integration platform.

## Features

- **Post Tweets**: Send tweets with text content
- **Reply Support**: Reply to existing tweets
- **Media Upload**: Attach images and videos to tweets
- **Tweet Management**: Read and delete tweets
- **User Interactions**: Follow, like, mute, block users
- **Direct Messages**: Send and read DMs
- **Lists & Bookmarks**: Manage lists and bookmarks

## Prerequisites

- Python 3.8+
- Composio account with Twitter/X integration
- Valid Composio credentials

## Installation

1. Clone or copy this skill to your OpenClaw skills directory:
   ```
   ~/.openclaw/workspace/skills/composio-composer-xskill/
   ```

2. Install required dependencies:
   ```bash
   pip install requests beautifulsoup4 python-dotenv
   ```

3. Configure your credentials (see Configuration section)

## Configuration

### Environment Variables

Create a `.env` file in the skill directory:

```env
COMPOSIO_CLIENT_ID=ca_FnLLbPT8bhMa
COMPOSIO_API_KEY=pg-test-c56f9730-7d01-4170-b828-52d1e6d45e3b
COMPOSIO_SESSION_TOKEN=your_session_token_here
COMPOSIO_BEARER_TOKEN=your_bearer_token_here
COMPOSIO_USER_ID=your_user_id_here
COMPOSIO_API_BASE=https://backend.composio.dev/api/v1
```

Or set them in your system environment.

## Usage

### Basic Tweet Posting

```python
from composio_composer_xskill import post_tweet

# Simple tweet
result = post_tweet("Hello from OpenClaw! 🐾")
print(f"Tweet posted: {result['tweet_url']}")
```

### Tweet with Reply

```python
result = post_tweet(
    text="Great point! I agree.",
    reply_to="1234567890123456789"
)
```

### Tweet with Media

```python
result = post_tweet(
    text="Check out this image!",
    media_paths=["/path/to/image.jpg"]
)
```

## API Reference

### `post_tweet(text, reply_to=None, media_paths=None)`

Post a tweet to Twitter/X.

**Parameters:**
- `text` (str): Tweet content (max 280 characters)
- `reply_to` (str, optional): Tweet ID to reply to
- `media_paths` (list, optional): List of media file paths

**Returns:**
- `dict`: Success status and tweet information

### `get_tweet(tweet_id)`

Retrieve a tweet by its ID.

### `delete_tweet(tweet_id)`

Delete a tweet by its ID.

### `like_tweet(tweet_id)`

Like a tweet.

### `follow_user(user_id)`

Follow a user.

### `send_dm(recipient_id, message)`

Send a direct message.

## How It Works

This skill uses HTTP requests with BeautifulSoup to interact with Composio's web interface, since direct API access through OpenClaw is currently unavailable.

1. **Authentication**: Uses bearer token and session token for API requests
2. **Request Building**: Constructs appropriate HTTP requests for each action
3. **Response Parsing**: Parses JSON responses from Composio
4. **Error Handling**: Graceful handling of API errors and rate limits

## Architecture

```
composio-composer-xskill/
├── SKILL.md           # Skill definition
├── README.md          # This file
├── __init__.py        # Skill initialization
├── composio_client.py # Core Composio client
├── twitter_client.py  # Twitter/X operations
├── config.py          # Configuration management
├── requirements.txt   # Python dependencies
└── examples/          # Usage examples
    └── example_usage.py
```

## Rate Limits

- Twitter/X: 200 tweets per day (authenticated)
- Composio: Per API plan limits
- Respect rate limits to avoid account restrictions

## Troubleshooting

### Authentication Errors
- Verify your credentials are correct
- Check session token hasn't expired (7200s = 2 hours)
- Ensure bearer token is valid

### Rate Limit Errors
- Wait before making additional requests
- Implement exponential backoff
- Check Twitter/X account status

### Network Errors
- Verify internet connection
- Check Composio API status
- Ensure firewall allows HTTPS

## License

MIT License

## Support

For issues or questions, please refer to:
- [Composio Documentation](https://docs.composio.dev)
- [Twitter/X Developer Terms](https://developer.twitter.com/en/developer-terms)

## Credits

Built for OpenClaw by Runeweaver Studios
