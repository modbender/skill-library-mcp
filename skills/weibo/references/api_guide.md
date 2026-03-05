# Weibo Open Platform API Guide

Last updated: 2026-02-27

## Official Documentation (Source of Truth)

- Developer portal: https://open.weibo.com/
- API wiki index: https://open.weibo.com/wiki/%E5%BE%AE%E5%8D%9AAPI
- OAuth mechanism: https://open.weibo.com/wiki/%E6%8E%88%E6%9D%83%E6%9C%BA%E5%88%B6
- OAuth authorize: https://open.weibo.com/wiki/OAuth2/authorize
- OAuth access token: https://open.weibo.com/wiki/OAuth2/access_token
- OAuth token info: https://open.weibo.com/wiki/OAuth2/get_token_info

## Base URLs

- REST API base: `https://api.weibo.com/2`
- OAuth API base: `https://api.weibo.com/oauth2`

## Authentication Model

- Protocol: OAuth 2.0 authorization code flow.
- Required app config: App Key, App Secret, Redirect URI.
- Typical flow:
1. Build authorize URL for user consent.
2. Exchange returned `code` for `access_token`.
3. Send `access_token` as request parameter to REST endpoints.

## Common Endpoints Used by This Skill

- `GET /2/statuses/public_timeline.json`
  - Purpose: fetch latest public statuses.
  - Common params: `access_token`, `count`, `page`.
- `GET /2/statuses/user_timeline.json`
  - Purpose: fetch statuses for a user.
  - Common params: `access_token`, `uid` (or `screen_name`), `count`, `page`.
- `GET /2/search/topics.json`
  - Purpose: query topic trends.
  - Common params: `access_token`, `q`, `count`, `page`.

Use endpoint-specific docs in the wiki to confirm required/optional params and permission scope before running production workflows.

## Operational Constraints

- App registration/review may be required before full endpoint access.
- Access can be region/account constrained.
- Rate limits and endpoint availability differ by app permission level.

## Skill Usage Guidance

- Primary automation interface: `scripts/weibo_cli.sh`.
- Optional fallback skill: `weibo-brave-search` when users intentionally want a Brave Search dependency.
