# Browser Publishing Guide

## Prerequisites

- A connected node with Chrome/Chromium, or a sandbox browser available
- User logged into 小红书 creator portal in the browser
- Browser tool configured with the appropriate profile and target for your setup

Example configuration (adjust to match your environment):
```
profile: openclaw
target: node (or sandbox)
node: <your-node-name>
```

## Pre-flight Check

Before attempting browser publish, verify:

```
1. Check node status: nodes → status
2. Test browser: browser → tabs (with your configured profile/target)
3. If tabs fails → fall back to manual publishing
```

## Publishing Steps

### 1. Navigate to Creator Portal

```
browser → navigate
  url: https://creator.xiaohongshu.com/publish/publish
```

Wait for page load, then snapshot to verify.

### 2. Check Login State

Snapshot the page. If redirected to login page:
- Notify user: "小红书需要重新登录，请在浏览器上登录后告诉我"
- Stop and wait for user confirmation

### 3. Enter Title

```
browser → snapshot (find title input field)
browser → act → click on title input
browser → act → type title text
```

Title input is typically the first text field on the publish page.

### 4. Enter Body Content

```
browser → snapshot (find body/content editor)
browser → act → click on content editor area
browser → act → type body text
```

The content editor is a rich text area. Type plain text — 小红书 handles basic formatting.

**Important**: The editor may use contenteditable div, not a standard input. Use snapshot to find the correct ref.

### 5. Upload Cover Image

Upload the cover image using browser automation:

```
browser → snapshot (find upload/image button)
browser → act → click upload area
browser → upload (paths: ["/path/to/cover.png"])
```

> **Note**: `setInputFiles` / `upload` may not trigger change events in all browser configurations. If the image doesn't appear after upload, ask the user to upload manually and provide the file path.

### 6. Publish

```
browser → snapshot (find publish/发布 button)
browser → act → click publish button
```

Wait and snapshot to verify success. Look for success message or redirect.

### 7. Verify

After publishing, navigate to the user's profile or the new post URL to confirm it's live.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| CDP connection fails | Fall back to manual publishing via channel message |
| Login expired | Ask user to re-login in their browser |
| Page layout changed | Use snapshot + aria refs to find elements dynamically |
| Upload fails silently | Ask user to upload cover manually and provide the file path |
| Publish button grayed out | Check if required fields (title, content) are filled |

## Fallback: Manual Publishing

If any browser step fails, deliver all content formatted for manual copy-paste:

```
📋 小红书发帖内容（请手动发布）

【标题】标题文本

【正文】
完整正文内容...

【标签】#tag1 #tag2 ...

【封面图】/path/to/cover.png
```

Always prioritize getting content to the user over perfect automation.
