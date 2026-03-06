# Test Checklist (Manual Validation)

## Preconditions

- flomo Web is logged in
- Chrome MCP tools are available in the current Codex session
- Prefer desktop viewport/layout

## Connectivity

- [ ] `get_windows_and_tabs` succeeds
- [ ] flomo tab can be switched to or opened
- [ ] `chrome_read_page` returns page structure on flomo tab
- [ ] `chrome_get_web_content` returns visible text from flomo page

## Query / Search

- [ ] Single keyword match returns one candidate with `memo_id`
- [ ] Multi-match query returns candidate list (not auto-write)
- [ ] Search deep-scan scrolls when initial view has no match
- [ ] Search stops at default cap (`50`) and reports cap reached
- [ ] Candidate list includes timestamp and short snippet

## Create / Insert

- [ ] Create plain text memo succeeds
- [ ] Create multi-line memo preserves line breaks
- [ ] Create memo with tags (e.g., `#tag/foo`) succeeds
- [ ] Result reports success and best-effort new `memo_id`

## Edit (Replace)

- [ ] Search -> choose candidate -> confirm -> replace succeeds
- [ ] Edit is not executed when user declines confirmation
- [ ] Updated memo content is verified after save
- [ ] Edit workflow stops safely if edit control cannot be found

## Delete

- [ ] Search -> choose candidate -> second confirmation -> delete succeeds
- [ ] Delete is not executed when user declines confirmation
- [ ] Post-delete verification shows target no longer found in scan range
- [ ] Delete workflow stops safely if delete control/confirm dialog is not found

## Resilience / Fallback

- [ ] Ref expiration is handled by re-reading page and retrying
- [ ] Switching away from flomo tab and back still works
- [ ] Coordinate fallback is only used after structured ref attempts fail
- [ ] Human element selection fallback works when requested

## Privacy / Logging

- [ ] No local file is created with memo body text
- [ ] Responses include only minimal operation metadata by default
