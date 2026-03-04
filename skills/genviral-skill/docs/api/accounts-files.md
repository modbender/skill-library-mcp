# Account & File Commands

## accounts
List connected BYO and hosted accounts in your scope. Use this to discover account IDs for posting.

```bash
genviral.sh accounts
genviral.sh accounts --json
```

Returns:
- Account ID (use in --accounts for create-post)
- Platform (tiktok, instagram, etc.)
- Type (byo or hosted)
- Username, display name, status

## upload
Upload a file to genviral's CDN using the presigned URL flow. Returns a CDN URL you can use in posts.

```bash
genviral.sh upload --file video.mp4 --content-type video/mp4
genviral.sh upload --file slide1.jpg --content-type image/jpeg --filename "slide1.jpg"
```

Supported content types:
- Videos: `video/mp4`, `video/quicktime`, `video/x-msvideo`, `video/webm`, `video/x-m4v`
- Images: `image/jpeg`, `image/png`, `image/gif`, `image/webp`, `image/heic`, `image/heif`

Returns the CDN URL (use in create-post).

## list-files
List files uploaded via the Partner API.

```bash
genviral.sh list-files
genviral.sh list-files --type video --limit 20 --offset 0
genviral.sh list-files --type image --context ai-studio,media-upload
genviral.sh list-files --context all  # include all contexts
genviral.sh list-files --json
```

`--type` accepts: `image` or `video`.
