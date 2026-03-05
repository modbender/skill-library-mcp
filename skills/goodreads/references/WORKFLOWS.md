# Goodreads Browser Workflows

Reusable step-by-step browser interaction sequences. All steps use the `browser` tool.

## ⚠️ Common Mistakes — Quick Reference

Before starting any workflow, review these patterns:

**Stale refs — always re-snapshot after navigation:**
```
WRONG: snapshot → navigate → act (using old ref)        ❌
RIGHT: snapshot → navigate → snapshot → act (new ref)   ✅
```

**Missing parameters — every browser action needs its required params:**
```
WRONG: browser → navigate (no targetUrl!)               ❌
RIGHT: browser → navigate → https://www.goodreads.com/… ✅

WRONG: browser → act (no ref, or ref from old snapshot!) ❌
RIGHT: browser → snapshot → act (ref from THAT snapshot) ✅
```

**Over-navigation — don't leave and come back when you can just re-snapshot:**
```
WRONG: Already on book page → navigate away → navigate back → snapshot  ❌
       (risks ERR_BLOCKED_BY_RESPONSE)
RIGHT: Already on book page → snapshot (get fresh refs for current page) ✅
```

**Wrapped errors — read the INNER error before giving up:**
```
WRONG: See "Can't reach browser control service" → tell user to restart  ❌
       (the inner error says "Element not found...Run a new snapshot")
RIGHT: Read inner error → recognize stale ref → re-snapshot → retry      ✅
```

---

## Workflow: Search and Get Details

Complete flow from search query to detailed book information.

```
1. browser → navigate → https://www.goodreads.com/search?q=<url-encoded-query>
2. browser → snapshot
3. Parse search results from snapshot (titles, authors, ratings)
4. Present top results to user
5. If user wants details on a specific book:
   a. browser → act → click on the book title ref from current snapshot
   b. browser → snapshot    ← MUST re-snapshot after navigation
   c. Parse book details (title, author, rating, description, reviews)
   d. If description is truncated:
      i.  browser → act → click "...more" ref
      ii. browser → snapshot    ← re-snapshot again
      iii. Parse full description
6. Present complete book details to user
```

## Workflow: Authentication Check

Verify whether the user is logged into Goodreads before auth-required actions.

```
1. browser → navigate → https://www.goodreads.com
2. browser → snapshot
3. Analyze snapshot for auth indicators:
   - LOGGED IN if: user profile name visible, "My Books" link present
   - LOGGED OUT if: "Sign In" button visible, "Join" call-to-action present
4. If LOGGED IN:
   → Proceed with the auth-required workflow
5. If LOGGED OUT:
   → Inform user: "You need to be logged into Goodreads. Please visit
     https://www.goodreads.com/user/sign_in and log in, then try again."
   → Optionally offer non-auth alternatives (genre browsing, public lists)
```

## Workflow: Add Book to "Want to Read" Shelf

```
1. If already on the target book's page (e.g., from a prior search/details lookup),
   skip navigation — just re-snapshot the current page for fresh refs.
   Otherwise, navigate to the book page (use Search workflow if needed).
2. browser → snapshot
3. Find the "Want to Read" button ref in the snapshot
4. browser → act → click on the "Want to Read" ref
5. browser → snapshot    ← re-snapshot to verify
6. Confirm to user:
   - Look for changed button state (e.g., checkmark, "Shelved" status)
   - If confirmation found: "Added '<Title>' to your Want to Read shelf!"
   - If unclear: use browser → screenshot to visually verify
   - If stale ref error: re-snapshot and retry — do NOT navigate away and back
```

## Workflow: Mark Book as Read with Rating

```
1. If already on the target book's page (e.g., from a prior search/details lookup),
   skip navigation — just re-snapshot the current page for fresh refs.
   Otherwise, navigate to the book page (use Search workflow if needed).
2. browser → snapshot
3. Find the shelf/status button or dropdown ref
4. browser → act → click to open status options
5. browser → snapshot    ← re-snapshot for updated refs
6. Find "Read" option ref
7. browser → act → click "Read" ref
8. browser → snapshot    ← re-snapshot again
9. Find star rating elements (look for rating stars or "Rate this book")
10. browser → act → click on the star corresponding to desired rating
    (e.g., 4th star for a 4/5 rating)
11. browser → snapshot    ← final verification
12. Confirm to user: "Marked '<Title>' as Read with a rating of <N>/5"
```

## Workflow: Expand Truncated Description

```
1. On a book detail page after snapshot
2. Look for "...more" or "Show more" ref in the description area
3. If found:
   a. browser → act → click on the "more" ref
   b. browser → snapshot    ← re-snapshot for full text
   c. Parse the now-expanded description
4. If not found:
   - Description may already be fully displayed
   - Or the expand control uses a different pattern — try browser → screenshot
     to visually inspect
```

## Workflow: Handle Pagination

For any list page (search results, shelves, genre pages) with multiple pages.

```
1. After parsing current page results
2. Look for pagination indicators in snapshot:
   - "Next" or "→" link ref
   - Page number refs (1, 2, 3, ...)
   - "Showing X-Y of Z results"
3. If more pages needed:
   a. Option A: Click "Next" ref
      - browser → act → click "Next" ref
      - browser → snapshot    ← re-snapshot
   b. Option B: Navigate directly
      - browser → navigate → append ?page=<N> to current URL
      - browser → snapshot
4. Parse and accumulate results from the new page
5. Repeat as needed (be mindful of not loading too many pages)
```

## Workflow: Browse Recommendations (Authenticated)

```
1. Run Authentication Check workflow
2. If logged in:
   a. browser → navigate → https://www.goodreads.com/recommendations
   b. browser → snapshot
   c. Parse recommendation groups:
      - Look for "Because you liked <Book>" headers
      - Under each, extract recommended book titles, authors, ratings
   d. Present recommendations grouped by source
3. If more recommendations exist:
   - Look for "Show more" or pagination
   - Follow Pagination workflow
```

## Workflow: Browse Recommendations (Unauthenticated Fallback)

When the user is not logged in, offer alternative discovery paths.

```
1. Ask user for a genre or interest
2. browser → navigate → https://www.goodreads.com/genres/<genre>
3. browser → snapshot
4. Parse "Most Popular" and "New Releases" sections
5. Present curated results to user

Alternative:
1. browser → navigate → https://www.goodreads.com/list/popular_lists
2. browser → snapshot
3. Parse popular list titles and descriptions
4. Let user pick a list to explore
5. browser → act → click on chosen list ref
6. browser → snapshot    ← re-snapshot
7. Parse and present list contents
```

## Workflow: View User's Shelf

```
1. Run Authentication Check workflow
2. If logged in:
   a. browser → snapshot (on Goodreads homepage)
   b. Find "My Books" link ref
   c. browser → act → click "My Books" ref
   d. browser → snapshot    ← re-snapshot
   e. Parse shelf contents: book titles, ratings, dates
   f. To switch shelves:
      - Find shelf tab refs ("Read", "Currently Reading", "Want to Read")
      - browser → act → click desired shelf ref
      - browser → snapshot    ← re-snapshot
      - Parse updated shelf contents
```

## General Tips

- **Always re-snapshot after any navigation or click that changes the page.** This is the single most important rule.
- **When in doubt, screenshot.** If snapshot output is confusing, take a screenshot to see the actual visual state.
- **Don't over-paginate.** For search results, 2-3 pages is usually sufficient. Ask the user before loading more.
- **Cache nothing.** Refs, page state, and content can change at any time. Always work with fresh snapshots.
- **Be explicit in confirmations.** After shelf actions, always re-snapshot to verify the action took effect.
