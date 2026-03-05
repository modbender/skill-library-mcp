---
name: falcon
description: Search, read, and interact with Twitter/X via TwexAPI
user-invocable: true
command-dispatch: tool
command-tool: Bash
command-arg-mode: raw
metadata: {"openclaw":{"requires":{"bins":["curl","jq"],"env":["TWEXAPI_KEY"]},"primaryEnv":"TWEXAPI_KEY","emoji":"🦅","os":["darwin","linux"]}}
---

falcon

Use falcon to read, search, and interact with Twitter/X.

Quick start

    falcon check
    falcon user elonmusk
    falcon tweets elonmusk 5
    falcon read <url-or-id>
    falcon search "bitcoin" 10

Reading users

    falcon user <username>               Profile info for a single user
    falcon users <u1,u2,...>             Look up multiple users (comma-separated)
    falcon find <keyword> [count]        Search for users by keyword (default: 5)
    falcon followers <username> [count]  List followers (default: 20)
    falcon following <username> [count]  List following (default: 20)

Reading tweets

    falcon tweets <username> [count]     User's tweets and replies (default: 20)
    falcon read <id-or-url> [...]        Read one or more tweets by ID or URL
    falcon replies <id-or-url> [count]   Replies to a tweet (default: 20)
    falcon similar <id-or-url>           Find similar tweets
    falcon retweeters <id-or-url> [cnt]  Who retweeted a tweet (default: 20)

Searching

    falcon search <query> [count]        Advanced search (default: 10)
    falcon hashtag <tag> [count]         Search by hashtag (default: 20)
    falcon cashtag <tag> [count]         Search by cashtag (default: 20)
    falcon trending [country]            Trending topics (default: worldwide)

Posting (confirm with user first)

    falcon tweet "text"
    falcon reply <id-or-url> "text"
    falcon quote <tweet-url> "text"

Engagement (confirm with user first)

    falcon like <id-or-url>
    falcon unlike <id-or-url>
    falcon retweet <id-or-url>
    falcon bookmark <id-or-url>
    falcon follow <username>
    falcon unfollow <username>

Account

    falcon check                         Verify API key and cookie are set
    falcon balance                       Check remaining API credits

Auth sources

    TWEXAPI_KEY env var: TwexAPI bearer token (required for all commands)
    TWITTER_COOKIE env var: Twitter auth cookie (required for write/engagement commands)

Important notes

    - The falcon script lives at {baseDir}/falcon.sh
    - All commands accept tweet URLs (x.com or twitter.com) or bare tweet IDs
    - Always confirm with the user before executing any write or engagement command
    - Search accepts any Twitter advanced search syntax
    - Hashtags can be passed with or without the # prefix
    - Cashtags can be passed with or without the $ prefix
    - Country for trending uses slug format: united-states, united-kingdom, japan, etc.
