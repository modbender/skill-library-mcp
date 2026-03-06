# Platform-Specific Configs Reference

Platform configs are passed as arrays in the `POST /social-posts` request body. Each config object is tied to a specific connection via `connectionId` (or `pageId` for Facebook).

## TikTok — `tiktokConfigs`

```json
{
  "tiktokConfigs": [
    {
      "connectionId": "tiktok-connection-id",
      "privacyLevel": "PUBLIC_TO_EVERYONE",
      "title": "Video title",
      "caption": "Extended caption text",
      "allowComments": true,
      "allowDuet": true,
      "allowStitch": true,
      "sendAsDraft": false,
      "aiGenerated": false,
      "brandedContent": false,
      "brandedContentOwnBrand": false,
      "autoAddMusic": false
    }
  ]
}
```

| Parameter                | Type    | Required | Description                                                                       |
| ------------------------ | ------- | -------- | --------------------------------------------------------------------------------- |
| `connectionId`           | string  | **yes**  | TikTok account connection ID                                                      |
| `privacyLevel`           | string  | **yes**  | `PUBLIC_TO_EVERYONE`, `MUTUAL_FOLLOW_FRIENDS`, `FOLLOWER_OF_CREATOR`, `SELF_ONLY` |
| `title`                  | string  | no       | Video title (max 90 chars)                                                        |
| `caption`                | string  | no       | Extended caption (max 2,200 chars)                                                |
| `allowComments`          | boolean | no       | Allow comments on the video                                                       |
| `allowDuet`              | boolean | no       | Allow duets                                                                       |
| `allowStitch`            | boolean | no       | Allow stitches                                                                    |
| `sendAsDraft`            | boolean | no       | Save as draft in TikTok app                                                       |
| `aiGenerated`            | boolean | no       | Mark content as AI-generated                                                      |
| `brandedContent`         | boolean | no       | Sponsored/partnership content                                                     |
| `brandedContentOwnBrand` | boolean | no       | Self-promotional content                                                          |
| `autoAddMusic`           | boolean | no       | Auto-add background music                                                         |

**Media notes:**

- Video: MP4/MOV, H.264, max 250MB, 3s-10min. Best: 15-30s, 1080x1920 (9:16)
- Carousels: 2-35 images (photo slideshows)
- Caption: max 2,200 characters

## Instagram — `instagramConfigs`

```json
{
  "instagramConfigs": [
    {
      "connectionId": "instagram-connection-id",
      "postType": "REEL"
    }
  ]
}
```

| Parameter      | Type   | Required | Description                                 |
| -------------- | ------ | -------- | ------------------------------------------- |
| `connectionId` | string | **yes**  | Instagram account connection ID             |
| `postType`     | string | no       | `FEED`, `REEL`, or `STORY`. Default: `FEED` |

**Content types:**

- **FEED**: Feed posts. Single image, carousel (up to 10), or video
- **REEL**: Short-form video, 3-90 seconds, 9:16 recommended. Gets 2-3x reach vs feed
- **STORY**: 24-hour temporary content. Image or video

**Media notes:**

- Video: max 1GB for Reels
- Carousels: up to 10 images or videos

## Facebook — `facebookConfigs`

```json
{
  "facebookConfigs": [
    {
      "pageId": "facebook-page-id",
      "postType": "REEL",
      "videoTitle": "My Video Title"
    }
  ]
}
```

| Parameter    | Type   | Required | Description                                  |
| ------------ | ------ | -------- | -------------------------------------------- |
| `pageId`     | string | **yes**  | Facebook page ID (from social accounts list) |
| `postType`   | string | no       | `FEED`, `REEL`, or `STORY`. Default: `FEED`  |
| `videoTitle` | string | no       | Video title (max 255 chars)                  |

**Content types:**

- **FEED**: Permanent feed content. Up to 10 images OR 1 video. Text limit: 63,206 chars
- **REEL**: Short-form vertical video
- **STORY**: 24-hour temporary content

**Media notes:**

- Images: JPG/PNG, max 30MB each, up to 10 per post
- Cannot mix images and videos in same post

## YouTube — `youtubeConfigs`

```json
{
  "youtubeConfigs": [
    {
      "connectionId": "youtube-connection-id",
      "postType": "SHORTS",
      "videoTitle": "My Video Title",
      "tags": ["tutorial", "howto"],
      "privacyStatus": "public",
      "license": "youtube",
      "notifySubscribers": true,
      "allowEmbedding": true,
      "madeForKids": false,
      "categoryId": "22",
      "playlistId": "PLxxxxxxxx"
    }
  ]
}
```

| Parameter           | Type     | Required | Description                                           |
| ------------------- | -------- | -------- | ----------------------------------------------------- |
| `connectionId`      | string   | **yes**  | YouTube channel connection ID                         |
| `postType`          | string   | no       | `VIDEO` or `SHORTS`. Default: `VIDEO`                 |
| `videoTitle`        | string   | no       | Video title (max 100 chars)                           |
| `tags`              | string[] | no       | Video tags (max 20 tags)                              |
| `privacyStatus`     | string   | no       | `public`, `private`, or `unlisted`. Default: `public` |
| `license`           | string   | no       | `youtube` or `creativeCommon`                         |
| `notifySubscribers` | boolean  | no       | Notify subscribers on publish                         |
| `allowEmbedding`    | boolean  | no       | Allow embedding on other sites                        |
| `madeForKids`       | boolean  | no       | COPPA compliance flag                                 |
| `categoryId`        | string   | no       | YouTube category ID                                   |
| `playlistId`        | string   | no       | Add to playlist after publishing                      |

**Media notes:**

- Shorts: up to 3 minutes, 9:16 or 1:1
- Copyrighted music limits Shorts to 60 seconds
- H.264 video codec with AAC audio recommended

## Pinterest — `pinterestConfigs`

```json
{
  "pinterestConfigs": [
    {
      "connectionId": "pinterest-connection-id",
      "boardId": "board-id-here",
      "title": "Pin Title",
      "link": "https://example.com/page"
    }
  ]
}
```

| Parameter      | Type   | Required | Description                                             |
| -------------- | ------ | -------- | ------------------------------------------------------- |
| `connectionId` | string | **yes**  | Pinterest account connection ID                         |
| `boardId`      | string | **yes**  | Target board ID                                         |
| `title`        | string | no       | Pin title (max 100 chars)                               |
| `link`         | string | no       | Destination URL when pin is clicked (must be valid URL) |

**Media notes:**

- Ideal aspect ratio: 2:3 (1000x1500)
- Carousels: 2-5 static images only (no video in carousels)

## Platforms Without Config Objects

These platforms use only connection ID arrays — no additional config:

### X (Twitter)

- Uses `twitterConnectionIds` array
- Character limit: 280
- Up to 4 images per post
- No video support via this API

### Bluesky

- Uses `blueskyConnectionIds` array
- Character limit: 300
- Up to 4 images
- No video support
- URLs auto-generate link cards
- No editing after publishing

### Threads

- Uses `threadsConnectionIds` array
- Text + images + video supported
- Carousels: up to 10 images

### LinkedIn

- Uses `linkedinConnectionIds` array
- Character limit: 3,000 (under 1,300 performs better)
- Up to 9 images, or video up to 10 min
- Put links in comments, not post body (LinkedIn deprioritizes external links)
- 3-5 hashtags max
