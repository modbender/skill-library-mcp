# Actor Contracts: Twitter/X Followers + Email

## Followers Actor

Default actor id: `bIYXeMcKISYGnHhBG`

### Input

```json
{
  "userNameList": ["elonmusk"],
  "userIdList": [],
  "maxFollowers": 1000,
  "maxFollowing": 1,
  "getFollowers": true,
  "getFollowing": false,
  "outputMode": "usernames"
}
```

### Expected output shape (examples)

Rows often contain one of these keys for username extraction:
- `username`
- `screenname`
- `userName`
- `handle`
- `value`

## Email Actor

Default actor id: `mSaHt2tt3Z7Fcwf0o`

### Input

```json
{
  "usernames": "user1\nuser2\nuser3",
  "max_results": 1000
}
```

### Expected output shape (examples)

- `screenname` or `username`
- `name`
- `email`

## Final normalized row

```json
{
  "targetUsername": "elonmusk",
  "username": "someuser",
  "sourceType": "followers",
  "collectedAt": "2026-02-28T11:00:00Z",
  "name": "Optional Name",
  "email": "optional@email.com"
}
```
