# Goodreads Page Structure & Selectors

Reference for identifying content in `browser` → `snapshot` output. Since Goodreads uses dynamic rendering, look for **text patterns and keywords** rather than CSS selectors.

## General Navigation (All Pages)

**Logged-in indicators** (present in snapshot when authenticated):

- User's display name in the navigation area
- "My Books" link
- "Browse" dropdown
- Notification bell / inbox icon references

**Logged-out indicators:**

- "Sign In" link/button
- "Join" link/button
- Prominent call-to-action for registration

## Search Results Page

**URL:** `/search?q=<query>`

**Content patterns in snapshot:**

```
Search results for "<query>"

<Book Title>                    ← Clickable link (has a ref)
by <Author Name>                ← Clickable link (has a ref)
<avg rating> avg rating — <N> ratings — published <year>
```

**Key anchors to look for:**

- `"Search results for"` — confirms you're on the search page
- `"by "` — precedes author name
- `"avg rating"` — precedes rating count
- `"ratings"` — follows rating number
- `"published"` — precedes publication year
- `"Showing <N> of <total>"` or pagination indicators

**No results pattern:**

- `"No results"` or `"0 results"`
- Suggestion text like `"Try searching for..."`

## Book Detail Page

**URL:** `/book/show/<id>`

**Content patterns in snapshot:**

```
<Book Title>
by <Author Name>

<rating value>                  ← e.g., "4.28"
<N> ratings                     ← e.g., "1,234,567 ratings"
<N> reviews                     ← e.g., "45,678 reviews"

<Description text>
...more                         ← Clickable ref to expand truncated descriptions

<N> pages, <format>             ← e.g., "412 pages, Paperback"
Published <date>                ← e.g., "Published August 1, 2005"

Genres:
<genre links>                   ← Clickable refs
```

**Key anchors to look for:**

- `"by "` — precedes author (clickable link)
- `"ratings"` — near the numeric rating value
- `"reviews"` — near the review count
- `"...more"` or `"Show more"` — truncated description expander
- `"pages"` — near page count
- `"Published"` — precedes publication date
- `"Genres"` or genre-like section — lists genres/shelves

**Shelf/Action buttons:**

- `"Want to Read"` — primary shelving button
- `"Currently Reading"` — status option
- `"Read"` — status option
- Star/rating indicators — for rating the book
- `"Write a review"` — review prompt

**Community reviews section:**

- `"Community Reviews"` header
- Individual reviews with rating stars, reviewer name, review text
- `"See all reviews"` or pagination for more reviews

## Recommendations Page

**URL:** `/recommendations`

**Content patterns in snapshot:**

```
Recommendations

Because you liked <Book Title>:
  <Recommended Book Title>      ← Clickable link
  by <Author Name>
  <rating> avg rating
```

**Key anchors:**

- `"Recommendations"` — page header
- `"Because you liked"` — recommendation reason
- `"Based on your"` — alternative recommendation context
- `"avg rating"` — rating for recommended book

**If not logged in:**

- Redirect to sign-in page
- Look for `"Sign In"` or `"sign_in"` in the URL

## User Shelf Page

**URL:** `/review/list/<user_id>?shelf=<shelf>`

**Content patterns in snapshot:**

```
<User Name>'s books

<shelf_name> (<count>)          ← Shelf tabs/links

<Book Title>                    ← Clickable link
<Author Name>
<user's rating>
<date read / date added>
```

**Key anchors:**

- Shelf name and count in parentheses
- `"date read"` or `"date added"` columns
- `"remove"` or shelf-change options per book
- Pagination indicators for large shelves

## Genre Page

**URL:** `/genres/<genre>`

**Content patterns in snapshot:**

```
<Genre Name> Books

Most Popular <Genre> Books
  <Book Title>                  ← Clickable link
  by <Author Name>
  <rating> avg rating — <N> ratings

New Releases in <Genre>
  ...
```

**Key anchors:**

- `"Most Popular"` — popular books section
- `"New Releases"` — recent additions
- `"avg rating"` — rating indicator

## Tips for Snapshot Parsing

1. **Ratings** are typically decimal numbers near the word "rating" or "ratings" (e.g., `4.28 avg rating`)
2. **Counts** use comma separators (e.g., `1,234,567 ratings`)
3. **Clickable elements** have ref numbers in the snapshot — these are what you pass to `act`
4. **Truncated text** often ends with `...more` or `...` followed by a clickable ref
5. **Multi-section pages** have clear header patterns to delineate sections
