###### WIP Computer
# wip-x

X Platform API. Read posts, search tweets, post, upload media.

Built on the official [@xdevplatform/xdk](https://github.com/xdevplatform/xdk) TypeScript SDK (v0.4.0, MIT, zero transitive deps).

Four interfaces: CLI, Module, MCP Server, Skill.

## Install

Open your AI coding tool and say:

```
Clone wipcomputer/wip-x and read the README and SKILL.md.
Then explain to me:
1. What is this tool?
2. What does it do?
3. What would it change or fix in our current system?

Then ask me if I have more questions, or if I want you to integrate it into our system.
```

Your agent will read the repo, explain the tool, and walk you through integration interactively.

### Authentication

The tool resolves credentials automatically:

1. **1Password** (preferred) ... vault "Agent Secrets", item "X Platform API"
2. **Environment variables** ... as a fallback

**Read-only** (fetch posts, search, user lookup):
```bash
export X_BEARER_TOKEN="your-bearer-token"
```

**Read + Write** (post tweets, bookmarks, upload media):
```bash
export X_API_KEY="your-api-key"
export X_API_SECRET="your-api-secret"
export X_ACCESS_TOKEN="your-access-token"
export X_ACCESS_TOKEN_SECRET="your-access-token-secret"
```

Get credentials at https://developer.x.com/en/portal/dashboard

## Usage

### CLI

```bash
# Sensor (read)
wip-x fetch https://x.com/parkertoddbrooks/status/123456
wip-x search "AI agents" --max=20
wip-x bookmarks --max=10
wip-x user parkertoddbrooks
wip-x me

# Actuator (write)
wip-x post "Hello from wip-x"
wip-x post "Replying!" --reply-to=123456
wip-x post "Check this out" --media=photo.jpg
wip-x delete 123456
wip-x bookmark 123456
wip-x upload photo.jpg
```

### As a Module

```javascript
import { fetch_post, search_recent, post_tweet, get_bookmarks } from '@wipcomputer/wip-x';

// Sensor: read
const post = await fetch_post({ id_or_url: 'https://x.com/user/status/123' });
console.log(post.data.text);

const results = await search_recent({ query: 'AI agents', max_results: 10 });
for (const tweet of results.data) {
  console.log(tweet.text);
}

const bookmarks = await get_bookmarks({ max_results: 20 });

// Actuator: write
const { data } = await post_tweet({ text: 'Hello from wip-x' });
console.log(`Posted: https://x.com/i/status/${data.id}`);
```

### MCP Server

Add to your `.mcp.json`:

```json
{
  "wip-x": {
    "command": "node",
    "args": ["/path/to/wip-x/mcp-server.mjs"]
  }
}
```

Exposes 7 tools: x_fetch_post, x_search_recent, x_get_bookmarks, x_get_user, x_post_tweet, x_delete_tweet, x_upload_media.

## Functions

### Sensor (Read)

| Function | What | Auth |
|----------|------|------|
| `fetch_post` | Fetch a post by ID or URL | Bearer |
| `search_recent` | Search tweets (last 7 days) | Bearer |
| `get_bookmarks` | Get your bookmarks | OAuth |
| `get_user` | Get user profile | Bearer |
| `get_me` | Get your own profile | OAuth |

### Actuator (Write)

| Function | What | Auth |
|----------|------|------|
| `post_tweet` | Post a new tweet | OAuth |
| `delete_tweet` | Delete a tweet | OAuth |
| `bookmark_post` | Bookmark a post | OAuth |
| `unbookmark_post` | Remove a bookmark | OAuth |
| `upload_media` | Upload image/video/gif | OAuth |

**Bearer** = read-only bearer token. **OAuth** = OAuth 1.0a with all four tokens.

## wip-x vs wip-grok

| | wip-x | wip-grok |
|---|---|---|
| **API** | X Platform API (api.x.com) | xAI API (api.x.ai) |
| **Search** | Raw tweet data, exact matches | AI-powered search via Grok |
| **Read posts** | Fetch by ID, search by query | Not available |
| **Write** | Post tweets, upload media | Generate images/video |
| **Auth** | Bearer token / OAuth 1.0a | xAI API key |

Use **wip-x** to read/write on X. Use **wip-grok** for AI-powered search and media generation.

## Attribution

Built on [@xdevplatform/xdk](https://github.com/xdevplatform/xdk) v0.4.0 (official X TypeScript SDK).

---

## License

MIT

Built by Parker Todd Brooks, with Claude Code and Lēsa (OpenClaw).
