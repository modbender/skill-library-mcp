# Note Interactions (Like / Collect / Comment / Reply / Delete)

All tools in this file require being inside a note detail page.
Use `xhs_open_note()` first, then `xhs_screenshot()` to confirm you're in the right place.

---

## Basic interactions

### xhs_like
Like the current note. No parameters.

Toggles like state — calling again will unlike. Check `xhs_screenshot()` to confirm the heart icon turned red.

### xhs_collect
Collect (save) the current note. No parameters.

Toggles collect state. The star icon fills when collected.

### xhs_get_note_url
Get the share URL of the current note. No parameters.

Returns a short `xhslink.com` URL. Useful for referencing the note externally or downloading video with `yt-dlp`.

### xhs_follow_author
Follow the author of the current note. No parameters.

Clicks the follow button in the top-right area. If already following, this may unfollow — screenshot to verify state first.

---

## Comments

### xhs_open_comments
Open the comment section. No parameters.

**Video notes:** Slides out a full comment panel on the right side. Fully supported.
**Image/text notes:** Only focuses the comment input box. Comment list is embedded in the right panel and requires scrolling (see ref-limits.md for AX constraints).

### xhs_scroll_comments
Scroll the comment section downward.

| Parameter | Type | Default |
|-----------|------|---------|
| `times` | integer | `3` |

Reliable on video notes. On image/text notes, scrolling may not reach comments due to AX focus limitations.

### xhs_get_comments
Get the list of visible comments. No parameters.

Returns:
```json
[
  {"index": 0, "author": "username", "cx": 1450, "cy": 368},
  {"index": 1, "author": "another_user", "cx": 1450, "cy": 440},
  ...
]
```

- `index` — use this for reply/delete
- `cx`, `cy` — global screen coordinates of the comment (for reference)

**Reliability:**
- ✅ Video notes — full comment list returned correctly
- ⚠️ Image/text notes — AX tree doesn't expose comment text (see ref-limits.md)

### xhs_post_comment
Post a top-level comment on the current note.

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | string | Comment content (required) |

Returns `True` on success. Follow up with `xhs_screenshot()` to confirm.

### xhs_reply_to_comment
Reply to a specific comment.

| Parameter | Type | Description |
|-----------|------|-------------|
| `index` | integer | Comment index from `xhs_get_comments` |
| `text` | string | Reply content (required) |

**Flow:**
```
xhs_open_comments()
xhs_get_comments()                         # → [{index:0, author:"foo"}, ...]
xhs_reply_to_comment(index=0, text="👍")  # reply to first comment
xhs_screenshot()                           # verify
```

### xhs_delete_comment
Delete one of your own comments. **Irreversible.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `index` | integer | Comment index from `xhs_get_comments` |

⚠️ **Only works on your own comments.** Verify `author` field in `get_comments` matches your account before deleting. Wrong index = deleting someone else's comment is not possible (App prevents it), but always double-check.

---

## Full comment workflow (video note)

```
xhs_open_note(col=0, row=0)
xhs_screenshot()                              # confirm note loaded

xhs_open_comments()
xhs_screenshot()                              # confirm comment panel open

xhs_get_comments()
# → [{"index":0,"author":"alice"},{"index":1,"author":"bob"}]

xhs_reply_to_comment(index=0, text="Great post!")
xhs_screenshot()                              # confirm reply sent
```
