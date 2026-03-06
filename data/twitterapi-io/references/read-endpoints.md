# READ Endpoints (GET, API key only)

## Tweet Endpoints

**Advanced Search** `GET /twitter/tweet/advanced_search`
```bash
curl -s "https://api.twitterapi.io/twitter/tweet/advanced_search?query=QUERY&queryType=Latest" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Params: `query` (required), `queryType` (`Latest` | `Top`, default: `Latest`), `cursor`
Returns: `{ tweets[], has_next_page, next_cursor }` -- up to 20 tweets/page

**Get Tweets by IDs** `GET /twitter/tweets`
```bash
curl -s "https://api.twitterapi.io/twitter/tweets?tweet_ids=ID1,ID2,ID3" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```

**Get Tweet Replies** `GET /twitter/tweet/replies`
```bash
curl -s "https://api.twitterapi.io/twitter/tweet/replies?tweetId=ID" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Params: `tweetId` (required), `sinceTime` (unix seconds), `untilTime` (unix seconds), `cursor`
Returns: `{ replies[], has_next_page, next_cursor }` -- up to 20/page, ordered by reply time desc
Note: `has_next_page` may return true even when no more data exists (Twitter platform limitation).

**Get Tweet Replies V2** `GET /twitter/tweet/replies/v2`
```bash
curl -s "https://api.twitterapi.io/twitter/tweet/replies/v2?tweetId=ID&queryType=Latest" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Params: `tweetId` (required), `queryType` (`Relevance` | `Latest` | `Likes`), `cursor`
Returns: `{ replies[], has_next_page, next_cursor }` -- supports sorting

**Get Tweet Quotations** `GET /twitter/tweet/quotes`
```bash
curl -s "https://api.twitterapi.io/twitter/tweet/quotes?tweetId=ID" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Params: `tweetId` (required), `cursor` -- 20/page

**Get Tweet Retweeters** `GET /twitter/tweet/retweeters`
```bash
curl -s "https://api.twitterapi.io/twitter/tweet/retweeters?tweetId=ID" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Params: `tweetId` (required), `cursor` -- ~100/page

**Get Tweet Thread Context** `GET /twitter/tweet/thread_context`
```bash
curl -s "https://api.twitterapi.io/twitter/tweet/thread_context?tweetId=ID" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Params: `tweetId` (required, can be any tweet in thread), `cursor`
Returns full thread: ancestors + descendants. Page size varies (Twitter limitation).

**Get Article** `GET /twitter/article`
```bash
curl -s "https://api.twitterapi.io/twitter/article?tweet_id=TWEETID" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Cost: 100 credits. Returns long-form article content from a tweet.

## User Endpoints

**Get User Info** `GET /twitter/user/info`
```bash
curl -s "https://api.twitterapi.io/twitter/user/info?userName=elonmusk" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Returns: `{ data: UserObject, status, msg }`

**Get User Profile About** `GET /twitter/user_about`
```bash
curl -s "https://api.twitterapi.io/twitter/user_about?userName=USERNAME" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Returns detailed bio with entities (links, mentions in bio).

**Batch Get Users by IDs** `GET /twitter/user/batch_info_by_ids`
```bash
curl -s "https://api.twitterapi.io/twitter/user/batch_info_by_ids?userIds=ID1,ID2,ID3" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Returns: `{ users[], status, msg }`. Bulk 100+ users: 10 credits each (vs 18 single).

**Get User Last Tweets** `GET /twitter/user/last_tweets`
```bash
curl -s "https://api.twitterapi.io/twitter/user/last_tweets?userName=USERNAME" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Params: `userName` (required), `cursor` -- 20/page, sorted by created_at desc
Tip: For frequent polling of single users, use Stream endpoints instead (cheaper).

**Get User Followers** `GET /twitter/user/followers`
```bash
curl -s "https://api.twitterapi.io/twitter/user/followers?userName=USERNAME" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Params: `userName` (required), `cursor` -- 200/page, newest first

**Get User Followings** `GET /twitter/user/followings`
```bash
curl -s "https://api.twitterapi.io/twitter/user/followings?userName=USERNAME" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Params: `userName` (required), `cursor` -- 200/page, newest first

**Get User Verified Followers** `GET /twitter/user/verifiedFollowers`
```bash
curl -s "https://api.twitterapi.io/twitter/user/verifiedFollowers?user_id=USERID&cursor=CURSOR" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Params: `user_id` (required, numeric), `cursor` -- 20/page. Cost: $0.30/1K.

**Get User Mentions** `GET /twitter/user/mentions`
```bash
curl -s "https://api.twitterapi.io/twitter/user/mentions?userId=USERID" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Params: `userId` (required, numeric), `cursor` -- 20/page, ordered by mention time desc

**Search Users** `GET /twitter/user/search`
```bash
curl -s "https://api.twitterapi.io/twitter/user/search?query=KEYWORD" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```

**Check Follow Relationship** `GET /twitter/user/check_follow_relationship`
```bash
curl -s "https://api.twitterapi.io/twitter/user/check_follow_relationship?source_user_name=A&target_user_name=B" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Returns: `{ data: { following: bool, followed_by: bool }, status, message }`
Cost: 100 credits/call.

## List Endpoints

**Get List Followers** `GET /twitter/list/followers`
```bash
curl -s "https://api.twitterapi.io/twitter/list/followers?listId=ID" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Params: `listId` (required), `cursor` -- 20/page. Cost: 150 credits/call.

**Get List Members** `GET /twitter/list/members`
```bash
curl -s "https://api.twitterapi.io/twitter/list/members?listId=ID" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Params: `listId` (required), `cursor` -- 20/page. Cost: 150 credits/call.

## Community Endpoints (Read)

**Get Community Info** `GET /twitter/community/info`
```bash
curl -s "https://api.twitterapi.io/twitter/community/info?communityId=ID" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Cost: 20 credits. Note: This endpoint may be slow (under optimization).

**Get Community Members** `GET /twitter/community/members`
```bash
curl -s "https://api.twitterapi.io/twitter/community/members?communityId=ID" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
20/page.

**Get Community Moderators** `GET /twitter/community/moderators`
```bash
curl -s "https://api.twitterapi.io/twitter/community/moderators?communityId=ID" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
20/page.

**Get Community Tweets** `GET /twitter/community/tweets`
```bash
curl -s "https://api.twitterapi.io/twitter/community/tweets?communityId=ID" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
20/page, ordered by creation time desc.

**Get All Community Tweets** `GET /twitter/community/get_tweets_from_all_community`
```bash
curl -s "https://api.twitterapi.io/twitter/community/get_tweets_from_all_community?cursor=CURSOR" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Tweets from ALL communities, 20/page.

## Other Read Endpoints

**Get Trends** `GET /twitter/trends`
```bash
curl -s "https://api.twitterapi.io/twitter/trends?woeid=2418046" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Params: `woeid` (required, [WOEID list](https://gist.github.com/tedyblood/5bb5a9f78314cc1f478b3dd7cde790b9)), `count` (optional, default 30)

**Get Space Detail** `GET /twitter/spaces/detail`
```bash
curl -s "https://api.twitterapi.io/twitter/spaces/detail?space_id=SPACEID" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```

**Get My Account Info** `GET /oapi/my/info`
```bash
curl -s "https://api.twitterapi.io/oapi/my/info" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Returns info about the account linked to your API key.

**Get DM History** `GET /twitter/get_dm_history_by_user_id`
```bash
curl -s "https://api.twitterapi.io/twitter/get_dm_history_by_user_id?userId=USERID&login_cookies=COOKIE&proxy=PROXY" \
  -H "X-API-Key: $TWITTERAPI_IO_KEY"
```
Requires login_cookies + proxy (even though it is GET).
