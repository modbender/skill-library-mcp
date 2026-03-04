# Instagram Graph API — Carousel Publishing Reference

## Endpoints

All endpoints use `https://graph.facebook.com/v21.0/`.

### Create Carousel Item Container
```
POST /{ig-user-id}/media
  image_url={public_url}
  is_carousel_item=true
  access_token={token}
```
Returns: `{"id": "container_id"}`

### Create Carousel Container
```
POST /{ig-user-id}/media
  caption={text}
  media_type=CAROUSEL
  children={comma_separated_container_ids}
  access_token={token}
```
Returns: `{"id": "carousel_id"}`

### Publish
```
POST /{ig-user-id}/media_publish
  creation_id={carousel_id}
  access_token={token}
```
Returns: `{"id": "post_id"}`

### Get Permalink
```
GET /{post_id}?fields=permalink&access_token={token}
```
Returns: `{"permalink": "https://www.instagram.com/p/XXX/", "id": "..."}`

## Constraints
- Carousel: 2–10 images
- Images must be publicly accessible URLs (no localhost, no auth-gated)
- JPEG format, max 8MB per image
- Rate limit: ~25 API calls per hour per user
- `--data-urlencode` for caption (contains special chars)

## Common Issues
- **Image format error**: Cloudflare CDN may transform images. Use raw GitHub URLs instead.
- **Container not ready**: Wait a few seconds after creating child containers before creating the carousel container.
- **Token expiry**: Long-lived tokens last 60 days. Check with `GET /me?access_token={token}`.
