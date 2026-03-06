# Error Handling & Recovery

Strategies for handling common error scenarios when interacting with Goodreads via the `browser` tool.

## Error: No Search Results

**Symptoms in snapshot:**

- "No results" or "0 results" text
- Empty results area
- Suggestion text like "Did you mean..." or "Try different keywords"

**Recovery:**

1. Check if the query was properly URL-encoded
2. Try simplifying the query (remove special characters, use fewer words)
3. Try alternative search terms:
   - If searching by full title, try a shorter version
   - If searching by ISBN, try the title instead
   - If searching by author, try "author name" without first name

**User response template:**
> I couldn't find any results for "<query>" on Goodreads. Here are some things to try:
>
> - Check the spelling of the title or author name
> - Try a shorter or simpler search term
> - Search by author name if the title isn't working
>
> Would you like me to try a different search?

## Error: Authentication Required

**Symptoms in snapshot:**

- Redirected to sign-in page (`/user/sign_in` in URL)
- "Sign In" form visible
- "You need to be signed in" message

**Recovery:**

1. Do NOT attempt to fill in login credentials
2. Inform the user they need to log in manually
3. Offer non-auth alternatives when possible

**User response template:**
> This action requires you to be logged into Goodreads. Please:
>
> 1. Open <https://www.goodreads.com/user/sign_in> in your browser
> 2. Log in with your Goodreads account
> 3. Once logged in, try your request again
>
> In the meantime, I can help with things that don't require login, like searching for books or viewing book details.

## Error: Authentication Session Expired

**Symptoms in snapshot:**

- Was previously logged in but now seeing sign-in prompts
- Partial page load with auth wall

**Recovery:**

1. Run the Authentication Check workflow to confirm state
2. Inform the user their session has expired
3. Same response as Authentication Required above

## Error: Page Not Found (404)

**Symptoms in snapshot:**

- "Page not found" or "404" text
- Generic error page content
- "The page you're looking for doesn't exist"

**Recovery:**

1. Verify the URL was constructed correctly (check book ID, query encoding)
2. Try navigating to the Goodreads homepage and searching from there
3. The book/resource may have been removed from Goodreads

**User response template:**
> I couldn't find that page on Goodreads — it may have been removed or the URL may be incorrect. Let me try searching for it instead.

## Error: Rate Limiting or Blocking

**Symptoms in snapshot:**

- CAPTCHA or verification challenge
- "Access denied" or "Too many requests" message
- Cloudflare challenge page
- Blank or minimal page content

**Recovery:**

1. Wait a moment before retrying (the browser tool may handle this)
2. If CAPTCHA is present, inform the user
3. Use `browser` → `screenshot` to see if there's a visual challenge

**User response template:**
> Goodreads is showing a verification challenge, which likely means we've made too many requests. Please:
>
> 1. Wait a minute or two
> 2. Try your request again
>
> If the issue persists, you may need to open Goodreads in your browser and complete the verification manually.

## Error: ERR_BLOCKED_BY_RESPONSE

**Symptoms:**

- Error message contains `ERR_BLOCKED_BY_RESPONSE` or `net::ERR_BLOCKED_BY_RESPONSE`
- Navigation fails immediately without loading any page content
- Often occurs when retrying a navigation too quickly after a failed action

**Cause:**

Goodreads response headers (Cross-Origin Resource Policy / Cross-Origin Embedder Policy) are blocking the browser's automated access. This is distinct from rate limiting or CAPTCHAs — it's a server-side header-level block that prevents the page from loading at all.

**Recovery:**

1. Do NOT retry the same navigation immediately — this will likely fail again
2. First, navigate to the Goodreads homepage: `browser → navigate → https://www.goodreads.com`
3. Call `browser → snapshot` to verify the homepage loaded
4. Then navigate to your target page from there
5. If the target page is still blocked, provide the user with the direct URL and manual instructions

**Prevention:**

- Avoid unnecessary re-navigation. If you're already on the correct page, re-snapshot instead of navigating away and back
- When transitioning between skill capabilities (e.g., from "Get Book Details" to "Manage Reading Lists"), stay on the current page and re-snapshot rather than navigating to the same page again

**User response template:**
> Goodreads is blocking my attempt to access that page directly. Let me try a different approach...
>
> If I'm unable to get through, you can complete this action manually:
> 1. Open `<target URL>` in your browser
> 2. `<describe the action the user wanted, e.g., "Click the 'Currently Reading' button">`

## Error: Missing Required Parameters

**Symptoms:**

- Error message contains `"targetUrl required"`, `"ref required"`, or similar missing-parameter errors
- Browser action fails immediately without attempting any page interaction
- Typically occurs during panicked error recovery when the agent rushes a retry

**Cause:**

The agent called a browser action without all required parameters. Common cases:
- `navigate` called without a `targetUrl`
- `act` called without a `ref` or with a ref that was never obtained from a snapshot

**Recovery:**

1. **Stop and assess.** Do not immediately retry — identify what you were trying to do
2. Determine the correct target URL or ref:
   - For `navigate`: construct the full Goodreads URL (e.g., `https://www.goodreads.com/book/show/12345`)
   - For `act`: call `snapshot` first to get fresh refs, then use the correct ref
3. Construct the browser call with all required parameters
4. Execute the corrected call

**Prevention checklist — verify before every browser call:**

- `navigate` → Do I have a `targetUrl`? Is it a valid, complete URL?
- `act` → Do I have a `ref` from my most recent `snapshot`? (Not from a previous page)
- `snapshot` / `screenshot` → No required parameters (safe to call anytime)

**Wrong:**
```
→ act fails with stale ref
→ Panic: browser → navigate (without targetUrl!)   ← ERROR
```

**Right:**
```
→ act fails with stale ref
→ browser → snapshot (get fresh refs)
→ browser → act (using fresh ref from new snapshot)
```

## Error: Stale Refs

**Symptoms:**

- Error message: `Unknown ref "X". Run a new snapshot` (exact pattern)
- Error message: `Element "X" not found or not visible. Run a new snapshot to see current page elements`
- `act` command fails or targets the wrong element
- Page content seems different from what was expected
- Actions produce unexpected results

**⚠️ CRITICAL: Wrapped error messages.** Stale ref errors are sometimes wrapped inside a misleading outer error. For example:

```json
{
  "status": "error",
  "error": "Can't reach the OpenClaw browser control service. ... (Error: Error: Element \"e87\" not found or not visible. Run a new snapshot to see current page elements.)"
}
```

**Do NOT take the outer message ("Can't reach the browser control service") at face value.** Read the INNER error — if it says `"not found or not visible. Run a new snapshot"`, this is a stale ref error, NOT a service outage. The fix is to re-snapshot and retry, not to tell the user to restart anything.

**Cause:**

Refs from `snapshot` are tied to a specific page state. Any navigation, page reload, or significant DOM change invalidates all existing refs. This commonly occurs when:
- Transitioning between skill capabilities (e.g., from "Get Book Details" to "Manage Reading Lists")
- Reusing refs after clicking a link that loaded a new page
- Acting on refs obtained before an intervening navigation

**Recovery:**

1. **Always re-snapshot after any navigation.** This is the #1 prevention strategy.
2. If an action seems wrong, immediately re-snapshot to get fresh refs
3. Re-identify the target element in the new snapshot
4. Retry the action with the correct ref

**Wrong:**
```
→ browser → snapshot → get ref "17" for book title
→ browser → act click ref "17" (navigates to book page)
→ browser → act click ref "5" from the FIRST snapshot   ← STALE REF ERROR
```

**Right:**
```
→ browser → snapshot → get ref "17" for book title
→ browser → act click ref "17" (navigates to book page)
→ browser → snapshot  ← GET FRESH REFS
→ browser → act click ref "3" from the NEW snapshot      ← correct
```

**Prevention:**

- Never store or reuse refs across page navigations
- After every `act` that might change the page, call `snapshot` again
- If more than ~30 seconds have passed since last snapshot, re-snapshot before acting
- **When transitioning between skill capabilities** (e.g., from "Get Book Details" to "Manage Reading Lists"), always start with a fresh snapshot even if you think you're on the right page
- If a stale ref error occurs, re-snapshot and retry — do NOT navigate away and back, as this may trigger `ERR_BLOCKED_BY_RESPONSE` blocks

## Error: Unexpected Page Structure

**Symptoms in snapshot:**

- Expected elements (buttons, links, sections) are missing
- Page layout seems different from documented patterns
- Content is present but in an unrecognizable format

**Recovery:**

1. Use `browser` → `screenshot` to get a visual view of the page
2. Compare visual layout with snapshot text to understand what's changed
3. Adapt extraction approach based on what's actually on the page
4. If the page structure has fundamentally changed, inform the user

**User response template:**
> Goodreads appears to have updated their page layout, and I'm having trouble reading the content in the expected format. Let me try a different approach...

**Long-term fix:**

- Update `references/SELECTORS.md` with new page patterns
- Update `references/WORKFLOWS.md` if interaction flows changed

## Error: Book Page Missing Expected Data

**Symptoms:**

- Book page loads but some fields are empty
- Description missing, rating not shown, reviews not visible

**Recovery:**

1. Some books have incomplete data on Goodreads — this is normal
2. Report what data IS available
3. For missing descriptions, check if there's a "more" link that wasn't detected
4. For missing reviews, the book may simply have no community reviews yet

**User response template:**
> Here's what I found for "<Book Title>" (note: some information wasn't available on Goodreads):
>
> - Title: <title>
> - Author: <author>
> - Rating: <rating or "Not yet rated">
> - Description: <description or "No description available">

## Error: Browser Tool Failure

**Symptoms:**

- Browser tool returns an error instead of page content
- Navigation timeout
- Snapshot returns empty or error content

**⚠️ FIRST: Check for wrapped errors.** Before treating this as a true browser failure, read the FULL error message. If the error text contains `"not found or not visible. Run a new snapshot"` or `"Unknown ref"`, this is actually a stale ref error wrapped in a misleading outer message — see the "Stale Refs" section above. Re-snapshot and retry instead of giving up.

**Recovery (for genuine browser failures only):**

1. Retry the navigation once
2. If the retry fails, try navigating to the Goodreads homepage first, then to the target page
3. If all navigation fails, inform the user of a technical issue

**User response template:**
> I'm having trouble connecting to Goodreads right now. This could be a temporary issue. Please try again in a moment, or you can visit Goodreads directly at <https://www.goodreads.com>.

## General Error Handling Principles

1. **Retry once** before reporting failure — transient issues are common
2. **Screenshot on confusion** — when snapshot output doesn't match expectations, a screenshot reveals the truth
3. **Never guess** — if you can't confirm an action succeeded, say so honestly
4. **Offer alternatives** — when one approach fails, suggest a different path to the user's goal
5. **Stay calm in responses** — don't alarm the user about technical details; focus on what they can do next
6. **Never handle credentials** — if auth is needed, always direct the user to log in themselves
