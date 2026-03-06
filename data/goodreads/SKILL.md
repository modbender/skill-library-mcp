---
name: goodreads
description: >
  Search for books, get book details and reviews, discover personalized
  recommendations, and manage reading lists on Goodreads — all through
  browser automation.
metadata:
  emoji: "📚"
allowed-tools:
  - browser
---

# Goodreads Skill

You are an AI assistant helping the user interact with Goodreads.com through the `browser` tool. Goodreads has no public API, so all interactions happen via browser automation.

## Critical Rules

1. **MANDATORY: Re-snapshot after ANY navigation.** Refs from `snapshot` are NEVER stable across page loads. After any `navigate`, or any `act` click that changes the page, you MUST call `snapshot` again before using `act`. NEVER reuse refs from a previous snapshot — they will be stale and cause errors.

   **Wrong:** snapshot → navigate → act (using old ref) ❌
   **Right:** snapshot → navigate → snapshot → act (using new ref) ✅

2. **Check authentication before auth-required actions.** Recommendations and shelf management require a logged-in Goodreads session. Always verify auth state first.
3. **Use `snapshot` for data extraction, `screenshot` for debugging.** Prefer snapshot for reading page content. Use screenshot when snapshot output is confusing or when you need to verify visual layout.
4. **URL-encode search queries.** When building search URLs, encode spaces and special characters properly.
5. **Always provide required parameters to browser actions.** Every `navigate` call MUST include a `targetUrl`. Every `act` call MUST include a valid ref from the most recent snapshot. Never call a browser action with missing parameters, even during error recovery.
6. **Read the FULL error message before giving up.** Browser errors can wrap a recoverable inner error (like a stale ref) inside a misleading outer message (like "Can't reach the browser control service"). Always check the inner error text — if it mentions `"not found or not visible"` or `"Run a new snapshot"`, it's a stale ref problem, not a service outage. Re-snapshot and retry.

## Capabilities

### 1. Search for Books

Use this when the user wants to find books by title, author, ISBN, or keyword.

**Steps:**

1. Build the search URL: `https://www.goodreads.com/search?q=<url-encoded-query>`
2. Use `browser` → `navigate` to go to the search URL
3. Use `browser` → `snapshot` to get the page content
4. Extract search results from the snapshot. Look for patterns like:
   - Book titles (linked text)
   - Author names (usually appears as "by Author Name")
   - Average rating and number of ratings
   - Publication year
5. Present the top results to the user in a clear format

**Example flow:**

```
User: search for dune

→ browser navigate to https://www.goodreads.com/search?q=dune
→ browser snapshot
→ Extract and present results:
  1. "Dune" by Frank Herbert — 4.28 avg rating — 1,234,567 ratings — published 1965
  2. "Dune Messiah" by Frank Herbert — 3.89 avg rating — ...
  ...
```

**If no results are found:**
- Check if the query was URL-encoded correctly
- Suggest alternative search terms to the user
- Try a broader search query

### 2. Get Book Details & Reviews

Use this when the user wants detailed information about a specific book.

**Steps:**

1. If you have a book URL, use `browser` → `navigate` directly to it
2. If coming from search results, use `browser` → `act` to click on the book title (using the ref from the current snapshot)
3. Use `browser` → `snapshot` to get the book page content
4. Extract details from the snapshot:
   - **Title** and **author**
   - **Average rating** and **rating count** (look for "avg rating" pattern)
   - **Description** (may be truncated — look for a "more" or expand link)
   - **Genres** / shelves
   - **Page count** and **publication info** (look for "published", "pages")
   - **Top reviews** — extract the first few community reviews
5. If the description is truncated, use `browser` → `act` to click the expand/more link, then re-snapshot

**Example flow:**

```
User: tell me about project hail mary

→ browser navigate to https://www.goodreads.com/search?q=project%20hail%20mary
→ browser snapshot (get search results)
→ browser act click on "Project Hail Mary" title ref
→ browser snapshot (get book detail page)
→ Extract and present book details
```

**Handling truncated descriptions:**
- Look for "...more" or a "Show more" link in the snapshot
- Click it using `act`, then re-snapshot to get the full text

### 3. Get Personalized Recommendations

Use this when the user wants book recommendations from Goodreads.

**Steps:**

1. **Check authentication first** (see Authentication Check below)
2. If logged in: use `browser` → `navigate` to `https://www.goodreads.com/recommendations`
3. Use `browser` → `snapshot` to get recommendations
4. Extract recommended books with their reasons (e.g., "Because you liked X")
5. Present recommendations grouped by category if available

**If not logged in:**
- Inform the user that personalized recommendations require a Goodreads login
- Offer to search for books by genre instead: `https://www.goodreads.com/genres/<genre>`
- Provide the login URL: `https://www.goodreads.com/user/sign_in`

**Alternative (no auth required):**
- Browse popular lists: `https://www.goodreads.com/list/popular_lists`
- Browse by genre: `https://www.goodreads.com/genres/<genre>`
- View "Readers also enjoyed" on any book page

### 4. Manage Reading Lists

Use this when the user wants to add books to shelves, mark books as read, or rate books.

**Steps:**

0. **Check current page state.** If you are already on the target book's page from a prior action (e.g., you just looked up its details), do NOT navigate away — simply re-snapshot the current page to get fresh refs. Only navigate if you are not already on the correct book page.
1. **Check authentication first** (see Authentication Check below)
2. Navigate to the book page (search first if needed) — skip if Step 0 confirmed you're already there
3. Use `browser` → `snapshot` to find shelf/action buttons. **If your last snapshot was from a different workflow step (e.g., search results or a different book), re-snapshot NOW before clicking any shelf buttons.**
4. Look for these elements in the snapshot:
   - "Want to Read" button (to add to want-to-read shelf)
   - "Read" or "Currently Reading" status options
   - Star rating elements
   - Shelf dropdown or menu
5. Use `browser` → `act` to click the appropriate button/element
6. Re-snapshot to confirm the action was taken

**Adding to "Want to Read":**

```
→ Navigate to book page
→ Snapshot to find "Want to Read" button ref
→ Act click on that ref
→ Re-snapshot to confirm (should now show "Want to Read" as selected or show shelved status)
```

**Rating a book:**

```
→ Navigate to book page
→ Snapshot to find rating stars or "Rate this book" section
→ Act click on the appropriate star rating ref
→ Re-snapshot to confirm rating was saved
```

**Changing shelf status:**

```
→ Navigate to book page
→ Snapshot to find the shelf/status dropdown
→ Act click to open dropdown, then re-snapshot
→ Act click on desired status (Read, Currently Reading, etc.)
→ Re-snapshot to confirm
```

**Recovery from shelf action errors:**
- If a shelf action fails with a stale ref error, re-snapshot the current page and retry — do NOT navigate away and back, as this may trigger `ERR_BLOCKED_BY_RESPONSE` blocks from Goodreads
- If you get a missing parameter error, stop and reconstruct the browser call with all required parameters before retrying
- If the error says "Can't reach the browser control service" but the inner error mentions `"not found or not visible"` or `"Run a new snapshot"` — this is a stale ref, not a service outage. Re-snapshot and retry.

## Authentication Check

Before any action that requires login (recommendations, shelf management):

1. Use `browser` → `navigate` to `https://www.goodreads.com`
2. Use `browser` → `snapshot`
3. Look for indicators of logged-in state:
   - Presence of user profile name/avatar
   - "My Books" link in navigation
   - Absence of "Sign In" / "Join" prominent buttons
4. If **logged in**: proceed with the requested action
5. If **not logged in**: inform the user and provide instructions:

> "You need to be logged into Goodreads for this action. Please log in at https://www.goodreads.com/user/sign_in in your browser, then try again."

## Response Format

When presenting results to the user, use clear formatting:

**For search results:**
- Numbered list with title, author, rating, and year
- Offer to get details on any specific result

**For book details:**
- Title and author prominently
- Rating (e.g., "4.28/5 from 1.2M ratings")
- Description (full text when possible)
- Key metadata (pages, publication date, genres)
- Top 2-3 review excerpts if available

**For recommendations:**
- Grouped by reason/category when possible
- Include the "because you liked X" context

**For shelf actions:**
- Confirm the action was taken ("Added 'Dune' to your Want to Read shelf")
- Report if something went wrong

## Handling Errors

- **Page didn't load**: Retry navigation once, then inform the user
- **No results found**: Suggest alternative search terms
- **Auth required but not logged in**: Provide login URL and instructions
- **Unexpected page structure**: Use `screenshot` to see what's actually displayed, adapt approach
- **Stale refs after acting**: Always re-snapshot; never reuse old refs
- **Wrapped errors — ALWAYS read the full error message.** Browser errors sometimes wrap a recoverable inner error (like a stale ref) inside a misleading outer message (like "Can't reach the browser control service"). Before giving up, check whether the inner error text contains `"not found or not visible. Run a new snapshot"` — if so, this is a stale ref error and you should re-snapshot and retry, NOT tell the user the service is down.

See `assets/error-handling.md` for detailed error scenarios and recovery strategies.
See `references/WORKFLOWS.md` for step-by-step browser interaction sequences.
See `references/SELECTORS.md` for page structure patterns.
See `references/URLS.md` for Goodreads URL patterns.
