---
name: unipile-linkedin
description: Interact with LinkedIn via Unipile API - send messages, view profiles, manage connections, create posts, react to content. Use when the user asks to message someone on LinkedIn, check LinkedIn messages, view LinkedIn profiles, send connection requests, create LinkedIn posts, or interact with LinkedIn content.
---

# Unipile LinkedIn

Access LinkedIn through the Unipile API using the CLI script.

## Setup

Requires environment variables in `~/.openclaw/workspace/TOOLS.md` or shell:
- `UNIPILE_DSN` - Your Unipile API endpoint (e.g., `https://api1.unipile.com:13111`)
- `UNIPILE_ACCESS_TOKEN` - Your Unipile access token

Get credentials from [dashboard.unipile.com](https://dashboard.unipile.com).

## Usage

Run commands via the CLI script:

```bash
./scripts/linkedin.mjs <command> [options]
```

## Commands

### Account Management
```bash
./scripts/linkedin.mjs accounts                    # List connected accounts
./scripts/linkedin.mjs account <account_id>        # Get account details
```

### Messaging
```bash
./scripts/linkedin.mjs chats [--account_id=X] [--limit=N] [--unread]   # List chats
./scripts/linkedin.mjs chat <chat_id>                                   # Get chat details
./scripts/linkedin.mjs messages <chat_id> [--limit=N]                   # List messages in chat
./scripts/linkedin.mjs send <chat_id> "<text>"                          # Send message
./scripts/linkedin.mjs start-chat <account_id> "<text>" --to=<user_id>[,<user_id>] [--inmail]  # Start new chat
```

### Profiles
```bash
./scripts/linkedin.mjs profile <account_id> <identifier> [--sections=experience,education,skills] [--notify]
./scripts/linkedin.mjs my-profile <account_id>                          # Your own profile
./scripts/linkedin.mjs company <account_id> <identifier>                # Company profile
./scripts/linkedin.mjs relations <account_id> [--limit=N]               # Your connections
```

### Invitations
```bash
./scripts/linkedin.mjs invite <account_id> <provider_id> ["message"]    # Send connection request
./scripts/linkedin.mjs invitations <account_id> [--limit=N]             # List pending invites
./scripts/linkedin.mjs cancel-invite <account_id> <invitation_id>       # Cancel invitation
```

### Posts
```bash
./scripts/linkedin.mjs posts <account_id> <identifier> [--company] [--limit=N]  # List posts
./scripts/linkedin.mjs post <account_id> <post_id>                              # Get post
./scripts/linkedin.mjs create-post <account_id> "<text>"                        # Create post
./scripts/linkedin.mjs comments <account_id> <post_id> [--limit=N]              # List comments
./scripts/linkedin.mjs comment <account_id> <post_id> "<text>"                  # Add comment
./scripts/linkedin.mjs react <account_id> <post_id> [--type=like|celebrate|support|love|insightful|funny]
```

### Attendees
```bash
./scripts/linkedin.mjs attendees [--account_id=X] [--limit=N]           # List chat contacts
```

## Examples

```bash
# List all chats, only unread
./scripts/linkedin.mjs chats --unread

# Send a message
./scripts/linkedin.mjs send "abc123" "Thanks for connecting!"

# View someone's profile with experience section
./scripts/linkedin.mjs profile "myaccount" "john-doe-123" --sections=experience,about

# Send connection request with note
./scripts/linkedin.mjs invite "myaccount" "jane-smith-456" "Hi Jane, let's connect!"

# Create a LinkedIn post
./scripts/linkedin.mjs create-post "myaccount" "Excited to announce our new product launch! 🚀"

# React to a post
./scripts/linkedin.mjs react "myaccount" "post789" --type=celebrate
```

## Notes

- `identifier` can be a LinkedIn user ID or profile URL slug
- `account_id` is your connected LinkedIn account ID (get from `accounts` command)
- Use `--inmail` flag when messaging non-connections (requires LinkedIn Premium)
