# Feed Browsing & Note Opening

## xhs_scroll_feed
Scroll the current feed.

| Parameter | Type | Values | Default |
|-----------|------|---------|---------|
| `direction` | string | `down` `up` | `down` |
| `times` | integer | any positive int | `3` |

Each "time" is one scroll tick (~5 lines). Use `times=5` or more to scroll past long posts.

---

## xhs_open_note
Open a note from the two-column waterfall feed by grid position.

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `col` | integer | `0` = left column, `1` = right column | `0` |
| `row` | integer | `0` = first row, `1` = second row, … | `0` |

**How the grid works:**
```
col:  0 (left)   1 (right)
row 0: [note]    [note]
row 1: [note]    [note]
row 2: [note]    [note]
```

After calling `xhs_open_note`, wait ~2s for the note detail page to load, then `xhs_screenshot()` to confirm.

---

## Full browsing workflow

```
# 1. Go to discover feed
xhs_navigate(tab="home")
xhs_navigate_top(tab="discover")
xhs_screenshot()   # see what's loaded

# 2. Scroll to find interesting content
xhs_scroll_feed(direction="down", times=5)
xhs_screenshot()

# 3. Open a specific note
xhs_open_note(col=0, row=1)   # left col, second row
xhs_screenshot()               # confirm note detail page

# 4. Interact with the note (see ref-note.md)
xhs_like()
xhs_collect()
```

---

## Tips

- After `xhs_scroll_feed`, the row indices shift — what was row 2 may now be row 0 in the visible area. Always `xhs_screenshot()` to confirm positions before clicking.
- If `xhs_open_note` lands on the wrong note, use `xhs_back()` and try adjusted coordinates.
- Video notes and image notes look different in the feed — `xhs_screenshot()` + image analysis can tell them apart before opening.
