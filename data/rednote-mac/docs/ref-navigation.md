# Navigation & Search

## xhs_screenshot
Capture the current RedNote App screen. Returns an image.

No parameters. Use after any action to verify the result.

---

## xhs_navigate
Switch the bottom tab bar.

| Parameter | Type | Values | Default |
|-----------|------|---------|---------|
| `tab` | string | `home` `messages` `profile` | required |

- `home` — main feed (Follow / Discover / Video tabs)
- `messages` — DM inbox + notifications
- `profile` — your own profile page

---

## xhs_navigate_top
Switch the top tab on the home screen.

| Parameter | Type | Values | Default |
|-----------|------|---------|---------|
| `tab` | string | `follow` `discover` `video` | required |

- `follow` — posts from accounts you follow
- `discover` — algorithmic recommendation feed
- `video` — video-only feed

**Note:** Call `xhs_navigate(tab="home")` first if you're not on the home screen.

---

## xhs_back
Go back one page (equivalent to the back arrow in the top-left).

No parameters. Safe to call multiple times to unwind the navigation stack.

---

## xhs_search
Type a keyword into the search bar and go to the search results page.

| Parameter | Type | Description |
|-----------|------|-------------|
| `keyword` | string | Search term (required) |

**Best practice — always set context first:**
```
xhs_navigate(tab="home")
xhs_navigate_top(tab="discover")
xhs_search(keyword="AI paper")
xhs_screenshot()   # verify results loaded
```

Calling search from inside a note detail page may not work reliably — navigate home first.

---

## Typical navigation flow

```
# Start fresh from anywhere
xhs_back()          # unwind if inside a note
xhs_back()
xhs_navigate(tab="home")
xhs_navigate_top(tab="discover")

# Now browse or search
xhs_search(keyword="machine learning")
xhs_screenshot()
```
