# Unsplash API

Search, browse, and download high-quality free photos from Unsplash's library of millions of images.

## Setup & Authentication

### Get your Access Key
1. Create account at https://unsplash.com/developers
2. Register a new application
3. Copy your **Access Key** (starts with your app name)

### Store credentials
```bash
mkdir -p ~/.config/unsplash
echo "YOUR_ACCESS_KEY" > ~/.config/unsplash/access_key
chmod 600 ~/.config/unsplash/access_key
```

Or set environment variable:
```bash
export UNSPLASH_ACCESS_KEY="your_access_key_here"
```

### Rate Limits
- **Demo**: 50 requests/hour
- **Production**: 5,000 requests/hour (after app approval)
- Only `/v1/messages` endpoints count; image URLs (`images.unsplash.com`) don't

## Common Operations

### Search Photos
```bash
curl "https://api.unsplash.com/search/photos?query=nature&per_page=10" \
  -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}"
```

**Parameters:**
- `query`: Search terms (required)
- `page`: Page number (default: 1)
- `per_page`: Results per page (default: 10, max: 30)
- `order_by`: `relevant` (default) or `latest`
- `color`: Filter by color (`black_and_white`, `black`, `white`, `yellow`, `orange`, `red`, `purple`, `magenta`, `green`, `teal`, `blue`)
- `orientation`: `landscape`, `portrait`, or `squarish`

### Get Random Photo
```bash
curl "https://api.unsplash.com/photos/random?query=coffee&count=1" \
  -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}"
```

**Parameters:**
- `query`: Limit to search term (optional)
- `count`: Number of photos (1-30, default: 1)
- `orientation`: Filter by orientation
- `collections`: Filter by collection IDs (comma-separated)

### Get Photo Details
```bash
curl "https://api.unsplash.com/photos/PHOTO_ID" \
  -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}"
```

Returns full photo metadata including EXIF, location, user info, and all image URLs.

### Track Download (Required!)
**Important:** You MUST trigger this endpoint when downloading a photo to comply with API guidelines.
```bash
curl "https://api.unsplash.com/photos/PHOTO_ID/download" \
  -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}"
```

This increments the download counter. Response includes the download URL.

### List Editorial Feed
```bash
curl "https://api.unsplash.com/photos?per_page=10" \
  -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}"
```

### Browse Collections
```bash
# List all collections
curl "https://api.unsplash.com/collections?per_page=10" \
  -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}"

# Get collection photos
curl "https://api.unsplash.com/collections/COLLECTION_ID/photos" \
  -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}"
```

### User Photos
```bash
curl "https://api.unsplash.com/users/USERNAME/photos?per_page=10" \
  -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}"
```

## Working with Images

### Image URLs
Every photo response includes these URLs:
```json
{
  "urls": {
    "raw": "https://images.unsplash.com/photo-xxx?ixid=xxx",
    "full": "...?ixid=xxx&q=80&fm=jpg",
    "regular": "...?ixid=xxx&w=1080&fit=max",
    "small": "...?w=400&fit=max",
    "thumb": "...?w=200&fit=max"
  }
}
```

### Dynamic Resizing
Add parameters to any image URL (keep the `ixid` parameter!):
- `w=1500`: Set width
- `h=800`: Set height
- `dpr=2`: Device pixel ratio
- `q=75`: Quality (1-100)
- `fm=jpg`: Format (jpg, png, webp, avif)
- `fit=crop`: Fit mode (crop, max, clip)
- `crop=entropy`: Crop mode

**Example:**
```
https://images.unsplash.com/photo-xxx?ixid=xxx&w=1500&h=1000&fit=crop&q=85
```

### BlurHash Placeholders
Each photo includes a `blur_hash` field - a compact string representation for showing blurred placeholders while images load.
```json
{
  "blur_hash": "LoC%a7IoIVxZ_NM|M{s:%hRjWAo0"
}
```

## Response Structure

### Photo Object (abbreviated)
```json
{
  "id": "LBI7cgq3pbM",
  "created_at": "2016-05-03T11:00:28-04:00",
  "width": 5245,
  "height": 3497,
  "color": "#60544D",
  "blur_hash": "LoC%a7IoIVxZ_NM|M{s:%hRjWAo0",
  "description": "A man drinking coffee",
  "urls": { "raw": "...", "full": "...", "regular": "..." },
  "links": {
    "download": "...",
    "download_location": "https://api.unsplash.com/photos/xxx/download"
  },
  "user": {
    "username": "johndoe",
    "name": "John Doe",
    "profile_image": { "small": "...", "medium": "...", "large": "..." }
  }
}
```

### Search Response
```json
{
  "total": 133,
  "total_pages": 7,
  "results": [ /* array of photo objects */ ]
}
```

## Best Practices

### Attribution
Always attribute photos to their creators:
```
Photo by [Name] on Unsplash
```
Link to photographer's Unsplash profile when possible.

### Download Tracking
- Call `/photos/:id/download` before allowing users to download
- This is required by Unsplash API Guidelines
- Don't use it for just displaying images (that's tracked automatically via hotlinking)

### Hotlinking
- You can hotlink images directly from `images.unsplash.com`
- These don't count against rate limits
- Views are tracked automatically
- Always keep the `ixid` parameter in URLs

### Caching
- Public endpoints (search, photos) are cacheable
- Consider caching search results client-side to reduce API calls

## Quick Reference
```bash
# Store key
export UNSPLASH_ACCESS_KEY="your_key"

# Search
curl "https://api.unsplash.com/search/photos?query=ocean&per_page=5" \
  -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}"

# Random photo
curl "https://api.unsplash.com/photos/random?query=mountains" \
  -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}"

# Get photo
curl "https://api.unsplash.com/photos/PHOTO_ID" \
  -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}"

# Track download (required when downloading!)
curl "https://api.unsplash.com/photos/PHOTO_ID/download" \
  -H "Authorization: Client-ID ${UNSPLASH_ACCESS_KEY}"
```

## Notes

- Base URL: `https://api.unsplash.com`
- All responses are JSON
- Pagination via `page` and `per_page` parameters
- Link headers provide first/prev/next/last page URLs
- Image requests to `images.unsplash.com` don't count against rate limits
- Keep the `ixid` parameter when using/manipulating image URLs
- For production use, apply for increased rate limits in your dashboard

## Common Filters

### Colors
`black_and_white`, `black`, `white`, `yellow`, `orange`, `red`, `purple`, `magenta`, `green`, `teal`, `blue`

### Orientations
`landscape`, `portrait`, `squarish`

### Sort Options
- Photos: `latest`, `oldest`, `popular`
- Search: `relevant`, `latest`

## Error Handling

- `401 Unauthorized`: Invalid or missing access key
- `403 Forbidden`: Rate limit exceeded or forbidden action
- `404 Not Found`: Photo/user/collection doesn't exist

Check `X-Ratelimit-Remaining` header to monitor your rate limit status.