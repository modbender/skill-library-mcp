# X (Twitter) DOM Selectors Reference

Last updated: 2026-02-26

## Core Compose
| Element | Selector | Notes |
|---------|----------|-------|
| Tweet textarea | `[data-testid="tweetTextarea_0"]` | Main composer input |
| Send button (modal) | `[data-testid="tweetButton"]` | In compose modal |
| Send button (inline) | `[data-testid="tweetButtonInline"]` | In inline reply |
| File input (images) | `input[type="file"][accept*="image"]` | Hidden, up to 4 images |
| Image preview | `[data-testid="attachments"] img` | Appears after upload |

## Tweet Actions
| Element | Selector | Notes |
|---------|----------|-------|
| Reply | `[data-testid="reply"]` | On tweet card |
| Retweet | `[data-testid="retweet"]` | Opens retweet menu |
| Like | `[data-testid="like"]` | Toggle |
| Unlike | `[data-testid="unlike"]` | Toggle |
| Share | `[data-testid="share"]` | Opens share menu |
| Bookmark | `[data-testid="bookmark"]` | Toggle |

## Retweet Menu
| Element | Selector | Notes |
|---------|----------|-------|
| Menu items | `[role="menuitem"]` | Text: "转帖"(repost) or "引用"(quote) in zh-CN |
| Repost confirm | `[data-testid="retweetConfirm"]` | Simple retweet |
| Unretweet confirm | `[data-testid="unretweetConfirm"]` | Undo retweet |

### Quote menu text by locale
- English: "Quote", "Quote Post"
- Chinese: "引用", "引用帖子"

## Article Compose
| Element | Selector | Notes |
|---------|----------|-------|
| Article list page | URL: `x.com/compose/articles` | Entry point |
| Create new article | `[aria-label="create"]` | Button on article list page |
| Editor page | URL: `x.com/compose/articles/edit/<id>` | Auto-generated after create |
| Title field | `textarea[placeholder="添加标题"], textarea[placeholder="Add a title"]` | Standard textarea, locale-dependent |
| Body editor | `[data-testid="composer"]` | contenteditable div, role="textbox" |
| Publish button | Button with text "发布" or "Publish" | |
| Media insert | `[aria-label="添加媒体内容"]` or `[aria-label="Add media"]` | Toolbar button, locale-dependent |
| Format menu | Button with text "标题"/"副标题"/"正文" (zh) or "Title"/"Subtitle"/"Body" (en) | Current block format indicator |
| Format options | `[role="menuitem"]` | Same labels as format menu button |

## Account
| Element | Selector | Notes |
|---------|----------|-------|
| Account switcher | `[data-testid="SideNav_AccountSwitcher_Button"]` | Contains @handle text |

## Tips
- X frequently updates class names but `data-testid` attributes are relatively stable
- Always add sleep/delay between actions to mimic human behavior
- If a selector breaks, inspect the page and update this file + `scripts/lib/cdp-utils.js`
- Quote menu labels vary by locale, check QUOTE_LABELS in cdp-utils.js
