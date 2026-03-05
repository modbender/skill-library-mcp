# Goodreads URL Patterns

Reference for all Goodreads URL patterns used by this skill.

**Base URL:** `https://www.goodreads.com`

## Search

| Pattern | Description | Example |
|---------|-------------|---------|
| `/search?q=<query>` | General search (books, authors, etc.) | `/search?q=dune` |
| `/search?q=<query>&search_type=books` | Books only | `/search?q=dune&search_type=books` |
| `/search?q=<query>&search_type=authors` | Authors only | `/search?q=frank+herbert&search_type=authors` |

**URL encoding tips:**

- Spaces → `+` or `%20` (both work)
- Ampersand → `%26`
- Quotes → `%22`
- Apostrophes → `%27`
- Colons → `%3A`

## Book Pages

| Pattern | Description | Example |
|---------|-------------|---------|
| `/book/show/<id>` | Book by numeric ID | `/book/show/234225` |
| `/book/show/<id>.<slug>` | Book with SEO slug | `/book/show/234225.Dune` |
| `/book/show/<id>-<slug>` | Alternative slug format | `/book/show/234225-dune` |

Book IDs are stable numeric identifiers. The slug portion is optional and ignored by Goodreads — only the numeric ID matters.

## Author Pages

| Pattern | Description | Example |
|---------|-------------|---------|
| `/author/show/<id>.<name>` | Author profile | `/author/show/58.Frank_Herbert` |
| `/author/list/<id>.<name>` | Author's book list | `/author/list/58.Frank_Herbert` |

## User Shelves & Reading Lists

| Pattern | Description | Example |
|---------|-------------|---------|
| `/review/list/<user_id>` | User's default shelf | `/review/list/12345678` |
| `/review/list/<user_id>?shelf=read` | "Read" shelf | `/review/list/12345678?shelf=read` |
| `/review/list/<user_id>?shelf=currently-reading` | "Currently Reading" shelf | `/review/list/12345678?shelf=currently-reading` |
| `/review/list/<user_id>?shelf=to-read` | "Want to Read" shelf | `/review/list/12345678?shelf=to-read` |
| `/review/list/<user_id>?shelf=<custom>` | Custom shelf | `/review/list/12345678?shelf=favorites` |

**Note:** User ID is required to view shelves. The logged-in user's shelves can be accessed via the "My Books" link in the navigation.

## Recommendations

| Pattern | Description | Auth Required |
|---------|-------------|---------------|
| `/recommendations` | Personalized recommendations | Yes |
| `/recommendations/genre/<genre>` | Genre-based recommendations | Yes |

## Genres & Lists

| Pattern | Description | Auth Required |
|---------|-------------|---------------|
| `/genres/<genre>` | Genre page | No |
| `/genres/list` | All genres | No |
| `/list/popular_lists` | Popular book lists | No |
| `/list/show/<id>` | Specific list | No |
| `/list/best_of_year/<year>` | Best of year lists | No |

**Common genre slugs:** `fiction`, `non-fiction`, `mystery`, `science-fiction`, `fantasy`, `romance`, `thriller`, `historical-fiction`, `horror`, `biography`

## Authentication

| Pattern | Description |
|---------|-------------|
| `/user/sign_in` | Login page |
| `/user/sign_up` | Registration page |

## Pagination

Most list pages support pagination via query parameter:

- `?page=<n>` — Page number (1-indexed)
- Example: `/search?q=dune&page=2`

Can be combined with other query params: `/review/list/12345678?shelf=read&page=2`
