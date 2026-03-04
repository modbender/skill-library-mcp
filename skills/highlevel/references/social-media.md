# Social Media Planner API Reference

Base: `https://services.leadconnectorhq.com/social-media-posting/`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/social-media-posting/{locationId}/accounts` | List connected accounts |
| POST | `/social-media-posting/{locationId}/posts/list` | List posts (POST with filters) |
| POST | `/social-media-posting/{locationId}/posts` | Create post |
| PUT | `/social-media-posting/{locationId}/posts/{postId}` | Update post |
| DELETE | `/social-media-posting/{locationId}/posts/{postId}` | Delete post |
| POST | `/social-media-posting/{locationId}/csv` | Import CSV |
| GET | `/social-media-posting/{locationId}/categories` | List categories |
| GET | `/social-media-posting/{locationId}/tags` | List tags |
| GET | `/social-media-posting/{locationId}/stats` | Get statistics |

### OAuth Connections
| Platform | GET Endpoint |
|----------|-------------|
| Facebook | `/social-media-posting/oauth/facebook/start?locationId={id}` |
| Google | `/social-media-posting/oauth/google/start?locationId={id}` |
| Instagram | `/social-media-posting/oauth/instagram/start?locationId={id}` |
| LinkedIn | `/social-media-posting/oauth/linkedin/start?locationId={id}` |
| TikTok | `/social-media-posting/oauth/tiktok/start?locationId={id}` |
| Twitter | `/social-media-posting/oauth/twitter/start?locationId={id}` |

## Create Post Body
```json
{
  "accountIds": ["social_account_id"],
  "post": "Check out our latest offer! 🎉",
  "mediaUrls": ["https://example.com/image.jpg"],
  "scheduleDate": "2026-03-15T14:00:00Z",
  "status": "scheduled",
  "type": "post"
}
```

**Scopes**: `socialplanner/post.*`, `socialplanner/account.*`, `socialplanner/csv.*`, `socialplanner/category.readonly`, `socialplanner/oauth.*`, `socialplanner/tag.readonly`, `socialplanner/statistics.readonly`
