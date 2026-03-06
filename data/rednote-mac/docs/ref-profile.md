# Profile & Author Stats

## xhs_get_author_stats
Read the stats from the currently visible profile page. No parameters.

Returns:
```json
{
  "following": "2",
  "followers": "29",
  "likes": "302",
  "bio": "OpenClaw-powered shrimp 🦞\nDiving into ArXiv daily..."
}
```

| Field | Description |
|-------|-------------|
| `following` | Number of accounts this user follows |
| `followers` | Number of followers |
| `likes` | Combined likes + collects received |
| `bio` | Full bio text (may contain newlines) |

---

## Check your own profile

```
xhs_navigate(tab="profile")
xhs_get_author_stats()
```

---

## Check an author's profile from their note

Currently there's no direct "open author profile" tool. Workarounds:

**Option A — screenshot + image analysis:**
```
xhs_open_note(col=0, row=0)
xhs_screenshot()
# Use image tool to read stats from the right panel
```

**Option B — follow then check:**
```
xhs_open_note(col=0, row=0)
xhs_follow_author()            # tap author avatar area
xhs_screenshot()               # may open their profile
xhs_get_author_stats()
```

---

## Notes

- `likes` maps to "获赞与收藏" (combined likes + collects) — this is how RedNote displays the stat.
- All values are returned as strings (e.g., `"1.2k"` for large numbers — parse accordingly).
- If `get_author_stats()` returns empty strings, you're likely not on a profile page — navigate there first.
