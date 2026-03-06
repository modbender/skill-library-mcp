# TwitterAPI.io — API Reference

Base URL: `https://api.twitterapi.io`
Auth: `X-API-Key: <key>` header

## Endpoints

### Search Tweets
`GET /twitter/tweet/advanced_search?query=QUERY&queryType=Latest`

Supports X search operators: `from:`, `-is:retweet`, `-is:reply`, `OR`, `has:links`, `min_faves:N`, `lang:en`, `conversation_id:`

Response: `{ tweets: [...], next_cursor: "..." }`

### User Info
`GET /twitter/user/info?userName=USERNAME`

Response: `{ data: { userName, name, description, followers, following, tweetsCount, ... } }`

### User Tweets
`GET /twitter/user/last_tweets?userName=USERNAME`

Response: `{ tweets: [...], next_cursor: "..." }`

### Tweets by ID
`GET /twitter/tweets?tweet_ids=ID1,ID2`

Response: `{ tweets: [...] }`

## Pricing
- $0.15 / 1,000 tweets
- $0.18 / 1,000 profiles
- Rate limit: 200 QPS
