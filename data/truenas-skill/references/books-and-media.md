# Books & Media

Book and media services for audiobooks, ebooks, and video downloads.
Each service is independent — users pick what applies to their setup.

## Environment Variables

```
AUDIOBOOKSHELF_URL, AUDIOBOOKSHELF_API_KEY
LAZYLIBRARIAN_URL, LAZYLIBRARIAN_API_KEY
METUBE_URL                           — YouTube downloader (no auth)
CALIBRE_WEB_URL                      — Ebook library (session auth, no API key)
```

## Audiobookshelf

```bash
# Health check
curl -s "$AUDIOBOOKSHELF_URL/healthcheck"

# Verify auth
curl -s -X POST "$AUDIOBOOKSHELF_URL/api/authorize" \
  -H "Authorization: Bearer $AUDIOBOOKSHELF_API_KEY"

# Libraries
curl -s "$AUDIOBOOKSHELF_URL/api/libraries" -H "Authorization: Bearer $AUDIOBOOKSHELF_API_KEY"

# Library items
curl -s "$AUDIOBOOKSHELF_URL/api/libraries/LIB_ID/items" \
  -H "Authorization: Bearer $AUDIOBOOKSHELF_API_KEY"

# Search
curl -s "$AUDIOBOOKSHELF_URL/api/libraries/LIB_ID/search?q=QUERY" \
  -H "Authorization: Bearer $AUDIOBOOKSHELF_API_KEY"

# Listening stats
curl -s "$AUDIOBOOKSHELF_URL/api/me/listening-stats" \
  -H "Authorization: Bearer $AUDIOBOOKSHELF_API_KEY"
```

## LazyLibrarian (Book Manager)

```bash
# Version/status
curl -s "$LAZYLIBRARIAN_URL/api?cmd=getVersion&apikey=$LAZYLIBRARIAN_API_KEY"

# Search for books
curl -s "$LAZYLIBRARIAN_URL/api?cmd=searchBook&name=QUERY&apikey=$LAZYLIBRARIAN_API_KEY"

# Search for author
curl -s "$LAZYLIBRARIAN_URL/api?cmd=findAuthor&name=AUTHOR&apikey=$LAZYLIBRARIAN_API_KEY"

# Get wanted books
curl -s "$LAZYLIBRARIAN_URL/api?cmd=getWanted&apikey=$LAZYLIBRARIAN_API_KEY"
```

## MeTube (YouTube Downloader)

```bash
# Queue download
curl -X POST "$METUBE_URL/add" -H "Content-Type: application/json" \
  -d '{"url": "YOUTUBE_URL", "quality": "best"}'

# History
curl -s "$METUBE_URL/api/history"
```

## Calibre-Web (Ebook Library)

Calibre-Web uses session authentication (username/password), not API keys.
The OPDS feed is available at `/opds` for e-reader integration.

## Common Agent Tasks

### "Search for an audiobook"

Use Audiobookshelf's search endpoint with the library ID.

### "Find a book"

Use LazyLibrarian's `searchBook` command.

### "Download a YouTube video"

Use MeTube's `/add` endpoint with the video URL.
