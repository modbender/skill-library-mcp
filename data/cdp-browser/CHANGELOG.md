# Changelog

## 2.0.1 (2026-02-19)

**cdp-browser v2.0.1 (Security + Reliability Patch)**

### Security hardening
- Blocked unsafe URL schemes in browser navigation flows to mitigate browser-context code execution risk.
- Added strict URL validation (http:// and https:// only) in:
  - pw.js (goto action)
  - cdp.js (newTab, gotoTab)
- Explicitly rejects schemes: javascript:, data:, file:, and other non-http(s) protocols.

### Post confirmation safety
- Fixed bin/tweet-post wrapper to require explicit --confirm.
- Removed implicit confirm behavior that could bypass expected posting safety checks.
- tweet-post now fails fast with: Error: --confirm required

### X compose/post flow reliability
- Updated compose launcher selectors to better match current X UI.
- Improved post action selector preference: tweetButton, fallback tweetButtonInline.
- Reduced false failures caused by disabled inline/reply buttons.

### Command surface improvements
- Added query ops: getUrl, getText [selector], getHtml [selector]
- Added tweet-draft --save-pending (writes to .cdp-browser/pending-tweet.json)

## 2.0.0 (2026-02-19)

**security: CDP v2 hardening - explicit confirm, draft/post split, safer selectors**

- tweet-post: require --confirm as second arg (strict), no auto-injection
- Split tweet: tweet-draft (compose only), tweet-post (requires --confirm)
- Legacy tweet action → draft only
- Compose launcher: SideNav_NewTweet_Button, /compose/post, Post only (avoid reply buttons)
- Post button: tweetButton, tweetButtonInline
- Add query ops: getUrl, getText, getHtml
- Add --save-pending for tweet-draft (pending-tweet.json)
- Replace curl with fetch in cdp.js (remove shell injection)
- Replace eval with allowlisted query in pw.js
- Add Telegram confirm flow: send-tweet-confirm.sh, .cdp-browser.json.example
- Docs: SKILL.md, README.md, SECURITY.md

## 1.0.0

Initial release.
