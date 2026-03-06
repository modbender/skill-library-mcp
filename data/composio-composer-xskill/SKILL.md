---
name: composio-composer-xskill
displayName: Composio Composer X Skill
description: Enables posting tweets to Twitter/X through Composio's integration platform via HTTP and BeautifulSoup. Use when posting tweets or integrating with Composio.
---

# Composio Composer X Skill

This skill enables posting tweets to Twitter/X through Composio's integration platform. It uses HTTP requests with BeautifulSoup to interact with Composio's web interface, providing a `post_tweet` function that can be called from OpenClaw.


## Installation

1. Install dependencies:
   ```bash
   pip install requests beautifulsoup4 python-dotenv
   ```

2. Configure credentials in `.env` file or environment

3. Import and use the skill in your OpenClaw workflow


## Tool Definitions

### post_tweet

Posts a tweet to Twitter/X using Composio.

**Function Signature:**
```python
def post_tweet(content: str, composio_auth_token: str) -> dict:
```

**Parameters:**
- `content` (str): The tweet content (max 280 characters)
- `composio_auth_token` (str): The Composio authentication token for authorization

**Returns:**
- `dict`: Contains:
  - `success` (bool): Whether the tweet was posted successfully
  - `tweet_id` (str): The posted tweet's ID (on success)
  - `tweet_url` (str): URL to view the tweet (on success)
  - `error` (str): Error message (on failure)

**Example:**
```python
result = post_tweet(
    content="Hello from OpenClaw! 🐾",
    composio_auth_token="your_composio_auth_token_here"
)
print(f"Tweet posted: {result.get('tweet_url')}")
```

### get_tweet

Retrieves a tweet by ID.

**Function Signature:**
```python
def get_tweet(tweet_id: str, composio_auth_token: str) -> dict:
```

**Parameters:**
- `tweet_id` (str): The tweet ID to retrieve
- `composio_auth_token` (str): The Composio authentication token

**Returns:**
- `dict`: Contains tweet data or error information

### delete_tweet

Deletes a tweet.

**Function Signature:**
```python
def delete_tweet(tweet_id: str, composio_auth_token: str) -> dict:
```

**Parameters:**
- `tweet_id` (str): The tweet ID to delete
- `composio_auth_token` (str): The Composio authentication token

**Returns:**
- `dict`: Contains `success` (bool) and status message


## Configuration

The skill requires the following environment variables:
- `COMPOSIO_CLIENT_ID`: Your Composio client ID
- `COMPOSIO_API_KEY`: Your Composio API key
- `COMPOSIO_SESSION_TOKEN`: Your Composio session token
- `COMPOSIO_BEARER_TOKEN`: Your Composio bearer token
- `COMPOSIO_USER_ID`: Your Composio user ID


## Notes

- This implementation uses HTTP requests to emulate Composio interaction
- Direct API access through OpenClaw is currently unavailable
- Rate limits apply per Twitter/X and Composio policies
- Session tokens expire after 7200 seconds (2 hours)
