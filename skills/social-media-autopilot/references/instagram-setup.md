# Instagram / Meta Graph API Setup

## Prerequisites
- Instagram Business or Creator account
- Facebook Page linked to the Instagram account
- Meta Developer account

## 1. Create a Meta App
1. Go to https://developers.facebook.com/apps/
2. Create app → Business type
3. Add "Instagram Graph API" product

## 2. Get Access Token
- In the Graph API Explorer (https://developers.facebook.com/tools/explorer/)
- Select your app
- Add permissions: `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`
- Generate a **User Access Token**
- Exchange for a long-lived token (60 days):

```bash
curl "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_LIVED_TOKEN"
```

## 3. Get Instagram Business Account ID
```bash
curl "https://graph.facebook.com/v18.0/me/accounts?access_token=TOKEN"
# Get the Page ID, then:
curl "https://graph.facebook.com/v18.0/PAGE_ID?fields=instagram_business_account&access_token=TOKEN"
```

## 4. Set Environment Variables
```bash
export INSTAGRAM_ACCESS_TOKEN="your_long_lived_token"
export INSTAGRAM_BUSINESS_ID="your_ig_business_id"
```

## Publishing Flow
Instagram requires a two-step process:
1. Create a media container (upload image/video)
2. Publish the container

```bash
# Step 1: Create container
curl -X POST "https://graph.facebook.com/v18.0/$INSTAGRAM_BUSINESS_ID/media" \
  -d "image_url=PUBLIC_IMAGE_URL&caption=Your+caption&access_token=TOKEN"

# Step 2: Publish
curl -X POST "https://graph.facebook.com/v18.0/$INSTAGRAM_BUSINESS_ID/media_publish" \
  -d "creation_id=CONTAINER_ID&access_token=TOKEN"
```
