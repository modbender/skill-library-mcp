# Known Limitations & Workarounds

## Image/Text Notes: Comment Text Not Readable via AX

**Symptom:** `xhs_get_comments()` returns empty or only metadata (no comment text) on image/text posts.

**Root cause:** RedNote renders image/text note comments using a custom Metal/Canvas drawing layer — completely bypassing the macOS Accessibility API. All AX attributes on the relevant elements return empty:
- `AXNumberOfCharacters = 0`
- `AXValue = kAXErrorNoValue (-25212)`
- Tried: `AXSelectedText`, `AXCustomContent`, `AXVisibleText`, `AXCustomRotors`, full AS traversal → all empty

**Affected:** Image/text posts only. **Video posts are fully supported** — comment panel renders in a standard AX-accessible layer.

**Workaround for image/text posts:**
```
xhs_open_comments()
xhs_screenshot()
# Pass screenshot to image tool for OCR/analysis
# image tool can read the rendered comment text from the screenshot
```

---

## App Must Be Visible

**Symptom:** Mouse click operations have no effect; coordinates are off.

**Root cause:** macOS mouse event API requires the target window to be on-screen.

**Rules:**
- ✅ App can be in the background (another window on top) — works fine
- ✅ App can be partially covered — works if target area is visible
- ❌ App minimized to Dock — all clicks fail
- ❌ Screen locked (loginwindow overlay) — all clicks fail

**Fix:** Keep RedNote visible. For automated tasks:
```bash
caffeinate -di &         # prevent sleep
defaults write com.apple.screensaver idleTime 0   # disable screensaver
```

---

## search() Must Be Called From Home Screen

**Symptom:** `xhs_search()` triggers but page doesn't navigate to results.

**Root cause:** The search bar AX element only exists reliably on the home/discover screen. Inside a note detail page, the search bar isn't present.

**Fix — always reset context before searching:**
```
xhs_back()
xhs_back()
xhs_navigate(tab="home")
xhs_navigate_top(tab="discover")
xhs_search(keyword="your keyword")
xhs_screenshot()   # verify results page loaded
```

---

## Image/Text Notes: Right Panel Scroll

**Symptom:** `xhs_scroll_comments()` doesn't scroll to the comment section in image/text posts.

**Root cause:** The right panel doesn't respond to mouse focus correctly. Scroll events go to the left image panel instead.

**Workaround:** These posts embed comments below the body text — use the comment icon click (`xhs_open_comments`) to focus the input, or use screenshot analysis to read visible comments.

---

## get_comments() Returns Odd Authors

**Symptom:** `get_comments()` returns entries like `{"author": "关注", "cx": ...}` or UUID-format strings.

**Root cause:** The AX traversal picks up non-comment buttons (follow button, avatar buttons) that happen to be in the same region.

**Fix:** Filter out entries where `author` is `"关注"`, matches UUID format, or is shorter than 2 characters. Real usernames are typically 2-20 characters.

---

## Summary Table

| Issue | Affected | Workaround |
|-------|----------|------------|
| Comment text unreadable | Image/text posts | `xhs_screenshot()` + image OCR |
| App clicks fail | Minimized / locked screen | Keep App visible, `caffeinate` |
| search() no effect | Called from note detail page | Navigate home first |
| scroll_comments fails | Image/text posts | Use screenshot analysis |
| get_comments garbage entries | Both types | Filter by author name length/format |
