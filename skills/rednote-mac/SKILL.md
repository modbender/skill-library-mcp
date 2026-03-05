---
name: rednote-mac
description: "Control the RedNote (Xiaohongshu) Mac app via macOS Accessibility API. Fills the gap headless tools can't: read/reply to comments on video posts, send DMs, get author stats. No browser, no API tokens. macOS only — requires Terminal accessibility permission."
metadata:
  openclaw:
    os: [darwin]
    requires:
      bins: [cliclick, python3]
      apps: [rednote]
      permissions: [accessibility]
---

# rednote-mac

Control RedNote's Mac app directly — no browser, no API tokens.
Uses macOS Accessibility API to drive the native App.

Headless tools (xiaohongshu-mcp) can't reach **DMs**, **comment replies**, or **video comment lists** — this skill can.

> ⚠️ Requires: Terminal → Accessibility permission + RedNote App visible on screen.
> No network access. No credentials stored.

## Setup

```bash
cd ~/.agents/skills/rednote-mac && bash install.sh
openclaw config set tools.allow '["rednote-mac"]'
openclaw gateway restart
```

Enable in System Settings → Privacy & Security → Accessibility → Terminal.

## Navigate

```
xhs_navigate(tab="home")          # home / messages / profile
xhs_navigate_top(tab="discover")  # follow / discover / video
xhs_back()
xhs_search(keyword="AI paper")
xhs_screenshot()                  # always verify after navigation
```

## Browse feed

```
xhs_scroll_feed(direction="down", times=5)
xhs_open_note(col=0, row=0)   # col: 0=left, 1=right  row: 0=first
xhs_screenshot()
```

## Interact with a note

```
xhs_like()
xhs_collect()
xhs_follow_author()
xhs_get_note_url()   # returns xhslink.com short URL
```

## Comments (video posts — fully reliable)

```
xhs_open_comments()
xhs_get_comments()
# → [{"index": 0, "author": "alice", "cx": 1450, "cy": 368}, ...]

xhs_post_comment(text="Great post!")
xhs_reply_to_comment(index=0, text="Thanks!")
xhs_delete_comment(index=0)   # ⚠️ irreversible — your comments only
xhs_scroll_comments(times=3)
```

## Direct messages

```
xhs_open_dm(index=0)           # 0 = first conversation in list
xhs_send_dm(text="Hello!")
xhs_screenshot()               # confirm sent
```

## Author stats

```
xhs_navigate(tab="profile")
xhs_get_author_stats()
# → {"following": "2", "followers": "29", "likes": "302", "bio": "..."}
```

## Reference docs (load on demand)

| Need to... | Read |
|-----------|------|
| Navigate / search details | `docs/ref-navigation.md` |
| Feed & note opening | `docs/ref-feed.md` |
| Comment workflows | `docs/ref-note.md` |
| DM details | `docs/ref-dm.md` |
| Profile & stats | `docs/ref-profile.md` |
| Limits & workarounds | `docs/ref-limits.md` |
